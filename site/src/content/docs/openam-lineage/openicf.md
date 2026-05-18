---
title: OpenICF Analysis
description: "Identity connector framework: 50+ connectors for LDAP, AD, databases, SaaS. The provisioning bridge between IDM and target systems."
sidebar:
  order: 6
---

# Chapter 11: OpenICF Analysis

OpenICF (Open Identity Connector Framework) is the integration layer of the Open Identity Platform suite, providing a standardized abstraction for connecting identity management systems to external data sources and applications. Its architecture splits cleanly into an API layer (what consumers call) and an SPI layer (what connector developers implement), bridging the gap through a framework that handles lifecycle management, class loading, connection pooling, and remote execution via Protobuf RPC. With 19 sub-modules and 9+ built-in connectors for LDAP, databases, CSV files, SSH, Kerberos, XML, HTTP, and Groovy scripting, OpenICF enables OpenIDM to provision and synchronize identities across heterogeneous environments. This chapter examines OpenICF's architecture, evaluates its strengths and limitations, compares it against modern integration approaches, and considers the broader question of whether connector frameworks remain the right abstraction for identity integration.

---

## 1. What OpenICF Does

Within the OIP architecture described in the project's `CLAUDE.md` and detailed in [Chapter 12: Modern Architecture Patterns](12-modern-architecture.md), OpenICF occupies the southernmost layer:

```
OpenIDM (provisioning/sync engine)
  --> OpenICF Connector Framework
    --> ConnectorFacade (API)
      --> Connector implementation (SPI)
        --> External system (LDAP, database, AD, cloud app, SSH host)
```

OpenICF solves three problems:

**Abstraction.** Every external system has its own interface -- LDAP uses bind/search/modify, databases use SQL, REST APIs use HTTP, SSH hosts use shell commands. OpenICF presents a unified CRUD + Sync + Authenticate interface to OpenIDM, hiding the protocol diversity behind `ConnectorFacade`. OpenIDM code that creates a user account is identical whether the target is an LDAP directory, a PostgreSQL database, or a remote Linux server.

**Remote execution.** Some external systems are accessible only from specific network locations -- an on-premises Active Directory domain controller, a mainframe behind a firewall, or a database in a private subnet. OpenICF's Remote Connector Server can be deployed adjacent to the target system, receiving connector operations over a Protobuf-based RPC channel from the OpenIDM host. This eliminates the need for OpenIDM to have direct network access to every target system.

**Lifecycle management.** Connector instances must be configured (connection parameters, credentials, timeouts), pooled (connection reuse for performance), health-checked, and cleanly shut down. The framework handles all of this, freeing connector developers to focus on the system-specific integration logic.

The commercial descendant of OpenICF is embedded within PingOne Advanced Identity Cloud (formerly ForgeRock Identity Cloud), where the connector framework continues to serve the same role within what is now Ping Identity's managed IDM service.

---

## 2. Architecture Overview

### 2.1 SPI/API Split

OpenICF's defining architectural decision is the separation between its **API** (consumer-facing) and **SPI** (implementor-facing) layers. Both reside in `OpenICF/OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/`.

**API layer** (`framework/api/`):

| Class | Purpose |
|-------|---------|
| `ConnectorFacade` | Primary client interface; all operations invoked here |
| `ConnectorInfo` | Metadata about a discovered connector (name, version, config schema) |
| `ConnectorInfoManager` | Discovers and manages available connectors |
| `ConnectorFacadeFactory` | Creates `ConnectorFacade` instances from connector metadata |
| `APIConfiguration` | Typed configuration object for connector initialization |

**SPI layer** (`framework/spi/`):

| Class | Purpose |
|-------|---------|
| `Connector` | Marker interface that all connectors implement |
| `@ConnectorClass` | Annotation declaring a class as a connector |
| `Configuration` | Base class for connector configuration properties |
| `SPIOperation` | Marker interface for operation capabilities |

The API layer is what OpenIDM (or any consumer) depends on. The SPI layer is what connector developers implement. The framework bridges the two at runtime through class loading, reflection, and operation dispatch. This separation serves three goals:

1. **Independent evolution.** The API can change between versions without breaking connectors, and vice versa.
2. **ClassLoader isolation.** Each connector runs in its own ClassLoader, preventing dependency conflicts between connectors that require different library versions.
3. **Pluggability.** New connectors are deployed as JAR files on the classpath. The framework discovers them via Java's `META-INF/services/org.identityconnectors.framework.spi.Connector` service loader mechanism.

### 2.2 Operation Interfaces

Connectors declare their capabilities by implementing specific SPI operation interfaces. A connector that supports only read operations implements only `SearchOp`; one that supports full lifecycle management implements `CreateOp`, `UpdateOp`, `DeleteOp`, `SearchOp`, and `SyncOp`.

**CRUD Operations:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `CreateOp` | `Uid create(ObjectClass, Set<Attribute>, OperationOptions)` | Create a resource; returns assigned unique ID |
| `UpdateOp` | `Uid update(ObjectClass, Uid, Set<Attribute>, OperationOptions)` | Update attributes on existing resource |
| `DeleteOp` | `void delete(ObjectClass, Uid, OperationOptions)` | Remove a resource |
| `SearchOp` | `void executeQuery(ObjectClass, Filter, ResultsHandler, OperationOptions)` | Query resources; streaming results via callback |

**Synchronization:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `SyncOp` | `void sync(ObjectClass, SyncToken, SyncResultsHandler, OperationOptions)` | Retrieve changes since last token; streaming deltas |

The `SyncOp` interface is the foundation of OpenIDM's LiveSync feature. A connector's `sync()` method returns `SyncDelta` objects, each containing a token (checkpoint), operation type (CREATE, UPDATE, DELETE), object class, unique ID, and changed attributes. OpenIDM stores the last sync token and resumes from that checkpoint on the next invocation.

**Authentication:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `AuthenticateOp` | `Uid authenticate(ObjectClass, String, GuardedString, OperationOptions)` | Validate credentials; returns UID or throws |

**Schema and Scripting:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `SchemaOp` | `Schema schema()` | Return resource schema (object classes, attributes, supported operations) |
| `ScriptOnResourceOp` | `Object runScriptOnResource(ScriptContext, OperationOptions)` | Execute a script on the target system |
| `ScriptOnConnectorOp` | `Object runScriptOnConnector(ScriptContext, OperationOptions)` | Execute a script within the connector JVM |

**Utility:**

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `ResolveUsernameOp` | `Uid resolveUsername(ObjectClass, String, OperationOptions)` | Convert username to unique ID |

The operation interface model is a pure Strategy pattern: each interface represents a capability, and the framework introspects which interfaces a connector implements to determine what operations it supports. The `Schema` returned by `SchemaOp` can further restrict operations per `ObjectClass` -- a connector might support CREATE for accounts but only SEARCH for groups.

### 2.3 Built-in Connectors

OpenICF ships with connectors for the most common enterprise integration targets:

| Connector | Bundle | Operations | Key Features |
|-----------|--------|------------|--------------|
| **LDAP** | `openicf-ldap-connector` | Create, Update, Delete, Search, Authenticate, Sync | TLS/SSL, connection pooling, paged results, password change, VLV |
| **Database (JDBC)** | `openicf-database-connector` | Create, Update, Delete, Search, Sync | SQL templates, transactions, timestamp-based change detection; PostgreSQL, MySQL, Oracle, SQL Server, H2 |
| **CSV** | `openicf-csv-connector` | Create, Update, Delete, Search | In-memory parsing, atomic file writes; no real-time sync |
| **SSH** | `openicf-ssh-connector` | Create, Delete, Search, custom scripts | Remote shell commands (bash, PowerShell), output parsing |
| **Groovy Scripted** | `openicf-groovy-connector` | User-defined (any) | Custom Groovy logic; rapid prototyping without Java compilation |
| **XML** | `openicf-xml-connector` | Create, Update, Delete, Search | XML file with objects as elements |
| **Kerberos/AD** | `openicf-ad-connector` | Create, Update, Delete, Search, Authenticate | LDAP + Kerberos, Windows-specific attributes |
| **HTTP/REST** | `openicf-http-connector` | Depends on target API | JSON/XML, OAuth2 and API key auth, configurable endpoints |
| **PowerShell** | Similar to SSH | Windows-specific | Active Directory module integration |

Each connector JAR includes a `META-INF/services` file for service loader discovery. Connector configuration (server addresses, credentials, connection pool sizes, schema mappings) is defined in OpenIDM's provisioner configuration files.

### 2.4 Remote Connector Server (Protobuf RPC)

The Remote Connector Server enables connectors to run in a separate JVM process, potentially on a different host, communicating with OpenIDM via Protobuf RPC.

**Architecture:**

```
OpenIDM host                          Remote host (near target system)
+-----------------------+             +---------------------------+
| ConnectorFacade       |             | RemoteConnectorServer     |
| RemoteConnectorInfo   |  Protobuf   | (standalone JVM, port     |
|   Manager             | ----------> |  8759)                    |
|                       |   RPC       | +-- LDAP Connector        |
|                       |             | +-- Database Connector     |
|                       |             | +-- AD Connector           |
+-----------------------+             +---------------------------+
                                        |        |         |
                                      LDAP     JDBC      AD
                                      Server   Server    DC
```

**Connection establishment:**

1. OpenIDM configuration specifies `remoteConnectorServer: "host:8759"`
2. `RemoteConnectorInfoManager` connects and authenticates via HMAC-SHA256 challenge-response over a shared key
3. The handshake exchanges: `SERVER_HANDSHAKE { version, challenge }` followed by `CLIENT_HANDSHAKE { HMAC(key, challenge) }`
4. After authentication, the client downloads the list of available connectors
5. `ConnectorFacade` is created for the remote connector, transparent to calling code

**Message format:**

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

Messages are framed as `[4 bytes: length (big-endian)] [N bytes: Protobuf payload]`. A single TCP connection handles multiple concurrent requests via request ID multiplexing. The server processes operations in a thread pool.

**Failover and load balancing** are configured declaratively:

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

The framework supports round-robin alternation, automatic skip of downed servers, periodic health checks, and circuit breaker behavior for unreliable servers.

**Design implications:** The Remote Proxy pattern makes network-distributed deployment transparent to business logic. The same `ConnectorFacade` interface is used whether the connector runs locally or remotely. Protobuf serialization provides compact, version-tolerant wire encoding.

---

## 3. Strengths

**Clean SPI/API separation.** The split between the consumer API and the implementor SPI is textbook interface segregation. Consumers depend only on `ConnectorFacade`; connector developers implement only the `Connector` interface and its capability annotations. The framework mediates between them, handling class loading, pooling, and dispatch. This separation enables independent versioning and ClassLoader isolation.

**Language-agnostic remote execution.** While the framework itself is Java, the Protobuf RPC mechanism is inherently language-agnostic. A Remote Connector Server could theoretically be implemented in any language that speaks Protobuf. In practice, this means connectors can run near their target systems regardless of the OpenIDM host's network location, crossing firewall boundaries and network segments.

**Comprehensive built-in connectors.** The nine built-in connectors cover the most common enterprise integration targets: LDAP directories, relational databases, Active Directory, CSV bulk imports, SSH-managed systems, and REST APIs. For many deployments, no custom connector development is needed.

**Pluggable operation model.** The operation interface pattern (implement only the interfaces your connector supports) avoids forcing connectors into a one-size-fits-all mold. A read-only connector implements only `SearchOp`; a full-lifecycle connector implements the complete CRUD + Sync + Auth interface. The `SchemaOp` interface enables runtime capability discovery.

**Groovy scripted connector.** The `openicf-groovy-connector` allows rapid development of custom connectors without Java compilation. For quick integrations, proof-of-concept work, or systems with simple APIs, a Groovy script implementing the required operations is significantly faster to develop than a full Java connector.

**Sync token checkpoint model.** The `SyncOp` interface's token-based checkpoint mechanism enables reliable incremental synchronization. If OpenIDM crashes mid-sync, it resumes from the last persisted token without data loss or duplication (assuming the connector's sync is idempotent).

**Multiplexed RPC.** The Protobuf RPC protocol multiplexes multiple concurrent operations over a single TCP connection, avoiding the overhead of per-request connection establishment. Request IDs ensure correct response pairing even when operations complete out of order.

---

## 4. Weaknesses

**Connector development complexity.** Building a new connector requires understanding the SPI, operation interfaces, `ObjectClass` and `Attribute` models, `Filter` translation (converting the framework's abstract filter tree into the target system's native query language), `Schema` construction, and `SyncToken` management. The learning curve is steep compared to writing a REST API integration in any modern language. Documentation for connector development is sparse in the open-source community version.

**Java-centric despite Protobuf.** Although Protobuf enables cross-language RPC in theory, the connector SPI is a Java interface. Implementing a connector requires Java (or JVM languages like Groovy/Kotlin). There are no official SDKs for writing connectors in Go, Python, or TypeScript. The .NET connector server that existed in the ForgeRock era has not been maintained in the OIP fork.

**Limited community connectors.** The built-in connector set (9 connectors) covers common targets, but the open-source ecosystem for additional connectors is thin. In contrast, SailPoint Identity Security Cloud ships with 200+ connectors, Saviynt with 500+, and iPaaS platforms like Workato with 1,000+. Organizations needing connectors for SaaS applications (Salesforce, Workday, ServiceNow, Box, Slack) must develop custom connectors or use the Groovy scripted connector as a bridge.

**No native SCIM support.** SCIM 2.0 (RFC 7642-7644) has become the standard REST API for identity provisioning across SaaS applications. OpenICF predates SCIM's widespread adoption and does not natively speak the protocol. Integrating with a SCIM endpoint requires either a custom connector or routing through the HTTP connector with manual attribute mapping. This is a significant gap given that virtually every modern SaaS application exposes SCIM endpoints for provisioning.

**Synchronous operation model.** The `SearchOp` callback interface (`ResultsHandler`) is synchronous and blocking. For large result sets from slow external systems, this can tie up connector threads. Modern integration frameworks favor reactive, non-blocking patterns (reactive streams, async/await) that handle backpressure more gracefully.

**Configuration complexity.** Connector configuration involves multiple layers: the connector's own `Configuration` class, the OpenIDM provisioner configuration (JSON), the remote server configuration (if remote), and the sync/recon mapping configuration. Debugging misconfiguration requires tracing through several files and log sources.

**Operational overhead of Remote Connector Server.** Each remote connector server is an additional JVM process to deploy, monitor, and maintain. In environments with many isolated network segments, the fleet of connector servers can become an operational burden. Modern alternatives (SCIM push, event-driven sync, cloud-native connectors) avoid this by shifting the integration point closer to the target system.

---

## 5. Modern Alternatives

### 5.1 OpenICF vs SCIM 2.0 Endpoints

**SCIM 2.0** (System for Cross-domain Identity Management, RFC 7642-7644) defines a standard REST API for identity provisioning.

| Dimension | OpenICF | SCIM 2.0 |
|-----------|---------|----------|
| Architecture | Middleware connector framework | Direct REST API on target application |
| Protocol | Proprietary (SPI + Protobuf RPC) | Standard REST (HTTP + JSON) |
| Development model | Java SPI implementation per target | Target application implements SCIM endpoints |
| Middleware required | Yes (OpenIDM + OpenICF) | No (IdP pushes directly to application) |
| Schema | Per-connector, framework-specific | Standardized User/Group schemas (RFC 7643) |
| Adoption | OIP/ForgeRock ecosystem | Universal (Okta, Entra ID, Google, SailPoint, 100s of SaaS apps) |
| Real-time sync | SyncOp polling (pull-based) | Push-based (IdP pushes changes) |
| Custom attributes | Per-connector mapping | SCIM extension schemas |
| Complexity | High (framework, server, pooling, ClassLoader) | Low (standard HTTP client/server) |

SCIM eliminates the middleware layer entirely. When a SaaS application supports SCIM, the identity provider (Okta, Entra ID, Keycloak, or OpenIDM itself) can push user/group changes directly via standard HTTP calls. No connector framework, no remote server, no Protobuf RPC.

The gap: SCIM only covers users and groups. It does not standardize entitlements, roles, or application-specific resources. SCIM implementation quality varies across vendors. And legacy systems that predate SCIM still need a connector-style integration.

### 5.2 OpenICF vs Native Cloud Connectors

Cloud identity platforms provide built-in, managed connectors that require no middleware:

| Platform | Connector count | Managed | Cost model |
|----------|----------------|---------|------------|
| **Okta** (OIN + SCIM) | 7,000+ app integrations | Yes | Included in subscription |
| **Microsoft Entra ID** | 500+ gallery apps | Yes | Included in Entra ID license |
| **Google Workspace** | Automated provisioning | Yes | Included in Workspace |
| **AWS IAM Identity Center** | SCIM to AWS accounts | Yes | Free with AWS SSO |
| **SailPoint ISC** | 200+ connectors | Hybrid (VA + SaaS) | Subscription |
| **Saviynt EIC** | 500+ connectors | SaaS | Subscription |

Native cloud connectors shift the integration burden from the customer to the vendor. The IdP vendor maintains, tests, and updates connectors. The customer configures attribute mappings via a UI.

The tradeoff: vendor lock-in. An organization using Okta's connectors cannot easily move to Keycloak or OpenIDM without rebuilding all integrations. OpenICF's open-source framework avoids this lock-in but shifts the development and maintenance burden to the deploying organization.

### 5.3 OpenICF vs iPaaS (Integration Platform as a Service)

iPaaS platforms (Workato, Tray.io, Mulesoft, Boomi) provide low-code integration between applications, including identity-relevant flows.

| Dimension | OpenICF | iPaaS |
|-----------|---------|-------|
| Development model | Java SPI, Groovy scripts | Low-code visual builder, pre-built connectors |
| Connector breadth | 9 built-in + custom | 1,000+ pre-built |
| Identity-specific | Yes (CRUD + Sync + Auth operations) | General-purpose (identity is one use case) |
| Real-time | SyncOp polling | Event-driven (webhooks, streaming) |
| Deployment | Self-hosted (OpenIDM + OpenICF) | SaaS (vendor-managed) |
| Cost | Infrastructure only | Subscription ($15k-200k+/year for enterprise) |
| Complexity | High (framework expertise) | Low (visual builder) |
| Reconciliation | Built into OpenIDM recon engine | Must be built as workflow |

iPaaS platforms excel at one-off integrations and event-driven flows. They struggle with the systematic reconciliation patterns that OpenIDM/OpenICF handle natively: full source-target comparison, link table management, conflict resolution, and phased create/update/delete processing (see the reconciliation flow in the component architecture extract). For full identity lifecycle management, iPaaS is a complement, not a replacement.

### 5.4 OpenICF vs Event-Driven Sync (CDC)

Change Data Capture (CDC) tools like Debezium and Kafka Connect capture database changes as events, enabling real-time identity synchronization without polling.

| Dimension | OpenICF SyncOp | CDC (Debezium + Kafka) |
|-----------|----------------|------------------------|
| Change detection | Connector-specific (timestamp column, changelog, polling) | Database log tailing (WAL, binlog, oplog) |
| Latency | Seconds to minutes (polling interval) | Sub-second (log tailing) |
| Overhead on source | Query-based (adds load) | Log-based (minimal overhead) |
| Reliability | Token checkpoint (at-least-once) | Offset tracking (exactly-once with transactions) |
| Schema | OpenICF attribute model | Raw database events (schema registry) |
| Deployment | OpenIDM + connector | Kafka cluster + Debezium + consumer |
| Infrastructure | Moderate | Significant (Kafka, ZooKeeper/KRaft, schema registry) |

CDC is architecturally superior for database-sourced identity data. It detects changes faster, with less load on the source system, and provides stronger delivery guarantees. However, CDC requires a streaming infrastructure (Kafka or equivalent) that many organizations do not have, and it only works for database sources -- not LDAP directories, SSH-managed systems, or SaaS APIs.

For organizations already operating Kafka, CDC-based identity sync (using Debezium for change capture and a custom consumer for identity mapping) can replace OpenICF's database connector with lower latency and higher reliability. For the remaining connector types (LDAP, SSH, Groovy-scripted), OpenICF remains necessary.

---

## 6. The Connector Dilemma

Identity integration faces a fundamental tension between three approaches, each optimal for different system categories:

### Approach 1: Standard APIs (SCIM)

Best for: SaaS applications, cloud services, new internal applications.

SCIM standardization eliminates the connector development problem entirely. If the target application exposes SCIM endpoints, integration reduces to attribute mapping and endpoint configuration. The trend is clear: SCIM adoption grew from a handful of vendors in 2015 to universal adoption among enterprise SaaS by 2024. Keycloak, Authentik, and Zitadel have all added SCIM support (see [Chapter 13: Comparison Matrices](13-comparison-matrices.md)).

### Approach 2: Event-Driven Sync (CDC + Webhooks)

Best for: Database-backed systems, real-time requirements, high-volume sync.

The IETF's Shared Signals Framework (SSF) and OpenID Connect's RISC (Risk and Incident Sharing and Coordination) are standardizing event-based identity notifications. When combined with CDC for database sources and webhooks for application events, event-driven sync provides lower latency and lower source overhead than connector polling.

### Approach 3: Connector Frameworks (OpenICF)

Best for: Legacy systems, heterogeneous protocols, systems that cannot expose APIs.

Connector frameworks remain necessary for the "last mile" of identity integration: mainframes, SSH-managed Unix systems, proprietary databases, legacy LDAP directories, and any system that cannot or will not implement SCIM or webhooks. These systems require custom integration logic -- exactly what OpenICF's SPI model provides.

### The Practical Reality

Most enterprises operate a mix of all three categories. A realistic identity integration architecture might look like:

```
SaaS apps (Salesforce, Workday, Slack)
  --> SCIM push from IdP (no middleware)

Databases (HR system, ERP)
  --> CDC via Debezium + Kafka --> identity consumer

Legacy systems (mainframe, SSH hosts, proprietary LDAP)
  --> OpenICF connectors (local or remote)

Cloud infrastructure (AWS, Azure, GCP)
  --> Native cloud provisioning APIs
```

OpenICF's value is concentrated in the legacy integration tier. As organizations modernize their application estates, the need for custom connectors diminishes. But for the systems that remain -- and in large enterprises, there are always systems that remain -- a connector framework like OpenICF is the only viable option.

---

## 7. Production Deployment Topology

Deploying OpenICF in production requires choosing between local (in-process) and remote connector execution, configuring connection pools, and planning for failover.

### 7.1 Local Connector Bundles (In-Process)

The simplest deployment runs connector bundles inside the OpenIDM JVM. The connector JAR is placed in OpenIDM's `connectors/` directory and discovered via service loader. All operations execute in OpenIDM's thread pool, sharing its heap and ClassLoader hierarchy.

```
OpenIDM JVM
+----------------------------------------------+
| openidm-core                                 |
|   +-- ConnectorFacade (local)                |
|       +-- LDAP Connector JAR (ClassLoader A) |
|       +-- DB Connector JAR  (ClassLoader B)  |
|       +-- CSV Connector JAR (ClassLoader C)  |
+----------------------------------------------+
  |           |            |
 LDAP        JDBC         File
 Server      Server       System
```

Local execution offers the lowest latency (no serialization overhead) and simplest operational model (one process to monitor). The framework isolates each connector in its own `BundleClassLoader` (see `BundleClassLoader.java` in `connector-framework-internal`), preventing dependency conflicts -- a connector using an older Guava version will not collide with another using a newer one. The downside: all connectors share the OpenIDM JVM's memory and CPU. A misbehaving connector (memory leak, thread starvation) affects the entire OpenIDM instance.

**When to use local:** Target systems are network-accessible from the OpenIDM host, connector count is modest (under ~10), and connector code is trusted/well-tested.

### 7.2 Remote Connector Server Deployment

When target systems reside in network segments unreachable from OpenIDM -- or when connector isolation is required for stability -- the Remote Connector Server runs as a standalone JVM on a host with direct access to the target.

```
DMZ / Cloud                    On-Premises Data Center
+------------------+           +----------------------------+
| OpenIDM          |           | Remote Connector Server    |
| (port 8080)      | Protobuf  | (port 8759, standalone JVM)|
|                  | --------> |  +-- AD Connector           |
|                  |  TLS      |  +-- Mainframe Connector    |
+------------------+           +----------------------------+
                                  |              |
                                Active         Mainframe
                                Directory      (TN3270)
```

The protocol between OpenIDM and the Remote Connector Server uses Protobuf serialization over TCP with length-prefixed framing, defined across six `.proto` files in `connector-framework-protobuf/src/main/protobuf/`: `RPCMessages.proto` (handshake, request/response envelopes), `OperationMessages.proto` (CRUD/sync/auth operations), `ConnectorObjects.proto` (Uid, ObjectClass, Attribute), `FilterMessages.proto` (filter tree serialization), `SchemaMessages.proto` (schema exchange), and `CommonObjectMessages.proto` (shared types). The connection authenticates via HMAC-SHA256 challenge-response over a pre-shared key.

**When to use remote:** Target systems are behind firewalls, on different network segments, or require OS-specific libraries (e.g., Windows DLLs for Active Directory).

### 7.3 Connection Pooling

Connectors that implement the `PoolableConnector` interface (extending `Connector` with a `checkAlive()` method) participate in the framework's connection pool. Pool behavior is governed by `ObjectPoolConfiguration` with five parameters:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `maxObjects` | 10 | Maximum total connections (idle + active) |
| `maxIdle` | 10 | Maximum idle connections retained in pool |
| `minIdle` | 1 | Minimum idle connections kept warm |
| `maxWait` | 150,000 ms | Timeout waiting for a free connection before error |
| `minEvictableIdleTimeMillis` | 120,000 ms | Idle time before a connection is eligible for eviction |

The pool implementation (`ObjectPool.java` in `connector-framework-internal`) uses a `ConcurrentLinkedQueue` for idle objects, a `Semaphore` for capacity enforcement, and a `ReentrantLock` for eviction. Before returning an idle connector to a caller, the pool invokes `checkAlive()` -- if the connector's underlying connection has timed out, it is discarded and a fresh instance is created. The `ConnectorPoolManager` maintains a `ConcurrentMap` keyed by `ConnectorKey` + configuration properties, so distinct configurations for the same connector type get separate pools.

Non-poolable connectors (those implementing only `Connector`, not `PoolableConnector`) are instantiated per-operation and disposed immediately. This is acceptable for stateless connectors (CSV, XML) but expensive for connectors that establish network connections (LDAP, database).

### 7.4 Failover Patterns

The RPC layer in `connector-framework-rpc` provides two load balancing algorithms for multi-server deployments:

- **`RoundRobinLoadBalancingAlgorithm`**: Distributes requests across connector servers in round-robin order. All servers are active simultaneously. If one server fails, it is skipped and retried after a health check interval.
- **`FailoverLoadBalancingAlgorithm`**: Sends all requests to a primary server. On failure, traffic shifts to the next server in the list. When the primary recovers (determined by periodic health checks), traffic returns to it.

Both algorithms operate through the `RemoteConnectionGroup` and `RequestDistributor` abstractions, which manage a set of `RemoteConnectionHolder` instances. Health checking is lightweight: the framework reuses the Protobuf channel's heartbeat mechanism rather than running full `TestOp` calls.

---

## 8. Connector Development Guide

### 8.1 SPI Operation Interfaces

A connector is a Java class annotated with `@ConnectorClass` that implements `Connector` (or `PoolableConnector` for pooled connections) plus one or more operation interfaces from `org.identityconnectors.framework.spi.operations`:

| Interface | When to Implement |
|-----------|-------------------|
| `CreateOp` | Connector can create resources on the target system |
| `UpdateOp` | Connector can modify existing resources |
| `UpdateAttributeValuesOp` | Connector supports add/remove of multi-valued attributes (vs. full replace) |
| `DeleteOp` | Connector can remove resources |
| `SearchOp<T>` | Connector can query resources; generic type `T` is the native query type |
| `SyncOp` | Connector can detect changes since a token (for LiveSync) |
| `SchemaOp` | Connector can describe its resource types and attributes at runtime |
| `AuthenticateOp` | Connector can validate credentials against the target |
| `TestOp` | Connector can verify its configuration and connectivity |
| `ScriptOnResourceOp` | Connector can execute scripts on the target system |
| `ScriptOnConnectorOp` | Connector can execute scripts in its own JVM |
| `BatchOp` | Connector supports batched operations |

The minimum viable connector implements `SearchOp` (read-only). A full lifecycle connector implements `CreateOp`, `UpdateOp`, `DeleteOp`, `SearchOp`, `SyncOp`, `SchemaOp`, and `TestOp`. The framework introspects implemented interfaces to advertise capabilities to OpenIDM.

`SearchOp<T>` deserves special attention: the generic type `T` represents the connector's native filter type. The connector provides a `FilterTranslator<T>` that converts the framework's abstract `Filter` tree into the target system's native query representation (e.g., LDAP filter strings, SQL WHERE clauses). This is the most complex part of connector development.

### 8.2 Groovy Scripted Connector

The fastest path to a custom connector is the Groovy scripted connector (`OpenICF-groovy-connector`). Instead of compiling Java, you write Groovy scripts for each operation. The `ScriptedConnector` class (which extends `ScriptedConnectorBase`) delegates each operation to a configured Groovy script file.

Typical script mapping in provisioner configuration:

```json
{
  "connectorRef": {
    "bundleName": "org.forgerock.openicf.connectors.groovy-connector",
    "connectorName": "org.forgerock.openicf.connectors.groovy.ScriptedConnector"
  },
  "configurationProperties": {
    "createScriptFileName": "CreateScript.groovy",
    "updateScriptFileName": "UpdateScript.groovy",
    "deleteScriptFileName": "DeleteScript.groovy",
    "searchScriptFileName": "SearchScript.groovy",
    "syncScriptFileName":   "SyncScript.groovy",
    "schemaScriptFileName": "SchemaScript.groovy",
    "testScriptFileName":   "TestScript.groovy"
  }
}
```

Each script receives pre-bound variables: `operation` (the operation name), `objectClass` (the resource type), `attributes` (for create/update), `uid` (for update/delete), `filter` (for search), `token` (for sync), and `connection` (if using `ScriptedPoolableConnector`). The Groovy scripted approach trades type safety for development speed -- ideal for proof-of-concept integrations, REST API targets, or systems where the integration logic changes frequently.

### 8.3 Database Table Connector

The database table connector (`OpenICF-databasetable-connector`) maps a single database table (or view) to an OpenICF object class. Key classes in `org.identityconnectors.databasetable`:

- `DatabaseTableConnector` -- implements `CreateOp`, `UpdateOp`, `DeleteOp`, `SearchOp`, `SyncOp`, `AuthenticateOp`, `TestOp`
- `DatabaseTableConfiguration` -- connection URL, driver class, table name, key column, password column, sync column (timestamp or integer for change detection)
- `DatabaseTableFilterTranslator` -- converts framework `Filter` objects into SQL WHERE clauses
- `DatabaseTableConnection` -- manages JDBC connection lifecycle, wraps `java.sql.Connection`

Change detection for `SyncOp` relies on a designated timestamp or auto-increment column. The connector queries rows where `syncColumn > lastToken`, returning them as `SyncDelta` objects. This is simple but limited: it cannot detect deletes unless a soft-delete column exists.

### 8.4 LDAP Connector for Non-OpenDJ Directories

The LDAP connector (`OpenICF-ldap-connector`) supports any LDAPv3-compliant directory, not just OpenDJ. Key configuration in `LdapConfiguration`:

- `host`, `port`, `ssl` -- connection parameters
- `principal`, `credentials` -- bind DN and password
- `baseContexts` -- search base DNs for accounts
- `accountObjectClasses` -- LDAP object classes representing user accounts (default: `inetOrgPerson`, `top`)
- `groupObjectClasses` -- LDAP object classes for groups
- `accountSearchFilter` -- additional LDAP filter for account searches
- `passwordAttribute` -- attribute name for password operations (default: `userPassword`)
- `changeLogBlockSize` -- number of changelog entries read per sync cycle
- `usePagedResultControl` -- enable LDAP paged results for large directories

The connector supports Active Directory via `ADLdapUtil` and `ADUserAccountControl` classes that handle AD-specific attributes (UAC flags, group types, primary group membership). The `GroupHelper` class manages group membership operations across both standard LDAP (via `member`/`memberOf`) and AD-specific patterns.

Sync detection uses the directory's changelog mechanism (cn=changelog for Sun/OIP directories, USN-changed for AD). Directories without changelog support (e.g., some OpenLDAP configurations) cannot use `SyncOp` and are limited to periodic full reconciliation.

### 8.5 Testing with the Contract Test Framework

OpenICF provides `connector-framework-contract`, a comprehensive test suite that validates any connector against the SPI contract. Located in `org.identityconnectors.contract.test`, the key classes are:

| Test Class | What It Validates |
|------------|-------------------|
| `CreateApiOpTests` | Create returns valid Uid; created object is retrievable |
| `DeleteApiOpTests` | Delete removes the object; subsequent get returns null |
| `UpdateApiOpTests` | Update modifies specified attributes; unmodified attributes unchanged |
| `SearchApiOpTests` | Search returns correct results for various filter types |
| `SyncApiOpTests` | Sync returns deltas for changes made after token |
| `SchemaApiOpTests` | Schema is non-null, contains expected object classes |
| `AuthenticationApiOpTests` | Valid credentials succeed; invalid credentials throw |
| `TestApiOpTests` | TestOp succeeds with valid configuration |
| `ConfigurationTests` | Configuration validates correctly, rejects invalid values |

To use: extend `ContractITCase`, configure a test properties file pointing at a real or test instance of the target system, and run with Maven. The `ConnectorHelper` utility class handles connector instantiation, configuration loading, and test data generation. The `connector-test-common` module provides `TestHelpers` for unit-level testing without a live target.

---

## 9. Migration Cost Analysis

### 9.1 OpenICF to SCIM 2.0

SCIM migration only works when the target system exposes SCIM endpoints. For targets that do -- Salesforce, Workday, Slack, Box, Zoom, and most modern SaaS applications -- the migration eliminates the connector entirely. OpenIDM (or any SCIM-capable IdP) pushes user/group changes directly via standard HTTP calls.

**What migrates cleanly:** Attribute mapping (OpenICF's `Attribute` model maps reasonably to SCIM's User/Group schemas). Provisioning flow (create/update/delete operations have direct SCIM equivalents).

**What does not migrate:** `SyncOp` (SCIM has no pull-based change detection; the IdP pushes, or the target emits events). Filter translation (SCIM has its own filter syntax, incompatible with OpenICF's `Filter` tree). Custom `ObjectClass` types beyond User and Group (SCIM extension schemas exist but are not universally supported). Authentication delegation (`AuthenticateOp` has no SCIM equivalent).

**Estimated effort:** Low per target (days, not weeks), but only for SCIM-compliant targets. Non-SCIM targets cannot use this path.

### 9.2 OpenICF to MidPoint ConnId

ConnId (Connector Identity) is the open-source fork of the OpenICF SPI, maintained by Evolveum as part of MidPoint. ConnId and OpenICF share the same lineage -- the `org.identityconnectors` package namespace, the same operation interfaces (`CreateOp`, `SearchOp`, `SyncOp`), and the same `ConnectorFacade` pattern. This is the highest-compatibility migration target.

**What migrates cleanly:** Most Java connectors compile against ConnId with minimal changes (package renames, dependency updates). The SPI contract is nearly identical. MidPoint's connector test framework is derived from the same `connector-framework-contract` tests.

**What requires work:** Groovy scripted connectors need adaptation to MidPoint's script binding conventions (different variable names, different configuration structure). Remote connector server protocol differs (ConnId uses its own RPC, not OpenICF's Protobuf). Pool configuration parameters map one-to-one but live in different configuration files.

**Estimated effort:** Low for Java connectors (hours to days). Moderate for Groovy scripted connectors (days). The reconciliation engine migration (OpenIDM recon to MidPoint synchronization tasks) is the larger effort, not the connector migration itself.

### 9.3 OpenICF to iPaaS (Workato, Mulesoft)

iPaaS platforms operate on a fundamentally different model: event-driven workflows with pre-built application connectors, not a connector SPI with reconciliation.

**What does not map:** OpenICF's `SyncOp` and OpenIDM's reconciliation engine have no iPaaS equivalent. Reconciliation (full source-target comparison, link table management, situation-based policy) must be reimplemented as iPaaS workflows -- a significant architectural change. Connection pooling and ClassLoader isolation are platform-managed, not configurable.

**What maps partially:** CRUD operations translate to iPaaS "actions" on target applications. Attribute mapping translates to iPaaS "data transformations." But each mapping must be rebuilt in the iPaaS visual builder; there is no automated migration path from OpenICF provisioner JSON to iPaaS workflow definitions.

**Estimated effort:** High. Each connector integration must be rebuilt from scratch in the iPaaS platform. The reconciliation logic must be redesigned as workflows. Budget weeks-to-months per complex integration.

### 9.4 Key Risk: Custom Groovy Connectors

Custom Groovy scripted connectors represent the highest migration risk across all targets. These connectors embed business-specific integration logic -- custom API calls, proprietary data transformations, environment-specific error handling -- in Groovy scripts that have no equivalent in SCIM, no direct port to ConnId's different scripting conventions, and no automated conversion to iPaaS workflows. Every custom Groovy connector requires manual analysis and rewrite regardless of the migration target. Organizations with 5+ custom Groovy connectors should budget significant effort for any migration scenario.

---

## 10. Codebase Navigation Guide

### 10.1 Repository Structure

The OpenICF codebase is split between the core framework and individual connector modules, all under `OpenICF/`:

```
OpenICF/
+-- OpenICF-java-framework/          # Core framework (19 sub-modules)
|   +-- connector-framework/          # SPI + API interfaces
|   +-- connector-framework-internal/ # Runtime: pooling, ClassLoader, dispatch
|   +-- connector-framework-protobuf/ # Protobuf message definitions (6 .proto files)
|   +-- connector-framework-rpc/      # RPC transport, load balancing
|   +-- connector-framework-server/   # Remote server bootstrap
|   +-- connector-framework-contract/ # Contract test suite for connectors
|   +-- connector-framework-osgi/     # OSGi bundle support
|   +-- connector-server-grizzly/     # Grizzly-based remote server
|   +-- connector-server-jetty/       # Jetty-based remote server
|   +-- connector-test-common/        # Test utilities (TestHelpers, PropertyBag)
|   +-- bundles-parent/               # Parent POM for connector bundles
|   +-- icfl-over-slf4j/              # Logging bridge
|   +-- openicf-zip/                  # Distribution packaging
|   +-- testbundlev1/, testbundlev2/  # Test connector bundles
|   +-- testcommonv1/, testcommonv2/  # Shared test infrastructure
+-- OpenICF-ldap-connector/           # LDAP/AD connector
+-- OpenICF-databasetable-connector/  # JDBC database table connector
+-- OpenICF-csvfile-connector/        # CSV file connector
+-- OpenICF-groovy-connector/         # Groovy scripted connector
+-- OpenICF-ssh-connector/            # SSH connector
+-- OpenICF-xml-connector/            # XML file connector
+-- OpenICF-kerberos-connector/       # Kerberos connector
+-- OpenICF-dbcommon/                 # Shared database utilities
+-- OpenICF-maven-plugin/             # Maven plugin for connector packaging
```

### 10.2 Key Source Paths

**SPI/API interfaces** -- the contract between framework and connectors:
- `OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/api/` -- Consumer API (`ConnectorFacade`, `ConnectorInfo`, `ConnectorInfoManager`)
- `OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/spi/` -- Implementor SPI (`Connector`, `PoolableConnector`, `Configuration`, `@ConnectorClass`)
- `OpenICF-java-framework/connector-framework/src/main/java/org/identityconnectors/framework/spi/operations/` -- Operation interfaces (16 files: `CreateOp`, `UpdateOp`, `DeleteOp`, `SearchOp`, `SyncOp`, `SchemaOp`, `AuthenticateOp`, `TestOp`, `BatchOp`, etc.)

**Connection pooling and ClassLoader isolation:**
- `connector-framework-internal/.../local/ObjectPool.java` -- Pool implementation (Semaphore + ConcurrentLinkedQueue)
- `connector-framework-internal/.../local/ConnectorPoolManager.java` -- Pool-per-configuration management
- `connector-framework-internal/.../local/BundleClassLoader.java` -- Per-connector ClassLoader isolation
- `connector-framework/src/main/java/org/identityconnectors/common/pooling/ObjectPoolConfiguration.java` -- Pool tuning parameters

**Protobuf protocol definitions** (remote connector server wire format):
- `connector-framework-protobuf/src/main/protobuf/RPCMessages.proto` -- Handshake, request/response envelopes
- `connector-framework-protobuf/src/main/protobuf/OperationMessages.proto` -- CRUD, sync, auth operation messages
- `connector-framework-protobuf/src/main/protobuf/ConnectorObjects.proto` -- Uid, ObjectClass, Attribute serialization
- `connector-framework-protobuf/src/main/protobuf/FilterMessages.proto` -- Filter tree serialization
- `connector-framework-protobuf/src/main/protobuf/SchemaMessages.proto` -- Schema exchange
- `connector-framework-protobuf/src/main/protobuf/CommonObjectMessages.proto` -- Shared primitive types

**RPC transport and failover:**
- `connector-framework-rpc/.../rpc/RoundRobinLoadBalancingAlgorithm.java`
- `connector-framework-rpc/.../rpc/FailoverLoadBalancingAlgorithm.java`
- `connector-framework-rpc/.../rpc/RemoteConnectionGroup.java` -- Server group management
- `connector-framework-rpc/.../rpc/RequestDistributor.java` -- Request routing

**Built-in connector implementations:**
- `OpenICF-ldap-connector/src/main/java/org/identityconnectors/ldap/LdapConnector.java` -- LDAP/AD connector entry point
- `OpenICF-databasetable-connector/src/main/java/org/identityconnectors/databasetable/DatabaseTableConnector.java` -- JDBC connector
- `OpenICF-csvfile-connector/src/main/java/org/forgerock/openicf/csvfile/CSVFileConnector.java` -- CSV connector
- `OpenICF-groovy-connector/src/main/java/org/forgerock/openicf/connectors/groovy/ScriptedConnector.java` -- Groovy entry point (delegates to `ScriptedConnectorBase`)
- `OpenICF-ssh-connector/` -- SSH/shell command execution
- `OpenICF-kerberos-connector/` -- Kerberos authentication integration

**Contract test framework** (for validating custom connectors):
- `connector-framework-contract/src/main/java/org/identityconnectors/contract/test/ContractITCase.java` -- Main test entry point
- `connector-framework-contract/.../test/CreateApiOpTests.java`, `SearchApiOpTests.java`, `SyncApiOpTests.java`, etc. -- Per-operation contract tests
- `connector-test-common/src/main/java/org/identityconnectors/test/common/TestHelpers.java` -- Unit test utilities

---

## 11. Verdict

OpenICF is a sound piece of integration engineering. Its SPI/API separation is a model of interface design. Its Protobuf RPC remote execution solves a real network topology problem. Its built-in connectors cover the most common enterprise targets. The sync token model enables reliable incremental synchronization.

Its weaknesses are primarily those of timing and market evolution. SCIM has standardized the integration interface for modern applications, eliminating the need for custom connectors in most new deployments. Cloud identity platforms (Okta, Entra ID, SailPoint) provide managed connectors that shift maintenance burden from customer to vendor. Event-driven approaches (CDC, SSF) offer better latency and reliability than polling-based sync. And the Java-centric SPI, despite Protobuf's theoretical language-agnosticism, limits the developer pool for custom connectors.

**For existing OIP deployments** that integrate with legacy systems (on-premises LDAP, databases, SSH hosts, mainframes), OpenICF remains the right tool. Its integration with OpenIDM's reconciliation engine, link table management, and sync token checkpointing is battle-tested and well-understood.

**For new deployments** evaluating identity integration, the recommendation depends on the target system landscape:

- If targets are primarily SaaS applications: adopt SCIM-native provisioning from the identity provider. No connector framework needed.
- If targets include databases requiring real-time sync: evaluate CDC (Debezium + Kafka) for the database tier, SCIM for SaaS, and OpenICF only for remaining legacy targets.
- If targets are predominantly legacy (on-premises LDAP, AD, mainframe, SSH): OpenICF or a commercial equivalent (SailPoint connectors, Saviynt connectors) is necessary. The choice between OpenICF and commercial options depends on budget, connector breadth requirements, and willingness to develop custom connectors.

The connector framework is not dead -- but its role has narrowed from "universal integration layer" to "legacy system adapter." As the portion of an organization's application estate that predates SCIM shrinks, so does the case for maintaining a connector framework. OpenICF's long-term relevance is tied to the persistence of legacy systems in enterprise IT -- and legacy systems, for better or worse, persist.
