# Prompt: Identity Security Evolution Roadmaps

## Goal

Produce a new chapter (`16-evolution-roadmaps.md`) that traces the evolution of **every major identity security topic area** from origin through current state to future trajectory. Each topic gets a self-contained roadmap showing: when it appeared, key milestones, what superseded what, what's actively used now, what's emerging, and what OpenAM/OIP implements.

"Identity Security" is the umbrella term encompassing: IAM (Identity & Access Management), PAM (Privileged Access Management), IGA (Identity Governance & Administration), ITDR (Identity Threat Detection & Response), CIEM (Cloud Infrastructure Entitlement Management), decentralized identity, workload identity, privacy/consent, and zero trust — the full spectrum.

**No line limits on any section.** Write as much detail as your knowledge allows. Go deep on each roadmap — include every relevant RFC, specification, vendor, product, standard, academic paper, and implementation detail you know. The more comprehensive, the better. This should be the definitive chronological reference for the entire identity security domain.

---

## Source Material (read all before writing)

| Priority | File | Why |
|----------|------|-----|
| 1 | `chapters/02-authentication-protocols.md` | Auth method evolution |
| 2 | `chapters/03-federation-protocols.md` | Federation protocol timeline |
| 3 | `chapters/04-authorization-frameworks.md` | AuthZ evolution |
| 4 | `chapters/05-directory-services.md` | Directory/LDAP evolution |
| 5 | `chapters/06-token-formats.md` | Token + session evolution |
| 6 | `chapters/12-modern-architecture.md` | 14 architecture shifts |
| 7 | `chapters/13-comparison-matrices.md` | Current vendor landscape |
| 8 | `chapters/15-historical-parallels.md` | Pre-computer trust patterns |
| 9 | `extracts/protocol-inventory.md` | 40+ protocol implementations |
| 10 | `extracts/standards-timeline.md` | RFC/spec timeline |
| 11 | `extracts/modern-landscape.md` | Current products + trends |
| 12 | `extracts/pre-computer-auth-research.md` | Ancient auth patterns |

**Also use your full training knowledge** for any dates, RFCs, milestones, vendor histories, market data, academic references, or technical details not in these files. The source files provide the OpenAM/OIP-specific data; your knowledge fills in the broader industry context.

---

## Document Structure

### Introduction
- Purpose: trace every identity security domain from earliest form to 2026 state
- Why "Identity Security" not just "IAM" — the scope has expanded far beyond traditional IAM
- How to read: each section is standalone; can be read in any order
- Notation: `[ACTIVE]` = widely deployed today, `[LEGACY]` = still exists but declining, `[EMERGING]` = <5% adoption, `[OBSOLETE]` = effectively dead

### Roadmap 1: Authentication Methods

**Timeline**: Passwords (1960s) → LDAP Simple Bind (1993) → Kerberos (1988/2005 in OpenAM) → X.509 Certificates (1988) → RADIUS/TACACS+ (1991/1993) → HTTP Basic/Digest (1996/1997) → NTLM (1993) → Form-based (2000s) → HOTP (RFC 4226, 2005) → TOTP (RFC 6238, 2011) → Push notifications (2013) → FIDO U2F (2014) → FIDO2/WebAuthn (2019) → Passkeys (2022-2024) → Continuous authentication (emerging)

For each milestone:
- RFC/spec reference and date
- What problem it solved vs predecessor
- OpenAM module that implements it (if applicable)
- Current status tag: `[ACTIVE]`, `[LEGACY]`, `[OBSOLETE]`

End with: MFA factor evolution table (knowledge → possession → inherence → context → behavior)

### Roadmap 2: Federation Protocols

**Timeline**: Kerberos cross-realm (1988) → SAML 1.0 (2002) → Liberty ID-FF (2003) → SAML 1.1 (2003) → SAML 2.0 (2005) → WS-Federation (2003/2009) → WS-Trust (2005) → OpenID 2.0 (2007) → OAuth 1.0 (2007) → OAuth 2.0 (RFC 6749, 2012) → OIDC (2014) → OAuth 2.1 (draft) → GNAP (draft) → Verifiable Presentations (emerging)

For each: spec body, key RFCs, what it replaced, adoption curve, OpenAM implementation status.

Include a "federation protocol family tree" showing which specs influenced which.

### Roadmap 3: Authorization Models

**Timeline**: Unix file permissions (1971) → ACLs (1980s) → RBAC (1992 NIST) → LDAP ACI (1993) → J2EE security roles (1999) → XACML 1.0 (2003) → XACML 2.0 (2005) → XACML 3.0 (2013) → OAuth scopes (2012) → UMA 1.0 (2015) → UMA 2.0 (2018) → OPA/Rego (2018) → Cedar (2023) → Zanzibar/SpiceDB (2019/2023) → OpenFGA (2022)

Cover: ABAC vs RBAC vs ReBAC, policy-as-code movement, OpenAM's entitlements engine, CIEM as cloud authorization.

### Roadmap 4: Token Formats & Session Management

**Timeline**: Kerberos tickets (1988) → SAML assertions (2002) → Proprietary session cookies (2000s) → OpenAM CTS tokens (2012) → OAuth 2.0 bearer tokens (2012) → JWT (RFC 7519, 2015) → JWT-at (RFC 9068, 2021) → DPoP (RFC 9449, 2023) → Transaction Tokens (TxnTokens, draft) → Verifiable Credentials (W3C 2022)

Cover: stateful vs stateless tradeoffs, token binding, sender-constrained tokens, token revocation strategies, OpenAM CTS architecture.

Session evolution: server-side sticky sessions → replicated sessions → CTS centralized → stateless JWT → hybrid (short-lived JWT + refresh rotation).

### Roadmap 5: Directory Services & Identity Stores

**Timeline**: X.500 (1988) → LDAPv2 (RFC 1777, 1995) → LDAPv3 (RFC 4510, 2006) → DSML v2 (2002) → REST2LDAP (2013) → SCIM 1.0 (2011) → SCIM 2.0 (RFC 7643/7644, 2015) → Cloud directories (Azure AD 2013, AWS Directory Service 2015) → PostgreSQL as identity store (Keycloak, Zitadel) → CockroachDB (Zitadel) → Event-sourced identity (Zitadel)

Cover: LDAP schema evolution, replication topologies, OpenDJ's unique features (multi-master, RxJava, Cassandra backend), the "LDAP demotion" trend, SCIM as the modern provisioning protocol, Active Directory's dominance and Microsoft Entra ID transition.

### Roadmap 6: Identity Governance & Administration (IGA)

**Timeline**: Manual provisioning (pre-2000) → Meta-directory sync (2000s) → Sun IdM (2005) → ForgeRock OpenIDM (2012) → SCIM 2.0 provisioning (2015) → Event-driven sync (2018+) → Modern IGA platforms (SailPoint IdentityNow, Saviynt, Omada) → AI-driven access reviews (2023+) → Identity orchestration (2024+)

Cover: Joiner-Mover-Leaver lifecycle, reconciliation patterns, OpenIDM's OSGi architecture, connector frameworks (OpenICF → SCIM → native APIs), workflow engines (Activiti BPMN in OpenIDM vs modern alternatives), access certification campaigns, SoD (Separation of Duties), role mining.

### Roadmap 7: API Security & Gateway Evolution

**Timeline**: HTTP Basic Auth (1996) → API keys (2000s) → OAuth 2.0 for APIs (2012) → Policy agents (OpenAM web/J2EE agents) → API gateways (Kong 2015, Apigee) → OpenIG identity gateway (2012) → Service mesh (Istio 2017, Linkerd 2017) → Envoy sidecar proxy (2016) → mTLS everywhere (2020+) → DPoP for APIs (2023) → API security platforms (Salt, Noname, 42Crunch) → API-first identity design

Cover: credential replay (OpenIG's unique capability), gateway vs sidecar pattern, API-first identity design, token introspection vs JWT validation at the edge, OWASP API Security Top 10.

### Roadmap 8: Privileged Access Management (PAM)

**Timeline**: su/sudo (1980s) → Shared account vaults (2000s) → CyberArk PAM (2005) → Session recording (2010s) → Just-in-Time access (2015+) → Delinea Secret Server → BeyondTrust → HashiCorp Vault (2015) → Cloud PAM (AWS SSM, Azure PIM) → Zero Standing Privileges (2023+) → Ephemeral access (2024+)

Cover: vault patterns, session brokering, secrets management vs privileged session management, ephemeral credentials, how PAM intersects with IAM (OpenAM admin delegation, OpenDJ admin access), PAM for cloud (CIEM overlap), break-glass procedures.

### Roadmap 9: Deployment Architecture for Identity Systems

**Timeline**: On-prem monolithic WAR (OpenAM) → Clustered J2EE (2005-2016) → Docker containers (2015+) → Kubernetes operators (2018+) → Microservices decomposition (Ory 2018) → Single-binary (Zitadel 2021) → Serverless auth (Cognito, Supabase Auth) → Edge-deployed identity (Cloudflare Access) → SaaS IDaaS (Auth0, Okta) → Hybrid/multi-cloud identity (2024+)

Cover: OpenAM's WAR deployment vs modern patterns, Helm charts, GitOps for identity infra, multi-region HA, the spectrum from self-hosted to fully managed, identity mesh architecture.

### Roadmap 10: Passwordless & MFA Evolution

**Timeline**: Passwords only (1960-2000) → SMS OTP (2005) → Hardware tokens RSA SecurID (1993) → HOTP (2005) → TOTP (2011) → Push authentication (2013) → FIDO U2F (2014) → Platform authenticators (Windows Hello 2015, Touch ID) → FIDO2/WebAuthn (2019) → Passkeys (2022) → Synced passkeys (2023) → Conditional UI (2023) → Device-bound keys (2024)

Cover: MFA fatigue attacks, phishing-resistant MFA, the Google/Apple/Microsoft passkey push, adoption statistics, NIST 800-63B guidance evolution, OpenAM's WebAuthn module status, the death-of-passwords timeline.

### Roadmap 11: Zero Trust & Perimeter Evolution

**Timeline**: Firewall perimeter (1990s) → DMZ architecture (2000s) → VPN remote access → Jericho Forum (2004) → Google BeyondCorp (2014 paper) → SDP/Software Defined Perimeter (CSA 2014) → NIST SP 800-207 (2020) → ZTNA products (Zscaler, Cloudflare) → CISA Zero Trust Maturity Model (2023) → Continuous verification → Device trust → Context-aware access policies

Cover: how identity became the new perimeter, policy enforcement points, microsegmentation, how OpenAM's adaptive auth and OpenIG's gateway fit the zero trust model, identity as the control plane.

### Roadmap 12: Machine & Workload Identity

**Timeline**: Service accounts (1990s) → API keys (2000s) → OAuth client credentials (2012) → Kubernetes service accounts (2015) → SPIFFE/SPIRE (2017/2018) → Cloud workload identity (AWS IAM roles, GCP WIF, Azure MI) → mTLS service mesh identity → Sigstore for supply chain (2021) → OpenPubkey (2023) → WIMSE working group (2024)

Cover: the machine-to-human identity ratio explosion, short-lived certificates, identity federation for workloads, how OpenAM handles service-to-service auth, non-human identity management as emerging discipline.

### Roadmap 13: Identity Threat Detection & Response (ITDR)

**Timeline**: Log aggregation (2000s) → SIEM correlation (2005+) → UEBA (2015) → ITDR as category (Gartner 2022) → CrowdStrike Identity Protection → Silverfort unified identity protection → Microsoft Entra ID Protection → Vectra AI → Identity-aware EDR integration → Identity Security Posture Management (2024+)

Cover: credential stuffing detection, impossible travel, MFA fatigue detection, lateral movement detection, how identity telemetry feeds SOC workflows, Kerberoasting/AS-REP roasting detection, identity attack surface management.

### Roadmap 14: Privacy, Consent & Regulatory Evolution

**Timeline**: OECD Privacy Guidelines (1980) → EU Data Protection Directive 95/46/EC (1995) → P3P (2002) → HIPAA Security Rule (2003) → PCI DSS (2004) → GDPR (2018) → CCPA (2020) → CPRA (2023) → Consent receipts (Kantara) → UMA as consent protocol → Privacy by design (ISO 31700, 2023) → Global Privacy Control (2021) → Age verification (EU 2024) → AI Act identity requirements (EU 2024)

Cover: how identity systems became consent engines, OpenAM's consent module, modern consent management platforms, data subject access requests as IAM flows, privacy-preserving identity (selective disclosure, zero-knowledge proofs).

### Roadmap 15: Decentralized & Self-Sovereign Identity

**Timeline**: PGP web of trust (1991) → Indie Web (2010s) → Sovrin Foundation (2016) → W3C DID spec (2019/2022) → Verifiable Credentials (2022) → ION/Sidetree (Bitcoin-anchored DIDs) → EU eIDAS 2.0 + EUDI Wallet (2024) → mDL (mobile driver's license, ISO 18013-5) → SD-JWT for selective disclosure → OpenID4VC/OpenID4VP (2023) → IETF SD-JWT VC (2024)

Cover: the promise vs reality of SSI, blockchain-based vs non-blockchain approaches, government adoption (EU, Canada, Australia, Bhutan), interoperability challenges, how traditional IAM (OpenAM) might integrate with VC issuance/verification, the wallet wars.

### Roadmap 16: Open-Source Identity Platform Evolution

**Timeline**: Sun Java System Identity Server (2003) → Sun Access Manager 7 (2005) → OpenSSO (2008) → ForgeRock OpenAM 9-13 (2010-2016) → ForgeRock goes closed (Nov 2016) → OIP fork (2017) → Wren Security fork (2018) → Keycloak 1.0 (2014) → Ory Hydra (2017) → Authentik (2020) → Zitadel (2021) → Casdoor (2022) → SuperTokens (2021) → Logto (2022) → Hanko (2022)

Cover: commit velocity chart references, fork divergence analysis, how Keycloak became the default, the Ory decomposition philosophy, Zitadel's event-sourcing approach, which platforms are gaining/losing momentum, GitHub star trajectories, commercial backing (Red Hat → Keycloak, CAOS AG → Zitadel).

### Roadmap 17: Cloud Infrastructure Entitlement Management (CIEM)

**Timeline**: AWS IAM (2011) → Azure RBAC (2014) → GCP IAM (2016) → Multi-cloud identity complexity (2018+) → CIEM as category (Gartner 2020) → Ermetic → Wiz (2020) → CrowdStrike CIEM → Prisma Cloud → AWS IAM Access Analyzer (2019) → Permission boundaries → Least-privilege automation (2024+)

Cover: cloud IAM sprawl, cross-cloud entitlement mapping, over-provisioned permissions, identity-based blast radius, how CIEM overlaps with PAM and IGA, CloudKnox acquisition by Microsoft.

### Roadmap 18: Identity Orchestration & Journey-Time Orchestration

**Timeline**: Authentication chains (OpenAM JAAS, 2005) → Authentication trees (ForgeRock 6.0, 2018) → No-code identity workflows (Auth0 Actions, 2021) → Identity orchestration platforms (Strata Maverics, Ping Identity DaVinci) → Journey-time orchestration (2023+) → Policy-driven adaptive journeys

Cover: how authentication evolved from linear chains to DAG-based trees to fully orchestrated journeys, OpenAM's auth module chain architecture, modern visual flow builders, vendor-neutral orchestration.

### Summary: The Grand Shift Table

A single consolidated table covering ALL roadmaps:

| # | Domain | Origin | Then (Pre-2010) | Now (2024-2026) | Next (2027+) |
|---|--------|--------|-----------------|-----------------|--------------|
| 1 | Authentication | Passwords (1960s) | LDAP bind + OTP | Passkeys + WebAuthn | Continuous auth |
| 2 | Federation | Kerberos (1988) | SAML 2.0 | OIDC | GNAP, VPs |
| ... | ... | ... | ... | ... | ... |

List ALL shifts with one-line summaries covering every roadmap.

---

## Writing Style

- **Chronological within each roadmap** — earliest to latest, always with dates
- **RFC/spec references** — cite RFC numbers, W3C specs, OASIS standards, NIST publications
- **Status tags** — every technology gets `[ACTIVE]`, `[LEGACY]`, `[EMERGING]`, or `[OBSOLETE]`
- **OpenAM/OIP implementation notes** — for each technology, note whether OpenAM implements it and which module
- **Be comprehensive** — this is the definitive reference. Include every relevant detail from your training data
- **Use tables, timeline markers, bullet points** — this is a reference chapter, optimize for scanability
- **Cross-reference** — link to other chapters where deeper analysis exists (e.g., "See Ch.02 for FIDO2 protocol details")
- **No fluff** — every line should contain a fact, date, specification reference, or implementation detail
- **Vendor-neutral tone** — present facts, not marketing claims

## Quality Criteria

1. Every roadmap has at least 8 chronological milestones with dates
2. Every technology mentioned has a status tag
3. OpenAM/OIP implementation status noted for at least 80% of technologies
4. All RFC numbers are accurate (verify via web search if unsure)
5. No duplicate coverage with other chapters — reference them instead of repeating
6. The summary table at the end covers all 18 roadmaps in a single glanceable view
7. Breadth matters more than brevity — cover every aspect the LLM has knowledge of

## Output

Save as: `docs/chapters/16-evolution-roadmaps.md`

Title: `# Chapter 16: Identity Security Evolution Roadmaps — How Every Domain Got Here`
