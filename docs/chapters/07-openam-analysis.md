# Chapter 7: OpenAM Analysis

OpenAM is the central access management component of the Open Identity Platform suite, providing single sign-on, multi-factor authentication, OAuth 2.0/OpenID Connect token issuance, SAML 2.0 federation, and XACML 3.0 policy evaluation within a single deployable WAR artifact. Descended from Sun Microsystems' OpenSSO via ForgeRock's stewardship (see Chapter 1), it carries one of the deepest feature sets of any open-source IAM system -- 34+ pluggable authentication modules, a complete OAuth 2.0 authorization server, and an entitlement engine capable of fine-grained attribute-based access control. That breadth is both its greatest asset and its heaviest burden: the codebase spans roughly 51 Maven modules, carries legacy UI code from the Sun era, and demands significant operational expertise to deploy and maintain. This chapter examines OpenAM's architecture in detail, evaluates its strengths and weaknesses, and positions it against modern alternatives ranging from Keycloak to the Ory stack to commercial SaaS platforms.

---

## 1. What OpenAM Does

OpenAM serves as a centralized authentication and authorization hub for web and API applications. Its core capabilities include:

- **Single sign-on (SSO)** across web applications using cookie-based session management, with cross-domain SSO via the Core Token Service (CTS).
- **Authentication** through 34+ pluggable modules organized into configurable chains, supporting LDAP, Kerberos, OAuth 2.0, OIDC, SAML 2.0, WebAuthn/FIDO2, HOTP/TOTP, push notifications, device fingerprinting, and scripted custom logic.
- **Authorization** via an XACML 3.0-compliant policy engine implementing PEP/PDP architecture with resource pattern matching, subject/environment conditions, and deny-overrides combining.
- **Federation** as both SAML 2.0 Identity Provider and Service Provider, with WS-Federation support and identity brokering for social login.
- **OAuth 2.0 / OpenID Connect** authorization server with support for authorization code, client credentials, password, JWT bearer, and device code grant types, plus token introspection, revocation, and dynamic client registration.

These capabilities make OpenAM suitable for enterprises requiring a self-hosted identity hub that can federate with partners, protect APIs, and authenticate users through multiple factors -- all without vendor lock-in to a commercial SaaS platform.

---

## 2. Architecture Overview

### Authentication Chain Model

OpenAM's authentication system is built on the Java Authentication and Authorization Service (JAAS) framework, implemented as a Chain of Responsibility pattern where multiple authentication modules execute in sequence according to configurable control flags.

The core classes that implement this model reside in `OpenAM/openam-core/src/main/java/com/sun/identity/authentication/`:

- **`AuthContext.java`** -- The public client-facing API. Applications call `AuthContext.login()` to initiate authentication and handle callbacks (username prompts, password prompts, OTP challenges) in a conversational loop.
- **`AMLoginContext.java`** -- The orchestration layer. It instantiates the JAAS `LoginContext`, wires up the configured chain of `AMLoginModule` instances, and manages pre/post-authentication processing hooks.
- **`AMAuthenticationManager.java`** -- The service locator. It loads authentication chain configurations and module instances from the LDAP-backed service schema, resolving module class names to concrete implementations at runtime.
- **`AMLoginModule.java`** (in the `spi/` package) -- The base class all authentication modules extend. It implements the JAAS `LoginModule` contract (`init()`, `login()`, `commit()`, `abort()`, `logout()`) and communicates with clients via `Callback` objects.
- **`LoginState.java`** -- Maintains stateful context across multi-step authentication flows, tracking the current module, failed attempts, and callback history.

Each module in a chain carries a JAAS control flag -- REQUIRED, REQUISITE, SUFFICIENT, or OPTIONAL -- that determines how its success or failure affects the overall chain outcome. This design enables composable multi-factor flows: a chain might require LDAP password verification (REQUIRED), then offer TOTP as a second factor (REQUIRED), with a persistent cookie check as a bypass (SUFFICIENT).

The data flow proceeds as:

```
Client -> AuthContext.login()
  -> AMLoginContext -> JAAS LoginContext.login()
    -> Chain of AMLoginModule instances
      -> DSAMECallbackHandler.handle(Callback[])
      -> Module validates credentials -> Subject population
    -> Final Subject with Principals + credentials
  -> SessionService.createSession()
```

New authentication modules are added by extending `AMLoginModule` and providing an XML service schema definition. Each module lives in its own Maven submodule under `OpenAM/openam-authentication/` -- for example, `openam-auth-ldap/` contains `LDAP.java` (the module implementation) and `amAuthLDAP.xml` (the service schema). This structure enables selective inclusion at build time.

### Session Management

Session management is handled by the `SessionService` class at `OpenAM/openam-core/src/main/java/com/iplanet/dpro/session/service/SessionService.java`. After successful authentication, the service creates an `InternalSession` object containing the session ID, creation timestamp, expiration, idle timeout, and arbitrary string properties. The session ID is encrypted into an `SSOToken` that travels to the client as a cookie or header value.

Session storage is pluggable through backend adapters:

| Backend | Module | Use Case |
|---------|--------|----------|
| JPA (default) | `openam-core/` | Single-node or small cluster |
| Cassandra | `openam-cassandra/` | Horizontally scalable, multi-datacenter HA |
| Redis | OIP extensions | High-throughput caching layer |
| Custom | `SessionStore` interface | Organization-specific backends |

The Cassandra backend (`OpenAM/openam-cassandra/`) was added by the OIP community to address the CE-era limitation of single-node session stores. It supports multi-master replication across data centers with TTL-based token expiration, enabling the kind of horizontal scaling that production deployments require.

Session lifecycle follows a well-defined sequence: creation after authentication success, token issuance with encrypted session ID, storage in the chosen backend, replication across cluster nodes, TTL-based or idle-timeout expiration, blacklist entry on logout, and final destruction. Session constraints (enforced by `SessionConstraint.java`) limit concurrent sessions per user, preventing session abuse.

### Policy Engine (XACML 3.0)

Authorization decisions are made by the entitlement engine in `OpenAM/openam-entitlements/`. The engine implements a PEP/PDP architecture where Policy Enforcement Points request decisions from the Policy Decision Point:

```
Client Request
  -> PolicyEvaluator.evaluate(resource, action, subject, environment)
    -> Load applicable policies from PolicyStore
      -> Evaluate conditions (subject, resource, action, environment)
        -> Short-circuit on DENY (deny-overrides combining)
        -> Aggregate permits
      -> Return decision + obligations
    -> Cache result (TTL-based invalidation)
```

Policies are structured as combinations of resource patterns (URI wildcards, regex), subjects (users, groups), actions (HTTP methods), environment conditions (IP range, time window, device type), and effects (Allow/Deny). Policies are stored in the OpenDJ LDAP backend as LDIF entries, making them subject to the same replication and backup mechanisms as identity data.

Extension points include custom subject matchers (extending `SubjectImplementation`), custom resource comparators (extending `ResourceMatch`), and custom environment evaluators (extending `EnvironmentImplementation`).

### OAuth 2.0 / OIDC Provider

The OAuth 2.0 implementation resides in `OpenAM/openam-oauth2/src/main/java/org/forgerock/oauth2/core/` with approximately 80 classes. Key interfaces follow the Strategy pattern for extensibility:

| Class | Role |
|-------|------|
| `AuthorizationService` | Handles `/authorize` endpoint |
| `AccessTokenService` | Handles `/token` endpoint |
| `ResponseTypeHandler` | SPI for code, token, id_token response types |
| `GrantTypeHandler` | SPI for authorization_code, client_credentials, password, jwt-bearer, device_code |
| `TokenStore` | SPI for pluggable token persistence (CTS-backed default) |
| `ScopeValidator` | SPI for custom scope validation logic |

The authorization code flow proceeds through request validation, resource owner authentication (delegating to the authentication chain), consent verification, authorization code generation and storage, and finally token exchange. OIDC extensions add ID Token (JWT) issuance alongside access tokens, a UserInfo endpoint for profile claims, and a discovery endpoint at `/.well-known/openid-configuration`.

### Plugin SPI

OpenAM's extensibility is built on a Service Locator + Factory pattern. Authentication modules are discovered via classpath scanning for `AMLoginModule` implementations, with XML/LDAP service definitions loaded at startup. Module properties are mapped from LDAP distinguished names to object attributes, and constructor instantiation occurs with configuration parameters injected from the service schema.

Post-authentication processing is handled through the `AMPostAuthProcessInterface`, which enables custom logic to execute after successful authentication -- session attribute injection, audit logging, external system notification, or conditional step-up requirements.

### Authentication Module Inventory

The complete module inventory spans seven categories, each living in its own Maven submodule under `OpenAM/openam-authentication/`:

| Category | Modules | Description |
|----------|---------|-------------|
| Directory/LDAP | `openam-auth-ldap`, `openam-auth-ad`, `openam-auth-nt`, `openam-auth-ntlmv2`, `openam-auth-membership` | Standard directory authentication including Active Directory, LDAP bind, NTLM, and membership validation |
| Multi-factor | `openam-auth-hotp`, `openam-auth-oath`, `openam-auth-fr-oath`, `openam-auth-push`, `openam-auth-webauthn` | HOTP, TOTP (OATH), ForgeRock OATH variant, mobile push approval, FIDO2/WebAuthn passkeys |
| Federation/Social | `openam-auth-oauth2`, `openam-auth-oidc`, `openam-auth-saml2` | OAuth 2.0 social login, OpenID Connect authentication, SAML 2.0 as an authentication module |
| External | `openam-auth-radius`, `openam-auth-msisdn`, `openam-auth-securid`, `openam-auth-cert`, `openam-auth-recaptcha` | RADIUS server, mobile subscriber MSISDN, RSA SecurID, X.509 client certificates, Google reCAPTCHA |
| Persistence | `openam-auth-persistentcookie`, `openam-auth-windowsdesktopsso` | Persistent cookie-based re-authentication, Windows Desktop SSO via Kerberos |
| Scripting | `openam-auth-scripted`, `openam-auth-amster` | Groovy-scripted custom auth logic, Amster-based admin provisioning auth |
| Advanced | `openam-auth-device-id`, `openam-auth-qr`, `openam-auth-application`, `openam-auth-adaptive`, `openam-auth-anonymous`, `openam-auth-httpbasic`, `openam-auth-jdbc` | Device fingerprinting, QR code, application tokens, risk-adaptive scoring, anonymous access, HTTP Basic, JDBC database auth |

The evolution across forks is significant. ForgeRock CE 11.0.3 shipped 20 modules. OIP 16.0.5 added 11 (OIDC, SAML2, WebAuthn, QR, push, device-id, scripted, recaptcha, ntlmv2, fr-oath, amster). Wren:AM 16.0.0-M1 adopted a selective subset: it kept 27 modules, dropped 4 (WebAuthn, QR, recaptcha, ntlmv2), and added its own Duo Security MFA integration (`wrenam-auth-duo`). The Wren strategy favors quality over breadth -- fewer modules to maintain, with Duo covering enterprise MFA requirements that the dropped modules partially served.

### Fork Divergence in Dependencies

The three forks diverge significantly in their technology stacks, as detailed in Chapter 5. The most architecturally consequential divergence is Guice dependency injection:

- **ForgeRock CE 11.0.3:** Guice 3.0
- **OIP 16.0.5:** Guice 7.0.0 (modern DI, breaking changes vs 3.0)
- **Wren:AM 16.0.0-M1:** Guice 3.0, wrapped in `wrensec-guice-core` and `wrensec-guice-servlet`

OIP's upgrade to Guice 7.0.0 modernizes the DI container but breaks backward compatibility with extensions compiled against Guice 3.0. Wren deliberately retained Guice 3.0 to preserve enterprise extension compatibility, wrapping it in namespace-isolated artifacts. This divergence means that custom authentication modules, post-authentication processors, and policy plugins are not binary-compatible between OIP and Wren builds -- a consideration for organizations maintaining custom extensions.

Other notable dependency differences include Jackson (OIP conservative at 2.3.x, Wren modern at 2.15.2), SLF4J (OIP on 1.7.x, Wren on 2.0.17), Restlet (OIP 2.4.4, Wren 2.6.0), and Jakarta EE level (OIP partial jakarta.servlet 4.0+, Wren full jakarta.servlet 5.0.0). Wren's aggressive dependency modernization, combined with its conservative Guice strategy, reflects a deliberate architectural choice: update everything except the plugin contract surface.

---

## 3. Strengths

**Breadth of authentication modules.** With 34+ authentication modules spanning LDAP, Kerberos, OAuth 2.0, OIDC, SAML 2.0, WebAuthn, HOTP/TOTP, push notifications, device fingerprinting, QR codes, scripted logic, and adaptive risk scoring, OpenAM covers more authentication scenarios in a single platform than any other open-source IAM system. The OIP fork (16.0.5) added 11 modules beyond the CE baseline, including WebAuthn/FIDO2, OIDC as an authentication method, SAML 2.0 as an authentication chain module, and push notification approval (see Chapter 5 for fork evolution details).

**Protocol convergence.** OpenAM combines SAML 2.0 IdP/SP, OAuth 2.0 authorization server, OIDC provider, UMA 2.0, and WS-Federation in one deployment. Organizations operating in heterogeneous federation environments -- where partners require SAML while internal APIs use OIDC -- can serve both from a single system without deploying separate products.

**XACML 3.0 policy engine.** The entitlement engine supports fine-grained, attribute-based access control with resource pattern matching, environment conditions, and deny-overrides combining. Few open-source alternatives offer XACML-level policy expressiveness; most limit authorization to RBAC or simple scope checks.

**Cassandra-backed high availability.** The `openam-cassandra` module enables horizontally scalable session and token storage across data centers, eliminating the single-node session bottleneck that plagued the CE era. Combined with OpenDJ's multi-master replication for configuration and identity data, OpenAM can achieve active-active deployments across geographies.

**Mature, battle-tested codebase.** The codebase traces its lineage to Sun's OpenSSO (2005), through ForgeRock's development (2010-2016), to the OIP and Wren forks. Twenty years of production deployments across government agencies, universities, telecommunications providers, and financial institutions have exercised edge cases that newer platforms have not yet encountered. The commercial descendant (now Ping Identity's PingOne Advanced Identity Cloud) validates the architectural foundations.

**Comprehensive audit infrastructure.** The OIP fork added a dedicated audit module (`OpenAM/openam-audit/`) with four submodules: audit context capture, event streaming engine, policy configuration, and REST API for trail queries. This infrastructure supports SOX, GDPR, and HIPAA compliance requirements with structured logging, correlation IDs, and queryable audit history.

**Scripting engine for custom logic.** The `openam-scripting` module enables Groovy-based custom authentication policies, token transformations, and authorization decisions without requiring a full rebuild -- critical for organizations that need to adapt authentication flows to business-specific requirements.

---

## 4. Weaknesses

**Jato legacy UI.** OpenAM's administrative console is built on the Jato framework, a Sun-era JSP rendering library that predates modern web frameworks by nearly two decades. The Jato framework is also the source of CVE-2021-35464 (CVSS 9.8), a pre-authentication remote code execution vulnerability exploited in the wild (see Section 4.1 below). The UI is difficult to extend, provides a poor user experience by modern standards, and represents a significant technical debt burden.

**Monolithic WAR deployment.** Despite internal modularity (51 Maven submodules), OpenAM deploys as a single WAR file. Scaling requires scaling the entire application; a defect in the SAML engine can take down the OAuth 2.0 provider; upgrading one capability demands redeploying the whole system. The memory footprint grows with every feature, whether or not a given deployment uses it. This is the architectural pattern that modern IAM platforms (Ory, Zitadel, even Keycloak on Quarkus) have deliberately moved away from (see Chapter 12).

**Configuration complexity.** OpenAM stores its configuration in an embedded or external OpenDJ instance as LDAP entries. Configuration changes involve manipulating LDAP attributes through the Jato admin console, the `ssoadm` command-line tool, or the REST API. There is no declarative configuration-as-code model comparable to Keycloak's realm export/import, Ory's YAML configuration, or Zitadel's Terraform provider. This makes infrastructure-as-code workflows, GitOps, and reproducible deployments significantly harder to achieve.

**Steep learning curve.** The combination of JAAS-based authentication chains, LDAP-backed configuration, realm/sub-realm hierarchy, agent profiles, policy definitions, and OAuth 2.0 client configuration creates a steep learning curve. Documentation for the OIP fork is sparse compared to Keycloak's official guides or Auth0's developer tutorials. New operators must often consult the ForgeRock-era documentation (e.g., the OpenAM 12 Reference PDF in this workspace) for context that the OIP community documentation omits.

**CVE history.** OpenAM's most serious vulnerability, CVE-2021-35464 (CVSS 9.8), enabled pre-authentication remote code execution via Java deserialization in the Jato framework's `/ccversion/*` endpoint. CISA issued advisory AA21-193A, and a Metasploit module exists. The OIP fork applied a workaround (PR #372), and Wren:AM patched it (PR #123), but the frozen ForgeRock CE 11.0.3 remains permanently unpatched. CVE-2021-29156 (CVSS 7.5) demonstrated LDAP injection via the Webfinger protocol, enabling character-by-character extraction of password hashes from the backing directory. Beyond these OpenAM-specific vulnerabilities, the deep Java dependency tree has accumulated CVEs in Commons FileUpload, Lodash, SnakeYAML, Apache Commons Text, Netty, and RequireJS (see Chapter 6 for the complete CVE history).

**Small maintainer community.** The OIP fork is maintained primarily by 3A Systems, LLC, with a small contributor base compared to Keycloak's ~1,100 contributors backed by Red Hat's engineering resources. Wren Security (Orchitech Solutions, Czech Republic) maintains an even smaller team. Critical vulnerability patches can lag weeks to months behind disclosure, and the pace of feature development cannot match commercially backed alternatives.

**No stateless session option.** Modern IAM platforms increasingly support stateless JWT-based sessions (or sender-constrained tokens via DPoP/mTLS) that eliminate server-side session storage entirely (see Chapter 12). OpenAM's session model is fundamentally server-side: sessions are stored in CTS (backed by JPA, Cassandra, or Redis), and the SSOToken is an opaque reference, not a self-contained JWT. While the `StatelessSessionActivator` exists as an interface in the codebase, stateless sessions are not the production-recommended path, and most deployments require the full CTS infrastructure. This architectural decision was appropriate in 2005 but adds operational burden in 2025 where stateless session models reduce infrastructure requirements.

**Legacy CDDL license.** The Common Development and Distribution License 1.0, created by Sun Microsystems for OpenSolaris, is a weak copyleft license that is not GPL-compatible. While CDDL is OSI-approved, it is less familiar to developers and legal teams than Apache 2.0, MIT, or GPL. Keycloak (Apache 2.0), Ory (Apache 2.0), and Zitadel (Apache 2.0) all use licenses with broader compatibility and better-understood obligations. The CDDL license is not a practical barrier to adoption but adds a minor friction point during legal review.

---

## 5. Modern Alternatives Comparison

### 5.1 OpenAM vs Keycloak

Keycloak, maintained by Red Hat and a CNCF Incubating project with approximately 26,000 GitHub stars, is the most direct open-source competitor to OpenAM. Both share Java roots and target the same use cases -- SSO, federation, multi-factor authentication -- but differ significantly in architecture, community, and trajectory.

| Dimension | OpenAM (OIP 16.0.5) | Keycloak (v26+) |
|-----------|----------------------|-----------------|
| **Runtime** | Monolithic WAR (Tomcat/Jetty) | Quarkus-native standalone JAR |
| **Language** | Java 11+ | Java 17+ (Quarkus) |
| **Admin UI** | Jato-based JSP (legacy) | React-based (rewritten v22+) |
| **OIDC Provider** | Yes | Yes (certified) |
| **SAML IdP/SP** | Yes | Yes |
| **Auth modules** | 34+ pluggable modules | SPI-based providers, fewer built-in but extensible |
| **Authorization** | XACML 3.0 policy engine | UMA 2.0, policy-based (less expressive) |
| **Multi-tenancy** | Realms/sub-realms | Realms + Organizations (v26 GA) |
| **User federation** | Embedded OpenDJ, LDAP | LDAP, AD, custom SPI |
| **Passkey/WebAuthn** | Yes (OIP module) | Yes (v22+) |
| **Configuration model** | LDAP-backed | Database-backed, realm export/import |
| **Kubernetes support** | Manual Docker/Helm | Official Kubernetes Operator |
| **CNCF status** | None | Incubating (2023) |
| **GitHub stars** | ~700 | ~26,000 |
| **Contributors** | ~30 | ~1,100 |
| **License** | CDDL 1.0 | Apache 2.0 |
| **Startup time** | 30-60s+ (WAR deployment) | ~5-10s (Quarkus optimized) |
| **Native image** | No | Experimental (GraalVM) |
| **Commercial backing** | 3A Systems (community) | Red Hat (~20 engineers) |

**Architecture differences.** Keycloak completed its migration from WildFly to Quarkus in v25 (2024), yielding roughly 50% faster startup, build-time provider optimization, and container-native immutable images. OpenAM remains a WAR-deployed application requiring a servlet container, with no path toward build-time optimization or native compilation.

**Admin experience.** Keycloak's React-based admin console and account console (rewritten in v22+) provide a modern management experience with declarative user profiles (v24), realm export/import for configuration-as-code, and Terraform community providers. OpenAM's Jato console has not been meaningfully updated in a decade.

**Community and ecosystem.** Keycloak's CNCF incubation provides governance, security audits, and vendor neutrality. Its SPI ecosystem supports extensive third-party extensions for themes, providers, and protocol mappers. OpenAM's community, while committed, lacks the scale to match this ecosystem.

**Where OpenAM retains an edge.** OpenAM's 34+ authentication modules (vs. Keycloak's more limited built-in set), its XACML 3.0 policy engine (vs. Keycloak's simpler UMA-based authorization), and its SAML 2.0 maturity (tested across thousands of federation deployments) remain differentiators for organizations with complex, legacy-heavy environments.

### 5.2 OpenAM vs Auth0/Okta

Auth0 (now Okta's Customer Identity Cloud) and Okta (Workforce Identity Cloud) represent the commercial SaaS end of the IAM spectrum.

| Dimension | OpenAM (OIP 16.0.5) | Auth0/Okta |
|-----------|----------------------|------------|
| **Deployment** | Self-hosted (on-prem or cloud IaaS) | Multi-tenant SaaS |
| **Pricing** | Free (CDDL), operational cost only | Free tier: 25K MAU; Professional/Enterprise: custom |
| **Extensibility** | Java SPI, Groovy scripts | Actions (Node.js serverless), 7,000+ app integrations |
| **Social login** | Via openam-auth-oauth2 module | 70+ pre-built social connections |
| **Compliance** | Self-managed (you prove compliance) | SOC 2 Type II, ISO 27001, PCI DSS, HIPAA BAA |
| **SLA** | Self-managed | 99.99% (Enterprise tier) |
| **Admin experience** | Jato console, ssoadm CLI | Modern dashboard, Management API, Terraform provider |
| **CIAM features** | Limited (no progressive profiling, consent mgmt) | Universal Login, progressive profiling, bot detection, breached password detection |
| **IGA integration** | Via OpenIDM (separate product) | Okta Identity Governance (built-in) |
| **Vendor risk** | Open source, no vendor dependency | Oct 2023 support system breach impacted reputation |

**When Auth0/Okta wins.** For organizations that prioritize speed to production, developer experience, managed compliance, and do not need on-premises deployment, Auth0/Okta is the rational choice. The breadth of pre-built integrations (7,000+ in Okta's Integration Network), the Actions extensibility model, and the managed infrastructure eliminate entire categories of operational burden.

**When OpenAM wins.** For organizations with strict data sovereignty requirements, air-gapped environments, complex legacy federation scenarios (dozens of SAML partners with custom metadata), or per-user cost sensitivity at scale (millions of users), self-hosted OpenAM avoids the per-MAU pricing that makes SaaS prohibitive. The CDDL license ensures no vendor lock-in, and the complete source code is auditable.

### 5.3 OpenAM vs AWS Cognito

AWS Cognito provides managed authentication for applications deployed on AWS, with User Pools (user directory + auth) and Identity Pools (federated access to AWS services).

| Dimension | OpenAM (OIP 16.0.5) | AWS Cognito |
|-----------|----------------------|-------------|
| **Deployment** | Self-hosted, cloud-agnostic | AWS-only managed service |
| **Pricing** | Free (CDDL) + infrastructure | Free: 50K MAU; then $0.0055-0.025/MAU |
| **SAML IdP** | Yes (full IdP/SP) | SAML consumer only (cannot produce SAML assertions) |
| **OAuth 2.0/OIDC** | Full provider | Yes |
| **Customization** | Full source code access | Lambda triggers, limited hosted UI customization |
| **User limit** | Unlimited (hardware-bound) | 40M per pool (soft limit) |
| **Migration path** | Portable (CDDL, standard protocols) | Non-trivial migration out of Cognito |
| **Vendor lock-in** | None | AWS-dependent |
| **Multi-cloud** | Yes | No |
| **Policy engine** | XACML 3.0 | IAM policies (separate system) |
| **Passkeys** | Yes (OIP module) | Yes (2024) |

**Cognito's primary limitation** is that it cannot act as a SAML Identity Provider -- it can consume SAML assertions from external IdPs but cannot produce them. Organizations needing to federate as a SAML IdP with partners must look elsewhere. Cognito's customization surface, while improved in the 2024 re-architecture (passwordless authentication, managed login branding), remains constrained compared to OpenAM's full source code access. The vendor lock-in to AWS is absolute: there is no self-hosted option and no straightforward migration path.

**Cognito's advantage** is zero operational overhead for teams already committed to AWS. Regional multi-AZ deployment, managed scaling, and integration with AWS IAM (via Identity Pools) eliminate infrastructure management entirely. For AWS-native applications with simple authentication requirements, Cognito is the path of least resistance.

### 5.4 OpenAM vs Ory Stack

The Ory stack (Hydra, Kratos, Keto, Oathkeeper) represents the architectural antithesis of OpenAM: a decomposed, headless, API-first microservices approach written in Go.

| Dimension | OpenAM (OIP 16.0.5) | Ory Stack |
|-----------|----------------------|-----------|
| **Architecture** | Monolithic WAR | Microservices (4 independent Go binaries) |
| **Language** | Java 11+ | Go |
| **OAuth 2.0/OIDC** | Yes | Hydra (certified OIDC) |
| **Identity management** | Embedded (LDAP-backed) | Kratos (API-first, JSON Schema identities) |
| **Authorization** | XACML 3.0 | Keto (Google Zanzibar ReBAC) |
| **Gateway/proxy** | OpenIG (separate product) | Oathkeeper (zero-trust proxy) |
| **UI** | Jato admin console, hosted login | Headless (no built-in UI; reference UIs provided) |
| **SAML** | Full IdP/SP | No SAML support |
| **Session model** | Server-side (LDAP/Cassandra) | Configurable (cookie-based, JWT) |
| **Managed offering** | None | Ory Network (SaaS) |
| **Operational complexity** | One WAR, one OpenDJ instance | 4+ services, each with its own database |
| **GitHub stars** | ~700 | ~40,000 (combined) |
| **License** | CDDL 1.0 | Apache 2.0 |

**Ory's headless approach** appeals to teams building custom authentication UX. By delegating login and consent decisions to the consuming application (Hydra redirects to your login page, not its own), Ory gives complete control over the user experience. OpenAM's hosted login page, while customizable via themes, constrains UX options.

**Ory's critical gap** is the absence of SAML support. Hydra implements OIDC but not SAML 2.0. Organizations with SAML federation requirements -- common in government, healthcare, and education -- cannot use Ory as a drop-in OpenAM replacement without adding a SAML bridge.

**Operational complexity** is Ory's trade-off. Four independent services, each requiring its own PostgreSQL/MySQL/CockroachDB database, load balancer, and monitoring, creates operational overhead that exceeds OpenAM's single-WAR deployment. The benefit is independent scaling and faster release cycles per component, but the cost is meaningful for teams without dedicated platform engineering.

**Keto's Zanzibar model** (relationship-based access control) is architecturally more modern than OpenAM's XACML policy engine, offering the permission model that powers Google's internal authorization. However, XACML's standards compliance and tooling maturity still matter for organizations invested in XACML policy authoring.

### 5.5 OpenAM vs Zitadel

Zitadel is a cloud-native identity platform built on event sourcing and CQRS, written in Go.

| Dimension | OpenAM (OIP 16.0.5) | Zitadel (v2.x) |
|-----------|----------------------|-----------------|
| **Architecture** | Monolithic WAR | Single Go binary + event-sourced CQRS |
| **Language** | Java 11+ | Go |
| **Deployment** | WAR + servlet container + OpenDJ | Single binary + PostgreSQL/CockroachDB |
| **Audit trail** | Add-on module (`openam-audit`) | Built-in (event sourcing IS the data model) |
| **Multi-tenancy** | Realms/sub-realms | Instances, Organizations, Projects (native) |
| **OIDC** | Yes | Yes |
| **SAML** | Full IdP/SP | Yes (v2.x) |
| **Authorization** | XACML 3.0 | RBAC with delegated management |
| **Passkeys** | Yes | Yes (WebAuthn native) |
| **SCIM** | No | Yes (2024) |
| **Management API** | REST, ssoadm CLI | gRPC + REST, Terraform provider |
| **Actions/extensibility** | Groovy scripting, Java SPI | JavaScript Actions on auth events |
| **GitHub stars** | ~700 | ~9,500 |
| **License** | CDDL 1.0 | Apache 2.0 |

**Zitadel's event-sourced architecture** is its most distinctive feature. Every state change is stored as an immutable event, making the audit trail not a bolt-on feature but the foundational data model. This provides point-in-time recovery, complete change history, and replay capability that OpenAM's audit module cannot match. The trade-off is the complexity of event-sourced systems: eventual consistency between the event store and read projections, projection rebuild time for large tenants, and the learning curve of CQRS for operators accustomed to CRUD systems.

**Operational simplicity** favors Zitadel. A single Go binary plus a PostgreSQL or CockroachDB database is the entire deployment, compared to OpenAM's WAR file, servlet container, and OpenDJ instance. Zitadel's Terraform provider enables declarative infrastructure-as-code workflows that OpenAM's LDAP-backed configuration cannot support natively.

**Where OpenAM retains advantage.** Zitadel's authorization model is RBAC, not ABAC/XACML. Organizations needing fine-grained, attribute-based policies with environment conditions and deny-overrides must implement this logic externally when using Zitadel. OpenAM's entitlement engine handles this natively.

---

## 6. Feature Gap Analysis

### What OpenAM Has That Alternatives Lack

| Capability | OpenAM | Keycloak | Ory | Zitadel | Auth0 |
|-----------|--------|----------|-----|---------|-------|
| XACML 3.0 policy engine | Yes | No | No | No | No |
| 34+ built-in auth modules | Yes | ~15 built-in | ~5 | ~8 | 70+ social, fewer protocol modules |
| SAML + OIDC + OAuth2 + UMA in one | Yes | Partial (no UMA 2.0 at parity) | No SAML | Yes (no UMA) | Yes (no UMA) |
| Cassandra session store | Yes | No (Infinispan) | No | No | N/A (managed) |
| Embedded LDAP (OpenDJ) | Yes | No (external) | No | No | No |
| RADIUS server | Yes | No | No | No | No |
| Standalone STS (Security Token Service) | Yes | No | No | No | No |

OpenAM's XACML 3.0 engine is unique among open-source IAM platforms. Keycloak offers UMA 2.0-based authorization services and is exploring fine-grained authorization, but it does not implement the XACML standard. The Ory stack delegates authorization to Keto (Zanzibar model), which is architecturally distinct. No mainstream open-source IAM platform matches OpenAM's XACML compliance.

### What Alternatives Have That OpenAM Lacks

| Capability | OpenAM | Keycloak | Ory | Zitadel | Auth0 |
|-----------|--------|----------|-----|---------|-------|
| Modern admin UI | No | Yes (React) | N/A (headless) | Yes (Angular) | Yes |
| Configuration-as-code | Limited | Realm export/import | Full YAML | Terraform provider | Terraform, Deploy CLI |
| Kubernetes Operator | No | Yes (official) | Helm charts | Helm charts | N/A (SaaS) |
| Event sourcing / audit by design | No | No | No | Yes | No |
| SCIM provisioning | No (separate OpenIDM) | Via extension | No | Yes | Yes (Enterprise) |
| Zanzibar-style ReBAC | No | No | Yes (Keto) | No | Yes (OpenFGA) |
| Visual flow editor | No | No | No | No | No (Authentik has one) |
| Passkey-first design | No | No | No | No | No (Hanko has this) |
| Native GraalVM support | No | Experimental | N/A (Go) | N/A (Go) | N/A |
| Organizations/B2B multi-tenancy | Realms | Organizations (v26) | Yes | Yes (native) | Yes (Organizations) |

The most significant gaps are operational: no Kubernetes Operator, no Terraform provider, no declarative configuration model, and no modern admin UI. These gaps make OpenAM harder to deploy, manage, and automate in cloud-native environments where infrastructure-as-code is the baseline expectation.

### The Protocol Gap: What Each Alternative Misses

One dimension not captured in simple feature matrices is protocol depth. OpenAM's SAML 2.0 implementation has been tested against hundreds of partner IdP/SP implementations over two decades, handling edge cases in metadata exchange, artifact resolution, attribute mapping, and logout propagation that newer SAML implementations have not yet encountered. The difference between "supports SAML" and "has been battle-tested across a thousand SAML federations" is material for organizations where SAML interoperability failures translate to business disruptions.

Similarly, OpenAM's OAuth 2.0 implementation supports grant types (JWT bearer, device code) and token management patterns (CTS-backed stateful tokens, introspection, revocation) that not all alternatives implement at the same depth. Keycloak matches or exceeds this depth; Ory Hydra is a certified OIDC provider with excellent OAuth 2.0 coverage; but smaller platforms (Logto, SuperTokens, Hanko) implement a subset focused on common flows and may lack edge-case grant types.

The inverse is also true. OpenAM does not implement SCIM 2.0, Zanzibar-style relationship-based authorization, event sourcing, or the modern passkey-first authentication flows that newer platforms provide. The protocol gap is bidirectional: OpenAM covers protocols of the 2005-2016 era with unmatched depth, while alternatives cover protocols and patterns of the 2020-2026 era with greater architectural alignment.

---

## 7. Build-vs-Buy Decision Framework

### When OpenAM Makes Sense

- **Existing ForgeRock deployment migration.** Organizations running ForgeRock CE 11.0.3 (which must be abandoned immediately due to unpatched critical CVEs -- see Chapter 6) or earlier ForgeRock versions can migrate to OIP OpenAM 16.0.5 or Wren:AM 16.0.0-M1 with relative architectural continuity. The module structure, authentication chains, and session management model are familiar.

- **Complex SAML federation environments.** Organizations with dozens of SAML 2.0 partners, custom metadata handling, and deep SAML attribute mapping requirements benefit from OpenAM's 20+ years of SAML maturity. Newer platforms support SAML but have not been tested across the same breadth of partner implementations.

- **XACML policy requirements.** If the organization has invested in XACML policy authoring or requires standards-compliant ABAC, OpenAM's entitlement engine is the only open-source option that delivers this without external policy engines.

- **Air-gapped or sovereign deployments.** Government and defense organizations that cannot use SaaS and require complete source code auditability benefit from OpenAM's CDDL-licensed, fully self-hosted model.

- **Java ecosystem alignment.** For organizations whose operations teams are deeply experienced with Java, Maven, and servlet containers, OpenAM's technology stack aligns with existing skills and tooling.

### When Alternatives Are Better

- **Greenfield projects.** For new deployments without legacy constraints, Keycloak is the safer open-source choice: larger community, CNCF governance, modern runtime, better documentation, and broader industry adoption. The risk-adjusted total cost of ownership is lower.

- **Cloud-native / Kubernetes-first.** If the deployment target is Kubernetes, Keycloak's Operator, Zitadel's single-binary model, or Ory's microservices architecture are architecturally better suited than OpenAM's WAR deployment.

- **Developer experience priority.** If developer onboarding speed and API-first design are priorities, Ory (headless, Go, clean APIs), Logto (TypeScript, beautiful default UI), or Auth0 (managed, extensive SDKs) will outperform OpenAM's steep learning curve.

- **CIAM / consumer-facing.** For customer identity scenarios requiring progressive profiling, social login breadth, bot detection, and managed compliance, Auth0 or AWS Cognito provide purpose-built capabilities that OpenAM lacks.

- **Budget for managed service.** If the organization can absorb per-MAU SaaS pricing, the operational savings from Auth0, Okta, or Zitadel Cloud typically exceed the infrastructure and personnel costs of self-hosting OpenAM.

- **Passkey-first strategy.** If passwordless authentication is the primary requirement, Hanko's passkey-native design or Keycloak's WebAuthn integration offer cleaner paths than OpenAM's bolt-on WebAuthn module.

### Migration Cost Considerations

For organizations currently running OpenAM (any fork) and evaluating migration to alternatives, the cost dimensions include:

- **Authentication chain migration.** OpenAM's JAAS-based chain model with control flags (REQUIRED, REQUISITE, SUFFICIENT, OPTIONAL) must be translated to the target platform's authentication flow model. Keycloak uses authentication flows with conditional sub-flows; Ory Kratos uses configurable self-service flows; Zitadel uses login policies. The mapping is not one-to-one, and complex chains with conditional branching require redesign.

- **SAML metadata migration.** Each SAML partner relationship involves metadata exchange, attribute mapping, and often custom configuration. Migrating dozens of SAML partnerships to a new IdP requires coordinated metadata updates with every partner -- a project-level effort that can take months.

- **Policy migration.** XACML policies stored in OpenDJ must be translated to the target platform's authorization model (Keycloak's UMA policies, OPA Rego, Cedar, or application-level RBAC). No automated translation tools exist for XACML-to-Rego or XACML-to-Cedar conversion.

- **Session migration.** Active user sessions cannot be migrated between platforms. Any migration requires a session cutover, which either forces all users to re-authenticate simultaneously or requires a period of dual-running where both old and new systems accept sessions.

- **Custom module migration.** Organizations with custom `AMLoginModule` implementations must rewrite them as Keycloak SPI providers, Ory webhooks, or equivalent extension mechanisms in the target platform. The effort depends on module complexity but typically ranges from days (simple credential validation) to weeks (complex multi-step flows with external system integration).

These costs are nontrivial but must be weighed against the ongoing operational cost of maintaining OpenAM: the CVE patching burden, the configuration complexity, and the growing difficulty of hiring engineers with JAAS, LDAP configuration, and Jato expertise.

---

## 8. Verdict

OpenAM remains the most feature-complete open-source access management platform in terms of raw protocol and authentication breadth. Its XACML 3.0 policy engine, 34+ authentication modules, and combined SAML/OIDC/OAuth2/UMA support are unmatched in the open-source ecosystem. However, its monolithic WAR architecture, Jato legacy UI, LDAP-backed configuration model, CVE history (including a CISA-flagged pre-auth RCE), and small maintainer community place it at a significant disadvantage against Keycloak and cloud-native alternatives for new deployments. OpenAM's strongest use case is brownfield: organizations migrating from ForgeRock, operating in complex SAML federation environments, or requiring XACML compliance in air-gapped settings. For greenfield projects, the risk-adjusted choice is Keycloak for self-hosted or Auth0/Zitadel Cloud for managed, unless specific OpenAM capabilities (XACML, deep SAML, RADIUS) are genuine requirements rather than checkbox items.
