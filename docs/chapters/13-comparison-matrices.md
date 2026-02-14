# Chapter 13: Comparison Matrices

This chapter consolidates the component-level analyses from earlier chapters into structured comparison tables across eight IAM functional domains: access management (Table 1), directory services (Table 2), identity governance (Table 3), API/identity gateways (Table 4), connector/integration frameworks (Table 5), privileged access management (Table 6), identity threat detection and response (Table 7), and workload identity (Table 8). Tables 1-5 compare OIP components against modern alternatives. Tables 6-8 cover adjacent domains not addressed by the OIP stack but critical to modern IAM architectures. A Tier 2 access management section tracks emerging OSS alternatives (Casdoor, SuperTokens). Following the tables, decision frameworks and cross-cutting considerations provide guidance for selecting between options. Data reflects the state of the market as of early 2026; version numbers and feature sets should be verified against current sources before use in procurement decisions.

---

## Table 1: Access Management

This table compares platforms that handle authentication, single sign-on, federation, and session management -- the domain covered by OpenAM (analyzed in detail in prior chapters) and its fork Wren:AM (see [Chapter 1: Historical Narrative](01-history.md) for fork lineage).

| Feature | OpenAM (OIP) | Keycloak | Auth0 | Okta WIC | AWS Cognito | Ory Stack | Zitadel | Authentik |
|---------|-------------|----------|-------|----------|-------------|-----------|---------|-----------|
| **Version** | 16.0.5 | 26.x-27.x | SaaS | SaaS | SaaS | Hydra 2.3, Kratos 1.3 | 2.x | 2024.x-2025.x |
| **License** | CDDL 1.0 | Apache 2.0 | Proprietary | Proprietary | Proprietary | Apache 2.0 | Apache 2.0 | SSPL |
| **Language** | Java | Java (Quarkus) | N/A (SaaS) | N/A (SaaS) | N/A (SaaS) | Go | Go | Python (Django) |
| **SAML 2.0 IdP** | Yes | Yes | Yes | Yes | No (SP only) | No | Yes | Yes |
| **SAML 2.0 SP** | Yes | Yes | Yes | Yes | Yes | No | Yes | Yes |
| **OIDC Provider** | Yes | Yes (certified) | Yes (certified) | Yes | Yes | Yes (certified, Hydra) | Yes | Yes |
| **OAuth 2.0** | Yes (all grants) | Yes (all grants) | Yes | Yes | Yes | Yes (Hydra) | Yes | Yes |
| **WS-Federation** | Yes | No | No | No | No | No | No | No |
| **MFA - TOTP** | Yes | Yes | Yes | Yes | Yes | Yes (Kratos) | Yes | Yes |
| **MFA - WebAuthn/Passkeys** | Yes (OIP only) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| **MFA - Push** | Yes | No (ext) | Yes | Yes (Okta Verify) | No | No | No | No |
| **MFA - SMS/Email OTP** | Yes (HOTP) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| **Social Login** | Yes (OAuth2 module) | Yes (50+ IdPs) | Yes (70+) | Yes (OIN) | Yes | Yes (Kratos OIDC) | Yes | Yes |
| **User Federation** | LDAP/AD (OpenDJ) | LDAP, AD, custom SPI | Enterprise connections | 7,000+ OIN apps | SAML, OIDC | No (API-first) | LDAP (planned) | LDAP, SAML, OIDC sources |
| **Self-Service** | Yes (OIP 16.x) | Yes | Yes | Yes | Yes | Yes (Kratos flows) | Yes | Yes |
| **Admin UI** | Yes (legacy JSP) | Yes (React, modern) | Yes (SaaS dashboard) | Yes (SaaS dashboard) | Yes (AWS Console) | No (API-only) | Yes (Angular console) | Yes (Lit web components) |
| **Visual Flow Editor** | No | No | No (Actions pipeline) | No | No | No | No | Yes (unique) |
| **SCIM Provisioning** | No | Via extension | Yes | Yes | No | No | Yes (2024) | Yes |
| **Event Sourcing** | No | No | No | No | No | No | Yes (core arch) | No |
| **Kubernetes Native** | No | Yes (Operator) | N/A (SaaS) | N/A (SaaS) | N/A (SaaS) | Yes (Helm, K8s) | Yes (single binary) | Yes (Docker, Helm) |
| **Scalability** | Horizontal (Cassandra CTS) | Horizontal (Infinispan) | Elastic (SaaS) | Elastic (SaaS) | Elastic (SaaS) | Horizontal (stateless) | Horizontal (CQRS) | Horizontal (Celery workers) |
| **Deployment Model** | Self-hosted | Self-hosted, managed (RHBK) | SaaS, private cloud | SaaS | SaaS (AWS only) | Self-hosted, Ory Network | Self-hosted, Zitadel Cloud | Self-hosted |
| **Pricing Model** | Free (OSS) | Free (OSS), RHBK sub | Per-MAU ($35+/mo) | Per-user/mo ($2-9) | Per-MAU ($0.005+) | Free (OSS), Ory Network | Free (OSS), Cloud sub | Free (source-available) |
| **Community (GitHub Stars)** | ~700 | ~26,000 | N/A | N/A | N/A | ~40,000 (combined) | ~9,500 | ~14,500 |
| **Enterprise Support** | 3A Systems (OIP) | Red Hat (RHBK) | Okta/Auth0 | Okta | AWS | Ory Corp | Zitadel AG | Authentik Security |
| **CNCF Status** | None | Incubating | N/A | N/A | N/A | None | None | None |

**Key observations:**

- OpenAM's protocol breadth (SAML, OIDC, WS-Federation, 34+ auth modules) exceeds most modern alternatives, but its community size and cloud-native capabilities lag significantly.
- Keycloak is the closest functional equivalent in the open-source space, with a much larger community, CNCF governance, and modern Quarkus runtime.
- Authentik is the only platform with a visual flow editor for authentication workflows, a unique capability for complex customization.
- Zitadel's event-sourced architecture provides built-in auditability that other platforms achieve only through bolt-on logging.
- Ory's headless, API-first approach appeals to developer teams building custom UIs; it lacks an admin console.
- OpenAM is the only platform in this comparison that supports WS-Federation, relevant for Microsoft-centric legacy federations.

---

## Table 2: Directory Services

This table compares LDAP directories and identity stores -- the domain covered by OpenDJ (see prior OpenDJ analysis chapters).

| Feature | OpenDJ (OIP) | 389 DS | FreeIPA | Azure AD / Entra ID | AWS Directory Service | Lldap |
|---------|-------------|--------|---------|---------------------|----------------------|-------|
| **Version** | 5.0.3 | 3.x | 4.12.x | SaaS | SaaS (Managed AD) | 0.5.x |
| **License** | CDDL 1.0 | GPL 2.0+ | GPL 3.0 | Proprietary | Proprietary | GPL 3.0 |
| **Language** | Java | C, Rust (growing) | Python, C | N/A (SaaS) | N/A | Rust |
| **LDAPv3 Compliance** | Full | Full | Full (389 DS backend) | LDAPS proxy only | Full (Managed AD) | Partial (simplified) |
| **REST API** | Yes (REST2LDAP, RxJava 3) | Cockpit UI | IPA CLI/API | Microsoft Graph API | No REST API | GraphQL |
| **Multi-Master Replication** | Yes (CSN-based changelog) | Yes (multi-supplier) | Yes (389 DS based) | Microsoft-managed | Microsoft-managed | No |
| **Backend Options** | JE, SQL (JDBC), Cassandra, in-memory | LMDB (default), BDB | 389 DS backends | Cloud-managed | Managed AD | SQLite, PostgreSQL, MySQL |
| **Schema Extensibility** | Yes (OID-based) | Yes (online schema) | Yes (via 389 DS) | Limited (extensions) | Standard AD schema | Fixed schema |
| **Cloud-Native** | No (WAR/standalone) | Container support (v3) | Requires Linux servers | Yes (Azure) | Yes (AWS) | Yes (lightweight container) |
| **Managed Option** | No | No | Red Hat IdM (RHEL) | Yes (Entra ID) | Yes (AWS DS) | No |
| **Virtual Attributes** | Yes | Yes | Yes | No | Via AD features | No |
| **Password Policy** | Yes (draft-behera) | Yes (comprehensive) | Yes (integrated) | Yes (Entra policies) | Yes (AD Group Policy) | Basic |
| **DSML v2** | Yes (SOAP gateway) | No | No | No | No | No |
| **Reactive I/O** | Yes (RxJava 3, Netty) | No (threaded) | No | N/A | N/A | Async (Tokio) |
| **Entries per GB** | ~800k | Similar | Depends on 389 DS | N/A | N/A | Higher (lightweight) |
| **Use Case** | OIP identity store, embedded in OpenAM | RHEL/FreeIPA backend, enterprise LDAP | Linux identity management (AD for Linux) | Cloud workforce identity | AWS workload directory | Lightweight home/small LDAP |
| **Community** | Small (OIP ecosystem) | Red Hat-backed | Red Hat-backed | Microsoft | AWS | Growing Rust community |

**Key observations:**

- OpenDJ and 389 DS share Sun Directory Server ancestry but diverged in language: Java vs C/Rust. Both are production-grade for large-scale deployments.
- OpenDJ's REST-to-LDAP gateway with RxJava 3 reactive streams is architecturally advanced, but the small community limits its long-term viability compared to Red Hat-backed 389 DS.
- Managed cloud directories (Entra ID, AWS Directory Service) eliminate operational overhead but sacrifice schema extensibility and self-hosting flexibility.
- Lldap represents a modern, lightweight alternative for environments that need basic LDAP compatibility without the complexity of a full directory server.
- FreeIPA bundles 389 DS with Kerberos, DNS, and CA -- an integrated identity management solution for Linux environments that no other entry matches.

---

## Table 3: Identity Governance and Administration (IGA)

This table compares platforms that handle identity lifecycle management, provisioning, access certification, and compliance -- the domain covered by OpenIDM.

| Feature | OpenIDM (OIP) | SailPoint ISC | Saviynt EIC | MidPoint | SCIM-Native (IdP-direct) |
|---------|--------------|---------------|-------------|----------|--------------------------|
| **Version** | 7.0.2 | SaaS (Atlas) | SaaS | 4.8.x | N/A (protocol) |
| **License** | CDDL 1.0 | Proprietary | Proprietary | Apache 2.0 | N/A |
| **Language** | Java (OSGi/Felix) | Java (SaaS) | Java (SaaS) | Java (Spring) | N/A |
| **Provisioning** | Yes (via OpenICF connectors) | Yes (200+ connectors, VA) | Yes (500+ connectors) | Yes (built-in connectors) | Yes (SCIM push) |
| **Reconciliation** | Yes (3-phase: create/update/delete) | Yes (aggregation + correlation) | Yes (full recon) | Yes (reconciliation tasks) | No |
| **LiveSync (real-time)** | Yes (SyncOp polling) | Yes (event-driven + polling) | Yes (event-driven) | Yes (live sync) | Push-based (webhook/SCIM) |
| **Workflow Engine** | Activiti BPMN 2.0 | SailPoint workflows (visual) | Saviynt workflows (visual) | Midpoint workflows (XML) | No |
| **Access Certification** | No (basic reports) | Yes (AI-driven campaigns) | Yes (campaign management) | Yes (certification campaigns) | No |
| **Access Request** | No (manual) | Yes (self-service portal) | Yes (self-service portal) | Yes | No |
| **Separation of Duties** | No | Yes (SoD policy enforcement) | Yes (SoD, cross-app) | Yes (role-based SoD) | No |
| **Role Mining / RBAC** | Basic (managed roles) | Yes (AI-driven role discovery) | Yes (auto-role mining) | Yes (role management) | No |
| **AI/ML Capabilities** | No | Yes (Identity AI: outlier detection, recommendations) | Yes (identity analytics) | No | No |
| **Compliance Reports** | Basic (audit module) | Yes (SOX, HIPAA, GDPR, PCI) | Yes (Control Exchange) | Yes (built-in reports) | No |
| **Managed Objects** | Yes (JSON-LD, /managed/* routes) | Yes (identity cubes) | Yes (identity warehouse) | Yes (midpoint objects) | SCIM User/Group only |
| **Connector Framework** | OpenICF (SPI/API) | SaaS Connectivity + VA | Saviynt connectors | ConnId (OpenICF fork) | SCIM 2.0 (RFC 7643) |
| **Deployment Model** | Self-hosted (OSGi) | SaaS + Virtual Appliance | SaaS | Self-hosted | N/A |
| **Pricing** | Free (OSS) | Enterprise subscription ($$$$) | Enterprise subscription ($$$) | Free (OSS) | Free (built into IdP) |
| **Target Market** | OIP deployers, self-hosted | Large enterprise (1,000+ users) | Large enterprise | Mid-market, EU government | Any (when SCIM suffices) |

**Key observations:**

- OpenIDM provides core provisioning and reconciliation but lacks the governance features (access certifications, SoD, role mining, AI-driven reviews) that define the modern IGA market.
- SailPoint and Saviynt represent the commercial IGA apex: 200-500+ connectors, AI-driven governance, compliance automation. Their pricing reflects this ($100k-1M+/year for large deployments).
- MidPoint (Evolveum) is the closest open-source IGA alternative to OpenIDM, with broader governance features and an active European community. Notably, MidPoint uses ConnId, a fork of the OpenICF connector framework (see [Chapter 11: OpenICF Analysis](11-openicf-analysis.md)).
- SCIM-native provisioning (using the identity provider's built-in SCIM client) eliminates the need for a separate IGA platform when the requirement is limited to user/group provisioning without governance workflows.
- OpenIDM's OSGi architecture (Apache Felix) is unusual in the 2025 landscape; modern alternatives favor Spring Boot, Quarkus, or Go.

---

## Table 4: API Gateway / Identity Gateway

This table compares platforms used for API security, traffic management, and identity-aware request proxying -- the domain covered by OpenIG (see [Chapter 10: OpenIG Analysis](10-openig-analysis.md)).

| Feature | OpenIG (OIP) | Kong (OSS) | Envoy + Istio | Traefik | AWS API GW | Apache APISIX |
|---------|-------------|------------|---------------|---------|------------|---------------|
| **Version** | 6.0.2 | 3.x | Envoy 1.31 / Istio 1.23 | 3.x | SaaS | 3.x |
| **License** | CDDL 1.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 | Proprietary | Apache 2.0 |
| **Language** | Java | C (Nginx) + Lua + Go | C++ (Envoy), Go (Istio) | Go | N/A | C (Nginx) + Lua |
| **Deployment** | WAR (servlet container) | Standalone, K8s, Docker | Sidecar, ambient, gateway | Standalone, K8s, Docker | SaaS | Standalone, K8s, Docker |
| **HTTP Protocol** | HTTP/1.1 (servlet-dependent) | HTTP/1.1, HTTP/2, gRPC | HTTP/1.1, HTTP/2, gRPC, TCP | HTTP/1.1, HTTP/2, gRPC | HTTP, WebSocket | HTTP/1.1, HTTP/2, gRPC |
| **Auth - OIDC** | Yes (OAuth2ResourceServerFilter) | Yes (OIDC plugin) | Yes (ext_authz to OPA/custom) | ForwardAuth to external | Cognito, Lambda authorizer | Yes (OIDC plugin) |
| **Auth - SAML** | Yes (SamlFederationFilter) | No (custom plugin needed) | No | No | No | No |
| **Auth - JWT Validation** | Yes | Yes | Yes (JWT filter) | No (ForwardAuth) | Yes | Yes |
| **Credential Replay** | Yes (native, unique) | No | No | No | No | No |
| **Rate Limiting** | Yes (RateLimitFilter, ThrottlingFilter) | Yes (advanced: sliding window, cluster) | Yes (Envoy rate limit service) | Yes (middleware) | Yes (per-stage, per-key) | Yes (advanced) |
| **Observability** | Basic (CaptureFilter, MetricsFilter) | Prometheus, OTel, Datadog, Zipkin | Built-in (tracing, metrics, access logs) | Prometheus, OTel, Datadog | CloudWatch | Prometheus, SkyWalking, Zipkin |
| **Plugin/Filter System** | 50+ Java filters + Groovy | Lua, Go, Python, JS plugins | Envoy filters (C++, Wasm, Lua) | Go middleware | Lambda functions, VTL | 80+ Lua plugins |
| **Service Discovery** | None (static routes) | DNS, Consul, K8s | K8s, Consul, DNS, xDS | Docker, K8s, Consul, etcd, Rancher | AWS service integration | Consul, Nacos, K8s, DNS |
| **Service Mesh** | No | Kong Mesh (Kuma/Envoy) | Istio (Envoy sidecars) | Traefik Mesh | App Mesh (Envoy) | APISIX Mesh |
| **Hot Reload** | Yes (route files) | Yes (Admin API, DB-backed) | Yes (xDS dynamic config) | Yes (auto-discovery) | Yes (API deployment) | Yes (etcd-backed) |
| **Kubernetes** | Manual containerization | Ingress Controller, Helm, Operator | Istio Operator, Helm | Ingress Controller, CRDs, Helm | N/A | Ingress Controller, Helm |
| **Community (GitHub Stars)** | ~200 | ~40,000 | ~25,000 (Envoy), ~36,000 (Istio) | ~52,000 | N/A | ~14,500 |
| **Expression Language** | Yes (built-in EL) | No (Lua scripting) | No (config-based) | No (labels/annotations) | VTL templates | No (Lua scripting) |

**Key observations:**

- OpenIG is the only gateway in this comparison with native credential replay -- a capability relevant for legacy application integration (see [Chapter 10: OpenIG Analysis](10-openig-analysis.md), Section 7).
- OpenIG is also the only gateway with native SAML federation support, relevant for organizations still operating SAML-based identity infrastructure.
- Kong and APISIX dominate the general-purpose API gateway space on features, performance, and community.
- Envoy/Istio occupy a different architectural layer (service mesh / sidecar) but increasingly absorb gateway responsibilities at the edge.
- Traefik's auto-discovery model is unmatched for dynamic containerized environments.
- OpenIG's Expression Language provides declarative dynamic behavior that other gateways achieve through scripting (Lua) or external policy engines (OPA).

---

## Table 5: Connector / Integration Framework

This table compares approaches to identity integration and provisioning -- the domain covered by OpenICF (see [Chapter 11: OpenICF Analysis](11-openicf-analysis.md)).

| Feature | OpenICF | SCIM 2.0 (Direct) | Native Cloud Connectors | iPaaS (Workato, etc.) | CDC (Debezium + Kafka) |
|---------|---------|-------------------|------------------------|----------------------|------------------------|
| **Architecture** | Middleware framework (SPI/API) | Standard REST API | Vendor-managed SaaS | Low-code SaaS | Event streaming |
| **Protocol** | Custom (Protobuf RPC + Java SPI) | HTTP/JSON (RFC 7642-7644) | Vendor-proprietary | HTTP/webhooks/vendor APIs | Database log tailing |
| **Pre-built Connectors** | 9 (LDAP, DB, CSV, SSH, Groovy, XML, Kerberos, HTTP, AD) | N/A (target app implements) | 200-7,000+ (vendor-dependent) | 1,000+ | Per-database (MySQL, PostgreSQL, MongoDB, Oracle, SQL Server) |
| **Custom Development** | Java SPI (steep learning curve) | N/A (standard API) | Limited (vendor SDK) | Low-code visual builder | Kafka Connect transforms |
| **Real-time Sync** | Polling (SyncOp, seconds-minutes) | Push (IdP pushes to app) | Push (vendor-managed) | Event-driven (seconds) | Sub-second (log tailing) |
| **Reconciliation** | Yes (via OpenIDM, 3-phase) | No (push-only) | Vendor-dependent | Must be built as workflow | No (event stream, no full scan) |
| **Remote Execution** | Yes (Remote Connector Server) | N/A (direct HTTP) | N/A (SaaS) | N/A (SaaS) | Debezium Connect workers |
| **Schema** | ConnectorObject + ObjectClass (framework-specific) | User/Group (standardized, RFC 7643) | Vendor-defined | Application-specific | Database schema (raw) |
| **Target Types** | LDAP, DB, AD, SSH, CSV, XML, REST, custom | SaaS apps supporting SCIM | SaaS apps in vendor catalog | Any with API/webhook | Database-backed systems |
| **Legacy System Support** | Yes (primary strength) | No (requires SCIM implementation) | No (SaaS-focused) | Limited (API required) | Database-only |
| **Deployment** | Self-hosted (OpenIDM + connector server) | N/A (protocol) | SaaS (vendor-managed) | SaaS | Self-hosted (Kafka cluster) |
| **Cost** | Infrastructure only | Free (protocol) | Included in IdP subscription | $15k-200k+/year | Infrastructure (Kafka cluster) |
| **License** | CDDL 1.0 | IETF standard (free) | Proprietary | Proprietary | Apache 2.0 (Debezium) |
| **Best For** | Legacy systems, heterogeneous protocols | Modern SaaS provisioning | Cloud-first organizations | Rapid integration, non-technical teams | Database-sourced identity, real-time |

**Key observations:**

- SCIM 2.0 has eliminated the need for custom connectors in the modern SaaS tier. Any new SaaS application is expected to support SCIM.
- OpenICF's value concentrates on legacy system integration -- the systems that cannot implement SCIM endpoints.
- CDC (Debezium + Kafka) offers superior latency and source-system efficiency for database-backed identity data, but requires significant streaming infrastructure.
- Native cloud connectors (Okta OIN, Entra ID gallery) provide the broadest pre-built coverage, at the cost of vendor lock-in.
- MidPoint's ConnId framework is a direct fork of OpenICF, making it the closest architectural equivalent in the open-source space.

---

![IAM Decision Framework](../diagrams/14-iam-decision-tree.png)

## Decision Framework

The following decision trees provide structured guidance for selecting between the platforms compared above. Each tree starts with a primary decision criterion and branches toward a recommended option.

### Decision 1: Access Management Platform Selection

```
START: Do you require self-hosting?
  |
  +-- NO (cloud/SaaS acceptable)
  |     |
  |     +-- Budget > $50k/year for identity?
  |     |     |
  |     |     +-- YES --> Is your user base primarily employees (B2E)?
  |     |     |            +-- YES --> Okta Workforce Identity Cloud
  |     |     |            +-- NO (B2C/B2B) --> Auth0 (Customer Identity Cloud)
  |     |     |
  |     |     +-- NO (budget-constrained)
  |     |           +-- AWS-native environment? --> AWS Cognito
  |     |           +-- Azure-native? --> Microsoft Entra External ID
  |     |           +-- Multi-cloud or neutral? --> Ory Network or Zitadel Cloud
  |     |
  +-- YES (self-hosting required)
        |
        +-- Team has Java expertise AND existing OIP/ForgeRock deployment?
        |     +-- YES --> OpenAM (OIP) or Wren:AM (continue existing investment)
        |     +-- NO
        |           |
        |           +-- Need SAML IdP + OIDC + enterprise features?
        |           |     +-- YES --> Keycloak (largest community, CNCF, Red Hat backing)
        |           |     +-- NO
        |           |           |
        |           |           +-- API-first, headless, microservices preferred?
        |           |           |     +-- YES --> Ory Stack (Hydra + Kratos + Keto)
        |           |           |
        |           |           +-- Visual workflow customization needed?
        |           |           |     +-- YES --> Authentik (visual flow editor)
        |           |           |
        |           |           +-- B2B multi-tenancy with event-sourced audit?
        |           |           |     +-- YES --> Zitadel
        |           |           |
        |           |           +-- Developer-friendly, TypeScript team?
        |           |           |     +-- YES --> Logto
        |           |           |
        |           |           +-- Passkey-first, minimal footprint?
        |           |                 +-- YES --> Hanko
        |           |
        |           +-- Homelab / internal tools SSO with reverse proxy?
        |                 +-- YES --> Authelia (lightweight, proxy-first)
```

### Decision 2: Directory Service Selection

```
START: Do you need a full LDAPv3 directory?
  |
  +-- NO (cloud directory or simple user store sufficient)
  |     |
  |     +-- Microsoft ecosystem? --> Microsoft Entra ID
  |     +-- AWS ecosystem? --> AWS Directory Service (Managed AD or Simple AD)
  |     +-- Lightweight self-hosted? --> Lldap (Rust, minimal overhead)
  |     +-- PostgreSQL/SQL backend preferred? --> Identity stored in application DB
  |
  +-- YES (full LDAPv3 required)
        |
        +-- Linux identity management (Kerberos, DNS, CA, sudo)?
        |     +-- YES --> FreeIPA (integrated stack, Red Hat backing)
        |
        +-- Existing OIP/ForgeRock deployment?
        |     +-- YES --> OpenDJ (continues existing investment, REST2LDAP)
        |
        +-- Red Hat / RHEL environment?
        |     +-- YES --> 389 Directory Server (upstream of RHEL IdM)
        |
        +-- Greenfield, general-purpose enterprise LDAP?
              +-- 389 DS (active development, Rust modernization, Red Hat-backed)
              +-- OpenDJ (if Java ecosystem and REST API are priorities)
```

### Decision 3: Identity Governance Platform Selection

```
START: Do you need access certifications, SoD, or compliance automation?
  |
  +-- NO (provisioning and sync only)
  |     |
  |     +-- All targets support SCIM?
  |     |     +-- YES --> SCIM-native provisioning from your IdP (no IGA platform needed)
  |     |
  |     +-- Mix of SCIM and legacy targets?
  |     |     +-- Existing OIP deployment? --> OpenIDM + OpenICF
  |     |     +-- No existing investment? --> MidPoint (OSS, broader governance)
  |     |
  |     +-- Database-sourced identity requiring real-time sync?
  |           +-- YES --> CDC (Debezium + Kafka) for DB tier, SCIM for SaaS tier
  |
  +-- YES (full IGA: certifications, SoD, role mining, compliance)
        |
        +-- Budget > $200k/year?
        |     |
        |     +-- Born-cloud preferred, strong ERP governance?
        |     |     +-- YES --> Saviynt EIC
        |     |
        |     +-- Largest connector ecosystem, AI-driven reviews?
        |           +-- YES --> SailPoint Identity Security Cloud
        |
        +-- Budget-constrained or open-source preference?
              +-- YES --> MidPoint (Apache 2.0, European community, ConnId connectors)
              +-- OpenIDM (if already operating OIP stack)
```

### Decision 4: API / Identity Gateway Selection

```
START: Do you need credential replay for legacy applications?
  |
  +-- YES
  |     +-- OpenIG (unique capability, no modern equivalent)
  |     +-- Consider: OpenIG behind a modern API gateway (Kong/Traefik for
  |         observability and rate limiting, OpenIG for credential replay)
  |
  +-- NO (standard API gateway / proxy)
        |
        +-- Service mesh (east-west inter-service mTLS)?
        |     +-- YES --> Istio + Envoy (or Linkerd for simpler mesh)
        |
        +-- Kubernetes / Docker environment with auto-discovery?
        |     +-- YES --> Traefik (native K8s ingress, auto-discovery, Let's Encrypt)
        |
        +-- API management (developer portal, analytics, monetization)?
        |     +-- YES --> Kong Enterprise or AWS API Gateway
        |
        +-- High-performance API gateway with Apache governance?
        |     +-- YES --> Apache APISIX
        |
        +-- AWS-native, serverless scaling?
        |     +-- YES --> AWS API Gateway
        |
        +-- General-purpose API gateway, self-hosted?
              +-- Kong OSS (largest community, Lua/Go plugins)
              +-- Traefik (auto-discovery, Go middleware)
              +-- APISIX (Nginx-based performance, Apache Foundation)
```

### Decision 5: Integration / Connector Framework Selection

```
START: What are your integration targets?
  |
  +-- Primarily modern SaaS applications
  |     +-- Use SCIM 2.0 push from your IdP (no middleware needed)
  |     +-- If IdP lacks SCIM client: evaluate Okta, Entra ID, or Zitadel
  |
  +-- Mix of SaaS and databases
  |     +-- SaaS tier: SCIM push from IdP
  |     +-- Database tier: Need real-time? --> CDC (Debezium + Kafka)
  |     +-- Database tier: Batch/scheduled OK? --> OpenICF database connector or MidPoint
  |
  +-- Legacy systems (LDAP, AD, SSH, mainframe, proprietary)
  |     |
  |     +-- Existing OIP/OpenIDM deployment?
  |     |     +-- YES --> OpenICF (continue existing investment)
  |     |
  |     +-- No existing investment?
  |           +-- Budget for commercial IGA? --> SailPoint or Saviynt connectors
  |           +-- Open-source preference? --> MidPoint + ConnId (OpenICF fork)
  |           +-- Rapid prototyping? --> OpenICF Groovy connector or iPaaS (Workato)
  |
  +-- Primarily databases (HR system, ERP, custom apps)
  |     +-- Real-time required? --> CDC (Debezium + Kafka Connect)
  |     +-- Batch acceptable? --> OpenICF database connector or SCIM with custom adapter
  |
  +-- Non-technical team, low-code preferred
        +-- iPaaS (Workato, Tray.io, Mulesoft)
        +-- Note: iPaaS lacks reconciliation; supplement with IGA platform if needed
```

---

## Table 6: Privileged Access Management (PAM)

PAM products secure, monitor, and audit access to high-privilege accounts -- root/admin credentials, service accounts, database superuser roles, and cloud console access. This domain was not historically addressed by the OIP stack (OpenAM handles user authentication, not privileged session brokering). PAM is included here because modern IAM architectures increasingly treat privileged access as a distinct control plane layered on top of the identity foundation.

| Feature | CyberArk PAM | Delinea Secret Server | BeyondTrust Password Safe | HashiCorp Vault + Boundary |
|---------|-------------|----------------------|--------------------------|---------------------------|
| **License** | Proprietary | Proprietary | Proprietary | BSL 1.1 (OSS fork: OpenBao, MPL 2.0) |
| **Deployment** | On-prem; Privilege Cloud (SaaS) | On-prem; SaaS (Azure-hosted); Delinea Platform | On-prem (virtual/physical); Cloud (AWS, Azure) | Self-managed; HCP Vault Dedicated; HCP Vault Secrets (multi-tenant) |
| **Credential Vaulting** | Yes -- Vault Technology (AES-256, FIPS 140-2) | Yes -- centralized encrypted vault (AES-256) | Yes -- auto-discovery and onboarding | Yes -- secrets engine (dynamic + static) |
| **Dynamic Secrets** | Conjur (DevOps) + Credential Provider | Limited (rotation-based) | Limited (rotation-based) | Yes -- core strength; generates short-lived DB creds, cloud IAM, PKI certs |
| **Session Recording** | PSM: video + keystroke logging | Advanced Session Recording (RDP, SSH, PuTTY) | Live monitoring, recording, lock/terminate | Boundary Enterprise: session recording to object store |
| **JIT Access** | Time-limited with approval (Slack, Teams, ServiceNow) | JIT elevation, automated credential rotation | Auto-rotate, JIT credential checkout | Boundary injects single-use credentials; no standing access |
| **MFA Integration** | Adaptive MFA; integrates with external IdPs | MFA at secret checkout | MFA integrated | Delegates to OIDC/SAML IdP |
| **Endpoint Privilege Mgmt** | EPM for Windows/Mac | Privilege Manager (Windows/Mac) | EPM for Windows/Mac/Linux | No |
| **Cloud PAM** | Privilege Cloud; multi-cloud IaaS/SaaS | SaaS platform; Azure-hosted | AWS/Azure appliance deployment | Cloud-native (HCP); strong in IaC/cloud workloads |
| **Target Market** | Large enterprise, regulated industries | Mid-market to enterprise | Mid-market to enterprise | DevOps/platform engineering, cloud-native orgs |
| **OSS Alternative** | None direct | None direct | None direct | OpenBao (MPL 2.0 Vault fork) |

### PAM Decision Guidance

```
What are you protecting?
+-- Human admin/root access to servers/databases
|     +-- Regulated industry (finance, healthcare)? --> CyberArk (broadest compliance coverage)
|     +-- Mid-market, simpler requirements? --> Delinea or BeyondTrust
|     +-- Already CyberArk customer? --> Extend to Privilege Cloud for hybrid
|
+-- Machine/application secrets (API keys, DB creds, TLS certs)
|     +-- Cloud-native / Kubernetes? --> HashiCorp Vault (or OpenBao for OSS)
|     +-- Mixed environment? --> Vault + CyberArk Conjur (both have strengths)
|
+-- Both human + machine
      +-- Single vendor preference? --> CyberArk (Conjur + PAM) or Delinea Platform
      +-- Best-of-breed? --> CyberArk/Delinea for human PAM + Vault for secrets
```

---

## Tier 2 Access Management: Emerging OSS Alternatives

The Table 1 comparison covers established access management platforms. Two newer open-source projects merit tracking as emerging alternatives, particularly for organizations seeking modern developer experience without the legacy weight of OpenAM or the Java dependency of Keycloak.

| Attribute | Casdoor | SuperTokens |
|-----------|---------|-------------|
| **Language** | Go (backend), React (frontend) | Java (core), Node.js (middleware), React (prebuilt UI) |
| **License** | Apache 2.0 | Apache 2.0 |
| **GitHub Stars** | ~13k | ~15k |
| **OIDC/OAuth 2.0** | Full OIDC Provider and Consumer | OAuth 2.0 / OIDC provider |
| **SAML 2.0** | Yes -- IdP and SP | No (OIDC-first design) |
| **Social Login** | 50+ providers | Major providers via recipes |
| **Deployment** | Docker, K8s, binary; Casdoor SaaS | Docker, binary; supertokens.com (managed) |
| **Key Differentiator** | UI-first; Casbin RBAC/ABAC integration; supports CAS, LDAP, SCIM, RADIUS, Kerberos, WebAuthn | Developer-first drop-in; prebuilt UI components; session mgmt as first-class; no user limits self-hosted |
| **Maturity** | Part of Casbin ecosystem; growing adoption in APAC | Auth0/Firebase replacement positioning; strong developer community |

Neither yet matches Keycloak's feature breadth or enterprise adoption, but both demonstrate the market trend toward lightweight, API-first, Go/Node-based identity platforms -- a trajectory relevant when evaluating whether to invest in modernizing an OIP deployment versus migrating to a newer platform.

---

## Table 7: Identity Threat Detection and Response (ITDR)

ITDR is an emerging security category (Gartner coined the term in 2022) focused on detecting identity-based attacks -- credential stuffing, lateral movement via stolen tokens, MFA fatigue attacks, Kerberos ticket manipulation, and identity store compromise. ITDR products complement the IAM infrastructure analyzed in earlier chapters by adding a detection-and-response layer on top of the authentication and authorization foundation.

| Feature | CrowdStrike Falcon Identity Protection | Silverfort | Microsoft Entra ID Protection |
|---------|---------------------------------------|-----------|-------------------------------|
| **Deployment** | Cloud-native (Falcon agent + cloud analytics) | Agentless, proxyless -- inline with AD/IdPs via API | Cloud-native (Entra / Defender XDR suite) |
| **Credential Stuffing Detection** | Cross-domain telemetry; correlates endpoint + identity signals | Protocol anomaly inspection; baseline deviation detection | ML-based risk from 100T+ daily signals; leaked credential detection |
| **Lateral Movement Detection** | Maps identity attack paths; blocks privilege escalation | Monitors every auth request in hybrid environments; ticket misuse, credential replay | Identity-centric correlation across accounts; Defender for Identity on-prem |
| **MFA Fatigue Attack Detection** | Phishing-resistant FIDO2 MFA; MFA bypass detection | Inline MFA challenge/block before auth completes; anomalous MFA patterns | Risk-based Conditional Access; token theft detection |
| **Identity Risk Scoring** | AI-driven per-user risk scoring | Real-time risk per authentication attempt | Per-user risk levels (low/medium/high); feeds Conditional Access |
| **Integration Points** | Falcon XDR, SIEM, SOAR; AD + Entra ID + Okta | AD, Entra ID, Okta, ADFS, RADIUS; SIEM/SOAR/XDR via API | Defender XDR, Sentinel SIEM, Conditional Access; Okta + third-party IdPs |
| **Unique Strength** | Unified endpoint + identity platform; inline AD/Entra prevention | Only solution operating inline within the authentication flow; no agents/proxies; fastest time-to-value | Native Microsoft ecosystem integration; massive signal corpus; included in E5 license |
| **OIP Relevance** | Can protect OpenAM-fronted AD environments | Can wrap OpenAM's AD authentication with risk-based MFA without modifying OpenAM | Limited (requires Entra ID as primary IdP) |

### ITDR Selection Guidance

ITDR products add the most value when deployed alongside, not instead of, a well-configured IAM stack. For organizations running the OIP suite:

- **Silverfort** has the lowest integration friction: it intercepts AD authentication requests without requiring changes to OpenAM or OpenDJ, making it the most practical ITDR overlay for legacy IAM deployments.
- **CrowdStrike Falcon** provides the broadest signal correlation if the organization already uses Falcon for endpoint protection.
- **Microsoft Entra ID Protection** is cost-effective for Microsoft-centric environments (E5 license) but assumes Entra ID as the primary IdP.

---

![SPIFFE/SPIRE Workload Identity Flow](../diagrams/12-spiffe-spire.png)

## Table 8: Workload Identity (SPIFFE/SPIRE)

Workload identity addresses how services authenticate to each other -- a problem orthogonal to human identity (OpenAM's domain) but increasingly critical in microservices and zero-trust architectures. SPIFFE (Secure Production Identity Framework for Everyone) is a CNCF-graduated standard; SPIRE is its reference implementation.

| Dimension | SPIFFE/SPIRE | Traditional Service Accounts / Static mTLS |
|-----------|-------------|---------------------------------------------|
| **Credential Lifetime** | Short-lived (minutes); auto-rotated | Long-lived; manual rotation |
| **Identity Format** | SVID: X.509 cert or JWT with SPIFFE ID URI (`spiffe://domain/service-a`) | Platform-specific (K8s ServiceAccount, AWS IAM Role, GCP SA) |
| **Identity Granularity** | Per-workload, per-node attestation | Per-service-account (often shared across instances) |
| **Secret Distribution** | No static secrets; identity derived from platform attestation | Requires secrets distribution (K8s secrets, env vars, mounted files) |
| **Cross-Platform** | Single model across cloud, K8s, VMs, bare-metal | Platform-specific approaches |
| **Certificate Management** | Fully automated issuance + rotation via SPIRE | Manual or requires separate CA (cert-manager, Vault PKI) |
| **Zero Trust Alignment** | Strong -- identity verified at every hop | Weak -- often relies on network perimeter or long-lived tokens |
| **Adoption** | GitHub, Netflix, Pinterest, Uber, Square, TransferWise; CNCF graduated (2022) | Universal but increasingly seen as legacy for service-to-service auth |
| **OIP Relevance** | Complements OpenAM: SPIFFE handles east-west (service-to-service), OpenAM handles north-south (user-to-app) | OpenAM's OAuth 2.0 client credentials grant is the traditional approach |

### Key Concepts

- **SPIFFE ID**: URI-format identity (`spiffe://trust-domain/workload`) assigned to each workload
- **SVID (SPIFFE Verifiable Identity Document)**: Short-lived X.509 certificate or JWT proving workload identity
- **Node Attestation**: SPIRE Server verifies node identity via platform attestors (AWS IID, GCP, K8s, bare-metal TPM)
- **Workload Attestation**: SPIRE Agent verifies workload process via kernel metadata, K8s pod info, Docker labels

### Workload Identity Decision Guidance

```
How do your services authenticate to each other?
+-- Kubernetes-only
|     +-- Simple setup? --> K8s ServiceAccount tokens + network policies
|     +-- Zero trust / cross-cluster? --> SPIFFE/SPIRE with K8s attestor
|
+-- Multi-platform (K8s + VMs + cloud functions)
|     +-- Need unified identity model? --> SPIFFE/SPIRE (purpose-built)
|     +-- Already use HashiCorp Vault? --> Vault Agent + PKI engine
|
+-- Legacy / monolithic
      +-- OpenAM OAuth 2.0 client credentials grant (sufficient for coarse service auth)
      +-- Plan SPIFFE adoption for future microservices decomposition
```

---

## Cross-Cutting Considerations

Beyond the per-domain decision trees, several factors apply across all five domains:

### Compliance and Data Residency

Organizations subject to GDPR, SOX, HIPAA, NIS2, or sector-specific regulations must consider:

- **Data residency**: SaaS platforms may store identity data in jurisdictions outside the organization's control. Self-hosted options (OpenAM, OpenDJ, OpenIDM, Keycloak, MidPoint) guarantee data stays in the organization's infrastructure.
- **Audit trail**: Event-sourced architectures (Zitadel) provide immutable audit logs by design. Others require explicit audit configuration.
- **Compliance reports**: Commercial IGA platforms (SailPoint, Saviynt) include pre-built compliance report templates. Open-source alternatives require custom report development.

### Team Size and Expertise

| Team Profile | Recommended Approach |
|-------------|---------------------|
| 1-3 engineers, full-stack | Managed SaaS (Auth0, Okta, Cognito) or lightweight OSS (Zitadel, Logto) |
| 3-10 engineers, Java expertise | Keycloak or OpenAM (if existing deployment) |
| 3-10 engineers, Go/TS expertise | Ory Stack, Zitadel, or Logto |
| 10+ engineers, dedicated identity team | Any option; commercial IGA (SailPoint, Saviynt) for governance |
| Platform engineering team | Self-hosted Keycloak with Kubernetes Operator, or Ory Stack as microservices |

### Migration Complexity

Organizations migrating from an existing OIP deployment face varying levels of effort:

| Migration Path | Effort | Key Challenge |
|---------------|--------|---------------|
| OpenAM --> Keycloak | High | Realm configuration, auth module migration, SAML/OIDC metadata |
| OpenAM --> Auth0/Okta | High | User migration, auth chain reconstruction in Actions/policies |
| OpenDJ --> 389 DS | Medium | Data export/import (LDIF), schema mapping, replication reconfiguration |
| OpenDJ --> Entra ID | High | LDAP-to-Graph API migration, schema translation, application refactoring |
| OpenIDM --> SailPoint/Saviynt | High | Mapping translation, connector replacement, workflow redesign |
| OpenIG --> Kong/Traefik | Medium-High | Filter logic rewrite as plugins, credential replay replacement |
| OpenICF --> SCIM | Low (if targets support SCIM) | Connector retirement, SCIM endpoint verification |

### Total Cost of Ownership

| Factor | Self-Hosted OSS (OIP, Keycloak) | Commercial SaaS (Okta, Auth0) | Managed OSS (Ory Network, Zitadel Cloud) |
|--------|-------------------------------|------------------------------|------------------------------------------|
| License cost | Free | $2-50/user/month | Free tier + usage-based |
| Infrastructure | Own servers/VMs/containers | None | None |
| Operations | Own team (patching, upgrades, monitoring) | Vendor-managed | Vendor-managed |
| Customization | Unlimited (source available) | Actions/plugins within platform limits | API-first extensibility |
| Vendor lock-in | None (OSS) | High (proprietary) | Low-Medium (OSS core, managed control plane) |
| Time to production | Weeks-months | Days-weeks | Days-weeks |
| Scaling burden | Own team | Automatic | Automatic |

The decision between self-hosted and SaaS is rarely purely technical. It depends on the organization's operational maturity, tolerance for vendor dependency, regulatory constraints, and the relative cost of engineering time versus subscription fees.
