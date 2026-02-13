# Identity Standards Evolution Timeline

## Executive Summary

Identity and access management standards have evolved over three decades from
directory-centric protocols to decentralized, zero-trust architectures.

**Key inflection points:**

- **1993**: LDAP (RFC 1487) simplified X.500 directory access, becoming the
  universal identity store protocol. LDAPv3 (RFC 2251, 1997) added SASL,
  TLS, and extensibility that remains the backbone of enterprise IAM today.
- **1993-1997**: Kerberos V5 (RFC 1510, 1993; updated RFC 4120, 2005) and
  RADIUS (RFC 2058, 1997; updated RFC 2865, 2000) established network
  authentication and authorization for on-premises and dial-up environments.
- **2002-2005**: SAML (OASIS, 2002-2005) delivered cross-domain SSO for
  enterprises. WS-Federation and Liberty Alliance competed but SAML 2.0
  became the dominant enterprise federation standard.
- **2007-2014**: OAuth 1.0 (2007), OAuth 2.0 (RFC 6749, 2012), and OpenID
  Connect (2014) shifted the industry toward API-centric, token-based
  authorization and consumer-scale federated authentication.
- **2003-2013**: XACML promised fine-grained policy-based authorization but
  complexity limited adoption. Simpler alternatives (OPA/Rego 2018,
  Cedar 2023) gained traction.
- **2011-2015**: SCIM (RFC 7642-7644, 2015) standardized identity
  provisioning, achieving broad SaaS adoption where SPML had failed.
- **2014-2022+**: FIDO U2F (2014), FIDO2/WebAuthn (W3C 2019), and Passkeys
  (2022+) are eliminating passwords with phishing-resistant credentials.
  Apple, Google, and Microsoft all shipped passkey support by late 2023.
- **2015-2018**: UMA 2.0 (Kantara, 2018) standardized user-managed resource
  sharing but adoption remained niche outside healthcare.
- **2019-present**: W3C Verifiable Credentials (2019/2022) and DIDs (2022)
  promise self-sovereign identity but production deployments are limited.
- **2020-present**: NIST SP 800-207 (2020) codified Zero Trust Architecture;
  US EO 14028 (2021) mandated federal adoption, driving industry-wide change.

**Current trajectory**: The industry is converging on OAuth 2.0 / OIDC for
authentication/authorization, passkeys for credentials, SCIM for provisioning,
and zero-trust principles for architecture. Legacy protocols (LDAP, SAML,
Kerberos) remain entrenched in enterprise environments but are increasingly
wrapped behind modern APIs and gateways.

---

## Detailed Findings

### Directory Protocols

#### X.500 and DAP (The Predecessor)

- **1988**: ITU-T X.500 series published (X.500, X.501, X.509, X.511, X.518,
  X.519, X.520, X.521). Defined the Directory Access Protocol (DAP) over the
  full OSI stack. Extremely heavyweight -- required a complete OSI
  implementation.
- **1993**: X.500 (1993 edition) added access control and replication. Still
  too complex for widespread adoption on TCP/IP networks.
- X.500 introduced the distinguished name (DN) hierarchy and the information
  model that LDAP inherited wholesale.

#### LDAP Evolution

| Year | Version | RFC(s) | Key Changes |
|------|---------|--------|-------------|
| 1993 | LDAPv1 | RFC 1487 | Lightweight X.500 access over TCP. Read-only subset of DAP. Tim Howes, Steve Kille, Colin Robbins, Wengyik Yeong at U-Michigan. |
| 1995 | LDAPv2 | RFC 1777, 1778, 1779 | Added write operations (add, delete, modify, modrdn). Simple bind authentication. String representation of DNs (RFC 1779). |
| 1997 | LDAPv3 | RFC 2251-2256 | Major revision: SASL authentication framework, TLS (StartTLS), extensible controls and extended operations, UTF-8, referrals, schema publication. Became an Internet Standard. |
| 2006 | LDAPv3 (revised) | RFC 4510-4519 | Technical specification refresh. RFC 4510 (roadmap), 4511 (protocol), 4512 (info models), 4513 (auth methods), 4514 (DN string), 4515 (search filters), 4516 (URL), 4517 (syntaxes), 4518 (internationalized matching), 4519 (schema). Obsoleted RFC 2251-2256. |
| 2006 | LDIF | RFC 2849 (1999) | LDAP Data Interchange Format -- text representation of entries and changes. Universally supported for import/export. |

#### Key LDAP Extensions

- **RFC 3062 (2001)**: Password Modify Extended Operation
- **RFC 3296 (2002)**: Referrals in LDAP
- **RFC 3671-3672 (2003)**: Collective attributes
- **RFC 3909 (2004)**: Cancel operation
- **RFC 4370 (2006)**: Proxied Authorization Control
- **RFC 4532 (2006)**: "Who am I?" extended operation
- **RFC 4533 (2006)**: Content Synchronization (syncrepl) -- critical for
  replication (used by OpenDJ, 389DS, OpenLDAP)
- **RFC 5805 (2010)**: Transactions over LDAP

#### LDAP Current Status

- **Active**: LDAPv3 remains the universal directory protocol. Every major
  identity platform (Active Directory, OpenDJ, OpenLDAP, 389 Directory Server,
  Ping Directory) implements it.
- **Cloud directories**: Azure AD (now Entra ID), Google Workspace, and AWS
  Directory Service all provide LDAP interfaces, often backed by proprietary
  stores.
- **Virtual directories**: Products like Radiant Logic provide LDAP facades
  over heterogeneous identity sources (SQL, REST, LDAP, flat files).
- LDAP is unlikely to be displaced for enterprise directory access but is
  increasingly hidden behind REST/GraphQL APIs (e.g., SCIM, Microsoft Graph).

---

### Authentication Standards

#### RADIUS

| Year | Event | Reference |
|------|-------|-----------|
| 1991 | Livingston Enterprises creates RADIUS for dial-up authentication at Merit Network | Internal spec |
| 1994 | First IETF draft | draft-ietf-radius-protocol |
| 1997 | RADIUS published | RFC 2058 (auth), RFC 2059 (accounting) |
| 2000 | RADIUS updated | RFC 2865 (auth), RFC 2866 (accounting) -- the definitive versions |
| 2003 | RADIUS over EAP | RFC 3579 -- enables 802.1X / Wi-Fi authentication |
| 2003 | RADIUS Accounting updates | RFC 2867 (tunnel accounting), RFC 2868-2869 (tunnel/extensions) |
| 2005 | Dynamic Authorization (CoA/Disconnect) | RFC 3576 (obsoleted by RFC 5176, 2008) |
| 2008 | RADIUS design guidelines | RFC 5080 |
| 2012 | RadSec (RADIUS over TLS) | RFC 6614 -- addresses RADIUS's inherent UDP/shared-secret weaknesses |
| 2020 | RADIUS over DTLS | RFC 7360 (experimental, 2014); continued work in IETF RADEXT WG |

**Current status**: Active but aging. RADIUS remains dominant for network
access (Wi-Fi, VPN), but the IETF RADEXT working group is developing
"RADIUS/TLS" to address fundamental security issues (MD5 dependency, shared
secrets). RADIUS is being supplanted by OAuth 2.0 / OIDC for application-layer
authentication.

#### Kerberos

| Year | Event | Reference |
|------|-------|-----------|
| 1983 | Project Athena begins at MIT | MIT internal |
| 1986 | Kerberos V1-V3 | Internal MIT development (never publicly released) |
| 1989 | Kerberos V4 | Released with MIT Project Athena. Used DES encryption. |
| 1993 | Kerberos V5 | RFC 1510 -- Extensible framework, ASN.1 encoding, cross-realm auth, forwardable/renewable tickets |
| 2005 | Kerberos V5 updated | RFC 4120 -- Obsoleted RFC 1510. Clarifications, encryption framework improvements |
| 2005 | Kerberos V5 crypto framework | RFC 3961 -- Generalized encryption/checksum framework |
| 2005 | AES encryption for Kerberos | RFC 3962 -- Replaced DES (broken) with AES |
| 2005 | PKINIT | RFC 4556 -- Public key cryptography for initial Kerberos authentication (smartcards/certs) |
| 2006 | SPNEGO/Negotiate | RFC 4178 -- GSS-API negotiation mechanism (used by HTTP Negotiate / "Integrated Windows Auth") |
| 2012 | Kerberos with camellia | RFC 6803 |
| 2017 | Deprecation of DES/RC4 | RFC 8429 -- DES and RC4 marked as deprecated |

**Current status**: Active. Kerberos V5 is foundational to Microsoft Active
Directory. Every Windows domain uses Kerberos for authentication. Also used in
Hadoop/big data ecosystems. However, Kerberos is complex to deploy outside AD
and is rarely used in greenfield cloud-native applications.

#### X.509 Certificates Evolution

| Year | Event | Reference |
|------|-------|-----------|
| 1988 | X.509 v1 | ITU-T X.509 (1988) -- Basic certificate structure |
| 1993 | X.509 v2 | Added issuer/subject unique identifiers |
| 1996 | X.509 v3 | Added extensions framework (key usage, SANs, CRL distribution points, etc.) |
| 1999 | PKIX profile | RFC 2459 -- Internet profile for X.509 certs and CRLs |
| 2002 | PKIX updated | RFC 3280 -- Obsoleted RFC 2459 |
| 2008 | PKIX updated again | RFC 5280 -- Current definitive Internet PKI profile. Widely implemented. |
| 2013 | Certificate Transparency | RFC 6962 -- Append-only logs for TLS cert issuance auditing |
| 2015 | Let's Encrypt launches | Free, automated DV certificates via ACME protocol |
| 2019 | ACME protocol | RFC 8555 -- Automated Certificate Management Environment |
| 2021 | CT v2 | RFC 9162 -- Updated Certificate Transparency |

**Current status**: Active and essential. X.509v3 certificates are the
foundation of TLS/HTTPS. The CA/Browser Forum governs trust requirements.
Let's Encrypt has issued billions of free certificates, democratizing HTTPS.
Certificate-based mutual TLS (mTLS) is increasingly used in zero-trust and
service mesh architectures.

#### Passwordless Authentication Evolution

| Year | Method | Notes |
|------|--------|-------|
| ~1990s | Hardware OTP tokens | RSA SecurID (1986), OATH HOTP later standardized in RFC 4226 (2005) |
| ~2000s | SMS OTP | Widely deployed; now deprecated by NIST SP 800-63B (2017) due to SIM-swap/SS7 attacks |
| 2005 | HOTP | RFC 4226 -- HMAC-based One-Time Password. Event-based counter. |
| 2011 | TOTP | RFC 6238 -- Time-based One-Time Password. 30-second window. Google Authenticator (2010) popularized it. |
| ~2012 | Push notifications | Duo Security (2010), Microsoft Authenticator. "Approve" model. |
| 2014 | FIDO U2F | FIDO Alliance 1.0. USB security keys (Yubico). See Strong Authentication section. |
| 2017 | Platform authenticators | Touch ID/Face ID, Windows Hello. On-device biometrics for WebAuthn. |
| 2019 | WebAuthn L1 | W3C Recommendation. See Strong Authentication section. |
| 2021 | WebAuthn L2 | Added resident keys, large blob storage, enterprise attestation |
| 2022 | Synced passkeys | Apple (WWDC 2022), Google, Microsoft. Cross-device passkeys synced via cloud. |
| 2023 | Device-bound passkeys | Enterprise variant -- keys tied to specific hardware (e.g., YubiKey 5). Not synced. |
| 2024 | Conditional UI | Autofill-integrated passkey selection. Supported in Chrome, Safari, Edge. |

---

### SAML & Legacy Federation

#### SAML (Security Assertion Markup Language)

| Year | Version | Key Details |
|------|---------|-------------|
| 2001 | S2ML, AuthXML | Competing pre-SAML specs from Netegrity and others. OASIS formed Security Services TC to unify. |
| 2002 Nov | SAML 1.0 | OASIS Standard. XML-based assertions (authentication, attribute, authorization). Browser/POST and Artifact profiles. |
| 2003 Sep | SAML 1.1 | OASIS Standard. Minor clarifications, error handling improvements. |
| 2004 | Liberty Alliance ID-FF 1.2 | Built on SAML; added circle-of-trust federation, single logout, name ID management. |
| 2005 Mar | SAML 2.0 | OASIS Standard. Merged SAML 1.1 + Liberty ID-FF 1.2 + Shibboleth. Major rewrite: new XML schema, metadata, enhanced bindings (HTTP-Redirect, HTTP-POST, HTTP-Artifact, SOAP, PAOS), persistent/transient name IDs, single logout, ECP. |
| 2008 | SAML 2.0 Profiles | Additional profiles: Holder-of-Key, Delegation, ECP (Enhanced Client or Proxy) |
| 2012 | SAML 2.0 Errata | OASIS approved errata (sstc-saml-approved-errata-2.0) |
| 2019 | SAML 2.0 Metadata extensions | Metadata interoperability profile, entity categories (REFEDS/InCommon) |

**Key specifications composing SAML 2.0**:
- `saml-core-2.0-os` -- Assertions and Protocols
- `saml-bindings-2.0-os` -- Protocol Bindings
- `saml-profiles-2.0-os` -- Profiles (Web Browser SSO, ECP, SLO, etc.)
- `saml-metadata-2.0-os` -- Metadata schema
- `saml-authn-context-2.0-os` -- Authentication Context
- `saml-conformance-2.0-os` -- Conformance Requirements
- `saml-glossary-2.0-os` -- Glossary
- `saml-sec-consider-2.0-os` -- Security and Privacy Considerations

**Current status**: Active and deeply entrenched. SAML 2.0 remains the
dominant enterprise federation protocol. Virtually every enterprise IdP
(Okta, Azure AD/Entra, Ping, OneLogin, Shibboleth) supports it. Education
(InCommon, eduGAIN), government (FedRAMP, FICAM), and healthcare rely heavily
on SAML. No successor has displaced it in enterprise B2B federation, though
OIDC is preferred for new consumer/SaaS integrations.

#### WS-Federation and WS-Trust

| Year | Event | Reference |
|------|-------|-----------|
| 2002 | WS-Security 1.0 | IBM/Microsoft/Verisign. SOAP message security. OASIS Standard 2004. |
| 2003 | WS-Trust 1.0 | IBM/Microsoft. Security Token Service (STS) for token issuance/exchange. |
| 2003 | WS-Federation 1.0 | IBM/Microsoft/BEA/VeriSign/RSA. Passive (browser) and active (SOAP) federation. |
| 2006 | WS-Trust 1.3 | OASIS Standard. Refined STS, token renewal, validation, cancellation. |
| 2009 | WS-Federation 1.2 | OASIS Standard. Passive requestor (browser-based) profile widely implemented in ADFS. |

**Current status**: Mostly deprecated for new projects. WS-Federation is still
used by Microsoft ADFS (Active Directory Federation Services) environments, but
Microsoft itself now recommends OIDC/OAuth 2.0. WS-Trust's STS concept
influenced OAuth 2.0's Token Exchange (RFC 8693). The WS-* stack (WS-Security,
WS-Policy, WS-SecureConversation) is maintained only for legacy SOAP services.

#### Liberty Alliance

| Year | Event | Reference |
|------|-------|-----------|
| 2001 | Liberty Alliance founded | Sun Microsystems, AOL, HP, Nokia, others. Response to Microsoft Passport. |
| 2003 | Liberty ID-FF 1.2 | Identity Federation Framework. Circle-of-trust model. |
| 2004 | Liberty ID-WSF 1.0 | Identity Web Services Framework. Attribute sharing, discovery. |
| 2005 | Merged into SAML 2.0 | Core ID-FF concepts absorbed into SAML 2.0. |
| 2009 | Kantara Initiative formed | Liberty Alliance wound down; Kantara took over UMA, consent management. |

**Current status**: Deprecated. Liberty Alliance's contributions live on inside
SAML 2.0. The organization itself dissolved into the Kantara Initiative.

---

### OAuth & OpenID

#### OpenID (Pre-OIDC)

| Year | Version | Key Details |
|------|---------|-------------|
| 2005 | OpenID 1.0 | Brad Fitzpatrick (LiveJournal). URL-based decentralized identity. User is identified by a URL. |
| 2006 | OpenID 1.1 | Minor update. Yadis discovery protocol. |
| 2007 | OpenID 2.0 | OpenID Foundation. Added XRI identifiers, Attribute Exchange (AX), claimed identifier discovery. |
| 2008 | OpenID AX 1.0 | Attribute Exchange -- request user attributes from providers. |
| 2009-2011 | Peak adoption | Yahoo, Google, AOL, MySpace supported OpenID 2.0. Estimated 1B+ OpenID-enabled accounts. |
| 2014 | Effectively superseded | OpenID Connect built on OAuth 2.0 replaced OpenID 2.0. Google, Yahoo deprecated OpenID 2.0 endpoints. |

**Current status**: Deprecated. OpenID 2.0 is no longer supported by major
providers. Replaced entirely by OpenID Connect.

#### OAuth

| Year | Version / Event | Reference |
|------|-----------------|-----------|
| 2006 | Twitter + Ma.gnolia discuss delegated auth | Led to OAuth concept |
| 2007 | OAuth 1.0 | Community spec. Cryptographic signatures on every request (HMAC-SHA1). |
| 2009 | OAuth 1.0 Session Fixation attack | Eran Hammer disclosed. Led to OAuth 1.0a. |
| 2009 | OAuth 1.0a | RFC 5849 (informational, published 2010). Fixed session fixation. Added `oauth_verifier`. |
| 2010 | IETF OAuth WG formed | Chartered to produce OAuth 2.0 |
| 2012 Oct | OAuth 2.0 | **RFC 6749** (framework), **RFC 6750** (bearer tokens). Major redesign: no signatures on requests, relies on TLS. Introduced grant types: authorization code, implicit, resource owner password, client credentials. |
| 2012 | OAuth 2.0 Threat Model | RFC 6819 -- Comprehensive threat analysis |
| 2015 | PKCE | **RFC 7636** -- Proof Key for Code Exchange. Mitigates authorization code interception for public clients (mobile apps). |
| 2017 | OAuth 2.0 for Native Apps | **RFC 8252** -- Best practices: use system browser, PKCE mandatory. |
| 2018 | Token Introspection | **RFC 7662** (2015). Allows resource servers to validate opaque tokens. |
| 2018 | Token Revocation | **RFC 7009** (2013). Endpoint for revoking access/refresh tokens. |
| 2019 | Device Authorization Grant | **RFC 8628**. For input-constrained devices (Smart TVs, CLI tools). |
| 2019 | OAuth 2.0 Security BCP | **RFC 6819** updated by draft-ietf-oauth-security-topics. Implicit flow deprecated. PKCE for all clients. |
| 2020 | Token Exchange | **RFC 8693**. Standardized STS-like token exchange (act-as, on-behalf-of). |
| 2020 | OAuth 2.0 for Browser-Based Apps | draft-ietf-oauth-browser-based-apps. BFF pattern recommended. |
| 2020 | Pushed Authorization Requests (PAR) | **RFC 9126** (published 2021). Pre-register auth requests for integrity. |
| 2021 | DPoP | **RFC 9449** (published 2023). Demonstration of Proof-of-Possession. Sender-constrained tokens without mTLS. |
| 2021 | Rich Authorization Requests (RAR) | **RFC 9396** (published 2023). Fine-grained `authorization_details` parameter. |
| 2023 | OAuth 2.1 | **draft-ietf-oauth-v2-1**. Consolidation: PKCE mandatory, no implicit flow, no password grant, refresh token rotation. Not yet RFC as of mid-2025. |
| 2020-present | GNAP | **Grant Negotiation and Authorization Protocol**. draft-ietf-gnap-core-protocol. IETF GNAP WG. Designed as "OAuth 3.0" but with different philosophy: interaction-centric, not redirect-centric. Still in draft. |

**OAuth 2.0 grant types summary**:
- **Authorization Code** (+ PKCE): Standard for web and native apps
- **Client Credentials**: Machine-to-machine (no user)
- **Device Authorization**: Input-constrained devices
- **Token Exchange (RFC 8693)**: STS-style delegation
- **~~Implicit~~**: Deprecated (OAuth 2.1 / Security BCP)
- **~~Resource Owner Password~~**: Deprecated (OAuth 2.1)

**Current status**: OAuth 2.0 is the dominant authorization framework. OAuth
2.1 is nearing completion as an RFC to codify current best practices. GNAP is
still experimental with no significant production adoption.

#### OpenID Connect (OIDC)

| Year | Version / Event | Reference |
|------|-----------------|-----------|
| 2011 | OpenID Connect development begins | OpenID Foundation. Built as identity layer on OAuth 2.0. |
| 2014 Feb | OpenID Connect Core 1.0 | Final specification. ID Token (JWT), UserInfo endpoint, standard claims, auth request parameters. |
| 2014 | OIDC Discovery 1.0 | `/.well-known/openid-configuration` metadata endpoint. |
| 2014 | OIDC Dynamic Registration 1.0 | Programmatic client registration. |
| 2014 | OIDC Session Management 1.0 | Front-channel/back-channel logout. |
| 2015 | OIDC for Identity Assurance | IDA (Identity Assurance) specification started. |
| 2017 | OIDC Back-Channel Logout 1.0 | Logout tokens pushed to RPs via back-channel. More reliable than front-channel. |
| 2019 | OIDC CIBA | Client-Initiated Backchannel Authentication. Decoupled auth flow (user authenticates on separate device). Important for PSD2/Open Banking. |
| 2021 | OIDC Federation 1.0 | Draft. Automatic trust establishment between OIDC entities via trust chains. Eliminates manual metadata exchange. |
| 2022 | OIDC for Verifiable Presentations | OpenID4VP. Present Verifiable Credentials via OIDC flows. |
| 2022 | OIDC for Verifiable Credential Issuance | OpenID4VCI. Issue VCs through OIDC mechanisms. |
| 2023 | OIDC Shared Signals Framework (SSF) | Formerly RISC + CAEP. Real-time security event sharing between providers (RFC 8935 SET). |
| 2024 | OIDC Federation gaining traction | EU Digital Identity Wallet (eIDAS 2.0) references OIDC Federation for trust infrastructure. |

**Key OIDC specifications**:
- `openid-connect-core-1_0` -- Core: authentication, ID Token, claims
- `openid-connect-discovery-1_0` -- Provider metadata discovery
- `openid-connect-registration-1_0` -- Dynamic client registration
- `openid-connect-rpinitiated-1_0` -- RP-Initiated Logout
- `openid-connect-backchannel-1_0` -- Back-Channel Logout
- `openid-connect-frontchannel-1_0` -- Front-Channel Logout

**Current status**: Active and growing. OIDC is the preferred protocol for new
identity integrations. Supported by all major IdPs (Google, Microsoft, Apple,
Okta, Auth0, Keycloak, OpenAM). OpenID4VC/VP and OIDC Federation are active
areas of development, especially for EU digital identity wallets.

---

### Authorization Standards

#### XACML (eXtensible Access Control Markup Language)

| Year | Version | Reference | Key Changes |
|------|---------|-----------|-------------|
| 2003 Feb | XACML 1.0 | OASIS Standard | XML-based policy language. PDP/PEP/PIP/PAP architecture. Subject/Resource/Action/Environment attributes. |
| 2005 Feb | XACML 2.0 | OASIS Standard | Obligations, policy combining algorithms improvements, hierarchical resources, multiple decision profile. |
| 2010 | XACML 3.0 Committee Draft | OASIS | Major rework: simplified policy language, `<Match>`, new combining algorithms, administrative delegation, JSON profile. |
| 2013 Jan | XACML 3.0 | OASIS Standard | Final release. Added JSON request/response profile, REST profile, SAML profile, multiple resource profile. |
| 2014 | XACML 3.0 JSON Profile | OASIS Committee Spec | JSON alternative to XML for requests/responses (addressing developer friction). |
| 2014 | ALFA (Abbreviated Language for Authorization) | Axiomatics proprietary | Human-readable DSL for XACML policies. Highlighted XACML's verbosity problem. |

**Why XACML adoption stalled**:
1. **Complexity**: XML policies are verbose and hard to author/debug
2. **Performance**: Real-time PDP evaluation with network round-trips to PIP
   added latency
3. **Developer friction**: No native SDK ecosystem; XML-heavy in a JSON world
4. **Deployment complexity**: PDP/PEP/PIP/PAP architecture requires multiple
   infrastructure components
5. **Lack of cloud-native tooling**: No Kubernetes-native, no serverless
   integration
6. **Vendor lock-in**: Most implementations were commercial (Axiomatics, IBM)

**What replaced/supplements XACML**:

| Year | Alternative | Notes |
|------|-------------|-------|
| 2018 | Open Policy Agent (OPA) / Rego | CNCF graduated project. General-purpose policy engine. Rego language is purpose-built, declarative. Kubernetes-native (Gatekeeper). Wide cloud-native adoption. |
| 2019 | Casbin | Open-source library. Supports RBAC, ABAC, ACL in 15+ languages. Embeddable. |
| 2021 | Google Zanzibar (2019 paper) | Inspired SpiceDB, Authzed, OpenFGA, Ory Keto. Relationship-based access control (ReBAC). |
| 2022 | OpenFGA | Open-source ReBAC implementation by Okta/Auth0. Based on Zanzibar model. CNCF sandbox. |
| 2023 | Cedar (AWS) | Policy language from AWS (used in Amazon Verified Permissions). Formal verification. Decidable, analyzable. Open-sourced. |
| 2023 | Topaz / OpenPolicyContainers | Aserto's open-source authorization. Combines OPA + directory. |

**Current status**: XACML 3.0 is an active OASIS standard but new deployments
are rare. OPA dominates cloud-native policy evaluation. Cedar and Zanzibar-
derived systems (OpenFGA, SpiceDB) are growing rapidly for application-level
authorization. The trend is toward embeddable, developer-friendly policy
engines rather than centralized PDP infrastructure.

---

### Provisioning Standards

#### SPML (Predecessor)

| Year | Version | Reference |
|------|---------|-----------|
| 2003 Oct | SPML 1.0 | OASIS Standard. Service Provisioning Markup Language. XML/SOAP based. |
| 2006 Apr | SPML 2.0 | OASIS Standard. More flexible, still XML/SOAP. |

**Status**: Deprecated. SPML failed due to SOAP complexity, limited vendor
adoption, and the industry shift to REST. Replaced by SCIM.

#### SCIM (System for Cross-domain Identity Management)

| Year | Version | Reference | Key Details |
|------|---------|-----------|-------------|
| 2011 | SCIM 1.0 | draft-scim-core-schema-00 | Initial draft by Salesforce, Cisco, Google, others. RESTful provisioning over JSON. |
| 2012 | SCIM 1.1 | IETF draft | Widely implemented despite being a draft (Salesforce, Google Apps). |
| 2015 Sep | SCIM 2.0 | **RFC 7642** (concepts), **RFC 7643** (core schema), **RFC 7644** (protocol) | IETF Proposed Standard. JSON/REST, `/Users`, `/Groups`, `/Schemas`, `/ResourceTypes`, `/ServiceProviderConfig` endpoints. CRUD + PATCH + bulk + filtering. |

**SCIM 2.0 key design decisions**:
- RESTful HTTP verbs (GET, POST, PUT, PATCH, DELETE)
- JSON payloads (no XML)
- Standard schema for Users and Groups (extensible)
- Filter syntax: `filter=userName eq "bjensen"`
- Bulk operations for efficiency
- ETags for concurrency control

**Real-world adoption**:
- **Widely adopted**: Microsoft Entra ID (Azure AD), Okta, OneLogin,
  Salesforce, Google Workspace, Slack, Zoom, AWS IAM Identity Center,
  Atlassian, ServiceNow, Workday
- **Estimated**: 70%+ of major SaaS providers support SCIM 2.0 provisioning
- **Limitations**: Schema negotiation is underspecified, PATCH semantics vary
  between implementations, no standard for password sync, no event/webhook
  standard (addressed by OIDC Shared Signals / SSF)

**Current status**: Active and dominant for cloud identity provisioning. The
IETF SCIM WG has been rechartered (2023) to work on SCIM 2.1 improvements
including events/signals integration and schema discovery enhancements.

---

### Strong Authentication & Passkeys

#### FIDO Alliance Timeline

| Year | Standard / Event | Key Details |
|------|------------------|-------------|
| 2012 Jul | FIDO Alliance founded | PayPal, Lenovo, Nok Nok Labs, Validity Sensors, Infineon, Agnitio. Mission: reduce reliance on passwords. |
| 2014 Dec | FIDO U2F 1.0 | Universal 2nd Factor. USB HID protocol for security keys. Challenge-response with public key crypto. Per-origin key pairs prevent phishing. |
| 2014 Dec | FIDO UAF 1.0 | Universal Authentication Framework. Passwordless biometric authentication on mobile devices. |
| 2015 | Google deploys U2F internally | Google mandated security keys for all employees. Reduced phishing to zero. Published at USENIX 2016. |
| 2016 | FIDO U2F 1.2 | NFC and Bluetooth Low Energy (BLE) transport support. |
| 2018 | FIDO2 Project announced | FIDO Alliance + W3C collaboration. Two components: WebAuthn (W3C) + CTAP (FIDO). |
| 2018 Apr | CTAP 1 (U2F renamed) | Client to Authenticator Protocol. Backward-compatible with U2F. |
| 2019 Mar | **WebAuthn Level 1** | **W3C Recommendation**. Browser API (`navigator.credentials.create/get`) for public key credential management. Supported in Chrome, Firefox, Edge, Safari. |
| 2019 | CTAP 2.0 | Added resident credentials (discoverable keys stored on authenticator), PIN/biometric verification, HMAC-secret extension. |
| 2021 Apr | **WebAuthn Level 2** | **W3C Recommendation**. Added: enterprise attestation, large blob storage, credential management, cross-origin iframes, Apple attestation format. |
| 2021 | CTAP 2.1 | Credential management, authenticator config, min PIN length, `credProtect` policy. |
| 2022 Jun | **Passkeys announced** | Apple (WWDC 2022), Google, Microsoft joint commitment. "Passkeys" = synced WebAuthn credentials stored in platform credential managers. |
| 2022 Sep | iOS 16 ships passkeys | Apple: iCloud Keychain sync, cross-device auth via QR/BLE hybrid. |
| 2022 Oct | Android ships passkeys | Google: passkeys in Google Password Manager, Chrome support. |
| 2023 May | Windows ships passkeys | Microsoft: Windows Hello passkey support in Windows 11 23H2. |
| 2023 Sep | 1Password, Dashlane support | Third-party password managers can store/sync passkeys. |
| 2023 | GitHub, Google, Amazon, PayPal | Major services offer passkey sign-in. |
| 2024 | **WebAuthn Level 3** | W3C Working Draft. Signal API, attestation improvements. |
| 2024 | Conditional UI maturity | Passkey autofill in browser credential pickers. Chrome, Safari, Edge all support. Seamless UX. |
| 2024 | FIDO Alliance: CXP, CXF | Credential Exchange Protocol/Format for migrating passkeys between providers. |
| 2025 | Enterprise passkey adoption growing | Device-bound passkeys (YubiKey 5, Titan Key) for regulated environments. Synced passkeys for consumer/workforce. |

**Passkey types**:
- **Synced passkeys**: Stored in platform credential manager (iCloud Keychain,
  Google Password Manager, 1Password). Survive device loss. Cross-device.
  Trade-off: cloud backup is a potential attack surface.
- **Device-bound passkeys**: Tied to specific hardware authenticator (YubiKey,
  Titan). Cannot be extracted. Higher assurance but no recovery without backup
  key.

**Phishing resistance**: Both types are phishing-resistant by design. The
origin is bound into the cryptographic challenge -- a credential created for
`example.com` cannot be used on `examp1e.com`. This is the fundamental security
advantage over passwords, SMS OTP, and TOTP.

**Enterprise adoption data** (approximate, 2024-2025):
- Google: 100% employee usage (security keys since 2015, passkeys since 2023)
- Microsoft: Passkey support in Entra ID since 2024
- Okta: Passkey support in Workforce Identity
- FIDO Alliance reports 12B+ accounts passkey-enabled as of 2024

---

### UMA (User-Managed Access)

| Year | Version / Event | Reference |
|------|-----------------|-----------|
| 2010 | UMA WG formed at Kantara Initiative | Eve Maler (lead). Goal: user-centric consent and resource sharing. |
| 2015 Apr | UMA 1.0 | Kantara Recommendation. Built on OAuth 2.0. Resource owner registers resources at Authorization Server (AS). Requesting party gets RPT (Requesting Party Token) after consent. |
| 2018 Jan | UMA 2.0 | Kantara Recommendation. Simplified: uses OAuth 2.0 grant type (UMA grant). Removed resource set registration API changes. Three main specs: Grant, Federated Authorization, Resource Registration. |
| 2020 | UMA 2.0 implementations | Gluu Server, ForgeRock/OpenAM, Keycloak, WSO2 IS, MITREid Connect (limited) |

**UMA 2.0 architecture**:
- **Resource Owner**: Controls access policies at the AS
- **Authorization Server**: Issues RPTs, evaluates policies, collects claims
- **Resource Server**: Protects resources, registers them at AS
- **Client/Requesting Party**: Requests access, presents claims

**Why UMA didn't achieve wider adoption**:
1. **Complexity**: Three-party auth (resource owner, requesting party, AS) is
   inherently more complex than two-party OAuth
2. **UX challenges**: Users don't want to manage fine-grained resource policies
3. **Chicken-and-egg problem**: Few resource servers support UMA, so few
   clients implement it
4. **OAuth 2.0 sufficiency**: Most delegation use cases are adequately served
   by standard OAuth scopes
5. **Enterprise vs consumer mismatch**: Designed for user empowerment but
   enterprises prefer centralized policy control
6. **Limited vendor investment**: Only a few IdPs implemented it fully

**Where UMA found niche adoption**:
- **Healthcare**: Patient-controlled health data sharing (e.g., Kantara's
  Health Relationship Trust -- HEART WG profiles UMA for healthcare)
- **Financial services**: Open banking consent management (limited)
- **Personal data stores**: MyData, Solid project concepts overlap with UMA

**Current status**: UMA 2.0 is an active Kantara specification but adoption
remains niche. The broader concept of user-managed consent is being addressed
by regulation (GDPR consent, Open Banking) rather than a single protocol.

---

### Decentralized Identity

#### W3C Verifiable Credentials

| Year | Event | Reference |
|------|-------|-----------|
| 2017 | W3C Verifiable Claims WG formed | Renamed to Verifiable Credentials WG |
| 2019 Nov | **Verifiable Credentials Data Model 1.0** | **W3C Recommendation**. JSON-LD based. Issuer -> Holder -> Verifier model. Supports multiple proof types (JWT, LD-Proofs). |
| 2021 | VC-JWT representation | JWTs as an alternative to JSON-LD for VC encoding. Simpler for developers. |
| 2022 | Verifiable Credentials Data Model 1.1 | W3C Recommendation. Clarifications, improved JWT encoding. |
| 2023 | **VC Data Model 2.0** | W3C Candidate Recommendation. Simplified base context, multiple securing mechanisms (VC-JOSE-COSE, Data Integrity), removed ZKP-specific features into separate specs. |
| 2023 | VC-JOSE-COSE | Securing VCs with JOSE (JWS/JWE) and COSE. SD-JWT VC for selective disclosure. |
| 2024 | SD-JWT VC | IETF draft. Selective Disclosure JWT for Verifiable Credentials. EU Digital Identity Wallet candidate format. |

#### Decentralized Identifiers (DIDs)

| Year | Event | Reference |
|------|-------|-----------|
| 2016 | DID concept emerges | Drummond Reed, Manu Sporny, others in W3C Credentials CG |
| 2019 | W3C DID WG chartered | |
| 2022 Jul | **DID Core 1.0** | **W3C Recommendation**. DID syntax (`did:method:identifier`), DID Documents (JSON-LD), DID resolution. 100+ DID methods registered. |
| 2022 | did:web | Simple DID method using HTTPS. Lower barrier to entry than blockchain-based methods. |
| 2023 | did:tdw (Trust DID Web) | Enhanced did:web with cryptographic trust chain and versioning. |

**DID method landscape** (selected):
- `did:web` -- HTTPS-based, no blockchain. Growing adoption.
- `did:key` -- Self-contained in the identifier itself. Ephemeral use.
- `did:ion` -- Microsoft's Bitcoin-anchored DID method (ION network)
- `did:ethr` -- Ethereum-based
- `did:sov` -- Hyperledger Indy/Sovrin
- `did:ebsi` -- EU blockchain (EBSI)
- 150+ methods registered, most with minimal adoption

#### Real Deployments vs Hype

**Real deployments** (as of 2024-2025):
- **EU Digital Identity Wallet (eIDAS 2.0)**: Regulation passed June 2024.
  Member states must offer digital identity wallets by 2026. Based on
  OpenID4VP + SD-JWT VC (not blockchain DIDs). The largest real-world VC
  initiative globally.
- **mDL (Mobile Driver's License)**: ISO/IEC 18013-5 (2021). Deployed in
  several US states (Utah, Louisiana, Colorado, Arizona, etc.). Apple Wallet
  and Google Wallet support. Uses CBOR/COSE, proximity protocols.
- **British Columbia**: OrgBook (Hyperledger Aries/Indy). Business
  credential verification. One of few production DID/VC systems.
- **IATA Digital Travel Credential**: Airline industry VC-based travel
  documents. Pilot phase.
- **Korea**: National digital ID using VCs. Government-backed deployment.
- **India**: DigiLocker. While not strictly W3C VC, uses verifiable document
  model at national scale.

**Hype vs reality assessment**:
- Blockchain-anchored DIDs have seen minimal mainstream adoption
- The EU approach (eIDAS 2.0) deliberately avoids blockchain requirements
- `did:web` is gaining traction as a pragmatic alternative
- SD-JWT VC (not JSON-LD VC) is emerging as the preferred format for
  government-scale deployments
- Self-sovereign identity (SSI) vision of "user controls everything" is being
  tempered by regulatory requirements for trust frameworks and governance
- Most production VC deployments use centralized or federated trust, not fully
  decentralized models

**Current status**: Verifiable Credentials are transitioning from pilot to
production, primarily driven by government regulation (eIDAS 2.0, mDL). DIDs
remain controversial -- practical deployments favor simpler trust models.
The SSI movement's blockchain maximalism has given way to pragmatic approaches.

---

### Zero Trust Architecture

| Year | Event | Reference |
|------|-------|-----------|
| 2004 | Jericho Forum founded | De-perimeterization concept. "The wall is crumbling." |
| 2010 | John Kindervag (Forrester) coins "Zero Trust" | Core principle: "never trust, always verify." Assumes breach. |
| 2014 | Google publishes BeyondCorp | BeyondCorp paper. Internal implementation of zero trust: no VPN, device-aware access, identity-centric. |
| 2017 | Gartner CARTA | Continuous Adaptive Risk and Trust Assessment. Zero trust variant. |
| 2019 | Google BeyondCorp published in book form | "BeyondCorp: A New Approach to Enterprise Security" |
| 2020 Aug | **NIST SP 800-207** | **Zero Trust Architecture**. Definitive federal framework. Core tenets: verify explicitly, least privilege, assume breach. Three ZTA approaches: identity governance, micro-segmentation, software-defined perimeter. |
| 2020 | NIST SP 800-207A (draft) | ZTA model for access control in cloud-native applications |
| 2021 May | **Executive Order 14028** | US presidential EO: "Improving the Nation's Cybersecurity." Mandated zero trust for federal agencies. |
| 2022 Jan | **OMB M-22-09** | Federal Zero Trust Strategy. Deadlines for agency adoption by end of FY2024. Five pillars: Identity, Devices, Networks, Applications, Data. |
| 2022 | CISA Zero Trust Maturity Model | Version 1.0. Guidance for federal agencies. Traditional -> Advanced -> Optimal maturity levels. |
| 2023 Apr | CISA ZTMM v2.0 | Updated maturity model. Added visibility/analytics pillar, governance/automation cross-cutting capabilities. |
| 2023 | DoD Zero Trust Strategy | Department of Defense published reference architecture and roadmap. Target: full ZT implementation by FY2027. |
| 2024 | NIST SP 1800-35 | Implementing a Zero Trust Architecture (practice guide). Multi-vendor reference implementations. |

**Zero Trust and identity standards intersection**:
- **Identity as the new perimeter**: ZTA elevates IdP to the most critical
  infrastructure component. Strong authentication (FIDO2/passkeys), continuous
  authorization, and real-time risk signals are essential.
- **Standards enabling ZTA**:
  - OAuth 2.0 / OIDC: Token-based access control
  - SCIM: Automated provisioning/deprovisioning
  - FIDO2/WebAuthn: Phishing-resistant authentication
  - CAEP/SSF (Shared Signals): Continuous evaluation (session revocation on
    risk change)
  - mTLS: Service-to-service identity in service mesh (Istio, Linkerd)
  - SPIFFE/SPIRE: Workload identity for microservices

**Current status**: Zero trust is the dominant enterprise security paradigm.
Federal mandates are driving adoption across government and defense. Private
sector adoption is accelerating, driven by insurance requirements and
regulatory pressure. The concept has evolved from network-centric (micro-
segmentation) to identity-centric (continuous verification).

---

### Chronological Master Timeline Table

| Year | Standard / Version | Organization | Status | Successor / Notes |
|------|-------------------|--------------|--------|-------------------|
| 1983 | Kerberos development begins (Project Athena) | MIT | Historical | Led to Kerberos V5 |
| 1986 | RSA SecurID hardware tokens | RSA Security | Active (evolved) | OATH HOTP/TOTP |
| 1988 | X.500 / DAP | ITU-T | Deprecated | LDAP |
| 1988 | X.509 v1 certificates | ITU-T | Superseded | X.509 v3 |
| 1989 | Kerberos V4 | MIT | Deprecated | Kerberos V5 |
| 1991 | RADIUS created | Livingston Enterprises | Historical | RFC 2865 (2000) |
| 1993 | LDAPv1 (RFC 1487) | IETF | Deprecated | LDAPv2 |
| 1993 | Kerberos V5 (RFC 1510) | IETF | Superseded | RFC 4120 (2005) |
| 1993 | X.509 v2 | ITU-T | Superseded | X.509 v3 |
| 1995 | LDAPv2 (RFC 1777) | IETF | Deprecated | LDAPv3 |
| 1996 | X.509 v3 | ITU-T | Active | RFC 5280 profile |
| 1997 | LDAPv3 (RFC 2251) | IETF | Superseded | RFC 4510 (2006) |
| 1997 | RADIUS (RFC 2058) | IETF | Superseded | RFC 2865 (2000) |
| 1999 | PKIX (RFC 2459) | IETF | Superseded | RFC 5280 (2008) |
| 2000 | RADIUS (RFC 2865/2866) | IETF | Active | RadSec (RFC 6614) |
| 2001 | Liberty Alliance founded | Sun/AOL/HP/Nokia | Dissolved (2009) | Merged into SAML 2.0, Kantara |
| 2002 | WS-Security 1.0 | IBM/Microsoft | Deprecated | OASIS Standard 2004 |
| 2002 | SAML 1.0 | OASIS | Deprecated | SAML 1.1 |
| 2003 | SAML 1.1 | OASIS | Deprecated | SAML 2.0 |
| 2003 | WS-Trust 1.0 | IBM/Microsoft | Superseded | WS-Trust 1.3 (2006) |
| 2003 | WS-Federation 1.0 | IBM/Microsoft/BEA | Superseded | WS-Fed 1.2 (2009) |
| 2003 | XACML 1.0 | OASIS | Deprecated | XACML 2.0 |
| 2003 | SPML 1.0 | OASIS | Deprecated | SCIM |
| 2004 | Liberty ID-FF 1.2 | Liberty Alliance | Deprecated | Merged into SAML 2.0 |
| 2005 | SAML 2.0 | OASIS | **Active** | Still dominant in enterprise federation |
| 2005 | Kerberos V5 (RFC 4120) | IETF | **Active** | Current spec |
| 2005 | XACML 2.0 | OASIS | Superseded | XACML 3.0 |
| 2005 | HOTP (RFC 4226) | IETF | **Active** | Supplemented by TOTP |
| 2005 | OpenID 1.0 | Community | Deprecated | OpenID 2.0 |
| 2005 | PKINIT (RFC 4556) | IETF | **Active** | Kerberos + smartcard/cert auth |
| 2006 | LDAPv3 revised (RFC 4510-4519) | IETF | **Active** | Current LDAPv3 spec |
| 2006 | WS-Trust 1.3 | OASIS | Deprecated | OAuth 2.0 Token Exchange |
| 2006 | SPML 2.0 | OASIS | Deprecated | SCIM |
| 2006 | SPNEGO (RFC 4178) | IETF | **Active** | HTTP Negotiate / Integrated Windows Auth |
| 2007 | OAuth 1.0 | Community | Deprecated | OAuth 1.0a, OAuth 2.0 |
| 2007 | OpenID 2.0 | OpenID Foundation | Deprecated | OpenID Connect |
| 2008 | PKIX (RFC 5280) | IETF | **Active** | Definitive X.509 Internet profile |
| 2009 | WS-Federation 1.2 | OASIS | Deprecated | OIDC / OAuth 2.0 |
| 2010 | OAuth 1.0a (RFC 5849) | IETF | Deprecated | OAuth 2.0 |
| 2011 | TOTP (RFC 6238) | IETF | **Active** | Supplemented by FIDO2/Passkeys |
| 2011 | SCIM 1.0 | IETF (draft) | Superseded | SCIM 2.0 |
| 2012 | OAuth 2.0 (RFC 6749/6750) | IETF | **Active** | OAuth 2.1 (draft) |
| 2012 | RadSec (RFC 6614) | IETF | **Active** | RADIUS over TLS |
| 2013 | XACML 3.0 | OASIS | **Active** | Limited new adoption; OPA/Cedar alternatives |
| 2013 | Certificate Transparency (RFC 6962) | IETF | **Active** | CT v2 (RFC 9162) |
| 2013 | Token Revocation (RFC 7009) | IETF | **Active** | Part of OAuth ecosystem |
| 2014 | OpenID Connect Core 1.0 | OpenID Foundation | **Active** | Growing, supplementing SAML |
| 2014 | FIDO U2F 1.0 | FIDO Alliance | Superseded | FIDO2/WebAuthn |
| 2014 | FIDO UAF 1.0 | FIDO Alliance | **Active** | Mobile passwordless (limited adoption) |
| 2015 | Token Introspection (RFC 7662) | IETF | **Active** | Part of OAuth ecosystem |
| 2015 | PKCE (RFC 7636) | IETF | **Active** | Mandatory in OAuth 2.1 |
| 2015 | UMA 1.0 | Kantara Initiative | Superseded | UMA 2.0 |
| 2015 | Let's Encrypt launches | ISRG | **Active** | Billions of certs issued |
| 2015 | SCIM 2.0 (RFC 7642-7644) | IETF | **Active** | SCIM 2.1 in development |
| 2017 | OAuth 2.0 for Native Apps (RFC 8252) | IETF | **Active** | Best practices |
| 2017 | Kerberos DES/RC4 deprecated (RFC 8429) | IETF | **Active** | Use AES |
| 2018 | FIDO2 / CTAP 2.0 | FIDO Alliance | **Active** | Foundation for passkeys |
| 2018 | UMA 2.0 | Kantara Initiative | **Active** | Niche adoption |
| 2018 | OPA 1.0 (Rego) | CNCF (Styra) | **Active** | Cloud-native policy engine |
| 2019 | WebAuthn Level 1 | W3C | Superseded | WebAuthn Level 2 |
| 2019 | ACME (RFC 8555) | IETF | **Active** | Automated certificate management |
| 2019 | Verifiable Credentials 1.0 | W3C | Superseded | VC Data Model 2.0 |
| 2019 | Device Authorization Grant (RFC 8628) | IETF | **Active** | Smart TV/CLI auth |
| 2019 | OIDC CIBA | OpenID Foundation | **Active** | Decoupled authentication |
| 2020 | NIST SP 800-207 (Zero Trust Architecture) | NIST | **Active** | Federal ZTA framework |
| 2020 | Token Exchange (RFC 8693) | IETF | **Active** | OAuth STS |
| 2021 | WebAuthn Level 2 | W3C | **Active** | Current W3C Recommendation |
| 2021 | PAR (RFC 9126) | IETF | **Active** | Pushed auth requests |
| 2021 | Executive Order 14028 | US Government | **Active** | Federal cybersecurity mandates |
| 2021 | ISO/IEC 18013-5 (mDL) | ISO | **Active** | Mobile driver's license |
| 2022 | DID Core 1.0 | W3C | **Active** | Controversial; pragmatic adoption varies |
| 2022 | OMB M-22-09 (Federal ZT Strategy) | OMB | **Active** | Agency deadlines FY2024 |
| 2022 | Passkeys announced | Apple/Google/Microsoft | **Active** | Synced WebAuthn credentials |
| 2022 | OpenFGA | Okta/CNCF | **Active** | Zanzibar-based ReBAC |
| 2022 | VC Data Model 1.1 | W3C | Superseded | VC Data Model 2.0 |
| 2023 | DPoP (RFC 9449) | IETF | **Active** | Sender-constrained tokens |
| 2023 | RAR (RFC 9396) | IETF | **Active** | Fine-grained authorization |
| 2023 | Cedar policy language | AWS (open source) | **Active** | Formally verified authZ |
| 2023 | CISA ZTMM v2.0 | CISA | **Active** | Federal ZT maturity model |
| 2023 | VC Data Model 2.0 | W3C | **Draft** | Candidate Recommendation |
| 2023 | OAuth 2.1 | IETF | **Draft** | Consolidation of OAuth 2.0 + BCP |
| 2023 | OIDC Shared Signals (SSF) | OpenID Foundation | **Active** | CAEP + RISC |
| 2024 | WebAuthn Level 3 | W3C | **Draft** | Working Draft |
| 2024 | eIDAS 2.0 regulation adopted | EU | **Active** | EU digital identity wallets by 2026 |
| 2024 | OIDC Federation 1.0 | OpenID Foundation | **Draft** | Automatic trust chains |
| 2024 | SD-JWT VC | IETF | **Draft** | Selective disclosure VCs |
| 2024 | NIST SP 1800-35 (ZTA practice guide) | NIST | **Active** | Multi-vendor reference implementation |
| 2025 | GNAP | IETF | **Draft** | Next-gen authorization protocol |
| 2025 | FIDO CXP/CXF | FIDO Alliance | **Draft** | Passkey portability between providers |

---

## Appendix A: Key Organizations

| Organization | Founded | Focus | URL |
|-------------|---------|-------|-----|
| IETF | 1986 | Internet standards (RFCs) | ietf.org |
| OASIS | 1993 | Enterprise standards (SAML, XACML, WS-*) | oasis-open.org |
| W3C | 1994 | Web standards (WebAuthn, VCs, DIDs) | w3.org |
| OpenID Foundation | 2007 | OpenID Connect, MODRNA, FAPI | openid.net |
| FIDO Alliance | 2012 | FIDO2, WebAuthn, passkeys | fidoalliance.org |
| Kantara Initiative | 2009 | UMA, identity assurance, consent | kantarainitiative.org |
| CNCF | 2015 | Cloud-native (OPA, SPIFFE, OpenFGA) | cncf.io |
| CA/Browser Forum | 2005 | TLS certificate trust requirements | cabforum.org |
| NIST | 1901 | US federal standards (SP 800-series) | nist.gov |
| ISO/IEC JTC 1 | 1987 | International standards (mDL, X.509) | iso.org |

## Appendix B: RFC Quick Reference

### Authentication & Directory
| RFC | Year | Title |
|-----|------|-------|
| 1487 | 1993 | X.500 Lightweight Directory Access Protocol (LDAPv1) |
| 1510 | 1993 | The Kerberos Network Authentication Service (V5) |
| 1777 | 1995 | Lightweight Directory Access Protocol (LDAPv2) |
| 2251 | 1997 | Lightweight Directory Access Protocol (v3) |
| 2865 | 2000 | Remote Authentication Dial In User Service (RADIUS) |
| 2866 | 2000 | RADIUS Accounting |
| 3961 | 2005 | Encryption and Checksum Specifications for Kerberos 5 |
| 4120 | 2005 | The Kerberos Network Authentication Service (V5) [current] |
| 4178 | 2006 | The Simple and Protected GSS-API Negotiation Mechanism (SPNEGO) |
| 4226 | 2005 | HOTP: An HMAC-Based One-Time Password Algorithm |
| 4510 | 2006 | LDAP: Technical Specification Road Map [current] |
| 4511 | 2006 | LDAP: The Protocol [current] |
| 4556 | 2005 | Public Key Cryptography for Initial Authentication in Kerberos (PKINIT) |
| 5280 | 2008 | Internet X.509 PKI Certificate and CRL Profile [current] |
| 6238 | 2011 | TOTP: Time-Based One-Time Password Algorithm |
| 6614 | 2012 | Transport Layer Security (TLS) Encryption for RADIUS |
| 8429 | 2018 | Deprecate Triple-DES and RC4 in Kerberos |
| 8555 | 2019 | Automatic Certificate Management Environment (ACME) |

### OAuth & OpenID Connect
| RFC | Year | Title |
|-----|------|-------|
| 5849 | 2010 | The OAuth 1.0 Protocol |
| 6749 | 2012 | The OAuth 2.0 Authorization Framework |
| 6750 | 2012 | The OAuth 2.0 Authorization Framework: Bearer Token Usage |
| 6819 | 2013 | OAuth 2.0 Threat Model and Security Considerations |
| 7009 | 2013 | OAuth 2.0 Token Revocation |
| 7519 | 2015 | JSON Web Token (JWT) |
| 7636 | 2015 | Proof Key for Code Exchange (PKCE) |
| 7662 | 2015 | OAuth 2.0 Token Introspection |
| 8252 | 2017 | OAuth 2.0 for Native Apps |
| 8414 | 2018 | OAuth 2.0 Authorization Server Metadata |
| 8628 | 2019 | OAuth 2.0 Device Authorization Grant |
| 8693 | 2020 | OAuth 2.0 Token Exchange |
| 8707 | 2020 | Resource Indicators for OAuth 2.0 |
| 9068 | 2021 | JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens |
| 9101 | 2021 | The OAuth 2.0 Authorization Framework: JWT-Secured Authorization Request (JAR) |
| 9126 | 2021 | OAuth 2.0 Pushed Authorization Requests (PAR) |
| 9207 | 2022 | OAuth 2.0 Authorization Server Issuer Identification |
| 9396 | 2023 | OAuth 2.0 Rich Authorization Requests (RAR) |
| 9449 | 2023 | OAuth 2.0 Demonstrating Proof of Possession (DPoP) |

### Provisioning
| RFC | Year | Title |
|-----|------|-------|
| 7642 | 2015 | SCIM: Definitions, Overview, Concepts, and Requirements |
| 7643 | 2015 | SCIM: Core Schema |
| 7644 | 2015 | SCIM: Protocol |

### Security Events
| RFC | Year | Title |
|-----|------|-------|
| 8935 | 2020 | Push-Based Security Event Token (SET) Delivery |
| 8936 | 2020 | Poll-Based Security Event Token (SET) Delivery |
| 9162 | 2021 | Certificate Transparency Version 2.0 |

## Appendix C: Standards Implementation in OpenAM / Open Identity Platform

The Open Identity Platform suite (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF)
implements many of the standards documented in this timeline:

| Standard | OIP Component | Implementation |
|----------|--------------|----------------|
| LDAPv3 | OpenDJ | Full LDAPv3 server (RFC 4510-4519), syncrepl, virtual attributes |
| RADIUS | OpenAM | RADIUS authentication module, RADIUS server integration |
| Kerberos V5 | OpenAM | Kerberos/SPNEGO authentication module (Windows Desktop SSO) |
| X.509 | OpenAM | Certificate-based authentication module, CRL/OCSP validation |
| SAML 2.0 | OpenAM | Full IdP and SP, all profiles, metadata management |
| OAuth 2.0 | OpenAM | Authorization server (all grant types), resource server |
| OpenID Connect | OpenAM | OIDC Provider, Discovery, Dynamic Registration |
| XACML 3.0 | OpenAM | Policy engine via entitlements service |
| SCIM | OpenIDM | SCIM 2.0 provisioning endpoints |
| FIDO/WebAuthn | OpenAM | WebAuthn authentication module (FIDO2) |
| UMA 2.0 | OpenAM | Authorization server with UMA grant type |
| HOTP/TOTP | OpenAM | OATH authentication modules |
| WS-Federation | OpenAM | WS-Federation IdP/SP (legacy support) |
| ACME | -- | Not implemented (certificate management external) |
