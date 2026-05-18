---
title: Migration Recommendations
description: "When to stay, when to migrate, and where to go — concrete effort estimates, risk factors, and decision criteria for every ForgeRock/OpenAM scenario."
sidebar:
  order: 2
---

![IAM decision tree](/idp-research/diagrams/14-iam-decision-tree.svg)

## When to Stay vs. When to Migrate

Not every OpenAM deployment needs to move. The decision depends on your current fork, your protocol requirements, and your team's operational capacity.

**Stay on OIP OpenAM or Wren:AM if:**
- You need SAML 2.0 IdP/SP + OAuth 2.0 + OIDC in a single WAR deployment
- Your team has existing Java/OpenAM expertise
- You have 20+ SAML partner integrations (migration coordination cost is high)
- You require XACML 3.0 policy evaluation with combining algorithms
- You operate WS-Federation or WS-Trust endpoints for legacy Windows clients

**Migrate immediately if:**
- You are running **ForgeRock CE 11.0.3** — it has four unpatched critical RCE vulnerabilities (CVE-2021-35464 CVSS 9.8, CVE-2022-1471, CVE-2022-42889, CVE-2024-38999). Any internet-facing deployment is compromisable. Metasploit modules exist for the primary exploit.
- You need cloud-native deployment (container-native, horizontal auto-scaling, GitOps-managed)
- Your primary use case is developer-facing OAuth 2.0/OIDC with no SAML requirements
- You need managed SaaS with SLA guarantees and no operational overhead

---

## Migration Paths by Target Platform

These estimates assume a mid-complexity deployment: 10–20 SAML partners, 5–10 custom authentication chains, 3–5 custom `AMLoginModule` implementations, XACML policies, and an OAuth 2.0/OIDC provider serving 20+ relying parties.

### Migration to Keycloak — 3–6 months (Medium effort)

Keycloak is the closest architectural analog to OpenAM. It is the recommended target for most OpenAM migrations.

**What maps cleanly:**
- OpenAM realms → Keycloak realms (sub-realm hierarchy may need flattening to a flat structure)
- SAML 2.0 metadata → Keycloak Identity Provider and Client configurations (import directly; attribute mapping must be recreated manually)
- OAuth 2.0/OIDC clients → re-register each client with matching `client_id`, `redirect_uri`, and scope; token format differences (opaque vs JWT, claim naming conventions) require client-side adjustments
- User data → LDIF export from OpenDJ, SCIM/REST import into Keycloak's database; verify password hash algorithm compatibility before migration

**What requires redesign:**
- Authentication chains (JAAS `REQUIRED`/`SUFFICIENT`/`OPTIONAL`/`REQUISITE` control flags) → Keycloak authentication flows with execution requirements (`REQUIRED`/`ALTERNATIVE`/`CONDITIONAL`/`DISABLED`). Complex chains with `REQUISITE` short-circuiting need careful rethinking.
- Custom `AMLoginModule` implementations → Keycloak SPI `Authenticator` implementations. The SPI contract differs but the concept is similar. Budget 2–4 weeks per complex module.
- XACML policies → **no Keycloak equivalent**. Options: Keycloak's UMA-based authorization services (less expressive), integrate OPA or Cedar externally, or port to application-level RBAC.

**Key risk:** XACML organizations must decide on an authorization architecture before starting — this is the longest lead-time item and frequently underestimated.

| Dimension | Effort |
|-----------|--------|
| Realm/policy migration | Low — mostly configuration |
| Auth chain migration | Medium — flow redesign required |
| SAML partner migration | Medium — metadata import + manual attribute mapping |
| OAuth2/OIDC client migration | Low — client re-registration |
| XACML policy migration | **High** — no native equivalent |
| User data migration | Low — LDIF export → SCIM import |
| Custom module rewrite | Medium-High — 2–4 weeks per module |

---

### Migration to Auth0 / Okta — 4–8 months (High effort)

The shift from self-hosted to SaaS introduces architectural constraints beyond code migration. Per-MAU pricing must be validated against actual user volumes before committing — organizations with millions of users may find Auth0 cost-prohibitive at scale.

**What migrates reasonably:**
- Social login: Auth0's 70+ pre-built social connections replace OpenAM's `openam-auth-oauth2` module with less custom code
- SAML partners → Auth0 Enterprise Connections (SAML) or OIDC connections; each partner requires coordinated metadata exchange
- Okta's lifecycle management and provisioning features can replace some OpenIDM functionality

**What is painful:**
- User export from OpenDJ (LDIF) must be transformed to Auth0's bulk import JSON format. Password hashes can be imported if the algorithm is supported (bcrypt, PBKDF2), but OpenAM-era hash schemes (SHA-256 with non-standard salt format) may require forced password resets on first login — coordinate with users in advance.
- Authentication chains → Auth0 Actions (Node.js). This is a fundamentally different programming model from Java JAAS. RADIUS, SecurID, and custom risk-scoring modules have no direct equivalent and require custom Action code.
- XACML policies cannot be migrated to Auth0. Authorization must move to Auth0's RBAC, custom claims in tokens via Actions, or an external policy engine.

**Key risk:** Vendor lock-in is complete. There is no self-hosted Auth0 option and no migration path out once user identity is in Auth0/Okta.

---

### Migration to Ory Stack — 6–12 months (Highest effort)

Ory demands the most effort due to a fundamentally different paradigm. OpenAM is a monolithic, UI-inclusive, Java-based platform; Ory is a decomposed, headless, Go-based microservices suite. Every login and registration screen must be built from scratch.

**Critical blocker: SAML.** Ory Hydra does not support SAML 2.0. Organizations with SAML requirements must add a SAML bridge (Satosa, Shibboleth) in front of Hydra, adding operational complexity and a dependency on a separate project.

**What works well in Ory:**
- OAuth 2.0/OIDC client migration to Hydra is clean — Hydra is a certified OIDC provider with standard client registration
- Cloud-native deployment: Ory is designed for Kubernetes, horizontal scaling, and GitOps workflows
- Fine-grained authorization via Ory Keto (Zanzibar-style relationship tuples) for teams adopting ReBAC

**What requires complete rearchitecting:**
- No realm concept — multi-tenancy requires separate Ory deployments or Ory Network projects
- Authentication chains → Ory Kratos self-service flows with webhooks and JSONNET-based data mapping. Every UI screen must be built.
- XACML policies → Ory Keto's ReBAC relationship model. This is a different authorization paradigm entirely; policies with complex environment conditions (IP range, time window) have no direct Keto equivalent.
- User data → JSON Schema definition for each identity type, transformation from LDAP attributes to Kratos traits

**Key risk:** Ory requires deep Go/Kubernetes expertise that most OpenAM teams do not have. Budget for significant hiring or consulting.

---

## The Module Assessment — Most Underestimated Task

OpenAM's 34+ authentication modules have no single-platform equivalent. Before choosing a target platform, inventory every authentication module in use:

| Module Category | Common Examples | Typical Migration Path |
|----------------|-----------------|----------------------|
| Standard protocols | LDAP, Kerberos, X.509, RADIUS | Usually supported natively on target |
| Social / OAuth2 | Google, Facebook, Microsoft | Pre-built connections on most platforms |
| MFA | OATH TOTP, HOTP, Push | Native MFA on most platforms |
| Hardware tokens | SecurID (RSA), YubiKey | Vendor SDK integration required |
| Adaptive risk | Device fingerprint, IP reputation | Custom development on all targets |
| Legacy enterprise | MSISDN, Windows Desktop SSO | Keycloak has equivalents; Ory/Auth0 do not |
| Security Token Service | WS-Trust, SOAP federation | No modern platform supports this natively |

Modules with no target equivalent — RADIUS authentication, adaptive risk scoring, Security Token Service — require custom development or architectural workarounds. **This per-module assessment is the most time-consuming component of migration planning.**

---

## Migration Effort Summary

| | **Keycloak** | **Auth0 / Okta** | **Ory Stack** |
|--|:---:|:---:|:---:|
| **Estimated timeline** | 3–6 months | 4–8 months | 6–12 months |
| **Architecture shift** | Low | High (self-hosted → SaaS) | Highest (monolith → microservices) |
| **Auth chain migration** | Medium (flow redesign) | High (Node.js Actions rewrite) | Highest (Kratos flows + custom UI) |
| **SAML partner migration** | Metadata import + manual attr mapping | Enterprise Connection recreation | Requires SAML bridge |
| **OAuth2/OIDC client migration** | Client re-registration | Client re-registration | Hydra registration (clean) |
| **XACML policy migration** | No equivalent (UMA or external OPA) | No equivalent (RBAC + Actions) | No equivalent (Keto ReBAC) |
| **User data migration** | LDIF → SCIM import | LDIF → JSON bulk import | LDIF → Kratos identity schema |
| **Operational model** | Self-hosted or RHSSO managed | SaaS (no self-hosted option) | Self-hosted Kubernetes |
| **SAML 2.0 IdP support** | Full | Full | Requires bridge (Satosa) |
| **Vendor lock-in risk** | Low | **High** | Low |

---

## Greenfield Architecture Recommendations

For teams starting fresh without an OpenAM deployment to migrate:

**Use Keycloak** if you need enterprise IAM breadth (SAML, OIDC, LDAP federation, admin UI) with no operational budget for microservices complexity. Red Hat SSO provides commercial support.

**Use Ory** if you are building a cloud-native, developer-first platform and need precise control over each IAM function. Accept the UI build cost upfront.

**Use Auth0** if developer experience and time-to-market matter more than cost or lock-in. Best for B2C or startup contexts.

**Use Zitadel** if you want a modern, Go-based, single-binary alternative with built-in audit logging and event sourcing — a strong middle ground between Keycloak's breadth and Ory's composability.

**Use Cognito** if you are already all-in on AWS and do not need to act as a SAML IdP to external partners. Cognito cannot produce SAML assertions — if you need that, look elsewhere.

---

## Further Reading

- [Platform Comparison Matrices](/idp-research/decision-guide/comparison/) — side-by-side feature, protocol, and licensing tables for 8 platforms
- [OpenAM Deep Dive](/idp-research/openam-lineage/openam/) — full architecture analysis, CVE history, and fork comparison
- [CVE History & Patch Matrix](/idp-research/reference/cve-history/) — why ForgeRock CE 11.0.3 must be replaced immediately
