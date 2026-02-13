# Excalidraw Diagram Generation Prompt

## Overview

Generate 15 Excalidraw diagrams (plus 1 two-part swim lane timeline = 16 files total) to visually support the IAM research project at `/Users/kirane/projects/idp/docs/`. Save all diagrams as `.excalidraw` files + exported PNGs in `docs/diagrams/`. After generation, link each PNG from the relevant markdown chapter(s) using relative paths.

Use the `diagram-generation:diagram-pro` agent for each diagram.

## Output Requirements

- **Format**: `.excalidraw` JSON + `.png` export for each diagram
- **Location**: `/Users/kirane/projects/idp/docs/diagrams/`
- **Naming**: `NN-short-name.excalidraw` and `NN-short-name.png` (e.g., `01-oip-architecture.excalidraw`)
- **Style**: Professional, clean, consistent color scheme across all diagrams. Use a blue/teal/navy palette consistent with the PPTX deck (#1C2833 navy, #2E4053 slate, #5DADE2 teal, #F4F6F6 white, #F39C12 gold, #E74C3C red)
- **Chapter linking**: After all diagrams are generated, edit each relevant chapter `.md` file to add `![Diagram Title](../diagrams/NN-short-name.png)` at the appropriate location

---

## Diagram Specifications

### Diagram 01: OIP Component Architecture
**File**: `01-oip-architecture`
**Link from**: `README.md`, `chapters/07-openam-analysis.md`
**Type**: Architecture / system context diagram

Show the full Open Identity Platform component stack with directional arrows:

```
Users/Apps
    │
    ▼
  OpenIG (Gateway, reverse proxy, policy enforcement)
    │
    ▼
  OpenAM (SSO, AuthN, AuthZ, Federation)
    │           │
    ▼           ▼
  OpenDJ      OpenIDM (Provisioning, sync, lifecycle)
  (LDAP)        │
                ▼
              OpenICF (Connector framework)
                │
                ▼
          External Systems (AD, Oracle HR, SAP, databases)
```

**Details to include**:
- Each component as a rounded rectangle with name + brief role
- Version numbers: OpenAM 16.0.5, OpenDJ 5.0.3, OpenIDM 7.0.2, OpenIG 6.0.2, OpenICF 2.0.2
- Directional arrows showing request flow (top-down) and data flow (bidirectional for OpenDJ)
- Color: Each component a slightly different shade of blue/teal
- External systems as gray boxes at bottom

---

### Diagram 02: Production HA Deployment Topology
**File**: `02-ha-deployment`
**Link from**: `chapters/07-openam-analysis.md`
**Type**: Deployment / infrastructure diagram

Multi-datacenter active-active deployment:

```
              Global DNS Load Balancer
              ┌─────────┴─────────┐
         DC-1 (Primary)      DC-2 (Secondary)
         ┌─────────┐         ┌─────────┐
         │   LB    │         │   LB    │
         │(sticky) │         │(sticky) │
         ├────┬────┤         ├────┬────┤
         │AM-1│AM-2│         │AM-3│AM-4│
         └──┬─┴─┬──┘         └──┬─┴─┬──┘
            │   │                │   │
         ┌──┴───┴──┐         ┌──┴───┴──┐
         │ OpenDJ-1│◄═══════►│ OpenDJ-2│  (multi-master replication)
         └────┬────┘         └────┬────┘
         ┌────┴────┐         ┌────┴────┐
         │Cassandra│◄═══════►│Cassandra│  (multi-DC replication)
         │  DC-1   │         │  DC-2   │
         └─────────┘         └─────────┘
```

**Details**:
- Load balancers with "sticky sessions (amlbcookie)" label
- OpenAM instances labeled "Tomcat 11 + OpenAM WAR"
- CTS (Core Token Service) label on Cassandra
- Replication arrows between DCs (dashed, bidirectional)
- Color: infrastructure gray, OpenAM blue, OpenDJ teal, Cassandra green

---

### Diagram 03: OpenIDM Provisioning Architecture
**File**: `03-openidm-provisioning`
**Link from**: `chapters/09-openidm-analysis.md`
**Type**: Architecture diagram

```
                    ┌─────────────────────────┐
                    │    OpenIDM (OSGi/Felix)  │
                    │  ┌─────────────────────┐ │
  Admin UI ────────►│  │   Sync Engine       │ │
  REST API ────────►│  │   Recon Engine      │ │
                    │  │   Workflow (Activiti)│ │
                    │  │   Managed Objects    │ │
                    │  └────────┬────────────┘ │
                    │           │              │
                    │  ┌────────┴────────────┐ │
                    │  │  OpenICF Provisioner │ │
                    │  └────────┬────────────┘ │
                    └───────────┼──────────────┘
                                │
                    ┌───────────┼───────────────┐
                    │           │               │
              ┌─────┴─────┐ ┌──┴──────┐ ┌──────┴────┐
              │ LDAP Conn │ │ DB Conn │ │ CSV Conn  │
              └─────┬─────┘ └──┬──────┘ └──────┬────┘
                    │          │               │
              Active Dir    Oracle HR      CSV Files
```

Also show:
- PostgreSQL as repository backend (left side)
- OpenAM integration for SSO (top, via OpenIG)
- BPMN workflow engine callout

---

### Diagram 04: Historical Timeline (2005-2026)
**File**: `04-historical-timeline`
**Link from**: `chapters/01-history.md`
**Type**: Timeline / evolution diagram

Horizontal timeline with these events marked:

| Date | Event | Type |
|------|-------|------|
| 2005 Oct | Sun announces OpenSSO (CDDL) | Launch |
| 2006 Jun | First OpenDS commit | Launch |
| 2009 Apr | Oracle acquires Sun ($7.4B) | Corporate |
| 2010 Jan | Oracle acquisition closes | Corporate |
| 2010 Oct | Oracle announces proprietary migration | Crisis |
| 2011 Feb | ForgeRock incorporated (Norway) | Launch |
| 2012 Jul | ForgeRock first commits to OpenAM/OpenDJ/OpenIDM | Launch |
| 2013 Nov | OpenAM 11.0.0 released | Release |
| 2014 | Peak: 10,744 commits, 895/month | Peak |
| 2015 Mar | Last CE binary (11.0.3) | Release |
| 2016 Sep | ForgeRock Series C ($88M) | Corporate |
| 2016 Nov | Last open tag (14.0.0-M2) — SOURCE CLOSED | Crisis |
| 2017 | 94% commit velocity drop (553→34/month) | Crisis |
| 2017 Nov | Final CE commit | End |
| 2018 Feb | OIP first release (14.0.0) | Fork |
| 2021 Sep | ForgeRock IPO ($2.8B, NYSE:FORG) | Corporate |
| 2023 Feb | Wren:AM 15.0.0-M1 (first tag) | Fork |
| 2023 Oct | Thoma Bravo acquires ForgeRock ($2.3B) → merges with PingIdentity | Corporate |
| 2025 Nov | OIP 16.0.3 release wave | Release |
| 2026 Feb | OIP 16.0.5, Wren:AM 16.0.0-M1 | Current |

**Visual treatment**:
- Color-coded eras: Sun (orange), Oracle (red), ForgeRock (blue), Post-closure (split into OIP green + Wren purple)
- Crisis events in red diamonds
- Corporate events in gold circles
- Releases in blue squares
- A subtle commit velocity sparkline running below the timeline if possible
- Fork point (Nov 2016) as a dramatic visual split into two branches

---

### Diagram 05: Protocol Evolution Timeline
**File**: `05-protocol-evolution`
**Link from**: `chapters/02-authentication-protocols.md`, `chapters/03-federation-protocols.md`
**Type**: Timeline diagram

Horizontal timeline showing protocol introductions:

| Year | Protocol | Category |
|------|----------|----------|
| 1993 | Kerberos V5 (RFC 1510) | AuthN |
| 1993 | LDAPv1 (RFC 1487) | Directory |
| 1997 | LDAPv3 (RFC 2251) | Directory |
| 2000 | RADIUS (RFC 2865) | AuthN |
| 2002 | SAML 1.0 | Federation |
| 2005 | SAML 2.0 (OASIS) | Federation |
| 2005 | HOTP (RFC 4226) | MFA |
| 2007 | OAuth 1.0 | AuthZ |
| 2011 | TOTP (RFC 6238) | MFA |
| 2012 | OAuth 2.0 (RFC 6749) | AuthZ |
| 2013 | XACML 3.0 | AuthZ |
| 2014 | OIDC Core 1.0 | Federation |
| 2014 | FIDO U2F 1.0 | MFA |
| 2015 | SCIM 2.0 (RFC 7644) | Provisioning |
| 2015 | JWT (RFC 7519) | Token |
| 2019 | WebAuthn L1 (W3C) | MFA |
| 2022 | Passkeys (Apple/Google/MS) | MFA |
| 2023 | DPoP (RFC 9449) | Token |
| 2024 | SD-JWT VC | Token |

**Visual**: Color-code by category (AuthN=blue, Federation=green, AuthZ=orange, MFA=purple, Token=teal, Directory=gray, Provisioning=gold). Show deprecated protocols with strikethrough (SAML 1.0, OAuth 1.0, LDAPv1, SPML).

---

### Diagram 06: Fork Divergence Comparison
**File**: `06-fork-divergence`
**Link from**: `chapters/01-history.md`
**Type**: Comparison / matrix diagram

Visual comparison of the three lineages:

| Dimension | ForgeRock CE 11.0.3 | OIP 16.0.5 | Wren:AM 16.0.0-M1 |
|-----------|--------------------|-----------|--------------------|
| Status | FROZEN (2017) | Active | Active |
| Java | 7 | 11+ | 17+ |
| Guice | 3.0 | 7.0.0 | 3.0 (wrapped) |
| Jakarta EE | javax.* | jakarta.* 4.0 | jakarta.* 5.0 |
| Modules | ~45 | 52+ | ~40 |
| Commits/year | 0 | 350+ | 80-120 |
| Contributors | 0 | ~8 active | ~4 active |
| Security | 4 UNPATCHED RCEs | All CVEs patched | All CVEs patched |
| LOC (OpenAM) | ~1.8M | ~2.35M | ~2.0M |

**Visual treatment**:
- Three columns, ForgeRock CE with red "DANGER" warning overlay
- Traffic light indicators: green (good), yellow (caution), red (critical)
- Security row highlighted with red background for CE

---

### Diagram 07: SAML 2.0 SP-Initiated SSO Flow
**File**: `07-saml-sso-flow`
**Link from**: `chapters/03-federation-protocols.md`
**Type**: Sequence / flow diagram

Three actors: **User/Browser**, **Service Provider (SP)**, **Identity Provider (IdP/OpenAM)**

```
User/Browser          SP                    IdP (OpenAM)
    │                  │                        │
    │──GET /resource──►│                        │
    │                  │──AuthnRequest──────────►│
    │◄─HTTP 302 Redirect to IdP────────────────│
    │──────────────────────────────────────────►│
    │                  │                        │──Authenticate user
    │◄─────────────Login form──────────────────│
    │──────────────Credentials─────────────────►│
    │                  │                        │──Generate SAML Assertion
    │                  │                        │──Sign with IdP private key
    │◄─────────HTTP POST to ACS endpoint───────│
    │──POST /saml/acs──►│                       │
    │                  │──Validate signature     │
    │                  │──Check audience         │
    │                  │──Check expiration        │
    │                  │──Create local session    │
    │◄─200 + session──│                         │
```

**Details**: Label each arrow with the protocol detail (HTTP Redirect binding, HTTP POST binding, XML signature, ACS URL). Show the SAML assertion as a callout box with key fields: Issuer, Subject/NameID, Conditions (NotBefore, NotOnOrAfter, AudienceRestriction), AuthnStatement.

---

### Diagram 08: OAuth2/OIDC Authorization Code + PKCE Flow
**File**: `08-oauth2-oidc-flow`
**Link from**: `chapters/03-federation-protocols.md`
**Type**: Sequence / flow diagram

Four actors: **User**, **Client App**, **Authorization Server (OpenAM)**, **Resource Server**

```
User        Client App        AuthZ Server (OpenAM)     Resource Server
 │              │                      │                       │
 │──Login──────►│                      │                       │
 │              │──GET /.well-known/openid-configuration──────►│
 │              │◄─────────JSON config (endpoints, keys)──────│
 │              │──302 /authorize?                             │
 │              │  response_type=code                          │
 │              │  &client_id=...                              │
 │              │  &scope=openid profile                       │
 │              │  &code_challenge=S256(verifier)              │
 │              │  &redirect_uri=...─────────────────────────►│
 │◄─────────────────Login form────────────────────────────────│
 │──────────────────Credentials───────────────────────────────►│
 │◄─────────────────Consent screen────────────────────────────│
 │──────────────────Approve───────────────────────────────────►│
 │              │◄─302 redirect_uri?code=ABC──────────────────│
 │              │──POST /token                                 │
 │              │  grant_type=authorization_code                │
 │              │  &code=ABC                                   │
 │              │  &code_verifier=...──────────────────────────►│
 │              │◄─{access_token, id_token (JWT), refresh}────│
 │              │──GET /api/resource                            │
 │              │  Authorization: Bearer <access_token>─────────────────►│
 │              │◄────────────────────────────────Resource data─────────│
 │◄─Response───│                                               │
```

**Details**: Show PKCE code_challenge/code_verifier exchange. Callout box for the JWT id_token structure: header (alg, kid), payload (iss, sub, aud, exp, iat, nonce), signature.

---

### Diagram 09: XACML Policy Evaluation Flow
**File**: `09-xacml-evaluation`
**Link from**: `chapters/04-authorization-frameworks.md`
**Type**: Architecture / flow diagram

```
                         ┌──────────────────┐
                         │  PAP (Policy      │
                         │  Administration)   │
                         │  Author/deploy     │
                         │  policies          │
                         └────────┬───────────┘
                                  │ Deploy policies
                                  ▼
┌─────────┐    Request    ┌───────────────┐    Query attrs    ┌──────────┐
│  PEP    │──────────────►│  PDP (Policy  │◄────────────────►│  PIP     │
│ (Guard) │               │  Decision)    │                   │ (LDAP,   │
│         │◄──────────────│  Evaluate     │                   │  DB,     │
│ Enforce │   Decision    │  policies     │                   │  REST)   │
│ result  │  (Permit/     └───────────────┘                   └──────────┘
└─────────┘   Deny +
              Obligations)
```

**Details**:
- PEP: "Intercepts access requests at enforcement point (OpenAM policy agent, OpenIG filter)"
- PDP: "Evaluates XACML policies using combining algorithms (deny-overrides, permit-overrides, first-applicable)"
- PIP: "Retrieves subject, resource, environment attributes from LDAP, databases, REST APIs, geolocation"
- PAP: "Policy authoring via XML/JSON, versioning, deployment to PDP"
- Show the XACML request/response cycle: Request (Subject, Resource, Action, Environment) → Decision (Permit/Deny/NotApplicable/Indeterminate + Obligations + Advice)

---

### Diagram 10: Token Format Evolution & Lifecycle
**File**: `10-token-lifecycle`
**Link from**: `chapters/06-token-formats.md`
**Type**: Combined timeline + lifecycle diagram

**Part A — Token Format Evolution** (top half):
Timeline showing progression:
- 1993: Kerberos tickets (binary, symmetric key, TGT+service tickets)
- 2005: SAML assertions (XML, signed, verbose)
- 2015: JWT (JSON, compact, signed/encrypted, RFC 7519)
- 2023: DPoP (proof-of-possession, sender-constrained, RFC 9449)
- 2024: SD-JWT VC (selective disclosure, verifiable credentials)

Show each format with a small visual representation of its structure.

**Part B — Token Lifecycle** (bottom half):
Circular flow:
```
  Issuance → Transmission → Validation → Storage
      ▲                                    │
      │                                    ▼
  Destruction ← Revocation ← Refresh
```

Label each stage with what happens:
- Issuance: AuthZ server creates token (signing, encryption)
- Transmission: Network transport (Authorization header, cookie, form POST)
- Validation: Signature check, expiration, audience, introspection (RFC 7662)
- Storage: CTS, cache, browser localStorage/sessionStorage
- Refresh: Token exchange (RFC 8693), refresh_token grant
- Revocation: Blacklist, CTS deletion, /revoke endpoint
- Destruction: Cleanup, logout, session timeout

---

### Diagram 11: Modern IAM Landscape Positioning
**File**: `11-iam-landscape`
**Link from**: `chapters/12-modern-architecture.md`, `chapters/13-comparison-matrices.md`
**Type**: Quadrant / positioning diagram

2x2 matrix:
- **X-axis**: Self-hosted ◄──► SaaS
- **Y-axis**: Integrated suite ◄──► Composable services

Position these products:
- **Top-left (Integrated + Self-hosted)**: OpenAM/OIP, Keycloak, Authentik
- **Top-right (Integrated + SaaS)**: Auth0, Okta, AWS Cognito, Microsoft Entra
- **Bottom-left (Composable + Self-hosted)**: Ory stack, Zitadel
- **Bottom-right (Composable + SaaS)**: Ory Network, Stytch, Descope

Additional annotations:
- Arrow from OpenAM toward Keycloak labeled "most common migration path"
- Callout: "OIP/Wren occupy a unique niche: full protocol coverage, no vendor lock-in, but no modern operational model"
- Bubble sizes could indicate relative market share or community size

---

### Diagram 12: SPIFFE/SPIRE Workload Identity Flow
**File**: `12-spiffe-spire`
**Link from**: `chapters/13-comparison-matrices.md`
**Type**: Sequence / architecture diagram

```
┌───────────────────────────────────────────────────────┐
│                    SPIRE Server                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Node         │  │ Registration │  │ CA (Cert     │ │
│  │ Attestor     │  │ API          │  │ Authority)   │ │
│  └──────┬───────┘  └──────────────┘  └──────┬──────┘ │
└─────────┼────────────────────────────────────┼────────┘
          │ Node attestation                   │ Issue SVID
          │ (AWS IID, GCP, K8s, TPM)          │
┌─────────┼────────────────────────────────────┼────────┐
│         ▼            SPIRE Agent             ▼        │
│  ┌──────────────┐                    ┌─────────────┐  │
│  │ Workload     │                    │ Workload    │  │
│  │ Attestor     │                    │ API (UDS)   │  │
│  └──────┬───────┘                    └──────┬──────┘  │
└─────────┼───────────────────────────────────┼─────────┘
          │ Process verification              │ SVID
          │ (kernel, K8s pod, Docker)         │ (X.509 / JWT)
          ▼                                   ▼
    ┌──────────┐                        ┌──────────┐
    │Workload A│◄══════ mTLS ══════════►│Workload B│
    │spiffe://  │                        │spiffe://  │
    │trust/svc-a│                        │trust/svc-b│
    └──────────┘                        └──────────┘
```

**Key callouts**:
- SPIFFE ID format: `spiffe://trust-domain/workload-identifier`
- SVID: Short-lived (minutes), auto-rotated X.509 cert or JWT
- No static secrets distributed — identity derived from platform attestation
- CNCF Graduated project (2022)

---

### Diagram 13: OpenAM Authentication Chain (JAAS)
**File**: `13-openam-auth-chain`
**Link from**: `chapters/07-openam-analysis.md`
**Type**: Flow / pipeline diagram

```
Client Request
    │
    ▼
AuthContext.login()
    │
    ▼
AMLoginContext → JAAS LoginContext
    │
    ▼
┌─────────────────────────────────────────────────────┐
│              Authentication Chain                     │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Module 1 │───►│ Module 2 │───►│ Module 3 │      │
│  │ LDAP     │    │ HOTP     │    │ Device   │      │
│  │ Auth     │    │ (MFA)    │    │ Print    │      │
│  │          │    │          │    │          │      │
│  │ REQUIRED │    │ REQUIRED │    │ OPTIONAL │      │
│  └──────────┘    └──────────┘    └──────────┘      │
│                                                      │
│  Control flags: REQUIRED | REQUISITE | SUFFICIENT |  │
│                 OPTIONAL                             │
└─────────────────────────────────────────────────────┘
    │
    ▼ (all REQUIRED modules pass)
DSAMECallbackHandler
    │
    ▼
Subject populated with Principals
    │
    ▼
SessionService.createSession()
    │
    ▼
Encrypted SSOToken → Client
```

**Details**: Show the four JAAS control flags with their behavior:
- REQUIRED: Must succeed, continue chain regardless
- REQUISITE: Must succeed, fail immediately if not
- SUFFICIENT: If succeeds and no prior REQUIRED failures, return success
- OPTIONAL: Success/failure doesn't matter

---

### Diagram 14: IAM Decision Framework
**File**: `14-iam-decision-tree`
**Link from**: `chapters/13-comparison-matrices.md`
**Type**: Decision tree / flowchart

```
                    ┌─────────────────┐
                    │ What do you need?│
                    └────────┬────────┘
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │ Access   │  │ Directory│  │ Identity │
         │ Mgmt     │  │ Services │  │ Governance│
         └────┬─────┘  └────┬─────┘  └────┬─────┘
              │              │              │
         Cloud-native?  LDAP required?  Budget?
         ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
         Yes      No   Yes      No   $$       $
         │        │    │        │    │        │
     ┌───┴───┐  OIP  OpenDJ  Postgres SailPoint OpenIDM
     │SaaS ok?│  AM   389 DS  CockroachDB Saviynt  MidPoint
     ┌┴───┐   │
    Yes   No  │
     │    │   │
   Auth0  │  ┌┴──────────┐
   Okta   │  │Microservices?│
   Cognito│  ┌┴────┐      │
          │  Yes   No     │
          │  │     │      │
          │  Ory   Keycloak│
          │  Stack  Zitadel│
          │               │
          └── OIP OpenAM ─┘
              (WS-Fed, XACML,
               full protocol
               coverage)
```

**Additional paths**:
- "Legacy app integration needed?" → OpenIG (credential replay, no modern equivalent)
- "PAM needed?" → CyberArk (enterprise) / HashiCorp Vault (DevOps)
- "ITDR needed?" → CrowdStrike (unified) / Silverfort (agentless) / Entra ID Protection (Microsoft shop)

---

### Diagram 15a: Swim Lane Timeline Part 1 — Origins & Foundations (1960-2005)
**File**: `15a-swimlane-origins`
**Link from**: `chapters/01-history.md`, `chapters/14-lessons-from-history.md`
**Type**: Swim lane timeline (large canvas)

**Lanes** (top to bottom):

#### Lane 1: Authentication Methods
| Period | Item | Status |
|--------|------|--------|
| ~1960s | Passwords (MIT CTSS) | Introduced → still active (declining) |
| 1986 | RSA SecurID hardware tokens | Introduced |
| 1993 | Kerberos V5 (RFC 1510) | Introduced → active |
| ~1990s | SMS OTP | Introduced → deprecated 2017 |
| 2005 | HOTP (RFC 4226) | Introduced |

#### Lane 2: Federation & SSO Protocols
| Period | Item | Status |
|--------|------|--------|
| 2002 | SAML 1.0 | Introduced → deprecated by 2.0 |
| 2003 | SAML 1.1 | Introduced → deprecated |
| 2003 | WS-Federation 1.0 | Introduced → declining |
| 2005 | SAML 2.0 (OASIS) | Introduced → active |

#### Lane 3: Authorization
| Period | Item | Status |
|--------|------|--------|
| ~1970s | ACLs (Unix, NTFS) | Introduced → active |
| ~1992 | RBAC (Ferraiolo-Kuhn paper) | Introduced → active |
| 2003 | XACML 1.0 | Introduced → superseded |
| 2005 | XACML 2.0 | Introduced → superseded |

#### Lane 4: Directory & Identity Stores
| Period | Item | Status |
|--------|------|--------|
| 1988 | X.500 (ITU-T) | Introduced → largely abandoned |
| 1993 | LDAPv1 (RFC 1487) | Introduced → deprecated |
| 1997 | LDAPv3 (RFC 2251) | Introduced → active |
| 1999 | Active Directory | Introduced → active |

#### Lane 5: Token Formats
| Period | Item | Status |
|--------|------|--------|
| 1993 | Kerberos tickets (binary) | Introduced → active |
| 2002 | SAML assertions (XML) | Introduced → active |

#### Lane 6: Products & Platforms
| Period | Item | Status |
|--------|------|--------|
| 2003 | Shibboleth | Introduced → active |
| 2004 | CAS (Apereo) | Introduced → active |
| 2005 | Sun Access Manager / OpenSSO (CDDL) | Launched |

#### Lane 7: Key Events & Standards Bodies
| Date | Event |
|------|-------|
| 1988 | ITU-T publishes X.500 |
| 1993 | IETF publishes LDAPv1, Kerberos V5 |
| 2001 | OASIS formed (from SGML Open) |
| 2004 | OpenID Foundation founded |
| 2005 | OASIS publishes SAML 2.0 |

**Visual treatment**:
- Time axis along the top (1960 → 2005)
- Each lane is a horizontal swim lane with colored bars
- Active items: solid blue bar
- Deprecated/obsolete: gray bar with red "deprecated" marker at end date
- Key events: diamond markers
- Large canvas (~3000px wide) for readability

---

### Diagram 15b: Swim Lane Timeline Part 2 — Modern Era (2005-2026)
**File**: `15b-swimlane-modern`
**Link from**: `chapters/01-history.md`, `chapters/12-modern-architecture.md`, `chapters/14-lessons-from-history.md`
**Type**: Swim lane timeline (large canvas)

**Lanes** (same 7 lanes, continuing):

#### Lane 1: Authentication Methods
| Period | Item | Status |
|--------|------|--------|
| 2005-present | HOTP (RFC 4226) | Active |
| 2010 | Google Authenticator (popularizes TOTP) | Active |
| 2011-present | TOTP (RFC 6238) | Active |
| 2012 | Duo push notifications | Active |
| 2014 | FIDO U2F 1.0 | Active → superseded by FIDO2 |
| 2017 | Platform authenticators (Touch ID, Face ID) | Active |
| 2019 | WebAuthn Level 1 (W3C) | Superseded by L2 |
| 2021 | WebAuthn Level 2 | Active |
| 2022 Jun | Passkeys announced (Apple WWDC) | Active |
| 2022 Sep-Oct | iOS 16 + Android ship passkeys | Active |
| 2023 May | Windows ships passkeys | Active |
| 2024 | Conditional UI maturity | Active |

#### Lane 2: Federation & SSO
| Period | Item | Status |
|--------|------|--------|
| 2007 | OAuth 1.0 | Introduced → deprecated |
| 2012 | OAuth 2.0 (RFC 6749) | Active |
| 2014 | OpenID Connect Core 1.0 | Active |
| 2015 | PKCE (RFC 7636) | Active |
| 2018 | UMA 2.0 | Active |
| 2023 | DPoP (RFC 9449) | Active |
| 2023 | RAR (RFC 9396) | Active |
| TBD | GNAP (in draft) | Draft |

#### Lane 3: Authorization
| Period | Item | Status |
|--------|------|--------|
| 2013 | XACML 3.0 | Active |
| 2018 | OPA/Rego (CNCF) | Active |
| 2019 | Google Zanzibar paper | Published |
| 2022 | OpenFGA (Okta, CNCF) | Active |
| 2023 | Cedar (AWS) | Active |

#### Lane 4: Directory & Identity Stores
| Period | Item | Status |
|--------|------|--------|
| 2006 | OpenDS → OpenDJ | Active |
| 2015 | SCIM 2.0 (RFC 7644) | Active |
| 2018+ | PostgreSQL as identity store (Keycloak, Zitadel) | Growing |
| 2020+ | CockroachDB (Zitadel) | Growing |

#### Lane 5: Token Formats
| Period | Item | Status |
|--------|------|--------|
| 2015 | JWT (RFC 7519) | Active |
| 2018 | Token introspection (RFC 7662) | Active |
| 2020 | Token exchange (RFC 8693) | Active |
| 2022 | SPIFFE SVIDs | Active |
| 2023 | DPoP (RFC 9449) | Active |
| 2024 | SD-JWT VC | Active |
| 2019-2025 | W3C Verifiable Credentials 1.0→2.0 | Active |

#### Lane 6: Products & Platforms
| Period | Item | Status |
|--------|------|--------|
| 2005 | Sun OpenSSO | → Oracle 2010 → ForgeRock 2011 |
| 2014 | Keycloak (Red Hat) | Active |
| 2016 | Ory stack (Go) | Active |
| 2016 Nov | **ForgeRock closes source** | CRISIS EVENT |
| 2017 | ForgeRock CE 11.0.3 frozen | FROZEN |
| 2018 | OIP fork (OpenAM 14.0.0) | Active |
| 2020 | Authentik (Python) | Active |
| 2021 | Zitadel (Go) | Active |
| 2023 | Wren:AM fork (15.0.0-M1) | Active |

#### Lane 7: Key Events
| Date | Event |
|------|-------|
| 2009 | Oracle acquires Sun ($7.4B) |
| 2013 | FIDO Alliance formed |
| 2016 Nov | ForgeRock closes source |
| 2017 | 94% commit velocity drop |
| 2018 | SPIFFE accepted into CNCF |
| 2021 Sep | ForgeRock IPO ($2.8B) |
| 2021 Dec | Log4Shell (CVE-2021-44228) |
| 2022 | SPIRE graduates CNCF |
| 2023 Oct | Thoma Bravo acquires ForgeRock ($2.3B) → PingIdentity merger |
| 2024 | eIDAS 2.0 regulation (EU digital identity) |

**Visual treatment**:
- Same style as Part 1 for visual continuity
- ForgeRock closure (Nov 2016) as a dramatic red vertical line spanning all lanes
- Fork divergence shown as branching paths in Lane 6
- The "passwordless" trajectory in Lane 1 highlighted (FIDO→WebAuthn→Passkeys) with a green "future direction" glow
- Deprecated items fade to gray
- Large canvas (~4000px wide) — this era has more density

---

## Chapter Linking Plan

After all diagrams are generated, insert image references in these chapters:

| Diagram | Insert in Chapter | After Section |
|---------|------------------|---------------|
| 01 | README.md | "How the Components Fit Together" |
| 01 | 07-openam-analysis.md | Section 1 intro |
| 02 | 07-openam-analysis.md | Production Deployment Topology section |
| 03 | 09-openidm-analysis.md | Architecture section |
| 04 | 01-history.md | Near top, after intro paragraph |
| 05 | 02-authentication-protocols.md or 03-federation-protocols.md | Protocol timeline section |
| 06 | 01-history.md | Fork Divergence section |
| 07 | 03-federation-protocols.md | SAML section |
| 08 | 03-federation-protocols.md | OAuth2/OIDC section |
| 09 | 04-authorization-frameworks.md | XACML section |
| 10 | 06-token-formats.md | Token lifecycle section |
| 11 | 12-modern-architecture.md | Landscape overview |
| 12 | 13-comparison-matrices.md | Workload Identity section |
| 13 | 07-openam-analysis.md | Authentication chain section |
| 14 | 13-comparison-matrices.md | Decision Framework section |
| 15a | 01-history.md + 14-lessons-from-history.md | Near top |
| 15b | 01-history.md + 12-modern-architecture.md | Modern era section |

**Image syntax**: `![Diagram Title](../diagrams/NN-short-name.png)`

---

## Execution Notes

1. **Parallelism**: Diagrams 01-03 (architecture), 04-06 (timeline/comparison), 07-10 (protocol flows), 11-14 (landscape/decisions), 15a-15b (swim lanes) can be done in 5 parallel batches
2. **Color consistency**: All diagrams should use the same palette (#1C2833, #2E4053, #5DADE2, #F4F6F6, #F39C12, #E74C3C)
3. **Canvas sizes**: Standard diagrams ~1600x900px, swim lane timelines ~3000-4000px wide x 1200px tall
4. **Font**: Use default Excalidraw hand-drawn font for consistency
5. **After generation**: Run `git add docs/diagrams/ && git commit` to checkpoint, then edit chapters to add links in a second commit
