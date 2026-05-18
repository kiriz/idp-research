---
title: Where IAM Is Today — Modern Landscape
description: "Keycloak, Ory, Auth0, Okta, Cognito, Zitadel, Authentik — the full modern IAM landscape analyzed and compared to the ForgeRock-era stack."
sidebar:
  order: 1
---

# Chapter 12: Modern Architecture Patterns

The architecture of identity and access management systems has undergone a fundamental transformation over the past decade. What began as monolithic, on-premises middleware suites -- exemplified by the Open Identity Platform (OIP) stack analyzed throughout this research -- has given way to cloud-native, API-first, composable identity services built on zero-trust principles. This chapter traces fourteen major architectural shifts, situating the OIP components (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF) as reference points for the "before" state and mapping each to its modern counterpart. The shifts are not purely technological; they reflect broader changes in threat models, deployment patterns, regulatory requirements, and the expanding definition of "identity" itself -- from human users authenticating via browsers to machine workloads, IoT devices, and AI agents operating across distributed infrastructure.

---

![Modern IAM Landscape Positioning](/idp-research/diagrams/11-iam-landscape.svg)

![Swim Lane Timeline: Modern Era (2005-2026)](/idp-research/diagrams/15b-swimlane-modern.svg)

## Then vs Now: Comparison Table

The following table summarizes all fourteen architectural shifts covered in this chapter.

| # | Dimension | Then (2005-2016 era) | Now (2020-2026 era) | Key Standards / Technologies |
|---|-----------|----------------------|----------------------|------------------------------|
| 1 | Platform architecture | Monolithic WAR-deployed IAM suites (OpenAM, OpenIDM) | Decomposed microservices, composable identity APIs | Ory stack, Keycloak on Quarkus, Kubernetes |
| 2 | Identity store | On-premises LDAPv3 directories (OpenDJ, 389 DS, AD) | Cloud-native identity stores, managed directories, SQL/NoSQL backends | SCIM, Microsoft Graph, PostgreSQL, CockroachDB |
| 3 | Federation protocol | SAML 2.0 with manual metadata exchange | OIDC with discovery, dynamic registration, OIDC Federation | OIDC Core 1.0, OIDC Federation, OpenID4VC |
| 4 | Policy enforcement | Policy agents embedded in web/app servers (OpenIG, J2EE agents) | API gateways + sidecar proxies + service mesh | Envoy, Istio, Kong, OPA, Ory Oathkeeper |
| 5 | Provisioning | Proprietary connectors (OpenICF), SPML | SCIM 2.0 + event-driven sync (SSF, webhooks, CDC) | RFC 7642-7644, OIDC Shared Signals |
| 6 | Session management | Server-side sessions, domain cookies | Stateless JWT, then sender-constrained tokens (DPoP, mTLS) | RFC 7519, RFC 9449, RFC 8705 |
| 7 | Credential type | Passwords + SMS OTP + TOTP | Passkeys (FIDO2), platform authenticators, conditional UI | WebAuthn L2/L3, CTAP 2.1, FIDO CXP/CXF |
| 8 | Security model | Perimeter-based (firewall + VPN + network zones) | Zero Trust (never trust, always verify, assume breach) | NIST SP 800-207, OMB M-22-09, BeyondCorp |
| 9 | Identity scope | Human users (employees, customers) | Human + machine + workload identity | SPIFFE/SPIRE, Kubernetes service accounts, Venafi |
| 10 | Intelligence | Static rules, manual access reviews | AI-driven adaptive auth, behavioral analytics, LLM-powered policy | SailPoint Identity AI, Entra ID Protection |
| 11 | Compliance | Per-audit checkbox exercises | Continuous compliance, consent management, data residency | GDPR, eIDAS 2.0, SOX, HIPAA, NIS2 |
| 12 | API security | Session cookies forwarded by reverse proxy | OAuth token validation at gateway, mTLS, service mesh identity | OAuth 2.0, mTLS (RFC 8705), SPIFFE, Istio |
| 13 | Threat detection | SIEM log correlation, manual investigation | Identity Threat Detection and Response (ITDR) | CrowdStrike Falcon, Silverfort, Entra ID Protection |
| 14 | Trust model | Centralized IdP as single source of truth | Decentralized identity, verifiable credentials, self-sovereign | W3C VCs 2.0, DIDs 1.0, SD-JWT VC, OID4VC |

---

## 1. Monolithic IAM Suites to Decomposed Microservices

### The Monolithic Era

The OIP stack represents the canonical monolithic IAM architecture of the 2005-2016 period. OpenAM deploys as a single WAR file containing authentication engines (34+ modules), OAuth 2.0/OIDC provider, SAML 2.0 IdP/SP, XACML policy engine, session management, and an administrative console (see [OpenAM Analysis](/idp-research/openam-lineage/openam/)). OpenIDM runs as a monolithic OSGi application bundling sync engine, reconciliation, workflow (Activiti BPMN), and connector orchestration (see [OpenIDM Analysis](/idp-research/openam-lineage/openidm/)). Each component carries the full weight of its capabilities whether or not a given deployment uses them all.

This model had clear strengths: a single deployment artifact, unified configuration, and well-tested internal integration paths. It also had structural weaknesses. Scaling required scaling the entire application; a bug in the SAML engine could take down the OAuth 2.0 provider; upgrading one capability required redeploying the whole system; and the monolith's memory footprint grew with every feature added.

### The Decomposed Model

Modern IAM architectures decompose the monolith into purpose-built services. The Ory stack (Hydra, Kratos, Keto, Oathkeeper) is the clearest example: each identity concern -- OAuth 2.0/OIDC issuance (Hydra), identity management (Kratos), authorization (Keto), and policy enforcement (Oathkeeper) -- is a standalone Go binary with its own database, API surface, and deployment lifecycle. Teams adopt only the components they need.

Keycloak occupies an intermediate position. It remains a single application, but its migration from WildFly to Quarkus (completed in v25, 2024) introduced build-time optimization, ahead-of-time provider compilation, and container-native immutable images. The result is a lighter, faster deployment that behaves more like a microservice even if it is not decomposed into separate processes.

Zitadel takes a different approach: a single Go binary backed by event sourcing and CQRS. The single-binary simplicity appeals to operators, while the event-sourced architecture provides the auditability and replay capabilities that monoliths typically lack.

### Architectural Implications

The decomposed model introduces inter-service communication overhead, distributed transaction complexity (saga patterns), and operational burden (more services to monitor). It also enables independent scaling, faster release cycles per component, and technology-appropriate choices per service (e.g., Go for a high-throughput token endpoint, Python for a policy engine). Gartner's "identity fabric" concept -- composing best-of-breed identity services rather than selecting a single platform -- codifies this direction.

The OIP stack's modular Maven structure (OpenAM alone has ~60 submodules) hints at internal decomposition boundaries that a modern rewrite might exploit. The dependency chain (OpenDJ -> OpenAM -> OpenIG; OpenICF -> OpenIDM) already defines natural service boundaries.

---

## 2. On-Premises LDAP to Cloud-Native Identity Stores

### LDAP as Universal Identity Store

LDAPv3 (RFC 4510-4519) has served as the universal identity store protocol since 1997. OpenDJ implements a full LDAPv3 server with multi-master replication, virtual attributes, and REST-to-LDAP mapping (see [OpenDJ Analysis](/idp-research/openam-lineage/opendj/)). Active Directory, 389 Directory Server, and OpenLDAP fill the same role in other ecosystems. The hierarchical DIT (Directory Information Tree) model, while powerful for organizational modeling, imposes a rigid schema that resists the fluid identity structures demanded by modern applications.

### Cloud-Native Alternatives

Cloud IAM platforms have moved away from LDAP as the primary identity store:

- **Managed directories as abstraction layers.** Microsoft Entra ID, AWS Directory Service, and Google Cloud Identity all expose LDAP interfaces but back them with proprietary, globally distributed stores. The LDAP protocol becomes a compatibility facade rather than the native storage model.

- **SQL and NewSQL backends.** Keycloak uses PostgreSQL, MySQL, or Oracle. Ory Kratos and Zitadel use PostgreSQL or CockroachDB. SuperTokens uses PostgreSQL or MySQL. These platforms chose relational databases for their maturity, tooling, and developer familiarity -- and because modern identity workloads (user profiles, credentials, consent records) map naturally to relational schemas.

- **SCIM as the wire protocol.** Where LDAP once served as both store and sync protocol, SCIM 2.0 (RFC 7642-7644) now handles cross-domain provisioning over REST/JSON. Applications no longer need to speak LDAP; they expose SCIM endpoints and let the IdP push identity data.

- **Virtual directories.** Products like Radiant Logic provide LDAP facades over heterogeneous sources (SQL, REST, LDAP, flat files), preserving LDAP compatibility for legacy consumers while the authoritative data lives elsewhere.

### What Persists

LDAP is not disappearing. Active Directory remains the dominant enterprise directory, and Kerberos V5 authentication still underpins Windows domain environments (see [Authentication Protocols](/idp-research/protocols/authentication/)). OpenDJ and 389 DS continue to serve organizations that need on-premises directory services. The shift is not the elimination of LDAP but its demotion from primary store to compatibility interface, increasingly hidden behind REST/GraphQL APIs (Microsoft Graph, SCIM) and accessed directly only by legacy systems.

---

## 3. SAML Federation to OIDC Federation

### SAML 2.0: The Enterprise Standard

SAML 2.0 (OASIS, 2005) became the dominant enterprise federation protocol by merging SAML 1.1, Liberty Alliance ID-FF, and Shibboleth concepts into a comprehensive XML-based framework (see [Federation Protocols](/idp-research/protocols/federation/)). OpenAM implements full SAML 2.0 IdP and SP capabilities with metadata management, all standard bindings (HTTP-Redirect, HTTP-POST, HTTP-Artifact, SOAP), and single logout.

SAML's strengths -- mature tooling, deep enterprise deployment, extensive metadata federations (InCommon, eduGAIN) -- are matched by weaknesses that modern architectures expose: XML complexity, verbose assertion payloads, lack of native mobile support, no built-in discovery mechanism, and manual metadata exchange that does not scale to thousands of relying parties.

### OIDC Ascendant

OpenID Connect (2014) built authentication on top of OAuth 2.0, inheriting its JSON/REST foundation, token-based model, and developer-friendly ecosystem. Key architectural advantages over SAML include:

- **Discovery.** The `/.well-known/openid-configuration` endpoint eliminates manual metadata exchange.
- **Dynamic registration.** Clients can register programmatically, enabling multi-tenant SaaS platforms to onboard relying parties without human intervention.
- **Compact tokens.** JWT-based ID tokens are smaller than SAML assertions and parse natively in JavaScript, Go, Python, and every modern language.
- **Mobile-native.** OIDC was designed for OAuth 2.0 flows that work in native apps (authorization code + PKCE per RFC 7636 and RFC 8252), whereas SAML's browser-redirect model fits poorly on mobile.
- **Active extension ecosystem.** OIDC CIBA (client-initiated backchannel auth), OIDC Shared Signals (SSF), and OpenID4VC/VP extend the protocol into new domains.

### OIDC Federation: Scaling Trust

OIDC Federation 1.0 (draft, gaining traction in 2024) addresses the remaining gap: automated trust establishment between OIDC entities via cryptographic trust chains, eliminating the manual metadata exchange that SAML federations require. The EU eIDAS 2.0 regulation references OIDC Federation as the trust infrastructure for European Digital Identity Wallets, providing a regulatory forcing function for adoption.

### Coexistence

SAML 2.0 is not being replaced overnight. Virtually every enterprise IdP (Okta, Entra ID, Ping Identity, Keycloak, OpenAM) supports both SAML and OIDC. Education federations (InCommon, eduGAIN) run on SAML. Government frameworks (FedRAMP, FICAM) rely on it. The practical trajectory is OIDC for new integrations, SAML for legacy and specialized federations, with identity brokering (Keycloak, OpenAM, Authentik) bridging the two.

---

## 4. Policy Agents to API Gateways and Sidecar Proxies

### The Agent Model

The OIP stack enforces access policy through dedicated agents and gateways. OpenIG operates as an identity-aware reverse proxy with a filter/handler pipeline (50+ filter types, 16 handler types) that intercepts HTTP requests, evaluates policies against OpenAM, and either permits or blocks access (see [OpenIG Analysis](/idp-research/openam-lineage/openig/)). OpenAM also provided J2EE and web server policy agents -- lightweight modules embedded directly in Apache, IIS, or Tomcat that intercepted requests at the container level.

This model assumed a known set of web applications running on known infrastructure. The agent must be installed and configured on each application server. Scaling meant deploying agents everywhere. Updates required touching every agent instance.

### API Gateways and Sidecars

Modern architectures decouple policy enforcement from application servers through three patterns:

**API gateways** (Kong, Envoy, AWS API Gateway, Traefik) sit at the ingress point and handle authentication (JWT validation, OAuth introspection), rate limiting, and request transformation. The gateway centralizes policy enforcement for all upstream services without requiring per-service agents. OpenIG was an early precursor to this pattern, but modern gateways operate at infrastructure level with declarative configuration and Kubernetes-native deployment.

**Sidecar proxies** (Envoy in Istio, Linkerd proxy) run alongside each service in a mesh, providing mTLS, authorization policy enforcement, and observability without application code changes. The sidecar intercepts all traffic to and from the service, applying policy decisions from a control plane (e.g., Istio's istiod). This is conceptually similar to the J2EE agent model but implemented at the network layer rather than the application layer.

**External authorization** (OPA, Ory Oathkeeper, Cedar via Amazon Verified Permissions) decouples policy decision from policy enforcement. The gateway or sidecar calls an external policy decision point (PDP) for authorization checks. OPA's Rego language and Cedar's formally verifiable policies represent a significant advance over OpenAM's XACML-based entitlements engine in developer usability and cloud-native integration (see [Authorization Frameworks](/idp-research/protocols/authorization/)).

### Comparison with OIP Approach

| Aspect | OIP (OpenIG / Agents) | Modern (Gateway + Sidecar + PDP) |
|--------|----------------------|----------------------------------|
| Deployment | Per-server agent install | Infrastructure-level (gateway) or per-pod sidecar |
| Configuration | Per-agent config files | Centralized, declarative (Kubernetes CRDs, Envoy xDS) |
| Protocol support | HTTP, J2EE | HTTP, gRPC, TCP, WebSocket |
| Policy language | XACML 3.0 (XML) | OPA/Rego, Cedar, YAML rules |
| Service mesh integration | None | Native (Istio, Linkerd, Consul Connect) |
| Observability | Application logs | Distributed tracing, metrics, access logs |

---

## 5. Provisioning Connectors to SCIM and Event-Driven Sync

### The Connector Framework Model

OpenICF (Open Identity Connector Framework) provides a Java SPI for building provisioning connectors -- LDAP, database, CSV, SSH, Kerberos, Groovy-scripted (see [OpenICF Analysis](/idp-research/openam-lineage/openicf/)). OpenIDM orchestrates these connectors for identity lifecycle operations: joiner/mover/leaver workflows, reconciliation, and synchronization. Each target system requires a dedicated connector implementation. The framework uses a pull-based reconciliation model where OpenIDM periodically scans source and target systems to detect and resolve differences.

### SCIM 2.0 as Universal Provisioning API

SCIM 2.0 (RFC 7642-7644, 2015) standardized what connector frameworks attempted to solve with proprietary code. Instead of writing a custom connector for each SaaS application, the IdP pushes user and group changes to the application's SCIM `/Users` and `/Groups` endpoints. Major SaaS providers (Salesforce, Slack, Zoom, GitHub Enterprise, Atlassian, Snowflake) now expose SCIM 2.0 endpoints. Okta, Entra ID, SailPoint, and Saviynt all provision via SCIM as the default mechanism.

SCIM's limitations are well-documented: no standard for entitlements or roles (only users and groups in the core schema), no event/webhook model (it is push-based from the IdP side but has no standard notification mechanism for changes on the application side), and inconsistent PATCH semantics across implementations.

### Event-Driven Sync

The gap left by SCIM's pull/push model is being filled by event-driven approaches:

- **OIDC Shared Signals Framework (SSF)**, formerly RISC + CAEP, standardizes real-time security event sharing between providers using Security Event Tokens (RFC 8935/8936). An IdP can notify relying parties of session revocation, credential compromise, or account changes in near-real-time.

- **Webhooks** provide application-specific event notification. Ory Kratos, Zitadel, Logto, and Authentik all support webhook events on identity lifecycle changes, enabling downstream systems to react without polling.

- **Change Data Capture (CDC)** at the database level (Debezium, DynamoDB Streams, PostgreSQL logical replication) enables event-driven identity sync without relying on application-layer APIs. This pattern is especially useful for legacy systems that predate SCIM.

The trajectory is clear: connector frameworks like OpenICF serve on-premises and legacy systems that lack standard APIs, while SCIM + event-driven sync handles cloud-native applications. Modern IGA platforms (SailPoint, Saviynt) maintain connector frameworks for legacy targets while defaulting to SCIM for SaaS.

---

## 6. Session Cookies to Stateless JWT to Token Binding

### Server-Side Sessions and Domain Cookies

Traditional IAM systems, including OpenAM, manage sessions server-side. OpenAM issues an `iPlanetDirectoryPro` cookie containing a session ID; the session state (user attributes, authentication level, timeout) lives in server memory or a shared store (see [OpenAM Analysis](/idp-research/openam-lineage/openam/)). This model requires sticky sessions or a distributed session store (OpenAM supports CTS -- Core Token Service backed by OpenDJ, or Cassandra). Domain cookies limit SSO to a single DNS domain unless combined with federation protocols.

### Stateless JWT

The OAuth 2.0/OIDC shift introduced stateless tokens. A JWT (RFC 7519) encodes claims, is signed by the issuer, and can be validated by any party with the public key -- no session store required (see [Token Formats](/idp-research/protocols/tokens/)). This removed the scaling bottleneck of centralized session stores and enabled cross-domain, cross-service authentication without shared cookies.

However, stateless JWTs introduced new problems: tokens cannot be revoked before expiry without a revocation list (negating some of the statelessness benefit); long-lived tokens increase the blast radius of theft; and bearer tokens are vulnerable to replay if intercepted.

### Sender-Constrained Tokens

The current generation of token standards addresses bearer token weaknesses:

- **DPoP (RFC 9449, 2023)** -- Demonstration of Proof-of-Possession. The client generates a key pair and includes a proof of possession in each request. The access token is bound to the client's public key, so a stolen token cannot be used without the corresponding private key. DPoP works without mTLS infrastructure, making it practical for browser-based and mobile applications.

- **mTLS-bound tokens (RFC 8705)** -- The access token is bound to the client certificate used in the TLS handshake. Requires mTLS infrastructure but provides stronger binding guarantees.

- **Token exchange (RFC 8693)** -- Enables STS-style delegation where a service can exchange an incoming token for a new, scoped-down token for downstream calls, limiting the blast radius of any single token.

### Evolution Summary

| Generation | Mechanism | State | Revocation | Theft resistance |
|------------|-----------|-------|------------|------------------|
| 1st | Server-side session + cookie | Stateful | Immediate (delete session) | Cookie theft = full impersonation |
| 2nd | Stateless JWT bearer token | Stateless | Difficult (requires revocation list) | Token theft = full impersonation until expiry |
| 3rd | DPoP / mTLS-bound token | Stateless | Short-lived + revocation list | Token theft insufficient without private key |

---

## 7. Password-Based Auth to Passwordless and Passkeys

### The Password Problem

For decades, passwords were the universal authentication credential. OpenAM's LDAP authentication module, DataStore module, and Active Directory module all ultimately validate a password against a directory store (see [Authentication Protocols](/idp-research/protocols/authentication/)). The limitations are well-documented: credential stuffing, phishing, password reuse, and the operational cost of password resets (Gartner estimated 20-50% of help desk calls are password-related).

Successive mitigations -- complexity requirements, HOTP (RFC 4226), TOTP (RFC 6238), SMS OTP, push notification -- added friction and security layers but did not solve the fundamental problem: the user possesses a shared secret that can be phished, leaked, or brute-forced.

### FIDO2 and WebAuthn

The FIDO Alliance and W3C addressed this with FIDO2, comprising WebAuthn (browser API) and CTAP (client-to-authenticator protocol). WebAuthn Level 1 became a W3C Recommendation in 2019; Level 2 followed in 2021; Level 3 is in working draft (2024).

The core innovation is asymmetric cryptography scoped to the relying party's origin. The authenticator generates a key pair per origin; the private key never leaves the authenticator; the public key is registered with the relying party. Authentication is a challenge-response using the private key. A credential created for `example.com` cryptographically cannot be used on `examp1e.com`, making phishing structurally impossible.

### Passkeys: Making FIDO2 Practical

Passkeys (announced 2022) solve FIDO2's usability gap -- device-bound credentials were lost when the device was lost. Passkeys are synced WebAuthn credentials stored in platform credential managers:

- **Apple iCloud Keychain** (iOS 16+, macOS Ventura+)
- **Google Password Manager** (Android 14+, Chrome)
- **Microsoft Windows Hello** (Windows 11 23H2+)
- **Third-party managers** (1Password, Bitwarden, Dashlane)

**Conditional UI** (2024) integrates passkeys into browser autofill, allowing users to select a passkey from the same UI they use for passwords -- no special "sign in with passkey" button required. This lowers the adoption barrier significantly.

**Device-bound passkeys** (hardware security keys like YubiKey 5, Google Titan) remain important for regulated environments requiring AAL3-equivalent assurance per NIST SP 800-63B. The private key cannot be extracted, providing the highest assurance against credential theft.

### Enterprise Adoption

FIDO Alliance reported 15B+ passkey-enabled accounts by late 2024. Google reported passkey sign-ins are 4x faster and more successful than password sign-ins. Enterprise deployments accelerate where phishing-resistant MFA mandates apply (US OMB M-22-09, NIST SP 800-63-4 draft).

Implementation support is broad: Keycloak (v22+), Auth0 (2024), Okta (2024), Entra ID (2024), Ory Kratos, Hanko (passkey-native), Zitadel, Authentik. OpenAM in the OIP distribution includes a WebAuthn authentication module, though it predates the passkey-sync era.

### The Remaining Challenges

Account recovery when all passkeys are lost remains an unsolved UX problem. Cross-platform passkey management (moving between Apple, Google, and Microsoft ecosystems) is addressed by the FIDO CXP/CXF (Credential Exchange Protocol/Format, 2024), but adoption is nascent. Enterprise device policies that restrict which authenticators are permitted add deployment complexity.

---

## 8. Perimeter Security to Zero Trust Architecture

### The Perimeter Model

Traditional IAM architectures assumed a trusted internal network. Firewalls, VPNs, and network zones defined trust boundaries. OpenAM authenticated users at the perimeter; OpenIG enforced policy at the reverse proxy layer; once inside the network, services communicated with minimal additional authentication. This model collapses when the perimeter dissolves -- remote workers, cloud workloads, SaaS applications, and mobile devices all operate outside the traditional network boundary.

### Zero Trust Principles

The zero trust model, codified by NIST SP 800-207 (2020) and mandated for US federal agencies by OMB M-22-09 (2022), rests on three principles:

1. **Verify explicitly.** Authenticate and authorize every request based on all available signals (identity, device, location, behavior, resource sensitivity).
2. **Least privilege access.** Grant minimum necessary access, just-in-time and just-enough.
3. **Assume breach.** Design systems as if the attacker is already inside the network. Minimize blast radius through micro-segmentation and continuous monitoring.

### Identity as the New Perimeter

Zero trust elevates the identity provider to the most critical infrastructure component. Every access decision depends on identity verification. This drives several technical requirements:

- **Strong authentication.** Phishing-resistant credentials (FIDO2/passkeys) replace passwords as the baseline. MFA is mandatory, not optional.
- **Continuous evaluation.** Access is not a one-time gate. The OIDC Shared Signals Framework (CAEP -- Continuous Access Evaluation Protocol) enables real-time session revocation when risk signals change (device compliance lost, impossible travel detected, credential compromised).
- **Device trust.** The identity of the device matters alongside the identity of the user. Device posture (patch level, disk encryption, MDM compliance) becomes an input to access decisions.
- **Micro-segmentation.** Network segments enforce that even authenticated users can reach only the resources they are authorized for. Service mesh (Istio, Linkerd) implements this at the application layer with mTLS and authorization policies.
- **Context-aware policies.** Authorization decisions consider user identity, device state, network location, time of access, resource sensitivity, and behavioral signals -- not just "is the user authenticated."

### From BeyondCorp to Standard Practice

Google's BeyondCorp (published 2014) demonstrated zero trust at scale: no VPN, every request authenticated and authorized regardless of network location, device inventory as a first-class concept. What was radical in 2014 is now standard guidance. The CISA Zero Trust Maturity Model (v2.0, 2023) provides a staged adoption framework across five pillars: Identity, Devices, Networks, Applications, and Data.

---

## 9. Human Identity to Machine Identity

### The Human-Centric Model

The OIP stack was designed primarily for human identity. OpenAM authenticates users via browser-based flows. OpenDJ stores person entries with attributes like `uid`, `mail`, and `telephoneNumber`. OpenIDM manages human lifecycle events (joiner, mover, leaver). The assumption was that identity = human using a browser or thick client.

### The Machine Identity Explosion

Non-human identities (NHIs) -- service accounts, API keys, workload identities, IoT devices, CI/CD pipelines, AI agents -- now outnumber human identities by ratios of 50:1 or more in large organizations. Each microservice, serverless function, container, and automated pipeline needs an identity to authenticate to other services and access resources. The OIP stack addresses this partially through OAuth 2.0 client credentials grants in OpenAM, but lacks a comprehensive machine identity framework.

### SPIFFE and SPIRE

The Secure Production Identity Framework for Everyone (SPIFFE) defines a standard for workload identity. SPIRE (SPIFFE Runtime Environment) is the reference implementation, graduated from CNCF in 2024.

Key concepts:

- **SPIFFE ID**: A URI-based identity (`spiffe://trust-domain/workload-path`) assigned to each workload.
- **SVID (SPIFFE Verifiable Identity Document)**: An X.509 certificate or JWT containing the SPIFFE ID, issued to the workload after attestation.
- **Workload API**: A local API (Unix domain socket) through which workloads obtain SVIDs without managing secrets. No secrets are baked into container images or config files.
- **Attestation**: Node attestation (is this compute node authorized?) and workload attestation (is this process authorized?) replace static credentials with dynamic, verifiable identity.

### Service Mesh Integration

Istio uses SPIFFE IDs natively for mTLS between services. Every service in the mesh gets a SPIFFE-compliant X.509 certificate, automatically rotated, with identity derived from the Kubernetes service account. This is the zero-trust analog of what OpenIG's policy agents did for HTTP services -- but applied to all east-west traffic, at the network layer, with cryptographic identity.

### Machine Identity Management

CyberArk's acquisition of Venafi (2024) and the broader machine identity management market address the operational challenge: certificate lifecycle management, SSH key management, code signing, and secrets management for non-human identities. HashiCorp Vault (now IBM) provides dynamic secrets -- short-lived credentials for databases, cloud providers, and PKI -- that eliminate the long-lived service account passwords historically stored in configuration files.

---

## 10. AI and Identity

### Adaptive Authentication

Risk-based or adaptive authentication predates the current AI wave. OpenAM's adaptive authentication module evaluated device fingerprints, geographic location, and login history to adjust authentication requirements. Modern implementations apply machine learning at greater scale:

- **Microsoft Entra ID Protection** evaluates sign-in risk (unfamiliar location, atypical travel, anonymous IP, malware-linked IP) and user risk (leaked credentials, anomalous behavior) using ML models trained on signals from billions of authentications across the Microsoft ecosystem.
- **Okta Identity Threat Protection** uses behavioral analysis to detect and respond to identity-based threats in real time.
- **Auth0 Adaptive MFA** dynamically steps up authentication based on transaction risk signals.

### Behavioral Biometrics

Behavioral biometrics -- keystroke dynamics, mouse movement patterns, touch pressure, navigation patterns -- provide continuous authentication signals without explicit user interaction. These signals feed into risk engines that can trigger step-up authentication or session termination when behavior deviates from established baselines. Products from BioCatch, Neuro-ID, and features within Entra ID Protection implement this pattern.

### AI-Driven Access Governance

Identity governance is where AI has the most tangible impact today:

- **Access outlier detection.** SailPoint Identity AI identifies users with access patterns that deviate significantly from peers in the same role or department.
- **Role mining and optimization.** ML algorithms analyze existing access patterns to suggest role definitions, reducing the manual effort of role engineering.
- **Access review recommendations.** During certification campaigns, AI recommends approve/revoke decisions based on usage patterns, peer access, and risk signals. SailPoint and Saviynt both offer this capability.
- **Automated provisioning recommendations.** When a user changes roles (mover event), AI suggests the access changes based on what others in the new role possess.

### LLM-Powered Policy

Large language models introduce new possibilities for identity and authorization:

- **Natural language policy authoring.** Instead of writing Rego or Cedar policies, administrators describe intent in natural language and the system generates formal policy. AWS has demonstrated Cedar policy generation from natural language descriptions.
- **Policy explanation.** LLMs can explain why an access request was denied by interpreting policy evaluation traces in human-readable terms.
- **Anomaly narration.** SIEM and ITDR tools use LLMs to generate natural language summaries of suspicious identity activity patterns, reducing analyst investigation time.

These applications are nascent and carry risks: LLM hallucination in policy generation could create security gaps, and reliance on AI for access decisions raises accountability questions. Human review of AI-generated policies remains essential.

---

## 11. Compliance-Driven IAM

### Audit Trails

Regulatory frameworks (SOX, HIPAA, PCI-DSS, GDPR) require demonstrable proof of who accessed what, when, and why. The OIP stack provides audit logging in OpenAM (authentication events, policy decisions) and OpenIDM (provisioning actions, reconciliation results), but audit was often an afterthought -- logs shipped to a SIEM for post-hoc analysis.

Modern architectures build audit into the data model. Zitadel's event-sourced architecture stores every state change as an immutable event, making the audit trail the system's primary data structure rather than a secondary log. Every identity lifecycle action, authentication event, and policy change is an event that can be replayed, queried, and attested.

### Consent Management

GDPR (2018) and subsequent privacy regulations (CCPA, LGPD, POPIA) require explicit user consent for data processing, the ability to withdraw consent, and data subject access requests (DSAR). IAM systems must track:

- What data is collected and for what purpose
- When and how consent was obtained
- Consent withdrawal and its downstream effects (deprovisioning, data deletion)
- Data retention periods and automated expiry

Auth0's progressive profiling and consent management, Ory Kratos's identity schema model (where collected attributes are explicitly defined), and IGA platforms' data access governance features address these requirements.

### Data Residency

Regulations increasingly mandate where identity data is stored. GDPR restricts transfer of EU personal data outside the EEA without adequate safeguards. China's PIPL, Russia's Federal Law 242-FZ, and similar laws impose local storage requirements.

This drives architectural decisions: multi-region identity stores with data partitioning by jurisdiction, region-specific IdP deployments, and metadata-only replication across borders. Cloud IAM providers (Okta, Auth0, Entra ID) offer region selection for data residency. Self-hosted solutions (Keycloak, OIP stack) give full control over data location but shift the operational burden.

### Continuous Compliance

The shift from periodic audits to continuous compliance monitoring reflects both regulatory evolution and technical capability. IGA platforms continuously evaluate access against policy (SoD violations, access beyond certification period, orphaned accounts). ITDR tools continuously monitor identity infrastructure for configuration drift and attack indicators. The goal is a compliance posture that is always audit-ready, not periodically remediated.

---

## 12. API Security and Identity

### The Traditional Model

In the OIP architecture, API security was an extension of web application security. OpenIG intercepted HTTP requests to backend services, validated sessions against OpenAM, and forwarded authenticated requests upstream. APIs exposed behind OpenIG inherited the same cookie-based session model used for web applications. OpenAM's OAuth 2.0 implementation added token-based access, but the token validation pattern was tightly coupled to OpenAM's token introspection endpoint.

### Modern API Security Architecture

Modern API security places identity at the core of every service interaction, whether between a client and an API, between two internal services, or between services across organizational boundaries.

**OAuth 2.0 token validation at the gateway.** API gateways (Kong, Envoy, AWS API Gateway) validate JWT access tokens at the edge, checking signature, expiry, issuer, audience, and scopes without a round-trip to the authorization server. For opaque tokens, the gateway calls the introspection endpoint (RFC 7662). This pattern decouples the API from the IdP implementation -- any OIDC-compliant IdP can issue tokens that any standards-compliant gateway can validate.

**mTLS for service-to-service identity.** Mutual TLS provides cryptographic identity for both client and server. In a service mesh (Istio, Linkerd), mTLS is automatic: the sidecar proxy handles certificate management, rotation, and verification. SPIFFE SVIDs (X.509 certificates with SPIFFE IDs in the SAN field) standardize the identity format within mTLS.

**Fine-grained authorization.** Coarse OAuth scopes (`read`, `write`, `admin`) are insufficient for complex authorization requirements. Rich Authorization Requests (RFC 9396) enable fine-grained `authorization_details` in OAuth flows. At the service layer, OPA/Rego or Cedar policies evaluate per-request authorization based on user attributes, resource attributes, and environmental context.

**Token binding and proof-of-possession.** As discussed in section 6, DPoP (RFC 9449) and mTLS certificate-bound tokens (RFC 8705) ensure that stolen tokens cannot be replayed by a different client. This is critical for high-value API transactions (financial services, healthcare).

### API Security in Service Mesh

Service mesh architectures (Istio, Linkerd, Consul Connect) unify several API security concerns:

| Concern | Mechanism |
|---------|-----------|
| Transport encryption | Automatic mTLS between all services |
| Service identity | SPIFFE-compliant X.509 certificates |
| Authorization policy | AuthorizationPolicy CRDs (Istio), OPA integration |
| Traffic control | Rate limiting, circuit breaking, retry policies |
| Observability | Distributed tracing, access logs, metrics |

This represents a comprehensive evolution from the OpenIG + OpenAM policy agent model: identity is embedded in the infrastructure rather than bolted on at the application layer (see [Chapter 13: Comparison Matrices](13-comparison-matrices.md) for a cross-platform feature comparison).

---

## 13. Identity Threat Detection and Response (ITDR)

### The Emerging Category

Identity Threat Detection and Response (ITDR) emerged as a recognized Gartner category in 2022-2023, reflecting the reality that identity is now the primary attack vector. Credential theft, privilege escalation, lateral movement, and account takeover dominate real-world breaches. Traditional SIEM-based detection was too slow and too noisy; ITDR tools focus specifically on identity-layer signals.

### Attack Patterns ITDR Addresses

| Attack pattern | Description | Traditional detection gap |
|---------------|-------------|---------------------------|
| Credential stuffing | Automated login attempts using breached credential lists | Rate limiting catches volume but not low-and-slow attacks |
| Password spraying | Few password attempts across many accounts | Below per-account lockout thresholds |
| Kerberos attacks | Golden Ticket, Silver Ticket, Kerberoasting, DCSync | Invisible to network-layer tools; requires AD-level monitoring |
| MFA fatigue / push bombing | Repeated MFA push notifications to wear down the user | MFA logs show "approved" even if user was socially engineered |
| Token theft / replay | Stealing OAuth/OIDC tokens from browser storage or logs | Bearer tokens are valid until expiry; no binding to client |
| Lateral movement | Using compromised credentials to pivot between systems | Each hop appears as a legitimate authentication |
| Privilege escalation | Exploiting misconfigurations to gain higher privileges | Requires baseline of normal privilege usage |
| Service account abuse | Using over-privileged service accounts for unauthorized access | Service accounts often exempt from MFA and monitoring |

### Leading ITDR Approaches

**CrowdStrike Falcon Identity Threat Detection** (formerly Preempt Security) monitors Active Directory in real time, detecting Kerberos attacks (Pass-the-Hash, Golden Ticket, DCSync), lateral movement, and identity hygiene issues (stale accounts, excessive privileges). It integrates with the broader Falcon XDR platform for unified threat response.

**Silverfort** takes a unique architectural approach: it integrates at the Active Directory domain controller level without agents or proxies, intercepting authentication decisions at the directory layer. This enables MFA enforcement for any resource (including legacy systems, file shares, and command-line tools that never supported MFA) and behavioral baselining of every authentication event.

**Microsoft Entra ID Protection + Defender for Identity** provides native ITDR for Microsoft environments. Entra ID Protection evaluates cloud-based sign-in risk; Defender for Identity monitors on-premises Active Directory. The integration with Microsoft 365 Defender (XDR) and Sentinel (SIEM) provides a unified identity security posture.

### ITDR and IAM Architecture

ITDR changes IAM architecture in several ways:

- **Continuous evaluation replaces point-in-time authentication.** The OIDC Shared Signals Framework (SSF, formerly RISC + CAEP) enables IdPs to push real-time risk events to relying parties, triggering session revocation or step-up authentication.
- **Identity infrastructure becomes a monitored attack surface.** Active Directory, IdP configurations, OAuth client registrations, and SAML trust relationships are monitored for unauthorized changes.
- **Service accounts get first-class monitoring.** Historically ignored by IAM (OpenAM and similar systems treated service accounts identically to user accounts), service accounts are now subject to behavioral baselining and anomaly detection.
- **Identity hygiene becomes continuous.** Stale accounts, excessive privileges, and unused entitlements are continuously detected rather than discovered during periodic access reviews.

---

## 14. Decentralized Identity

### The Centralized Status Quo

Every IAM architecture discussed in this research -- from the OIP stack to Keycloak to Okta -- relies on a centralized identity provider. The IdP issues assertions (SAML) or tokens (OIDC) that relying parties trust because they trust the IdP. The user does not control the credential; the IdP does. If the IdP revokes access, the user loses access. If the IdP is breached, all users are affected. If the IdP is unavailable, authentication fails.

### W3C Verifiable Credentials

Verifiable Credentials (W3C VC Data Model 2.0, 2024) invert this model. An **issuer** (university, government, employer) issues a cryptographically signed credential to a **holder** (the user). The holder stores the credential in a digital wallet and presents it to a **verifier** when needed. The verifier validates the credential's cryptographic signature against the issuer's public key without contacting the issuer. The holder controls when, to whom, and which claims within the credential are disclosed.

Key technical components:

- **Selective disclosure.** SD-JWT VC (IETF draft, EU Digital Identity Wallet candidate format) enables the holder to reveal only specific claims from a credential, not the entire document.
- **Revocation.** Status lists (bitstring status list) allow verifiers to check whether a credential has been revoked without contacting the issuer in real time.
- **Securing mechanisms.** VCs can be secured with JWT/JWS (VC-JOSE-COSE) or Data Integrity Proofs (JSON-LD linked data signatures). The JWT path is favored for government-scale deployments due to simplicity and tooling maturity.

### Decentralized Identifiers (DIDs)

DIDs (W3C DID Core 1.0, 2022) provide globally unique, self-controlled identifiers. A DID (`did:method:identifier`) resolves to a DID Document containing public keys, service endpoints, and verification methods. Over 150 DID methods have been registered, but practical adoption concentrates on a few:

- `did:web` -- DNS-based, no blockchain. Easiest to adopt. Growing in enterprise contexts.
- `did:key` -- Self-contained, ephemeral. Useful for testing and transient interactions.
- `did:jwk` -- JWK-based, simple key representation.
- Blockchain-anchored methods (`did:ion`, `did:ethr`, `did:sov`) have seen minimal mainstream adoption. The EU eIDAS 2.0 Architecture Reference Framework deliberately avoids mandating blockchain.

### OpenID for Verifiable Credentials (OID4VC)

The OID4VC suite of specifications bridges the established OIDC ecosystem with verifiable credentials:

- **OID4VCI** (OpenID for Verifiable Credential Issuance): Issue VCs through OIDC mechanisms.
- **OID4VP** (OpenID for Verifiable Presentations): Present VCs to verifiers via OIDC flows.
- **SIOPv2** (Self-Issued OpenID Provider v2): The user's wallet acts as its own IdP.

The EU eIDAS 2.0 Architecture Reference Framework adopted OID4VC as the credential exchange protocol for European Digital Identity Wallets (EUDIW), mandated for all member states by 2026. This is the largest regulatory forcing function for verifiable credential adoption.

### Adoption Reality

Decentralized identity is advancing but remains in early stages for most use cases:

| Segment | Status | Examples |
|---------|--------|----------|
| Government ID | Production pilots, regulatory mandates | EU Digital Identity Wallet (eIDAS 2.0), US mobile driver's licenses (ISO 18013-5), Korea national digital ID |
| Enterprise | Early exploration | Employee credential verification, supply chain attestation, professional certifications |
| Consumer | Limited | Primarily government-issued credentials in digital wallets |
| Blockchain-based SSI | Niche | Hyperledger Indy/Aries deployments, British Columbia OrgBook |

The "self-sovereign identity" vision of fully decentralized, user-controlled identity has been tempered by practical requirements: trust frameworks still need governance, issuers still need to be authoritative, and recovery mechanisms still need fallback options. What is emerging is a hybrid model where verifiable credentials coexist with centralized IdPs, with the user gaining portability and selective disclosure capabilities rather than full sovereignty.

---

## Cross-Cutting Themes

### Composability Over Monoliths

The overarching theme across all fourteen shifts is the move from integrated, monolithic platforms to composable, interoperable services. The OIP stack was designed as a suite where each component (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF) was purpose-built to work with the others. Modern architectures compose services from different vendors and open-source projects, connected by standardized protocols (OIDC, SCIM, SPIFFE) and enforced by policy engines (OPA, Cedar).

### Standards as Integration Fabric

The proliferation of interoperability standards (OIDC, SCIM, SPIFFE, WebAuthn, OID4VC) is what makes composability possible. Each standard addresses a specific integration seam:

| Integration seam | Legacy approach | Standard |
|-----------------|-----------------|----------|
| Authentication | Proprietary session cookies, SAML | OIDC |
| Provisioning | Custom connectors (OpenICF) | SCIM 2.0 |
| Authorization policy | Embedded XACML, proprietary rules | OPA/Rego, Cedar |
| Workload identity | Static service accounts | SPIFFE/SPIRE |
| Credential format | Passwords, TOTP | WebAuthn/Passkeys |
| Credential portability | None (locked to IdP) | W3C VCs, OID4VC |
| Security events | SIEM log shipping | OIDC SSF (CAEP + RISC) |

### Defense in Depth Through Identity

Zero trust architecture, ITDR, adaptive authentication, and service mesh identity collectively implement defense-in-depth centered on identity rather than network topology. Every layer -- gateway, sidecar, application, database -- verifies identity and enforces authorization. This is a fundamental departure from the perimeter model where identity was verified once at the edge and trusted throughout the interior.

### The Pace of Change

The standards timeline (see [Appendix: Standards Timeline](../extracts/standards-timeline.md)) reveals an accelerating pace. LDAP took 14 years from v1 (1993) to its definitive revision (2006). OAuth went from 1.0 (2007) to 2.0 (2012) in five years, and DPoP, PAR, and RAR followed within a few years more. Passkeys went from announcement (2022) to mainstream platform support (2024) in two years. This acceleration compresses the time organizations have to evaluate, plan, and adopt new patterns. The monolithic IAM suites of the 2005-2016 era had upgrade cycles measured in years; modern identity services operate on continuous delivery cadences measured in weeks.

---

## Summary

The fourteen architectural shifts documented in this chapter represent a comprehensive transformation of identity and access management. The OIP stack -- OpenAM, OpenDJ, OpenIDM, OpenIG, and OpenICF -- embodies the design principles of the 2005-2016 era: monolithic deployment, LDAP-centric storage, SAML-dominant federation, agent-based enforcement, and human-centric identity. Each of these principles has a modern counterpart that addresses the demands of cloud-native infrastructure, zero-trust security, machine identity, regulatory compliance, and an expanding threat landscape.

The transformation is not binary. LDAP coexists with cloud-native stores. SAML coexists with OIDC. Monolithic platforms (Keycloak) coexist with decomposed stacks (Ory). The practical trajectory for most organizations is a gradual shift -- wrapping legacy protocols behind modern APIs, adding zero-trust controls incrementally, adopting passkeys alongside existing MFA, and extending identity governance to machine identities and AI agents. The standards and patterns described here provide the architectural vocabulary for that journey.

---

## Modern Platform Landscape

# Modern IAM Landscape (2024-2025)

> **Data provenance note**: This document was compiled from training knowledge with
> a cutoff of May 2025. GitHub star counts, version numbers, and release dates
> reflect the best available data as of that date. Figures marked with `~` are
> approximate. Verify critical numbers against live sources before using in
> decision documents.

---

## Executive Summary

1. **Keycloak dominates OSS IAM.** With 26k+ GitHub stars and CNCF incubation
   (graduated to incubating in 2023), Keycloak is the de facto standard for
   self-hosted SSO/OIDC/SAML. v26 (late 2024) completed the migration from
   WildFly to a Quarkus-native runtime, dramatically reducing footprint.

2. **Ory is the cloud-native challenger.** The Ory stack (Hydra, Kratos, Keto,
   Oathkeeper) takes a headless, API-first, microservices approach to IAM.
   Combined GitHub stars exceed 40k. Ory Network provides a managed offering.

3. **Passkeys hit inflection.** Apple, Google, and Microsoft shipped passkey
   support across all major OS and browsers by mid-2024. Enterprise adoption
   accelerated through 2024-2025, with FIDO Alliance reporting 15B+ accounts
   passkey-enabled. WebAuthn is now a baseline expectation.

4. **Policy-as-code matures.** OPA/Rego remains dominant in Kubernetes policy,
   while AWS Cedar (open-sourced 2023) gains traction for application-level
   AuthZ. Both support formal verification of policies.

5. **IGA modernizes.** SailPoint went public then private (Thoma Bravo, 2024),
   Saviynt raised $200M+. Both push AI-driven access reviews and identity
   governance.

6. **ITDR emerges as a category.** Identity Threat Detection & Response became
   a recognized Gartner category in 2023. CrowdStrike, Silverfort, and
   Microsoft Entra ID Protection lead.

7. **Workload identity standardizes.** SPIFFE/SPIRE graduated CNCF incubation
   (2024). Adoption in service mesh and zero-trust architectures accelerated.

8. **Decentralized identity advances slowly.** W3C Verifiable Credentials
   reached v2.0 (2024). EU eIDAS 2.0 regulation mandates digital identity
   wallets by 2026, forcing real-world adoption timelines.

9. **Next-gen OSS entrants fragment the market.** Casdoor, Logto, SuperTokens,
   Hanko, Authentik, Authelia, and Zitadel each carve niches. None yet rival
   Keycloak's breadth, but developer experience is often superior.

10. **Vendor consolidation continues.** Okta acquired Auth0 (2021, fully
    integrated by 2024). Ping Identity merged with ForgeRock (2023). Thales
    acquired OneSpan's identity verification. CyberArk acquired Venafi.

---

## Detailed Findings

---

### Established IAM Platforms

---

#### Keycloak

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.keycloak.org |
| **GitHub** | https://github.com/keycloak/keycloak |
| **Stars** | ~26,000 |
| **Language** | Java (Quarkus) |
| **License** | Apache 2.0 |
| **Latest version** | 26.x (late 2024) / 27.x (early 2025) |
| **CNCF status** | Incubating (accepted 2023) |
| **Contributors** | ~1,100+ |
| **Maintainer** | Red Hat |

**Description**

Keycloak is the most widely deployed open-source IAM platform. It provides SSO,
identity brokering, user federation, admin console, and fine-grained
authorization services. Originally built on JBoss/WildFly, it completed its
migration to Quarkus in 2024, yielding significant performance improvements and
reduced memory footprint.

**Key features**

- OpenID Connect, OAuth 2.0, SAML 2.0 identity provider and service provider
- User federation (LDAP, Active Directory, custom providers via SPI)
- Identity brokering (login with Google, GitHub, SAML IdP, etc.)
- Fine-grained authorization services (UMA 2.0, policy-based)
- Admin console and Account console (React-based, rewritten in v22+)
- Client adapters retired in favor of standard OIDC libraries
- Declarative user profiles (v24+)
- Organizations support (v26+) for multi-tenancy
- Passkey/WebAuthn support
- Kubernetes Operator for cloud-native deployment
- Extensive SPI (Service Provider Interface) for customization
- Multi-realm architecture

**Architecture summary**

Keycloak runs as a standalone Quarkus application (previously WildFly). It uses
Infinispan for caching/clustering and supports PostgreSQL, MySQL, MariaDB,
Oracle, and MSSQL as backing stores. The Quarkus-native build (introduced in
v17, default since v22, sole option since v25) provides:

- ~50% faster startup compared to WildFly distribution
- Ahead-of-time optimization of providers
- Build-time configuration for immutable container images
- Native executable option via GraalVM (experimental)

Deployment patterns: standalone JAR, Docker container, Kubernetes Operator,
or embedded in a Java application.

**Recent milestones (2024-2025)**

- v24 (Mar 2024): Declarative user profiles GA, Quarkus 3.8
- v25 (Jul 2024): WildFly distribution removed entirely, persistent user
  sessions (preview), Organizations (preview)
- v26 (Nov 2024): Organizations GA, persistent user sessions GA, OpenTelemetry
  tracing improvements
- CNCF incubation status provides governance, security audits, and vendor
  neutrality

**Community**

Red Hat maintains the core team (~20 engineers). The broader community
contributes extensions via the Keycloak SPI ecosystem. Active mailing lists,
GitHub Discussions, and a Discourse forum. Extensive third-party extensions
exist for themes, providers, and protocol mappers.

---

#### Ory Stack (Hydra, Kratos, Keto, Oathkeeper)

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.ory.sh |
| **GitHub org** | https://github.com/ory |
| **Language** | Go |
| **License** | Apache 2.0 |
| **Managed offering** | Ory Network (SaaS) |
| **Company** | Ory Corp (Berlin, Germany) |

The Ory stack takes a fundamentally different approach from monolithic IAM
platforms like Keycloak. Each component is a standalone microservice with its
own database, API, and deployment lifecycle. This enables teams to adopt only
the pieces they need.

##### Ory Hydra (OAuth2 & OIDC Server)

| Attribute | Value |
|-----------|-------|
| **GitHub** | https://github.com/ory/hydra |
| **Stars** | ~15,800 |
| **Latest version** | v2.3.x (2024) |
| **Contributors** | ~300 |

- Certified OpenID Connect Provider (all profiles)
- Implements OAuth 2.0 Authorization Code, Client Credentials, Implicit,
  Device Authorization, and Token Exchange grants
- Headless: no login/consent UI -- delegates to your application via
  redirect-based consent/login flows
- PostgreSQL, MySQL, CockroachDB backends
- HSM support for signing keys
- OAuth 2.0 Token Introspection, Revocation, Dynamic Client Registration
- FAPI (Financial-grade API) compliance work ongoing

**Architecture**: Hydra is a stateless Go binary that exposes two API surfaces:
a public API (token endpoint, authorize endpoint, JWKS) and an admin API
(client management, consent/login flow management). Login and consent
decisions are delegated to an external application via HTTP redirects,
giving full control over UX.

##### Ory Kratos (Identity Management)

| Attribute | Value |
|-----------|-------|
| **GitHub** | https://github.com/ory/kratos |
| **Stars** | ~11,500 |
| **Latest version** | v1.3.x (2024-2025) |
| **Contributors** | ~220 |

- Cloud-native identity management (registration, login, account recovery,
  MFA, profile management, account verification)
- Headless: API-first with no built-in UI (reference UIs provided)
- Identity schema defined as JSON Schema (fully customizable fields)
- Self-service flows: registration, login, settings, recovery, verification
- MFA: TOTP, WebAuthn/passkeys, lookup secrets (backup codes)
- Social sign-in (OIDC providers)
- Identity credentials: password, OIDC, WebAuthn, TOTP, passwordless
- Webhooks for event-driven architectures
- Session management with configurable lifespans and refresh

**Architecture**: Kratos manages identity data in PostgreSQL, MySQL, or
CockroachDB. It exposes a public API (self-service flows) and an admin API
(identity CRUD). Browser and API (native app) flow variants are supported.
Identity schemas are JSON Schema documents that define what fields an
identity has.

##### Ory Keto (Authorization / Permissions)

| Attribute | Value |
|-----------|-------|
| **GitHub** | https://github.com/ory/keto |
| **Stars** | ~4,900 |
| **Latest version** | v0.12.x (2024) |
| **Contributors** | ~80 |

- Implements Google Zanzibar-style relationship-based access control (ReBAC)
- Relation tuples: `subject#relation@object` (e.g., `user:alice#member@group:engineering`)
- Check, Expand, List APIs
- Namespace configuration for defining relations and permissions
- Supports RBAC, ABAC, and ACL patterns via relation tuples
- gRPC and REST APIs

**Architecture**: Keto stores relation tuples in PostgreSQL, MySQL, or
CockroachDB. It implements the Zanzibar consistency model with snapshot
reads and change tracking. The Expand API computes the transitive closure
of permissions.

##### Ory Oathkeeper (Identity & Access Proxy)

| Attribute | Value |
|-----------|-------|
| **GitHub** | https://github.com/ory/oathkeeper |
| **Stars** | ~3,400 |
| **Latest version** | v0.40.x (2024) |
| **Contributors** | ~100 |

- Reverse proxy / API gateway for zero-trust architectures
- Authenticators: cookie session, bearer token, OAuth2 introspection,
  JWT, anonymous, no-op
- Authorizers: allow, deny, Keto (Zanzibar), remote (webhook)
- Mutators: header, cookie, ID token (JWT injection)
- Rule-based access control with JSON or YAML configuration
- Works as a standalone proxy, sidecar, or middleware

**Architecture**: Oathkeeper sits in front of upstream services. Each incoming
request is matched against access rules that define an authentication
handler, an authorization handler, and a credential mutation handler. It
can inject identity information (as headers or JWT) into upstream requests.

**Ory Network (Managed)**

Ory Network is the managed SaaS offering that bundles all four components.
It provides:
- Global edge deployment
- Managed infrastructure (no database administration)
- Built-in UI components (Ory Elements)
- Usage-based pricing (free tier available)
- SOC 2 Type II certified

---

#### Auth0 / Okta

| Attribute | Value |
|-----------|-------|
| **Website** | https://auth0.com / https://www.okta.com |
| **Parent** | Okta, Inc. (acquired Auth0 in May 2021 for $6.5B) |
| **Type** | Commercial SaaS (IDaaS) |
| **Market position** | Gartner Magic Quadrant Leader (Access Management) |

**Description**

Auth0 is a developer-focused identity platform, now part of Okta's Customer
Identity Cloud (CIC). Okta Workforce Identity Cloud (WIC) handles enterprise
IAM (SSO, lifecycle management, directory integration). Together they serve
both B2C/B2B (Auth0/CIC) and B2E (Okta/WIC) use cases.

**Key capabilities**

Auth0 (Customer Identity Cloud):
- Universal Login: hosted, customizable login page
- 70+ social connections, enterprise connections (SAML, OIDC, LDAP/AD)
- Adaptive MFA (SMS, email, push, TOTP, WebAuthn)
- Actions: serverless extensibility (replaced Rules and Hooks)
- Organizations: multi-tenant B2B identity
- Fine-grained authorization (Okta FGA, based on OpenFGA/Zanzibar)
- Breached password detection
- Bot detection
- Passkey support (2024)
- CIAM features: progressive profiling, consent management

Okta (Workforce Identity Cloud):
- SSO to 7,000+ pre-built app integrations (OIN)
- Lifecycle management and provisioning (SCIM)
- Okta Identity Governance (OIG) -- acquired via acquisition
- Okta Privileged Access (OPA) -- PAM capabilities
- Okta Device Access -- desktop MFA
- Okta Identity Threat Protection (ITDR)

**Pricing model**

Auth0/CIC:
- Free tier: 25,000 MAU (monthly active users) -- expanded in 2024
- Essentials: ~$35/month (up to 10k MAU)
- Professional: custom pricing
- Enterprise: custom, includes SLA, advanced security

Okta/WIC:
- Per-user/month pricing
- SSO: ~$2-6/user/month
- Adaptive MFA: ~$3-6/user/month
- Lifecycle Management: ~$4-9/user/month
- Bundles available

**Market position**

- Okta is the dominant independent identity vendor with ~$2.5B ARR (FY2025)
- 19,650+ customers (combined)
- Gartner Leader in Access Management for 8+ consecutive years
- Primary competitors: Microsoft Entra ID, Ping Identity (now merged with
  ForgeRock), CyberArk, and cloud provider native solutions
- Major security incident in Oct 2023 (support system breach) impacted
  reputation; followed by significant security investment in 2024
  ("Okta Secure Identity Commitment")

**Architecture**

Auth0 is a multi-tenant SaaS platform. Key architectural elements:
- Tenant isolation at the data layer
- Extensibility via Actions (Node.js serverless functions in a pipeline)
- Edge-deployed Universal Login for low-latency authentication
- Custom domains for white-labeling
- Private Cloud option for dedicated infrastructure

---

#### AWS Cognito

| Attribute | Value |
|-----------|-------|
| **Website** | https://aws.amazon.com/cognito |
| **Type** | Managed cloud service (AWS) |
| **Pricing** | Free tier: 50,000 MAU; then $0.0055-0.025/MAU |

**Description**

Amazon Cognito provides authentication, authorization, and user management for
web and mobile applications. It consists of User Pools (user directory and
authentication) and Identity Pools (federated identity for AWS resource
access). A major re-architecture was announced at re:Invent 2024.

**Key features**

- User Pools: managed user directory with sign-up, sign-in, MFA, account
  recovery, email/SMS verification
- Identity Pools: federated access to AWS services via temporary IAM
  credentials
- Social/enterprise identity federation (Google, Facebook, Apple, SAML, OIDC)
- Adaptive authentication (risk-based)
- Advanced security features: compromised credential detection, device
  fingerprinting
- Lambda triggers for customizing auth flows (pre/post authentication,
  pre sign-up, custom messages, token generation)
- Hosted UI for quick integration
- OAuth 2.0 / OIDC compliance
- Passkey/WebAuthn support (added 2024)
- Managed login UI customization improvements (2024)
- Access token customization (2024)
- Threat protection enhancements

**Cognito re-architecture (2024-2025)**

AWS announced significant Cognito improvements:
- Passwordless authentication (magic links, passkeys) -- GA 2024
- Managed login (redesigned hosted UI with branding editor)
- Essentials tier with advanced features bundled at lower price
- Access token customization without Lambda triggers
- Simplified pricing tiers (Lite, Essentials, Plus)

**Architecture summary**

- User Pools: regional service, multi-AZ by default
- Data stored in AWS-managed infrastructure (not directly accessible)
- Integration via AWS SDKs, Amplify libraries, or standard OIDC/OAuth2
- Lambda triggers execute at various points in the auth flow
- Identity Pools issue temporary AWS STS credentials mapped to IAM roles
- No self-hosted option; AWS-only

**Limitations**

- Vendor lock-in to AWS
- Limited customization of hosted UI (improved in 2024 but still constrained)
- User pool limits: 40M users per pool (soft limit)
- No built-in SAML IdP functionality (can consume SAML, not produce it)
- Complex pricing with feature-dependent tiers
- Migration path out of Cognito is non-trivial

---

#### Azure AD B2C / Microsoft Entra External ID

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-external-id |
| **Type** | Managed cloud service (Azure) |
| **Rebranding** | Azure AD -> Microsoft Entra ID (Jul 2023); Azure AD B2C -> Entra External ID |

**Description**

Microsoft Entra External ID (formerly Azure AD B2C) is Microsoft's CIAM
solution for customer-facing applications. It is part of the broader Microsoft
Entra family which also includes Entra ID (workforce IAM), Entra ID Governance,
Entra Permissions Management, Entra Verified ID, and Entra Workload ID.

**Key features**

- Custom authentication experiences via user flows and custom policies
- Social identity providers (Google, Facebook, Apple, etc.)
- Enterprise federation (SAML, OIDC, WS-Federation)
- Self-service sign-up with attribute collection
- Progressive profiling
- Conditional Access policies
- Identity Protection (risk-based authentication)
- Custom branding
- Multi-language support
- API connectors for integration with external systems

**Entra External ID (next generation, 2024-2025)**

Microsoft has been building a next-generation CIAM platform under the Entra
External ID brand:
- Native integration with Entra ID (single admin portal)
- External tenants for customer-facing scenarios
- Pre-built sign-in/sign-up UI components
- Native passkey support
- Custom authentication extensions (replacing custom policies)
- CIAM SDKs (MSAL-based)
- Event-driven extensibility

**Architecture**

- Built on the Microsoft Entra (Azure AD) platform
- Global presence across Azure regions
- XML-based Identity Experience Framework (IEF) for custom policies (B2C)
  -- being replaced by simpler flows in External ID
- Token service supporting OIDC, OAuth 2.0, SAML 2.0
- Integration with Azure API Management, Azure Functions

**Pricing**

- Free tier: 50,000 MAU (authentications/month)
- P1: ~$0.00325/authentication beyond free tier
- P2: ~$0.01625/authentication (adds Identity Protection, Conditional Access)
- MFA add-on charges apply

---

#### Google Identity Platform

| Attribute | Value |
|-----------|-------|
| **Website** | https://cloud.google.com/identity-platform |
| **Type** | Managed cloud service (GCP) |
| **Relation** | Upgraded version of Firebase Authentication |

**Description**

Google Identity Platform is Google Cloud's CIAM solution, providing
authentication and user management. It is the enterprise tier of Firebase
Authentication, adding multi-tenancy, SLA, and advanced features.

**Key features**

- Email/password, phone, social sign-in (Google, Facebook, Twitter, Apple,
  Microsoft, GitHub, etc.)
- SAML and OIDC federation
- Multi-tenancy (multiple user pools in one project)
- Multi-factor authentication (SMS, TOTP)
- Blocking functions (Cloud Functions triggers)
- Anonymous authentication (for guest users)
- Custom authentication (bring your own auth system)
- reCAPTCHA Enterprise integration
- Password policy enforcement
- Email enumeration protection
- Passkey support via Firebase Auth (2024)

**Architecture**

- Global Google infrastructure
- Client SDKs: Firebase Auth SDK (Web, iOS, Android, Flutter, Unity, C++)
- Admin SDK: Node.js, Java, Python, Go, C#
- REST API and gRPC
- Integration with Google Cloud IAM for resource access
- Emulator suite for local development

**Pricing**

- Firebase Auth (Spark plan): free, limited features
- Identity Platform (Blaze plan): $0.0055/MAU (phone auth: $0.01-0.06/SMS)
- No charge for first 50,000 MAU/month
- SAML/OIDC federation: $0.015/MAU

**Limitations**

- Less mature CIAM feature set vs. Auth0 or Entra External ID
- Limited customization of authentication flows
- No built-in authorization/RBAC (must build on top)
- Primarily designed for consumer apps, less suited for complex B2B

---

### Next-Generation OSS Entrants

---

#### Casdoor (Go-based, Casbin ecosystem)

| Attribute | Value |
|-----------|-------|
| **Website** | https://casdoor.org |
| **GitHub** | https://github.com/casdoor/casdoor |
| **Stars** | ~10,500 |
| **Language** | Go (backend), React (frontend) |
| **License** | Apache 2.0 |
| **Latest version** | v1.x (continuously released, ~2-4 week cadence) |
| **Ecosystem** | Casbin (authorization library) |

**Description**

Casdoor is a UI-first IAM platform built by the Casbin community. It provides
a centralized authentication platform with built-in UI for sign-up, sign-in,
user management, and organization management. It integrates tightly with
Casbin for authorization.

**Key features**

- Built-in web UI (not headless) for all IAM operations
- OAuth 2.0 / OIDC provider
- SAML IdP and SP
- LDAP client and server
- 80+ social login providers (third-party OAuth connectors)
- Multi-factor authentication (SMS, email, TOTP)
- Multi-tenancy (organizations, applications)
- User management (CRUD, import/export)
- Role-based access control (via Casbin integration)
- Webhook support
- CAS 3.0 protocol support
- Resource management (file storage with S3, local, etc.)
- Built-in SMTP for email verification

**Architecture**

Casdoor is a monolithic Go application with an embedded React SPA. It
supports MySQL, PostgreSQL, SQL Server, SQLite, and CockroachDB as backends.
The Casbin library is embedded for policy enforcement. Deployment is
straightforward: single binary or Docker container.

**Community**

- Primarily maintained by the Casbin open-source community (China-based core team)
- Active development with frequent releases
- Documentation in English and Chinese
- Growing adoption in Asian markets; less known in Western enterprise contexts

---

#### Logto (TypeScript, OIDC-native)

| Attribute | Value |
|-----------|-------|
| **Website** | https://logto.io |
| **GitHub** | https://github.com/logto-io/logto |
| **Stars** | ~9,500 |
| **Language** | TypeScript (Node.js backend, React frontend) |
| **License** | MPL 2.0 |
| **Latest version** | v1.x (2024-2025) |
| **Managed offering** | Logto Cloud |

**Description**

Logto is a modern, developer-friendly OIDC-native identity platform. It
emphasizes developer experience, beautiful out-of-the-box UI, and a clean
architecture. It positions itself as an open-source Auth0 alternative.

**Key features**

- Certified OpenID Connect provider
- Beautiful, customizable sign-in experience (pre-built UI)
- Social sign-in (30+ connectors)
- Passwordless: magic link, SMS, email OTP
- MFA: TOTP, WebAuthn, backup codes
- Machine-to-machine (M2M) authentication
- Organizations (multi-tenancy for B2B SaaS) -- added in 2024
- Role-based access control
- Audit logs
- User management console
- Webhooks
- Custom JWT claims
- Management API
- SDKs: Next.js, React, Vue, Express, Go, Python, etc.

**Architecture**

Logto runs as a Node.js (TypeScript) application with a React-based admin
console. It uses PostgreSQL as the sole database backend. The OIDC core is
built on the `oidc-provider` npm package (certified implementation).
Deployment: Docker, Docker Compose, or Logto Cloud.

**Differentiators**

- TypeScript end-to-end (appealing to JS/TS-heavy teams)
- Opinionated but extensible (less configuration complexity than Keycloak)
- Modern UI/UX out of the box
- Active, responsive maintainer team
- MPL 2.0 license (permissive with copyleft for modified files)

---

#### SuperTokens (Self-hosted Auth0 Alternative)

| Attribute | Value |
|-----------|-------|
| **Website** | https://supertokens.com |
| **GitHub** | https://github.com/supertokens/supertokens-core |
| **Stars** | ~13,500 |
| **Language** | Java (core), Node.js/Python/Go (SDKs) |
| **License** | Apache 2.0 (core), ELv2 (some features) |
| **Latest version** | v9.x (2024-2025) |
| **Managed offering** | SuperTokens Managed Service |

**Description**

SuperTokens is a self-hosted authentication solution designed as a drop-in
Auth0 replacement. It provides pre-built auth recipes (login methods) that
can be composed and customized. The core is written in Java; frontend and
backend SDKs are provided for popular frameworks.

**Key features**

- Auth recipes: email/password, passwordless (magic link, OTP), social login,
  phone/email OTP
- Session management (rotating refresh tokens, anti-CSRF)
- Pre-built UI components (React, React Native)
- Multi-tenancy (2024)
- Account linking (multiple auth methods per user)
- User roles and permissions
- MFA: TOTP, phone OTP, email OTP
- Dashboard for user management
- Override architecture for customization

**Architecture**

SuperTokens Core is a Java HTTP service that handles authentication logic and
stores data in PostgreSQL or MySQL. It exposes a private API consumed by
backend SDKs (Node.js, Python, Go). Backend SDKs expose middleware that
integrates with your application framework (Express, FastAPI, Flask, Go HTTP,
etc.). Frontend SDKs (React, React Native, vanilla JS) provide pre-built
UI components.

```
Frontend SDK <-> Backend SDK (middleware) <-> SuperTokens Core <-> Database
```

**Differentiators**

- Recipe-based architecture: each auth method is a composable recipe
- Override system: customize any behavior without forking
- Tight framework integration (not just OIDC redirect)
- Self-hosted by default (not cloud-first)
- Apache 2.0 core ensures no vendor lock-in

---

#### Hanko (Passkey-first, WebAuthn Native)

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.hanko.io |
| **GitHub** | https://github.com/teamhanko/hanko |
| **Stars** | ~7,000 |
| **Language** | Go (backend), TypeScript (web components) |
| **License** | AGPL 3.0 (Community), Commercial (Enterprise) |
| **Latest version** | v1.x (2024-2025) |
| **Managed offering** | Hanko Cloud |

**Description**

Hanko is a passkey-first authentication platform. Unlike most IAM solutions
that bolt passkey support onto existing password flows, Hanko was designed
from the ground up for passwordless/passkey authentication. It provides
drop-in web components for passkey registration and login.

**Key features**

- Passkey-first authentication (WebAuthn/FIDO2)
- Passkey login and registration web components (`<hanko-auth>`, `<hanko-profile>`)
- Passcode fallback (email OTP for devices without passkey support)
- OAuth social login
- User management API
- Customizable UI via CSS custom properties
- JWT session tokens
- Webhook events
- Multi-tenancy (enterprise)
- SAML enterprise SSO (enterprise)

**Architecture**

Hanko backend is a Go application exposing a REST API. It uses PostgreSQL as
the database. Frontend integration is via Web Components (framework-agnostic)
that handle the entire passkey registration/authentication UX. JWTs are
issued after authentication.

**Differentiators**

- Passkey-native design (not an afterthought)
- Drop-in Web Components (minimal frontend code)
- Strong alignment with FIDO Alliance direction
- Focus on user experience for passwordless flows
- Growing community around passkey-first approach

---

#### Authelia

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.authelia.com |
| **GitHub** | https://github.com/authelia/authelia |
| **Stars** | ~22,500 |
| **Language** | Go (backend), TypeScript (frontend) |
| **License** | Apache 2.0 |
| **Latest version** | v4.38.x (2024-2025) |
| **Contributors** | ~150 |

**Description**

Authelia is an authentication and authorization server that provides 2FA and
SSO for applications via a reverse proxy. It is designed to work behind
reverse proxies like Nginx, Traefik, HAProxy, and Caddy. Authelia is
particularly popular in homelab and self-hosted infrastructure communities.

**Key features**

- Single sign-on (SSO) via OpenID Connect 1.0 provider
- Multi-factor authentication: TOTP, WebAuthn/FIDO2, Duo Push
- Access control policies (bypass, one_factor, two_factor per resource)
- Password reset / self-service
- User database: file-based (YAML) or LDAP backend
- Session storage: in-memory, Redis, PostgreSQL, MySQL
- Notification: SMTP, file-based
- Regulation: brute force protection / account lockout
- Themes and branding
- High availability deployment with Redis and PostgreSQL

**Architecture**

Authelia sits between a reverse proxy and upstream applications. The proxy
forwards authentication decisions to Authelia, which checks session state
and applies access policies. If unauthenticated, the user is redirected to
Authelia's portal for login/2FA. Once authenticated, the session cookie
allows pass-through.

```
Client -> Reverse Proxy -> (auth check) -> Authelia -> (verified) -> Upstream App
```

**Use cases**

- Protecting self-hosted applications (Nextcloud, Gitea, Grafana, etc.)
- Adding SSO and 2FA to applications that lack native support
- Homelab and small business infrastructure
- Internal tools and dashboards

**Differentiators**

- Proxy-first design (works with existing reverse proxy infrastructure)
- Lightweight and easy to deploy
- Very popular in self-hosted / homelab communities
- Does not aim to be a full CIAM platform (focused scope)
- Mature access control policy engine

---

#### Authentik

| Attribute | Value |
|-----------|-------|
| **Website** | https://goauthentik.io |
| **GitHub** | https://github.com/goauthentik/authentik |
| **Stars** | ~14,500 |
| **Language** | Python (Django backend), TypeScript (Lit frontend) |
| **License** | SSPL (source-available, Authentik Security license) |
| **Latest version** | 2024.x / 2025.x (calendar versioning) |
| **Company** | Authentik Security Inc. |

**Description**

Authentik is an identity provider focused on flexibility and versatility.
It supports a wide range of protocols and provides a powerful flow engine
that allows administrators to build custom authentication and enrollment
workflows visually. It positions itself as a comprehensive IAM solution for
self-hosted environments.

**Key features**

- Protocol support: OAuth 2.0, OIDC, SAML 2.0, LDAP (as a provider),
  SCIM (provisioning), RADIUS
- Flow engine: visual, drag-and-drop workflow designer for authentication,
  enrollment, recovery, and authorization flows
- Application proxy: forward auth and reverse proxy mode
- Outpost architecture: deploy protocol providers (LDAP, proxy, RADIUS)
  as separate containers near your applications
- User management with groups, roles, and attributes
- MFA: TOTP, WebAuthn, Duo, SMS, static tokens
- Source integrations: LDAP, SAML, OAuth/OIDC, Plex
- Event logging and audit trail
- Branding and customization
- Blueprints: declarative configuration-as-code

**Architecture**

Authentik is a Django (Python) application with a Lit-based web frontend.
It uses PostgreSQL for data storage and Redis for caching/task queuing.
The "outpost" model allows protocol providers (LDAP, proxy, RADIUS) to run
as separate containers that connect back to the core authentik instance,
enabling flexible deployment topologies.

Components:
- Core server (Django): identity management, flow engine, admin UI
- Worker (Celery): background tasks, SCIM sync
- Outposts: LDAP provider, proxy provider, RADIUS provider (Go-based)

**Differentiators**

- Visual flow engine (unique among OSS IAM)
- LDAP provider (acts as an LDAP server, fronting its user directory)
- Outpost architecture for distributed deployment
- Very active development and community
- Appeals to self-hosted / homelab power users AND small enterprises
- Calendar-based versioning with regular releases

**Note on licensing**

Authentik uses SSPL (Server Side Public License), similar to MongoDB. This
means it is source-available but not considered "open source" by OSI.
Commercial use as a service requires a commercial license.

---

#### Zitadel

| Attribute | Value |
|-----------|-------|
| **Website** | https://zitadel.com |
| **GitHub** | https://github.com/zitadel/zitadel |
| **Stars** | ~9,500 |
| **Language** | Go (backend), Angular (console) |
| **License** | Apache 2.0 |
| **Latest version** | v2.x (2024-2025) |
| **Company** | Zitadel (Switzerland) |
| **Managed offering** | Zitadel Cloud |

**Description**

Zitadel is a cloud-native identity management platform built with event
sourcing at its core. It provides multi-tenancy, delegated access management,
and a clean API. It was designed from the ground up for B2B SaaS and
multi-tenant scenarios.

**Key features**

- Multi-tenancy: instances, organizations, projects, applications
- Event-sourced architecture (full audit trail by design)
- OIDC and SAML 2.0 provider
- Passkey/WebAuthn support
- Passwordless authentication
- MFA: TOTP, WebAuthn, OTP (email/SMS)
- Machine-to-machine authentication (personal access tokens, service users)
- Actions: custom serverless logic on auth events (JavaScript)
- Branding per organization
- RBAC with delegated management
- Self-service console for organizations
- SCIM provisioning (2024)
- Custom metadata on users and organizations
- Management API (gRPC and REST)

**Architecture**

Zitadel is built on event sourcing and CQRS (Command Query Responsibility
Segregation). Every change is stored as an immutable event, providing a
complete audit trail. The system uses:

- CockroachDB or PostgreSQL as the event store
- Projections (read models) built from events for query performance
- Single Go binary deployment (no external cache or message queue needed)
- Embedded or external database

This architecture provides:
- Built-in audit log (it IS the data model)
- Point-in-time recovery and replay
- Simple deployment (single binary + database)

**Differentiators**

- Event-sourced architecture (unique in IAM space)
- True multi-tenancy with delegated management
- Swiss company (data sovereignty appeal)
- Single binary deployment (operational simplicity)
- Apache 2.0 license (truly open source)
- B2B SaaS focus

---

### IGA, PAM, and ITDR

---

#### IGA: Identity Governance and Administration

##### SailPoint

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.sailpoint.com |
| **Type** | Commercial (taken private by Thoma Bravo, 2024) |
| **Products** | SailPoint Identity Security Cloud (SaaS), IdentityIQ (on-prem) |
| **Market position** | Gartner Leader in IGA |

**Description**

SailPoint is the dominant vendor in Identity Governance and Administration
(IGA). It provides identity lifecycle management, access certifications,
access request workflows, separation of duties (SoD) enforcement, and
identity analytics.

**Key capabilities**

- Identity lifecycle management (joiner/mover/leaver automation)
- Access certifications (periodic reviews of who has access to what)
- Access request and approval workflows
- Separation of duties (SoD) policy enforcement
- Role mining and role management
- Provisioning connectors (200+ out of the box)
- AI-driven recommendations (Identity AI):
  - Access outlier detection
  - Role discovery and optimization
  - Recommendation engine for access reviews
- Data access governance (DAG) -- visibility into unstructured data access
- Non-employee identity management
- Cloud infrastructure entitlement management (CIEM)

**Architecture**

- SailPoint Identity Security Cloud (ISC): multi-tenant SaaS, with
  Virtual Appliance (VA) for on-prem connector connectivity
- IdentityIQ: on-premises Java application (Tomcat + RDBMS)
- Connectivity: SaaS Connectivity Framework + legacy connectors via VA
- APIs: REST, Event Triggers (webhooks), SailPoint CLI

**Recent developments (2024-2025)**

- Thoma Bravo acquisition completed (2024, ~$6.9B)
- Continued AI/ML investment in identity security posture
- Data Access Governance expanded
- Atlas platform (underlying SaaS infrastructure) matured
- Non-employee risk management enhanced

##### Saviynt

| Attribute | Value |
|-----------|-------|
| **Website** | https://saviynt.com |
| **Type** | Commercial SaaS |
| **Products** | Enterprise Identity Cloud (EIC) |
| **Market position** | Gartner Leader in IGA (since 2023) |

**Description**

Saviynt is a cloud-native IGA platform that has rapidly gained market share.
It converges IGA, Cloud PAM, Application Access Governance, and Third-Party
Access Governance into a single platform.

**Key capabilities**

- Identity lifecycle management
- Access certifications and reviews
- Access request workflows
- Cloud Privileged Access Management (CPAM)
- Application access governance (AAG)
- Segregation of duties (SoD)
- Identity analytics and intelligence
- 500+ connectors (including deep ERP connectors for SAP, Oracle, Workday)
- Data access governance
- Third-party/external identity management
- Control Exchange (pre-built compliance controls for SOX, HIPAA, etc.)

**Architecture**

- Cloud-native, multi-tenant SaaS (AWS-based)
- Enterprise Identity Cloud (EIC) platform
- Connectivity via Saviynt connectors + Identity Warehouse
- Real-time cloud event monitoring
- REST APIs, webhooks, SCIM

**Differentiators vs. SailPoint**

- Born in the cloud (no legacy on-prem product to maintain)
- Converged IGA + CPAM platform
- Strong ERP access governance (SAP fine-grained authorization objects)
- Generally considered more modern UX
- Aggressive pricing vs. SailPoint

---

#### PAM: Privileged Access Management

##### CyberArk

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.cyberark.com |
| **Type** | Commercial (public, NASDAQ: CYBR) |
| **Market position** | Gartner Leader in PAM, #1 market share |
| **Revenue** | ~$1B ARR (2024) |

**Description**

CyberArk is the dominant PAM vendor, providing privileged credential
management, session isolation/monitoring, and least-privilege enforcement.
It has expanded into identity security broadly with acquisitions of Idaptive
(SSO/MFA) and Venafi (machine identity).

**Key products**

- Privilege Cloud (SaaS PAM):
  - Credential vaulting and rotation
  - Session isolation and recording
  - Just-in-time (JIT) access
  - Privileged threat analytics
- Endpoint Privilege Manager (EPM):
  - Least privilege enforcement on endpoints
  - Application control
  - Credential theft protection
- Secrets Hub / Conjur:
  - Secrets management for DevOps/CI-CD
  - Kubernetes secrets injection
  - Conjur (open-source secrets management)
- CyberArk Identity (formerly Idaptive):
  - Workforce SSO and adaptive MFA
  - User behavior analytics
- CyberArk Secure Cloud Access:
  - JIT access to cloud consoles (AWS, Azure, GCP)
  - Zero standing privileges
- Venafi (acquired 2024):
  - Machine identity management
  - TLS certificate lifecycle
  - Code signing
  - SSH key management

**Architecture**

- Privilege Cloud: SaaS with Connector (Privilege Cloud Connector) for
  on-prem target connectivity
- Self-hosted: Digital Vault (hardened Windows server), Central Policy
  Manager (CPM), Privileged Session Manager (PSM)
- Secrets management: Conjur (containers), Credential Providers (agents)

##### Delinea (formerly Thycotic + Centrify)

| Attribute | Value |
|-----------|-------|
| **Website** | https://delinea.com |
| **Type** | Commercial (private, TPG Capital) |
| **Market position** | Gartner Leader in PAM |

**Key products**

- Secret Server: credential vaulting and management
- Server PAM: least privilege on servers (Linux/Windows)
- Privilege Manager: endpoint privilege management
- Connection Manager: session management
- DevOps Secrets Vault: cloud-native secrets management
- Platform: unified SaaS PAM (launched 2024)

**Differentiators**

- Considered easier to deploy and use vs. CyberArk
- Competitive pricing
- Unified platform strategy (converging products)
- Strong in mid-market

##### BeyondTrust

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.beyondtrust.com |
| **Type** | Commercial (private, Francisco Partners) |
| **Market position** | Gartner Leader in PAM |

**Key products**

- Privileged Remote Access: secure vendor/remote access with session recording
- Password Safe: enterprise credential management
- Endpoint Privilege Management: least privilege on Windows, Mac, Linux
- Cloud Security Management: multi-cloud entitlement visibility
- Identity Security Insights: identity-centric threat detection
- DevOps Secrets Safe: secrets management

**Differentiators**

- Strong remote access use case (VPN-less privileged access)
- Endpoint privilege management leadership
- Unified platform approach
- Acquired Bomgar (remote access), merged capabilities

##### HashiCorp Vault

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.vaultproject.io |
| **GitHub** | https://github.com/hashicorp/vault |
| **Stars** | ~31,500 |
| **Language** | Go |
| **License** | BSL 1.1 (changed from MPL 2.0 in Aug 2023) |
| **Latest version** | v1.18.x (2024-2025) |
| **Managed offering** | HCP Vault (HashiCorp Cloud Platform) |
| **Acquisition** | IBM acquired HashiCorp (2024, ~$6.4B) |

**Description**

HashiCorp Vault is the most widely used secrets management solution,
particularly in cloud-native and DevOps environments. It manages secrets,
encryption keys, and provides identity-based access to sensitive data.

**Key features**

- Secret engines: KV, databases (dynamic credentials), PKI, SSH, transit
  (encryption as a service), TOTP, cloud provider secrets (AWS, Azure, GCP)
- Authentication methods: token, LDAP, OIDC/JWT, Kubernetes, AppRole,
  cloud IAM (AWS, Azure, GCP), TLS certificates, GitHub
- Dynamic secrets: generate on-demand, short-lived credentials for databases,
  cloud providers, etc.
- PKI secrets engine: private CA, certificate issuance and renewal
- Transit engine: encryption as a service (encrypt/decrypt/sign/verify)
- Namespaces: multi-tenancy (Enterprise)
- Sentinel policies (Enterprise): policy-as-code for Vault operations
- Replication: performance and disaster recovery (Enterprise)
- Auto-unseal: AWS KMS, Azure Key Vault, GCP Cloud KMS, HSM (PKCS#11)
- Vault Agent / Vault Proxy: sidecar for automatic token renewal and
  secret caching
- Vault Secrets Operator (VSO): Kubernetes operator for syncing secrets
- HCP Vault Secrets: managed secrets-as-a-service (simpler than full Vault)
- HCP Vault Radar: secret scanning and detection

**Architecture**

Vault uses a client-server architecture:
- Server: stateless, stores encrypted data in a configurable storage backend
  (Integrated Raft storage, Consul, S3, DynamoDB, etc.)
- Barrier: all data is encrypted before leaving the server
- Seal/Unseal mechanism: master key split via Shamir's Secret Sharing or
  auto-unseal
- HA: active/standby with automatic failover (Raft or external)
- Audit: every operation logged to configured audit devices

**License change and IBM acquisition**

- License changed from MPL 2.0 to BSL 1.1 (Aug 2023), restricting competitive
  SaaS usage. This led to the OpenBao fork (Linux Foundation).
- IBM acquired HashiCorp in 2024 for ~$6.4B. Impact on Vault's direction
  and licensing remains to be seen.

**OpenBao (community fork)**

| Attribute | Value |
|-----------|-------|
| **GitHub** | https://github.com/openbao/openbao |
| **Stars** | ~3,500 |
| **License** | MPL 2.0 |
| **Status** | Linux Foundation project, active development |

OpenBao forked from Vault at v1.14 before the BSL license change. It aims
to be a community-driven, truly open-source secrets management solution.
Early but growing, with backing from IBM competitors and cloud providers
concerned about BSL licensing.

---

#### ITDR: Identity Threat Detection and Response

ITDR is a relatively new security category (Gartner coined the term in 2022)
focused on detecting and responding to identity-based attacks. It addresses the
reality that identity is now the #1 attack vector, with credential theft,
privilege escalation, and lateral movement being primary techniques.

##### CrowdStrike (Falcon Identity Threat Detection)

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.crowdstrike.com |
| **Product** | Falcon Identity Threat Detection (formerly Preempt Security, acquired 2020) |
| **Type** | Commercial SaaS (part of Falcon platform) |

**Capabilities**

- Real-time Active Directory threat detection
- Lateral movement detection and prevention
- Identity-based attack detection (Pass-the-Hash, Golden Ticket, DCSync, etc.)
- Conditional access policies based on identity risk
- Identity hygiene assessment (stale accounts, excessive privileges)
- Integration with CrowdStrike Falcon XDR for unified threat response
- AD object change monitoring

##### Silverfort

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.silverfort.com |
| **Type** | Commercial (raised $116M Series D, 2024) |
| **Differentiator** | Agentless, proxyless MFA and identity security |

**Capabilities**

- Agentless MFA for any resource (including legacy systems, mainframes,
  OT/IoT, file shares, command-line tools)
- Identity threat detection: compromised credentials, lateral movement,
  service account abuse
- Service account discovery and protection (automated discovery of all
  service accounts, behavioral baselining)
- Identity firewall: real-time blocking of unauthorized authentication
- Risk-based authentication (risk engine evaluates each access attempt)
- AD bridge: extend modern identity security to non-web resources
- Integration: sits as a "virtual layer" above AD, analyzing all Kerberos
  and NTLM authentication without requiring agents or proxies

**Architecture**

Silverfort deploys as a lightweight integration with Active Directory domain
controllers (no agents on endpoints, no proxies in line). It intercepts
authentication decisions at the directory level, evaluates risk, and can
enforce MFA or block access in real time. This is architecturally unique --
most ITDR solutions require endpoint agents or network taps.

##### Microsoft Entra ID Protection + ITDR

| Attribute | Value |
|-----------|-------|
| **Products** | Entra ID Protection, Microsoft Defender for Identity |

**Capabilities**

- Entra ID Protection:
  - Risk-based Conditional Access (sign-in risk, user risk)
  - Leaked credential detection
  - Anomalous sign-in detection (unfamiliar location, atypical travel, etc.)
  - Risky user remediation (forced password reset, MFA challenge)
  - Risk events API for SIEM integration

- Microsoft Defender for Identity (formerly Azure ATP):
  - On-premises Active Directory monitoring
  - LDAP and Kerberos attack detection (Pass-the-Hash, Pass-the-Ticket,
    Golden Ticket, DCShadow, etc.)
  - Lateral movement path detection
  - Honeytoken accounts
  - Entity behavior analytics
  - Integration with Microsoft 365 Defender (XDR)

**Differentiator**

Native integration across the Microsoft ecosystem (Entra ID, Defender XDR,
Sentinel SIEM, Intune) provides a unified identity security posture for
Microsoft-centric environments.

---

### Directory Services

---

#### FreeIPA

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.freeipa.org |
| **GitHub** | https://github.com/freeipa/freeipa (mirrors on Pagure) |
| **Stars** | ~1,200 (GitHub mirror) |
| **Language** | Python, C |
| **License** | GPL 3.0 |
| **Latest version** | 4.12.x (2024) |
| **Upstream of** | Red Hat Identity Management (IdM) |

**Description**

FreeIPA is an integrated identity management solution combining LDAP directory
(389 DS), Kerberos KDC (MIT Kerberos), DNS, NTP, and certificate management
(Dogtag CA). It is the upstream project for Red Hat Identity Management (IdM),
included in RHEL.

**Key features**

- Centralized authentication (Kerberos) and authorization
- LDAP directory (389 Directory Server) for identity storage
- Certificate authority (Dogtag) for PKI
- DNS management (BIND integration)
- Host-based access control (HBAC)
- Sudo rule centralization
- SELinux user mapping
- Trust relationships with Active Directory (cross-realm Kerberos)
- Web UI and CLI (`ipa` command)
- Multi-master replication
- OTP authentication support

**Architecture**

FreeIPA is a Linux-centric identity management system that bundles:
- 389 Directory Server (LDAP)
- MIT Kerberos 5 KDC
- Dogtag Certificate System (CA, RA)
- BIND DNS with automatic record management
- SSSD (System Security Services Daemon) on clients

Deployment: typically 2+ replicas for HA. Clients use SSSD to authenticate
against FreeIPA. AD trust enables FreeIPA users and AD users to access
resources in either domain.

**Use cases**

- Linux/Unix identity management (the "Active Directory for Linux")
- Hybrid environments needing Linux + AD coexistence
- Certificate management for infrastructure
- Replacing NIS (Network Information Service)

#### 389 Directory Server

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.port389.org |
| **GitHub** | https://github.com/389ds/389-ds-base |
| **Stars** | ~300 |
| **Language** | C, Rust (increasing) |
| **License** | GPL 2.0+ |
| **Latest version** | 3.x (2024-2025) |
| **Upstream of** | Red Hat Directory Server |

**Description**

389 Directory Server is an enterprise-grade LDAPv3 directory server. It is the
LDAP backend used by FreeIPA and Red Hat Identity Management. It is one of the
most performant and feature-rich open-source LDAP implementations.

**Key features**

- Full LDAPv3 compliance
- Multi-supplier replication (formerly multi-master)
- Content synchronization (syncrepl)
- MemberOf plugin (automatic group membership tracking)
- Referential integrity
- Attribute uniqueness
- DNA (Distributed Numeric Assignment) plugin
- Access control information (ACI) model
- TLS/STARTTLS support
- Password policy with complexity, history, lockout
- Rust-based plugins (ongoing rewrite of performance-critical components)
- Online configuration (cn=config)
- Cockpit web management UI (dscontainer)
- Container-native deployment
- Cloud-native improvements (v3.x)

**Comparison with OpenDJ**

Both are descendants of Sun's Directory Server. 389 DS is C-based (with
growing Rust), while OpenDJ is Java-based. 389 DS is more common in Red Hat
ecosystems; OpenDJ in ForgeRock/OIP deployments. Both support multi-master
replication and are production-grade.

---

#### Ping Identity (Current State)

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.pingidentity.com |
| **Type** | Commercial (private, Thoma Bravo) |
| **Merger** | Ping Identity + ForgeRock merged (2023) |
| **Market position** | Gartner Leader in Access Management |

**Description**

Ping Identity merged with ForgeRock in 2023 (both owned by Thoma Bravo) to
create a comprehensive identity platform. The combined entity offers workforce
IAM, customer IAM, identity governance, and directory services.

**Key products (post-merger)**

- **PingOne Advanced Identity Cloud** (formerly ForgeRock Identity Cloud):
  Cloud-native IAM platform, the strategic SaaS offering going forward.
  Based on ForgeRock's AM/IDM/DS stack.
- **PingFederate**: On-premises federation server (SAML, OIDC, WS-Federation).
  Mature, widely deployed in large enterprises.
- **PingAccess**: API security and access management gateway.
- **PingDirectory**: LDAPv3 directory server (high-performance, derived from
  a different Sun DS lineage than OpenDJ/389).
- **PingOne DaVinci**: No-code identity orchestration (visual flow builder).
- **PingOne Protect**: Threat detection and risk management.
- **PingOne Verify**: Identity verification and proofing.
- **PingOne Authorize**: Dynamic authorization (fine-grained, policy-based).
- **PingOne MFA**: Cloud MFA service.
- **PingOne SSO**: Cloud SSO.
- **PingOne Neo**: Decentralized identity / verifiable credentials.

**Architecture**

The strategic direction is PingOne Advanced Identity Cloud (AIC), which is the
ForgeRock Identity Cloud rebranded. It runs ForgeRock AM (access management),
IDM (identity management), and DS (directory server) as a managed,
multi-tenant SaaS. On-premises products (PingFederate, PingAccess,
PingDirectory) continue to be supported for customers who need them.

**Market significance**

- The Ping + ForgeRock merger created the most comprehensive independent
  identity platform, competing directly with Okta and Microsoft Entra
- Combined ~2,700 enterprise customers
- Strong in large enterprise, financial services, healthcare, government
- ForgeRock's open-source heritage (OpenAM, OpenDJ, OpenIDM, OpenIG) lives
  on in the OIP and Wren Security community forks (covered in this workspace)

**Relevance to this workspace**

The repos in this workspace (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF) are the
open-source community forks of what is now Ping Identity's commercial product
suite. Understanding the commercial evolution helps contextualize the
open-source projects' positioning:

| Open Source (this workspace) | Commercial (Ping) |
|------------------------------|-------------------|
| OpenAM (OIP) / WrenAM | PingOne AIC (AM) |
| OpenDJ (OIP) / Wren:DS | PingDirectory |
| OpenIDM (OIP) / Wren:IDM | PingOne AIC (IDM) |
| OpenIG (OIP) / Wren:IG | PingGateway |
| OpenICF (OIP) / Wren:ICF | ICF (embedded in IDM) |

---

### Standards and Patterns

---

#### OPA/Rego (Policy Engine)

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.openpolicyagent.org |
| **GitHub** | https://github.com/open-policy-agent/opa |
| **Stars** | ~10,000 |
| **Language** | Go |
| **License** | Apache 2.0 |
| **CNCF status** | Graduated (2021) |
| **Latest version** | v1.x (2024-2025) |
| **Policy language** | Rego |

**Description**

Open Policy Agent (OPA) is a general-purpose policy engine that decouples
policy decisions from application code. Policies are written in Rego, a
declarative language designed for expressing complex policies over structured
data. OPA is the de facto standard for Kubernetes admission control and is
widely adopted for API authorization, infrastructure policy, and data
filtering.

**Key capabilities**

- General-purpose: works for any domain (Kubernetes, APIs, Terraform, SQL,
  microservices, CI/CD, etc.)
- Rego language: pattern matching, rule composition, comprehensions,
  built-in functions for JWT, HTTP, crypto, etc.
- Bundle API: distribute policies as versioned bundles
- Decision logs: record every policy decision for audit
- Status API: monitoring OPA health and policy status
- Partial evaluation: pre-compute policy decisions for performance
- WebAssembly compilation: compile Rego to Wasm for embedding in any language
- REST API: query OPA as a sidecar or centralized service

**Ecosystem**

- Gatekeeper: OPA for Kubernetes admission control (Constraint Framework)
- Conftest: OPA for structured data file testing (YAML, JSON, HCL, Dockerfile)
- Styra DAS: enterprise OPA management (commercial, by OPA creators)
- Libraries: SDKs for Go, Java, JavaScript, Python, Rust, C#

**Rego language characteristics**

```rego
# Example: allow if user has required role
allow if {
    some role in input.user.roles
    role == data.required_roles[input.action]
}
```

- Declarative (what, not how)
- Set/object comprehensions
- Rule chaining and incremental definition
- No side effects (pure evaluation)
- OPA v1.0 (2024) introduced breaking changes to Rego syntax for consistency

#### Cedar (AWS Policy Language)

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.cedarpolicy.com |
| **GitHub** | https://github.com/cedar-policy/cedar |
| **Stars** | ~4,200 |
| **Language** | Rust |
| **License** | Apache 2.0 |
| **Created by** | AWS (Amazon) |
| **First release** | Open-sourced May 2023 |
| **Latest version** | v4.x (2024-2025) |

**Description**

Cedar is a policy language and evaluation engine developed by AWS. It powers
Amazon Verified Permissions (AVP) and is also used in AWS IAM Identity Center.
Cedar is designed specifically for application-level authorization with an
emphasis on analyzability -- policies can be formally verified for correctness.

**Key capabilities**

- Purpose-built for authorization (unlike OPA which is general-purpose)
- Static analysis: policies can be analyzed before deployment to detect
  conflicts, redundancies, and verify properties
- Formal verification: Cedar has Lean 4 proofs of soundness (authorization
  decisions are provably correct)
- Entity-based model: principals, actions, resources, context
- Policy language: `permit` and `forbid` policies with conditions
- Schema validation: policies are validated against a schema defining
  entity types, actions, and relationships
- Hierarchical entities: groups, organizational units, resource containers

**Cedar policy example**

```cedar
permit (
    principal in Group::"engineering",
    action == Action::"read",
    resource in Folder::"project-x"
) when {
    context.ip_address.isInRange(ip("10.0.0.0/8"))
};
```

**Architecture**

- Cedar engine: Rust library embeddable in any application
- Policy sets: collections of permit/forbid policies evaluated together
- Entity store: hierarchical graph of principals and resources
- Amazon Verified Permissions: managed service wrapping Cedar in AWS

**Cedar vs. OPA/Rego**

| Dimension | Cedar | OPA/Rego |
|-----------|-------|----------|
| Scope | Authorization-specific | General-purpose policy |
| Language | Cedar (purpose-built) | Rego (general-purpose) |
| Analyzability | Formal verification | Limited static analysis |
| Entity model | Built-in hierarchical | User-defined data model |
| Ecosystem | AWS-centric (AVP) | CNCF, Kubernetes-centric |
| Maturity | Young (2023) | Mature (CNCF Graduated 2021) |

---

#### SCIM 2.0 (Provisioning Standard)

| Attribute | Value |
|-----------|-------|
| **Specification** | RFC 7642, 7643, 7644 (IETF, 2015) |
| **Full name** | System for Cross-domain Identity Management |
| **Version** | 2.0 |
| **Status** | Widely adopted (2024-2025) |

**Description**

SCIM 2.0 is the dominant standard for automated user provisioning and
deprovisioning between identity providers and applications. It defines a
REST API schema for representing users and groups, enabling automated
lifecycle management.

**Key features**

- Standardized user and group schemas (Core schema + Enterprise extension)
- RESTful API: CRUD operations on /Users and /Groups endpoints
- Bulk operations for large-scale provisioning
- Filtering, sorting, pagination
- PATCH operations for partial updates
- Service provider configuration discovery
- Schema discovery endpoint

**Adoption status (2024-2025)**

- SCIM is now a baseline requirement for enterprise SaaS applications
- Major adopters: Microsoft Entra ID, Okta, SailPoint, Saviynt, Google
  Workspace, Slack, Salesforce, GitHub Enterprise, Atlassian, Zoom,
  Snowflake, Datadog, and hundreds more
- Keycloak added SCIM support via extensions; Authentik has native SCIM
- Zitadel added SCIM provisioning in 2024
- AWS IAM Identity Center uses SCIM for user/group provisioning to AWS accounts

**Limitations and gaps**

- No standard for entitlements/roles (only users and groups in core spec)
- Limited support for custom schemas in practice
- No event/webhook model (pull-based polling for changes)
- SCIM 2.1 / next-generation work in IETF is slow-moving
- Governance provisioning (access requests, certifications) is not in scope

**Practical considerations**

- Most IdPs implement SCIM as a push-based provisioner (IdP pushes changes
  to downstream apps)
- Quality of SCIM implementations varies significantly across vendors
- Testing: SCIM compliance test suites exist but adoption is inconsistent
- Common issues: partial PATCH support, inconsistent error handling,
  schema extension interoperability

---

#### Passkeys / WebAuthn (Enterprise Rollout)

| Attribute | Value |
|-----------|-------|
| **Specification** | W3C Web Authentication (WebAuthn) Level 3 |
| **Alliance** | FIDO Alliance |
| **Protocol** | FIDO2 (WebAuthn + CTAP2) |
| **Status** | Mainstream adoption (2024-2025) |

**Description**

Passkeys are FIDO2 credentials that replace passwords with cryptographic
key pairs. They use WebAuthn for browser/platform interaction and CTAP2 for
communicator-to-authenticator communication. Passkeys can be device-bound
(hardware security keys) or synced across devices (via cloud sync).

**Platform support (as of 2024-2025)**

| Platform | Synced passkeys | Device-bound | Status |
|----------|----------------|--------------|--------|
| Apple (iOS/macOS) | iCloud Keychain | Face ID/Touch ID | GA since iOS 16 / macOS Ventura |
| Google (Android/Chrome) | Google Password Manager | Fingerprint/PIN | GA since Android 14 |
| Microsoft (Windows) | Windows Hello | Windows Hello + security keys | GA since Windows 11 23H2 |
| Browser support | Chrome, Safari, Firefox, Edge | All major browsers | Universal |

**Enterprise adoption data**

- FIDO Alliance reported 15B+ accounts enabled for passkeys (late 2024)
- Google: 800M+ accounts using passkeys; passkey sign-ins 4x faster and
  more successful than password sign-ins
- Microsoft: passkey support rolled out across consumer and Entra accounts
- Enterprise deployments accelerating but slower than consumer:
  - Phishing-resistant auth mandates (e.g., US OMB M-22-09) drive adoption
  - NIST SP 800-63-4 (draft) recognizes passkeys as AAL2/AAL3
  - Challenges: device management, account recovery, cross-platform UX
    inconsistencies, organizational device policies

**Key developments (2024-2025)**

- Cross-device authentication (CDA): use phone as authenticator for desktop
  login (QR code + Bluetooth proximity)
- Passkey import/export: FIDO Alliance published specification for portable
  passkeys between providers (2024)
- Attestation and enterprise features: device-bound passkeys with enterprise
  attestation for regulated industries
- Conditional UI / autofill passkeys: browsers show passkeys in autofill
  suggestions, reducing friction
- Third-party passkey providers: 1Password, Bitwarden, Dashlane support
  synced passkeys as alternatives to platform-native sync

**Implementation in IAM platforms**

| Platform | Passkey support | Notes |
|----------|----------------|-------|
| Keycloak | Yes (v22+) | WebAuthn authenticator, passwordless flow |
| Auth0 | Yes (2024) | Database connections with passkey |
| Okta | Yes (2024) | Okta FastPass + passkeys |
| Entra ID | Yes (2024) | FIDO2 security keys + synced passkeys |
| Ory Kratos | Yes | WebAuthn MFA and passwordless |
| Hanko | Native | Passkey-first design |
| Zitadel | Yes | Passwordless via WebAuthn |
| Authentik | Yes | WebAuthn device enrollment |

---

#### SPIFFE/SPIRE (Workload Identity)

| Attribute | Value |
|-----------|-------|
| **Website** | https://spiffe.io |
| **GitHub** | https://github.com/spiffe/spire |
| **Stars** | ~1,800 (SPIRE) |
| **Language** | Go |
| **License** | Apache 2.0 |
| **CNCF status** | Graduated (2024) |
| **Latest version** | SPIRE v1.11.x (2024-2025) |

**Description**

SPIFFE (Secure Production Identity Framework for Everyone) defines a standard
for workload identity. SPIRE (SPIFFE Runtime Environment) is the reference
implementation. Together they provide cryptographically verifiable identity
to workloads in heterogeneous environments without relying on secrets.

**SPIFFE specification**

- **SPIFFE ID**: URI-based identity (`spiffe://trust-domain/path`)
- **SVID (SPIFFE Verifiable Identity Document)**:
  - X.509-SVID: X.509 certificate containing SPIFFE ID in SAN
  - JWT-SVID: JWT token containing SPIFFE ID in claims
- **Trust bundle**: set of root certificates for a trust domain
- **Workload API**: local API (Unix domain socket) for workloads to obtain
  SVIDs without managing secrets

**SPIRE architecture**

- **SPIRE Server**: central component that manages identity issuance and
  attestation policies. Issues SVIDs to attested workloads.
- **SPIRE Agent**: runs on each node, attests local workloads, exposes
  Workload API, caches SVIDs.
- **Attestation**: node attestation (proving the node is authorized) and
  workload attestation (proving the process is authorized).
  - Node attestors: AWS IID, Azure MSI, GCP IIT, Kubernetes, TPM, X.509
  - Workload attestors: Kubernetes, Docker, Unix PID, systemd

**Key capabilities**

- Automatic certificate rotation (short-lived certificates, no manual renewal)
- Cross-cluster and cross-cloud federation (trust bundle exchange)
- Integration with service meshes (Istio, Envoy, Linkerd)
- Integration with secrets managers (HashiCorp Vault)
- OIDC federation: SPIRE can issue JWTs federated with OIDC providers
- Nested SPIRE: hierarchical deployments for large organizations
- Kubernetes Workload Registrar: automatic registration of Kubernetes
  workloads

**Adoption (2024-2025)**

- CNCF Graduated (2024): signifies production readiness and broad adoption
- Used by: Bloomberg, ByteDance, Uber, Netflix, Square, Pinterest, HP,
  and others
- AWS IRSA (IAM Roles for Service Accounts) and EKS Pod Identity build on
  SPIFFE concepts
- Growing adoption in zero-trust network architectures
- Service mesh integration is a primary driver (Istio uses SPIFFE IDs
  natively for mTLS)
- SPIFFE integration in Vault, Consul, Envoy, Cilium

---

#### W3C Verifiable Credentials / DIDs (Decentralized Identity)

| Attribute | Value |
|-----------|-------|
| **Specifications** | W3C Verifiable Credentials Data Model v2.0 (2024), W3C DIDs v1.0 (2022) |
| **Status** | Standards finalized; adoption accelerating via regulation |
| **Key driver** | EU eIDAS 2.0 regulation (EUDIW mandate by 2026) |

**Description**

Verifiable Credentials (VCs) and Decentralized Identifiers (DIDs) form the
foundation of decentralized identity (also called self-sovereign identity or
SSI). VCs are tamper-evident digital credentials (like digital versions of
physical IDs, diplomas, certifications). DIDs are globally unique identifiers
that the holder controls, without dependence on a centralized registry.

**W3C Verifiable Credentials (VCs)**

- **VC Data Model v2.0** (W3C Recommendation, 2024):
  - Issuer issues a credential to a Holder about a Subject
  - Verifier verifies the credential's authenticity
  - JSON-LD or JWT/SD-JWT serialization formats
  - Selective disclosure: reveal only specific claims
  - Status lists: credential revocation/suspension checking
  - Multi-proof support
  - Securing mechanisms: Data Integrity Proofs, JWT (JWS), SD-JWT

- **Key concepts**:
  - **Issuer**: trusted entity that creates and signs credentials
  - **Holder**: entity that possesses and presents credentials (typically the user)
  - **Verifier**: entity that checks credential validity
  - **Credential**: set of claims about a subject, signed by the issuer
  - **Presentation**: packaged credential(s) presented by holder to verifier

**Decentralized Identifiers (DIDs)**

- **DID Core v1.0** (W3C Recommendation, 2022):
  - Format: `did:method:method-specific-id` (e.g., `did:web:example.com`)
  - DID Document: contains public keys, service endpoints, verification methods
  - DID Methods: 100+ methods registered (did:web, did:key, did:ion, did:ethr,
    did:jwk, etc.)
  - Resolution: DID -> DID Document via method-specific resolver
  - DID Controller: entity that can make changes to the DID Document

- **Practical DID methods (most adopted)**:
  - `did:web` - DNS-based, easiest to adopt, hosted at a web domain
  - `did:key` - self-contained, public key encoded in the identifier
  - `did:jwk` - JWK-based, simple key representation
  - `did:ion` - Bitcoin-anchored (Microsoft's implementation)
  - `did:ethr` - Ethereum-based

**EU eIDAS 2.0 and EUDIW**

The EU Digital Identity Regulation (eIDAS 2.0, adopted 2024) mandates that:
- All EU member states offer a European Digital Identity Wallet (EUDIW) to
  citizens by 2026
- Wallets must support VCs and DIDs
- Public services and regulated private services must accept wallet-based
  identity
- Architecture Reference Framework (ARF) specifies technical standards
- Large-Scale Pilots (LSPs) running 2023-2025: EWC, POTENTIAL, DC4EU, NOBID

**Key implementations and frameworks**

| Project | Description | Status |
|---------|-------------|--------|
| Walt.id | Kotlin/JVM SSI toolkit (VCs, DIDs, wallets) | Active, EU-focused |
| Sphereon | VC/DID platform, OID4VC support | Active |
| SpruceID | Rust-based DIDKit, SSX | Active |
| Microsoft Entra Verified ID | Commercial VC issuance/verification | GA |
| Ping One Neo | Commercial decentralized identity | GA |
| Hyperledger Aries | Agent framework for DID-based messaging | Active |
| Hyperledger AnonCreds | Privacy-preserving credentials (ZKP) | Active |

**OpenID for Verifiable Credentials (OID4VC)**

A suite of specs that use OpenID Connect patterns for VC issuance and
presentation, bridging the OIDC world with VCs:
- **OID4VCI**: OpenID for Verifiable Credential Issuance
- **OID4VP**: OpenID for Verifiable Presentations
- **SIOPv2**: Self-Issued OpenID Provider v2
- Status: nearing final drafts at OpenID Foundation (2024-2025)
- Adopted by EU ARF as the credential exchange protocol for EUDIW

**Adoption assessment**

- **Government/regulated**: Strong momentum (EU mandate, US state mobile
  driver's licenses, ICAO Digital Travel Credentials)
- **Enterprise**: Early stage. Use cases: employee credential verification,
  supply chain attestation, professional certifications
- **Consumer**: Limited outside government ID wallets. User experience and
  recovery challenges remain.
- **Technical maturity**: Standards are ready. Tooling and interoperability
  are still maturing. The "wallet wars" (platform wallets vs. standalone)
  are ongoing.

---

## Appendix: Competitive Landscape Summary

### OSS IAM Feature Matrix

| Feature | Keycloak | Ory | Authentik | Zitadel | Logto | Casdoor | Authelia | SuperTokens | Hanko |
|---------|----------|-----|-----------|---------|-------|---------|----------|-------------|-------|
| OIDC Provider | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | No |
| SAML IdP | Yes | No | Yes | Yes | No | Yes | No | No | No |
| LDAP Provider | No | No | Yes | No | No | Yes | No | No | No |
| SCIM | Ext | No | Yes | Yes | No | No | No | No | No |
| WebAuthn/Passkeys | Yes | Yes | Yes | Yes | Yes | No | Yes | No | Yes |
| MFA | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Passkey |
| Multi-tenancy | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes | Ent |
| Visual flow editor | No | No | Yes | No | No | No | No | No | No |
| Event sourcing | No | No | No | Yes | No | No | No | No | No |
| Self-service UI | Yes | Ref | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| License | Apache | Apache | SSPL | Apache | MPL | Apache | Apache | Apache/ELv2 | AGPL |
| Language | Java | Go | Python | Go | TS | Go | Go | Java | Go |

**Legend**: Ext = via extension, Ref = reference UI provided, Ent = enterprise only

### Market Segments

```
                    ┌─────────────────────────────────────────┐
                    │           Identity Security             │
                    │                                         │
    ┌───────────┐   │   ┌──────┐  ┌──────┐  ┌──────┐        │
    │  CIAM     │   │   │ IGA  │  │ PAM  │  │ ITDR │        │
    │  (B2C)    │   │   │      │  │      │  │      │        │
    │           │   │   └──────┘  └──────┘  └──────┘        │
    │ Auth0     │   │                                         │
    │ Cognito   │   │   ┌──────────────────────────────┐     │
    │ Entra Ext │   │   │    Workforce IAM (B2E)       │     │
    │ Keycloak  │   │   │                              │     │
    │ Logto     │   │   │ Okta WIC, Entra ID, Ping,    │     │
    │ SuperTkns │   │   │ Keycloak, Ory                │     │
    │ Hanko     │   │   └──────────────────────────────┘     │
    └───────────┘   │                                         │
                    │   ┌──────────────────────────────┐     │
                    │   │    Directory Services         │     │
                    │   │ Entra ID, AD, OpenDJ, 389 DS, │     │
                    │   │ PingDirectory, FreeIPA        │     │
                    │   └──────────────────────────────┘     │
                    │                                         │
                    │   ┌──────────────────────────────┐     │
                    │   │    Policy & Authorization     │     │
                    │   │ OPA, Cedar, Casbin, OSO       │     │
                    │   └──────────────────────────────┘     │
                    │                                         │
                    │   ┌──────────────────────────────┐     │
                    │   │    Standards                  │     │
                    │   │ OIDC, SAML, SCIM, SPIFFE,    │     │
                    │   │ WebAuthn, VCs, DIDs           │     │
                    │   └──────────────────────────────┘     │
                    └─────────────────────────────────────────┘
```

### Key Trends to Watch (2025-2026)

1. **AI and identity**: AI-powered access reviews, anomaly detection,
   and identity governance automation. SailPoint and Saviynt leading.

2. **Passkey ubiquity**: Enterprise passkey deployments will accelerate
   as conditional UI and cross-device auth mature.

3. **Policy-as-code convergence**: OPA and Cedar ecosystems may converge
   or a clear winner may emerge for application-level authorization.

4. **EU digital identity wallets**: eIDAS 2.0 mandates will force real
   VC/DID adoption in Europe by 2026. Spillover effects globally.

5. **Machine identity explosion**: Non-human identities (service accounts,
   APIs, IoT, AI agents) outnumber human identities 50:1+. SPIFFE, Venafi
   (CyberArk), and cloud-native approaches compete.

6. **Identity fabric / composable identity**: Gartner's identity fabric
   concept -- composing best-of-breed identity services rather than
   monolithic platforms -- aligns with Ory's approach and challenges
   Keycloak's monolithic model.

7. **Vendor consolidation continues**: Expect more M&A. PAM, IGA, and
   IAM vendors are converging into "identity security platforms."

8. **Zero trust mandates**: US government (OMB M-22-09), EU NIS2, and
   enterprise zero-trust initiatives continue to drive identity
   modernization spending.

---

*Document compiled: 2025-02 (data as of training cutoff)*
*Sources: Training knowledge with cutoff May 2025. GitHub statistics, version numbers, and market data are approximate and should be verified against current sources.*
