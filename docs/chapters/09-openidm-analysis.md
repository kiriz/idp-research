# Chapter 9: OpenIDM Analysis

OpenIDM is the identity lifecycle management component of the Open Identity Platform suite, responsible for provisioning, synchronization, reconciliation, and workflow orchestration across heterogeneous identity systems. Unlike OpenAM (which handles authentication and authorization at runtime) and OpenDJ (which stores identity data), OpenIDM addresses the operational plane: ensuring that user accounts, group memberships, and access entitlements are created, updated, and removed across every system in the enterprise as employees join, move between roles, and leave. Built on an Apache Felix OSGi container with a REST-first architecture, OpenIDM coordinates identity lifecycle through configurable sync mappings, a reconciliation engine, managed objects with lifecycle hooks, and BPMN 2.0 workflow integration via Activiti. Its connector framework, OpenICF, provides the translation layer between OpenIDM's abstract identity operations and the specific APIs of target systems -- LDAP directories, relational databases, CSV files, SSH endpoints, and cloud services. This chapter examines OpenIDM's architecture, evaluates its position against commercial IGA platforms and modern provisioning approaches, and assesses whether its open-source identity governance capabilities remain viable in a market dominated by SailPoint, Saviynt, and cloud-native SCIM.

---

## 1. What OpenIDM Does

OpenIDM manages the complete identity lifecycle through four core capabilities:

- **Provisioning.** Creating, updating, and deleting user accounts and entitlements across target systems (Active Directory, LDAP, databases, SaaS applications, custom systems) through the OpenICF connector framework. When HR creates a new employee record, OpenIDM can automatically create corresponding accounts in Active Directory, email systems, LDAP directories, and application databases according to configurable mapping rules.

- **Synchronization.** Keeping identity data consistent across multiple authoritative and downstream systems through two mechanisms: LiveSync (real-time change detection via connector polling) and Reconciliation (batch comparison of source and target objects with create/update/delete actions for discrepancies). Synchronization mappings define attribute-level transformations between source and target schemas.

- **Reconciliation.** A three-phase batch process that compares all objects between a source system and a target system: Phase 1 creates missing target entries, Phase 2 updates mismatched attributes on linked entries, and Phase 3 optionally deletes orphaned target entries that lack source counterparts. Reconciliation is idempotent and produces detailed reports of created, updated, deleted, and errored objects.

- **Workflow.** BPMN 2.0 process automation via the embedded Activiti workflow engine, enabling human-in-the-loop approval workflows, escalation chains, and complex joiner-mover-leaver processes modeled as business processes. Workflows are exposed through REST endpoints (`/workflow/processinstance`, `/workflow/taskinstance`) and integrate with managed objects for event-driven triggering.

Together, these capabilities address the "Day 2" identity problem: not authentication (handled by OpenAM) but the ongoing operational work of ensuring the right people have the right access to the right systems at the right time, and that access is revoked when no longer appropriate.

---

![OpenIDM Provisioning Architecture](../diagrams/03-openidm-provisioning.png)

## 2. Architecture Overview

### OSGi Service Model (Apache Felix)

OpenIDM is the only OIP component built on an OSGi container rather than a WAR deployment. The Apache Felix v5.x OSGi framework provides a modular runtime where each functional component is packaged as a bundle with explicit service contracts, lifecycle management, and runtime service discovery.

Core bundle activators (implementing the `BundleActivator` pattern) register services at startup:

- `OpenIDM/openidm-router/src/main/java/org/forgerock/openidm/router/Activator.java` -- Registers the `RouterRegistry` service and `RequestHandler` service.
- `OpenIDM/openidm-repo-jdbc/src/main/java/org/forgerock/openidm/repo/jdbc/impl/Activator.java` -- Registers the JDBC repository backend as a data source and query executor.
- `OpenIDM/openidm-system/src/main/java/org/forgerock/openidm/core/internal/Activator.java` -- Initializes the OpenIDM core runtime.
- `OpenIDM/openidm-config/src/main/java/org/forgerock/openidm/config/persistence/Activator.java` -- Loads configuration from the filesystem or LDAP backend.
- `OpenIDM/openidm-repo-orientdb/src/main/java/org/forgerock/openidm/repo/orientdb/impl/Activator.java` -- Registers the OrientDB repository backend.

The OSGi bundle lifecycle follows the standard state machine: INSTALLED -> RESOLVED -> STARTING -> ACTIVE -> STOPPING -> UNINSTALLED. Services are registered via `BundleContext.registerService()` with a service PID and properties dictionary, and discovered at runtime via `ServiceTracker`. This Service Locator + Factory pattern enables decoupled components to interact through interface contracts without compile-time dependencies.

The OSGi model brings genuine modularity -- bundles can be started, stopped, and updated at runtime without restarting the entire application. However, it also introduces significant complexity (discussed in Section 4).

### Sync/Recon Engine

The synchronization and reconciliation engine, located in `OpenIDM/openidm-core/src/main/java/org/forgerock/openidm/sync/`, is OpenIDM's most architecturally significant subsystem. It implements an ETL (Extract-Transform-Load) + Change Data Capture pattern with five key components:

1. **SyncEngine** -- The main coordinator orchestrating both LiveSync and Reconciliation operations.
2. **Reconciliation Service** -- Executes the three-phase batch comparison (source creation, target update, target cleanup).
3. **LiveSync Service** -- Real-time change capture from source systems via connector polling.
4. **Implicit Sync** -- Auto-triggered synchronization on managed object writes (create, update, delete of managed objects can cascade to target systems).
5. **Link Store** -- Maintains the source-to-target object ID mapping (stored in JDBC or OrientDB), enabling OpenIDM to track which source object corresponds to which target object.

The reconciliation flow proceeds as:

```
Trigger: POST /openidm/recon?_action=recon
  |
SyncEngine.recon() -> Load mapping (e.g., "user-to-ldap")
  |
Phase 1: Source -> Target Creation
  - Query all source objects
  - For each: check if linked entry exists in target
    - If no link: create target via connector, record link
  |
Phase 2: Target Update
  - For each linked source:
    - Get target object, compare attributes
    - If differences: apply updates via connector
  |
Phase 3: Target Cleanup
  - For each target: check if has source link
    - If no link + policy=delete: delete target via connector
  |
Final Report: created, updated, deleted counts + errors
```

Mappings are defined in JSON configuration:

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

LiveSync operates through the connector framework's `SyncOp` interface. Connectors that support change detection (LDAP changelog, database timestamp columns, file modification dates) return `SyncDelta` objects containing a sync token (checkpoint), operation type (CREATE/UPDATE/DELETE), object class, unique identifier, and changed attributes. OpenIDM processes each delta, updates or creates the corresponding managed object, checks downstream mappings, and applies implicit sync if configured. The sync token is persisted after processing, enabling resume from the last checkpoint on restart.

### Managed Objects

Managed objects are OpenIDM's central abstraction for identity data, defined in `managed.json` configuration as JSON-LD documents independent of any external system. Each managed object type (user, role, assignment, etc.) has:

- **Schema properties** with types, validation rules, and format constraints.
- **Relationships** supporting typed links between objects (user-to-role, user-to-manager) with reverse relationship support.
- **Lifecycle hooks** (JavaScript or Groovy) triggered on create, read, update, delete, and query operations.
- **Protected properties** that are encrypted at rest, masked in audit logs, and never returned in plain text via HTTP.

REST endpoints follow CREST (Common REST) conventions:

| Operation | Endpoint | Notes |
|-----------|----------|-------|
| Create | `POST /managed/user` | Returns `_id`, full object |
| Read | `GET /managed/user/{id}` | System fields: `_id`, `_rev`, `_created`, `_updated` |
| Update | `PUT /managed/user/{id}` | Optimistic locking via `_rev` |
| Delete | `DELETE /managed/user/{id}` | Removes object + relationships |
| Query | `GET /managed/user?_queryFilter=...` | CREST filter syntax |
| Relationships | `GET /managed/user/{id}/roles` | Traverses relationship graph |

The managed object model follows a Document Store + Event-Driven pattern: JSON documents with hooks that trigger reactive workflows on state changes. This enables complex identity lifecycle logic -- automatically generating usernames on creation, cascading role changes to downstream systems, encrypting sensitive fields on write -- without embedding that logic in the provisioning engine itself.

### Router (Request Dispatcher)

The OpenIDM router (`OpenIDM/openidm-router/src/main/java/org/forgerock/openidm/router/RouterRegistryImpl.java`) implements a trie-based request dispatcher using an Interceptor/Chain of Responsibility pattern. All requests -- internal and external -- flow through the router, which matches URL paths to registered handlers:

| Pattern | Handler | Operations |
|---------|---------|------------|
| `/managed/{type}/{id}` | ManagedObject service | CRUD + relationships |
| `/system/{connector}/{objectClass}/{id}` | OpenICF ConnectorFacade | CRUD via connector |
| `/repo/{table}/{id}` | Repository service (JDBC, OrientDB) | Direct database CRUD |
| `/sync` | SyncEngine service | `_action=recon`, `_action=liveSync` |
| `/recon` | ReconService | Reconciliation reports |
| `/workflow/processinstance` | Activiti engine wrapper | Start process, complete task |
| `/audit/access`, `/audit/activity` | Audit service | Query audit events |
| `/custom/*` | Application bundles | Custom routes |

The trie-based path matching provides O(n) complexity where n is the path depth (typically 3-4 segments). Before reaching the handler, requests pass through a filter chain: authentication filter (session token validation), authorization filter (RBAC check), validation filter (schema validation), transformation filter (encryption, format mapping), and audit filter (before/after state capture).

### Workflow Integration

The workflow module (`OpenIDM/openidm-workflow-activiti/`) embeds the Activiti BPMN 2.0 workflow engine, enabling human-in-the-loop approval processes. Workflows are defined in BPMN XML and exposed through REST:

- Start a process instance: `POST /workflow/processinstance?_action=create`
- Complete a human task: `POST /workflow/taskinstance/{taskId}?_action=complete`
- Query pending tasks: `GET /workflow/taskinstance?_queryFilter=assignee eq "manager1"`

Integration with managed objects enables event-driven workflow triggering: a new user creation can automatically start an approval workflow, with the account remaining in a "pending" state until the workflow completes. This is the mechanism enterprises use for access request/approval, manager approval of role changes, and automated onboarding sequences.

### Repository Layer

OpenIDM supports dual repository backends:

- **JDBC** (`OpenIDM/openidm-repo-jdbc/`) -- PostgreSQL, MySQL, Oracle, SQL Server, H2. The production-recommended backend, using SQL with JSON column types where supported. HikariCP provides connection pooling.
- **OrientDB** (`OpenIDM/openidm-repo-orientdb/`) -- An embedded document database used in development and small deployments. OrientDB provides schema-less JSON document storage without requiring a separate database server.

The repository layer stores managed objects, link records (source-to-target ID mappings), configuration, audit logs, and workflow state. All repository access goes through the router's `/repo/*` route, meaning the repository backend is transparent to higher layers.

### OpenICF Connector Architecture

The OpenICF connector framework (`OpenICF/OpenICF-java-framework/`, 19 sub-modules) deserves detailed examination because it is the mechanism through which OpenIDM interacts with every external system. The architecture follows a clean SPI/API split:

**API layer** (client-facing, at `org.identityconnectors.framework.api/`): `ConnectorFacade` is the entry point. Applications call `ConnectorFacade.create()`, `.update()`, `.delete()`, `.search()`, `.authenticate()`, and `.sync()` without knowing the underlying connector implementation.

**SPI layer** (connector-facing, at `org.identityconnectors.framework.spi/`): Connector developers implement a subset of operation interfaces:

| Interface | Purpose |
|-----------|---------|
| `CreateOp` | Create resource object, return assigned UID |
| `UpdateOp` | Replace attributes on existing object |
| `DeleteOp` | Remove object by UID |
| `SearchOp` | Query objects via filter with streaming callback |
| `AuthenticateOp` | Validate credentials, return UID or throw |
| `SyncOp` | Return changes since last sync token |
| `SchemaOp` | Return resource schema (object classes, attributes) |
| `ScriptOnResourceOp` | Execute script on the target resource (shell, SQL) |
| `ScriptOnConnectorOp` | Execute Groovy in the connector JVM |

Connectors declare supported operations by implementing the relevant interfaces. A JDBC connector might implement CreateOp, UpdateOp, DeleteOp, SearchOp, and SyncOp (via timestamp columns) but not AuthenticateOp. The framework handles capability detection at runtime.

**Remote connector server.** The remote connector server (`OpenICF/OpenICF-java-framework/connector-framework-server/`) enables connectors to run in a separate JVM on a different host, communicating with OpenIDM over Protobuf RPC on port 8759. The handshake uses HMAC-SHA256 authentication with a shared key. Connections are multiplexed (multiple concurrent operations over a single TCP connection) with request ID pairing. Failover supports round-robin across multiple remote servers with circuit breaker patterns for flaky backends.

Built-in connectors cover the most common integration targets:

| Connector | Key Features |
|-----------|-------------|
| LDAP | TLS/SSL, connection pooling, paging, password change, changelog sync |
| Database/JDBC | SQL templating, transactions, timestamp-based sync |
| CSV | In-memory parsing, atomic writes |
| SSH | Remote shell commands (bash, PowerShell), output parsing |
| Kerberos/AD | LDAP + Kerberos, Windows-specific attributes |
| Groovy Scripted | Custom logic without Java compilation |
| HTTP/REST | JSON/XML, OAuth2/API key auth, customizable endpoints |

Each connector JAR includes `META-INF/services/org.identityconnectors.framework.spi.Connector` for Java ServiceLoader discovery at runtime.

---

## 3. Strengths

**Flexible sync/recon engine.** The mapping-based synchronization engine is OpenIDM's core differentiator. Attribute-level transformations (via JavaScript or Groovy expressions in mapping configurations), configurable conflict resolution policies, and the three-phase reconciliation model provide the granular control that enterprise provisioning requires. The engine is idempotent (safe to re-run) and produces comprehensive audit trails of every action taken.

**Connector framework (OpenICF).** The OpenICF connector framework (`OpenICF/OpenICF-java-framework/`) provides a clean SPI/API split that separates client code (API layer at `org.identityconnectors.framework.api/`) from connector implementation (SPI layer at `org.identityconnectors.framework.spi/`). Built-in connectors cover LDAP, JDBC (PostgreSQL, MySQL, Oracle, SQL Server), CSV, XML, SSH, Kerberos/AD, Groovy scripted, and HTTP/REST endpoints. The remote connector server (Protobuf RPC on port 8759) enables connectors to run on separate hosts near target systems, with HMAC-SHA256 authenticated handshake, multiplexed connections, round-robin failover, and circuit breaker patterns for flaky backends. Custom connectors implement a small set of operation interfaces (`CreateOp`, `UpdateOp`, `DeleteOp`, `SearchOp`, `SyncOp`, `AuthenticateOp`, `SchemaOp`) and are discovered at runtime via `META-INF/services` registration.

**BPMN 2.0 workflow integration.** The embedded Activiti workflow engine enables visual process modeling for approval chains, escalation, and complex lifecycle orchestration. Unlike commercial IGA platforms that treat workflow as a proprietary feature, OpenIDM's Activiti integration uses the open BPMN 2.0 standard, meaning process definitions are portable and can be authored in any BPMN-compliant editor (Camunda Modeler, Activiti Designer, Bizagi).

**REST-first architecture.** Every OpenIDM capability is accessible through a uniform REST API using CREST conventions. Managed objects, connectors, sync operations, reconciliation reports, workflows, audit logs, and configuration are all manipulable through HTTP/JSON. This enables integration with any programming language or automation tool without Java SDK dependencies.

**JSON-based configuration.** Unlike OpenAM's LDAP-backed configuration (see Chapter 7), OpenIDM uses JSON files for configuration (`managed.json`, `sync.json`, `provisioner.openicf-*.json`, `router.json`). These files are human-readable, version-controllable, and diff-friendly -- closer to modern configuration-as-code practices than LDAP-backed alternatives.

**Comprehensive audit trail.** The audit service captures before/after state for every managed object change, every sync/recon operation, every connector call, and every workflow action. Audit records are stored in the repository (JDBC or OrientDB) and queryable via REST at `/audit/access` and `/audit/activity`. This provides the evidentiary basis for compliance reporting, access reviews, and incident investigation.

**Link store for identity correlation.** The link store maintains bidirectional mappings between source and target object identifiers across systems. This enables OpenIDM to answer the question "which Active Directory account corresponds to this HR record?" without relying on matching attributes (which can change). Link records are stored in the repository and survive system restarts.

**Groovy scripted connector for rapid prototyping.** The `openicf-groovy-connector` enables custom connector development without Java compilation. Administrators can write Groovy scripts that implement CRUD + Sync operations against arbitrary APIs (REST services, file systems, legacy databases with non-standard schemas), test them in place, and iterate without build/deploy cycles. This dramatically reduces the time to integrate a new target system, particularly during proof-of-concept and pilot phases.

**Declarative mapping transformations.** Sync mappings support attribute-level transformations expressed as JavaScript or Groovy expressions directly in the JSON configuration. Common patterns -- concatenating first and last name into displayName, generating email addresses from username and domain, converting date formats, conditionally assigning default values -- are configured without code deployment. The transformation engine also supports conditional mappings (apply only when a condition expression evaluates to true) and multi-valued attribute handling (merge, replace, additive).

**Optimistic concurrency on managed objects.** Every managed object carries a `_rev` (revision) field that enables optimistic locking. Update operations must include the current `_rev` value; if the stored revision differs (indicating a concurrent modification), the update is rejected with a conflict error. This prevents lost updates in multi-client scenarios without the performance overhead of pessimistic locking or database-level row locks.

---

## 4. Weaknesses

**OSGi complexity.** The Apache Felix OSGi container introduces a layer of runtime complexity that is unfamiliar to most Java developers and operators. Bundle lifecycle management, service dependency resolution, classloader isolation, and the distinction between compile-time and runtime service availability create failure modes that do not exist in simple WAR or Spring Boot deployments. Debugging service resolution failures ("service not found" at runtime despite correct compile-time dependencies) requires OSGi-specific expertise that is increasingly rare. Modern Java frameworks (Spring Boot, Quarkus, Micronaut) have demonstrated that modularity can be achieved through build-time mechanisms without the runtime complexity of OSGi.

**OrientDB dependency.** OpenIDM supports OrientDB as a repository backend, but OrientDB's trajectory has been unstable. Originally developed by Orient Technologies, acquired by CallidusCloud, then SAP, and subsequently open-sourced under a permissive license, OrientDB has seen declining community engagement relative to PostgreSQL, MongoDB, or CockroachDB. The JDBC backend (PostgreSQL, MySQL) is the production-recommended option, but OrientDB remains embedded in the codebase as an alternative path, adding maintenance burden without clear value for new deployments.

**Limited IGA features vs. commercial platforms.** Commercial IGA platforms (SailPoint, Saviynt) offer capabilities that OpenIDM does not: AI-driven access outlier detection, automated access certification campaigns, separation of duties (SoD) policy enforcement, role mining and optimization, data access governance, and compliance control libraries (pre-built SOX, HIPAA, GDPR controls). OpenIDM provides the provisioning and sync engine but not the governance layer that enterprises increasingly require for regulatory compliance. The gap between "identity management" (OpenIDM) and "identity governance and administration" (SailPoint, Saviynt) is significant and widening.

**Activiti version and BPMN limitations.** The embedded Activiti engine is not the latest version; Activiti has since evolved into Activiti Cloud (Kubernetes-native) and been forked as Flowable. The version embedded in OpenIDM lacks modern features like CMMN (Case Management Model and Notation), DMN (Decision Model and Notation), and cloud-native workflow distribution. For complex workflow requirements, organizations may find the embedded engine limiting.

**No native SCIM endpoint.** OpenIDM does not expose a SCIM 2.0 server endpoint for inbound provisioning from external IdPs. It can consume identity data from source systems via connectors, but it cannot act as a SCIM service provider that receives push provisioning from Okta, Entra ID, or other SCIM-capable IdPs. This is a meaningful gap in modern identity architectures where SCIM is the standard inbound provisioning protocol (see Chapter 12).

**Small community and documentation.** OpenIDM's community is smaller than OpenAM's or OpenDJ's, reflecting its more specialized use case. Documentation for the OIP fork is minimal; operators must often consult ForgeRock-era documentation (which describes a diverged commercial product) or reverse-engineer behavior from configuration files and source code.

**Dual repository architecture complexity.** Supporting both JDBC and OrientDB as repository backends means maintaining two code paths, two sets of query implementations, and two sets of schema migration scripts. This complicates upgrades, testing, and bug reproduction. Modern practice would be to standardize on a single backend (PostgreSQL is the clear choice) and remove the OrientDB option.

**JavaScript/Groovy scripting security surface.** OpenIDM allows JavaScript and Groovy scripts in managed object lifecycle hooks, sync mapping transformations, and custom endpoints. While this provides flexibility, it also expands the attack surface: a malicious or poorly written script can access the JVM's full capabilities, read the filesystem, make arbitrary network connections, or exhaust resources. The OSGi sandbox provides some isolation, but script injection or configuration tampering (if an attacker gains write access to the configuration directory) can lead to arbitrary code execution. Commercial platforms like SailPoint's Actions (sandboxed serverless functions) and Auth0's Actions (Node.js with explicit permissions) provide safer extensibility models.

**No real-time event streaming.** OpenIDM's LiveSync mechanism is poll-based: connectors periodically query source systems for changes since the last sync token. The polling interval introduces latency between a change in the source system and its propagation to OpenIDM. Modern identity architectures increasingly expect event-driven provisioning via webhooks, OIDC Shared Signals Framework (SSF), or change data capture (CDC) streams. OpenIDM's poll-based model is adequate for most enterprise provisioning scenarios but falls short for real-time identity propagation requirements.

**Limited role modeling.** OpenIDM's managed objects support basic role assignment (user-to-role relationships) but lack the advanced role modeling capabilities that enterprise IGA requires: role hierarchies with inheritance, temporal role assignments (start/end dates), conditional role assignments based on attributes, role mining from existing entitlements, or role certification campaigns. These capabilities are foundational to SailPoint, Saviynt, and Midpoint, and their absence in OpenIDM is the clearest marker of the gap between "identity management" and "identity governance."

### Security Considerations

OpenIDM's security posture requires attention in several areas:

- **REST API authentication.** OpenIDM's REST API is protected by configurable authentication filters (session token, mutual TLS, or OpenAM integration). In default development configurations, the admin credentials may be simple (`openidm-admin/openidm-admin`), and operators must ensure production deployments enforce strong authentication and TLS.

- **Connector credential management.** Connector configurations contain credentials for target systems (LDAP bind passwords, database passwords, API keys). These are stored in the configuration directory and encrypted by OpenIDM's crypto service, but the encryption key management is local to the OpenIDM instance. Organizations should evaluate whether the built-in key management meets their security requirements or whether integration with an external secrets manager (HashiCorp Vault, AWS Secrets Manager) is necessary.

- **Script execution.** As noted above, JavaScript and Groovy scripts in managed object hooks and sync transformations execute within the JVM with access to the full Java runtime. Input validation in scripts is the operator's responsibility; OpenIDM does not sandbox script execution beyond OSGi bundle isolation.

- **CVE exposure.** The security commit analysis (see [security-cve-history extract](../extracts/security-cve-history.md)) shows 17 CVE-related commits and 77 security-keyword commits in the OpenIDM repository. Notable vulnerabilities include CVE-2019-17495 (Swagger UI XSS) and CVE-2023-22102 (MySQL Connector compromise). The dependency on OpenICF adds CVE-2024-47554 (Commons IO DoS) and CVE-2024-38999 (RequireJS prototype pollution) to the exposure surface. OIP has patched these in their respective repositories.

- **Remote connector server authentication.** The Protobuf RPC connection between OpenIDM and remote connector servers uses HMAC-SHA256 with a shared key for authentication. The shared key must be protected; compromise of the key allows an attacker to impersonate either endpoint. Mutual TLS is recommended as an additional layer for production deployments.

---

## 5. Modern Alternatives

### 5.1 OpenIDM vs SailPoint IdentityNow / Identity Security Cloud

SailPoint is the market leader in Identity Governance and Administration, positioned as a Gartner Magic Quadrant Leader with approximately $6.9 billion valuation (Thoma Bravo acquisition, 2024).

| Dimension | OpenIDM (OIP 7.0.2) | SailPoint ISC |
|-----------|----------------------|---------------|
| **Deployment** | Self-hosted (OSGi application) | Multi-tenant SaaS (Virtual Appliance for on-prem connectors) |
| **Provisioning** | Yes (OpenICF connectors) | Yes (200+ out-of-box connectors + SaaS Connectivity Framework) |
| **Reconciliation** | Yes (three-phase recon engine) | Yes (correlation, aggregation) |
| **Access certifications** | No | Yes (periodic access reviews with AI recommendations) |
| **Role mining** | No | Yes (AI-driven role discovery and optimization) |
| **Separation of duties** | No | Yes (SoD policy enforcement) |
| **Access request/approval** | Basic (Activiti BPMN) | Full (self-service portal, approval workflows, fulfillment) |
| **AI/ML** | No | Identity AI (outlier detection, recommendations, role optimization) |
| **Data access governance** | No | Yes (unstructured data visibility) |
| **Compliance controls** | Manual | Pre-built (SOX, HIPAA, GDPR control libraries) |
| **SCIM** | Outbound only (via connector) | Yes (both inbound and outbound) |
| **Pricing** | Free (CDDL) + operational cost | Enterprise pricing ($30K-500K+ annual, depending on scale) |
| **Community** | Small (OIP) | Commercial (SailPoint engineering + partner ecosystem) |

**SailPoint's decisive advantages** are in the governance layer: access certifications, SoD enforcement, role mining, and AI-driven recommendations. These capabilities are not features that can be bolted onto OpenIDM; they require fundamentally different data models (entitlement catalogs, certification campaigns, SoD rule engines) and years of domain-specific development.

**OpenIDM's advantages** are cost (free under CDDL), self-hosted sovereignty, and the ability to inspect and modify every aspect of the provisioning engine. For organizations that need provisioning and sync without governance -- academic institutions, small enterprises, or development environments -- OpenIDM provides the core engine without SailPoint's enterprise pricing.

### 5.2 OpenIDM vs Saviynt

Saviynt is a cloud-native IGA platform that has rapidly gained market share, reaching Gartner Leader status in 2023.

| Dimension | OpenIDM (OIP 7.0.2) | Saviynt EIC |
|-----------|----------------------|-------------|
| **Architecture** | OSGi on-premises | Cloud-native SaaS (AWS) |
| **Provisioning** | OpenICF connectors | 500+ connectors (deep ERP: SAP, Oracle, Workday) |
| **IGA features** | Limited (provisioning + sync) | Full IGA + Cloud PAM + Application Access Governance |
| **ERP governance** | Basic JDBC connector | Deep SAP authorization objects, Oracle EBS roles |
| **Compliance** | Manual | Control Exchange (pre-built SOX, HIPAA controls) |
| **Third-party identity** | Via connector | Native non-employee identity management |
| **AI/ML** | No | Identity analytics, risk scoring |
| **Pricing** | Free + infrastructure | Enterprise SaaS pricing |

**Saviynt's differentiator** over SailPoint (and by extension, over OpenIDM) is its born-in-the-cloud architecture and its deep ERP access governance, particularly for SAP environments where fine-grained authorization objects require specialized connector logic that generic JDBC connectors cannot provide.

**OpenIDM's position relative to Saviynt** is clear: OpenIDM is a provisioning engine, not a governance platform. Organizations evaluating Saviynt have governance requirements (access certifications, SoD, compliance automation) that OpenIDM does not address.

### 5.3 OpenIDM vs SCIM 2.0 Native Provisioning

An increasingly common architecture replaces dedicated provisioning middleware with direct SCIM 2.0 integration between the IdP and target applications.

| Dimension | OpenIDM | SCIM-Native Architecture |
|-----------|---------|--------------------------|
| **Pattern** | Dedicated provisioning middleware (hub-and-spoke) | Point-to-point SCIM push from IdP to applications |
| **Protocol** | Proprietary connector framework (OpenICF) | Standardized SCIM 2.0 (RFC 7642-7644) |
| **Middleware** | Required (OpenIDM + connectors) | Not required (IdP pushes directly) |
| **Transformation** | Rich (JavaScript/Groovy in mappings) | Limited (SCIM schema extensions, IdP-side transforms) |
| **Non-SCIM targets** | Supported (SSH, JDBC, CSV, custom connectors) | Not supported (SCIM only) |
| **Operational cost** | OpenIDM instance + connector management | Zero middleware (IdP-managed) |

Modern IdPs (Okta, Entra ID, Keycloak with SCIM extension, Zitadel, Authentik) can push user and group provisioning directly to SCIM-compliant applications without middleware. For organizations whose target systems all support SCIM 2.0, this architecture eliminates OpenIDM entirely.

**OpenIDM remains necessary** when target systems do not support SCIM: legacy LDAP directories, databases with custom schemas, mainframe systems accessible only via SSH, or custom applications with proprietary APIs. The OpenICF connector framework bridges these gaps that SCIM cannot reach. The practical question is the ratio of SCIM-compliant to non-SCIM targets: if most targets support SCIM, the value of dedicated middleware diminishes.

### 5.4 OpenIDM vs Midpoint (Evolveum)

Midpoint is the closest open-source competitor to OpenIDM: a Java-based identity governance and administration platform maintained by Evolveum (Slovakia).

| Dimension | OpenIDM (OIP 7.0.2) | Midpoint (v4.8+) |
|-----------|----------------------|-------------------|
| **License** | CDDL 1.0 | Apache 2.0 |
| **Language** | Java (OSGi) | Java (Spring Boot) |
| **Provisioning** | Yes (OpenICF connectors) | Yes (ConnId connectors, compatible with ICF) |
| **Reconciliation** | Yes (three-phase) | Yes (comprehensive correlation and sync) |
| **Access certifications** | No | Yes (campaign-based reviews) |
| **Role management** | Basic (managed objects) | Advanced (role mining, role catalog, inducements) |
| **Organizational structure** | Basic | Advanced (orgs as first-class objects, delegated admin) |
| **Policy enforcement** | Basic | Policy rules with segregation of duties |
| **Workflow** | Activiti BPMN | Built-in approval workflows (BPMN-like) |
| **GUI** | REST API + basic admin | Full admin GUI (Wicket-based) |
| **Documentation** | Sparse (OIP) | Extensive (Evolveum docs, book) |
| **Community** | Small | Moderate (active forum, commercial support from Evolveum) |
| **Commercial support** | 3A Systems | Evolveum (subscription model) |

**Midpoint's advantages over OpenIDM** are substantial: it provides access certifications, role mining, organizational structure management, SoD policy rules, and a comprehensive admin GUI -- features that push it from "identity management" into "identity governance." Its connector framework (ConnId) is API-compatible with OpenICF, meaning existing ICF connectors can run in Midpoint with minimal modification. Spring Boot deployment is operationally simpler than OSGi.

**OpenIDM's advantages** are its tighter integration with the OIP stack (OpenAM for authentication, OpenDJ for directory, OpenIG for gateway) and its REST-first design. For organizations already invested in the OIP ecosystem, OpenIDM provides provisioning without introducing a second vendor's technology stack.

For organizations evaluating open-source IGA from scratch (without existing OIP investment), Midpoint is the stronger choice due to its governance features, better documentation, and more active community.

---

## 6. The IGA Market

### Where OpenIDM Fits

The identity governance and administration market segments into three tiers:

**Tier 1: Enterprise IGA platforms (SailPoint, Saviynt, One Identity, IBM Security Verify Governance).** These platforms provide the full governance stack: provisioning, access certifications, SoD enforcement, role management, AI-driven analytics, and compliance automation. Annual license costs range from $30K to $500K+ depending on user count and features. They target large enterprises with regulatory compliance requirements (SOX, HIPAA, GDPR, NIS2) and serve organizations with thousands to millions of identities.

**Tier 2: Open-source IGA (Midpoint, OpenIDM).** These platforms provide provisioning and sync with varying degrees of governance capability. Midpoint reaches into governance territory (access certifications, role mining, SoD). OpenIDM remains primarily a provisioning engine. Both are viable for organizations that cannot or will not pay Tier 1 pricing but need identity lifecycle automation. Total cost of ownership includes infrastructure, operational expertise, and the opportunity cost of building governance features that commercial platforms provide out of the box.

**Tier 3: SCIM-native / no-middleware.** Modern architectures increasingly bypass dedicated IGA middleware for organizations whose target systems all support SCIM 2.0. The IdP (Okta, Entra ID, Keycloak) pushes provisioning directly to applications. This approach works well for cloud-native SaaS environments but fails for legacy targets without SCIM endpoints.

OpenIDM sits firmly in Tier 2, competing primarily with Midpoint for open-source provisioning use cases. It does not compete with Tier 1 platforms on governance features, nor with Tier 3 approaches on operational simplicity.

### Market Trends Affecting OpenIDM

**AI-driven governance.** SailPoint and Saviynt are investing heavily in AI/ML for access outlier detection, role optimization, and certification recommendations. OpenIDM has no AI capability and no clear path to adding it given the community's size and focus.

**Cloud-native provisioning.** The shift from on-premises middleware to SaaS-based provisioning (SailPoint Identity Security Cloud, Saviynt Enterprise Identity Cloud) makes OpenIDM's self-hosted OSGi deployment model feel increasingly dated. Modern enterprises expect SaaS delivery with API-first management.

**SCIM ubiquity.** As more applications implement SCIM 2.0 endpoints, the need for custom connector frameworks (OpenICF) diminishes. The long tail of non-SCIM legacy systems keeps connector frameworks relevant, but the addressable market for dedicated provisioning middleware shrinks with each SaaS application that adds SCIM support.

**Convergence of IAM and IGA.** Commercial vendors are converging access management (IAM) and identity governance (IGA) into unified platforms. Ping Identity's merger with ForgeRock, Okta's addition of Identity Governance, and CyberArk's expansion into identity all reflect this trend. The OIP suite's separation of OpenAM (IAM) and OpenIDM (provisioning) maps to an older market structure where these were distinct product categories.

### OpenIDM's Niche

Despite the market pressures described above, OpenIDM occupies a defensible niche for a specific class of organization:

- **Universities and research institutions** that need automated provisioning between student information systems, HR databases, LDAP directories, and learning management systems -- but lack the budget for SailPoint or Saviynt. OpenIDM's mapping engine handles these flows, and its REST API integrates with custom admission and enrollment systems.

- **Government agencies** with air-gapped networks where SaaS IGA is not an option and Midpoint's GPL-compatible Apache 2.0 license may not satisfy procurement requirements differently than OpenIDM's CDDL license. (Note: CDDL and Apache 2.0 are both OSI-approved; license preference varies by agency policy.)

- **Organizations already running the OIP stack** (OpenAM + OpenDJ) that need provisioning without introducing a second vendor's technology. OpenIDM's integration with OpenAM for authentication and OpenDJ for identity storage is architecturally coherent and well-tested.

- **Development and test environments** where a lightweight, JSON-configured provisioning engine is needed for identity lifecycle testing. OpenIDM's OrientDB backend enables zero-dependency startup for local development.

For organizations outside these niches, the value proposition of dedicated provisioning middleware (vs. SCIM-native or commercial IGA) must be evaluated against the operational costs of running and maintaining an OSGi-based Java application with a small community.

### Cross-Component Integration

OpenIDM's position within the OIP suite creates integration patterns that span all five components (see the system architecture diagram in the project's CLAUDE.md):

```
Users/Apps --> OpenIG (gateway) --> OpenAM (SSO/auth) --> OpenDJ (LDAP store)
                                    OpenIDM (provisioning) --> OpenICF (connectors) --> External Systems
```

- **OpenIDM <-> OpenDJ.** OpenDJ serves as the primary identity store. Sync mappings connect `managed/user` (OpenIDM's managed object) to `system/ldap/account` (OpenDJ via the LDAP connector). LiveSync detects changes in OpenDJ's changelog and propagates them to downstream systems.

- **OpenIDM <-> OpenAM.** OpenIDM can invoke OpenAM for authentication of its own REST API (session validation). OpenAM can trigger OpenIDM workflows on authentication events (e.g., creating a managed object when a user first authenticates via social login).

- **OpenIDM <-> OpenICF.** The router dispatches `/system/*` requests to `ConnectorFacade` instances, which communicate with external systems through local or remote connectors. The OpenICF framework's SPI contract is OpenIDM's primary extension mechanism for reaching systems beyond LDAP and SQL.

This integration model is coherent but tightly coupled to the OIP ecosystem. Organizations that adopt Keycloak instead of OpenAM, or PostgreSQL instead of OpenDJ, lose the integration benefits that justify OpenIDM's architectural complexity.

### Production Deployment Topology

A production OpenIDM deployment involves several infrastructure decisions that significantly affect reliability, performance, and operational complexity. The following diagram illustrates a typical production topology:

```
                          ┌─────────────────────────────┐
                          │       Load Balancer          │
                          │    (HAProxy / F5 / ALB)      │
                          └──────────┬──────────────────-┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                 │
              ┌─────▼─────┐   ┌─────▼─────┐    ┌─────▼─────┐
              │  OpenIG    │   │  OpenIG    │    │  OpenIG    │
              │ (gateway)  │   │ (gateway)  │    │ (gateway)  │
              └─────┬──────┘   └─────┬──────┘    └─────┬──────┘
                    │                │                  │
              ┌─────▼──────────────-─▼─────────────────▼─────┐
              │              OpenAM (SSO/AuthN)               │
              └──────────────────┬───────────────────────────-┘
                                 │ session validation
              ┌──────────────────▼───────────────────────────-┐
              │         OpenIDM (active instance)              │
              │  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
              │  │ SyncEngine│ │ Workflow │ │ Managed Objects│  │
              │  │ (Recon)   │ │(Activiti)│ │  (CRUD+hooks) │  │
              │  └─────┬─────┘ └────┬─────┘ └───────┬───────┘  │
              └────────┼────────────┼───────────────┼──────────┘
                       │            │               │
         ┌─────────────▼────────────▼───────────────▼──────────┐
         │          PostgreSQL (JDBC repository)                │
         │  [managed objects] [links] [audit] [workflow state]  │
         └──────────────────────────────────────────────────────┘
                       │
         ┌─────────────▼──────────────────────┐
         │    OpenIDM (warm standby)           │
         │    (shares same JDBC repository)    │
         └────────────────────────────────────-┘

              ┌────────────────────────────────┐
              │  Remote OpenICF Connector       │
              │  Server (corporate LAN zone)    │
              │  ┌────────┐  ┌───────────────┐  │
              │  │  LDAP   │  │ JDBC (HR DB) │  │
              │  │connector│  │  connector    │  │
              │  └────┬────┘  └──────┬────────┘  │
              └───────┼──────────────┼───────────┘
                      │              │
                ┌─────▼────┐  ┌─────▼──────┐
                │   Active  │  │  Oracle HR  │
                │ Directory │  │  Database   │
                └───────────┘  └────────────┘
```

#### OSGi Container: Single-Node vs Clustered

OpenIDM runs as a single Apache Felix v5.x OSGi process. Unlike OpenAM, which supports session replication across a cluster of instances behind a load balancer, OpenIDM does not natively support active-active clustering. The reconciliation engine maintains in-memory state (current phase, processed object counts, link cache) that is not replicated between instances.

Production deployments typically run OpenIDM as a single active instance with a warm standby for failover, using an external load balancer or DNS failover to redirect traffic. The warm standby shares the same JDBC repository, so managed objects and link records are immediately available on failover, but in-flight reconciliation jobs are lost and must be restarted.

Organizations requiring higher availability can run multiple OpenIDM instances with partitioned workloads -- each instance owns a subset of sync mappings -- but this requires careful coordination to avoid duplicate processing and link store conflicts.

#### JDBC Repository Backend

The production-recommended repository is a relational database accessed via the JDBC module (`OpenIDM/openidm-repo-jdbc/`). The `DatabaseType` enum (`OpenIDM/openidm-repo-jdbc/src/main/java/org/forgerock/openidm/repo/jdbc/DatabaseType.java`) enumerates supported backends:

| Database | TableHandler | Notes |
|----------|-------------|-------|
| PostgreSQL | `PostgreSQLTableHandler`, `PostgreSQLMappedTableHandler` | Native JSONB columns, strongest choice for new deployments |
| MySQL | `MySQLTableHandler` | Second most common, JSON column support in 5.7+ |
| SQL Server | `MSSQLTableHandler`, `MSSQLMappedTableHandler` | Windows-centric environments |
| Oracle | `OracleTableHandler`, `OracleMappedTableHandler` | Enterprise Oracle shops |
| DB2 | `DB2TableHandler` | IBM mainframe environments |
| H2 | via `GenericTableHandler` | In-memory testing only |

Each database has a dedicated `TableHandler` implementation that handles SQL dialect differences, JSON column types, and vendor-specific exception mapping via corresponding `SQLExceptionHandler` classes (`MySQLExceptionHandler`, `MSSQLExceptionHandler`, `DB2SQLExceptionHandler`, `DefaultSQLExceptionHandler`).

Connection pooling is handled by HikariCP (`HikariCPDataSourceConfig`, `HikariCPDataSourceFactory`), with BoneCP available as a legacy alternative. The repository stores managed objects, link records, audit logs, configuration, and Activiti workflow state -- all in the same database unless explicitly separated.

#### OrientDB for Development Only

The OrientDB backend (`OpenIDM/openidm-repo-orientdb/`) runs as an embedded document database via `EmbeddedOServerService`, requiring zero external infrastructure. This makes it useful for local development and rapid prototyping: a single `./startup.sh` command starts OpenIDM with a fully functional repository.

However, OrientDB lacks the transactional guarantees, replication maturity, backup tooling, and operational expertise that production deployments require. The `OrientDBRepoService` and associated query infrastructure (`ConfiguredQueries`, `PredefinedQueries`) implement a parallel code path to the JDBC module, meaning bugs fixed in one backend may not be fixed in the other. Production deployments should always use the JDBC backend.

#### External OpenICF Connector Server

For target systems that reside in network segments inaccessible from the OpenIDM host (e.g., Active Directory domain controllers in a corporate LAN, databases behind firewalls), OpenICF's remote connector server runs as a separate process on a host with network access to those targets. The remote server communicates with OpenIDM over Protobuf RPC (default port 8759), authenticated via HMAC-SHA256 shared key.

This topology enables a "connector-near-target" deployment: the OpenICF connector server sits in the same network zone as the target system, avoiding firewall exceptions for every target. Multiple remote connector servers can run in parallel behind round-robin selection with circuit breaker failover.

Sync failure handling supports multiple strategies for resilient processing of transient target failures:

- `DeadLetterQueueHandler` -- persists failed sync events to a repository-backed queue for later manual or automated retry.
- `InfiniteRetrySyncFailureHandler` -- retries the failed operation indefinitely with configurable backoff.
- `SimpleRetrySyncFailureHandler` -- retries a configurable number of times before escalating.
- `ScriptedSyncFailureHandler` -- executes a custom Groovy script on failure, enabling application-specific error handling (e.g., sending alerts, writing to external audit systems).

#### Workflow Engine (Activiti BPMN)

The embedded Activiti engine (`ActivitiServiceImpl`) uses the same JDBC data source as the OpenIDM repository for workflow state persistence (process instances, task assignments, history). In production, this means workflow state is transactionally consistent with managed object state -- an approval that completes and triggers account creation is atomic within the database.

BPMN process definitions are deployed through REST or placed in a monitored directory. The `SharedIdentityService` bridges Activiti's user/group model with OpenIDM's managed objects, allowing workflow task assignment to reference managed users and roles without a separate identity store for the workflow engine. Common production workflow patterns include:

- **Access request/approval.** User requests a role assignment via REST; workflow routes to the user's manager for approval; on approval, the role is assigned and downstream sync mappings propagate the entitlement to target systems.
- **Onboarding sequences.** HR system creates a managed user via sync; workflow orchestrates sequential account creation across multiple target systems with wait states for manual verification at each step.
- **Escalation chains.** Approval tasks left unactioned for a configurable period are escalated to a backup approver or auto-approved/denied based on policy.

#### Integration with OpenAM for SSO-Protected Admin Console

OpenIDM's REST API can be protected by OpenAM's policy agent or by configuring OpenIDM's authentication filter to validate OpenAM session tokens. In a production OIP deployment, the typical pattern is:

1. OpenIG sits in front of OpenIDM's admin endpoint.
2. OpenIG enforces authentication via OpenAM (SSO cookie validation).
3. OpenIG passes the authenticated principal to OpenIDM in a header.
4. OpenIDM's authorization filter evaluates RBAC policies against the authenticated user.

This eliminates the need for separate admin credentials (`openidm-admin/openidm-admin`) in production and provides centralized audit of admin access through OpenAM's access logs.

### Migration Cost Analysis

Organizations considering migration away from OpenIDM face varying levels of effort depending on the target platform. The core challenge is that OpenIDM's configuration model -- JSON-based sync mappings, Groovy/JavaScript lifecycle hooks, OpenICF connector configurations, and Activiti BPMN workflows -- has no direct portable equivalent in any target platform.

**OpenIDM to SailPoint IdentityNow (Identity Security Cloud).** SailPoint replaces OpenIDM's sync mappings with "identity profiles" and "transforms" for attribute computation. Each OpenIDM mapping (`sync.json` entry) must be recreated as a SailPoint source-to-identity-profile connection. Attribute transformations written as JavaScript or Groovy expressions in OpenIDM mappings must be rewritten as SailPoint transforms (a declarative JSON format with ~30 built-in transform types) or as SailPoint Rules (BeanShell scripts, requiring SailPoint Expert Services approval for cloud deployments). OpenICF connectors must be replaced with SailPoint connectors or the SaaS Connectivity Framework (TypeScript-based); LDAP and JDBC connectors have direct SailPoint equivalents, but custom Groovy scripted connectors require ground-up reimplementation. Activiti BPMN workflows must be redesigned using SailPoint's approval framework, which is less flexible than arbitrary BPMN but covers common access request/approval patterns. Estimated effort: 3-6 months for a deployment with 5-10 source/target systems, dominated by connector replacement and workflow redesign.

**OpenIDM to Saviynt Enterprise Identity Cloud.** Saviynt's mapping model uses "connection" configurations with attribute mappings that are conceptually similar to OpenIDM's sync.json but use Saviynt's own expression language. The migration effort for attribute mappings is comparable to SailPoint. Saviynt has better native SCIM 2.0 support, so targets that OpenIDM reached via custom OpenICF connectors may be reachable via Saviynt's SCIM connector without custom code. Saviynt's deep ERP connectors (SAP, Oracle EBS, Workday) may simplify integrations that required complex Groovy scripted connectors in OpenIDM. Workflows transition to Saviynt's workflow designer, which supports multi-level approvals and escalations but uses a proprietary visual model rather than BPMN. The OrientDB-to-Saviynt data migration is straightforward (export managed objects as JSON, transform to Saviynt import format); JDBC repository migration is similarly a SQL export/transform/load operation. Estimated effort: 2-5 months, potentially lower than SailPoint if ERP connectors reduce custom integration work.

**OpenIDM to Midpoint (Evolveum).** Midpoint is the closest architectural match to OpenIDM: both are Java-based identity management platforms with connector frameworks (OpenICF vs ConnId, which is API-compatible), sync/recon engines, and managed object models. However, the configuration formats differ fundamentally. OpenIDM uses JSON configuration (`sync.json`, `managed.json`, `provisioner.openicf-*.json`); Midpoint uses XML-based "resource definitions" and "object templates" with its own expression language. Each sync mapping must be translated to a Midpoint resource definition with inbound/outbound mappings. OpenICF connectors can run in Midpoint via the ConnId compatibility layer with minimal modification, since ConnId descends from the same Sun ICF codebase. This is the single largest migration advantage: existing connector JARs (LDAP, JDBC, CSV) work in both platforms. Activiti workflows must be replaced with Midpoint's built-in approval mechanisms (policy rules with approval actions), which are less visually modelable but more tightly integrated with Midpoint's policy engine. Estimated effort: 2-4 months, with connector reuse offsetting the XML configuration translation cost.

**Key risk: custom Groovy scripts.** The single largest migration risk across all three target platforms is custom Groovy scripting. OpenIDM allows Groovy (and JavaScript) in managed object lifecycle hooks (`onCreate`, `onUpdate`, `onDelete`, `onRead`, `postCreate`, `postUpdate`, `postDelete`), sync mapping attribute transformations, correlation queries, situation-action scripts, custom endpoints, and scripted connectors. Organizations with mature OpenIDM deployments may have dozens of Groovy scripts encoding business logic -- username generation algorithms, conditional attribute derivation, multi-system correlation rules, error handling and notification logic.

These scripts have no portable equivalent:

- **SailPoint** uses BeanShell (restricted in cloud deployments, requires Expert Services approval) or transforms (declarative JSON, ~30 built-in types, limited expressiveness).
- **Saviynt** uses its own expression language with a narrower function library than Groovy's full JVM access.
- **Midpoint** uses its own XML-embedded expression language. Groovy is partially supported in Midpoint expressions, but the script context objects (`source`, `target`, `openidm.*` functions) and APIs differ completely from OpenIDM's script bindings.

Every Groovy script must be analyzed, its intent understood, and the logic reimplemented in the target platform's idiom. This is the most labor-intensive and error-prone component of any OpenIDM migration.

#### Migration Summary

| Dimension | SailPoint ISC | Saviynt EIC | Midpoint |
|-----------|--------------|-------------|----------|
| **Mapping translation** | Identity profiles + transforms | Connection configs | XML resource definitions |
| **Connector reuse** | None (SailPoint connectors or SaaS Connectivity Framework) | Partial (SCIM targets simplify) | High (ConnId is ICF-compatible) |
| **Workflow migration** | Approval framework (less flexible) | Proprietary visual designer | Built-in approval policies |
| **Groovy script portability** | None (BeanShell/transforms) | None (proprietary expressions) | Partial (Groovy supported, different APIs) |
| **Data export** | SQL/JSON export + transform | SQL/JSON export + transform | SQL/JSON export + transform |
| **Estimated effort (5-10 targets)** | 3-6 months | 2-5 months | 2-4 months |
| **Governance features gained** | Full IGA (certifications, SoD, AI) | Full IGA + ERP governance | Access certifications, role mining, SoD |
| **Cost model change** | Free -> $30K-500K+/year | Free -> enterprise SaaS pricing | Free -> free (Apache 2.0) + optional support |

### Codebase Navigation Guide

For developers and architects evaluating OpenIDM's source, the following module map identifies the key entry points for each major subsystem. All paths are relative to the `OpenIDM/` repository root. OpenIDM contains 42 modules in total; the five described below are the most architecturally significant.

| Module | Purpose | Key Entry Class | Java Files |
|--------|---------|----------------|------------|
| `openidm-core/` | Sync engine, reconciliation, managed objects | `SynchronizationService`, `ReconciliationService` | 50+ (sync/impl/) |
| `openidm-provisioner-openicf/` | OpenICF connector bridge | `OpenICFProvisionerService` | 30+ |
| `openidm-workflow-activiti/` | BPMN 2.0 workflow engine | `ActivitiServiceImpl` | 33 |
| `openidm-repo-jdbc/` | JDBC repository backend | `JDBCRepoService` | 51 |
| `openidm-repo-orientdb/` | OrientDB repository backend | `OrientDBRepoService` | 13 |
| `openidm-script/` | Groovy/JS scripting infrastructure | `ScriptRegistryService` | 8 |

**`openidm-core/` -- Sync engine and reconciliation.** The most architecturally significant module. The sync engine lives in `src/main/java/org/forgerock/openidm/sync/impl/`. Key classes: `SynchronizationService` (OSGi service entry point, handles `/sync` route, dispatches LiveSync and implicit sync operations), `ReconciliationService` (manages reconciliation lifecycle, thread pool, JMX monitoring via `ReconciliationServiceMBean`), `ObjectMapping` (represents a single sync mapping with source, target, properties, policies, and correlation configuration), `Recon` and `ReconPhase` (reconciliation state machine coordinating source, target, and link phases), `SyncOperation`/`SourceSyncOperation`/`TargetSyncOperation` (per-object sync execution with situation detection and action dispatch), `Link` and `LinkType` (link store access for source-to-target ID mappings), and `Correlation` (matching logic to find target objects for unlinked source objects). The `Situation` enum defines the 12 possible states (SOURCE_MISSING, TARGET_MISSING, CONFIRMED, FOUND, AMBIGUOUS, etc.) that drive the policy engine's action selection. `ReconciliationStatistic` and `PhaseStatistic` capture per-run metrics exposed in recon reports.

**`openidm-provisioner-openicf/` -- Connector integration.** Bridges OpenIDM's CREST request model to OpenICF's `ConnectorFacade` API. Key classes: `OpenICFProvisionerService` (the central OSGi service, implements `ProvisionerService`, registers `/system/{connector}` routes, manages connector lifecycle and configuration), `ConnectorInfoProviderService` (discovers and manages local and remote connector bundles, handles connection to remote OpenICF connector servers), `ObjectClassResourceProvider` (translates CREST CRUD operations to OpenICF `CreateOp`/`UpdateOp`/`DeleteOp`/`SearchOp` calls), `OpenICFFilterAdapter` (converts CREST query filters to OpenICF filter objects), and the `syncfailure/` package (`DeadLetterQueueHandler`, `InfiniteRetrySyncFailureHandler`, `SimpleRetrySyncFailureHandler`, `ScriptedSyncFailureHandler`) which implements configurable failure handling strategies for LiveSync operations.

**`openidm-workflow-activiti/` -- BPMN workflows.** Embeds the Activiti process engine within OpenIDM's OSGi runtime. Key classes: `ActivitiServiceImpl` (initializes the `ProcessEngine` with OpenIDM's JDBC data source, configures custom resolver factories and session factories), `ProcessInstanceResource` and `TaskInstanceResource` (REST resource providers for `/workflow/processinstance` and `/workflow/taskinstance` endpoints), `SharedIdentityService` (bridges Activiti's identity model with OpenIDM's managed users/groups via `JsonUser`, `JsonUserQuery`, `JsonGroup`, `JsonGroupQuery`), `OpenIDMELResolver` and `OpenIDMResolverFactory` (enable BPMN process definitions to access OpenIDM's router via expression language, allowing workflow scripts to read/write managed objects), and `ProcessDefinitionResource`/`TaskDefinitionResource` (BPMN definition deployment and introspection).

**`openidm-repo-jdbc/` and `openidm-repo-orientdb/` -- Dual repository support.** The JDBC module provides production-grade persistence. Key classes: `JDBCRepoService` (OSGi service implementing the repository contract for `/repo/*` routes, dispatches to database-specific table handlers), `GenericTableHandler` (default handler using JSON-in-column storage with `GenericSQLQueryFilterVisitor` for query translation), `MappedTableHandler` (explicit column-per-attribute mapping for performance-critical tables), and database-specific handlers (`PostgreSQLTableHandler`, `MySQLTableHandler`, `OracleTableHandler`, `MSSQLTableHandler`, `DB2TableHandler`) that handle SQL dialect differences. Connection pooling is configured via `HikariCPDataSourceConfig` / `HikariCPDataSourceFactory`, with `BoneCPDataSourceConfig` as a legacy alternative. The OrientDB module mirrors this structure: `OrientDBRepoService` implements the same repository contract, with `EmbeddedOServerService` managing the embedded database lifecycle and `ConfiguredQueries`/`PredefinedQueries` handling the OrientDB-specific query language.

**`openidm-script/` -- Groovy/JavaScript scripting hooks.** Provides the scripting infrastructure used by managed object lifecycle hooks, sync mapping transformations, and custom endpoints. Key classes: `ScriptRegistryService` (OSGi service that manages script compilation, caching, and execution using `javax.script.ScriptEngine`), `AbstractScriptedService` (base class for OSGi services that expose custom scripted endpoints), `ScriptedRequestHandler` (CREST request handler that executes a configured script on each request), `ResourceFunctions` (utility functions injected into script scope: `openidm.create()`, `openidm.read()`, `openidm.update()`, `openidm.delete()`, `openidm.query()`, `openidm.action()` -- these are the functions that scripts call to interact with OpenIDM's router), and `ScriptExecutor` (executes scripts within a configured context with bindings for the current request, managed object state, and router access). The script directory (`script/` in the OpenIDM installation) is monitored for changes, enabling hot-reload of script modifications without restarting the OSGi container.

---

## 7. Verdict

OpenIDM provides a competent identity provisioning and synchronization engine with genuine architectural strengths: a flexible mapping-based sync/recon engine, a well-designed connector framework (OpenICF) with remote execution capability, BPMN 2.0 workflow integration, and a REST-first JSON API. Within the OIP ecosystem, it fills the essential role of identity lifecycle management, connecting OpenAM's authentication with OpenDJ's directory storage and external systems via OpenICF connectors. However, its OSGi runtime complexity, OrientDB legacy, absence of governance features (access certifications, SoD, role mining), lack of native SCIM server endpoints, and small community place it at a disadvantage against both commercial IGA platforms and its open-source peer Midpoint. OpenIDM's strongest use case is as the provisioning layer within an existing OIP or WrenAM deployment, where its tight integration with OpenAM and OpenDJ provides coherent identity lifecycle management without introducing a second vendor stack. For organizations evaluating open-source IGA independently of the OIP ecosystem, Midpoint offers more governance capability with better documentation and a more modern runtime. For organizations with budget for commercial IGA and regulatory compliance requirements, the gap between OpenIDM and SailPoint/Saviynt is too large to bridge with operational effort alone.
