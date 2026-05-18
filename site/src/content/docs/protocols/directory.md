---
title: Directory Services
description: "LDAPv3, OpenDJ, 389 DS, and the future of directory services as SCIM replaces LDAP provisioning."
sidebar:
  order: 5
---

# Chapter 5: Directory Services

Directory services provide hierarchical data storage optimized for read-heavy workloads, attribute-based queries, and identity management. The Lightweight Directory Access Protocol (LDAPv3) has dominated directory services for nearly three decades, surviving multiple waves of technological change. This chapter examines LDAPv3's protocol design, OpenDJ's implementation architecture, gateway protocols bridging LDAP to modern APIs, and the evolution toward cloud directories.

## LDAPv3: The Universal Directory Protocol

LDAP (Lightweight Directory Access Protocol) emerged in 1993 as a simplified access protocol for X.500 directories. While X.500 required the full OSI protocol stack, LDAP ran directly over TCP/IP, making directory access practical for internet-scale deployments. LDAPv3, standardized in 1997 (RFC 2251) and revised in 2006 (RFC 4510-4519), remains the definitive directory protocol.

### Protocol Design and Operations

LDAPv3 is a client-server protocol using a request-response model over TCP port 389 (unencrypted) or 636 (LDAPS, LDAP over TLS). StartTLS (RFC 4511) allows upgrading an unencrypted connection to TLS on port 389.

**Core protocol operations:**

**Bind (Authentication)**: Client authenticates to the directory server. Three bind types:

- **Simple bind**: Client sends DN and password in cleartext. Requires TLS to prevent credential exposure.
- **SASL bind** (RFC 4511, RFC 4513): Extensible authentication framework supporting EXTERNAL (TLS client cert), DIGEST-MD5 (challenge-response), GSSAPI (Kerberos), PLAIN, and custom mechanisms. SASL provides mechanism negotiation and supports multi-step authentication.
- **Anonymous bind**: No credentials provided. Server grants limited access based on anonymous user rights.

**Search**: Query the directory tree. Parameters:

- **Base DN**: Starting point for search (e.g., `ou=users,dc=example,dc=com`)
- **Scope**: Base (base DN only), One (immediate children), Sub (entire subtree)
- **Filter**: Boolean expression matching entry attributes (see filter syntax below)
- **Attributes**: List of attributes to return (empty list = all attributes, explicit list = selected attributes)
- **Size limit**: Maximum entries to return
- **Time limit**: Maximum seconds for search execution
- **Controls**: Extensions modifying search behavior (paging, sorting, persistent search)

**Add**: Create a new entry. Client specifies DN and attribute set. Entry must conform to schema (objectClass constraints, required attributes, attribute syntax).

**Modify**: Update existing entry attributes. Operations:

- **Add**: Add new attribute values (multi-valued attributes) or add new attribute type
- **Delete**: Remove attribute values or entire attribute
- **Replace**: Replace all values of an attribute with new values
- **Increment**: Atomic increment for integer attributes (RFC 4525)

**Delete**: Remove an entry. Entry must be a leaf (no children) unless server supports the subtree delete control (OID 1.2.840.113556.1.4.805, defined in draft-armijo-ldap-treedelete).

**ModifyDN**: Rename or move an entry. Parameters:

- **Old DN**: Current entry DN
- **New RDN**: New relative DN (e.g., change `cn=John Smith` to `cn=John Doe`)
- **Delete old RDN**: Remove old RDN attribute values
- **New superior DN**: Move entry to new parent (optional, not all servers support)

**Compare**: Test if an entry has a specific attribute value. Efficient for access control checks without retrieving full entry. Returns true/false/error.

**Extended operation**: Generic extension mechanism (RFC 4511). Standard extended operations:

- **StartTLS** (RFC 4511): Upgrade connection to TLS
- **Modify password** (RFC 3062): Change user password with old password verification
- **Who Am I** (RFC 4532): Query current authenticated identity
- **Cancel** (RFC 3909): Cancel an in-progress operation

**Abandon**: Client requests server to stop processing an operation. Server may ignore (best-effort).

**Unbind**: Client terminates connection. Server closes TCP connection.

### Search Filter Syntax

LDAP search filters use prefix notation with logical operators:

**Equality**: `(attribute=value)` matches entries where attribute equals value. Example: `(uid=alice)`, `(mail=alice@example.com)`

**Substring**: `(attribute=*substring*)` matches entries where attribute contains substring. Wildcards:
- `(cn=*Smith)` - ends with "Smith"
- `(cn=John*)` - starts with "John"
- `(cn=*Doe*)` - contains "Doe"
- `(cn=John*Smith)` - starts with "John", ends with "Smith"

**Presence**: `(attribute=*)` matches entries that have the attribute (any value).

**Greater than/less than**: `(attribute>=value)`, `(attribute<=value)` - lexicographic comparison for strings, numeric for integers.

**Approximate match**: `(attribute~=value)` - fuzzy match (server-defined algorithm, often Soundex or Metaphone).

**Extensible match**: `(attribute:dn:matchingRule:=value)` - custom matching rules. Example: `(cn:caseIgnoreMatch:=john)`.

**Logical operators**:

- **AND**: `(&(filter1)(filter2)...)` - all filters must match
- **OR**: `(|(filter1)(filter2)...)` - at least one filter must match
- **NOT**: `(!(filter))` - filter must not match

**Complex example**:

```
(&
  (objectClass=inetOrgPerson)
  (|
    (departmentNumber=Engineering)
    (departmentNumber=Research)
  )
  (!(employeeType=Contractor))
  (mail=*@example.com)
)
```

Matches: inetOrgPerson entries in Engineering or Research departments, excluding contractors, with email addresses ending in @example.com.

**Filter performance considerations**:

- Indexed attributes (uid, cn, mail) enable fast searches
- Non-indexed attributes require full table scans
- Substring filters with leading wildcards (`*value`) cannot use indexes (some servers use trigram indexes)
- Complex filters with many OR branches may be slow; denormalize data or use multiple searches

### Controls and Extensions

LDAP controls (RFC 4511) modify operation behavior without changing the protocol. Controls are attached to requests and responses.

**Critical vs. non-critical**: Controls marked critical cause the operation to fail if the server doesn't support the control. Non-critical controls are ignored if unsupported.

**Common controls:**

**Paged results** (RFC 2696): Retrieve search results in pages (batches). Client specifies page size; server returns results plus a cookie for the next page. Essential for large result sets to avoid memory exhaustion.

**Server-side sort** (RFC 2891): Sort search results by specified attributes before returning to client. Reduces client-side sorting overhead.

**Virtual list view (VLV)** (draft): Retrieve a "window" of sorted results (e.g., entries 100-200 of sorted list). Used for scrolling interfaces.

**Persistent search** (draft): Client subscribes to change notifications. Server sends search results, then streams updates (adds, modifies, deletes) as they occur. Used for real-time synchronization and replication.

**ManageDsaIT** (RFC 3296): Treat referrals as regular entries (manage directory server info). Allows modification of referral entries.

**Proxy authorization** (RFC 4370): Perform operation on behalf of another user. Control specifies target user DN. Requires authorization to proxy.

**Subtree delete** (draft): Delete an entry and all descendants in one operation. Server extension; not universally supported.

**OpenDJ-specific controls** (inferred from module structure):

- **GetEffectiveRights**: Determine what operations a user can perform on an entry (access control evaluation without modifying data)
- **Account usability**: Check if an account is locked, expired, or password needs reset
- **Password policy**: Retrieve password policy state (expiration, grace logins remaining)

### Schema and ObjectClasses

LDAP schema defines the structure of directory data:

**Attribute types**: Define attribute names, syntax (data type), matching rules (comparison behavior), and whether attributes are single-valued or multi-valued.

Example attribute definition:

```
attributeType: ( 0.9.2342.19200300.100.1.3
  NAME 'mail'
  EQUALITY caseIgnoreIA5Match
  SUBSTR caseIgnoreIA5SubstringsMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{256} )
```

- OID: 0.9.2342.19200300.100.1.3 (unique identifier)
- NAME: 'mail' (human-readable name)
- EQUALITY: caseIgnoreIA5Match (case-insensitive comparison)
- SUBSTR: substring matching rule
- SYNTAX: IA5 String (ASCII), max 256 characters

**ObjectClasses**: Define entry types. Each objectClass specifies:

- **MUST**: Required attributes (entry must have these)
- **MAY**: Optional attributes (entry can have these)
- **SUP**: Superclass (inheritance)
- **STRUCTURAL** vs. **AUXILIARY**: Structural defines entry type (one per entry); auxiliary provides additional attributes (multiple allowed)

Example objectClass:

```
objectClass: ( 2.5.6.6
  NAME 'person'
  SUP top
  STRUCTURAL
  MUST ( cn $ sn )
  MAY ( userPassword $ telephoneNumber $ seeAlso $ description ) )

objectClass: ( 2.5.6.7
  NAME 'organizationalPerson'
  SUP person
  STRUCTURAL
  MAY ( title $ x121Address $ registeredAddress $ destinationIndicator $
        preferredDeliveryMethod $ telexNumber $ teletexTerminalIdentifier $
        telephoneNumber $ internationaliSDNNumber $
        facsimileTelephoneNumber $ street $ postOfficeBox $ postalCode $
        postalAddress $ physicalDeliveryOfficeName $ ou $ st $ l ) )

objectClass: ( 2.16.840.1.113730.3.2.2
  NAME 'inetOrgPerson'
  SUP organizationalPerson
  STRUCTURAL
  MAY ( audio $ businessCategory $ carLicense $ departmentNumber $
        displayName $ employeeNumber $ employeeType $ givenName $
        homePhone $ homePostalAddress $ initials $ jpegPhoto $
        labeledURI $ mail $ manager $ mobile $ o $ pager $
        photo $ roomNumber $ secretary $ uid $ x500uniqueIdentifier $
        preferredLanguage $ userSMIMECertificate $ userPKCS12 ) )
```

**Common objectClasses**:

- **top**: Base of objectClass hierarchy (all entries must have top)
- **person**: Basic person entry (cn, sn required)
- **organizationalPerson**: Person with organizational attributes (title, phone)
- **inetOrgPerson**: Internet person (email, photo, employee number)
- **groupOfNames**: Group with member attribute (DN-valued)
- **groupOfUniqueNames**: Group with uniqueMember
- **organization**: Organization entry (o, businessCategory)
- **organizationalUnit**: Organizational unit (ou)

**Schema extensibility**: Administrators can define custom attribute types and objectClasses. Schema definitions are stored in the directory (cn=schema entry) and loaded at server startup.

### Why LDAP Persists

Despite being nearly 30 years old, LDAP remains ubiquitous:

**1. Universal adoption**: Every major identity platform supports LDAP: Active Directory, OpenDJ, OpenLDAP, 389 DS, FreeIPA, Ping Directory. Billions of identity records stored in LDAP directories worldwide.

**2. Mature ecosystem**: LDAP client libraries exist for every programming language. System authentication (PAM/NSS on Linux), application integration (JNDI in Java), and federation (SAML/OIDC IdPs use LDAP backends) all rely on LDAP.

**3. Performance characteristics**: LDAP is optimized for read-heavy workloads (90%+ reads in typical deployments). Attribute indexing provides millisecond query times for filtered searches. Connection pooling and persistent connections reduce overhead.

**4. Hierarchical data model**: The tree structure naturally represents organizational hierarchies (organizations, departments, users). DN-based relationships enable efficient parent-child queries.

**5. Rich query language**: LDAP filters provide expressive queries without SQL's complexity. Attribute-based queries map naturally to identity lookups ("find all users in Engineering department with manager=alice").

**6. Multi-master replication**: LDAPv3 servers support eventual consistency across replicas. Write operations can occur on any server; changes propagate to peers. This enables geographically distributed directories with local read performance.

**7. Security model**: Access control lists (ACI in OpenDJ/389, ACL in OpenLDAP) provide fine-grained permissions at the entry and attribute level. LDAP over TLS encrypts traffic. SASL supports strong authentication mechanisms.

**8. Standards compliance**: LDAP is an IETF standard with formal specifications. Interoperability between vendors is high. Migration between directory servers is feasible (LDIF interchange format).

**9. Operational maturity**: Decades of operational knowledge. Backup/restore, replication, schema management, and performance tuning are well-understood. Tools and monitoring solutions are mature.

**10. Resistance to displacement**: While REST APIs and SQL databases could theoretically replace LDAP, the ecosystem investment (applications, authentication systems, administrative tools) creates immense inertia. Migrating away from LDAP requires rewriting authentication logic across thousands of applications.

## OpenDJ Implementation Architecture

OpenDJ (Open Identity Platform, version 5.0.3) is a high-performance LDAPv3 directory server with modular backend architecture, multi-master replication, and REST gateway capabilities. The server consists of 26+ modules totaling over 1,900 Java files.

### Backend Abstraction Layer

OpenDJ separates the LDAP protocol layer from storage via a backend abstraction. This enables multiple storage engines without changing protocol handling.

**Core classes** (`OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/`):

**DirectoryServer** (`core/DirectoryServer.java`): Singleton managing all server components. Responsibilities:

- Server initialization and shutdown
- Backend registration and lifecycle management
- Connection handler registration (LDAP, LDAPS, HTTP)
- Plugin management (pre-operation, post-operation)
- Schema loading and validation
- Configuration management (config.ldif parsing)

The DirectoryServer class coordinates startup sequence:

```
1. Load configuration from config/config.ldif
2. Initialize schema (load schema/ directory LDIF files)
3. Initialize backends (JE, SQL, custom)
4. Initialize replication (if configured)
5. Initialize connection handlers (LDAP listener on 1389, LDAPS on 1636)
6. Initialize plugins (access control, referrals, password policy)
7. Start all components
8. Mark server as online
```

**Backend interface** (`api/Backend.java`): SPI for storage backends. Core methods:

```java
public interface Backend {
    void initializeBackend() throws InitializationException;
    void finalizeBackend();

    boolean entryExists(DN entryDN);
    Entry getEntry(DN entryDN);
    void addEntry(Entry entry, AddOperation addOperation);
    void deleteEntry(DN entryDN, DeleteOperation deleteOperation);
    void replaceEntry(Entry oldEntry, Entry newEntry, ModifyOperation modifyOperation);
    void renameEntry(DN currentDN, Entry entry, ModifyDNOperation modifyDNOperation);

    void search(SearchOperation searchOperation);

    Set<DN> getBaseDNs();
    boolean supportsBackup();
    boolean supportsRestore();

    // Indexing
    Set<String> getSupportedControls();
    Set<String> getSupportedFeatures();
}
```

**LocalBackend** (`api/LocalBackend.java`): Extends Backend for local storage implementations. Adds:

- Transaction support (begin, commit, rollback)
- Export/import (LDIF)
- Backup/restore
- Index management
- Compact operation (reclaim space)

**Available backend implementations:**

**Berkeley DB Java Edition (JE)**: Default backend. ACID-compliant transactional key-value store. OpenDJ uses JE for:

- **id2entry**: Entry storage (entry ID -> LDIF bytes)
- **dn2id**: DN-to-ID index
- **Attribute indexes**: One JE database per indexed attribute (attribute value -> entry ID set)
- **Changelog**: Replication change sequence number (CSN) to change record mapping

JE provides:

- Hot backup (backup while server running)
- Database compaction (reduce file size after deletes)
- Cache tuning (configurable JE cache size)
- Transaction durability options (sync, write-no-sync, no-sync)

Configuration (config.ldif excerpt):

```
dn: ds-cfg-backend-id=userRoot,cn=Backends,cn=config
objectClass: ds-cfg-local-db-backend
ds-cfg-backend-id: userRoot
ds-cfg-base-dn: dc=example,dc=com
ds-cfg-db-directory: db
ds-cfg-enabled: true
ds-cfg-writability-mode: enabled
ds-cfg-db-cache-percent: 50
```

**SQL backend** (experimental): Maps LDAP to relational tables. Schema:

- **ldap_entries**: (entry_id, dn, objectclasses, attributes JSON)
- **ldap_attributes**: (entry_id, attribute_name, attribute_value) for indexed attributes
- **ldap_changelog**: Replication changes

Supports PostgreSQL, MySQL, Oracle, SQL Server. Useful for integrating LDAP with existing SQL infrastructure or leveraging SQL analytics on identity data.

**In-memory backend**: Stores all entries in heap memory. Fast but no persistence. Used for:

- Temporary directories (test data)
- Configuration storage (cn=config, cn=schema, cn=monitor)
- Small, static datasets (root DSE)

**Pluggable backend** (PDB): Generic plugin interface for community-developed backends. Custom backends implement the Backend interface and register via configuration.

**Backend selection at startup**:

```
DirectoryServer.initializeBackends():
  for each backend in config:
    className = backend.getAttribute("ds-cfg-java-class")
    backendClass = ClassLoader.loadClass(className)
    backendInstance = backendClass.newInstance()
    backendInstance.initializeBackend(config)
    registerBackend(baseDNs, backendInstance)
```

Backends are instantiated via reflection, allowing dynamic backend loading without recompilation.

### Multi-Master Replication

OpenDJ supports multi-master replication (all servers are writable) using change sequence number (CSN) based conflict resolution. The replication module is located at `OpenDJ/opendj-server-legacy/src/main/java/org/opends/server/replication/`.

**Replication architecture components:**

**Replication Domain**: Per-suffix replication state. Each replicated suffix (e.g., dc=example,dc=com) has a replication domain tracking:

- Replication server connections
- Local server ID
- Changelog database
- CSN generator

**Replication Server**: Optional hub for replication traffic. Instead of full mesh topology (N servers with N*(N-1)/2 connections), servers connect to replication servers (star topology). Replication servers store changelog history and forward changes between servers. Reduces connection overhead in large deployments.

**Replication Broker**: Client connection to replication server. Sends local changes and receives remote changes.

**Change Sequence Number (CSN)**: Globally unique change identifier. Format:

```
<timestamp>.<serverID>.<sequenceNumber>.<operation_id>
Example: 20250213143000.000Z#000001#0001#000001
```

Components:

- **timestamp**: Millisecond-precision UTC timestamp (format: yyyyMMddHHmmss.SSS)
- **serverID**: Unique server identifier (1-127)
- **sequenceNumber**: Per-server monotonic counter (handles multiple changes in same millisecond)
- **operation_id**: Sub-operation identifier for multi-step operations

CSN properties:

- **Totally ordered**: CSNs can be compared lexicographically for global ordering
- **Causality**: Later CSN implies later wall-clock time (with clock skew tolerance)
- **Collision-free**: Multiple servers generate unique CSNs even for simultaneous changes

**Replication flow:**

```
1. Client writes to Server A (add user alice)
2. Server A backend processes write, stores entry
3. Server A generates CSN: 20250213143000Z#000001#0001#000001
4. Server A records change in local changelog:
   {
     "csn": "20250213143000Z#000001#0001#000001",
     "changeType": "add",
     "dn": "uid=alice,ou=users,dc=example,dc=com",
     "entry": "... LDIF ..."
   }
5. ReplicationBroker on Server A sends change to ReplicationServer
6. ReplicationServer forwards change to Server B, Server C brokers
7. Server B receives change, validates CSN is newer than last applied
8. Server B applies change to local backend
9. Server B updates replication state (last applied CSN)
10. Server B records change in local changelog (for serving other replicas)
```

**Conflict resolution:**

Conflicts occur when multiple servers modify the same entry simultaneously. OpenDJ uses CSN ordering for deterministic resolution:

**Modify-modify conflict**: Two servers modify different attributes of the same entry. Resolution: Apply both changes. Each attribute modification has its own CSN. The server merges changes, preserving all modifications.

**Delete-modify conflict**: Server A deletes entry, Server B modifies entry. Resolution: CSN comparison. If delete CSN > modify CSN, delete wins (entry is deleted). If modify CSN > delete CSN, modify wins (entry exists with modifications). This ensures eventual consistency: all servers converge to the same state based on CSN ordering.

**Add-add conflict**: Two servers add entries with the same DN. Resolution: Both adds succeed, but one entry gets renamed to a unique DN (DN with conflict marker added). Example: `uid=alice,ou=users,dc=example,dc=com` becomes `uid=alice+conflict-<serverID>-<csn>,ou=users,dc=example,dc=com`.

**Rename conflict**: Two servers rename the same entry to different DNs. Resolution: CSN ordering determines final DN. Losing rename is treated as conflict and entry gets conflict marker.

**Changelog database**: Each server maintains a changelog storing recent changes (configurable retention period, default 3 days). Changelog is a JE database mapping CSN to change record. Used for:

- Replication: Serve changes to other servers
- External changelog (ECL): Allow clients to poll for changes (persistent search alternative)

**Configuration** (config.ldif excerpt):

```
dn: cn=Replication Server,cn=Multimaster Synchronization,cn=Synchronization Providers,cn=config
objectClass: ds-cfg-replication-server
cn: Replication Server
ds-cfg-replication-port: 8989
ds-cfg-replication-server-id: 1
ds-cfg-replication-db-directory: changelogDb

dn: cn=dc=example\,dc=com,cn=domains,cn=Multimaster Synchronization,cn=Synchronization Providers,cn=config
objectClass: ds-cfg-replication-domain
cn: dc=example,dc=com
ds-cfg-base-dn: dc=example,dc=com
ds-cfg-server-id: 1
ds-cfg-replication-server: localhost:8989
```

**External Changelog (ECL)**:

OpenDJ exposes the changelog via LDAP searches on `cn=changelog` base DN. Clients can poll for changes:

```
ldapsearch -h localhost -p 1389 -D "cn=admin" -w password \
  -b "cn=changelog" "(targetDN=uid=*,ou=users,dc=example,dc=com)" \
  changeNumber changeType targetDN changes
```

Response:

```
dn: changeNumber=1,cn=changelog
changeNumber: 1
changeType: add
targetDN: uid=alice,ou=users,dc=example,dc=com
changes:: <base64-encoded LDIF>

dn: changeNumber=2,cn=changelog
changeNumber: 2
changeType: modify
targetDN: uid=alice,ou=users,dc=example,dc=com
changes:: <base64-encoded LDIF>
```

ECL enables synchronization with external systems without requiring persistent search connections.

### Connection Handling and RxJava

OpenDJ uses reactive programming patterns via RxJava 3 for connection handling and I/O operations. The reactive approach enables:

- Non-blocking I/O (Netty-based)
- Backpressure handling (slow clients don't block server)
- Asynchronous operation processing
- Efficient resource utilization (fewer threads)

**Core classes** (`OpenDJ/opendj-core/src/main/java/org/forgerock/opendj/ldap/`):

**LDAPListener**: Server-side LDAP connection listener. Accepts incoming TCP connections, performs bind, and dispatches operations.

**LDAPConnectionFactory**: Client-side connection factory. Provides connection pooling and load balancing across multiple servers.

**LDAPConnection**: Represents a single client-server connection. Sends requests, receives responses.

**ServerConnectionFactory**: SPI for server-side connection handling. Custom implementations can provide authentication, authorization, and operation handling logic.

**Reactive search example**:

```java
// Client-side: search returns Promise<SearchResultEntry>
LDAPConnectionFactory factory = new LDAPConnectionFactory("localhost", 1389);
Connection connection = factory.getConnection();

SearchRequest request = Requests.newSearchRequest(
    "ou=users,dc=example,dc=com",
    SearchScope.WHOLE_SUBTREE,
    "(uid=a*)", "cn", "mail");

// Async search with reactive callback
LdapPromise<SearchResultEntry> promise = connection.searchAsync(request);

promise.thenOnResult(entry -> {
    System.out.println("Found: " + entry.getName());
})
.thenOnException(error -> {
    System.err.println("Search failed: " + error);
})
.thenOnResultOrException(new Runnable() {
    public void run() {
        connection.close();
    }
});
```

**Server-side reactive pipeline**:

```
TCP connection accepted (Netty)
  -> LDAPReader decodes LDAP messages
  -> OperationWrapper created (contains request)
  -> WorkQueue dispatches to thread pool
  -> Backend.search() executes query
  -> Results stream back via reactive Flowable
  -> LDAPWriter encodes response messages
  -> TCP socket write (Netty)
```

RxJava's backpressure mechanisms prevent fast backends from overwhelming slow clients. If a client cannot consume search results quickly, the server buffers and throttles backend operations.

### Request Processing Pipeline

OpenDJ's operation pipeline processes every LDAP request through a series of plugin stages:

**Pipeline architecture**:

```
Client Request
  |
LDAP Protocol Parser (decode BER)
  |
Pre-Operation Plugins
  |  - AccessControlPlugin (evaluate ACI)
  |  - Schema validation
  |  - Password policy checks
  |  - Custom pre-operation plugins
  |
Backend Operation (read/write)
  |
Post-Operation Plugins
  |  - Replication (generate CSN, update changelog)
  |  - Audit logging
  |  - Referral processing
  |  - Custom post-operation plugins
  |
LDAP Protocol Formatter (encode BER)
  |
Client Response
```

**Plugin types**:

**Pre-parse plugins**: Execute before request parsing (connection-level inspection).

**Pre-operation plugins**: Execute after parsing, before backend operation. Can:

- Modify request parameters
- Validate request (reject if invalid)
- Perform preliminary authorization checks
- Trigger external systems (webhooks, notifications)

**Post-operation plugins**: Execute after backend operation completes. Can:

- Modify response
- Trigger post-operation actions (replication, audit)
- Update derived data (group membership, virtual attributes)

**Search result plugins**: Filter search results (remove attributes, add virtual attributes).

**Intermediate response plugins**: Process intermediate responses (referrals, search references).

**Example plugin: MemberOf**:

The MemberOf plugin maintains a `memberOf` virtual attribute on user entries listing groups the user belongs to. When a group's `member` attribute is updated, the plugin:

1. Post-modify plugin detects change to `member` attribute
2. Extracts added and removed member DNs
3. Updates `memberOf` attribute on affected user entries
4. Logs changes for replication

This avoids expensive searches for "find all groups this user belongs to" by maintaining reverse pointers.

**Access Control Plugin**:

OpenDJ's access control plugin evaluates ACI (Access Control Instructions) at pre-operation stage. ACI syntax:

```
aci: (target="ldap:///ou=users,dc=example,dc=com")
     (targetattr="*")
     (version 3.0; acl "Allow read to all users";
      allow (read,search,compare)
      userdn="ldap:///all";)
```

ACI components:

- **target**: LDAP URL specifying affected entries (subtree, filter)
- **targetattr**: Attributes affected (wildcard or list)
- **targetfilter**: Additional filter on target entries
- **permissions**: allow or deny
- **rights**: read, write, add, delete, search, compare, selfwrite, proxy
- **userdn**: Subject (who the ACI applies to)

ACI evaluation:

```
1. Client attempts operation (e.g., search)
2. AccessControlPlugin intercepts
3. Load all ACIs applying to target DN and attributes
4. Evaluate ACIs in order (deny-overrides combining)
5. If any ACI denies: reject operation
6. If any ACI allows: permit operation
7. If no ACI matches: deny (default-deny)
```

ACIs are stored as operational attributes on entries (each entry can have local ACIs) or globally in `cn=config`. This enables delegated administration: departments can manage ACIs for their subtree without global admin access.

## DSML v2: SOAP Gateway to LDAP

Directory Services Markup Language v2 (DSML, OASIS standard 2002) provides an XML/SOAP interface to LDAP directories. DSML was an early attempt to web-enable LDAP, predating REST by several years.

### Protocol Design

DSML v2 defines XML schema for LDAP operations and responses, transmitted via SOAP over HTTP. Each LDAP operation has an equivalent DSML XML representation.

**DSML add operation (XML)**:

```xml
<batchRequest xmlns="urn:oasis:names:tc:DSML:2:0:core">
  <addRequest dn="uid=alice,ou=users,dc=example,dc=com">
    <attr name="objectClass">
      <value>inetOrgPerson</value>
      <value>organizationalPerson</value>
      <value>person</value>
      <value>top</value>
    </attr>
    <attr name="cn">
      <value>Alice Anderson</value>
    </attr>
    <attr name="sn">
      <value>Anderson</value>
    </attr>
    <attr name="mail">
      <value>alice@example.com</value>
    </attr>
  </addRequest>
</batchRequest>
```

**DSML search operation (XML)**:

```xml
<batchRequest xmlns="urn:oasis:names:tc:DSML:2:0:core">
  <searchRequest dn="ou=users,dc=example,dc=com" scope="wholeSubtree">
    <filter>
      <equalityMatch name="mail">
        <value>alice@example.com</value>
      </equalityMatch>
    </filter>
    <attributes>
      <attribute name="cn"/>
      <attribute name="mail"/>
    </attributes>
  </searchRequest>
</batchRequest>
```

**DSML batch operations**: Multiple operations can be batched in a single HTTP request, processed sequentially. Batch processing modes:

- **Sequential**: Execute operations in order; stop on first error
- **Parallel**: Execute operations concurrently (server discretion)
- **Unordered**: Server chooses execution order

### OpenDJ DSML Servlet

OpenDJ provides a DSML servlet located at `OpenDJ/opendj-dsml-servlet/`. The servlet architecture:

**DSMLServlet** (`org.opends.dsml.protocol.DSMLServlet`): HTTP servlet handling DSML requests. Steps:

```
1. Receive HTTP POST with SOAP envelope containing DSML batch request
2. Parse SOAP/DSML XML (SAX parser)
3. Extract DSML operations (add, modify, delete, search, compare, modifyDN, abandon)
4. For each operation:
   a. Convert DSML to LDAP operation (DSMLAddOperation -> AddOperation)
   b. Execute operation against OpenDJ backend via LDAP connection
   c. Convert LDAP result to DSML response (ResultCode -> DSMLResultCode)
5. Construct DSML batch response XML
6. Wrap in SOAP envelope
7. Return HTTP 200 with SOAP response
```

**Operation classes**:

- `DSMLAddOperation`, `DSMLDeleteOperation`, `DSMLModifyOperation`
- `DSMLSearchOperation`, `DSMLCompareOperation`, `DSMLModifyDNOperation`
- `DSMLAbandonOperation`, `DSMLExtendedOperation`

Each operation class implements:

- `parseXML()`: Parse DSML XML into operation object
- `execute()`: Execute LDAP operation via connection
- `toXML()`: Convert result to DSML XML response

**Authentication**: DSML servlet supports HTTP Basic authentication. Credentials are passed to OpenDJ via LDAP bind.

**Deployment**: The DSML servlet runs in a servlet container (Jetty, Tomcat) as a WAR file. Configuration specifies OpenDJ connection parameters (host, port, bind DN).

### Why DSML Failed to Achieve Wide Adoption

DSML never achieved significant adoption:

**1. Timing**: DSML emerged in the early 2000s when SOAP was the dominant web services protocol. By the time LDAP directories needed web APIs, REST had displaced SOAP (2010s). DSML was SOAP-based, making it obsolete before it matured.

**2. Complexity**: DSML adds XML verbosity to LDAP's already complex data model. Simple LDAP operations require 50+ lines of XML. Developers preferred direct LDAP connections (less overhead) or REST APIs (simpler data formats).

**3. Limited tooling**: Few client libraries supported DSML. SOAP tooling (WSDL, code generation) did not align well with LDAP's dynamic schema and attribute-based queries.

**4. Performance overhead**: XML parsing and SOAP envelope processing added latency compared to binary LDAP protocol. For high-throughput applications, the overhead was unacceptable.

**5. No compelling use case**: DSML solved a problem that didn't exist. Applications needing web-based directory access adopted REST APIs (or waited for REST-to-LDAP gateways). DSML filled a narrow gap between LDAP and HTTP that REST filled more elegantly.

**6. Lack of vendor support**: Major directory vendors (Microsoft, Oracle, IBM) did not prioritize DSML. OpenDJ's DSML implementation exists for standards compliance, not because of market demand.

### Current Status

DSML v2 is a dormant standard. OpenDJ's DSML servlet is maintained for backward compatibility but not actively developed. REST2LDAP (described next) provides superior web API integration.

## REST2LDAP Gateway

OpenDJ's REST2LDAP gateway (`OpenDJ/opendj-rest2ldap/`, `OpenDJ/opendj-rest2ldap-servlet/`) provides a RESTful HTTP API for LDAP operations. Unlike DSML, REST2LDAP uses JSON payloads, standard HTTP methods, and modern authentication patterns (OAuth2, JWT).

### HTTP-to-LDAP Mapping

REST2LDAP maps HTTP requests to LDAP operations:

**Create entry** (POST):

```
POST /users
Content-Type: application/json

{
  "uid": "alice",
  "cn": "Alice Anderson",
  "sn": "Anderson",
  "mail": "alice@example.com",
  "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"]
}
```

Mapped to LDAP Add:

```
dn: uid=alice,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: alice
cn: Alice Anderson
sn: Anderson
mail: alice@example.com
```

**Read entry** (GET):

```
GET /users/alice
```

Mapped to LDAP Search:

```
base: uid=alice,ou=users,dc=example,dc=com
scope: base
filter: (objectClass=*)
attributes: * (all user attributes)
```

Response:

```json
{
  "_id": "alice",
  "_rev": "0000000000000001",
  "cn": ["Alice Anderson"],
  "sn": ["Anderson"],
  "mail": ["alice@example.com"],
  "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"]
}
```

System fields:

- `_id`: RDN value (uid=alice -> "alice")
- `_rev`: ETag for optimistic concurrency (CSN or modifyTimestamp)

**Update entry** (PUT):

```
PUT /users/alice
If-Match: 0000000000000001
Content-Type: application/json

{
  "_id": "alice",
  "_rev": "0000000000000001",
  "cn": ["Alice Anderson"],
  "sn": ["Anderson-Smith"],
  "mail": ["alice.smith@example.com"]
}
```

Mapped to LDAP Modify:

```
dn: uid=alice,ou=users,dc=example,dc=com
changetype: modify
replace: sn
sn: Anderson-Smith
-
replace: mail
mail: alice.smith@example.com
```

Optimistic locking: `If-Match` header contains `_rev` value. Server rejects update if current entry version doesn't match (prevents lost updates).

**Patch entry** (PATCH):

```
PATCH /users/alice
Content-Type: application/json

[
  { "operation": "replace", "field": "/mail/0", "value": "newemail@example.com" },
  { "operation": "add", "field": "/telephoneNumber/-", "value": "+1-555-1234" }
]
```

Mapped to LDAP Modify with specific operations (replace, add, delete).

**Delete entry** (DELETE):

```
DELETE /users/alice
```

Mapped to LDAP Delete:

```
dn: uid=alice,ou=users,dc=example,dc=com
```

**Query entries** (GET with filter):

```
GET /users?_queryFilter=mail eq "alice@example.com"
```

Mapped to LDAP Search:

```
base: ou=users,dc=example,dc=com
scope: subtree
filter: (mail=alice@example.com)
```

CREST query filter syntax:

- `mail eq "value"` -> `(mail=value)`
- `cn co "substring"` -> `(cn=*substring*)`
- `age gt 30` -> `(age>30)` (if age is integer attribute)
- `department eq "Engineering" and manager eq "alice"` -> `(&(department=Engineering)(manager=alice))`

Response (paginated):

```json
{
  "result": [
    { "_id": "alice", "cn": ["Alice Anderson"], "mail": ["alice@example.com"] }
  ],
  "totalPagedResults": 1,
  "pagedResultsCookie": null
}
```

### Authorization Plugins

REST2LDAP supports multiple authorization mechanisms via pluggable resolvers:

**RFC 7662 Token Introspection**: Validate OAuth2 access tokens by calling an introspection endpoint.

Configuration:

```json
{
  "authorization": {
    "oauth2": {
      "introspection-endpoint": "https://openam.example.com/oauth2/introspect",
      "client-id": "rest2ldap-client",
      "client-secret": "secret123",
      "scopes": ["ldap.read", "ldap.write"]
    }
  }
}
```

Flow:

```
1. Client sends: GET /users/alice
   Authorization: Bearer <access_token>
2. REST2LDAP extracts token
3. REST2LDAP calls introspection endpoint:
   POST https://openam.example.com/oauth2/introspect
   {
     "token": "<access_token>",
     "client_id": "rest2ldap-client",
     "client_secret": "secret123"
   }
4. OpenAM returns:
   {
     "active": true,
     "scope": "ldap.read ldap.write",
     "sub": "alice",
     "exp": 1676419200
   }
5. REST2LDAP checks required scopes (ldap.read present)
6. REST2LDAP binds to LDAP as alice (maps sub -> DN)
7. REST2LDAP executes LDAP search
8. Returns JSON response
```

**CTS (Core Token Service) Resolver**: Directly queries OpenAM's CTS for token validation (bypasses introspection endpoint). Requires REST2LDAP to have access to CTS LDAP backend.

**HTTP Basic Authentication**: Extract credentials from `Authorization: Basic` header, bind to LDAP with those credentials.

**Direct LDAP Bind**: Use credentials from HTTP request to bind to LDAP. If bind succeeds, authorization granted.

**Proxy Authorization**: REST2LDAP uses a privileged service account to bind to LDAP, then performs operations on behalf of authenticated user via proxy authorization control.

### JSON Schema Mapping

REST2LDAP uses mapping files to define JSON-to-LDAP transformations:

```json
{
  "baseDN": "ou=users,dc=example,dc=com",
  "readOnUpdatePolicy": "controls",
  "objectClasses": ["inetOrgPerson"],
  "attributes": {
    "uid": {
      "ldapAttribute": "uid",
      "isRequired": true,
      "isMultiValued": false
    },
    "name": {
      "ldapAttribute": "cn",
      "isRequired": true,
      "isMultiValued": true
    },
    "email": {
      "ldapAttribute": "mail",
      "isRequired": false,
      "isMultiValued": false
    },
    "password": {
      "ldapAttribute": "userPassword",
      "isRequired": false,
      "isMultiValued": false,
      "writability": "createOnly"
    }
  }
}
```

Mapping features:

- **Field name transformation**: JSON `name` maps to LDAP `cn`
- **Multi-valued handling**: JSON arrays map to multi-valued LDAP attributes
- **Writability**: `createOnly` (set on create, not updatable), `writeOnly` (never returned in GET), `readOnly` (never accepted in PUT/PATCH)
- **Default values**: Specify default attribute values for creates
- **Derived attributes**: Compute JSON fields from multiple LDAP attributes

### Current Usage

REST2LDAP is actively used in scenarios requiring modern API access to LDAP directories:

- **Frontend applications**: JavaScript/TypeScript apps calling LDAP without LDAP client libraries
- **Microservices**: Services needing identity data without maintaining LDAP connection pools
- **API gateways**: Centralizing identity lookups behind REST APIs
- **OAuth2 integration**: Validating OAuth2 tokens and accessing LDAP in one gateway

REST2LDAP provides a pragmatic bridge between legacy LDAP infrastructure and modern API-first architectures. Performance overhead is acceptable (milliseconds per request) for read-heavy workloads.

## Cloud Directory Evolution

Directory services have evolved from on-premises LDAP to cloud-native identity stores with REST APIs. This evolution reflects broader shifts toward SaaS, multi-tenancy, and API-first architectures.

### Virtual Directories

Virtual directories federate multiple identity sources behind a unified LDAP interface. Products like Radiant Logic VDS (Virtual Directory Server) aggregate:

- Multiple LDAP directories (Active Directory, OpenDJ, 389 DS)
- SQL databases (identity tables)
- REST APIs (cloud identity sources)
- Flat files (CSV, LDIF)

into a single virtual LDAP namespace.

**Use case**: Enterprise with fragmented identity landscape (HR system in Oracle, email in AD, contractors in CSV) exposes unified directory view to applications without migrating data.

**Architecture**:

```
Applications -> Virtual Directory (LDAP) -> Multiple Backends
                                           - AD (LDAP bind)
                                           - Oracle (JDBC)
                                           - REST API (HTTP)
```

Virtual directories apply transformations (attribute mapping, DN rewriting, filtering) and caching to present a coherent view.

**Limitations**:

- Performance overhead (extra network hop, transformation latency)
- Complex configuration (mapping rules can be intricate)
- Synchronization delays (caches may be stale)
- Limited write support (writes to virtual entries require complex proxying)

### Cloud Directories

Cloud identity providers abstract directory services behind REST APIs:

**Azure Active Directory** (rebranded Microsoft Entra ID): Microsoft's cloud directory. Stores user identities, groups, applications. Exposes:

- Microsoft Graph API (REST, primary interface)
- Azure AD Graph API (REST, legacy)
- LDAP interface (via Azure AD Domain Services, subset of full LDAP)

Entra ID is not a traditional LDAP directory. It stores identity data in proprietary format optimized for OAuth2/OIDC. The Graph API provides richer queries and relationships than LDAP.

**Google Cloud Directory** (Cloud Identity, Google Workspace): Google's cloud directory. Users, groups, devices. Exposes:

- Cloud Identity API (REST, gRPC)
- Directory API (REST)
- No native LDAP (third-party LDAP gateways available)

**AWS Directory Service**: Offers three options:

- **AWS Managed Microsoft AD**: Full Active Directory deployment managed by AWS. Native LDAP support.
- **AD Connector**: Proxy to on-premises AD. Allows AWS services to authenticate against existing AD without replication.
- **Simple AD**: Samba-based directory (LDAP-compatible subset). Lower cost, limited features.

AWS services integrate with Directory Service for authentication (SSO, IAM roles, EC2 domain join).

### SCIM 2.0 for Provisioning

SCIM (System for Cross-domain Identity Management) v2.0 (RFC 7642-7644, 2015) is the dominant standard for cloud identity provisioning. SCIM defines REST APIs for user and group lifecycle management.

**SCIM endpoints**:

- `POST /Users`: Create user
- `GET /Users/{id}`: Read user
- `PUT /Users/{id}`: Replace user (full update)
- `PATCH /Users/{id}`: Partial update
- `DELETE /Users/{id}`: Delete user
- `GET /Users?filter=userName eq "alice"`: Query users
- `/Groups`, `/ServiceProviderConfig`, `/ResourceTypes`, `/Schemas`: Additional endpoints

**SCIM user schema**:

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "id": "12345",
  "userName": "alice@example.com",
  "name": {
    "formatted": "Alice Anderson",
    "familyName": "Anderson",
    "givenName": "Alice"
  },
  "emails": [
    { "value": "alice@example.com", "type": "work", "primary": true }
  ],
  "active": true,
  "groups": [
    { "value": "67890", "$ref": "../Groups/67890", "display": "Engineering" }
  ]
}
```

**SCIM adoption**: Most SaaS applications support SCIM for inbound provisioning (receive user accounts from IdP). Identity providers (Okta, Entra ID, OneLogin) act as SCIM clients, pushing user changes to downstream applications.

**SCIM vs LDAP**:

| Dimension | LDAP | SCIM |
|-----------|------|------|
| Protocol | Binary (ASN.1 BER) | REST/JSON |
| Transport | TCP, TLS | HTTPS |
| Operations | 8 core operations | RESTful CRUD |
| Schema | Extensible (schema stored in directory) | Fixed core schema + extensions |
| Query | LDAP filters | URL query parameters with filters |
| Replication | Multi-master (built-in) | Not standardized |
| Use case | General directory | Cloud identity provisioning |
| Adoption | Universal (legacy and modern) | SaaS standard |

SCIM provides a web-friendly alternative to LDAP for identity synchronization. Organizations use SCIM to provision users from central IdP to SaaS applications, eliminating manual account creation.

**SCIM in OpenIDM**: OpenIDM provides SCIM 2.0 endpoints for managed objects. External systems can use SCIM to create/update users in OpenIDM, which then syncs to target systems via OpenICF connectors.

### From LDAP to Graph APIs

Modern identity platforms move beyond hierarchical LDAP to graph-based data models:

**Microsoft Graph**: Unified API for Microsoft 365, Entra ID, Intune. Exposes users, groups, devices, applications, mail, calendar, files as graph nodes with relationships. GraphQL-like query capabilities.

Example Graph API query:

```
GET https://graph.microsoft.com/v1.0/users/alice@example.com?$select=displayName,mail,manager&$expand=manager($select=displayName)
```

Response:

```json
{
  "displayName": "Alice Anderson",
  "mail": "alice@example.com",
  "manager": {
    "displayName": "Bob Smith"
  }
}
```

Graph APIs enable richer queries (transitive relationships, multi-hop traversals) than LDAP. However, they lack LDAP's standardization and interoperability.

### Why LDAP Persists Despite Cloud Directories

Cloud directories have not displaced LDAP:

**1. Ecosystem inertia**: Millions of applications integrate with LDAP. Rewriting authentication logic for Graph APIs is expensive. LDAP remains the common denominator.

**2. On-premises deployments**: Many enterprises run on-premises infrastructure where cloud directories are inaccessible or undesirable (data sovereignty, latency, cost).

**3. Hybrid environments**: Most organizations run hybrid (on-prem + cloud). LDAP provides consistent interface across both environments. Azure AD Domain Services and AWS Managed AD are cloud-hosted LDAP for this reason.

**4. Open standards**: LDAP is an IETF standard. Graph APIs are vendor-specific. Organizations value standards-based interoperability.

**5. Performance**: LDAP is optimized for attribute-based queries with millisecond latency. REST APIs add HTTP overhead (connection establishment, TLS handshake, JSON parsing). For high-throughput authentication, LDAP is faster.

**6. Feature richness**: LDAP supports advanced features (complex filters, attribute indexes, replication, access control) that REST APIs provide inconsistently or not at all.

LDAP will coexist with cloud directories for the foreseeable future. REST gateways (REST2LDAP, SCIM) bridge the two worlds without forcing wholesale migration.

## Summary

Directory services remain foundational to identity management. LDAPv3 persists due to universal adoption, mature tooling, and performance characteristics suited to read-heavy identity workloads. OpenDJ exemplifies modern LDAP implementation with backend abstraction, multi-master replication via CSN-based conflict resolution, and reactive I/O patterns.

DSML v2 failed as an XML/SOAP bridge to LDAP, rendered obsolete by REST. REST2LDAP provides pragmatic HTTP/JSON access to LDAP directories with OAuth2 integration and flexible authorization plugins.

Cloud directories abstract LDAP behind REST APIs (Microsoft Graph, Google Cloud Identity) and introduce graph-based data models. SCIM 2.0 standardizes cloud identity provisioning, supplementing LDAP for cross-domain synchronization.

Despite cloud evolution, LDAP remains the universal directory protocol, coexisting with cloud directories in hybrid deployments. REST2LDAP and SCIM bridge legacy LDAP infrastructure with modern API-first architectures without requiring migration.

References: OpenDJ source code at [github.com/OpenIdentityPlatform/OpenDJ](https://github.com/OpenIdentityPlatform/OpenDJ) (modules: opendj-core, opendj-server-legacy, opendj-rest2ldap). LDAP RFCs 4510-4519, DSML v2 (OASIS), SCIM RFCs 7642-7644.
