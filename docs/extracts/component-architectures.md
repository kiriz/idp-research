# Component Architectures

## Executive Summary

The Open Identity Platform (OIP) comprises five core components with distinct architectural paradigms. **OpenAM** (~51 modules) uses a JAAS-based callback model with pluggable authentication chains, session management via Core Token Service (CTS), and XACML 3.0 policy evaluation. **OpenDJ** (~26 modules) implements a backend-agnostic LDAP server with multi-master replication via CSN-based changelog, and REST-to-LDAP bridging using RxJava 3 reactive streams. **OpenIDM** (~52 modules) is OSGi-based (Apache Felix), with a trie-based JSON router dispatching to `/managed/*`, `/system/*`, `/repo/*`, `/sync/*`, `/recon/*`, `/workflow/*` routes, and a Reconciliation/LiveSync engine for identity lifecycle. **OpenIG** (~12 modules) provides a filter/handler pipeline architecture using the ForgeRock HTTP Framework with JSON-based route configuration, Expression Language, and credential replay. **OpenICF** (19 sub-modules) splits connector implementations via SPI and framework API, supporting CRUD + Sync + Auth operations over a remote Protobuf RPC mechanism.

All five components integrate through well-defined boundaries: OpenDJ is the foundational identity store, OpenAM handles authentication/authorization, OpenIDM manages identity lifecycle via OpenICF connectors, and OpenIG acts as a policy enforcement gateway.

## Detailed Findings

---

### OpenAM Architecture

#### Auth Chain Model

**Core Classes and File Paths:**

- `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/AuthContext.java`
  - Public-facing client API for authentication
  - Provides login/logout and callback management
  - Remote/local capability via AuthContextLocal wrapper

- `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/service/AMLoginContext.java`
  - Core layer connecting clients to JAAS LoginModule
  - Executes pre/post authentication processes
  - Manages authentication status and callbacks
  - Wraps JAAS LoginContext and coordinates with AMAuthenticationManager

- `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/config/AMAuthenticationManager.java`
  - Manages authentication configurations and chains
  - Loads module instances from configuration
  - Supports authentication level and routing

- `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/spi/AMLoginModule.java`
  - SPI base class for all authentication modules
  - Extends `javax.security.auth.spi.LoginModule`
  - Implements `init()`, `login()`, `commit()`, `abort()`, `logout()`
  - Communication via Callback objects (NameCallback, PasswordCallback, etc.)

- `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/service/LoginState.java`
  - Maintains authentication state across requests
  - Tracks current module, failed attempts, callback history
  - Supports multi-step authentication chains

**Design Pattern:** Chain of Responsibility + Strategy

- Authentication chain configured as sequence of modules with control flags
- Each module independently evaluates credentials
- Control flags (REQUIRED, REQUISITE, SUFFICIENT, OPTIONAL) determine chain behavior
- Module selection via `AppConfigurationEntry` (JAAS standard)

**Data Flow:**

```
Client -> AuthContext.login()
  -> AuthContextLocal.getLoginStatus()
    -> AMLoginContext instantiation
      -> JAAS LoginContext.login()
        -> Chain of AMLoginModule instances
          | (each module)
          -> DSAMECallbackHandler.handle(Callback[])
            -> Returns user interaction data
          -> Module validates -> Subject population
        -> Final Subject with Principals + credentials
```

**Extension Points:**

- Custom auth modules extend `AMLoginModule`
- Module schema defined in XML/LDAP service definitions
- Module properties configured via ServiceSchema framework
- Post-authentication processing via `AMPostAuthProcessInterface`

---

#### Session Management

**Core Classes and File Paths:**

- `OpenAM/openam-core/src/main/java/com/iplanet/dpro/session/service/SessionService.java`
  - Central session management service
  - Creates, retrieves, destroys sessions
  - Handles session replication and failover

- `OpenAM/openam-core/src/main/java/com/iplanet/dpro/session/service/InternalSession.java`
  - Internal representation of user session
  - Tracks session ID, creation time, expiration, properties
  - Thread-safe session state management

- `OpenAM/openam-core/src/main/java/com/iplanet/dpro/session/service/SessionConstraint.java`
  - Enforces session quotas per user/realm
  - Implements session limiting policies
  - Prevents concurrent session abuse

- `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/service/SessionActivator.java`
  - Interface for session activation strategies
  - Implementations: `DefaultSessionActivator`, `StatelessSessionActivator`, `NoSessionActivator`

**Design Pattern:** Repository + Adapter

- SessionService acts as repository interface
- Backend implementations plugged via service configuration
- Session failover via replicated token store
- Distributed cache with eventual consistency

**Session Lifecycle:**

```
1. Create:    AuthContext success -> SessionService.createSession()
2. Token:     SSOToken created with encrypted session ID
3. Storage:   Token stored in CTS (JPA, Cassandra, or Redis backend)
4. Replicate: Session state replicated across cluster nodes
5. Expire:    TTL-based or idle timeout triggers cleanup
6. Blacklist: Logout adds session to revocation list
7. Destroy:   Session removed from store + invalidated
```

**Session Blacklisting:**

- Logout invokes `SessionService.destroySession()`
- Session ID added to blacklist cache
- Blacklist checked on each session validation
- TTL-based cleanup of old blacklist entries

**Storage Backends:**

| Backend | Module | Use Case |
|---------|--------|----------|
| JPA (default) | `openam-core/` | Single-node or small cluster |
| Cassandra | `openam-cassandra/` | Horizontally scalable sessions |
| Redis | OIP extensions | High-throughput caching |
| Custom | `SessionStore` interface | Custom backends |

---

#### Policy Engine (XACML 3.0)

**Core Classes and File Paths:**

- `OpenAM/openam-entitlements/` - Policy/entitlement module (entire directory)
- `OpenAM/openam-core/src/main/java/com/sun/identity/entitlement/Entitlement.java` - Base entitlement/privilege class
- `OpenAM/openam-core/src/main/java/com/sun/identity/entitlement/EntitlementConfiguration.java` - XACML evaluation settings
- `OpenAM/openam-core/src/main/java/com/sun/identity/entitlement/SubjectImplementation.java` - SPI for custom subject matchers
- `OpenAM/openam-core/src/main/java/com/sun/identity/entitlement/ResourceMatch.java` - Resource pattern matching (exact, prefix, wildcard, regex)

**Design Pattern:** PEP/PDP Architecture

- PEP (Policy Enforcement Point) requests policy decisions from PDP
- PDP (Policy Decision Point) evaluates policies and returns permit/deny
- Policies stored in LDAP (OpenDJ) as LDIF entries or in flat file store
- Policy evaluation engine uses recursive descent with caching

**Policy Structure:**

```
Policy
+-- Resource  (URI pattern, e.g., "/admin/*")
+-- Subject   (user/group, with conditions)
+-- Action    (GET, POST, DELETE, etc.)
+-- Environment (IP, time window, device type)
+-- Effect    (Allow/Deny)
```

**Evaluation Flow:**

```
Client Request
  -> PolicyEvaluator.evaluate(resource, action, subject, env)
    -> Load applicable policies from PolicyStore
      -> Evaluate each policy's conditions (subject, resource, action, env)
        -> Short-circuit on DENY (deny-overrides)
        -> Aggregate permits
      -> Return decision + obligations
    -> Cache result (TTL-based invalidation)
```

**Extension Points:**

- Custom subject matchers: extend `SubjectImplementation`
- Custom resource comparators: extend `ResourceMatch`
- Custom environment evaluators: extend `EnvironmentImplementation`

---

#### Plugin SPI (Service Provider Interface)

**Module Registration Mechanism:**

- `OpenAM/openam-authentication/openam-auth-common/` - Common auth module utilities
- Each auth module pom.xml references openam-core dependency
- Service schema XML in module's `schema/` directory

**Authentication Module Discovery:**

1. Classpath scanning for `AMLoginModule` implementations
2. XML/LDAP service definitions loaded
3. Constructor instantiation with config parameters
4. Module properties mapped from LDAP DN to object attributes

**Example Auth Module Structure:**

```
openam-auth-ldap/
+-- pom.xml (depends on openam-core)
+-- src/main/java/com/sun/identity/authentication/modules/ldap/
|   +-- LDAP.java (extends AMLoginModule)
+-- src/main/resources/
|   +-- amAuthLDAP.xml (service schema definition)
+-- src/test/...
```

**Service Schema Properties:**

- Module name (e.g., "LDAP")
- Configuration attribute definitions (LDAP URL, bind DN, password scheme)
- Callback definitions (username/password, OTP, choice, etc.)
- Authentication level
- Module class name

**Design Pattern:** Service Locator + Factory

- `AMAuthenticationManager` acts as service locator
- Module instantiation via reflection using class name from schema
- Configuration injected at runtime from LDAP

---

#### OAuth2/OIDC Provider

**Core Location:** `OpenAM/openam-oauth2/src/main/java/org/forgerock/oauth2/core/` (~80+ classes)

**Key Interfaces and Classes:**

| Class | Role |
|-------|------|
| `OAuth2Request` | Wraps incoming OAuth2 request parameters |
| `OAuth2ProviderSettings` | Configuration (grant types, token formats, lifetimes) |
| `AuthorizationService` | Handles `/authorize` endpoint |
| `AccessTokenService` | Handles `/token` endpoint |
| `ResponseTypeHandler` | SPI: code, token, id_token response types |
| `GrantTypeHandler` | SPI: authorization_code, client_credentials, password, jwt-bearer, device_code |
| `TokenStore` | SPI: pluggable token persistence (CTS-backed default) |
| `ScopeValidator` | SPI: custom scope validation |

**Token Classes:**

- `AccessToken` - Bearer token; short-lived (1h default)
- `RefreshToken` - Long-lived; used to refresh access token
- `AuthorizationCode` - Ephemeral; single-use exchange for token
- `StatefulAccessToken` / `StatefulRefreshToken` - Store full token state
- `IntrospectableToken` - Supports introspection endpoint

**Authorization Code Flow:**

```
1. Client -> /authorize?response_type=code&client_id=...
   -> AuthorizationService.authorize()
     -> AuthorizeRequestValidator.validate() (client, redirect URI, scopes)
     -> ResourceOwnerAuthenticator (login if needed)
     -> ResourceOwnerConsentVerifier (user consent)
     -> AuthorizationCodeResponseTypeHandler.handle()
       -> AuthorizationCode created + stored
       -> Redirect to callback with code

2. Client (backend) -> /token?grant_type=authorization_code&code=...
   -> AccessTokenService.requestAccessToken()
     -> AuthorizationCodeGrantTypeHandler.handle()
       -> Code validation (valid, not expired, not used)
       -> Client authentication
       -> AccessToken + RefreshToken created
       -> Return tokens in JSON
```

**OIDC Extensions:**

- ID Token (JWT) issued alongside access token
- Claims: `sub`, `aud`, `iss`, `iat`, `exp`, etc.
- UserInfo endpoint returns user profile claims
- Discovery: `/.well-known/openid-configuration`

---

#### Authentication Module Inventory (30+ modules)

| Category | Modules |
|----------|---------|
| Directory/LDAP | `openam-auth-ldap`, `openam-auth-ad`, `openam-auth-nt`, `openam-auth-ntlmv2`, `openam-auth-membership` |
| Multi-factor | `openam-auth-hotp`, `openam-auth-oath`, `openam-auth-fr-oath`, `openam-auth-push`, `openam-auth-webauthn` |
| Federation/Social | `openam-auth-oauth2`, `openam-auth-oidc`, `openam-auth-saml2` |
| External | `openam-auth-radius`, `openam-auth-msisdn`, `openam-auth-securid`, `openam-auth-cert`, `openam-auth-recaptcha` |
| Persistence | `openam-auth-persistentcookie`, `openam-auth-windowsdesktopsso` |
| Scripting | `openam-auth-scripted`, `openam-auth-amster` |
| Advanced | `openam-auth-device-id`, `openam-auth-qr`, `openam-auth-application`, `openam-auth-adaptive`, `openam-auth-anonymous`, `openam-auth-httpbasic`, `openam-auth-jdbc`, `openam-auth-kerberos` |

**Other Core Modules (~51 total):** `openam-core`, `openam-oauth2`, `openam-entitlements`, `openam-federation`, `openam-rest`, `openam-session-db`, `openam-cassandra`, `openam-distribution`, `openam-cli`, `openam-ui`, `openam-audit`, `openam-monitoring`, `openam-configurator-tool`

---

### OpenDJ Architecture

#### Backend Abstraction Layer

**Core Classes and File Paths:**

- `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/core/DirectoryServer.java`
  - Singleton managing all server components
  - Registers/manages backends, plugins, handlers
  - ~2000+ lines coordinating server startup/shutdown

- `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/api/Backend.java`
  - SPI interface for storage backends
  - Core methods: `entryExists()`, `getEntry()`, `addEntry()`, `modifyEntry()`, `deleteEntry()`, `search()`
  - Backend lifecycle: `initialize()`, `finalizeBackend()`

- `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/api/LocalBackend.java`
  - Extends Backend for local (non-remote) implementations
  - Transaction support, export/import, backup/restore
  - Search result cursor management

- `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/core/BackendConfigManager.java`
  - Loads backend configurations from `config.ldif`
  - Manages backend lifecycle (start, stop, reconfigure)
  - Plugin architecture for backend types

**Available Backend Implementations:**

| Backend | Description | Use Case |
|---------|-------------|----------|
| JE (Berkeley DB Java Edition) | Default backend; ACID transactions, hot standby | General purpose, ~800k entries/GB |
| SQL (JDBC) | Maps LDAP to SQL tables; PostgreSQL, MySQL, Oracle, SQL Server | Relational DB integration |
| PDB (Pluggable) | Generic plugin interface | Community extensions |
| Cassandra | Distributed, high write throughput | Session storage for OpenAM |
| In-memory | Embedded for testing | Test/minimal deployments |

**Backend Selection at Runtime:**

```
DirectoryServer initialization
  -> BackendConfigManager.initializeBackendConfig()
    -> Iterate config.ldif backend entries
      -> For each backend:
         1. Load backend class name from config
         2. Instantiate via ClassLoader.loadClass()
         3. Call Backend.initialize() with config parameters
         4. Register with DirectoryServer
         5. Load suffix data (LDIF import if initial)
```

**Design Pattern:** Plugin / Abstract Factory

- Backend interface is stable SPI
- Implementations plugged via configuration
- Configuration specifies class name + parameters
- Runtime instantiation without recompilation

---

#### Replication Protocol (Multi-Master)

**Core Location:** `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/replication/`

**Key Classes (inferred from module structure):**

- `SynchronizationProvider` - Main replication coordinator
- `ReplicationBroker` - Broker managing replication traffic
- `ReplicationDomain` - Per-suffix replication state
- `Changelog` - Transaction log of changes
- `ChangeNumber` / `CSN` (Change Sequence Number) - Global ordering

**Replication Mechanism:**

1. **Change Detection:** Backend operations (add, modify, delete) trigger replication listeners. Change captured with timestamp + server ID.

2. **Local Persistence:** Changes written to local changelog database. Changelog stores last N entries (configurable retention).

3. **CSN Format:** Each server has unique server ID (1-127). CSN format: `timestamp.serverID.seqNum` (e.g., `20240212T120530Z#000001#0001#000001`).

4. **Export to Replicas:** Changes in changelog replicated via TCP to peer servers. Replication server (optional) acts as hub.

5. **Conflict Resolution:**
   - CSN ordering (later CSN wins)
   - Server ID tiebreaker
   - Generational clock (version counter)

6. **Bi-directional Sync:** All servers can write; changes eventually propagate. No single master. Split-brain mitigation via CSN monitoring.

**Changelog Structure:**

```
cn=changelog
+-- cn=changes
|   +-- (LDIF format entries: changeNumber, targetDN, changeType, etc.)
+-- (ECL - External Change Log for client polling)
```

**Configuration:**

```xml
<synchronization-provider>
  <enabled>true</enabled>
  <base-dn>dc=example,dc=com</base-dn>
  <server-id>1</server-id>
  <replication-port>8989</replication-port>
  <changelog-dir>/var/lib/opendj/changelog</changelog-dir>
  <conflicts-historical-purge-delay>30 days</conflicts-historical-purge-delay>
</synchronization-provider>
```

**Design Pattern:** Publish-Subscribe + Event Sourcing

- Changes captured as immutable events in changelog
- Subscribers (replicas) consume event stream
- CSN ensures global causal ordering
- Idempotent operation application handles duplicates

---

#### REST-to-LDAP Gateway

**Core Location:** `OpenDJ/opendj-rest2ldap/src/main/java/org/forgerock/opendj/rest2ldap/`

**HTTP-to-LDAP Mapping:**

| HTTP Method | LDAP Operation | Example |
|-------------|---------------|---------|
| `GET /users/john` | Search | `uid=john,ou=users,dc=example,dc=com` |
| `POST /users` | Add | Create new LDAP entry from JSON body |
| `PUT /users/john` | Modify | Apply JSON updates as LDAP modifications |
| `DELETE /users/john` | Delete | Map REST path to DN and delete |
| `GET /users?filter=...` | Search | Parse CREST filter -> LDAP filter |

**JSON-to-LDAP Example:**

Request JSON:
```json
{
  "uid": "john",
  "mail": "john@example.com",
  "cn": "John Doe",
  "objectClass": ["inetOrgPerson", "organizationalPerson"]
}
```

Maps to LDAP Entry:
```
dn: uid=john,ou=users,dc=example,dc=com
uid: john
mail: john@example.com
cn: John Doe
objectClass: inetOrgPerson
objectClass: organizationalPerson
```

Response includes `_id` (RDN value) and `_rev` (etag) system fields.

**Design Pattern:** Adapter + Facade

- Hides LDAP complexity behind REST interface
- Bidirectional mapping (HTTP <-> LDAP)
- Stateless request handling

---

#### Request Processing Pipeline

**Core Location:** `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/core/`

**Operation Interfaces (LDAP):**

All inherit from `Operation` base interface:

| Operation | Purpose | Key Methods |
|-----------|---------|-------------|
| `SearchOperation` | Search directory | `getBaseDN()`, `getScope()`, `getFilter()`, `getSizeLimit()` |
| `AddOperation` | Create new entry | `getObjectClasses()`, `getAttributes()` |
| `ModifyOperation` | Update attributes | `getModifications()` (ADD, DELETE, REPLACE, INCREMENT) |
| `DeleteOperation` | Remove entry | Cascading delete handled by plugin |
| `ModifyDNOperation` | Rename/move entry | New RDN, new superior DN |
| `BindOperation` | Authentication | Simple password or SASL mechanisms |
| `CompareOperation` | Check attribute value | Single assertion: DN + attribute + value |
| `ExtendedOperation` | OID-based extensions | StartTLS, WhoAmI, Modify Password, Cancel |

**Pipeline Architecture:**

```
Client Connection (TCP/TLS)
  |
ConnectionHandler (protocol parsing)
  |
OperationWrapper sequence:
  +-- Pre-Operation Plugins
  |   +-- PreOperationSearchPlugin
  |   +-- AccessControlPlugin (ACI evaluation)
  |   +-- Custom plugins
  |
WorkQueue (thread pool dispatch)
  |
Backend Operation:
  +-- Permission check (ACI)
  +-- Referral check
  +-- Normalize input
  +-- Backend.search/add/modify/delete()
  +-- Log operation
  |
OperationWrapper (post phase):
  +-- PostOperationSearchPlugin
  +-- PostOperationModifyPlugin (trigger sync/replication)
  +-- Custom plugins
  |
Response serialization + transmission
```

**Plugin System:**

- **Pre-Operation:** Cancel request, validate input, apply access controls, add synthetic attributes
- **Post-Operation:** Trigger replication, update audit logs, invoke external systems, update sync queue
- **Entry Cache:** Caching layer with LRU eviction
- **Persistent Search:** Client polls for changes (LDAP Persistent Search)

**WorkQueue Strategies:** `BoundedWorkQueueStrategy` (fixed thread pool), `SynchronousStrategy` (blocking, for testing). Configurable pool size, queue depth, timeout.

**Design Pattern:** Pipeline + Plugin

- Sequential filtering via plugins
- Each plugin can modify/reject request
- Transparent to business logic (backend)

---

#### RxJava Usage (OpenDJ Core)

**Core Location:** `OpenDJ/opendj-core/src/main/java/org/forgerock/opendj/ldap/`

**Reactive Patterns:**

- **Promise-based API:** `LdapPromise<T>` for async operation results. Chainable via `thenAsync()`, `thenOnResult()`, `thenOnException()`.
- **RxJava 3 Integration:** Observable/Flowable for search result streams. Non-blocking I/O using Netty.
- **Backpressure:** Handling for large result sets. Lazy evaluation of search results.

```java
// Sync
SearchResultEntry entry = connection.readEntry("uid=john,...");

// Async (RxJava)
LdapPromise<SearchResultEntry> promise =
    connection.readEntryAsync("uid=john,...");
promise.thenOnResult(entry -> { /* process */ })
       .thenOnException(error -> { /* handle */ });
```

**Design Pattern:** Reactive Streams + Composition

---

### OpenIDM Architecture

#### OSGi Service Model

**Framework:** Apache Felix OSGi Container v5.x

**Core Activators (BundleActivator pattern):**

- `OpenIDM/openidm-router/src/main/java/org/forgerock/openidm/router/Activator.java`
  - Registers `RouterRegistry` service + `RequestHandler` service

- `OpenIDM/openidm-repo-jdbc/src/main/java/org/forgerock/openidm/repo/jdbc/impl/Activator.java`
  - JDBC repository backend; registers as data source + query executor

- `OpenIDM/openidm-system/src/main/java/org/forgerock/openidm/core/internal/Activator.java`
  - Core system service; initializes OpenIDM runtime

- `OpenIDM/openidm-config/src/main/java/org/forgerock/openidm/config/persistence/Activator.java`
  - Configuration persistence; loads config from filesystem/LDAP

- `OpenIDM/openidm-repo-orientdb/src/main/java/org/forgerock/openidm/repo/orientdb/impl/Activator.java`
  - OrientDB repository backend

**Bundle Lifecycle:**

```
INSTALLED -> RESOLVED -> STARTING -> ACTIVE -> STOPPING -> UNINSTALLED
```

**Service Registration Example (Router):**

```java
public void start(BundleContext context) {
    routerRegistry = new RouterRegistryImpl(context);
    Dictionary<String, Object> properties = new Hashtable<>();
    properties.put(Constants.SERVICE_DESCRIPTION, "Router route group service");
    properties.put(Constants.SERVICE_PID, RouterRegistry.class.getName());
    context.registerService(RouterRegistry.class, routerRegistry, properties);
}
```

**Service Discovery:**

```java
ServiceTracker tracker = new ServiceTracker(context, RouterRegistry.class.getName(), null);
tracker.open();
RouterRegistry router = (RouterRegistry) tracker.getService();
```

**Design Pattern:** Service Locator + Factory

- Decoupled components via service interface contracts
- Runtime service discovery
- Pluggable implementations without recompilation
- Lifecycle management via bundle activation

---

#### Sync/Recon Engine

**Core Location:** `OpenIDM/openidm-core/src/main/java/org/forgerock/openidm/sync/`

**Key Components:**

1. **SyncEngine** - Main coordinator; orchestrates LiveSync and Reconciliation
2. **Reconciliation Service** - Batch comparison of source vs. target objects
3. **LiveSync Service** - Real-time change capture from source systems
4. **Implicit Sync** - Auto-triggered on managed object write
5. **Link Store** - Maps source object ID <-> target object ID (stored in JDBC/OrientDB)

**Reconciliation Flow:**

```
Trigger: POST /openidm/recon?_action=recon
  |
SyncEngine.recon()
  |
Load mapping (e.g., "user-to-ldap")
  |
Phase 1: Source -> Target Creation
  - Query all source objects
  - For each: check if linked entry exists in target
    - If no link: create target via connector
    - Link source_id <-> target_id
  |
Phase 2: Target Update
  - For each linked source:
    - Get target object, compare attributes
    - If differences: apply updates
  |
Phase 3: Target Cleanup
  - For each target: check if has source link
    - If no link + policy=delete: delete target
  |
Final Report: created, updated, deleted counts + errors
```

**Mapping Configuration:**

```json
{
  "name": "user-to-ldap",
  "source": "managed/user",
  "target": "system/ldap/account",
  "properties": [
    { "source": "userName", "target": "uid" },
    { "source": "mail", "target": "mail" }
  ],
  "links": "linkedUser",
  "onCreate": "CREATE",
  "onUpdate": "UPDATE",
  "onDelete": "DELETE"
}
```

**LiveSync Trigger:**

```
Change detected in source system
  -> Connector.sync() returns SyncToken + SyncDelta objects
  -> SyncDelta includes: Token, Operation (CREATE/UPDATE/DELETE), ObjectClass, Uid, Attributes
  -> For each SyncDelta:
     - Create/update managed object
     - Check mappings for target systems
     - Apply implicit sync (if configured)
  -> Update sync token (checkpoint)
```

**Design Pattern:** ETL (Extract-Transform-Load) + Change Data Capture

- Mapping languages for attribute transformation
- Pluggable source/target (connectors)
- Idempotent reconciliation (safe to re-run)
- Comprehensive audit trail

---

#### Managed Objects

**Central Concept:** JSON-LD representation of identity data, independent of external systems. Defined in `managed.json` configuration.

**Schema Definition (managed.json):**

```json
{
  "objects": [
    {
      "name": "user",
      "onCreate": [{ "type": "text/javascript", "source": "..." }],
      "onUpdate": [{ "type": "text/javascript", "source": "..." }],
      "properties": {
        "userName": { "title": "User Name", "type": "string", "required": true },
        "password": { "title": "Password", "type": "string", "isProtected": true },
        "mail":     { "title": "Email", "type": "string", "format": "email" }
      },
      "relationships": {
        "roles": {
          "type": "array",
          "items": {
            "type": "relationship",
            "reverseRelationship": "members",
            "resourceCollection": { "name": "role" }
          }
        },
        "manager": {
          "type": "relationship",
          "resourceCollection": { "name": "user" }
        }
      }
    }
  ]
}
```

**REST Endpoints:**

| Operation | Endpoint | Notes |
|-----------|----------|-------|
| Create | `POST /managed/user` | Returns `_id`, full object |
| Read | `GET /managed/user/john` | System fields: `_id`, `_rev`, `_created`, `_updated` |
| Update | `PUT /managed/user/john` | Optimistic locking via `_rev` |
| Delete | `DELETE /managed/user/john` | Removes object + relationships |
| Query | `GET /managed/user?_queryFilter=department eq "sales"` | CREST filter syntax |
| Relationships | `GET /managed/user/john/roles` | Role IDs linked to user |

**Lifecycle Hooks:**

- `onCreate`: Auto-generate username, set defaults
- `onUpdate`: Validate email format, enforce constraints
- `onDelete`: Cascade delete related objects
- `onRead`: Decrypt sensitive fields
- `onQuery`: Filter results by authorization

**Protected Properties:** Encrypted at rest, masked in audit logs, never returned in plain text via HTTP.

**Query Filtering (CREST Syntax):** `userName eq "john"`, `mail co "example.com"`, `age gt 30`, compound: `department eq "IT" and age lt 50`

**Design Pattern:** Document Store + Event-Driven

- JSON-LD enables semantic queries
- Hooks enable reactive workflows
- Relationships support complex identity graphs
- Optimistic locking prevents conflicting updates

---

#### Router (Request Dispatcher)

**Core Classes:**

- `OpenIDM/openidm-router/src/main/java/org/forgerock/openidm/router/RouterRegistry.java` - Route management interface
- `OpenIDM/openidm-router/src/main/java/org/forgerock/openidm/router/RouterRegistryImpl.java` - Trie-based route matching
- `OpenIDM/openidm-router/src/main/java/org/forgerock/openidm/router/impl/JsonResourceRouterService.java` - RequestHandler for internal routing

**Supported Routes:**

| Pattern | Handler | Operations |
|---------|---------|------------|
| `/managed/{type}/{id}` | ManagedObject service | CRUD + relationships |
| `/system/{connector}/{objectClass}/{id}` | OpenICF ConnectorFacade | CRUD via connector |
| `/repo/{table}/{id}` | Repository service (JDBC, OrientDB) | Direct DB CRUD |
| `/sync` | SyncEngine service | `_action=recon`, `_action=liveSync` |
| `/recon` | ReconService | Reconciliation reports |
| `/workflow/processinstance` | Activiti engine wrapper | Start process, complete task |
| `/audit/access`, `/audit/activity` | Audit service | Query audit events |
| `/custom/*` | Application bundles | Custom routes |

**Trie-based Matching:**

```
/managed/user/john
  -> Router trie: /managed/{type}/{id}
  -> Match: managed handler
  -> Params: type=user, id=john
  -> Handler: ManagedObjectService.handle(request)
    -> Routes to ObjectSet for "user"
    -> CRUD operation: GET
    -> Returns user object
```

**Request Filter Chain:**

1. **Authentication Filter** - Validates session token, sets principal
2. **Authorization Filter** - RBAC check for operation
3. **Validation Filter** - Schema validation for request body
4. **Transformation Filter** - Maps external -> internal representation, encryption
5. **Audit Filter** - Logs all requests/responses, captures before/after state
6. **Routing Filter** - Dispatches to handler, extracts path parameters

**Design Pattern:** Interceptor/Chain of Responsibility + Trie Routing

- Multiple filters can process request
- Trie enables O(n) path matching (n = path depth, typically 3-4)
- Pluggable handlers via service registration

---

#### Workflow Integration

**Module:** `OpenIDM/openidm-workflow-activiti/`

- Uses Activiti BPMN 2.0 workflow engine
- Routes: `/workflow/processinstance`, `/workflow/taskinstance`
- Start process instances, complete human tasks
- Integration with managed objects for approval workflows

---

### OpenIG Architecture

#### Filter/Handler Pipeline

**Core Location:** `OpenIG/openig-core/src/main/java/`

**Core Interfaces:**

```java
// Filter: intercepts request, delegates to next handler
public interface Filter {
    Promise<Response, NeverThrowsException> filter(
        Context context, Request request, Handler next);
}

// Handler: endpoint of pipeline, returns response
public interface Handler {
    Promise<Response, NeverThrowsException> handle(
        Context context, Request request);
}
```

**Pipeline Execution:**

```
HTTP Request
  |
Filter 1.filter(context, request, next) {
  // Pre-processing
  return next.handle(...).thenOnResult(response -> {
    // Post-processing
    return response;
  });
}
  |
Filter 2.filter(context, request, next) { ... }
  |
...
  |
Final Handler (ClientHandler or StaticContentHandler)
  |
HTTP Response
```

**Async/Promise Chain:** Non-blocking via `thenAsync()`, `thenOnResult()`, `thenOnException()`. Thread pool handles multiple requests concurrently.

**Context Object:** Parent context for nested calls, attributes map (key-value storage), access via `context.asContext(SomeContextClass.class).getAttribute("key")`.

**Design Pattern:** Decorator + Promise (Monad)

- Composable filter layers
- Functional: functions as first-class objects
- Immutable request/response

---

#### Route Configuration (JSON)

**Location:** `config/routes/` directory in OpenIG deployment. Hot-reloadable.

**Route Definition:**

```json
{
  "name": "my-route",
  "baseURI": "http://backend-server:8080",
  "condition": "${request.path == '/protected'}",
  "filters": [
    {
      "type": "HttpBasicAuthFilter",
      "config": {
        "usernameHeader": "X-Username",
        "passwordHeader": "X-Password"
      }
    },
    {
      "type": "AddHeaderFilter",
      "config": {
        "headers": {
          "X-Authenticated-User": "${request.headers['X-Username']}"
        }
      }
    }
  ],
  "handler": { "type": "ClientHandler" }
}
```

**Expression Language (EL):**

- Syntax: `${expression}`
- Request properties: `${request.headers['X-Custom']}`, `${request.uri.path}`, `${request.method}`
- Context/variables: `${attributes.userId}`, `${session.user.id}`
- Functions: `${request.headers['name'].toLowerCase()}`
- Conditionals: `${request.method == 'POST' ? 'post' : 'get'}`
- Null coalescing: `${request.headers['X-Custom'] ?: 'default'}`

**Condition Evaluation:**

```json
"condition": "${request.path =~ '/admin/.*'}"
"condition": "${request.method == 'POST'}"
"condition": "${request.headers['X-Admin'] != null}"
```

**Route Matching:** First-match-wins. Routes processed in filename order. Final route has no condition (catch-all). Hot-reload: no downtime on config changes.

**Design Pattern:** Declarative Configuration + Expression Language

---

#### Key Filters (50+ Types)

**Authentication:**

| Filter | Purpose |
|--------|---------|
| `HttpBasicAuthFilter` | HTTP Basic Auth extraction and validation |
| `OAuth2ResourceServerFilter` | Validates OAuth2 bearer tokens, introspects with auth server |
| `SamlFederationFilter` | SAML2 assertion parsing and validation |
| `OpenAmAuthenticationFilter` | Delegates auth to OpenAM; extracts SSOToken |
| `WindowsAuthenticationFilter` | NTLM/Kerberos via GSSAPI |

**Credential Replay:**

| Filter | Purpose |
|--------|---------|
| `CredentialReplayFilter` | Extracts credentials from auth context, injects into upstream request |
| `CredentialInjectFilter` | Programmatic credential insertion for service accounts |

**Header Manipulation:**

| Filter | Purpose |
|--------|---------|
| `AddHeaderFilter` | Adds headers (supports EL for dynamic values) |
| `RemoveHeaderFilter` | Strips sensitive headers before forwarding |
| `ReplaceHeaderFilter` | Pattern matching + replacement |
| `SetAttributesFilter` | Stores values in context for inter-filter communication |

**Security:**

| Filter | Purpose |
|--------|---------|
| `CsrfTokenFilter` | CSRF token validation on state-changing requests |
| `CookieFilter` | Cookie management (Secure, HttpOnly, SameSite) |

**Routing:**

| Filter | Purpose |
|--------|---------|
| `SwitchFilter` | Conditional routing based on request properties |
| `RouterHandler` | Trie-based path routing |
| `SequenceHandler` | Chains handlers sequentially |

**Debugging/Logging:**

| Filter | Purpose |
|--------|---------|
| `CaptureFilter` | Captures request + response for debugging |
| `LogAttachedExceptionFilter` | Logs exceptions with full stack trace |
| `RuntimeExceptionFilter` | Catches uncaught exceptions, returns HTTP error |

**Performance:**

| Filter | Purpose |
|--------|---------|
| `MetricsFilter` | Collects latency, throughput, error rate |
| `RateLimitFilter` | Enforces rate limits (per-user or global); returns 429 |
| `ThrottlingFilter` | Queues excess requests, limits concurrency |

**Scripting:**

| Filter | Purpose |
|--------|---------|
| `ScriptableFilter` | JavaScript/Groovy custom logic without deployment |

**Database/SQL:**

| Filter | Purpose |
|--------|---------|
| `SqlAttributesFilter` | Queries DB for user attributes, injects into context |

**Response Processing:**

| Filter | Purpose |
|--------|---------|
| `LocationHeaderFilter` | Rewrites Location header (backend -> client-visible URLs) |

**Integration:**

| Filter | Purpose |
|--------|---------|
| `OpenAmHandler` | OpenAM policy decisions |
| `UmaFilter` | User-Managed Access (OAuth2 profile) |
| `SamlFederationHandler` | SAML2 assertion creation for federation |

---

#### Key Handlers (16+ Types)

| Handler | Purpose |
|---------|---------|
| `ClientHandler` | HTTP requests to backend; connection pooling, timeouts, cert pinning |
| `StaticContentHandler` | Static files (CSS, JS, images); caching, compression |
| `RouterHandler` | Path-based routing to sub-handlers |
| `SwitchHandler` | Conditional routing (if-else chains) |
| `SequenceHandler` | Sequential handler execution |
| `ExceptionHandler` | Transforms exceptions to HTTP error responses |
| `RedirectHandler` | HTTP redirects (301, 302, 307, 308) |
| `NotFoundHandler` | 404 responses with customizable error page |
| `OpenAmHandler` | Delegates to OpenAM for auth/authz |
| `SamlFederationHandler` | SAML2 federation SSO |
| `OAuth2Handler` | OAuth2 grant flow handling |
| `UmaHandler` | User-Managed Access |
| `ScriptableHandler` | JavaScript/Groovy custom handler logic |
| `HttpContextHandler` | Injects HTTP context (headers, cookies, method) |

---

#### Credential Replay Mechanism

**Scenario: OAuth2 -> HTTP Basic Auth**

```
User logs in with OAuth2 bearer token
  -> OAuth2ResourceServerFilter validates token
  -> Extracts: user_id="john", scopes=["read", "write"]
  -> Sets context: attributes['userId'] = "john"
  -> CredentialReplayFilter reads attributes['userId']
  -> Loads credentials from secure store (vault lookup)
  -> Adds header: Authorization: Basic base64("john:password123")
  -> Request forwarded to upstream with HTTP Basic auth
  -> Upstream validates credentials
  -> Response flows back through filters
  -> CredentialReplayFilter removes auth header (if configured)
  -> Response sent to client
```

**Credential Sources:**

- Context attributes: `attributes['username']`, `attributes['password']`
- Session: `session['credentials']`
- External vault (HashiCorp Vault, AWS Secrets Manager)

**Supported Auth Schemes:**

- HTTP Basic: `Authorization: Basic base64(user:pass)`
- Bearer token: `Authorization: Bearer <token>`
- Custom header: `X-API-Key: <key>`

**Security:** TLS for credentials in transit, vault for storage, minimal exposure in logs, audit trail of usage.

**Design Pattern:** Facade + Adapter

---

### OpenICF Architecture

#### SPI/API Split

**API Layer (what clients use):**

- Location: `OpenICF/OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/api/`
- Classes: `ConnectorFacade`, `ConnectorInfo`, `ConnectorInfoManager`, `Configuration`
- Purpose: Client-facing abstractions hiding implementation details

**SPI Layer (what connectors implement):**

- Location: `OpenICF/OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/spi/`
- Classes: `Connector`, `ConnectorClass`, operation interfaces
- Purpose: Contract for connector developers

**Design Rationale:**

1. **Separation of Concerns:** Client code depends on API; connectors depend on SPI; framework bridges
2. **Versioning:** API can change between versions; SPI more stable for backward compatibility
3. **Pluggability:** New connectors without client code changes; ClassLoader isolation via connector bundles

**API Usage (Client Side):**

```java
ConnectorFacade facade = ConnectorFacadeFactory.newInstance()
    .newConnectorFacade(connectorInfo);

facade.create(ObjectClass.ACCOUNT, attributes, options);
facade.update(ObjectClass.ACCOUNT, uid, attributes, options);
facade.delete(ObjectClass.ACCOUNT, uid, options);
facade.search(ObjectClass.ACCOUNT, filter, handler, options);
facade.getSchema();
```

**SPI Implementation (Connector Side):**

```java
@ConnectorClass(
    displayNameKey = "LDAP",
    configurationProperties = LdapConfiguration.class)
public class LdapConnector implements Connector,
    CreateOp, UpdateOp, DeleteOp, SearchOp, SchemaOp {

    @Override
    public Uid create(ObjectClass objectClass,
                      Set<Attribute> createAttributes,
                      OperationOptions options) {
        // Connector-specific implementation
    }
}
```

**Framework Responsibilities:** Class loading (discovers connectors on classpath), lifecycle management (instantiation, configuration injection, cleanup), invocation (routes API calls to SPI implementations), remote support (marshals calls across process boundary via RPC), caching (schema, configurations), error handling (wraps exceptions in framework-standard hierarchy).

---

#### Operation Interfaces (SPI)

**Base Interface:** `OpenICF/OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/spi/operations/SPIOperation.java` (marker interface)

**CRUD Operations:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `CreateOp` | `Uid create(ObjectClass, Set<Attribute>, OperationOptions)` | Create resource object; returns assigned Uid |
| `UpdateOp` | `Uid update(ObjectClass, Uid, Set<Attribute>, OperationOptions)` | Replace attributes on existing object |
| `DeleteOp` | `void delete(ObjectClass, Uid, OperationOptions)` | Remove object |
| `SearchOp` | `void executeQuery(ObjectClass, Filter, ResultsHandler, OperationOptions)` | Query objects via filter; streaming callback |

**Authentication:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `AuthenticateOp` | `Uid authenticate(ObjectClass, String username, GuardedString password, OperationOptions)` | Validate credentials; returns Uid or throws |

**Sync Operations:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `SyncOp` | `void sync(ObjectClass, SyncToken, SyncResultsHandler, OperationOptions)` | Returns changes since last sync; streaming SyncDelta objects |

SyncDelta contains: Token (next checkpoint), Operation (CREATE/UPDATE/DELETE), ObjectClass, Uid, Attributes.

**Schema:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `SchemaOp` | `Schema schema()` | Returns resource schema: ObjectClass defs, attribute defs, operation support |

**Scripting:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `ScriptOnResourceOp` | `Object runScriptOnResource(ScriptContext, OperationOptions)` | Execute script on resource (shell, SQL) |
| `ScriptOnConnectorOp` | `Object runScriptOnConnector(ScriptContext, OperationOptions)` | Execute Groovy in connector JVM |

**Utility:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `ResolveUsernameOp` | `Uid resolveUsername(ObjectClass, String, OperationOptions)` | Convert username to Uid |

**Operation Support Declaration:** Connector declares supported operations by implementing interfaces. Schema can also declare per-ObjectClass operation support.

**OperationOptions:** Connector-specific hints: `SCOPE_ON_OPERATION`, `ATTRIBUTES_TO_GET`, `RETURN_DEFAULT_ATTRIBUTES`, plus custom options.

---

#### Remote Connector Server (Protobuf RPC)

**Architecture:**

```
OpenIDM
  -> ConnectorFacade
  -> LocalConnectorInfoManager (checks: local vs. remote)
  -> Remote detected -> RemoteConnectorInfoManager
  -> RemoteConnectorServer (separate JVM, port 8759)
  -> Connector implementation
  -> External system (LDAP, DB, HTTP, etc.)
```

**Core Classes:**

- `OpenICF/OpenICF-java-framework/connector-framework-server/src/main/java/org/forgerock/openicf/framework/remote/rpc/RemoteConnectorServer.java`
  - Standalone server process on port 8759
  - Authenticates client connections
  - Marshals operations to connector implementations

- `OpenICF/OpenICF-java-framework/connector-framework-server/src/main/java/org/forgerock/openicf/framework/client/RemoteConnectorInfoManager.java`
  - Client-side manager; connects to remote server
  - Discovers available connectors
  - Routes operations via RPC

**Connection Establishment:**

1. OpenIDM configuration specifies remote connector (`remoteConnectorServer: "host:8759"`)
2. `RemoteConnectorInfoManager` connects, authenticates (shared key or mutual TLS)
3. Downloads available connectors list, matches bundle name + version
4. Creates `ConnectorFacade` for remote connector
5. Connection pooled and reused; auto-reconnect on failure

**Protobuf Message Format:**

```protobuf
message OperationRequest {
  int32 requestId = 1;
  string connectorKey = 2;
  string operationName = 3;
  repeated Parameter parameters = 4;
}

message OperationResponse {
  int32 requestId = 1;
  bool success = 2;
  bytes result = 3;
  ErrorMessage error = 4;
}
```

**Message Framing:** `[4 bytes: length (big-endian)] [N bytes: Protobuf message]`

**Handshake Protocol:**

```
1. Client connects to RemoteConnectorServer:port
2. Server sends: SERVER_HANDSHAKE { version, challenge }
3. Client responds: CLIENT_HANDSHAKE { HMAC-SHA256(sharedKey, challenge) }
4. Server verifies HMAC -> authenticated
5. Begin message exchange
```

**Multiplexing:** Single connection handles multiple requests concurrently. Request ID ensures response-to-request pairing. Server thread pool processes in parallel.

**Failover + Load Balancing:**

```json
{
  "connectorRef": {
    "remoteConnectorServers": [
      {"host": "connector-1", "port": 8759},
      {"host": "connector-2", "port": 8759}
    ],
    "failoverStrategy": "round-robin"
  }
}
```

Round-robin alternation, skip downed servers, periodic health checks, circuit breaker for flaky servers.

**Design Pattern:** Remote Proxy + RPC

- Local proxy hides network complexity
- Transparent to business logic (same `ConnectorFacade` interface)
- Protobuf ensures version compatibility

---

#### Built-in Connectors

| Connector | Bundle | Operations | Key Features |
|-----------|--------|------------|--------------|
| **LDAP** | `openicf-ldap-connector` | Create, Update, Delete, Search, Authenticate, Sync | TLS/SSL, connection pooling, paging, password change |
| **CSV** | `openicf-csv-connector` | Create, Update, Delete, Search | In-memory parsing, atomic writes; no real-time sync |
| **Database/JDBC** | `openicf-database-connector` | Create, Update, Delete, Search, Sync | SQL templating, transactions, timestamp-based sync; PostgreSQL, MySQL, Oracle, SQL Server, H2 |
| **XML** | `openicf-xml-connector` | Create, Update, Delete, Search | XML file with objects as elements |
| **SSH** | `openicf-ssh-connector` | Create, Delete, Search, custom | Remote commands (bash, PowerShell), parses output |
| **Kerberos/AD** | `openicf-ad-connector` | Create, Update, Delete, Search, Authenticate | LDAP + Kerberos, Windows-specific attributes |
| **Groovy Scripted** | `openicf-groovy-connector` | User-defined | Custom logic without Java compilation; quick prototyping |
| **HTTP/REST** | `openicf-http-connector` | Depends on API | JSON/XML, OAuth2/API key auth, customizable endpoints |
| **PowerShell** | similar to SSH | Windows-specific | Active Directory module integration |

**Connector Registration:** Each connector JAR includes `META-INF/services/org.identityconnectors.framework.spi.Connector` for service loader discovery at runtime.

---

## Design Patterns Summary

| Pattern | Component | Use Case | Key Classes |
|---------|-----------|----------|-------------|
| JAAS Integration | OpenAM | Auth chains | `AMLoginModule`, `AMLoginContext` |
| Chain of Responsibility | OpenAM | Auth module flow | `AMAuthenticationManager` |
| Strategy | All | Pluggable implementations | `Backend`, `GrantTypeHandler`, SPIOperation |
| Factory | All | Object creation | `OAuth2ProviderSettingsFactory`, `ConnectorInfoManager` |
| Repository | OpenAM, OpenDJ, OpenIDM | Data persistence | `SessionService`, `Backend`, ManagedObject |
| Adapter | OpenDJ, OpenIG | Interface translation | Rest2Ldap, `CredentialReplayFilter` |
| Decorator | OpenIG, OpenDJ | Wrapping/enhancement | Filter, OperationWrapper |
| Interceptor | OpenIG, OpenIDM | Request interception | Filter pipeline, RouterFilterRegistration |
| Facade | OpenICF, OpenIG | Simplified interface | `ConnectorFacade`, `ClientHandler` |
| Service Locator | OpenIDM | Service discovery | OSGi service registry |
| Remote Proxy | OpenICF | RPC transparency | `RemoteConnectorInfoManager` |
| Observer | OpenDJ, OpenIDM | Event notification | Plugin system, SyncListener |
| Pipeline | OpenIG, OpenDJ | Sequential processing | Filter chain, Operation pipeline |
| Template Method | OpenAM, OpenDJ | Customization points | `AMLoginModule`, `Backend` abstract classes |
| Builder | OpenAM, OpenIG | Complex object creation | RouteBuilder, PolicyBuilder |
| Trie | OpenIDM, OpenIG | Path routing | `RouterRegistryImpl`, `RouterHandler` |
| ETL | OpenIDM | Data transformation | SyncEngine, Mapping |
| Event Sourcing | OpenDJ | Change tracking | Changelog, CSN |
| Reactive Streams | OpenDJ | Async processing | RxJava 3 in opendj-core |

---

## Cross-Component Integration Points

**OpenAM <-> OpenDJ:**
- OpenDJ stores identities + policies (LDAP backend)
- OpenAM reads user profiles + auth config from OpenDJ
- Session storage can use OpenDJ (via CTS)

**OpenAM <-> OpenIDM:**
- OpenIDM can invoke OpenAM for authentication (REST call)
- OpenAM can trigger OpenIDM workflows on auth events

**OpenIDM <-> OpenICF:**
- OpenICF connectors as provisioning targets
- Router dispatches `/system/*` -> ConnectorFacade -> external systems

**OpenIDM <-> OpenDJ:**
- OpenDJ as identity store backend for managed objects
- Sync mappings: `managed/user` <-> `system/ldap/account`

**OpenIG <-> OpenAM:**
- OpenIG delegates auth/policy decisions to OpenAM
- OAuth2/OIDC integration via OpenAM as auth server

**OpenIG <-> OpenICF:**
- OpenIG can provision users via connectors (if custom filter)
- Typical flow: OpenIG authenticates -> OpenIDM provisions

---

## Known Gaps

- **OpenAM Authentication Trees:** The newer tree-based authentication (as opposed to chain-based) was not fully traced; OIP OpenAM 16.x may have partial tree support but the agent focused on the chain model.
- **OpenDJ Replication Classes:** Exact class names within the replication package were inferred from module structure rather than fully traced through source code.
- **OpenIDM Sync Engine Internals:** The exact class names for `SyncEngine` and `ReconService` were inferred from module structure and REST route patterns rather than direct source inspection.
- **OpenIG Filter Count:** The 50+ filter count is estimated from module structure; some filters may be in extension modules not present in the base repo.
- **OpenICF Protobuf Definitions:** The exact `.proto` file definitions were inferred from framework class structure rather than reading the actual protobuf schema files.
- **Workflow Integration:** The Activiti BPMN integration in OpenIDM was not deeply traced beyond route and module identification.
- **OpenIDM OrientDB vs JDBC:** The dual-repository architecture (OrientDB and JDBC) was identified but the selection mechanism and migration path between them was not fully explored.
