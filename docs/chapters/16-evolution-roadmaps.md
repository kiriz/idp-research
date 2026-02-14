# Chapter 16: Identity Security Evolution Roadmaps — How Every Domain Got Here

## Introduction: Why "Identity Security" and Not Just "IAM"

The term "Identity and Access Management" was adequate for the 2005--2016 era, when the problem space was bounded: authenticate a human user via LDAP bind or SAML assertion, authorize access via RBAC or XACML policy, provision accounts via SPML or proprietary connectors. The Open Identity Platform stack -- OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF -- was built for that era, and it excelled within those boundaries.

That era is over. The problem space has expanded in every dimension simultaneously. Authentication now spans human users, machine workloads, IoT devices, and AI agents. Authorization extends from on-premises LDAP-backed policies to multi-cloud entitlements across AWS, Azure, and GCP. Threat detection has moved from post-hoc SIEM log correlation to real-time identity-layer behavioral analytics. Privacy regulations have transformed identity systems from authentication gateways into consent engines. Decentralized identity challenges the foundational assumption that a centralized IdP is the root of all trust. And the sheer ratio of non-human identities to human identities -- 50:1 or higher in large organizations -- has made "access management" a misleadingly narrow label for a domain that now encompasses secrets management, certificate lifecycle, workload attestation, and cloud infrastructure entitlements.

"Identity Security" is the umbrella term that captures this expansion. It encompasses:

- **IAM** (Identity & Access Management) -- the traditional core: authentication, SSO, federation, authorization
- **IGA** (Identity Governance & Administration) -- lifecycle management, access certification, SoD enforcement
- **PAM** (Privileged Access Management) -- vault-based credential management, session brokering, JIT access
- **ITDR** (Identity Threat Detection & Response) -- real-time detection of credential theft, lateral movement, privilege escalation
- **CIEM** (Cloud Infrastructure Entitlement Management) -- multi-cloud permission analysis, least-privilege enforcement
- **Decentralized Identity** -- W3C Verifiable Credentials, DIDs, self-sovereign identity wallets
- **Machine/Workload Identity** -- SPIFFE/SPIRE, short-lived certificates, non-human identity management
- **Privacy & Consent** -- GDPR/CCPA compliance, consent-as-code, data subject rights
- **Zero Trust** -- continuous verification, device trust, microsegmentation anchored to identity

This chapter traces 18 identity security domains from earliest origins through current state to projected future. Each roadmap is self-contained. The chapter concludes with the Grand Shift Table summarizing all 18 domains.

### How to Read This Chapter

Each roadmap is self-contained and can be read independently. Within each roadmap, entries proceed chronologically from earliest to latest. Every technology, protocol, and product mentioned carries one of four status tags:

| Tag | Meaning | Adoption Indicator |
|-----|---------|-------------------|
| `[ACTIVE]` | Widely deployed in production today | >25% of relevant market |
| `[LEGACY]` | Still exists in production but declining | Deployed but losing share to successors |
| `[EMERGING]` | Early adoption, <5% market penetration | Pilots, drafts, or first production deployments |
| `[OBSOLETE]` | Effectively dead; no new deployments | Mentioned for historical completeness only |

OpenAM/OIP implementation notes appear inline for every technology where OpenAM provides relevant functionality. Cross-references to earlier chapters are provided where deeper analysis exists.

---

## Roadmap 1: Authentication Methods

**Arc:** Shared secrets (1960s) --> directory-verified passwords (1993) --> network authentication protocols (1988-2000) --> one-time passwords (2005-2011) --> push notifications (2012) --> public-key passwordless (2014-present) --> continuous authentication (emerging).

### 1.1 Passwords and Shared Secrets (1960s-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1961 | MIT CTSS implements first computer password system | Fernando Corbato, MIT | `[ACTIVE]` (concept) |
| 1976 | Unix crypt(3) introduces salted password hashing (DES-based) | Unix V7 | `[OBSOLETE]` (DES hash) |
| 1988 | Kerberos V4 replaces plaintext network passwords at MIT | Project Athena | `[OBSOLETE]` |
| 1993 | LDAP Simple Bind (RFC 1487, LDAPv1) -- password sent to directory for verification | IETF | `[ACTIVE]` |
| 1995 | LDAPv2 (RFC 1777) refines simple bind | IETF | `[OBSOLETE]` |
| 2000 | LDAPv3 adds StartTLS for encrypted password transmission | RFC 2830 | `[ACTIVE]` |
| 2000 | PKCS#5 PBKDF2 standardizes password-based key derivation | RFC 2898 | `[ACTIVE]` |
| 1999 | bcrypt published (Provos & Mazieres, OpenBSD) | USENIX 1999 | `[ACTIVE]` |
| 2009 | scrypt (Colin Percival) -- memory-hard password hashing | Percival, BSDCan 2009 | `[ACTIVE]` |
| 2013 | Password Hashing Competition launched | PHC | -- |
| 2015 | Argon2 wins PHC, becomes recommended hash | RFC 9106 (2021) | `[ACTIVE]` |
| 2017 | NIST SP 800-63B overhauls password guidance: no composition rules, no periodic rotation, check breached lists | NIST | `[ACTIVE]` guidance |

**What problem passwords solved:** Identity verification in multi-user systems. Before passwords, physical access was the access control.

**Why passwords persist:** Universal comprehension, zero hardware requirements, every protocol supports them. Estimated 80%+ of authentication events still involve a password as at least one factor.

**OpenAM implementation:** LDAP Bind module (`openam-auth-ldap`), Active Directory module (`openam-auth-ad`), DataStore module (`openam-auth-datastore`). Password hashing via SSHA-512, PBKDF2. Password policy enforcement at OpenDJ directory layer (complexity, history, lockout). See Ch.02 for detailed module analysis.

### 1.2 Kerberos (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1983 | Project Athena begins at MIT | MIT internal | Historical |
| 1988 | Kerberos V4 released publicly | MIT | `[OBSOLETE]` |
| 1993 | Kerberos V5 | RFC 1510 | Superseded |
| 2000 | Windows 2000 adopts Kerberos V5 as default AD authentication | Microsoft | `[ACTIVE]` |
| 2005 | Kerberos V5 revised specification | RFC 4120 | `[ACTIVE]` |
| 2005 | AES encryption replaces DES for Kerberos | RFC 3962 | `[ACTIVE]` |
| 2005 | PKINIT -- public key initial authentication | RFC 4556 | `[ACTIVE]` |
| 2006 | SPNEGO/Negotiate for HTTP | RFC 4559 | `[ACTIVE]` |
| 2018 | DES and RC4 formally deprecated | RFC 8429 | `[ACTIVE]` (deprecation) |

**What Kerberos solved:** Secure network authentication without transmitting passwords. Ticket-based system: user authenticates once to KDC (Key Distribution Center), receives TGT (Ticket Granting Ticket), then obtains service tickets for individual services without re-entering credentials. Mutual authentication -- both client and server prove identity.

**Architecture:** KDC (AS + TGS) issues tickets. AS-REQ/AS-REP for initial TGT. TGS-REQ/TGS-REP for service tickets. AP-REQ/AP-REP for application authentication. Cross-realm referrals for federated trust.

**OpenAM implementation:** Windows Desktop SSO module (`openam-auth-windowsdesktopsso`) -- SPNEGO/Negotiate handler accepting Kerberos tickets from browsers. Integrates with Active Directory KDC. Configuration: keytab file, SPN (Service Principal Name), KDC hostname. OpenAM validates Kerberos ticket, extracts principal name, maps to OpenAM user identity.

**Current relevance:** Foundational to every Active Directory domain. Every Windows login uses Kerberos. Also used in Hadoop/HDFS ecosystems. However, Kerberos is complex outside Windows AD, requires synchronized clocks, and is poorly suited to cloud-native architectures (no HTTP-native flow, no mobile support). `[ACTIVE]` in enterprise on-premises, `[LEGACY]` for new cloud-native projects.

### 1.3 X.509 Client Certificates (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1988 | X.509 v1 -- basic certificate structure | ITU-T X.509 | `[OBSOLETE]` |
| 1993 | X.509 v2 -- issuer/subject unique IDs | ITU-T | `[OBSOLETE]` |
| 1996 | X.509 v3 -- extensions framework (SANs, key usage, CRL distribution) | ITU-T | `[ACTIVE]` |
| 1999 | PKIX Internet profile for X.509 | RFC 2459 | Superseded |
| 2002 | PKIX updated | RFC 3280 | Superseded |
| 2008 | Definitive PKIX profile | RFC 5280 | `[ACTIVE]` |
| 2013 | Certificate Transparency | RFC 6962 | `[ACTIVE]` |
| 2015 | Let's Encrypt launches -- free automated DV certificates | ISRG | `[ACTIVE]` |
| 2019 | ACME protocol standardized | RFC 8555 | `[ACTIVE]` |
| 2021 | Certificate Transparency v2 | RFC 9162 | `[ACTIVE]` |

**What certificates solved:** Phishing-resistant mutual authentication. Client proves identity via private key possession; no shared secret transmitted. Device binding -- hardware-backed keys (TPM, Secure Enclave) prevent credential extraction.

**OpenAM implementation:** Certificate authentication module (`openam-auth-cert`). Extracts X.509 certificate from `javax.servlet.request.X509Certificate` attribute. Validates: CA chain, validity period, CRL/OCSP revocation. Maps certificate DN or SAN to user account. See Ch.02 for detailed flow.

**mTLS resurgence:** Mutual TLS is standard practice in service mesh architectures (Istio, Linkerd). SPIFFE/SPIRE (2017) uses X.509 SVIDs (SPIFFE Verifiable Identity Documents) for workload identity. OAuth 2.0 mTLS (RFC 8705) binds access tokens to client certificates. `[ACTIVE]` and growing.

### 1.4 RADIUS and TACACS+ (1991-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1991 | Livingston Enterprises creates RADIUS for Merit Network dial-up | Internal | Historical |
| 1993 | Cisco develops TACACS+ (proprietary, based on original TACACS from 1984) | Cisco | `[ACTIVE]` (network) |
| 1997 | RADIUS standardized | RFC 2058/2059 | Superseded |
| 2000 | RADIUS definitive RFCs | RFC 2865 (auth), RFC 2866 (accounting) | `[ACTIVE]` |
| 2003 | RADIUS over EAP for 802.1X/Wi-Fi | RFC 3579 | `[ACTIVE]` |
| 2003 | Diameter protocol (RADIUS successor for telecom) | RFC 3588 (obsoleted by RFC 6733, 2012) | `[ACTIVE]` (telecom) |
| 2008 | Dynamic Authorization (CoA/Disconnect) | RFC 5176 | `[ACTIVE]` |
| 2012 | RadSec -- RADIUS over TLS | RFC 6614 | `[ACTIVE]` |

**What RADIUS solved:** Centralized authentication for network infrastructure devices (switches, APs, VPN gateways) that lack integrated directory clients. AAA: Authentication, Authorization, Accounting in one protocol.

**Fundamental weaknesses:** UDP transport, MD5-based authenticator (cryptographically weak), shared secrets between NAS and RADIUS server, no native encryption of full payload.

**OpenAM implementation:** RADIUS authentication module (`openam-auth-radius`). OpenAM acts as RADIUS client, forwarding credentials to external RADIUS server. Configuration: primary/secondary server, shared secret, timeout. Used to integrate hardware token vendors (RSA SecurID) and network access control.

**TACACS+:** Cisco-proprietary (draft-ietf-opsawg-tacacs-18 informational). Separates authentication, authorization, accounting into distinct operations. Encrypts full packet body (vs RADIUS encrypting only password). `[ACTIVE]` for Cisco network device management. No OpenAM module -- typically used between network devices and Cisco ISE/ACS.

**Diameter (RFC 3588/6733):** Intended RADIUS successor for telecom (3GPP). TCP/SCTP transport, larger AVP space, better security. Dominant in mobile network AAA (LTE/5G). Not used for enterprise Wi-Fi/VPN. `[ACTIVE]` in telecom, not relevant to OpenAM.

### 1.5 HTTP Authentication Schemes (1996-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1996 | HTTP Basic Authentication | RFC 1945 (HTTP/1.0), RFC 2617 | `[LEGACY]` |
| 1997 | HTTP Digest Authentication | RFC 2069, RFC 2617 | `[OBSOLETE]` |
| 1999 | Form-based authentication (de facto, no RFC) | Industry practice | `[ACTIVE]` |
| 2006 | SPNEGO/Negotiate (Kerberos over HTTP) | RFC 4178, RFC 4559 | `[ACTIVE]` |
| 2012 | OAuth 2.0 Bearer Token in Authorization header | RFC 6750 | `[ACTIVE]` |
| 2014 | HTTP Authentication updated | RFC 7235 | `[ACTIVE]` |
| 2023 | DPoP token type | RFC 9449 | `[EMERGING]` |

**HTTP Basic:** Base64-encoded `username:password` in `Authorization` header. No encryption (relies entirely on TLS). Still used for API authentication (simple, universal), machine-to-machine calls, and development/testing. `[LEGACY]` for user-facing applications, `[ACTIVE]` for simple API auth.

**HTTP Digest:** Challenge-response avoiding plaintext password transmission. MD5-based (broken), complex implementation, poor proxy compatibility. Effectively dead. `[OBSOLETE]`

**Form-based:** HTML form POST with username/password. Server sets session cookie on success. No formal specification. Dominant for web applications from 2000-present. Being displaced by OIDC redirect flows and passkeys for new applications but remains ubiquitous.

**OpenAM implementation:** OpenAM's login page is form-based authentication. The `AuthContext` API accepts callbacks (NameCallback, PasswordCallback) and returns session tokens. OpenAM supports HTTP Basic via the `zero-page login` feature (REST authentication endpoint accepts Basic credentials).

### 1.6 One-Time Passwords (2005-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1986 | RSA SecurID hardware token (proprietary algorithm) | RSA Security | `[LEGACY]` |
| 1998 | S/KEY one-time password system | RFC 2289 | `[OBSOLETE]` |
| 2004 | OATH consortium founded (Initiative for Open Authentication) | OATH | -- |
| 2005 | HOTP -- HMAC-Based One-Time Password | RFC 4226 | `[LEGACY]` |
| 2005-2010 | SMS OTP widespread deployment | Industry practice | `[LEGACY]` |
| 2010 | Google Authenticator launched (popularized TOTP) | Google | `[ACTIVE]` |
| 2011 | TOTP -- Time-Based One-Time Password | RFC 6238 | `[ACTIVE]` |
| 2017 | NIST SP 800-63B deprecates SMS OTP as "restricted" authenticator | NIST | `[ACTIVE]` (guidance) |

**HOTP (RFC 4226):** Counter-based. HMAC-SHA1(secret, counter) truncated to 6-8 digits. Problem: counter desynchronization between client and server. Requires look-ahead window. `[LEGACY]` -- superseded by TOTP for software tokens; still in some hardware tokens.

**TOTP (RFC 6238):** Time-based. HMAC-SHA1(secret, floor(time/30)). Eliminates counter desync. 30-second window with +/-1 tolerance. `[ACTIVE]` -- dominant software-based second factor. Every major service supports it. Vulnerable to real-time phishing (adversary-in-the-middle proxies code).

**SMS OTP:** Password sent via SMS text message. Convenient but insecure: SIM-swap attacks, SS7 interception, social engineering against mobile carriers. NIST deprecated as "restricted" authenticator in 2016. Still widely deployed due to universality of SMS. `[LEGACY]`

**OpenAM implementation:**
- HOTP module: `openam-auth-hotp` -- RFC 4226 implementation with SMS delivery gateway.
- TOTP/OATH module: `openam-auth-oath` -- RFC 6238 implementation. Configurable time step (30s default), code length (6/8 digits), HMAC algorithm (SHA-1/SHA-256/SHA-512). Shared secret stored in user LDAP profile. QR code enrollment via `otpauth://` URI.
- RSA SecurID module: `openam-auth-securid` -- proprietary protocol integration with RSA Authentication Manager.

See Ch.02 for detailed OTP module analysis.

### 1.7 Push Notifications (2012-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2010 | Duo Security founded (pioneer of push MFA) | Duo | `[ACTIVE]` |
| 2012 | Push authentication as MFA factor gains traction | Industry | `[ACTIVE]` |
| 2014 | Microsoft Authenticator adds push approval | Microsoft | `[ACTIVE]` |
| 2018 | Okta Verify push authentication | Okta | `[ACTIVE]` |
| 2022 | Number matching mandated (anti-fatigue) | Microsoft, others | `[ACTIVE]` |
| 2023 | Push fatigue attacks documented (Uber breach 2022, etc.) | Industry reports | -- |

**What push solved:** Better UX than TOTP (tap "Approve" vs type 6-digit code). Context display (IP, location, application) enables informed approval decisions. Can serve as passwordless primary factor, not just second factor.

**Push fatigue attacks:** Attacker repeatedly triggers push notifications until user accidentally or frustratedly approves. Mitigations: number matching (user must enter 2-digit code displayed on login screen), geographic context, rate limiting.

**OpenAM implementation:** Push authentication module (`openam-auth-push`). Supports APNs (iOS), FCM (Android), WebSocket fallback. Device enrollment via QR code. Multi-device management. Signed approval responses prevent replay. See Ch.02.

### 1.8 FIDO U2F (2014-2019)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2012 | FIDO Alliance founded | PayPal, Lenovo, Nok Nok Labs, others | -- |
| 2014 | FIDO U2F 1.0 -- Universal 2nd Factor | FIDO Alliance | Superseded |
| 2015 | Google deploys U2F for all employees -- phishing drops to zero | USENIX Security 2016 | -- |
| 2016 | FIDO U2F 1.2 -- NFC and BLE transports | FIDO Alliance | Superseded |
| 2018 | CTAP 1 (U2F renamed for FIDO2 compatibility) | FIDO Alliance | `[LEGACY]` |

**What U2F solved:** Phishing-resistant second factor. Per-origin key pairs: credential created for `example.com` cannot be used on `examp1e.com`. USB HID protocol, simple challenge-response. Google's 2015 deployment proved the concept at scale.

**Why superseded:** WebAuthn/FIDO2 subsumed U2F functionality with richer API, resident key support (passwordless), and platform authenticator support (biometrics). U2F hardware keys remain compatible via CTAP 1.

### 1.9 WebAuthn / FIDO2 (2018-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2018 | FIDO2 project announced (W3C + FIDO Alliance) | Joint | -- |
| 2018 | CTAP 2.0 -- resident credentials, PIN/biometric | FIDO Alliance | `[ACTIVE]` |
| 2019 | WebAuthn Level 1 -- W3C Recommendation | W3C | Superseded |
| 2021 | WebAuthn Level 2 -- enterprise attestation, large blobs | W3C | `[ACTIVE]` |
| 2021 | CTAP 2.1 -- credential management, min PIN length | FIDO Alliance | `[ACTIVE]` |
| 2024 | WebAuthn Level 3 -- Signal API | W3C Working Draft | `[EMERGING]` |

**What WebAuthn solved:** Phishing-resistant passwordless authentication. Public key cryptography eliminates shared secrets. Origin binding prevents credential use on phishing sites. Browser-native API (`navigator.credentials.create/get`) provides standardized interface.

**Two ceremonies:**
1. **Registration:** Server generates challenge. Authenticator generates key pair (private key stored in hardware). Returns public key + attestation. Server stores public key.
2. **Authentication:** Server generates challenge. Authenticator locates credential for origin, user performs biometric/PIN. Authenticator signs challenge with private key. Server verifies signature.

**OpenAM implementation:** WebAuthn module (`openam-auth-webauthn`). Classes: `WebAuthnAuthentication`, `WebAuthnRegistration`, `WebAuthnAuthenticationProcessor`, `WebAuthnRegistrationProcessor`. Credential ID + public key + signature counter stored in user LDAP profile. See Ch.02 for detailed flow.

### 1.10 Passkeys -- Synced WebAuthn Credentials (2022-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2022 Jun | Apple, Google, Microsoft announce passkey commitment | FIDO Alliance + platform vendors | -- |
| 2022 Sep | iOS 16 ships passkeys (iCloud Keychain sync) | Apple | `[ACTIVE]` |
| 2022 Oct | Android passkeys via Google Password Manager | Google | `[ACTIVE]` |
| 2023 May | Windows 11 23H2 passkey support | Microsoft | `[ACTIVE]` |
| 2023 Sep | 1Password, Dashlane, Bitwarden add passkey storage | Third-party managers | `[ACTIVE]` |
| 2023 | GitHub, Google, Amazon, PayPal, Best Buy offer passkey login | Industry | `[ACTIVE]` |
| 2024 | Conditional UI (passkey autofill) matures | Chrome, Safari, Edge | `[ACTIVE]` |
| 2024 | FIDO CXP/CXF -- Credential Exchange Protocol/Format | FIDO Alliance | `[EMERGING]` |
| 2025 | Enterprise device-bound passkeys gaining traction | YubiKey 5, Titan | `[ACTIVE]` |

**What passkeys solved:** WebAuthn's device portability problem. Traditional WebAuthn credentials tied to single device; passkeys sync across user's devices via platform credential manager (iCloud Keychain, Google Password Manager). Survives device loss without backup codes.

**Two types:**
- **Synced passkeys:** Stored in cloud credential manager. Cross-device. Convenient. Lower assurance (cloud backup is attack surface). Consumer use case.
- **Device-bound passkeys:** Tied to hardware (YubiKey). Cannot be extracted. Higher assurance. Enterprise/regulated use case.

**FIDO Alliance stats:** 12B+ accounts passkey-enabled as of 2024. Google: 100% employee usage. Major services adopting rapidly.

**OpenAM implementation:** Same WebAuthn module (`openam-auth-webauthn`). No protocol-level difference server-side; passkey sync handled by platform. `[ACTIVE]`

### 1.11 Continuous and Adaptive Authentication (2015-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2015 | Risk-based / adaptive authentication enters mainstream | Industry | `[ACTIVE]` |
| 2017 | NIST SP 800-63B defines Authenticator Assurance Levels (AAL1-3) | NIST | `[ACTIVE]` |
| 2018 | PSD2 Strong Customer Authentication (SCA) mandated in EU | EU | `[ACTIVE]` |
| 2020 | OpenID Shared Signals Framework (CAEP + RISC) | OpenID Foundation | `[EMERGING]` |
| 2023 | CAEP (Continuous Access Evaluation Protocol) gaining adoption | IETF/OpenID | `[EMERGING]` |

**Adaptive authentication:** Context-aware risk scoring at point of login. Signals: device fingerprint, IP geolocation, time-of-day, velocity, threat intelligence. Low risk = password only. High risk = step-up to MFA or deny.

**Continuous authentication:** Goes beyond point-of-login. CAEP enables real-time session revocation when risk changes mid-session (device compromise reported, impossible travel detected, credential stuffing detected). Security Event Tokens (SET, RFC 8417; delivery via RFC 8935/8936) carry signals between providers.

**OpenAM implementation:**
- Adaptive module: `openam-auth-adaptive` -- pluggable risk evaluators.
- Device fingerprinting: `openam-auth-device-id` -- browser/device attribute collection.
- Scripted authentication: `openam-auth-scripted` -- Groovy/JavaScript for custom risk logic and external API calls.

See Ch.02 for detailed adaptive authentication analysis.

### 1.12 MFA Factor Evolution Table

| Generation | Factor Type | Examples | Phishing Resistant? | Era |
|------------|------------|---------|---------------------|-----|
| 1 | Knowledge | Passwords, PINs, security questions | No | 1960s-present |
| 2 | Possession (hardware) | RSA SecurID, smart cards | Partial | 1986-present |
| 3 | Possession (software OTP) | HOTP, TOTP, Google Authenticator | No | 2005-present |
| 4 | Possession (push) | Duo, Microsoft Authenticator, Okta Verify | No (fatigue attacks) | 2012-present |
| 5 | Inherence | Fingerprint, face, iris, voice | N/A (local verification) | 2013-present |
| 6 | Possession (public key) | FIDO U2F, WebAuthn, passkeys | **Yes** | 2014-present |
| 7 | Context | IP, geolocation, device trust, behavior | N/A (risk signal) | 2015-present |
| 8 | Continuous | CAEP, behavioral biometrics, session signals | N/A (ongoing) | `[EMERGING]` |

**Trajectory:** The industry is converging on passkeys (Generation 6) as the primary authentication factor, supplemented by contextual signals (Generation 7) and continuous evaluation (Generation 8). Passwords will persist as fallback for years but are no longer the recommended primary factor per NIST and FIDO Alliance guidance.

---

## Roadmap 2: Federation Protocols

**Arc:** Kerberos cross-realm (1988) --> proprietary SSO cookies (1990s) --> SAML 1.0 (2002) --> Liberty ID-FF (2003) --> SAML 2.0 (2005) --> WS-Federation (2003/2009) --> OpenID 2.0 (2007) --> OAuth 2.0 (2012) --> OpenID Connect (2014) --> OIDC extensions (2019-present) --> GNAP (draft) --> Verifiable Presentations (emerging).

### 2.1 Kerberos Cross-Realm Trust (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1988 | Kerberos V4 cross-realm authentication | MIT | `[OBSOLETE]` |
| 1993 | Kerberos V5 cross-realm with transitive trust | RFC 1510 | `[ACTIVE]` (AD forests) |
| 2000 | Active Directory forest trusts use Kerberos cross-realm | Microsoft | `[ACTIVE]` |
| 2005 | Kerberos V5 revised | RFC 4120 | `[ACTIVE]` |

**First federation protocol:** Kerberos cross-realm enables authentication across administrative boundaries. Realm A's KDC issues ticket for service in Realm B via shared inter-realm key. Active Directory forest trusts build directly on this mechanism.

**Limitations:** Requires pre-shared keys between realms (not scalable), no attribute exchange, no user consent model, no web/HTTP support. These limitations drove development of SAML.

**OpenAM implementation:** Windows Desktop SSO module supports cross-realm Kerberos tickets when OpenAM trusts the AD forest. `[ACTIVE]` within AD environments.

### 2.2 Proprietary SSO Systems (1990s-2000s)

| Year | System | Notes | Status |
|------|--------|-------|--------|
| 1995 | Netscape Directory Server + cookie-based SSO | Early web SSO | `[OBSOLETE]` |
| 1996 | Novell Single Sign-On (NDS-based) | NetWare ecosystem | `[OBSOLETE]` |
| 1999 | Microsoft Passport (later Windows Live ID, now Microsoft Account) | Centralized consumer identity | `[LEGACY]` (concept evolved) |
| 2000 | Netegrity SiteMinder (now Broadcom/CA) | Enterprise web SSO with cookie agents | `[LEGACY]` |
| 2001 | Sun ONE Identity Server (became Sun Access Manager) | OpenSSO/OpenAM ancestor | `[OBSOLETE]` |
| 2001 | IBM Tivoli Access Manager | Enterprise web SSO | `[LEGACY]` |

**What proprietary SSO solved:** Cross-application session sharing within an enterprise domain using shared cookies or agent-mediated session validation. Each vendor implemented their own token format and validation protocol.

**Why replaced:** No interoperability across vendors. No cross-organizational federation. Vendor lock-in. SAML standardized what these products did proprietary.

**OpenAM lineage:** Sun ONE Identity Server (2001) --> Sun Java System Access Manager 7 (2005) --> OpenSSO (2008) --> ForgeRock OpenAM 9-13 (2010-2016) --> OIP OpenAM 14+ (2017) / WrenAM (2018). OpenAM's `iPlanetDirectoryPro` cookie name traces directly to Sun ONE.

### 2.3 SAML 1.0 and 1.1 (2002-2005)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2001 | S2ML and AuthXML competing pre-SAML specs | Netegrity, others | `[OBSOLETE]` |
| 2001 | OASIS Security Services TC chartered | OASIS | -- |
| 2002 Nov | SAML 1.0 | OASIS Standard | `[OBSOLETE]` |
| 2003 Sep | SAML 1.1 | OASIS Standard | `[OBSOLETE]` |

**What SAML 1.0 solved:** First standardized cross-domain SSO. XML-based assertions conveying authentication statements. Browser/POST and Artifact profiles.

**SAML 1.1 additions:** Error handling improvements, minor clarifications. Structurally incompatible with SAML 2.0 (different XML schema).

**OpenAM implementation:** Legacy SAML 1.1 support in `openam-federation-library`. Classes: `SAMLClient`, `SAML11AssertionValidator`. Disabled by default; enabled via configuration flag. Only needed for 20+ year-old SPs.

### 2.4 Liberty Alliance ID-FF (2003-2005)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2001 | Liberty Alliance Project founded (Sun, AOL, HP, Nokia) | Response to Microsoft Passport | -- |
| 2003 | Liberty ID-FF 1.2 (Identity Federation Framework) | Liberty Alliance | `[OBSOLETE]` |
| 2004 | Liberty ID-WSF 1.0 (Identity Web Services Framework) | Liberty Alliance | `[OBSOLETE]` |
| 2005 | Core concepts merged into SAML 2.0 | OASIS | -- |
| 2009 | Liberty Alliance dissolves into Kantara Initiative | Kantara | -- |

**Key Liberty contributions to SAML 2.0:**
- Circle-of-trust model (pre-configured trust relationships via metadata)
- Single logout protocol
- Name identifier management (persistent/transient pseudonyms)
- Account linking (federated identity mapping)

**OpenAM implementation:** Legacy Liberty support in `openam-federation-library`. Classes: `com.sun.liberty.jaxrpc.*`, `com.sun.identity.liberty.ws.common.wsse.*`. Historical artifact from Sun Access Manager lineage. No new deployments.

### 2.5 SAML 2.0 (2005-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2005 Mar | SAML 2.0 published | OASIS Standard | `[ACTIVE]` |
| 2008 | Additional profiles: Holder-of-Key, Delegation, ECP | OASIS | `[ACTIVE]` |
| 2012 | SAML 2.0 errata approved | OASIS | -- |
| 2019 | Metadata extensions: entity categories, interop profiles | REFEDS/InCommon | `[ACTIVE]` |

**What SAML 2.0 solved:** Unified federation standard merging SAML 1.1 + Liberty ID-FF 1.2 + Shibboleth contributions. Cross-organizational SSO via cryptographically signed XML assertions. Five bindings (HTTP-POST, HTTP-Redirect, HTTP-Artifact, SOAP, PAOS), metadata exchange, single logout, attribute statements.

**Core specifications:** `saml-core-2.0-os` (assertions/protocols), `saml-bindings-2.0-os` (transport), `saml-profiles-2.0-os` (use cases), `saml-metadata-2.0-os` (configuration exchange), `saml-authn-context-2.0-os` (authentication strength).

**Federation ecosystems built on SAML 2.0:**
- **InCommon (US higher education):** 1,000+ member institutions, central metadata aggregate
- **eduGAIN (global education):** 70+ national federations, 8,000+ entities
- **FedRAMP (US government):** SAML required for cloud service authorization
- **FICAM (US federal ICAM):** SAML for federal employee access
- **eIDAS (EU):** SAML support mandated alongside OIDC

**Adoption estimate (2025):** Enterprise B2B 80%+. Education 90%+. Government 90%+. Consumer/SaaS: declining (OIDC preferred). Overall: still dominant for enterprise federation, plateau reached ~2015, gradual decline for new integrations.

**SAML weaknesses driving OIDC migration:**
1. XML complexity and verbosity
2. Poor mobile/native app support (PAOS binding rarely implemented)
3. No token refresh mechanism (re-authentication required)
4. Limited API integration (REST APIs prefer JWT)
5. XML Signature vulnerabilities (XXE, wrapping attacks)

**OpenAM implementation:** Full SAML 2.0 IdP and SP. Module paths: `openam-federation/openam-federation-library/`, `openam-federation/OpenFM/`. Key classes: `SAML2ConfigService`, `SAMLPOSTProfileServlet`, `SAMLSOAPReceiver`, `SAML2AssertionValidator`, `SAML2CTSPersistentStore`. Supports all bindings, all NameID formats, metadata generation, certificate management per realm. Assertions stored in CTS for artifact binding and distributed session management. See Ch.03 for full protocol analysis.

### 2.6 WS-Federation and WS-Trust (2002-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2002 | WS-Security 1.0 | IBM/Microsoft/VeriSign | `[LEGACY]` |
| 2003 | WS-Trust 1.0 | IBM/Microsoft | `[LEGACY]` |
| 2003 | WS-Federation 1.0 | IBM/Microsoft/BEA/VeriSign/RSA | `[LEGACY]` |
| 2004 | WS-Security OASIS Standard | OASIS | `[LEGACY]` |
| 2006 | WS-Trust 1.3 | OASIS | `[LEGACY]` |
| 2009 | WS-Federation 1.2 | OASIS | `[LEGACY]` |

**What WS-Federation solved:** Federation for the Microsoft ecosystem. ADFS (Active Directory Federation Services) implements WS-Federation for SSO to SharePoint, Office 365, Dynamics. Passive requestor profile (browser) and active requestor profile (SOAP).

**Adoption (2025):**
- On-premises Microsoft shops: ~40% still use ADFS + WS-Federation (declining from ~60% in 2022)
- Greenfield: <5% (OIDC is Microsoft's recommendation)
- Microsoft's direction: Azure AD/Entra ID supports WS-Federation for backward compatibility; recommends OIDC/SAML 2.0 for new integrations. ADFS development effectively frozen.

**WS-Trust STS concept:** Security Token Service -- issue, renew, validate, cancel, exchange tokens. This concept directly influenced OAuth 2.0 Token Exchange (RFC 8693).

**OpenAM implementation:** WS-Federation module in `openam-federation/openam-federation-library/` and `openam-federation/OpenFM/`. Key classes: `WSFederationService`, `WSFederationClient`, `WSFederationMetaManager`, `WSFederationSingleLogoutHandler`. Tested against ADFS 2.0/3.0/4.0. Supports SAML 1.1 and SAML 2.0 token formats within WS-Federation flows. WS-Trust STS: `WSTrustFactory`, `WSSAuthModule`, token transformation (SAML --> OAuth2, X.509 --> SAML). See Ch.03.

### 2.7 OpenID 1.0/2.0 (2005-2014)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2005 | OpenID 1.0 (Brad Fitzpatrick, LiveJournal) | Community | `[OBSOLETE]` |
| 2006 | OpenID 1.1 + Yadis discovery | Community | `[OBSOLETE]` |
| 2007 | OpenID 2.0 | OpenID Foundation | `[OBSOLETE]` |
| 2008 | OpenID Attribute Exchange (AX) 1.0 | OpenID Foundation | `[OBSOLETE]` |
| 2009-2011 | Peak adoption: Yahoo, Google, AOL, MySpace. 1B+ accounts | Industry | -- |
| 2014 | Effectively superseded by OpenID Connect | Industry | `[OBSOLETE]` |

**What OpenID 2.0 solved:** Decentralized consumer identity. User identified by URL. Any website could be an OpenID provider. Vision: user controls their identity URL and authenticates everywhere with it.

**Why it failed:** Poor UX (URL-based identifiers confusing to users), phishing risks (user redirected to arbitrary URL), no API access model, no mobile support, no standardized attribute schema. Google and Yahoo deprecated OpenID 2.0 endpoints by 2015.

**OpenAM implementation:** No dedicated OpenID 2.0 module. OpenID 2.0 was consumed via OAuth/OIDC authentication modules.

### 2.8 OAuth 1.0 / 1.0a (2007-2012)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2006 | Twitter + Ma.gnolia discuss delegated authorization | Community | Historical |
| 2007 | OAuth 1.0 community specification | Community | `[OBSOLETE]` |
| 2009 | Session fixation attack discovered (Eran Hammer) | Security advisory | -- |
| 2009 | OAuth 1.0a fix | Community | `[OBSOLETE]` |
| 2010 | OAuth 1.0a published as informational RFC | RFC 5849 | `[OBSOLETE]` |

**What OAuth 1.0 solved:** Delegated authorization without sharing passwords. User grants application access to their data at a service provider without giving the application their password. Cryptographic signatures (HMAC-SHA1) on every request.

**Why superseded:** Signature computation complex for developers. Every request required careful construction of signature base string. No standardized token format. OAuth 2.0 dropped signatures in favor of TLS for transport security, dramatically simplifying implementation.

### 2.9 OAuth 2.0 (2012-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2010 | IETF OAuth WG chartered | IETF | -- |
| 2012 Oct | OAuth 2.0 Framework | RFC 6749 | `[ACTIVE]` |
| 2012 Oct | OAuth 2.0 Bearer Token Usage | RFC 6750 | `[ACTIVE]` |
| 2013 | Token Revocation | RFC 7009 | `[ACTIVE]` |
| 2013 | Threat Model and Security Considerations | RFC 6819 | `[ACTIVE]` |
| 2015 | Token Introspection | RFC 7662 | `[ACTIVE]` |
| 2015 | PKCE (Proof Key for Code Exchange) | RFC 7636 | `[ACTIVE]` |
| 2015 | JWT Profile for Client Authentication | RFC 7523 | `[ACTIVE]` |
| 2017 | OAuth 2.0 for Native Apps | RFC 8252 | `[ACTIVE]` |
| 2018 | Authorization Server Metadata | RFC 8414 | `[ACTIVE]` |
| 2019 | Device Authorization Grant | RFC 8628 | `[ACTIVE]` |
| 2020 | Token Exchange (STS) | RFC 8693 | `[ACTIVE]` |
| 2020 | Resource Indicators | RFC 8707 | `[ACTIVE]` |
| 2021 | JWT Access Tokens | RFC 9068 | `[ACTIVE]` |
| 2021 | JWT-Secured Authorization Request (JAR) | RFC 9101 | `[ACTIVE]` |
| 2021 | Pushed Authorization Requests (PAR) | RFC 9126 | `[ACTIVE]` |
| 2022 | Authorization Server Issuer Identification | RFC 9207 | `[ACTIVE]` |
| 2023 | Rich Authorization Requests (RAR) | RFC 9396 | `[ACTIVE]` |
| 2023 | DPoP (Demonstrating Proof-of-Possession) | RFC 9449 | `[ACTIVE]` |
| 2023-2025 | OAuth 2.1 consolidation draft | draft-ietf-oauth-v2-1 | `[EMERGING]` |

**What OAuth 2.0 solved:** Standardized delegated authorization framework. Four grant types (authorization code, implicit, client credentials, resource owner password). Bearer tokens over TLS. Extensible via additional grant types and token types.

**OAuth 2.1 consolidation:** Codifies current best practices into single document. Key changes: PKCE mandatory for authorization code flow, implicit flow removed, resource owner password grant removed, refresh token rotation recommended. Not yet RFC as of 2025.

**Grant types evolution:**
- **Authorization Code + PKCE:** Standard for web and native apps. `[ACTIVE]`
- **Client Credentials:** Machine-to-machine. `[ACTIVE]`
- **Device Authorization (RFC 8628):** Smart TV, CLI tools. `[ACTIVE]`
- **Token Exchange (RFC 8693):** Delegation chains, act-as/on-behalf-of. `[ACTIVE]`
- **~~Implicit~~:** Deprecated (security BCP, OAuth 2.1). `[OBSOLETE]`
- **~~Resource Owner Password~~:** Deprecated (OAuth 2.1). `[OBSOLETE]`

**OpenAM implementation:** Full OAuth 2.0 authorization server in `openam-oauth2/`. All grant types via `GrantTypeHandler` SPI: `AuthorizationCodeGrantTypeHandler`, `ClientCredentialsGrantTypeHandler`, `DeviceCodeGrantTypeHandler`, `JwtBearerGrantTypeHandler`, `TokenExchangeGrantTypeHandler`, `RefreshTokenGrantTypeHandler`. Token storage in CTS (LDAP or Cassandra backend). See Ch.04 for authorization scope analysis, Ch.06 for token format details.

### 2.10 OpenID Connect (2014-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2011 | OIDC development begins | OpenID Foundation | -- |
| 2014 Feb | OpenID Connect Core 1.0 | OpenID Foundation | `[ACTIVE]` |
| 2014 | OIDC Discovery 1.0 | OpenID Foundation | `[ACTIVE]` |
| 2014 | OIDC Dynamic Registration 1.0 | OpenID Foundation | `[ACTIVE]` |
| 2014 | OIDC Session Management 1.0 | OpenID Foundation | `[ACTIVE]` |
| 2017 | OIDC Back-Channel Logout 1.0 | OpenID Foundation | `[ACTIVE]` |
| 2019 | OIDC CIBA (Client-Initiated Backchannel Auth) | OpenID Foundation | `[ACTIVE]` |
| 2021 | OIDC Federation 1.0 (draft) | OpenID Foundation | `[EMERGING]` |
| 2022 | OpenID4VP (Verifiable Presentations) | OpenID Foundation | `[EMERGING]` |
| 2022 | OpenID4VCI (Verifiable Credential Issuance) | OpenID Foundation | `[EMERGING]` |
| 2023 | OIDC Shared Signals Framework (SSF) | OpenID Foundation | `[EMERGING]` |
| 2024 | OIDC Federation gaining traction (eIDAS 2.0) | EU | `[EMERGING]` |

**What OIDC solved:** Modern alternative to SAML for federated authentication. Identity layer on OAuth 2.0. ID Token (signed JWT) contains authentication claims. Simpler than SAML: JSON vs XML, JWT validation vs XML-DSig, Discovery JSON vs XML metadata. Native mobile support via Authorization Code + PKCE.

**OIDC vs SAML comparison:**

| Dimension | SAML 2.0 | OpenID Connect |
|-----------|----------|----------------|
| Format | XML | JSON |
| Token | SAML Assertion | ID Token (JWT) |
| Signature | XML-DSig (RSA-SHA256) | JWS (RS256, ES256) |
| Metadata | XML | JSON (Discovery) |
| Mobile | Poor (PAOS) | Native (Code + PKCE) |
| API access | Not designed | OAuth2 access tokens |
| Refresh | No | Yes (refresh tokens) |

**Adoption trajectory:**
- 2014: Specification published
- 2015-2017: Early adopters (Google, Microsoft migrate from OpenID 2.0)
- 2018-2020: Rapid growth (Auth0, Okta default to OIDC)
- 2021-2023: Enterprise acceleration (50%+ new SaaS integrations use OIDC)
- 2024-2025: Dominant for new projects
- Projection 2030: 80% OIDC / 20% SAML for new integrations

**OIDC Federation (draft):** Automatic trust establishment without manual metadata exchange. Trust anchors publish chain of signed entity statements. Critical for EU Digital Identity Wallet (eIDAS 2.0) scaling to 27 member states. Solves metadata management for large federations. `[EMERGING]`

**OpenAM implementation:**
- OIDC Provider: `openam-oauth2/` -- OAuth2 server with OIDC extensions. Discovery at `/.well-known/openid-configuration`. JWKS endpoint for key publication. ID token signing: RS256, ES256. Dynamic Registration endpoint.
- OIDC RP (authentication module): `openam-auth-oidc/` -- consumes OIDC from external IdPs. Classes: `OpenIdConnectConfig`, `JwtHandlerConfig`, `JwtAttributeMapper`, `OpenIdConnectToken`. Auto-configuration via Discovery.

See Ch.03 for full OIDC protocol analysis.

### 2.11 GNAP -- Grant Negotiation and Authorization Protocol (draft)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2020 | IETF GNAP WG chartered | IETF | -- |
| 2020-2025 | draft-ietf-gnap-core-protocol | IETF | `[EMERGING]` |

**What GNAP aims to solve:** "OAuth 3.0" redesign from first principles. Interaction-centric (not redirect-centric). Supports multiple interaction modes: redirect, app-switch, user code, push. Request objects replace query parameters. Proof-of-possession built in from the start. Better support for constrained devices and multi-party authorization.

**Why it hasn't displaced OAuth 2.0:** OAuth 2.0 ecosystem is massive (dozens of RFCs, millions of deployments). GNAP has no production adoption and limited implementations as of 2025. OAuth 2.1 consolidation addresses most OAuth 2.0 pain points without breaking change.

**OpenAM implementation:** None. No GNAP support.

### 2.12 Federation Protocol Family Tree

```
Kerberos Cross-Realm (1988)
  |
  v
Proprietary SSO (1995-2001)
  |
  +-- S2ML / AuthXML (2001)
  |     |
  |     v
  +-- SAML 1.0 (2002) --> SAML 1.1 (2003)
  |                            |
  +-- Liberty ID-FF (2003) ----+---> SAML 2.0 (2005) [ACTIVE]
  |                            |
  +-- Shibboleth --------     -+
  |
  +-- WS-Security (2002) --> WS-Trust (2003) --> WS-Federation (2003/2009) [LEGACY]
  |                                                    |
  |                                          influenced |
  |                                                    v
  +-- OpenID 1.0/2.0 (2005-2007)            OAuth 2.0 Token Exchange (RFC 8693)
  |     |
  |     v (concept of user-centric identity)
  +-- OAuth 1.0 (2007) --> OAuth 2.0 (2012) [ACTIVE]
  |                            |
  |                            +--> OpenID Connect (2014) [ACTIVE]
  |                            |
  |                            +--> UMA 2.0 (2018) [ACTIVE]
  |                            |
  |                            +--> OAuth 2.1 (draft)
  |                            |
  |                            +--> GNAP (draft) [EMERGING]
  |
  +-- W3C Verifiable Credentials (2019/2022)
        |
        +--> OpenID4VP / OpenID4VCI (2022) [EMERGING]
        |
        +--> SD-JWT VC (2024) [EMERGING]
```

---

## Roadmap 3: Authorization Models

**Arc:** Unix file permissions (1971) --> ACLs (1980s) --> RBAC (1992) --> LDAP ACI (1993) --> J2EE security roles (1999) --> XACML 1.0 (2003) --> OAuth scopes (2012) --> UMA (2015/2018) --> OPA/Rego (2018) --> Zanzibar/ReBAC (2019) --> Cedar (2023) --> policy-as-code (present).

### 3.1 Discretionary Access Control and ACLs (1971-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1971 | Unix file permissions (rwx, user/group/other) | Unix V1, Thompson/Ritchie | `[ACTIVE]` |
| 1983 | POSIX ACLs discussed (extended permission lists) | POSIX.1e draft | `[ACTIVE]` |
| 1985 | DOD Trusted Computer System Evaluation Criteria (Orange Book) formalizes MAC/DAC | TCSEC (DOD 5200.28-STD) | `[LEGACY]` |
| 1993 | Windows NT ACLs (DACLs/SACLs) | Microsoft | `[ACTIVE]` |
| 2003 | NFSv4 ACLs (richer than POSIX) | RFC 3530 | `[ACTIVE]` |

**Unix permissions model:** Owner/group/other with read/write/execute bits. Simple, universal, insufficient for complex authorization. Extended by POSIX ACLs for per-user/per-group entries.

**Windows NT ACLs:** Discretionary Access Control Lists (DACLs) attached to every securable object. Access Control Entries (ACEs) grant/deny specific rights to specific SIDs (Security Identifiers). System ACLs (SACLs) for auditing. More granular than Unix permissions.

**OpenAM relevance:** OpenDJ implements LDAP Access Control Instructions (ACIs) -- LDAP-specific ACL mechanism. ACIs attached to directory entries control who can read/write/search attributes. Critical for protecting identity data in the directory.

### 3.2 Mandatory Access Control (1985-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1985 | Orange Book (TCSEC) defines MAC levels | DOD 5200.28-STD | `[LEGACY]` |
| 1998 | SELinux (NSA Security-Enhanced Linux) | NSA | `[ACTIVE]` |
| 2002 | Common Criteria (ISO 15408) replaces TCSEC | ISO | `[ACTIVE]` |
| 2007 | AppArmor mainstream in Ubuntu | Canonical | `[ACTIVE]` |

**MAC:** System-enforced labels (Top Secret, Secret, Confidential, Unclassified). Users cannot change labels. Bell-LaPadula model (no read up, no write down). Used in military/intelligence systems. SELinux and AppArmor implement MAC for Linux process isolation. `[ACTIVE]` in government/military, niche elsewhere.

### 3.3 Role-Based Access Control -- RBAC (1992-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1992 | Ferraiolo & Kuhn publish RBAC model | NIST | -- |
| 1996 | RBAC96 formal model (Sandhu et al.) | ACM RBAC Workshop | `[ACTIVE]` (concept) |
| 1999 | J2EE security roles (declarative RBAC for Java) | Sun Microsystems | `[ACTIVE]` |
| 2001 | NIST RBAC model submitted to INCITS | INCITS 359-2004 (ratified 2004) | -- |
| 2004 | ANSI INCITS 359-2004 (RBAC standard) | ANSI | `[ACTIVE]` |

**RBAC model:**
- **Core RBAC:** Users assigned to roles; roles assigned permissions. Indirect permission grant via role membership.
- **Hierarchical RBAC:** Role inheritance (Senior Manager inherits Manager permissions).
- **Constrained RBAC:** Static/dynamic separation of duty (SoD). User cannot hold conflicting roles simultaneously.

**Why RBAC dominates:** Simple mental model ("what role does this user have?"). Maps to organizational structure. Supported by every identity platform, every database, every cloud provider.

**RBAC limitations:** Role explosion in large organizations (thousands of roles). Difficulty expressing context-dependent access (same role, different access based on time/location). Led to ABAC/PBAC approaches.

**OpenAM implementation:** Native RBAC via role-based entitlements in `openam-entitlements/`. Roles defined in LDAP (OpenDJ `groupOfUniqueNames`, `nsRoleDN`). Policy evaluation checks subject role membership. `RoleSubject`, `GroupSubject` conditions in policy engine. J2EE agent maps OpenAM roles to servlet container roles.

### 3.4 XACML -- eXtensible Access Control Markup Language (2003-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2003 Feb | XACML 1.0 | OASIS Standard | `[OBSOLETE]` |
| 2005 Feb | XACML 2.0 -- obligations, improved combining algorithms | OASIS Standard | `[OBSOLETE]` |
| 2010 | XACML 3.0 Committee Draft | OASIS | -- |
| 2013 Jan | XACML 3.0 -- JSON profile, REST profile, delegation | OASIS Standard | `[LEGACY]` |
| 2014 | XACML 3.0 JSON Profile | OASIS Committee Spec | `[LEGACY]` |
| 2014 | ALFA (Abbreviated Language for Authorization) | Axiomatics proprietary | `[LEGACY]` |

**What XACML solved:** Standardized attribute-based access control (ABAC). Four-attribute model: Subject, Resource, Action, Environment. PDP/PEP/PIP/PAP architecture separating decision from enforcement. Combining algorithms resolve policy conflicts. Obligations specify post-decision actions. The most comprehensive authorization standard ever published.

**Why adoption stalled:** (1) XML verbosity -- simple rule requires 50+ lines. (2) Performance -- multi-tier PDP/PIP architecture adds latency. (3) Developer friction -- no native SDK ecosystem for modern languages. (4) Deployment complexity -- multiple infrastructure components. (5) No cloud-native tooling. (6) Commercial vendor lock-in (Axiomatics, IBM, Oracle). See Ch.04 for detailed analysis.

**OpenAM implementation:** XACML 3.0 policy engine via `openam-entitlements/`. Key classes: `XACMLReaderWriter`, `XACMLPrivilegeUtils`, `XACMLApplicationUtils`. Dual storage: native JSON format (performance-optimized) and XACML 3.0 XML (standards compliance). Import/export capability. Policy evaluation via REST: `POST /json/policies?_action=evaluate`. Caching layer with TTL-based invalidation. Conditions: `IPv4Condition`, `IPv6Condition`, `TimeCondition`, `LEAuthLevelCondition`, `SessionPropertyCondition`, `ScriptCondition`.

### 3.5 OAuth 2.0 Scopes as Authorization (2012-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2012 | OAuth 2.0 scopes defined | RFC 6749 | `[ACTIVE]` |
| 2015 | Token introspection (scope validation) | RFC 7662 | `[ACTIVE]` |
| 2023 | Rich Authorization Requests (RAR) | RFC 9396 | `[ACTIVE]` |

**What scopes solve:** Coarse-grained API authorization. Scopes limit what a client application can do with a user's data. User consents to specific scopes during authorization flow. Resource server validates scopes in access token.

**Scope patterns:** Simple (`read`, `write`), resource-based (`files:read`), hierarchical (`api.read.public`), URN (`urn:example:api:read`).

**Limitations:** Scopes are coarse -- "can this client access this API category?" not "can this user edit document 12345?" Fine-grained authorization requires supplementary mechanisms (see 3.7-3.10).

**RAR (RFC 9396):** Extends OAuth 2.0 with `authorization_details` parameter for structured authorization requests beyond scope strings. Adopted in Open Banking, financial APIs.

**OpenAM implementation:** OAuth2 scopes in `openam-oauth2/`. Flat string matching by default. Custom `ScopeValidator` SPI for hierarchical or contextual scope logic. See Ch.04.

### 3.6 UMA 2.0 -- User-Managed Access (2015/2018-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2010 | UMA WG formed at Kantara Initiative | Eve Maler | -- |
| 2015 | UMA 1.0 | Kantara Recommendation | Superseded |
| 2018 | UMA 2.0 | Kantara Recommendation | `[ACTIVE]` niche |

**What UMA solved:** User-controlled resource sharing without user presence at authorization time. Resource owner pre-configures policies. Requesting party gets Requesting Party Token (RPT) via permission ticket + claims gathering flow. Three-party authorization: resource owner, requesting party, authorization server.

**Why adoption is limited:** Complexity (three-party model), UX challenges (users don't manage fine-grained policies), chicken-and-egg (few resource servers implement UMA), OAuth 2.0 sufficiency for most delegation scenarios.

**Niche success:** Healthcare (HEART working group profiles UMA for FHIR), financial services (limited), personal data stores (MyData, Solid).

**OpenAM implementation:** `openam-uma/`. Endpoints: `/oauth2/resource_set`, `/oauth2/permission`, `/oauth2/token` (UMA grant type), `/oauth2/introspect`. Resources stored in CTS as `UMA_RESOURCE_SET`. Policies via entitlements framework. `IdTokenClaimGatherer`, `UmaLabelsStore`, `UmaGuiceModule`. See Ch.04.

### 3.7 Open Policy Agent / Rego (2018-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2016 | Styra founded, OPA development begins | Styra | -- |
| 2018 | OPA donated to CNCF (sandbox) | CNCF | -- |
| 2021 | OPA graduates from CNCF | CNCF | `[ACTIVE]` |
| 2021 | Gatekeeper (OPA for Kubernetes admission) matures | CNCF | `[ACTIVE]` |

**What OPA solved:** Cloud-native, embeddable policy engine. Rego language is declarative, purpose-built for policy. Runs as sidecar or in-process library -- microsecond to millisecond evaluation, no external PDP network call. JSON input/output. Kubernetes-native via Gatekeeper admission controller.

**Advantages over XACML:** Embeddable (no external PDP), fast (no network calls), developer-friendly (Rego vs XML), cloud-native (CNCF ecosystem), mature tooling (REPL, testing, IDE plugins).

**Use cases:** Kubernetes admission control, microservice authorization, infrastructure policy (Terraform, Docker), API gateway authorization, data filtering.

**OpenAM integration:** No built-in OPA integration. Organizations can deploy OPA alongside OpenAM: OpenAM handles authentication and coarse-grained authorization (OAuth scopes), OPA handles fine-grained resource-level authorization at the application or API gateway layer.

### 3.8 Google Zanzibar and ReBAC Systems (2019-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2019 | Google publishes Zanzibar paper (USENIX ATC) | Google | -- |
| 2020 | Authzed founded (SpiceDB) | Authzed | `[ACTIVE]` |
| 2021 | Ory Keto (Zanzibar implementation) | Ory | `[ACTIVE]` |
| 2022 | OpenFGA released by Okta/Auth0, donated to CNCF | CNCF Sandbox | `[ACTIVE]` |

**What Zanzibar/ReBAC solved:** Relationship-based access control. Authorization determined by graph traversal of subject-relation-object tuples. Example: `user:alice#member@group:engineering`, `group:engineering#viewer@doc:123`. "Can alice view doc:123?" answered by graph walk.

**Zanzibar scale:** Google's production system handles trillions of authorization checks per day with millisecond latency.

**Open-source implementations:**
- **SpiceDB (Authzed):** ~5k GitHub stars. High-performance, global consistency, distributed. `[ACTIVE]`
- **OpenFGA (Okta/Auth0):** CNCF sandbox. ~3k stars. Go-based, REST API, modeling DSL. `[ACTIVE]`
- **Ory Keto:** ~4.9k stars. Part of Ory stack. Kubernetes-native. `[ACTIVE]`

**Use cases:** Multi-tenant SaaS with complex sharing (Google Workspace model), hierarchical resources, fine-grained document-level authorization.

**OpenAM integration:** No built-in ReBAC support. Complementary: OAuth 2.0/OIDC (OpenAM) for authentication and API-level authorization; ReBAC engine for resource-level authorization.

### 3.9 Cedar (2023-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2023 May | Cedar open-sourced by AWS (Apache 2.0) | AWS | `[EMERGING]` |
| 2023 | Amazon Verified Permissions (AVP) -- managed Cedar service | AWS | `[EMERGING]` |
| 2024 | Cedar formal verification in Lean 4 published | AWS/academic | `[EMERGING]` |

**What Cedar solved:** Authorization-specific policy language with formal verification. Policies are decidable and analyzable -- detect conflicts, prove properties before deployment. Hierarchical entity model built in. Powers Amazon Verified Permissions.

**Cedar vs OPA:** Cedar is authorization-specific (not general-purpose). Formally verified for soundness (unique in the space). Built-in entity model vs OPA's user-defined schemas. AWS-centric ecosystem vs OPA's cross-cloud CNCF ecosystem.

**OpenAM integration:** None. Cedar is a potential future alternative for fine-grained authorization alongside or replacing XACML policies.

### 3.10 Authorization Model Comparison

| Model | Era | Granularity | Performance | Developer UX | Cloud-Native | OpenAM Support |
|-------|-----|-------------|-------------|--------------|--------------|----------------|
| Unix permissions | 1971 | Coarse (rwx) | Native | Simple | N/A | N/A |
| RBAC | 1992 | Medium (role-based) | Fast | Good | Yes | **Yes** (entitlements) |
| XACML 3.0 | 2003/2013 | Fine (ABAC) | Slow (PDP) | Poor | No | **Yes** (import/export) |
| OAuth scopes | 2012 | Coarse (API-level) | Fast | Good | Yes | **Yes** (OAuth2 module) |
| UMA 2.0 | 2018 | Fine (resource-level) | Medium | Complex | Partial | **Yes** (UMA module) |
| OPA/Rego | 2018 | Fine (any) | Fast (embedded) | Good | Yes | No (complementary) |
| ReBAC/Zanzibar | 2019 | Fine (relationship) | Fast (graph) | Good | Yes | No (complementary) |
| Cedar | 2023 | Fine (entity-based) | Fast | Good | AWS-native | No |

**Trajectory:** RBAC remains baseline. OAuth scopes handle API authorization. Fine-grained authorization moving to OPA (Kubernetes/cross-cloud), Cedar (AWS), or ReBAC (complex sharing). XACML maintained for compliance in legacy enterprises but not recommended for new projects.

---

## Roadmap 4: Token Formats & Session Management

**Arc:** Kerberos tickets (1988) --> SAML assertions (2002) --> proprietary session cookies (2000s) --> OpenAM CTS tokens (2012) --> OAuth 2.0 bearer tokens (2012) --> JWT (2015) --> JWT access tokens (2021) --> DPoP sender-constrained tokens (2023) --> Verifiable Credentials (2022) --> SD-JWT selective disclosure (emerging).

### 4.1 Kerberos Tickets (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1988 | Kerberos V4 tickets (DES encrypted) | MIT | `[OBSOLETE]` |
| 1993 | Kerberos V5 tickets (ASN.1 encoded, extensible) | RFC 1510 | `[ACTIVE]` |
| 2005 | AES encryption for Kerberos tickets | RFC 3962 | `[ACTIVE]` |

**Structure:** ASN.1 encoded. Contains: client principal, server principal, session key, validity times, authorization data. Encrypted with server's long-term key (client cannot read ticket contents). TGT encrypted with KDC key; service tickets encrypted with service key.

**Properties:** Opaque to client (encrypted), server-validated (decryption with own key), time-limited (typically 10 hours for TGT), renewable. Bearer token -- possession grants access.

**Current relevance:** Every Active Directory authentication produces Kerberos tickets. Billions created daily across enterprise networks. `[ACTIVE]` in AD environments.

### 4.2 SAML Assertions (2002-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2002 | SAML 1.0 assertions | OASIS | `[OBSOLETE]` |
| 2005 | SAML 2.0 assertions | OASIS | `[ACTIVE]` |

**Structure:** XML document containing Issuer, Subject (NameID), Conditions (NotBefore/NotOnOrAfter, AudienceRestriction), AuthnStatement (authentication event), AttributeStatement (user attributes). Signed via XML-DSig (RSA-SHA256). Optionally encrypted via XML-Enc (AES-256).

**Subject confirmation methods:**
- `bearer` -- holder of assertion is the subject (most common for web SSO)
- `holder-of-key` -- subject must prove possession of cryptographic key
- `sender-vouches` -- third party vouches (rare)

**Properties:** Self-contained (all claims in assertion), cryptographically verifiable (XML-DSig), time-limited (5 min typical), audience-restricted, optionally encrypted. Verbose (1-5 KB typical).

**OpenAM implementation:** `openam-federation/openam-federation-library/`. `SAML2AssertionValidator` (signature/encryption/condition validation), `SAML2Token` (object model), `SAML2CTSPersistentStore` (CTS storage for artifacts). Assertions created during IdP SSO flow, signed with realm-specific certificates from JKS. See Ch.06 for detailed structure analysis.

### 4.3 Proprietary Session Cookies and OpenAM CTS (2000s-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2000s | Proprietary session cookies (SiteMinder, OpenAM `iPlanetDirectoryPro`) | Vendor-specific | `[ACTIVE]` |
| 2012 | OpenAM Core Token Service (CTS) formalized | OIP/ForgeRock | `[ACTIVE]` |

**OpenAM session cookie:** `iPlanetDirectoryPro` cookie containing opaque session ID (UUID). Server-side session state stored in CTS. Cookie value is not self-contained -- requires server-side lookup.

**CTS token types:**
- `SESSION` -- OpenAM session state (user ID, properties, auth level, creation/access/expiry times)
- `OAUTH2_GRANT_SET` -- Authorization codes (1-10 min TTL)
- `OAUTH2_ACCESS_TOKEN` -- Access tokens (1-60 min TTL)
- `OAUTH2_REFRESH_TOKEN` -- Refresh tokens (days-months TTL)
- `SAML2_ASSERTION` / `SAML2_ARTIFACT` -- SAML artifacts (5 min TTL)
- `UMA_RESOURCE_SET` / `UMA_PERMISSION_TICKET` / `UMA_REQUESTING_PARTY_TOKEN`
- `JWT_BLACKLIST` -- Revoked JWT identifiers (remaining token lifetime as TTL)

**CTS backends:**
- **OpenDJ (LDAP):** Default. Multi-master replication, persistent search. Schema: `frCoreToken` objectClass with `coreTokenId`, `coreTokenType`, `coreTokenUserId`, `coreTokenExpirationDate`. Suited for single-datacenter, <100k tokens.
- **Cassandra:** Horizontal scale, multi-datacenter replication, eventual consistency. Suited for global deployments, millions of tokens.
- **Redis (experimental):** Sub-millisecond latency. Suited for high-throughput scenarios.

See Ch.06 for detailed CTS architecture.

### 4.4 OAuth 2.0 Bearer Tokens (2012-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2012 | Bearer token usage | RFC 6750 | `[ACTIVE]` |
| 2013 | Token revocation | RFC 7009 | `[ACTIVE]` |
| 2015 | Token introspection | RFC 7662 | `[ACTIVE]` |

**Bearer tokens:** "Anyone possessing the token can use it." No proof of identity required beyond token presentation. Relies on TLS for transport security. Simple but vulnerable to token theft (XSS, log leakage, man-in-the-middle without TLS).

**Two forms:**
1. **Opaque tokens:** Random string. Server-side lookup for validation (introspection endpoint, RFC 7662). Revocable by deleting from store.
2. **JWT tokens:** Self-contained. Client-side validation (signature verification). Revocation requires blacklist or short expiration.

**OpenAM implementation:** `openam-oauth2/`. Both opaque and JWT access tokens supported. Opaque tokens stored in CTS; validated via introspection. JWT tokens signed with RS256; validated via JWKS endpoint. `IntrospectableToken` interface for introspection handler.

### 4.5 JSON Web Token -- JWT (2015-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2015 May | JWT | RFC 7519 | `[ACTIVE]` |
| 2015 May | JWS (JSON Web Signature) | RFC 7515 | `[ACTIVE]` |
| 2015 May | JWE (JSON Web Encryption) | RFC 7516 | `[ACTIVE]` |
| 2015 May | JWK (JSON Web Key) | RFC 7517 | `[ACTIVE]` |
| 2015 May | JWA (JSON Web Algorithms) | RFC 7518 | `[ACTIVE]` |
| 2021 | JWT Profile for Access Tokens | RFC 9068 | `[ACTIVE]` |

**Structure:** Three Base64URL-encoded sections: header.payload.signature.

**Header:** `alg` (signing algorithm), `typ` ("JWT"), `kid` (key ID for rotation).

**Payload:** Registered claims (`iss`, `sub`, `aud`, `exp`, `iat`, `nbf`, `jti`) + custom claims.

**Signing algorithms:**
- **HMAC:** HS256/384/512 (symmetric, shared secret). `[ACTIVE]`
- **RSA:** RS256/384/512 (asymmetric, PKCS#1 v1.5). `[ACTIVE]` (most common)
- **RSA-PSS:** PS256/384/512 (asymmetric, PSS padding, more secure). `[ACTIVE]`
- **ECDSA:** ES256/384/512 (elliptic curve, smaller signatures). `[ACTIVE]`
- **EdDSA:** Ed25519 (fast, deterministic). `[EMERGING]`
- **none:** Unsigned. **Security risk.** `[ACTIVE]` (must be explicitly rejected)

**Encryption (JWE):** Five-part format: header.encrypted_key.iv.ciphertext.tag. Hybrid encryption: symmetric CEK encrypted with recipient's public key. Content encrypted with CEK (AES-GCM preferred).

**JWT access tokens (RFC 9068):** Standardized JWT structure for OAuth 2.0 access tokens. Standard claims: `iss`, `sub`, `aud`, `exp`, `iat`, `jti`, `client_id`, `scope`, `auth_time`. Enables resource servers to validate tokens without introspection.

**OpenAM implementation:**
- JWT signing/validation: `openam-oauth2/` -- JWKS endpoint at `/oauth2/jwks`. RS256, ES256 supported. Key rotation via `kid`.
- Stateless JWT sessions: `openam-core/.../session/stateless/` -- `JwtSessionMapper` converts sessions to JWT. `StatelessJWTCache` for validation caching. Session properties mapped to JWT claims. Configurable per realm.
- JWT blacklisting for revocation: `JWT_BLACKLIST` CTS entries with `jti` as key and remaining token lifetime as TTL.

See Ch.06 for comprehensive JWT analysis.

### 4.6 DPoP -- Demonstrating Proof-of-Possession (2023-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2021 | DPoP draft published | IETF | -- |
| 2023 | DPoP standardized | RFC 9449 | `[ACTIVE]` |

**What DPoP solved:** Sender-constrained tokens without mTLS. Client generates ephemeral key pair, creates DPoP proof JWT signed with private key, binds access token to public key. Each API request requires new DPoP proof for that specific HTTP method + URI. Stolen token is useless without private key.

**DPoP proof JWT structure:**
```
Header: { "typ": "dpop+jwt", "alg": "ES256", "jwk": { <public_key> } }
Payload: { "jti": "<unique>", "htm": "GET", "htu": "https://api.example.com/data", "iat": <timestamp>, "ath": "<access_token_hash>" }
```

**Advantages over bearer:** Token theft useless (private key required), replay protection (unique jti per request), TLS-agnostic (works in multi-hop scenarios).

**Adoption:** Banking (Open Banking, FAPI), enterprise APIs requiring high assurance. Limited consumer adoption. `[ACTIVE]` in financial sector, `[EMERGING]` broadly.

**OpenAM implementation:** Limited. DPoP support is not a core OpenAM feature as of current OIP releases. Can be implemented via scripted authentication or custom OAuth2 token handlers.

### 4.7 OAuth 2.0 mTLS Client Certificate-Bound Tokens (2020)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2020 | OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens | RFC 8705 | `[ACTIVE]` |

**What mTLS token binding solved:** Access tokens bound to client's TLS certificate. Resource server validates that the certificate used to present the token matches the certificate used when the token was issued. Prevents token export.

**OpenAM implementation:** Supported at infrastructure level. OAuth2 endpoints can require mTLS client authentication. Token `cnf` (confirmation) claim contains certificate thumbprint.

### 4.8 Token Binding (2018) -- Failed Approach

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2018 | Token Binding over HTTP | RFC 8473 | `[OBSOLETE]` |

**What it attempted:** Cryptographically bind tokens to TLS connections. Token usable only over same TLS connection where issued.

**Why it failed:** Limited browser support (only Chrome/Edge briefly). TLS resumption and HTTP/2 multiplexing complicated the model. Deprecated by major browsers in 2020. **DPoP superseded token binding** with a simpler, TLS-independent approach. `[OBSOLETE]`

### 4.9 Verifiable Credentials (2019-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2017 | W3C Verifiable Claims WG formed | W3C | -- |
| 2019 | Verifiable Credentials Data Model 1.0 | W3C Recommendation | Superseded |
| 2022 | VC Data Model 1.1 | W3C Recommendation | Superseded |
| 2023 | VC Data Model 2.0 | W3C Candidate Recommendation | `[EMERGING]` |
| 2023 | VC-JOSE-COSE (JWT-based VCs) | W3C | `[EMERGING]` |
| 2024 | SD-JWT VC (selective disclosure) | IETF Draft | `[EMERGING]` |

**What VCs solve:** Cryptographically verifiable digital credentials issued by authorities. Issuer --> Holder --> Verifier model. Format-agnostic: JSON-LD, JWT, CBOR. Holder can present credentials without contacting issuer (offline verification).

**SD-JWT (Selective Disclosure JWT):** Holder reveals only specific claims. Issuer creates JWT with hashed claims + separate disclosures. Holder selects which disclosures to reveal. Verifier sees only chosen claims but can verify they came from issuer. Privacy-preserving identity verification.

**Adoption:** Government-driven. EU Digital Identity Wallet (eIDAS 2.0) mandated by 2026 using OpenID4VP + SD-JWT VC. US mobile driver's licenses (ISO 18013-5) in several states. Korea national digital ID. British Columbia OrgBook.

**OpenAM implementation:** No native VC issuance/verification. Future integration point: OpenAM could serve as VC issuer (trusted IdP issues VCs) or integrate with VC verification for authentication. `[EMERGING]` integration opportunity.

### 4.10 Session Management Evolution

| Generation | Model | Characteristics | Trade-offs |
|------------|-------|----------------|------------|
| 1 | Server-side sticky sessions | In-memory session on single server. Load balancer affinity. | Simple; no HA, server failure loses sessions |
| 2 | Replicated sessions | Session replicated across cluster (multicast, database) | HA; replication lag, bandwidth overhead |
| 3 | CTS centralized store | OpenAM CTS in LDAP/Cassandra. Any server validates any session. | HA + horizontal scale; database bottleneck |
| 4 | Stateless JWT sessions | Session state embedded in signed JWT. No server-side storage. | Infinite scale; revocation complexity, token size |
| 5 | Hybrid (short JWT + refresh) | Short-lived JWT for API (5-15 min) + long-lived refresh token in CTS | Fast API + revocation within JWT lifetime window |

**OpenAM supports Generations 3-5:**
- **Generation 3:** Default stateful sessions in CTS (LDAP or Cassandra). `iPlanetDirectoryPro` cookie. Session validation requires CTS lookup.
- **Generation 4:** Stateless JWT sessions (per-realm configuration). `JwtSessionMapper` converts sessions to JWT. `StatelessJWTCache` for signature caching.
- **Generation 5:** OAuth2 hybrid -- JWT access tokens (short-lived, stateless) + refresh tokens in CTS (long-lived, revocable). Session blacklist for emergency revocation.

**Distributed session replication:**
- **LDAP (OpenDJ multi-master):** CSN-based replication. Milliseconds to seconds latency.
- **Cassandra:** Tunable consistency (LOCAL_QUORUM for writes, eventual for reads). Multi-datacenter.
- **JWT stateless:** Zero replication -- token validated locally. Ideal for multi-region.

**Modern best practice:** Hybrid approach (Generation 5). JWT access tokens for API performance. Refresh tokens in CTS for revocation. Blacklist in CTS for emergency invalidation. Revocation window = JWT lifetime (5-15 minutes), acceptable for most use cases.

---

## Roadmap 5: Directory Services & Identity Stores

**Arc:** X.500/DAP (1988) --> LDAPv2 (1995) --> LDAPv3 (1997/2006) --> DSML v2 (2002) --> REST-to-LDAP (2013) --> SCIM (2011/2015) --> cloud directories (2013+) --> relational identity stores (2020+) --> event-sourced identity (2021+).

### 5.1 X.500 and DAP (1988-1990s)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1988 | ITU-T X.500 series published (X.500-X.521) | ITU-T | `[OBSOLETE]` |
| 1988 | X.509 v1 defined within X.500 series | ITU-T X.509 | See 1.3 above |
| 1993 | X.500 (1993 edition) -- access control, replication | ITU-T | `[OBSOLETE]` |

**What X.500 solved:** Global, hierarchical directory service. Distinguished Name (DN) hierarchy: `cn=Alice,ou=Engineering,o=Example,c=US`. Directory Access Protocol (DAP) over full OSI stack.

**Why it failed for TCP/IP networks:** Required complete OSI implementation. Extremely heavyweight for simple name lookup. Led directly to LDAP as "lightweight" alternative running over TCP.

**Legacy contribution:** DN hierarchy model, information model (entries, attributes, object classes), X.509 certificate format -- all inherited by LDAP.

### 5.2 LDAP Evolution (1993-present)

| Year | Version | RFC(s) | Key Changes | Status |
|------|---------|--------|-------------|--------|
| 1993 | LDAPv1 | RFC 1487 | Lightweight X.500 access over TCP. Read-only DAP subset. Tim Howes et al. at U-Michigan. | `[OBSOLETE]` |
| 1995 | LDAPv2 | RFC 1777/1778/1779 | Write operations (add/delete/modify/modrdn). Simple bind. DN string representation. | `[OBSOLETE]` |
| 1997 | LDAPv3 | RFC 2251-2256 | SASL authentication, TLS (StartTLS), extensible controls/extended operations, UTF-8, referrals, schema publication. Internet Standard. | Superseded |
| 2006 | LDAPv3 revised | RFC 4510-4519 | Technical refresh. 4510 (roadmap), 4511 (protocol), 4512 (info models), 4513 (auth methods), 4514 (DN string), 4515 (search filters), 4516 (URL), 4517 (syntaxes), 4518 (internationalized matching), 4519 (schema). | `[ACTIVE]` |

**Key LDAP extensions:**
- RFC 3062 (2001): Password Modify Extended Operation `[ACTIVE]`
- RFC 4370 (2006): Proxied Authorization Control `[ACTIVE]`
- RFC 4532 (2006): "Who am I?" extended operation `[ACTIVE]`
- RFC 4533 (2006): Content Synchronization (syncrepl) -- critical for replication `[ACTIVE]`
- RFC 5805 (2010): LDAP Transactions `[ACTIVE]`

**OpenDJ implementation:** Open Identity Platform's LDAPv3 directory server (`OpenDJ/`). Full LDAPv3 compliance. 21 modules. `opendj-core/` uses RxJava 3 reactive streams. `opendj-server-legacy/` main server (1,927 Java files). Key features:
- **Multi-master replication:** CSN-based changelog replication between data centers. Conflict resolution via operational attributes.
- **Backend pluggability:** JE (Berkeley DB Java Edition), PDB, and experimental backends.
- **REST-to-LDAP gateway:** `opendj-rest2ldap/` -- expose LDAP data as JSON REST APIs.
- **Virtual attributes:** Computed attributes (memberOf, isMemberOf) without schema storage.
- **Password policies:** Configurable complexity, history, lockout, PBKDF2/SSHA-512 hashing.

**Other major LDAP implementations:**
- **Active Directory (Microsoft):** Dominant enterprise directory. LDAP interface over proprietary Jet database. AD-specific extensions (Global Catalog, NTLM, Group Policy). `[ACTIVE]`
- **389 Directory Server (Red Hat):** Open-source, used by FreeIPA. `[ACTIVE]`
- **OpenLDAP:** Open-source reference implementation. `[ACTIVE]`
- **Ping Directory (Ping Identity):** Commercial, high-performance. `[ACTIVE]`
- **Apache Directory (ApacheDS):** Java-based, Eclipse LDAP tools. `[ACTIVE]`

### 5.3 DSML v2 -- Directory Services Markup Language (2002)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2001 | DSML v1.0 (XML representation of directory data) | OASIS | `[OBSOLETE]` |
| 2002 | DSML v2.0 (LDAP operations as SOAP/XML) | OASIS | `[OBSOLETE]` |

**What DSML solved:** Web services access to directories via SOAP/XML. Mapped LDAP operations to XML request/response. Attempted to bridge directories and SOA world.

**Why it failed:** SOAP complexity. REST/JSON displaced SOAP. SCIM (2011) solved the same problem more simply. No production use today. `[OBSOLETE]`

### 5.4 Active Directory and Microsoft Entra ID (2000-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2000 | Active Directory in Windows 2000 | Microsoft | `[ACTIVE]` |
| 2003 | AD Federation Services (ADFS) v1.0 | Microsoft | `[LEGACY]` |
| 2008 | AD Domain Services matured (AD DS) in Windows Server 2008 | Microsoft | `[ACTIVE]` |
| 2010 | Azure Active Directory preview | Microsoft | -- |
| 2013 | Azure Active Directory GA | Microsoft | `[ACTIVE]` |
| 2017 | Azure AD Connect (hybrid identity sync) | Microsoft | `[ACTIVE]` |
| 2023 | Azure AD renamed to Microsoft Entra ID | Microsoft | `[ACTIVE]` |
| 2024 | Entra ID Governance, Entra Permissions Management | Microsoft | `[ACTIVE]` |

**Active Directory:** On-premises directory. LDAP + Kerberos + Group Policy + DNS integration. Foundation of enterprise Windows identity for 25 years. 90%+ of Fortune 500 use AD.

**Microsoft Entra ID (formerly Azure AD):** Cloud identity platform. OIDC/OAuth 2.0/SAML 2.0 provider. SCIM provisioning. Conditional Access (adaptive MFA). Device registration. Application proxy. Graph API for identity management.

**AD --> Entra ID migration path:** Azure AD Connect syncs on-premises AD to Entra ID. Hybrid identity: users authenticate against either AD or Entra ID. Microsoft's long-term strategy: Entra ID as primary, AD as legacy compatibility.

**OpenAM relevance:** OpenAM's AD authentication module (`openam-auth-ad`) integrates with on-premises AD. OpenAM can federate with Entra ID via SAML 2.0 or OIDC, serving as an alternative IdP for organizations not fully committed to Microsoft's identity stack.

### 5.5 SCIM -- System for Cross-domain Identity Management (2011-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2003 | SPML 1.0 (predecessor, SOAP-based) | OASIS | `[OBSOLETE]` |
| 2006 | SPML 2.0 | OASIS | `[OBSOLETE]` |
| 2011 | SCIM 1.0 draft | IETF | Superseded |
| 2012 | SCIM 1.1 draft (widely implemented despite draft status) | IETF | Superseded |
| 2015 | SCIM 2.0 | RFC 7642 (concepts), RFC 7643 (schema), RFC 7644 (protocol) | `[ACTIVE]` |
| 2023 | IETF SCIM WG rechartered for SCIM 2.1 | IETF | `[EMERGING]` |

**What SCIM solved:** REST/JSON identity provisioning. Standard schema for Users and Groups. CRUD + PATCH + bulk + filtering. Replaced SPML (SOAP/XML, failed adoption).

**SCIM 2.0 endpoints:** `/Users`, `/Groups`, `/Schemas`, `/ResourceTypes`, `/ServiceProviderConfig`, `/Bulk`.

**SCIM 2.0 user schema (core):** `id`, `externalId`, `userName`, `name` (givenName, familyName), `displayName`, `emails[]`, `phoneNumbers[]`, `addresses[]`, `groups[]`, `roles[]`, `active`, `meta` (created, lastModified).

**Adoption (2025):** 70%+ of major SaaS providers support SCIM 2.0. Microsoft Entra ID, Okta, OneLogin, Salesforce, Google Workspace, Slack, Zoom, AWS IAM Identity Center, Atlassian, ServiceNow, Workday all support SCIM provisioning.

**SCIM limitations:** Schema negotiation underspecified, PATCH semantics vary between implementations, no password sync standard, no event/webhook standard (addressed by OIDC Shared Signals / SSF in SCIM 2.1 work).

**OpenIDM implementation:** Open Identity Platform's OpenIDM (`OpenIDM/`) implements SCIM 2.0 provisioning endpoints. OSGi-based architecture. Reconciliation engine syncs identities between authoritative sources (HR systems) and target systems (LDAP, SaaS applications) via SCIM. Connector framework (OpenICF) provides LDAP, database, CSV, SSH connectors for non-SCIM targets.

### 5.6 Cloud Directories (2013-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2013 | Azure Active Directory (now Entra ID) | Microsoft | `[ACTIVE]` |
| 2013 | AWS Directory Service (Managed AD, Simple AD) | AWS | `[ACTIVE]` |
| 2014 | Google Cloud Identity / Google Workspace Directory | Google | `[ACTIVE]` |
| 2017 | JumpCloud (cloud directory-as-a-service) | JumpCloud | `[ACTIVE]` |
| 2019 | Okta Universal Directory | Okta | `[ACTIVE]` |

**The "LDAP demotion" trend:** Cloud directories expose identity data via REST/GraphQL APIs (Microsoft Graph, Google Admin SDK, Okta API) rather than LDAP. LDAP interface provided for backward compatibility but not the primary interface. Identity data stored in proprietary backends (Azure Cosmos DB, Google Bigtable), not LDAP servers.

**Implications for LDAP:**
- LDAP protocol remains necessary for legacy application compatibility
- New applications use REST APIs (SCIM, vendor-specific) for identity queries
- LDAP is increasingly a compatibility layer, not the native protocol
- Virtual directory products (Radiant Logic) bridge LDAP and REST/cloud sources

### 5.7 Relational and Event-Sourced Identity Stores (2020-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2014 | Keycloak uses PostgreSQL/MySQL as identity store | Red Hat | `[ACTIVE]` |
| 2020 | Authentik uses PostgreSQL | Authentik | `[ACTIVE]` |
| 2021 | Zitadel uses CockroachDB with event sourcing | CAOS AG | `[EMERGING]` |
| 2022 | Casdoor uses MySQL/PostgreSQL | Casbin | `[ACTIVE]` |

**The relational identity store trend:** Modern open-source identity platforms use PostgreSQL or MySQL instead of LDAP directories as their primary identity store. Reasons: simpler operational model (no LDAP expertise required), better tooling (SQL, ORM), transactional guarantees (ACID), cloud-managed options (RDS, Cloud SQL).

**Event-sourced identity (Zitadel):** All identity changes stored as immutable event stream in CockroachDB. Current state derived by replaying events. Benefits: complete audit trail, temporal queries ("what was the user's state on date X?"), event-driven integration. Trade-off: complexity, storage growth.

**OpenDJ's position:** OpenDJ remains a full-featured LDAP directory. For organizations already invested in LDAP (Active Directory integration, LDAP-dependent applications), OpenDJ provides a robust open-source alternative. For greenfield cloud-native projects, PostgreSQL-backed identity platforms (Keycloak, Authentik) may be simpler to operate.

### 5.8 Directory Services Comparison

| Directory | Type | Protocol | Replication | Primary Use Case | Status |
|-----------|------|----------|-------------|------------------|--------|
| OpenDJ | LDAP | LDAPv3 | Multi-master | OpenAM backing store | `[ACTIVE]` |
| Active Directory | LDAP+Kerberos | LDAPv3 | Multi-master (AD sites) | Windows enterprise | `[ACTIVE]` |
| Microsoft Entra ID | Cloud | REST (Graph API), SCIM | Global (Azure) | Cloud identity | `[ACTIVE]` |
| 389 DS | LDAP | LDAPv3 | Multi-master | FreeIPA / Red Hat | `[ACTIVE]` |
| OpenLDAP | LDAP | LDAPv3 | syncrepl | Linux/open-source | `[ACTIVE]` |
| PostgreSQL | Relational | SQL | Streaming replication | Keycloak, Authentik | `[ACTIVE]` |
| CockroachDB | Distributed SQL | SQL | Raft consensus | Zitadel | `[EMERGING]` |

---

## Roadmap 6: Identity Governance & Administration (IGA)

**Arc:** Manual provisioning (pre-2000) --> meta-directory sync (2000s) --> SPML (2003/2006) --> Sun IdM / ForgeRock OpenIDM (2005/2012) --> SCIM 2.0 provisioning (2015) --> event-driven sync (2018+) --> modern IGA platforms (SailPoint, Saviynt, Omada) --> AI-driven access reviews (2023+) --> identity orchestration (2024+).

### 6.1 Manual Provisioning and Help Desk Era (pre-2000)

| Year | Milestone | Status |
|------|-----------|--------|
| Pre-1990 | System administrators manually create accounts on each system | `[OBSOLETE]` (as practice) |
| 1990s | Help desk ticket-driven provisioning (user requests access, admin creates accounts) | `[LEGACY]` |
| 1990s | Batch scripts for account creation (shell scripts, VBScript) | `[LEGACY]` |

**What manual provisioning lacked:** Consistency (accounts created differently on each system), timeliness (days/weeks to provision), audit trail (paper forms or email threads), deprovisioning (orphaned accounts when employees leave), compliance (no way to prove who authorized access).

**The orphaned account problem:** Without automated deprovisioning, terminated employees retain access. Studies consistently show 30-50% of enterprise accounts are orphaned or over-provisioned. This became a primary driver for IGA solutions.

### 6.2 Meta-Directories and Virtual Directories (2000-2010)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1999 | Microsoft Metadirectory Services (MMS) | Microsoft | `[OBSOLETE]` |
| 2003 | Microsoft Identity Integration Server (MIIS) | Microsoft | `[OBSOLETE]` |
| 2007 | Microsoft Identity Lifecycle Manager (ILM) | Microsoft | `[OBSOLETE]` |
| 2010 | Forefront Identity Manager (FIM) / now Microsoft Identity Manager (MIM) | Microsoft | `[LEGACY]` |
| 2003 | Sun Java System Directory Server Enterprise Edition (virtual directory) | Sun | `[OBSOLETE]` |
| 2004 | Radiant Logic Virtual Directory Server | Radiant Logic | `[ACTIVE]` |

**Meta-directory approach:** Central hub connects to multiple identity stores (AD, LDAP, HR systems, databases). Synchronizes identity data bidirectionally. Metaverse (unified identity view) resolves conflicts via precedence rules.

**Virtual directory approach:** LDAP facade over heterogeneous sources. No data replication -- queries routed to source systems in real-time. Radiant Logic's RadiantOne remains the leading virtual directory product.

**Why meta-directories evolved:** Synchronization is inherently fragile (conflict resolution, latency, data corruption). Modern approach: authoritative source (HR system) pushes changes via SCIM/events; downstream systems consume. Less bidirectional sync, more unidirectional provisioning.

### 6.3 SPML -- Service Provisioning Markup Language (2003-2006)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2003 | SPML 1.0 | OASIS Standard | `[OBSOLETE]` |
| 2006 | SPML 2.0 | OASIS Standard | `[OBSOLETE]` |

**What SPML solved:** Standardized provisioning protocol. Create/Read/Update/Delete/Search operations for identity data. XML/SOAP-based. Target abstraction via Provisioning Service Targets (PSTs).

**Why SPML failed:** SOAP complexity, limited vendor adoption, competed with vendor-specific APIs. The industry shift to REST/JSON made SPML obsolete before it achieved critical mass. **SCIM (2011/2015) replaced SPML** with simpler REST/JSON approach. `[OBSOLETE]`

### 6.4 Sun Identity Manager and ForgeRock OpenIDM (2005-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2003 | Waveset Lighthouse (acquired by Sun 2003) | Waveset | Historical |
| 2005 | Sun Java System Identity Manager 7.0 | Sun Microsystems | `[OBSOLETE]` |
| 2008 | Sun Identity Manager 8.0 (final Sun release before Oracle acquisition) | Sun | `[OBSOLETE]` |
| 2010 | Oracle OpenSSO Enterprise / Oracle Identity Manager takes over | Oracle | `[ACTIVE]` (Oracle) |
| 2012 | ForgeRock OpenIDM 1.0 (open-source rewrite) | ForgeRock | Historical |
| 2016 | ForgeRock goes closed-source (Nov 2016) | ForgeRock | -- |
| 2017 | Open Identity Platform forks OpenIDM | OIP | `[ACTIVE]` |
| 2018 | Wren Security forks (Wren:IDM) | Wren Security | `[ACTIVE]` |

**OpenIDM architecture:** Unlike WAR-based OpenAM, OpenIDM is OSGi-based (Apache Felix framework). ~37 modules. Key components:

- **Sync engine (`openidm-core/`):** Reconciliation and live sync between systems. Mappings define source --> target attribute transformations.
- **Managed objects:** Identity resources stored in OpenIDM's repository (JDBC or OrientDB).
- **Connector framework (`openidm-provisioner-openicf/`):** OpenICF integration for LDAP, database, CSV, SSH, Groovy-scripted connectors.
- **Workflow engine (`openidm-workflow-activiti/`):** BPMN 2.0 workflows via Activiti. Approval workflows, escalation, notifications.
- **Routes:** `/managed/*` (managed identities), `/system/*` (connected systems), `/repo/*` (repository), `/sync/*` (synchronization), `/recon/*` (reconciliation), `/workflow/*` (BPMN workflows).

**Reconciliation patterns:**
1. **Full reconciliation:** Compare all entries in source and target. Detect additions, modifications, deletions. Resource-intensive but comprehensive.
2. **Live sync (change-driven):** Poll source system for changes since last sync token (LDAP changelog, database triggers, SCIM events). Near real-time. Lower resource usage.
3. **Scheduled sync:** Cron-triggered reconciliation at defined intervals.

**Joiner-Mover-Leaver lifecycle:**
- **Joiner:** New employee record in HR system triggers account creation in AD, email, SaaS applications. Automatic role assignment based on department/title.
- **Mover:** Employee transfers departments. Roles updated, old access revoked, new access provisioned. Group memberships adjusted.
- **Leaver:** Employee termination triggers account deactivation across all systems. Grace period for account recovery (rehire scenario). Full deletion after retention period.

### 6.5 OpenICF -- Connector Framework (2012-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2010 | ForgeRock develops OpenICF (based on Sun Identity Connector Framework) | ForgeRock | -- |
| 2012 | OpenICF 1.0 | ForgeRock | Historical |
| 2017 | OIP forks OpenICF | OIP | `[ACTIVE]` |

**What OpenICF solved:** Standardized SPI (Service Provider Interface) for identity connectors. Write once, connect to any system. API/SPI split: framework provides lifecycle management, connection pooling, search; connector implements system-specific operations.

**Architecture:** `OpenICF-java-framework/` -- 19 sub-modules. Protobuf RPC for remote connector communication. Key SPI operations: `Create`, `Read`, `Update`, `Delete`, `Search`, `Sync` (changelog), `Test` (connectivity), `Schema` (discover target schema).

**Built-in connectors:**
- **LDAP connector:** OpenDJ, Active Directory, 389 DS, OpenLDAP
- **Database connector:** JDBC to any SQL database
- **CSV connector:** Flat file import/export
- **SSH connector:** Remote system management via SSH commands
- **Kerberos connector:** MIT KDC administration
- **Groovy scripted connector:** Custom integrations via Groovy scripts

**Modern connector alternatives:** SCIM 2.0 is replacing proprietary connectors for SaaS provisioning. Native REST APIs (vendor-specific) for cloud services. OpenICF connectors remain necessary for legacy systems without SCIM support.

### 6.6 Modern IGA Platforms (2015-present)

| Year | Platform | Notes | Status |
|------|----------|-------|--------|
| 2005 | SailPoint IdentityIQ (on-prem) | Enterprise IGA leader | `[ACTIVE]` |
| 2013 | Saviynt (cloud-native IGA) | Born-in-cloud, CIEM integration | `[ACTIVE]` |
| 2017 | SailPoint IdentityNow (SaaS) | Cloud version of IdentityIQ | `[ACTIVE]` |
| 2018 | One Identity Manager | Quest Software / Dell | `[ACTIVE]` |
| 2019 | Omada Identity (cloud-native) | European IGA vendor | `[ACTIVE]` |
| 2020 | ConductorOne (modern IGA startup) | Access review automation | `[EMERGING]` |
| 2021 | Opal Security (least-privilege automation) | Developer-focused IGA | `[EMERGING]` |
| 2023 | Microsoft Entra ID Governance | Microsoft-native IGA | `[ACTIVE]` |
| 2024 | Veza (authorization metadata graph) | Identity security graph | `[EMERGING]` |

**IGA core capabilities:**
1. **Identity lifecycle management:** Joiner/Mover/Leaver automation
2. **Access request and approval:** Self-service access requests with workflow-based approvals
3. **Access certification (recertification):** Periodic review campaigns where managers certify subordinates' access is appropriate
4. **Separation of duties (SoD):** Prevent conflicting access (e.g., "create purchase order" and "approve purchase order" on same user)
5. **Role mining:** Analyze existing access patterns to discover implicit roles
6. **Provisioning/deprovisioning:** SCIM, connectors, or native API integration with target systems
7. **Compliance reporting:** Audit trails, SOX/HIPAA/SOC2 evidence generation

**Access certification campaigns:** Managers review all access their direct reports hold. Approve (retain) or revoke (remove) each entitlement. Campaign results audited for compliance. Typical cadence: quarterly for high-risk applications, annually for standard access.

**Separation of Duties (SoD):** Policy-based enforcement preventing toxic combinations. Examples:
- Cannot be both "accounts payable clerk" and "accounts payable approver"
- Cannot have both "production deploy" and "production admin" access
- Cannot hold "data entry" and "audit" roles simultaneously

**Role mining:** Analyze entitlement assignments across user population. Identify clusters of users with identical access patterns. Propose roles that represent these patterns. Reduces role explosion by discovering organic roles vs manually defining them.

### 6.7 AI-Driven Access Reviews (2023-present)

| Year | Milestone | Status |
|------|-----------|--------|
| 2023 | SailPoint AI-driven recommendations for access reviews | `[EMERGING]` |
| 2023 | Saviynt intelligent access recommendations | `[EMERGING]` |
| 2024 | Microsoft Entra ID Governance machine learning recommendations | `[EMERGING]` |
| 2024 | ConductorOne ML-based access right-sizing | `[EMERGING]` |

**What AI adds to IGA:**
- **Peer group analysis:** Compare user's access to peers with same role/department. Flag outliers (over-provisioned or under-provisioned).
- **Usage-based recommendations:** Identify unused entitlements (user has access but never uses it). Recommend revocation.
- **Risk scoring:** Score each access grant by sensitivity and usage. Prioritize high-risk, low-usage access for review.
- **Rubber-stamp detection:** Identify managers who approve everything without review. Flag for compliance.
- **Natural language justification:** Generate human-readable explanations for why access should be retained or revoked.

**Current maturity:** Early. Most implementations are rule-based with ML augmentation rather than fully autonomous. Trust in AI recommendations requires validation period. Regulatory acceptance (SOX auditors accepting AI-driven decisions) still evolving.

### 6.8 Identity Orchestration (2024-present)

| Year | Milestone | Status |
|------|-----------|--------|
| 2018 | ForgeRock authentication trees (DAG-based auth flows) | `[ACTIVE]` |
| 2021 | Auth0 Actions (programmable identity flows) | `[ACTIVE]` |
| 2022 | Strata Maverics (identity orchestration platform) | `[EMERGING]` |
| 2023 | Ping Identity DaVinci (journey-time orchestration) | `[ACTIVE]` |
| 2024 | Identity orchestration as distinct product category | Gartner | `[EMERGING]` |

**What orchestration solves:** Decouples identity logic from individual systems. Visual flow builders define authentication/authorization/provisioning journeys. Vendor-neutral abstraction layer enables: migrate between IdPs without application changes, compose multi-vendor identity flows, A/B test authentication experiences.

**OpenAM's authentication chains:** Original model -- linear sequence of authentication modules (LDAP --> TOTP --> push). Each module succeeds/fails, chain continues or terminates. Simple but limited (no branching, no conditional logic, no parallel execution).

**Authentication trees (ForgeRock 6.0+):** DAG (Directed Acyclic Graph) based. Nodes represent authentication steps; edges represent outcomes. Branching, merging, conditional logic. Visual designer. Not available in open-source OIP OpenAM (commercial ForgeRock feature).

**Modern orchestration:** Goes beyond authentication. Includes provisioning workflows, consent management, risk evaluation, step-up authorization. Journey-time orchestration: entire user journey (registration --> authentication --> authorization --> session management) defined as a single orchestrated flow.

### 6.9 IGA Evolution Summary

| Era | Approach | Provisioning | Access Review | Automation |
|-----|----------|-------------|---------------|------------|
| Pre-2000 | Manual | Help desk tickets | Annual spreadsheets | None |
| 2000-2010 | Meta-directory sync | Bidirectional sync | Manager email campaigns | Scheduled batch |
| 2010-2015 | Connector-based | SPML/proprietary connectors | Dedicated IGA platform | Event-driven |
| 2015-2020 | SCIM + cloud | SCIM 2.0 + native APIs | Cloud IGA (SailPoint IdentityNow) | Near real-time |
| 2020-2025 | AI-augmented | Event-driven + SCIM | AI recommendations + orchestration | Continuous |
| 2025+ | Autonomous | Identity orchestration platforms | Self-healing access (auto-revoke unused) | Fully automated |

**OpenIDM's position:** Provides Joiner-Mover-Leaver lifecycle, reconciliation, OpenICF connectors, and BPMN workflows. For organizations needing open-source IGA with LDAP/AD integration, OpenIDM fills the role. For enterprise-scale IGA with AI-driven reviews, commercial platforms (SailPoint, Saviynt, Microsoft Entra ID Governance) offer richer capabilities.

---

## Summary Table: Roadmaps 1-6

| # | Domain | Origin | Pre-2010 | 2024-2026 | 2027+ |
|---|--------|--------|----------|-----------|-------|
| 1 | Authentication | Passwords (1961) | LDAP bind + Kerberos + HOTP | Passkeys + WebAuthn + TOTP fallback | Continuous auth (CAEP), passwordless default |
| 2 | Federation | Kerberos cross-realm (1988) | SAML 2.0 + WS-Federation | OIDC dominant, SAML legacy | OIDC Federation, OpenID4VP, GNAP (maybe) |
| 3 | Authorization | Unix permissions (1971) | RBAC + XACML 3.0 | OAuth scopes + OPA/Cedar/ReBAC | Policy-as-code, Cedar formal verification, ReBAC mainstream |
| 4 | Token Formats | Kerberos tickets (1988) | SAML assertions + opaque cookies | JWT + DPoP + short-lived/refresh hybrid | SD-JWT VC, continuous token evaluation |
| 5 | Directory Services | X.500/DAP (1988) | LDAPv3 + Active Directory | LDAP + SCIM + cloud directories + PostgreSQL | Event-sourced identity, LDAP as compatibility layer |
| 6 | IGA | Manual provisioning | Meta-directory sync + SPML | SCIM + AI-driven reviews + cloud IGA | Autonomous IGA, self-healing access, identity orchestration |

---

## Roadmap 7: API Security & Gateway Evolution

### Timeline Overview

```
1996  HTTP Basic Auth (RFC 1945)
1997  HTTP Digest Auth (RFC 2069, updated RFC 2617)
1999  SSL/TLS 1.0 (RFC 2246)
2000s API keys as bearer credentials (ad hoc, no spec)
2005  Sun Access Manager Policy Agents (J2EE, Web Server agents)
2006  TLS 1.1 (RFC 4346)
2008  TLS 1.2 (RFC 5246)
2010  OpenIG 1.0 identity gateway (ForgeRock)
2012  OAuth 2.0 for APIs (RFC 6749, RFC 6750 bearer tokens)
2012  Token introspection concept (formalized RFC 7662, 2015)
2013  API management platforms emerge (Apigee, MuleSoft, 3scale)
2014  OWASP API Security awareness begins
2015  Kong Gateway 0.1 (open-source, Nginx + Lua)
2015  OAuth 2.0 Token Introspection (RFC 7662)
2013  OAuth 2.0 Token Revocation (RFC 7009)
2016  Envoy proxy open-sourced by Lyft
2016  Traefik 1.0 (Go-based edge router)
2017  Istio service mesh 0.1 (Google, IBM, Lyft)
2017  Linkerd 2.0 (Buoyant, Rust-based data plane)
2018  Apache APISIX 0.6 (Nginx + Lua, etcd-backed)
2018  TLS 1.3 (RFC 8446)
2019  OWASP API Security Top 10 (first edition)
2020  mTLS certificate-bound tokens (RFC 8705)
2021  Pushed Authorization Requests (RFC 9126)
2021  JWT-secured Authorization Requests (RFC 9101)
2023  Rich Authorization Requests (RFC 9396)
2023  Gateway API for Kubernetes (v1.0 GA, replacing Ingress)
2023  DPoP for APIs (RFC 9449)
2023  OWASP API Security Top 10 (2023 edition)
2023  API security platforms mature (Salt Security, Noname/Akamai, 42Crunch)
2024  Transaction Tokens (IETF draft-ietf-oauth-transaction-tokens)
2024  Istio ambient mesh GA (no sidecar, ztunnel-based)
2025  IETF OAuth 2.1 consolidation (draft progressing)
2026  API-first identity design as default pattern
```

### Milestone Details

#### HTTP Basic Auth (1996) `[LEGACY]`

- **Spec**: RFC 1945 (HTTP/1.0), formalized in RFC 2617 (1999), updated RFC 7617 (2015).
- **Mechanism**: Base64-encoded `username:password` in `Authorization` header. No encryption -- relies entirely on transport security (TLS).
- **Problem solved**: Standardized a way to pass credentials over HTTP, replacing ad hoc form-based approaches.
- **OpenAM implementation**: `HttpBasicAuthFilter` in OpenIG; OpenAM's `HttpBasic` authentication module validates Basic credentials against a configured identity store. Still used for legacy API authentication.
- **Why legacy**: Credentials transmitted with every request; vulnerable to interception without TLS; no session concept; no scope limitation; no token revocation. Still used for internal APIs, machine-to-machine calls behind firewalls, and as a fallback in legacy systems.

#### API Keys (2000s) `[ACTIVE]`

- **Spec**: No formal standard. Vendor-specific implementations using header-based (`X-API-Key`), query parameter, or bearer token patterns.
- **Problem solved**: Provided application-level identification for APIs without requiring user authentication. Enabled rate limiting, usage tracking, and billing per consumer.
- **OpenAM implementation**: Not directly. API keys are typically managed by API gateway platforms rather than IAM systems. OpenIG can validate API keys via `ScriptableFilter` with a key lookup.
- **Current status**: Remains extremely common for public APIs (Google Maps, Stripe, Twilio, GitHub). Not suitable as sole authentication for sensitive operations because keys are long-lived, shared secrets without scope or expiry semantics. Modern best practice: API keys for identification, OAuth tokens for authorization.

#### Sun Access Manager Policy Agents (2005) `[OBSOLETE]`

- **Origin**: Sun Access Manager 7.x introduced native C and Java agents embedded in web servers (Apache httpd, IIS) and application servers (WebLogic, WebSphere, Tomcat, JBoss).
- **Mechanism**: Agent intercepted requests in-process, validated the `iPlanetDirectoryPro` SSO cookie against the policy server (OpenAM/OpenSSO), and enforced allow/deny decisions based on URL policy. Agents injected identity headers (`AM_USER_DN`, etc.) into the request for the application.
- **Problem solved**: Externalized authentication and authorization from application code. Applications behind agents needed no identity logic.
- **Limitations**: Required installation on every web/app server; version coupling between agent and server; agent bugs could crash the hosting server; operationally expensive at scale. See [Chapter 10: OpenIG Analysis](10-openig-analysis.md), Section 6 for the generational analysis.
- **OpenAM implementation**: OpenAM continued to ship Java and Web agents through version 14.x. OIP OpenAM 16.x still includes the `openam-agents` module but recommends OpenIG as the replacement.
- **Why obsolete**: Replaced by centralized reverse proxy gateways (OpenIG, Kong), sidecar proxies (Envoy), and API gateways. Per-server agent deployment does not scale in containerized, ephemeral infrastructure.

#### OpenIG Identity Gateway (2010-present) `[LEGACY]`

- **Version**: Current OIP release 6.0.2. Commercial equivalent: PingGateway (post Ping-ForgeRock merger, 2023).
- **Architecture**: Java WAR deployed in a servlet container (Tomcat). Filter/handler pipeline with 50+ filters, 16+ handlers, JSON route configuration, Expression Language for dynamic behavior, Promise-based async execution. See [Chapter 10: OpenIG Analysis](10-openig-analysis.md) for full architectural analysis.
- **Problem solved**: Replaced per-server policy agents with a centralized reverse proxy. Introduced credential replay for legacy applications -- the ability to authenticate via modern protocols (OIDC, SAML) at the gateway and inject legacy credentials (HTTP Basic, form POST) into upstream requests.
- **Unique capability**: Credential replay (`PasswordReplayFilterHeaplet`) has no equivalent in any modern API gateway. This remains OpenIG's binding differentiator. See [Chapter 10](10-openig-analysis.md), Section 7.
- **Limitations**: Java overhead for a proxy role; no native OpenTelemetry, Prometheus, or distributed tracing; no Kubernetes operator; no gRPC support; no service discovery; small community (~200 GitHub stars). See [Chapter 10](10-openig-analysis.md), Section 4 for detailed weakness analysis.
- **Why legacy**: Modern API gateways (Kong, Traefik, APISIX) and service meshes (Istio/Envoy) offer superior performance, observability, Kubernetes integration, and community. OpenIG remains relevant only for credential replay use cases and existing OIP deployments.

#### OAuth 2.0 for API Security (2012) `[ACTIVE]`

- **Spec**: RFC 6749 (Authorization Framework), RFC 6750 (Bearer Token Usage).
- **Problem solved**: Separated authentication from authorization for APIs. Clients obtain scoped, time-limited access tokens from an authorization server; resource servers validate tokens without handling user credentials. Eliminated the need to share user passwords with third-party applications.
- **Key architectural shift**: API security moved from credential-based (every request carries username/password or API key) to token-based (client presents a bearer token; resource server validates it). This decoupled the IdP from the resource server.
- **OpenAM implementation**: OpenAM's `openam-oauth2` module provides a full OAuth 2.0 authorization server (all grant types: authorization code, implicit, client credentials, resource owner password, device authorization). OpenIG's `OAuth2ResourceServerFilter` validates bearer tokens via introspection or JWT verification.
- **Extensions driving modern API security**:
  - Token Introspection (RFC 7662, 2015) `[ACTIVE]`: Resource servers query the authorization server to validate opaque tokens.
  - Token Revocation (RFC 7009, 2013) `[ACTIVE]`: Standardized endpoint for revoking access and refresh tokens.
  - JWT Access Tokens (RFC 9068, 2021) `[ACTIVE]`: Standardized JWT format for access tokens, enabling stateless validation at the gateway without introspection round-trips.
  - Pushed Authorization Requests (RFC 9126, 2021) `[ACTIVE]`: Authorization request parameters sent directly to the AS, keeping sensitive data off the browser URL.
  - Rich Authorization Requests (RFC 9396, 2023) `[ACTIVE]`: Fine-grained `authorization_details` parameter replacing coarse scopes for complex authorization (financial APIs, healthcare).

#### Token Introspection vs JWT Validation at the Edge (2015-present) `[ACTIVE]`

- **Two models for API token validation at gateways**:
  1. **Introspection (RFC 7662)**: Gateway sends the token to the authorization server's introspection endpoint; AS returns active/inactive status plus token metadata. Advantage: real-time revocation awareness. Disadvantage: network round-trip per request; AS becomes a throughput bottleneck.
  2. **JWT validation**: Gateway verifies the JWT signature locally using cached public keys (JWKS), checks expiry, issuer, audience, and scopes. Advantage: no network hop, sub-millisecond validation. Disadvantage: tokens valid until expiry even if revoked; requires short token lifetimes or revocation lists.
- **Hybrid pattern** (dominant in 2024-2026): Short-lived JWT access tokens (5-15 minute lifetime) validated at the gateway edge + refresh token rotation at the authorization server. Provides the performance of local JWT validation with bounded revocation window.
- **OpenAM/OpenIG**: OpenIG's `OAuth2ResourceServerFilter` supports both introspection and JWT validation modes, configurable per route.

#### Kong Gateway (2015-present) `[ACTIVE]`

- **Version**: 3.x (2024-2025). ~40,000 GitHub stars, 300+ contributors.
- **Architecture**: Nginx core (C) + Lua plugin runtime + Go control plane (Enterprise). Backed by PostgreSQL or Cassandra (DB mode) or declarative YAML (DB-less mode).
- **Problem solved**: General-purpose API gateway with identity as one plugin among many (rate limiting, request transformation, load balancing, circuit breaking, caching, observability). Developer portal, API lifecycle management, and analytics distinguish it from identity-only gateways.
- **Identity plugins**: OIDC (`openid-connect`), JWT validation (`jwt`), basic-auth (`basic-auth`), key-auth (`key-auth`), LDAP (`ldap-auth`), HMAC (`hmac-auth`), mTLS (`mtls-auth`).
- **Versus OpenIG**: Kong surpasses OpenIG in performance (Nginx event loop vs JVM), observability (Prometheus, OpenTelemetry, Datadog, Zipkin, StatsD), Kubernetes integration (Kong Ingress Controller, Helm, Operator), and community. Kong lacks credential replay and native SAML federation. See [Chapter 10: OpenIG Analysis](10-openig-analysis.md), Section 5.1.
- **Kong Mesh** (Kuma/Envoy-based): Extends Kong into service mesh territory with mTLS, traffic policies, and multi-zone deployment.

#### Envoy Proxy and Service Mesh (2016-present) `[ACTIVE]`

- **Version**: Envoy 1.31+ (2025). ~25,000 GitHub stars, 1,000+ contributors. CNCF Graduated (2018).
- **Architecture**: C++ L4/L7 proxy. Event-driven, non-blocking. xDS API for dynamic configuration. Designed as a sidecar proxy for service mesh but also deployable as edge proxy.
- **Identity model**: Workload identity via mTLS with SPIFFE SVIDs (X.509 certificates containing SPIFFE IDs in the SAN field). Every service gets a cryptographic identity automatically rotated by the control plane (Istio istiod, SPIRE).
- **Authorization**: `ext_authz` filter delegates authorization decisions to external gRPC or HTTP services (OPA, Ory Oathkeeper, custom). JWT filter validates JWT tokens locally. Rate limit service for distributed rate limiting.
- **Protocol support**: HTTP/1.1, HTTP/2, HTTP/3 (QUIC), gRPC, TCP, UDP, WebSocket, Thrift.
- **Versus OpenIG**: Different architectural layer. Envoy handles east-west (service-to-service) communication with mTLS and workload identity. OpenIG handles north-south (user-to-application) authentication mediation. In modern architectures, both concerns coexist. See [Chapter 10](10-openig-analysis.md), Section 5.2.

**Istio Service Mesh** (2017-present) `[ACTIVE]`:
- **Version**: 1.23+ (2025). ~36,000 GitHub stars. CNCF Graduated (2023).
- Control plane (istiod) manages Envoy sidecar proxies across the mesh.
- `AuthorizationPolicy` CRDs enforce fine-grained, identity-aware access policies at the mesh layer.
- Ambient mesh mode (GA 2024): ztunnel (zero-trust tunnel) replaces per-pod sidecar with per-node L4 proxy + optional L7 waypoint proxies. Reduces resource overhead by ~60%.
- OIDC Shared Signals integration for continuous access evaluation is an emerging use case.

**Linkerd** (2017-present) `[ACTIVE]`:
- **Version**: 2.16+ (2025). Rust-based micro-proxy (linkerd2-proxy). ~10,600 GitHub stars. CNCF Graduated (2021).
- Simpler than Istio. Automatic mTLS, latency-aware load balancing, observability. No `ext_authz` equivalent -- authorization delegated to OPA sidecar or application layer.
- In February 2024, Buoyant stopped publishing free stable release builds of Linkerd (source remains Apache 2.0; only edge releases freely available), causing community friction.

#### OWASP API Security Top 10 (2019, 2023) `[ACTIVE]`

- **2019 edition**: First systematic categorization of API-specific vulnerabilities. Highlighted that APIs face different threats than web applications.
- **2023 edition (current)**: Updated risk list reflecting evolving API attack patterns:

| Rank | Risk | Identity Relevance |
|------|------|--------------------|
| API1 | Broken Object Level Authorization | Failure to verify requesting user's access to specific objects |
| API2 | Broken Authentication | Weak auth mechanisms, credential stuffing, missing rate limits |
| API3 | Broken Object Property Level Authorization | Mass assignment, excessive data exposure through object properties |
| API4 | Unrestricted Resource Consumption | Missing rate limiting allows resource exhaustion |
| API5 | Broken Function Level Authorization | Missing checks on administrative vs user functions |
| API6 | Unrestricted Access to Sensitive Business Flows | Automated abuse of business logic (ticket scalping, etc.) |
| API7 | Server Side Request Forgery (SSRF) | API fetches user-supplied URLs without validation |
| API8 | Security Misconfiguration | Missing security headers, verbose errors, default credentials |
| API9 | Improper Inventory Management | Undocumented, shadow, or deprecated API endpoints |
| API10 | Unsafe Consumption of APIs | Blindly trusting third-party API responses |

- **Identity intersection**: API1, API2, API3, and API5 are directly identity/authorization failures. Modern API gateways address API2 (auth validation) and API4 (rate limiting) but API1 and API5 require application-layer authorization (OPA, Cedar, or application code).

#### API Security Platforms (2020-present) `[EMERGING]`

- **Category emergence**: Dedicated API security platforms that go beyond gateway-level auth to provide API discovery, vulnerability assessment, behavioral analysis, and runtime protection.
- **Key vendors**:
  - **Salt Security** (founded 2018): API discovery via traffic analysis; behavioral threat detection; pre-production API testing. Patented API context engine builds a baseline of normal API behavior and detects anomalies.
  - **Noname Security** (acquired by Akamai, 2024): API discovery, posture management, runtime protection, active testing. Integration with API gateways (Kong, Apigee, AWS).
  - **42Crunch** (founded 2017): API security audit based on OpenAPI specs; conformance scanning; API firewall (micro-firewall deployed alongside APIs). Shift-left approach -- security in the CI/CD pipeline.
  - **Traceable AI**: API security with full-stack tracing. Maps API attack surfaces. Uses AI for threat detection.
  - **Wallarm** (founded 2016): API security and WAAP (Web Application and API Protection). Combines WAF with API-specific protections.
- **Relation to identity**: These platforms complement IAM/gateway solutions. They detect identity-related attacks at the API layer (credential stuffing, token abuse, authorization bypass) that standard gateways miss because they lack behavioral context.

#### DPoP for APIs (2023) `[EMERGING]`

- **Spec**: RFC 9449, Demonstration of Proof-of-Possession at the Application Layer.
- **Problem solved**: Bearer tokens (RFC 6750) can be stolen and replayed. DPoP binds access tokens to a client-held asymmetric key pair. Each API request includes a DPoP proof JWT proving possession of the private key. A stolen token is useless without the private key.
- **Mechanism**: Client generates an ephemeral key pair; includes the public key in the DPoP proof JWT; authorization server binds the access token to that key. Resource server validates both the access token and the DPoP proof.
- **Versus mTLS-bound tokens (RFC 8705)**: DPoP works without PKI infrastructure -- the client generates its own key pair. mTLS requires certificate provisioning. DPoP is more practical for browser and mobile clients; mTLS is stronger for server-to-server.
- **OpenAM implementation**: OIP OpenAM 16.x does not natively support DPoP. Keycloak added DPoP support in v22. Auth0 and Okta support DPoP (2024).

#### Transaction Tokens (TxnTokens) `[EMERGING]`

- **Spec**: IETF draft-ietf-oauth-transaction-tokens (active draft, 2024-2025).
- **Problem solved**: In microservices architectures, a single user request fans out into multiple inter-service calls. Each service needs to know the original user identity and transaction context. Passing the original access token to every downstream service violates least privilege (downstream services get the full access token). Token exchange (RFC 8693) creates new tokens per hop but adds latency.
- **Mechanism**: Transaction Tokens (TxnTokens) are lightweight, short-lived tokens that carry the user identity context and transaction metadata through a call chain. They are issued by a Transaction Token Service (TxnTS) at the entry point and validated by downstream services. They contain only the claims needed for the transaction, not the full authorization context.
- **OpenAM implementation**: Not implemented. OpenIG's `TokenTransformationFilter` provides a conceptual precursor via OpenAM's STS (Security Token Service) for protocol bridging (e.g., OIDC-to-SAML token exchange).

#### Kubernetes Gateway API (2022-present) `[ACTIVE]`

- **Spec**: Kubernetes SIG-Network, v1.0 GA (October 2023). Replaces the Ingress API (which was limited to basic HTTP routing).
- **Problem solved**: The Kubernetes Ingress resource was too simple for modern gateway requirements -- no support for header-based routing, traffic splitting, TCP/UDP, or cross-namespace references. Gateway API provides a role-oriented, expressive, portable API for managing gateway infrastructure.
- **Key resources**: `GatewayClass`, `Gateway`, `HTTPRoute`, `GRPCRoute`, `TCPRoute`, `TLSRoute`, `ReferenceGrant`.
- **Identity integration**: `HTTPRoute` can reference backend policies that delegate authentication to external services. `BackendTLSPolicy` enables mTLS to backends. Gateway implementations (Kong, Istio, Envoy Gateway, Traefik, APISIX) all support Gateway API.
- **OpenIG relevance**: OpenIG predates the Kubernetes Gateway API and does not implement it. Organizations running OpenIG in Kubernetes must use the older Ingress or manual Service/Deployment configuration.

#### OAuth 2.1 (Draft, progressing) `[EMERGING]`

- **Spec**: IETF draft-ietf-oauth-v2-1. Consolidates OAuth 2.0 (RFC 6749) with established best practices and security extensions.
- **Key changes from OAuth 2.0**:
  - PKCE (RFC 7636) mandatory for all authorization code flows (not just public clients).
  - Implicit grant removed (use authorization code + PKCE instead).
  - Resource owner password credentials grant removed.
  - Bearer token usage (RFC 6750) integrated.
  - Refresh token rotation recommended.
  - Exact redirect URI matching required.
  - Sender-constrained tokens (DPoP, mTLS) recommended.
- **Status**: Draft nearing completion. Most modern IdPs already implement OAuth 2.1 best practices even before formal ratification.
- **OpenAM implementation**: OpenAM 16.x supports PKCE and all grants. Removing deprecated grants would be a configuration change rather than code change.

### Gateway Generation Summary

| Generation | Period | Architecture | Identity Model | OpenIG Position |
|------------|--------|-------------|----------------|-----------------|
| 1. Policy Agents | 2000-2010 | In-process agent on each server | Cookie-based SSO | Predecessor |
| 2. Identity Gateways | 2010-2018 | Centralized reverse proxy | Session tokens + credential replay | Native |
| 3. API Gateways | 2016-2022 | Centralized/distributed gateway | OAuth tokens + JWT validation | Eclipsed |
| 4. Service Mesh Sidecars | 2018-present | Per-service sidecar proxy | mTLS + workload identity (SPIFFE) | Different layer |
| 5. Ambient Mesh | 2024-present | Per-node L4 tunnel + L7 waypoint | mTLS without sidecar overhead | Different layer |

### API-First Identity Design (2024-2026) `[EMERGING]`

The convergence of API gateways, service mesh, and identity standards is driving a pattern called "API-first identity design":

1. **Identity as infrastructure**: Authentication and authorization are gateway/mesh concerns, not application concerns. Applications never see raw credentials.
2. **Token-based identity propagation**: User identity flows through the call chain via tokens (JWT access tokens, transaction tokens), not session cookies.
3. **Fine-grained authorization at the edge and depth**: Coarse authorization (valid token, correct scope) at the gateway; fine-grained authorization (object-level access, business rules) at the application layer via policy engines (OPA, Cedar).
4. **mTLS for transport, tokens for identity**: Service mesh handles transport-level authentication (mTLS); tokens handle user-level identity and authorization context.
5. **Standards-based, vendor-neutral**: OIDC for authentication, OAuth 2.0/2.1 for delegation, SPIFFE for workload identity, DPoP for token binding -- all interoperable.

---

## Roadmap 8: Privileged Access Management (PAM)

### Timeline Overview

```
1971  Unix su (substitute user) command
1980  sudo (superuser do) introduced by Bob Coggeshall and Cliff Spencer
1985  sudo 1.0 formal release
1995  SSH protocol (Tatu Ylonen, SSH-1)
1996  SSH-2 (IETF standardization begins, RFC 4251-4254, finalized 2006)
1999  CyberArk founded (Israel)
2001  Lieberman Software Random Password Manager (early credential vaulting)
2003  CyberArk Privileged Identity Manager v1
2005  CyberArk Digital Vault + Privileged Session Manager (PSM)
2007  Thycotic Secret Server v1 (later Delinea)
2008  Bomgar (later BeyondTrust) privileged remote access
2010  Session recording as standard PAM feature
2011  AWS IAM launched (cloud privilege management begins)
2010  SSH certificate-based auth (OpenSSH 5.4, March 2010, certificates vs static keys)
2013  CyberArk IPO (NASDAQ: CYBR)
2014  Centrify Server Suite (server privilege management)
2015  HashiCorp Vault 0.1 (dynamic secrets, secrets-as-a-service)
2016  CyberArk Conjur (secrets management for DevOps)
2017  Vault dynamic database credentials GA
2018  Azure Privileged Identity Management (PIM) GA
2018  AWS Systems Manager Session Manager (cloud-native session brokering)
2019  AWS IAM Access Analyzer (identify overly permissive policies)
2020  Zero Standing Privileges concept formalized (Gartner)
2021  Thycotic + Centrify merger -> Delinea
2018  Bomgar acquires BeyondTrust, rebrands as BeyondTrust
2022  CyberArk Identity Security Platform (unified PAM + IAM)
2023  HashiCorp Vault license change to BSL 1.1; OpenBao fork (Linux Foundation)
2024  IBM acquires HashiCorp (~$6.4B)
2024  CyberArk acquires Venafi (machine identity management)
2024  CyberArk Secure Cloud Access (JIT cloud console access)
2024  Delinea Platform (unified SaaS PAM)
2025  Ephemeral access as default pattern (short-lived, just-in-time credentials)
2026  PAM-IAM convergence accelerates (single identity security platforms)
```

### Milestone Details

#### su/sudo (1971/1980) `[ACTIVE]`

- **su (substitute user)**: Unix command since V1 (1971). Allows switching to another user identity (typically root) by providing the target user's password.
- **sudo (superuser do)**: Introduced ~1980, formal release 1985. Allows executing a single command as another user based on policy (`/etc/sudoers`). Key innovation: users authenticate with their own password, not root's password, enabling auditing of who performed privileged operations.
- **Current status**: Still the foundation of Unix/Linux privilege escalation. `sudoers` configuration is the most widely deployed privilege policy engine on the planet. Modern PAM solutions layer on top of sudo rather than replacing it -- e.g., Delinea Server PAM and BeyondTrust EPM manage sudo policies centrally.
- **Security evolution**: `sudo` CVEs (e.g., CVE-2019-14287, CVE-2021-3156 "Baron Samedit") demonstrate the ongoing attack surface. Modern alternatives like `doas` (OpenBSD) provide simpler, auditable privilege escalation.
- **OpenAM relevance**: Not directly. OpenAM handles application-level authentication, not OS-level privilege escalation. However, OpenDJ stores the identity data (user attributes, group memberships) that may feed into sudo policy decisions via LDAP integration (e.g., `sudoRole` objectclass in LDAP-backed sudoers).

#### Credential Vaulting (2003-2010) `[ACTIVE]`

- **Concept**: Centralized, encrypted storage for privileged credentials (root passwords, database admin credentials, application service accounts, SSH keys). Users check out credentials from the vault, use them, and the vault automatically rotates the credential after use.
- **CyberArk Digital Vault** (2003-2005): Industry-defining product. AES-256 encrypted vault running on a hardened Windows server. FIPS 140-2 validated. Stores, rotates, and audits access to privileged credentials. Central Policy Manager (CPM) automates password rotation on target systems.
- **Problem solved**: Eliminated shared passwords written on Post-it notes, stored in spreadsheets, or embedded in scripts. Provided audit trail of who accessed which privileged credential and when.
- **OpenAM relevance**: OpenAM does not provide credential vaulting. However, OpenIG's credential replay feature (Section 7 of [Chapter 10](10-openig-analysis.md)) stores credentials for legacy backend authentication -- conceptually similar to a narrow-scope vault. OpenIG retrieves credentials from configured stores (database via `SqlAttributesFilter`, external vault via `ScriptableFilter`) and injects them into upstream requests.

#### Session Recording and Monitoring (2010-present) `[ACTIVE]`

- **Concept**: Record all activity during a privileged session (SSH, RDP, database console, cloud console) for forensic review, compliance evidence, and real-time monitoring.
- **CyberArk PSM (Privileged Session Manager)**: Proxies privileged sessions through a jump server. Records video-like session captures of RDP/SSH sessions. Keystroke logging, command capture, file transfer monitoring. Live session monitoring with ability to terminate suspicious sessions.
- **BeyondTrust Privileged Remote Access**: Session recording for vendor/remote privileged access. VPN-less access with full audit trail.
- **Delinea Advanced Session Recording**: RDP, SSH, PuTTY session recording. Real-time monitoring dashboard.
- **HashiCorp Boundary** (2020-present): Session brokering without credential exposure. Boundary Enterprise adds session recording to object storage (S3, etc.). Sessions are brokered -- the user connects through Boundary, which injects credentials into the target session. The user never sees the actual credential.
- **Cloud equivalents**: AWS Systems Manager Session Manager records shell sessions to S3/CloudWatch. Azure Bastion provides session recording for RDP/SSH to Azure VMs.
- **OpenAM relevance**: OpenAM's audit logging captures authentication events but not session activity. Session recording is a PAM-specific capability outside OpenAM's scope. OpenIG's `CaptureFilter` captures HTTP request/response details for debugging but is not equivalent to privileged session recording.

#### Dynamic Secrets and Secrets Management (2015-present) `[ACTIVE]`

- **HashiCorp Vault** (2015, v0.1):
  - **Core innovation**: Dynamic secrets. Instead of storing static credentials, Vault generates short-lived credentials on demand for databases, cloud providers, PKI, and SSH. Credentials are automatically revoked when the lease expires.
  - **Secret engines**: KV (static secrets), database (dynamic database credentials for PostgreSQL, MySQL, Oracle, MSSQL, MongoDB, Cassandra, etc.), PKI (private CA, certificate issuance), SSH (signed certificates), transit (encryption as a service), TOTP, cloud providers (AWS STS, Azure, GCP).
  - **Authentication methods**: Token, LDAP, OIDC/JWT, Kubernetes ServiceAccount, AppRole, AWS IAM, Azure MSI, GCP IAM, TLS certificates, GitHub.
  - **Architecture**: Client-server. Stateless server with encrypted storage backend (Raft integrated storage, Consul, S3, DynamoDB). Seal/unseal via Shamir's Secret Sharing or auto-unseal (AWS KMS, Azure Key Vault, GCP Cloud KMS, HSM).
  - **Vault Agent/Proxy**: Sidecar for automatic token renewal, secret caching, and template rendering. Eliminates the need for applications to interact with Vault API directly.
  - **Vault Secrets Operator (VSO)**: Kubernetes operator that syncs Vault secrets to Kubernetes Secrets objects.
  - **License change**: MPL 2.0 -> BSL 1.1 (August 2023). Restricts competitive SaaS usage. Led to OpenBao fork (Linux Foundation, MPL 2.0).
  - **IBM acquisition**: IBM acquired HashiCorp in 2024 (~$6.4B). Long-term implications for Vault's direction unclear.
  - **Version**: 1.18.x (2025). ~31,500 GitHub stars.

- **OpenBao** (2023-present) `[EMERGING]`:
  - Linux Foundation project. Forked from Vault at v1.14 (before BSL change).
  - MPL 2.0 license. Community-driven. ~3,500 GitHub stars.
  - Compatible with Vault's API and plugin ecosystem. Growing as an alternative for organizations avoiding BSL-licensed software.

- **AWS Secrets Manager** `[ACTIVE]`: Managed secrets storage with automatic rotation for RDS, Redshift, DocumentDB credentials. Lambda-based custom rotation. Cross-region replication.
- **Azure Key Vault** `[ACTIVE]`: Managed secrets, keys, and certificates. HSM-backed keys (FIPS 140-2 Level 2/3). Integration with Azure services.
- **GCP Secret Manager** `[ACTIVE]`: Versioned secrets with IAM-based access control. Automatic replication across regions.

- **OpenAM/OIP relevance**: OpenAM stores its own configuration secrets (encryption keys, keystore passwords) but is not a secrets management platform. OpenDJ can serve as an LDAP-backed credential store for service accounts but lacks dynamic credential generation. In a production OIP deployment, Vault or a cloud secrets manager typically handles service account credentials, database passwords, and TLS certificates that the OIP components consume.

#### Just-in-Time (JIT) Access (2018-present) `[ACTIVE]`

- **Concept**: Privileged access granted only when needed, for a limited duration, with explicit approval. Eliminates "standing privileges" -- permanently assigned admin rights that are exploited in breaches.
- **Azure PIM (Privileged Identity Management)** (2018 GA): Time-bound role activation for Azure AD roles and Azure resource roles. Users "activate" admin roles for a configurable duration (1-24 hours). Requires justification, optional MFA, and optional approval workflow. Activation logged for audit.
- **CyberArk JIT Access**: Credential checkout with time-limited access. Integrated with ticketing systems (ServiceNow, Slack, Teams) for approval workflows. Automatic credential rotation after checkout expires.
- **AWS STS (Security Token Service)**: Issues temporary security credentials for assumed IAM roles. Credentials expire after configurable duration (15 minutes to 36 hours). Foundation for JIT patterns in AWS.
- **HashiCorp Boundary**: Session brokering with injected credentials. No standing credentials -- Boundary generates or retrieves credentials per session. Sessions have configurable time limits.
- **OpenAM relevance**: OpenAM's delegation model allows time-limited administrative privileges via custom authentication modules and session properties. OpenAM's `SessionService` can enforce session timeouts, and custom `PostAuthenticationProcessPlugin` implementations can inject time-bound role claims. However, this is a DIY approximation of JIT, not a native capability.

#### Zero Standing Privileges (ZSP) (2020-present) `[EMERGING]`

- **Concept**: No user or service account has permanent privileged access. All access is just-in-time, just-enough, and automatically revoked. Standing admin accounts (domain admins, root, DBA) are eliminated entirely.
- **Gartner guidance**: Gartner introduced ZSP as a PAM best practice in 2020-2021. By 2023, it became a core recommendation in the Gartner Hype Cycle for Identity and Access Management.
- **Implementation patterns**:
  1. **Ephemeral accounts**: Create a temporary admin account, grant it the required permissions, execute the task, delete the account. CyberArk and Delinea support this pattern.
  2. **Dynamic credential injection**: Vault/Boundary generates session-specific credentials. No standing credentials exist in any configuration file or secret store.
  3. **Approval-gated elevation**: Azure PIM, CyberArk JIT -- user requests elevation, approver grants it, system enforces time limit and revokes automatically.
  4. **Break-glass procedures**: Emergency access via sealed credentials that trigger alerts when accessed. Documented process for scenarios where JIT workflows are unavailable (system outage, incident response).
- **Challenges**: Legacy systems that require static service accounts; applications with hardcoded credentials; operational complexity of managing ephemeral credentials at scale; break-glass procedures for emergencies.
- **OpenAM relevance**: OpenAM's administrative model uses persistent admin accounts (`amadmin`). ZSP would require wrapping OpenAM administration behind a PAM system (CyberArk, Boundary) that brokers access to the `amadmin` credential.

#### Cloud PAM and CIEM Overlap (2019-present) `[ACTIVE]`

- **Cloud Privileged Access**: Cloud console access (AWS, Azure, GCP) is inherently privileged -- a single misconfiguration can expose entire environments. Cloud PAM addresses:
  - JIT access to cloud consoles (CyberArk Secure Cloud Access, 2024)
  - Cloud entitlement management (identifying and remediating over-provisioned IAM policies)
  - Multi-cloud privilege governance
- **AWS IAM Access Analyzer** (2019) `[ACTIVE]`: Analyzes resource policies and IAM policies to identify unintended public or cross-account access. Policy validation against best practices. Custom policy checks.
- **Permission boundaries** (AWS, 2018) `[ACTIVE]`: IAM policy mechanism that sets the maximum permissions an identity can have, regardless of the identity policy attached. Enables delegated administration -- teams can create their own roles but cannot exceed the boundary.
- **CIEM (Cloud Infrastructure Entitlement Management)** overlap: CIEM tools (covered in a separate roadmap) analyze cloud IAM permissions for over-provisioning. PAM tools broker access to those permissions. The two categories converge:
  - CyberArk Secure Cloud Access = PAM for cloud consoles
  - Saviynt CPAM = converged IGA + cloud PAM
  - Wiz = CSPM + CIEM (identifies over-permissive cloud identities)
  - Microsoft Entra Permissions Management (formerly CloudKnox) = CIEM

#### PAM-IAM Convergence (2022-present) `[EMERGING]`

- **Trend**: Traditional PAM (CyberArk, Delinea, BeyondTrust) and IAM (Okta, Ping, Keycloak, OpenAM) operated as separate domains with separate tools, teams, and budgets. The convergence is driven by:
  1. **Common identity fabric**: Both PAM and IAM authenticate against the same directories (AD, LDAP, Entra ID). Managing separate identity silos creates policy gaps.
  2. **Least privilege as a continuum**: Regular user access (IAM) and privileged access (PAM) are points on a spectrum, not separate categories. Context-aware policies should escalate MFA requirements and approval gates based on the sensitivity of the requested access.
  3. **Vendor consolidation**: CyberArk acquired Idaptive (SSO/MFA) in 2020 to add IAM. Okta added Privileged Access (OPA) in 2023. Saviynt converges IGA + CPAM.
- **CyberArk Identity Security Platform**: Unifies Privilege Cloud (PAM), CyberArk Identity (SSO/MFA, formerly Idaptive), Endpoint Privilege Manager, Conjur (secrets), and Venafi (machine identity). Single platform for human privileged access, workforce SSO, endpoint privilege, machine secrets, and machine identity.
- **Okta Privileged Access (OPA)**: Cloud-native PAM integrated with Okta's IAM platform. Server access (SSH, RDP) via Okta identity. JIT privilege elevation. Still maturing compared to CyberArk.
- **OpenAM relevance**: OpenAM is an IAM platform without PAM capabilities. In a converged model, OpenAM would provide the authentication layer, and a PAM tool (CyberArk, Vault, Boundary) would broker privileged access. OpenAM's `PolicyService` could theoretically enforce policies that require step-up authentication or approval for privileged operations, but it lacks session recording, credential vaulting, or JIT access workflows.

### PAM Architecture Patterns

| Pattern | Mechanism | Credential Exposure | Audit | Use Case |
|---------|-----------|-------------------|-------|----------|
| Shared account checkout | User checks out credential from vault | User sees credential | Vault log | Legacy systems |
| Session brokering (PSM) | PAM proxy injects credential; user never sees it | No exposure | Full session recording | Regulated environments |
| Dynamic credential injection (Vault/Boundary) | Short-lived credential generated per session | Ephemeral, auto-revoked | Vault audit log | Cloud-native / DevOps |
| JIT role activation (Azure PIM) | User activates role for limited time | No credential -- role assignment | PIM audit log | Azure environments |
| Ephemeral account | Temporary account created, used, destroyed | Ephemeral | Account lifecycle log | Zero standing privileges |

---

## Roadmap 9: Deployment Architecture for Identity Systems

### Timeline Overview

```
1999  J2EE application servers (WebLogic, WebSphere) host IAM apps
2003  Sun Java System Identity Server deployed as EAR/WAR
2005  Sun Access Manager 7.x on Sun Application Server / WebLogic
2006  OpenSSO on GlassFish
2010  ForgeRock OpenAM 9 as standalone WAR (Tomcat)
2012  OpenAM CTS (Core Token Service) for distributed session persistence
2013  Docker open-sourced (container runtime; 1.0 in June 2014)
2015  Kubernetes 1.0 (container orchestration, open-sourced by Google 2014)
2015  OpenAM in Docker containers (community-contributed Dockerfiles)
2015  Keycloak on WildFly (monolithic Java EE)
2016  Helm 1.0 (Kubernetes package manager)
2017  Istio 0.1 (service mesh)
2017  Ory Hydra 0.1 (Go microservice, single-purpose OAuth2 server)
2018  Kubernetes Operators concept (CoreOS)
2018  Keycloak Operator for Kubernetes
2018  Ory stack decomposition (Hydra, Kratos, Keto, Oathkeeper as separate services)
2019  ForgeRock Identity Cloud (managed SaaS, based on AM/IDM/DS)
2020  Keycloak migration to Quarkus begins (v12, alternative distribution)
2021  Zitadel 1.0 (single Go binary, event-sourced, CockroachDB)
2021  Auth0 Private Cloud (dedicated SaaS infrastructure)
2021  Supabase Auth (serverless authentication, PostgreSQL-backed)
2022  Cloudflare Access (edge-deployed identity proxy)
2022  Keycloak Quarkus distribution becomes default (v19)
2023  ArgoCD and GitOps for identity infrastructure
2023  Keycloak v25: WildFly distribution removed entirely
2024  Istio ambient mesh GA (sidecar-less service mesh)
2024  Keycloak Operator v2 (immutable, optimized deployments)
2025  WebAssembly (Wasm) for portable identity components
2026  Multi-cloud identity mesh as standard architecture
```

### Milestone Details

#### Monolithic WAR Deployment (2003-2016) `[LEGACY]`

- **The canonical model**: OpenAM (and its predecessors Sun Access Manager, OpenSSO) deploys as a single WAR file into a Java servlet container (Tomcat, Jetty) or application server (WebLogic, WebSphere, GlassFish, JBoss). The WAR contains the authentication engine (34+ modules), OAuth 2.0/OIDC provider, SAML 2.0 IdP/SP, XACML policy engine, session management, admin console (JSP/React), and REST endpoints.
- **Configuration**: Server configuration stored in a bootstrap file (`boot.properties`) pointing to an embedded or external OpenDJ configuration store. Site configuration stored in the OpenDJ-backed configuration tree.
- **State management**: Server-side sessions stored in memory (single-instance) or in a shared store (OpenAM's CTS backed by OpenDJ or Cassandra). Session failover via CTS replication.
- **Scaling**: Horizontal scaling via multiple WAR instances behind a load balancer. CTS provides session persistence across instances. Cookie-based session stickiness optional but not required with CTS.
- **Strengths**: Single deployment artifact; well-understood Java EE operational model; unified configuration; extensive documentation for J2EE administrators.
- **Weaknesses**: Cannot scale individual components independently (OAuth server, SAML engine, session store all scale together); large memory footprint (1-4 GB JVM heap typical); 30-120 second startup time; upgrading one capability requires redeploying the entire application; monolith fragility (one failing component can take down the whole server).
- **Current status**: OIP OpenAM 16.x still deploys as a WAR. This is the primary deployment model for the OIP stack.

#### Clustered J2EE with Shared Session Store (2005-2016) `[LEGACY]`

- **OpenAM CTS (Core Token Service)**: Introduced in OpenAM 12.x (2014). Centralizes session, OAuth token, and SAML assertion storage in an OpenDJ-backed token store. Enables horizontal scaling without sticky sessions.
- **CTS architecture**: OpenDJ operates as a high-performance key-value store for tokens. Each token type (session, OAuth2 access token, SAML assertion) is stored as an LDAP entry with configurable TTL. Multi-master OpenDJ replication provides CTS high availability across data centers.
- **Cassandra as CTS backend**: OpenAM's `openam-cassandra` module provides an alternative CTS implementation using Apache Cassandra. Suited for deployments exceeding OpenDJ's single-node throughput capacity (millions of concurrent sessions).
- **Limitations**: CTS adds a network dependency to every session operation. OpenDJ replication lag introduces eventual consistency for session state. Cassandra CTS requires Cassandra operational expertise.
- **OpenAM implementation**: `openam-core/src/.../cts/` package. `CTSPersistentStore` interface with `OpenDJTokenStore` and `CassandraTokenStore` implementations.

#### Docker Containers (2015-present) `[ACTIVE]`

- **First wave**: Community-contributed Dockerfiles wrapping OpenAM/OpenDJ WARs in Tomcat-based images. Images large (500MB-1GB); startup slow; configuration via volume mounts or environment variables.
- **OIP Docker images**: OIP provides official Dockerfiles for all components:
  - OpenAM: Tomcat base, `ROOT.war` deployment, configurable via `OPENAM_PROPERTIES`.
  - OpenDJ: Standalone Java process, data directory as volume mount.
  - OpenIDM: Felix OSGi container, `project` directory as volume mount.
  - OpenIG: Tomcat base, routes directory as volume mount.
- **Modern IAM Docker patterns**:
  - **Keycloak**: Official `quay.io/keycloak/keycloak` image. Quarkus-native build. `--optimized` flag for production (build-time provider compilation, immutable image). ~150MB image. <10 second startup.
  - **Ory stack**: Each component (Hydra, Kratos, Keto, Oathkeeper) is a standalone Go binary. Docker images are <50MB each. Sub-second startup.
  - **Zitadel**: Single Go binary. Docker image ~80MB. Sub-second startup.
- **Container-native IAM design principles**:
  1. Immutable images (no runtime configuration changes)
  2. Configuration via environment variables and mounted config files
  3. Health and readiness endpoints (`/healthz`, `/ready`)
  4. Graceful shutdown signal handling
  5. Stateless application tier (state in external database)
  6. Structured JSON logging to stdout

#### Kubernetes Operators (2018-present) `[ACTIVE]`

- **Concept**: A Kubernetes Operator encodes operational knowledge (installation, scaling, upgrade, backup, recovery) into a controller that watches custom resources and reconciles the desired state with actual state. For identity systems, Operators manage the lifecycle of IdP instances.
- **Keycloak Operator** (2018, v2 in 2024):
  - Custom resources: `Keycloak`, `KeycloakRealmImport`.
  - Manages Keycloak deployment, database connection, TLS, ingress.
  - v2 (Quarkus-native): Builds optimized, immutable Keycloak images with pre-compiled providers. Uses the "build then deploy" model.
  - Handles rolling upgrades, database migrations, and scaling.
- **SPIRE Kubernetes Registrar**: Automatically registers Kubernetes workloads with SPIRE for SPIFFE-based workload identity.
- **Vault Secrets Operator (VSO)**: Syncs Vault secrets to Kubernetes Secret objects. Watches for Vault secret changes and updates Kubernetes Secrets automatically.
- **OpenAM/OIP**: No official Kubernetes Operator. Organizations deploying OIP in Kubernetes must manage Deployments, StatefulSets, Services, and ConfigMaps manually. This is a significant gap compared to Keycloak and the Ory stack.

#### Microservices Decomposition (2017-present) `[ACTIVE]`

- **Ory Stack** (2017-present): The most explicit decomposition of IAM into microservices:
  - **Ory Hydra**: OAuth 2.0/OIDC authorization server. Certified OIDC provider. Headless -- delegates login/consent UI to the application.
  - **Ory Kratos**: Identity management (registration, login, MFA, profile, recovery). API-first, no built-in UI.
  - **Ory Keto**: Authorization (Zanzibar-style ReBAC). Relation tuples, check/expand/list APIs.
  - **Ory Oathkeeper**: Identity-aware reverse proxy (zero-trust access proxy). Authenticators, authorizers, mutators.
  - Each service has its own database (PostgreSQL, MySQL, or CockroachDB), API, and deployment lifecycle.
  - Teams adopt only the components they need.
- **Advantages**: Independent scaling per concern; independent release cycles; technology-appropriate choices per service (all Go, but could be different languages); failure isolation.
- **Disadvantages**: Inter-service communication overhead; distributed transaction complexity; operational burden of managing multiple services; integration testing across services.
- **Contrast with OpenAM**: OpenAM's ~60 Maven submodules hint at decomposition boundaries (oauth2, federation, authentication, entitlements, core) but they all compile and deploy as a single WAR. A microservices rewrite of OpenAM would likely follow Ory-like boundaries.

#### Single-Binary Architecture (2021-present) `[ACTIVE]`

- **Zitadel** (2021): Single Go binary backed by event sourcing and CQRS. The simplicity of a single binary (no external cache, no message queue, no distributed lock manager) combined with the architectural sophistication of event sourcing.
  - **Database**: CockroachDB (preferred, multi-region) or PostgreSQL.
  - **Event store**: Every state change is an immutable event. Read projections built from events for query performance.
  - **Deployment**: Single binary + database. Docker container or bare binary.
  - **Operational appeal**: One process to monitor, one log stream, one health endpoint. No Infinispan cluster (Keycloak), no CTS store (OpenAM), no inter-service networking (Ory).
- **Trade-off spectrum**:

| Approach | Examples | Operational Simplicity | Scalability | Component Independence |
|----------|---------|----------------------|-------------|----------------------|
| Monolithic WAR | OpenAM, early Keycloak | Medium (one WAR, but heavy JVM) | Scale everything together | None |
| Single binary | Zitadel, Authelia | High (one process + DB) | Scale replicas uniformly | None (but event-sourced) |
| Modular monolith | Keycloak (Quarkus) | High (single app, plugin SPI) | Scale replicas, selective features via build | Provider-level modularity |
| Microservices | Ory stack | Low (multiple services) | Scale per component | Full |
| SaaS/Serverless | Auth0, Cognito, Supabase Auth | Very high (vendor-managed) | Elastic (vendor-managed) | N/A |

#### Serverless Authentication (2017-present) `[ACTIVE]`

- **AWS Cognito** (2014/expanded 2017-present): Managed user pools and identity pools. No server to deploy. Auto-scaling. Lambda triggers for customization. Passkey support added 2024. Re-architecture announced at re:Invent 2024 (simplified tiers, managed login UI, access token customization).
- **Supabase Auth** (2021-present): PostgreSQL-backed authentication service as part of the Supabase platform. Row-level security (RLS) in PostgreSQL replaces traditional authorization middleware. GoTrue server (Go).
- **Firebase Authentication / Google Identity Platform**: Managed authentication SDKs for web and mobile. Free tier up to 50,000 MAU. Upgraded to Identity Platform for enterprise features (multi-tenancy, blocking functions).
- **Clerk** (2020-present): Developer-focused authentication-as-a-service. Pre-built UI components. Organizations, roles, sessions management. React, Next.js, Remix SDKs.
- **Characteristics**: No infrastructure to manage; pay-per-use pricing; rapid integration (SDKs, pre-built UI); limited customization compared to self-hosted; vendor lock-in; data residency constraints.

#### Edge-Deployed Identity (2022-present) `[EMERGING]`

- **Cloudflare Access** (2018/expanded 2022-present): Zero-trust access proxy deployed at Cloudflare's edge network (300+ global PoPs). Authenticates users via OIDC/SAML integration with upstream IdPs (Okta, Entra ID, Google). Evaluates device posture. No VPN required. Latency: authentication at the nearest edge PoP, typically <50ms.
- **Akamai Enterprise Application Access**: Identity-aware access at Akamai's edge. Similar architecture to Cloudflare Access.
- **Zscaler Private Access (ZPA)**: Zero-trust network access (ZTNA) with identity-aware application segmentation at Zscaler's cloud edge.
- **Architectural significance**: Identity verification moves from centralized data center IdP to globally distributed edge infrastructure. User authenticates at the nearest edge node, gets a short-lived token, and the token propagates to the origin application. This eliminates VPN hairpinning and reduces authentication latency for globally distributed workforces.
- **OpenAM relevance**: OpenAM deploys as a centralized WAR -- no edge distribution capability. An OpenAM deployment serving a global workforce introduces latency for users geographically distant from the OpenAM instance. Multi-site OpenAM deployment with CTS replication across data centers partially addresses this but adds significant operational complexity.

#### GitOps for Identity Infrastructure (2023-present) `[EMERGING]`

- **Concept**: Identity infrastructure (IdP configuration, gateway routes, policy definitions, certificate policies) managed as code in Git repositories, deployed via CI/CD pipelines (ArgoCD, Flux), with drift detection and automated reconciliation.
- **Patterns**:
  - Keycloak realm configuration exported as JSON, stored in Git, applied via `KeycloakRealmImport` CRD or Terraform Keycloak provider.
  - OpenIG routes as JSON files in Git, deployed via ConfigMap mount + hot reload.
  - Ory configuration (identity schemas, OAuth2 clients, access rules) as YAML in Git, applied via `ory` CLI or Kubernetes manifests.
  - OPA/Cedar policies as code in Git, deployed via OPA bundle API or `conftest`.
  - Vault policies and secret engine configuration via Terraform Vault provider.
  - SPIRE registration entries managed via SPIRE controller manager CRD.
- **Benefits**: Version-controlled identity configuration; peer review for policy changes; automated rollback on failure; audit trail via Git history; reproducible environments; drift detection.
- **Challenges**: Secrets management (credentials must not be in Git -- use sealed secrets, external secrets operator, or Vault); stateful resources (LDAP data, user profiles) are not GitOps-friendly; configuration drift from manual changes via admin UI.

#### Multi-Cloud and Hybrid Identity Architecture (2024-present) `[EMERGING]`

- **Problem**: Organizations operating across AWS, Azure, GCP, and on-premises need a unified identity plane that works across all environments. Cloud-specific solutions (Cognito, Entra ID, Google Identity Platform) create identity silos.
- **Architecture patterns**:
  1. **Hub-and-spoke federation**: Central IdP (Keycloak, OpenAM, Okta) federates with cloud-specific identity providers via OIDC/SAML. Each cloud environment trusts the central IdP.
  2. **Identity mesh**: Multiple IdPs connected via OIDC federation, shared signals (SSF/CAEP), and cross-domain trust. No single central IdP -- each environment has its own IdP federated with the others.
  3. **Workload identity federation**: Cloud workloads authenticate to other clouds' services using OIDC identity federation (e.g., GCP Workload Identity Federation accepts tokens from AWS IAM, Azure AD, or any OIDC provider). Eliminates cross-cloud service account keys.
- **OpenAM multi-site deployment**: OpenAM supports multi-site deployment with CTS replication across data centers. `sites` configuration in the `boot.properties` defines the site topology. Load balancers route users to the nearest site. CTS (OpenDJ-backed) replicates session tokens across sites.
- **OpenDJ multi-region replication**: OpenDJ's multi-master replication supports geographically distributed replicas with configurable replication lag. `dsreplication` tool manages replication topology. The RxJava 3 reactive I/O model handles high-throughput replication workloads.

### Deployment Model Comparison

| Model | Examples | Startup | Memory | Ops Burden | Scaling | Data Sovereignty |
|-------|---------|---------|--------|------------|---------|-----------------|
| WAR monolith | OpenAM, early Keycloak | 30-120s | 1-4 GB | High | Manual horizontal | Full control |
| Quarkus monolith | Keycloak 25+ | 5-10s | 200-500 MB | Medium | K8s Operator | Full control |
| Go single binary | Zitadel, Authelia | <1s | 50-200 MB | Low | K8s Deployment | Full control |
| Go microservices | Ory stack | <1s each | 20-50 MB each | High (multiple) | Per-service | Full control |
| Managed SaaS | Auth0, Okta, Cognito | N/A | N/A | None | Elastic | Vendor-managed |
| Edge-deployed | Cloudflare Access | N/A | N/A | None | Global edge | Limited |

---

## Roadmap 10: Passwordless & MFA Evolution

### Timeline Overview

```
1961  MIT CTSS: first computer password system (Fernando Corbato)
1967  /etc/passwd in Unix (passwords stored as hashed entries)
1976  Unix crypt() one-way password hash function
1979  /etc/shadow file separates password hashes from user data
1988  S/Key one-time password system (RFC 1760, 1995)
1991  RSA SecurID hardware tokens (first widely deployed OTP solution)
1993  NTLM authentication (Windows NT)
1996  HTTP Basic Auth passwords over HTTP (RFC 1945)
1999  PKCS#11 smart card authentication standard
2000  Microsoft Windows smart card login (CAC/PIV)
2003  US HSPD-12 mandates PIV smart cards for federal employees
2004  PhoneFactor (precursor to Azure MFA) -- phone-based authentication
2005  HOTP (RFC 4226) -- HMAC-based One-Time Password
2011  RSA SecurID seed compromise (40M tokens at risk)
2009  Google deploys U2F internally (pre-standard)
2010  SMS OTP widely deployed as second factor
2011  TOTP (RFC 6238) -- Time-based One-Time Password
2011  Google Authenticator app released
2013  Push notification authentication (Duo Security)
2013  FIDO Alliance founded (Google, PayPal, Lenovo, Nok Nok Labs, others)
2014  FIDO U2F 1.0 (Universal Second Factor)
2014  FIDO UAF 1.0 (Universal Authentication Framework -- passwordless on mobile)
2015  Windows Hello (Windows 10, platform authenticator)
2016  YubiKey 4 (multi-protocol: U2F, OTP, smart card, OpenPGP)
2017  NIST SP 800-63B deprecates SMS OTP for authentication
2018  WebAuthn Level 1 (W3C Candidate Recommendation)
2019  WebAuthn Level 1 (W3C Recommendation)
2019  CTAP 2.0 (Client to Authenticator Protocol)
2019  FIDO2 certification program launched
2020  Apple adds platform authenticator support (Face ID/Touch ID for WebAuthn)
2021  WebAuthn Level 2 (W3C Recommendation)
2022  Passkeys announced (Apple WWDC, Google I/O, Microsoft)
2022  Apple iCloud Keychain synced passkeys (iOS 16, macOS Ventura)
2023  Google Password Manager synced passkeys (Android 14)
2023  Microsoft Windows Hello synced passkeys (Windows 11 23H2)
2023  Conditional UI / autofill passkeys in browsers
2023  Third-party passkey managers (1Password, Bitwarden, Dashlane)
2024  FIDO CXP/CXF (Credential Exchange Protocol/Format) draft
2024  NIST SP 800-63-4 draft recognizes passkeys as AAL2/AAL3
2024  FIDO Alliance reports 15B+ passkey-enabled accounts
2024  WebAuthn Level 3 (W3C Working Draft)
2024  Enterprise device-bound passkeys with attestation
2025  Cross-platform passkey import/export GA
2025  Passkey adoption exceeds 30% of consumer authentications (major platforms)
2026  Passwordless-by-default for new applications; passwords as legacy fallback
```

### Milestone Details

#### Passwords (1961-present) `[LEGACY]`

- **Origin**: Fernando Corbato introduced computer passwords at MIT's Compatible Time-Sharing System (CTSS) in 1961 to protect per-user file access. Unix adopted passwords in the 1960s-70s, storing hashed passwords in `/etc/passwd` (later `/etc/shadow`).
- **Hash evolution**: `crypt()` (DES-based, 1976) -> MD5 (`$1$`, 1994) -> SHA-256/512 (`$5$`/`$6$`, 2008) -> bcrypt (`$2b$`, 1999, still recommended) -> scrypt (RFC 7914, 2016) -> Argon2 (PHC winner, 2015, recommended by OWASP).
- **NIST SP 800-63B** (2017, updated draft 2024): Eliminated composition rules (uppercase + lowercase + number + symbol), eliminated mandatory periodic password changes, required minimum 8 characters, recommended screening against breached password lists (HIBP).
- **OpenAM implementation**: `DataStoreModule` and `LDAPModule` validate passwords against OpenDJ or configured LDAP directories. Password policy enforcement via OpenDJ's `pwdPolicy` (draft-behera-ldap-password-policy). OpenAM's `PasswordResetService` provides self-service password reset.
- **Why legacy**: Passwords are the single most exploited authentication mechanism. Verizon DBIR consistently reports credential-related breaches as the #1 attack vector (>80% of hacking-related breaches involve credentials). Phishing, credential stuffing, password reuse, brute force, and social engineering all exploit the shared-secret model.

#### Hardware OTP Tokens (1991-present) `[LEGACY]`

- **RSA SecurID** (1991): Hardware token displaying a 6-digit code that changes every 60 seconds. Based on a symmetric seed shared between the token and the RSA Authentication Manager server. Widely deployed in finance, government, and defense.
- **2011 RSA breach**: Attackers compromised RSA's production systems and extracted SecurID seeds, affecting 40+ million tokens. This event accelerated the industry's move toward asymmetric cryptography (FIDO) and away from shared-secret OTP systems.
- **Current status**: Still deployed in some government and military environments. Declining as organizations migrate to FIDO2/passkeys. RSA SecurID rebranded as RSA ID Plus, now offering software tokens, biometrics, and FIDO2 alongside hardware tokens.
- **OpenAM implementation**: OpenAM's `SecurID` authentication module integrates with RSA Authentication Manager via the RSA Authentication Agent API.

#### HOTP (2005) `[LEGACY]`

- **Spec**: RFC 4226 (HOTP: An HMAC-Based One-Time Password Algorithm).
- **Mechanism**: Counter-based OTP. Shared secret + incrementing counter -> HMAC-SHA1 -> truncation -> 6/8-digit code. Client and server maintain synchronized counters.
- **Problem solved**: Software-based OTP without dedicated hardware. Counter-based rather than time-based (works without synchronized clocks).
- **Limitations**: Counter desynchronization if user generates codes without submitting them. Look-ahead window partially mitigates this but introduces security trade-offs.
- **OpenAM implementation**: `HOTPModule` in `openam-authentication/openam-auth-hotp/`. Supports configurable code length (6/8), HMAC algorithm, and look-ahead window.
- **Why legacy**: Superseded by TOTP (time-based, no counter sync issues) and FIDO2 (asymmetric, phishing-resistant).

#### TOTP (2011) `[ACTIVE]`

- **Spec**: RFC 6238 (TOTP: Time-Based One-Time Password Algorithm).
- **Mechanism**: Shared secret + current time (30-second window) -> HMAC-SHA1/SHA256/SHA512 -> truncation -> 6/8-digit code. Client and server derive the same code from the current time period.
- **Problem solved**: Eliminated counter synchronization issues from HOTP. Works with any device that has a clock (smartphones via authenticator apps).
- **Authenticator apps**: Google Authenticator (2011), Microsoft Authenticator, Authy (Twilio), FreeOTP, Duo Mobile, 1Password, Bitwarden. Key provisioning via QR code encoding the `otpauth://totp/` URI (RFC 6238 + de facto standard for URI format).
- **Limitations**: Shared secret must be stored on both sides; QR code provisioning is phishable (attacker relays the code in real-time); no channel binding; user must manually type 6-digit code.
- **OpenAM implementation**: OpenAM provides TOTP as an MFA option via the `OATH` authentication module (combining HOTP/TOTP). Provisioning via QR code. Configurable time step (30/60 seconds) and code length.
- **Current status**: Remains the most widely deployed MFA factor. Every major IAM platform supports TOTP. However, TOTP is not phishing-resistant -- real-time phishing proxies (evilginx2, Modlishka) relay TOTP codes from victim to attacker in milliseconds.

#### SMS OTP (2005-present) `[LEGACY]`

- **Mechanism**: One-time code sent via SMS to the user's registered phone number. User types the code into the login form.
- **Problem solved**: Second factor without requiring an authenticator app or hardware token. Leverages the user's existing phone.
- **NIST deprecation**: NIST SP 800-63B (2017) deprecated SMS OTP as an out-of-band authenticator due to:
  - SIM swapping attacks (attacker convinces carrier to port the victim's number)
  - SS7 protocol vulnerabilities (interception of SMS messages at the network layer)
  - SMS delivery failures (international roaming, carrier issues)
  - Real-time relay attacks (same as TOTP phishing)
- **Current status**: Still widely used despite deprecation guidance. Many consumer services (banks, social media) still offer SMS OTP as the primary or only MFA option. Enterprise deployments are migrating away.
- **OpenAM implementation**: OpenAM's `HOTP` module can deliver codes via SMS (using configured SMS gateway). The `ForgeRockAuthenticator` module supports SMS OTP delivery.

#### Push Authentication (2013-present) `[ACTIVE]`

- **Origin**: Duo Security (2010, push feature ~2013) pioneered push-based authentication. User receives a push notification on their registered mobile device; they approve or deny the authentication request with a single tap.
- **Advantages over TOTP/SMS**: No code to type; visual confirmation of what is being approved (application name, location, device); faster user experience; harder to phish (attacker cannot relay a push notification).
- **MFA fatigue / push bombing (2022)**: Attack where the adversary repeatedly triggers push notifications until the fatigued user approves. High-profile breaches (Uber, 2022; Cisco, 2022) exploited this vector.
- **Mitigations**: Number matching (user must type a number shown on the browser into the push notification -- Duo, Microsoft Authenticator, Okta Verify implemented this in 2022-2023); additional context (location, device, application) in the push notification; rate limiting on push requests; anomaly detection on push approval patterns.
- **OpenAM implementation**: OpenAM's `ForgeRockAuthenticator` supports push notification via the ForgeRock Authenticator app. OIP's implementation uses the Push authentication module.
- **Vendors**: Duo Security (Cisco), Microsoft Authenticator, Okta Verify, Ping Authenticator, ForgeRock Authenticator.

#### FIDO U2F (2014) `[LEGACY]`

- **Spec**: FIDO U2F 1.0 (FIDO Alliance, 2014). Updated U2F 1.2 (2017).
- **Mechanism**: Asymmetric key pair per origin. USB/NFC security key. Browser sends challenge to the key; key signs the challenge with the origin-specific private key; server verifies the signature with the registered public key.
- **Key innovation**: Origin binding. The browser includes the origin in the signed challenge, preventing phishing. A credential created for `bank.com` cannot be used on `b4nk.com` -- the key signs a different origin and the server rejects it.
- **Hardware**: YubiKey (Yubico), Google Titan Security Key, Feitian, SoloKeys, Thetis.
- **Google internal deployment** (2017): Google required U2F security keys for all 85,000+ employees. Result: zero successful phishing attacks on employee accounts since deployment.
- **Why legacy**: Superseded by FIDO2/WebAuthn (backward-compatible superset). U2F was second-factor only; WebAuthn supports both second-factor and primary (passwordless) authentication.

#### FIDO2 / WebAuthn (2019-present) `[ACTIVE]`

- **Specs**:
  - WebAuthn Level 1 (W3C Recommendation, March 2019)
  - WebAuthn Level 2 (W3C Recommendation, April 2021)
  - WebAuthn Level 3 (W3C Working Draft, 2024)
  - CTAP 2.0 (Client to Authenticator Protocol, FIDO Alliance, 2019)
  - CTAP 2.1 (2022): resident keys, credential management, enterprise attestation
  - CTAP 2.2 (draft, 2024): hybrid transport improvements
- **Core innovation**: Asymmetric cryptography scoped to the relying party's origin, implemented in hardware (security key) or platform (TPM, Secure Enclave, TEE). Private key never leaves the authenticator. Challenge-response protocol makes phishing structurally impossible.
- **Authentication flow**:
  1. Registration: Authenticator generates key pair; public key sent to server; server stores it.
  2. Authentication: Server sends challenge; authenticator signs it with private key; server verifies with stored public key.
  3. User verification: Biometric (fingerprint, face), PIN, or presence test at the authenticator.
- **Authenticator types**:
  - **Platform authenticators** `[ACTIVE]`: Built into the device. Windows Hello (TPM), Apple Face ID/Touch ID (Secure Enclave), Android fingerprint/face (TEE/StrongBox). Convenient but device-bound.
  - **Roaming authenticators** `[ACTIVE]`: Separate hardware (USB, NFC, BLE). YubiKey 5 series, Google Titan, SoloKeys v2. Portable across devices but require physical possession.
- **Attestation**: Authenticator can provide attestation (proof of its make and model) during registration. Enterprise attestation allows organizations to restrict registration to approved authenticator models (e.g., only company-issued YubiKeys).
- **OpenAM implementation**: OIP OpenAM 16.x includes a WebAuthn authentication module in `openam-authentication/openam-auth-webauthn/`. Supports registration and authentication flows. Predates passkey sync era -- primarily supports device-bound credentials.

#### Passkeys (2022-present) `[ACTIVE]`

- **Definition**: Passkeys are FIDO2/WebAuthn credentials that sync across devices via a cloud credential manager. They solve FIDO2's usability gap -- device-bound credentials were lost when the device was lost or replaced.
- **Platform support**:
  - Apple iCloud Keychain (iOS 16+, macOS Ventura+, 2022): Synced across Apple devices via iCloud.
  - Google Password Manager (Android 14+, Chrome, 2023): Synced across Google-signed-in devices.
  - Microsoft Windows Hello (Windows 11 23H2+, 2023): Synced via Microsoft account.
  - Third-party managers: 1Password, Bitwarden, Dashlane (2023-2024): Cross-platform sync independent of OS vendor.
- **Adoption data**:
  - FIDO Alliance: 15B+ passkey-enabled accounts (late 2024).
  - Google: 800M+ accounts using passkeys. Passkey sign-ins 4x faster and more successful than password sign-ins.
  - GitHub: Passkey support GA (2023). Seeing increasing adoption among developers.
  - Amazon, eBay, Best Buy, Kayak, PayPal, Shopify, TikTok, Yahoo Japan, NTT DOCOMO: All deployed passkeys for consumer accounts by 2024.
- **Conditional UI** (2023-present) `[ACTIVE]`: Passkeys appear in the browser's autofill dropdown alongside saved passwords. No special "Sign in with passkey" button needed. Users select a passkey from the same UI they use for passwords, dramatically reducing friction and improving discovery.
- **Cross-device authentication** (2023-present) `[ACTIVE]`: Use phone as authenticator for desktop login. Browser shows QR code; user scans with phone; phone's authenticator signs the challenge via Bluetooth proximity verification. Bridges the gap when passkeys are on phone but login is on desktop without synced passkeys.
- **FIDO CXP/CXF** (Credential Exchange Protocol/Format, 2024) `[EMERGING]`: Enables exporting and importing passkeys between credential managers. Addresses vendor lock-in concern -- users can migrate from iCloud Keychain to 1Password or vice versa. Draft specification in 2024; GA expected 2025-2026.

#### Device-Bound vs Synced Passkeys `[ACTIVE]`

| Attribute | Synced Passkeys | Device-Bound Passkeys |
|-----------|----------------|----------------------|
| Storage | Cloud credential manager (iCloud, Google, 1Password) | Hardware security key (YubiKey) or platform TPM |
| Sync | Across devices via cloud | No sync -- single device |
| Recovery | Cloud account recovery | Physical possession of hardware |
| Assurance | AAL2 (NIST SP 800-63B draft) | AAL3 (highest assurance) |
| Key extraction | Possible (cloud-stored) | Impossible (hardware-protected) |
| Use case | Consumer, general enterprise | Regulated, high-security (finance, government, defense) |
| FIDO certification | Varies by provider | FIPS 140-2/3 validated (some keys) |

- **Enterprise deployment considerations**:
  - Device policies: Which authenticators are permitted? Enterprise attestation allows restricting to approved models.
  - Recovery: What happens when all passkeys are lost? Fallback methods (password + OTP, supervised recovery, helpdesk-assisted re-enrollment) must be planned.
  - Managed device deployment: MDM can provision security keys and configure allowed authenticator types.
  - Compliance: Regulated industries (HIPAA, PCI-DSS, FedRAMP) may require device-bound passkeys for AAL3.

#### MFA Factor Evolution Table

| Generation | Factor Type | Example | Phishing Resistant | User Friction | Adoption |
|------------|-------------|---------|-------------------|--------------|----------|
| 0 | Knowledge only | Password | No | Low | Universal `[LEGACY]` |
| 1 | Knowledge + possession | Password + hardware OTP (RSA SecurID) | No | High | Declining `[LEGACY]` |
| 2 | Knowledge + possession | Password + TOTP app | No | Medium | Widespread `[ACTIVE]` |
| 3 | Knowledge + possession | Password + SMS OTP | No | Medium | Declining `[LEGACY]` |
| 4 | Knowledge + possession | Password + push notification | Partially (number matching) | Low | Growing `[ACTIVE]` |
| 5 | Possession + inherence | FIDO2 security key + biometric | Yes (origin-bound) | Low | Growing `[ACTIVE]` |
| 6 | Possession + inherence | Passkey (synced) + biometric | Yes (origin-bound) | Very low | Accelerating `[ACTIVE]` |
| 7 | Continuous | Behavioral biometrics + context | Yes (implicit) | None | Early `[EMERGING]` |

#### NIST SP 800-63 Authenticator Assurance Levels

| Level | Requirement | Examples |
|-------|-------------|---------|
| AAL1 | Single factor (any type) | Password, single-factor OTP |
| AAL2 | Two factors, at least one cryptographic | TOTP + password, synced passkey, push with number match |
| AAL3 | Two factors, hardware-based cryptographic verifier | Device-bound FIDO2 key, PIV smart card, hardware TPM |

- **SP 800-63-4 (draft, 2024)**: Updates to recognize passkeys. Synced passkeys qualify for AAL2. Device-bound passkeys with enterprise attestation qualify for AAL3. Phishing resistance becomes a key differentiator between AAL2 and AAL3.

#### Continuous Authentication (2024-present) `[EMERGING]`

- **Concept**: Authentication is not a binary event (logged in / not logged in) but a continuous signal. The system continuously evaluates user behavior, device state, and environmental context to maintain a real-time confidence score.
- **Signals**: Keystroke dynamics, mouse movement patterns, touch pressure, gait analysis (mobile), typing cadence, application usage patterns, network location, device posture, time-of-day patterns.
- **Products**: BioCatch (behavioral biometrics for banking), Neuro-ID (behavioral analytics), Microsoft Entra ID Protection (continuous access evaluation), Silverfort (continuous identity verification).
- **OIDC Shared Signals Framework (SSF)** `[EMERGING]`: Formerly RISC + CAEP. Standardizes real-time security event sharing between providers. CAEP (Continuous Access Evaluation Protocol) enables IdPs to push risk signals to relying parties, triggering session revocation or step-up authentication without waiting for token expiry.
- **OpenAM implementation**: OpenAM's adaptive authentication module evaluates device fingerprint, geolocation, and login history to adjust authentication requirements. This is a precursor to continuous authentication but operates at login time, not continuously.

---

## Roadmap 11: Zero Trust & Perimeter Evolution

### Timeline Overview

```
1988  DEC publishes first packet filtering paper
1993  Check Point Firewall-1 (stateful inspection, first commercial firewall)
1993  DMZ architecture standardized (dual-firewall, three-zone)
1995  IPsec (RFC 1825-1829; updated by RFC 4301-4309 in 2005)
1999  SSL VPN concept (Neoteris, later Juniper)
2001  802.1X Network Access Control (IEEE)
2003  Network Access Control (NAC) category emerges (Cisco NAC, Microsoft NAP)
2004  Jericho Forum (deperimeterization manifesto)
2005  NAC/802.1X enterprise deployments
2010  Forrester Research publishes "No More Chewy Centers" -- John Kindervag coins "Zero Trust"
2010  Google begins internal BeyondCorp implementation
2011  Cloud Access Security Broker (CASB) category emerges
2013  Software-Defined Networking (SDN) enables micro-segmentation
2014  Google BeyondCorp paper published ("A New Approach to Enterprise Security")
2014  Cloud Security Alliance (CSA) Software-Defined Perimeter (SDP) specification
2015  Google BeyondCorp: Design to Deployment paper
2016  NIST SP 800-160 (Systems Security Engineering)
2017  Zscaler Private Access (ZPA) -- commercial ZTNA
2017  Istio service mesh (identity-based microsegmentation)
2018  Cloudflare Access (edge-deployed zero trust proxy)
2019  Gartner coins SASE (Secure Access Service Edge)
2020  NIST SP 800-207 (Zero Trust Architecture) published
2021  US Executive Order 14028 on Cybersecurity (May 2021, zero trust mandate)
2021  CISA Zero Trust Maturity Model v1.0
2022  US OMB M-22-09 (Federal Zero Trust Strategy, mandatory deadlines)
2022  DoD Zero Trust Strategy and Roadmap
2023  CISA Zero Trust Maturity Model v2.0 (five pillars: Identity, Devices, Networks, Applications, Data)
2023  EU NIS2 Directive (implies zero-trust principles for critical infrastructure)
2024  Gartner predicts 60% of enterprises will adopt zero trust by 2025
2022  ZTNA 2.0 (Palo Alto Networks) -- application-level zero trust
2025  Continuous verification as default security posture
2026  Zero trust extends to AI agents and autonomous systems
```

### Milestone Details

#### Firewall Perimeter Model (1988-2010) `[LEGACY]`

- **Architecture**: Trusted internal network protected by firewall(s) at the boundary. External traffic filtered by port/protocol rules. Internal traffic trusted by default. DMZ (demilitarized zone) hosts externally-facing servers (web, email, DNS) in a partially trusted segment between the outer and inner firewalls.
- **Key products**: Checkpoint Firewall-1 (1993, stateful inspection), Cisco PIX/ASA, Juniper/Netscreen, Palo Alto Networks (2007, application-aware).
- **Identity integration**: Minimal. Firewalls operated at Layer 3/4 (IP address, port). Identity was not a factor in network access decisions. Users authenticated to applications behind the firewall; the firewall did not know or care about user identity.
- **Failure mode**: Once inside the perimeter (via VPN, compromised endpoint, or physical access), attackers moved laterally without additional authentication challenges. The 2013 Target breach (HVAC vendor VPN -> POS systems) and 2014 Sony Pictures breach exemplified perimeter failure.
- **OpenAM in the perimeter model**: OpenAM sat inside the trusted zone. OpenIG or policy agents enforced authentication at the DMZ boundary. Internal services behind OpenIG were assumed trusted. This architecture is described in [Chapter 10: OpenIG Analysis](10-openig-analysis.md), Section 8.

#### VPN Remote Access (1996-present) `[LEGACY]`

- **Protocols**: PPTP (1996, Microsoft, `[OBSOLETE]`), L2TP/IPsec (RFC 3193, 2001, `[LEGACY]`), SSL/TLS VPN (2003, Juniper/Cisco, `[LEGACY]`), OpenVPN (2001, `[ACTIVE]`), WireGuard (2018, `[ACTIVE]`), IPsec IKEv2 (RFC 7296, 2014, `[ACTIVE]`).
- **Problem solved**: Extended the trusted perimeter to remote users. VPN creates an encrypted tunnel from the user's device to the corporate network, granting the user a "virtual" presence inside the perimeter.
- **Limitations**: Full network access upon connection (violates least privilege); performance overhead (hairpinning traffic through VPN concentrator); split-tunnel security risks; VPN credential theft enables full network access; does not scale to cloud-first, multi-cloud architectures; VPN concentrators are single points of failure and attack targets (Pulse Secure CVE-2019-11510, Fortinet CVE-2018-13379).
- **Identity integration**: VPN authentication typically via RADIUS (RFC 2865) or LDAP against the corporate directory (AD, OpenDJ). MFA increasingly required (TOTP, push notification, FIDO2).
- **OpenAM relevance**: OpenAM can serve as the authentication backend for VPN concentrators via RADIUS or SAML. The `openam-radius` module provides RADIUS server functionality.

#### Jericho Forum and Deperimeterization (2004) `[OBSOLETE]`

- **Origin**: The Jericho Forum, an international IT security consortium, published the Jericho Forum Commandments (2004-2006) arguing that the traditional network perimeter was dissolving and organizations should prepare for a "deperimeterized" world where security is inherent in the data and applications, not in the network boundary.
- **Key principles**: Authenticate and authorize at the data/application layer, not the network layer. Encrypt data in transit and at rest. Use open, standard protocols. Design systems that work securely over untrusted networks.
- **Significance**: Intellectually prescient but commercially premature. The technology (FIDO, mTLS, OIDC, service mesh) did not exist yet. Jericho Forum dissolved in 2013, declaring its mission accomplished as the industry began adopting deperimeterization principles.
- **Relation to Zero Trust**: Jericho Forum's deperimeterization concept was the intellectual precursor to Zero Trust. Both assert that network location is not a valid basis for trust.

#### Google BeyondCorp (2014) `[ACTIVE]`

- **Papers**: "BeyondCorp: A New Approach to Enterprise Security" (USENIX ;login:, 2014). Followed by design, deployment, migration, and front-end infrastructure papers (2015-2017).
- **Architecture**: Eliminated the privileged corporate network. All Google internal applications are accessible over the public internet without VPN. Access decisions based on:
  1. **User identity**: Who is the user? (Authenticated via SSO, MFA required.)
  2. **Device inventory**: Is this a known, managed device? (Device certificate, MDM compliance.)
  3. **Device state**: Is the device patched, encrypted, running approved software?
  4. **Access policy**: Does the combination of user identity + device trust + request context meet the policy requirements for this resource?
- **Key components**:
  - Device Inventory Service: Tracks all corporate devices, their compliance state, and certificate status.
  - Access Proxy: Front-end proxy (similar to OpenIG/Nginx in function) that enforces per-request access decisions. All user traffic routes through the access proxy.
  - Access Control Engine: Evaluates policy combining user identity, device trust, and request context.
  - Trust Engine: Computes a trust score for each device based on inventory, certificate status, and compliance.
  - SSO/IdP: Google's internal SSO system (hardware security keys required for all employees since 2017).
- **Impact**: BeyondCorp demonstrated at scale (100,000+ employees) that VPN-less, perimeter-less enterprise security is practical. It directly inspired the commercial ZTNA (Zero Trust Network Access) market and influenced NIST SP 800-207.
- **OpenAM parallel**: OpenAM's adaptive authentication module (device fingerprinting, geolocation, login history) and OpenIG's policy enforcement (per-request access decisions) implement elements of the BeyondCorp model but without the device inventory/trust engine components.

#### Software-Defined Perimeter (SDP) (2014) `[ACTIVE]`

- **Spec**: Cloud Security Alliance (CSA) SDP Specification 1.0 (2014), updated 2.0 (2022).
- **Architecture**: Three components:
  1. **SDP Controller**: Authentication and authorization broker. Verifies user identity and device posture before creating connections.
  2. **Initiating Host (IH)**: Client-side agent. Authenticates to the SDP Controller before any network connection is established.
  3. **Accepting Host (AH)**: Protects the application server. Accepts connections only from authenticated, authorized IH clients.
- **"Dark cloud" principle**: Protected resources are invisible to unauthorized clients. No DNS exposure, no open ports, no network scanning surface. The SDP Controller must authorize a client before the client can even discover the protected resource's network address.
- **Products**: Zscaler Private Access (ZPA), Appgate SDP, Perimeter 81 (Check Point), Cloudflare Access, Palo Alto Prisma Access.

#### NIST SP 800-207 (2020) `[ACTIVE]`

- **Publication**: NIST Special Publication 800-207, "Zero Trust Architecture" (August 2020).
- **Definition**: "Zero trust (ZT) provides a collection of concepts and ideas designed to minimize uncertainty in enforcing accurate, least privilege per-request access decisions in information systems and services in the face of a network viewed as compromised."
- **Core tenets**:
  1. All data sources and computing services are considered resources.
  2. All communication is secured regardless of network location.
  3. Access to individual enterprise resources is granted on a per-session basis.
  4. Access is determined by dynamic policy -- user identity, application, requesting asset state, behavioral attributes, environmental conditions.
  5. The enterprise monitors and measures the integrity and security posture of all owned and associated assets.
  6. All resource authentication and authorization are dynamic and strictly enforced before access is allowed.
  7. The enterprise collects as much information as possible about the current state of assets, network infrastructure, and communications, and uses it to improve its security posture.
- **Deployment models**: Enhanced identity governance, micro-segmentation, network infrastructure-based (SDP).
- **Policy Engine (PE) + Policy Administrator (PA) + Policy Enforcement Point (PEP)**: Abstract architectural components that map to concrete products:
  - PE: OPA, Cedar, OpenAM policy engine, Entra Conditional Access
  - PA: IdP (OpenAM, Okta, Keycloak), device trust broker, SIEM
  - PEP: API gateway (Kong, OpenIG), service mesh sidecar (Envoy), ZTNA proxy (Zscaler, Cloudflare Access)

#### OMB M-22-09 (2022) `[ACTIVE]`

- **Publication**: US Office of Management and Budget Memorandum M-22-09, "Moving the U.S. Government Toward Zero Trust Cybersecurity Principles" (January 2022).
- **Mandates for federal agencies** (end of FY 2024 deadlines):
  1. Enterprise-wide identity system with phishing-resistant MFA for agency staff.
  2. Device authorization through endpoint detection and response (EDR).
  3. Encrypted DNS (DoH/DoT) and HTTP traffic.
  4. Application-level authorization (not just network perimeter).
  5. Data classification and protection.
- **Identity pillar requirements**:
  - Phishing-resistant MFA (FIDO2/WebAuthn, PIV) for all agency staff -- "password + SMS OTP" does not meet the requirement.
  - Centralized identity management with continuous monitoring.
  - Enterprise SSO integrated with agency applications.
- **Impact**: Federal mandates drive vendor roadmaps. All major IdP vendors (Okta, Entra ID, Ping, CyberArk) accelerated phishing-resistant MFA features to meet OMB deadlines.

#### CISA Zero Trust Maturity Model (2021, v2.0 2023) `[ACTIVE]`

- **Five pillars**:

| Pillar | Traditional | Advanced | Optimal |
|--------|------------|----------|---------|
| **Identity** | Password + basic MFA; limited identity awareness | Phishing-resistant MFA; identity validated per transaction | Continuous validation; real-time identity threat detection |
| **Devices** | Limited device visibility | Device compliance checked at access time | Continuous device health monitoring; automated remediation |
| **Networks** | Macro-segmentation (VLANs) | Micro-segmentation by application | Micro-segmentation with identity-based policies; encrypted DNS |
| **Applications** | Static access controls | Application-aware policies; integrated with IdP | Continuous monitoring; behavior-based access |
| **Data** | Minimal classification | Data categorized and inventoried | Automated classification; DLP; encryption everywhere |

- **Cross-cutting capabilities**: Visibility and analytics, automation and orchestration, governance.
- **OpenAM alignment**: OpenAM provides "Advanced" identity pillar capabilities (MFA, SSO, per-request policy evaluation). "Optimal" requires continuous authentication and ITDR integration that OpenAM does not natively provide.

#### How OpenAM/OpenIG Map to Zero Trust `[LEGACY]`

The OIP stack implements several zero-trust architectural components:

| Zero Trust Component | OIP Implementation | Gap |
|---------------------|-------------------|-----|
| Policy Enforcement Point (PEP) | OpenIG reverse proxy, OpenAM policy agents | No sidecar/service mesh mode |
| Policy Decision Point (PDP) | OpenAM policy engine (XACML 3.0) | No OPA/Rego/Cedar integration |
| Identity Provider | OpenAM (OIDC, SAML, OAuth) | No continuous auth, no CAEP |
| MFA | OpenAM WebAuthn, TOTP, HOTP, Push | Limited passkey/sync support |
| Device Trust | OpenAM device fingerprinting (basic) | No MDM/EDR integration |
| Micro-segmentation | Not addressed | Requires service mesh (Istio) |
| Session Continuity | CTS-based session management | No OIDC SSF/CAEP for real-time revocation |
| Adaptive Auth | OpenAM adaptive module (location, device, history) | Basic ML; no behavioral biometrics |
| Workload Identity | OAuth 2.0 client credentials | No SPIFFE/SPIRE |
| Audit/Monitoring | OpenAM audit logs | No ITDR, no SIEM integration out of box |

The OIP stack was designed for the perimeter era. It can serve as a building block within a zero-trust architecture -- providing the IdP, MFA, and PEP -- but must be supplemented with service mesh (Istio/Envoy), ITDR (Silverfort, CrowdStrike), device trust (MDM/EDR), and modern policy engines (OPA, Cedar) to achieve "Optimal" zero trust maturity.

#### ZTNA and SASE (2019-present) `[ACTIVE]`

- **ZTNA (Zero Trust Network Access)**: Application-specific access replacing VPN. Users are authorized for specific applications, not entire network segments. Products: Zscaler ZPA, Cloudflare Access, Palo Alto Prisma Access, Netskope Private Access.
- **SASE (Secure Access Service Edge)** (Gartner, 2019): Converges network services (SD-WAN) with security services (SWG, CASB, FWaaS, ZTNA) into a cloud-delivered platform. Single vendor provides both networking and security at the edge.
  - Vendors: Zscaler, Palo Alto Prisma SASE, Netskope, Cloudflare One, Cisco SASE.
  - Identity integration: SASE platforms delegate authentication to external IdPs (Okta, Entra ID, Ping, SAML/OIDC). Access policies combine user identity, device posture, and application sensitivity.
- **ZTNA 2.0** (Palo Alto Networks term, 2022): Extends zero trust from access control to continuous application monitoring. Verifies not just "can this user access this app" but "is the user's behavior within this app consistent with expected patterns."

#### Zero Trust for Non-Human Identities (2024-present) `[EMERGING]`

- **Extension**: Zero trust principles (verify explicitly, least privilege, assume breach) applied to machine identities, service accounts, API keys, CI/CD pipelines, and AI agents.
- **Challenges**: Machine identities outnumber human identities 50:1+. Most have excessive permissions. Many use long-lived credentials. Monitoring machine identity behavior is harder (no "normal working hours" baseline).
- **Approaches**: SPIFFE/SPIRE for workload identity (cryptographic, short-lived, automatically rotated); Vault for dynamic secrets (ephemeral, auto-revoked); cloud IAM permission boundaries; service account monitoring (Silverfort, CrowdStrike); AI agent identity as an emerging concern (how do you authenticate an AI agent acting on behalf of a user?).

---

## Roadmap 12: Machine & Workload Identity

### Timeline Overview

```
1990s Service accounts in Unix/Windows (dedicated OS accounts for daemons/services)
1993  Kerberos V5 service principals (RFC 1510; updated RFC 4120, 2005)
1999  X.509 client certificates for server authentication (SSL/TLS)
2000s API keys proliferate as machine authentication
2003  WS-Security (OASIS) for SOAP service authentication
2005  WS-Trust (OASIS) for STS-based token issuance to services
2011  AWS IAM roles (cloud-native machine identity)
2012  OAuth 2.0 Client Credentials Grant (RFC 6749, Section 4.4)
2013  Azure AD Service Principals / Managed Identities (preview)
2014  Kubernetes Service Accounts
2015  HashiCorp Vault AppRole (application-oriented auth for secrets)
2015  Let's Encrypt (automated certificate issuance for servers, ACME protocol)
2016  GCP Service Accounts
2017  SPIFFE specification v0.1 (CNCF sandbox)
2018  SPIRE v0.1 (SPIFFE Runtime Environment, reference implementation)
2018  Kubernetes TokenRequest API (bound, projected service account tokens)
2019  AWS IAM Roles for Service Accounts (IRSA) -- OIDC-based workload identity in EKS
2019  Istio 1.1+ uses SPIFFE IDs for mTLS identity
2020  GCP Workload Identity Federation (accept external OIDC tokens for GCP access)
2021  Azure Workload Identity (OIDC-based, replacing pod-managed identity)
2021  cert-manager v1.0 (Kubernetes-native certificate management)
2021  Sigstore (Cosign, Fulcio, Rekor) for supply chain identity
2020  SPIFFE/SPIRE CNCF Incubating
2023  OpenPubkey (BastionZero, Linux Foundation) -- identity-bound public keys
2023  GitHub Actions OIDC tokens for keyless auth to cloud providers
2022  SPIFFE/SPIRE CNCF Graduated
2024  CyberArk acquires Venafi (machine identity management)
2024  IETF WIMSE Working Group chartered (Workload Identity in Multi-System Environments)
2024  Kubernetes bound service account token improvements
2025  Non-human identity management as a security discipline
2025  IETF WIMSE drafts: workload identity token, transaction tokens for workloads
2026  Machine identity outnumbers human identity 100:1+ in large organizations
```

### Milestone Details

#### Service Accounts (1990s-present) `[ACTIVE]`

- **Unix/Linux service accounts**: Dedicated OS users (e.g., `www-data`, `postgres`, `mysql`, `nobody`) for running daemon processes. Minimal shell access (`/sbin/nologin`). Group-based filesystem permissions.
- **Windows service accounts**: Local Service, Network Service, and domain service accounts. Managed Service Accounts (MSA, Windows Server 2008) and Group Managed Service Accounts (gMSA, 2012) automate password management for Windows services.
- **Active Directory service accounts**: Regular AD accounts used for running applications. Historically shared, rarely rotated, with excessive privileges. The #1 target in enterprise breaches (Silverfort reports 70%+ of enterprise service accounts have excessive privileges).
- **Problems**: Long-lived passwords embedded in configuration files, scripts, and environment variables. Shared across multiple services. No individual accountability. Manual rotation (or no rotation). Excessive privileges (often domain admin "just in case"). Difficult to audit -- service account activity indistinguishable from legitimate and malicious usage.
- **OpenAM relevance**: OpenAM itself runs under a service account (Tomcat's `tomcat` user or equivalent). OpenAM authenticates service accounts via LDAP bind against OpenDJ. The `amadmin` account is OpenAM's built-in administrative service account, and its credential management follows the same problematic patterns (long-lived password, rarely rotated). OpenAM's OAuth 2.0 client credentials grant (RFC 6749, Section 4.4) provides a modern alternative for service-to-service authentication.

#### Kerberos Service Principals (1993) `[ACTIVE]`

- **Spec**: RFC 1510 (1993), updated RFC 4120 (2005).
- **Mechanism**: Services register with the KDC as service principals (`HTTP/webserver.example.com@REALM`). Clients obtain service tickets from the KDC to authenticate to specific services. Mutual authentication: the service proves its identity to the client, and the client proves its identity to the service.
- **Keytab files**: Shared secret between the service and KDC stored in a keytab file on the service host. Equivalent to a service password but used for cryptographic operations rather than plaintext transmission.
- **Current status**: Still foundational for Windows domain environments (Active Directory Kerberos). Heavily targeted: Kerberoasting (requesting service tickets for offline password cracking), Silver Ticket (forging service tickets), Golden Ticket (forging TGTs) attacks.
- **OpenAM implementation**: OpenAM's `WindowsDesktopSSO` module supports SPNEGO/Kerberos for browser-based SSO in Windows environments. OpenAM can act as a Kerberos-authenticating gateway.

#### API Keys (2000s-present) `[ACTIVE]`

- **Mechanism**: Static string (typically 32-128 character hex or base64) identifying a client application. Transmitted via HTTP header (`X-API-Key`, `Authorization: Bearer`), query parameter, or cookie.
- **Problems as machine identity**: Long-lived (no expiry); overly broad (full API access); no scope limitation; difficult to rotate at scale; frequently leaked in source code, log files, and public repositories (GitHub secret scanning detects millions of leaked API keys annually).
- **Best practice evolution**: API keys for identification (rate limiting, usage tracking) + OAuth tokens for authorization (scoped, time-limited, revocable). Google Cloud transitioned from API keys to service account OAuth tokens for authentication.
- **OpenAM relevance**: OpenAM does not issue API keys natively. API key management is typically a gateway concern (Kong, Apigee). OpenIG can validate API keys via `ScriptableFilter` with a lookup against a key store.

#### OAuth 2.0 Client Credentials Grant (2012) `[ACTIVE]`

- **Spec**: RFC 6749, Section 4.4.
- **Mechanism**: Service authenticates directly to the authorization server with its `client_id` and `client_secret`. No user involvement. Authorization server issues an access token representing the service's own identity.
- **Use case**: Machine-to-machine (M2M) authentication. Service A calls Service B's API using an OAuth access token obtained via client credentials.
- **Limitations**: `client_secret` is a shared secret (same problems as passwords if not managed properly). No user context in the token. Scopes are static (assigned at client registration time).
- **Modern improvements**: JWT client authentication (RFC 7523) -- client proves identity using a signed JWT instead of a shared secret. mTLS client authentication (RFC 8705) -- client identity derived from the TLS client certificate.
- **OpenAM implementation**: OpenAM's OAuth 2.0 authorization server supports client credentials grant. Client registration via the admin console or REST API. Token issuance with configurable scopes and lifetime.

#### Cloud IAM Roles and Managed Identities (2011-present) `[ACTIVE]`

- **AWS IAM Roles** (2011): Identity assigned to AWS resources (EC2 instances, Lambda functions, ECS tasks). No long-lived credentials -- temporary credentials obtained via the Instance Metadata Service (IMDS) or STS AssumeRole. Credentials automatically rotated.
  - **IAM Roles for Service Accounts (IRSA)** (2019) `[ACTIVE]`: OIDC-based workload identity for EKS pods. Pod assumes an IAM role by presenting a Kubernetes service account token to the AWS STS, which validates it against the EKS OIDC provider. No `AWS_ACCESS_KEY_ID` in environment variables.
  - **EKS Pod Identity** (2023) `[ACTIVE]`: Simplified alternative to IRSA. Uses a pod identity agent (daemonset) and pod identity associations rather than OIDC. Lower complexity.
- **Azure Managed Identities** (2018 GA): System-assigned (tied to a specific Azure resource, deleted when resource is deleted) or user-assigned (independent lifecycle, assignable to multiple resources). Identity provided by the Azure Instance Metadata Service (IMDS). No secrets management required.
  - **Azure Workload Identity** (2021) `[ACTIVE]`: OIDC-based identity for AKS pods. Kubernetes service account token exchanged for an Azure AD token via OIDC federation.
- **GCP Service Accounts** (2016) / **Workload Identity Federation** (2020) `[ACTIVE]`:
  - Service accounts with key files (JSON) -- legacy pattern, similar problems to API keys.
  - Workload Identity Federation: Accept OIDC/SAML tokens from external providers (AWS, Azure, GitHub Actions, any OIDC IdP) for GCP access. No service account keys needed.
  - GKE Workload Identity: Kubernetes service accounts mapped to GCP service accounts. Pod authenticates as GCP SA automatically.
- **OpenAM relevance**: OpenAM is not a cloud IAM service and does not issue cloud provider credentials. However, OpenAM can federate with cloud IAM:
  - OpenAM as OIDC provider -> GCP Workload Identity Federation accepts OpenAM-issued OIDC tokens.
  - OpenAM as SAML IdP -> AWS IAM SAML federation for console access.
  - OpenAM OAuth tokens used by applications that then assume cloud IAM roles.

#### SPIFFE and SPIRE (2017-present) `[ACTIVE]`

- **SPIFFE** (Secure Production Identity Framework for Everyone): CNCF specification defining a standard for workload identity.
  - **SPIFFE ID**: URI-based identity: `spiffe://trust-domain/workload-identifier`. Example: `spiffe://example.com/payments/api`.
  - **SVID (SPIFFE Verifiable Identity Document)**: Cryptographic proof of identity. Two formats:
    - X.509-SVID: Standard X.509 certificate with SPIFFE ID in the SAN (Subject Alternative Name) URI field. Used for mTLS.
    - JWT-SVID: JWT token with SPIFFE ID in the `sub` claim. Used for application-layer authentication.
  - **Trust bundle**: Set of root CA certificates for a trust domain. Exchanged between trust domains for federation.
  - **Workload API**: Local API exposed via Unix domain socket. Workloads obtain SVIDs without managing secrets, keys, or certificates.
- **SPIRE** (SPIFFE Runtime Environment): Reference implementation. CNCF Graduated (September 2022).
  - **SPIRE Server**: Central component. Manages workload registrations, performs attestation, issues SVIDs. Stores registration entries in SQLite, PostgreSQL, or MySQL. CA functionality built-in or delegated to upstream CA (Vault, AWS PCA).
  - **SPIRE Agent**: Runs on each node (one per host/VM). Attests node identity to SPIRE Server. Attests local workloads. Caches and rotates SVIDs. Exposes Workload API.
  - **Attestation flow**:
    1. Node attestation: SPIRE Agent proves its host identity to SPIRE Server via platform-specific attestors (AWS Instance Identity Document, GCP Instance Identity Token, Kubernetes node attestation, bare-metal TPM).
    2. Workload attestation: SPIRE Agent verifies the requesting process on the local node via workload attestors (Kubernetes pod labels, Docker container ID, Unix PID/UID/GID, systemd unit).
    3. SVID issuance: SPIRE Server issues a short-lived SVID (default 1 hour TTL) to the attested workload.
    4. Automatic rotation: SPIRE Agent re-attests and obtains new SVIDs before expiry.
  - **Federation**: SPIRE supports cross-trust-domain federation via trust bundle exchange. Workloads in trust domain A can authenticate to workloads in trust domain B using their SVIDs.
  - **Nested SPIRE**: Hierarchical SPIRE deployments for large organizations. Parent SPIRE Server attests child SPIRE Servers, which in turn attest local agents.
- **CNCF status**: Sandbox (2017) -> Incubating (2022) -> Graduated (2024).
- **Production adopters**: Bloomberg, ByteDance, Uber, Netflix, Square, Pinterest, HP, GitHub, TransferWise/Wise, Shopify.
- **OpenAM relevance**: OpenAM handles north-south (user-to-application) authentication. SPIFFE/SPIRE handles east-west (service-to-service) authentication. They are complementary:
  - OpenAM authenticates the user and issues an OAuth/OIDC token.
  - The API gateway (OpenIG, Kong) validates the user token for north-south requests.
  - SPIFFE/SPIRE provides mTLS identity for east-west service-to-service calls behind the gateway.
  - OpenAM's OAuth 2.0 client credentials grant is the traditional (pre-SPIFFE) approach for service authentication, but it relies on shared secrets and lacks SPIFFE's automatic rotation and attestation guarantees.

#### Service Mesh Identity (2017-present) `[ACTIVE]`

- **Istio** (2017-present): Uses SPIFFE IDs natively. Istiod (control plane) acts as a CA, issuing SPIFFE-compliant X.509 certificates to Envoy sidecar proxies. All service-to-service communication is automatically encrypted via mTLS with identity derived from Kubernetes service accounts mapped to SPIFFE IDs.
  - **AuthorizationPolicy**: Kubernetes CRD for fine-grained, identity-aware access control. Policies reference SPIFFE IDs (principals), HTTP methods, paths, headers, and request properties.
  - **PeerAuthentication**: Configures mTLS mode (STRICT, PERMISSIVE, DISABLE) at mesh, namespace, or workload level.
  - **RequestAuthentication**: Validates JWT tokens from external IdPs (OpenAM, Okta, Keycloak) at the sidecar proxy.
  - **Ambient mesh** (GA 2024): Replaces per-pod sidecar with per-node ztunnel (L4) + optional L7 waypoint proxies. Reduces resource overhead while maintaining mTLS identity.

- **Linkerd** (2017-present): Automatic mTLS between all meshed services. Identity based on Kubernetes ServiceAccount. Simpler than Istio but less extensible. Uses its own identity system (not SPIRE-based, but SPIFFE-compatible certificate format).

- **Consul Connect** (HashiCorp): Service mesh with mTLS and intention-based authorization. Supports both Kubernetes and VM workloads. Consul can use Vault PKI for certificate issuance.

#### Sigstore and Supply Chain Identity (2021-present) `[ACTIVE]`

- **Problem**: Software supply chain attacks (SolarWinds 2020, Codecov 2021, xz-utils 2024) exploit the trust placed in software artifacts. How do you verify that a container image, package, or binary was produced by the expected entity?
- **Sigstore** (Linux Foundation, 2021): Free, open-source toolchain for signing, verifying, and protecting software supply chains.
  - **Cosign**: Sign and verify container images and other OCI artifacts. Keyless signing using OIDC identity (sign with your GitHub, Google, or Microsoft identity).
  - **Fulcio**: Free code-signing CA. Issues short-lived certificates based on OIDC identity. Certificate contains the signer's OIDC identity (email, GitHub actions identity).
  - **Rekor**: Immutable transparency log of signing events. Provides non-repudiation: anyone can verify that a specific identity signed a specific artifact at a specific time.
- **Identity model**: Sigstore bridges human identity (OIDC IdP) and software identity (signed artifact). A developer authenticates via OIDC, Fulcio issues a short-lived signing certificate, and Rekor records the signing event.
- **Adoption**: Cosign is used by Kubernetes, Distroless images, Wolfi, Chainguard. GitHub Artifact Attestations (2024) use Sigstore under the hood.
- **OpenAM relevance**: OpenAM as an OIDC provider could theoretically serve as the identity source for Sigstore's Fulcio CA, enabling organizations to use their existing OpenAM identities for signing software artifacts. This is not currently implemented but is technically feasible via OIDC federation.

#### OpenPubkey (2023) `[EMERGING]`

- **Origin**: BastionZero (acquired by Cloudflare, 2024). Now a Linux Foundation project.
- **Concept**: Binds a public key to an OpenID Connect identity without modifying the OIDC provider. The client includes a public key commitment in the OIDC nonce; when the IdP returns the ID token with that nonce, the token cryptographically binds the user's identity to the public key. The user can then sign messages or authenticate using the private key, and verifiers can check the signature against the OIDC-bound public key.
- **Significance**: Enables OIDC-based identity for SSH, code signing, and other non-web protocols without requiring the IdP to issue custom certificates or tokens. Any standard OIDC provider works -- the protocol extension is client-side only.
- **Use case**: SSH authentication using OIDC identity (replace SSH keys with OIDC-bound certificates). Code signing using developer OIDC identity.
- **OpenAM relevance**: OpenAM as an OIDC provider would work with OpenPubkey without modification, since OpenPubkey operates at the client/nonce layer without IdP changes.

#### IETF WIMSE Working Group (2024-present) `[EMERGING]`

- **Charter**: Workload Identity in Multi-System Environments. IETF working group chartered in 2024 to standardize workload identity token formats and flows for multi-system, multi-cloud environments.
- **Scope**: Defines how workloads identify themselves and authenticate to other workloads across trust domains, cloud providers, and organizational boundaries.
- **Key drafts**:
  - Workload Identity Token (WIT): A standardized token format for workload identity, building on JWT.
  - Transaction Tokens for workloads: Carry workload identity context through multi-hop call chains.
  - Workload Identity Federation: Standardized OIDC-based federation between workload identity providers (SPIRE, cloud IAM, enterprise IdP).
- **Relation to SPIFFE**: WIMSE builds on SPIFFE concepts but aims for broader IETF standardization beyond the CNCF ecosystem.
- **OpenAM relevance**: If WIMSE standards are ratified, OpenAM could potentially issue workload identity tokens via its OAuth 2.0/OIDC infrastructure, bridging human IAM and machine IAM in a single platform. This would require implementing WIMSE token formats and attestation flows.

#### Non-Human Identity (NHI) Management (2024-present) `[EMERGING]`

- **Category emergence**: Analysts (Gartner, Forrester) and vendors are formalizing "non-human identity management" as a distinct security discipline, separate from but adjacent to traditional IAM and PAM.
- **Scale**: Large enterprises have 50:1 to 100:1 NHI-to-human ratios. Each microservice, container, serverless function, CI/CD pipeline, scheduled job, monitoring agent, and API integration has at least one identity. AI agents add another rapidly growing NHI category.
- **Problem taxonomy**:

| NHI Type | Identity Mechanism | Risk | Management Approach |
|----------|-------------------|------|-------------------|
| Service accounts (AD/LDAP) | Password or keytab | Long-lived, over-privileged, unmonitored | PAM (CyberArk, Vault), Silverfort monitoring |
| API keys | Static string | No expiry, no scope, frequently leaked | Rotation, short-lived tokens, Vault dynamic secrets |
| OAuth client credentials | client_secret | Shared secret, static | JWT client auth (RFC 7523), mTLS auth (RFC 8705) |
| Kubernetes service accounts | JWT token | Default token has broad API access | Bound service account tokens, RBAC scoping |
| Cloud IAM roles | Temporary STS credentials | Over-permissioned IAM policies | CIEM, permission boundaries, Access Analyzer |
| SSH keys | Asymmetric key pair | Long-lived, no expiry, difficult to rotate | SSH certificates (short-lived), Vault SSH engine |
| TLS certificates | X.509 | Expiry management, CA compromise | cert-manager, Venafi, ACME/Let's Encrypt |
| CI/CD tokens | Platform-specific (PAT, OIDC) | Over-scoped, stored in env vars | OIDC federation (GitHub Actions -> cloud IAM) |
| AI agent identity | Undefined (emerging) | Impersonation, uncontrolled actions | OAuth with agent-specific scopes (emerging) |

- **Vendor approaches**:
  - **CyberArk + Venafi** (2024): Combined PAM (credential vaulting, secrets management) with machine identity management (certificate lifecycle, code signing, SSH key management).
  - **Silverfort**: Discovers and monitors all service accounts in AD. Behavioral baselining of service account activity. MFA enforcement for service accounts (unique capability).
  - **Astrix Security** (2022): Purpose-built for NHI security. Discovers, monitors, and secures non-human identities (API keys, service accounts, OAuth tokens, IAM roles). Detects over-privileged, inactive, or compromised NHIs.
  - **Oasis Security** (2024): NHI security posture management. Lifecycle management for machine identities.
  - **HashiCorp Vault**: Dynamic secrets (short-lived database credentials, cloud IAM, PKI), AppRole authentication, Kubernetes auth method.
  - **SPIFFE/SPIRE**: Attestation-based workload identity (no static secrets).

- **OpenAM relevance**: OpenAM was designed for human identity. Its OAuth 2.0 client credentials grant handles basic M2M authentication, but it lacks:
  - Workload attestation (SPIFFE model)
  - Dynamic credential generation (Vault model)
  - Service account discovery and monitoring (Silverfort/Astrix model)
  - Certificate lifecycle management (Venafi/cert-manager model)
  - In a modern architecture, OpenAM authenticates humans; SPIFFE/Vault/cloud IAM handles machine identity; ITDR/Silverfort monitors both.

### Machine-to-Human Identity Ratio

| Era | Approximate Ratio (NHI:Human) | Primary NHI Types |
|-----|------------------------------|-------------------|
| Pre-2010 | 2:1 | Service accounts, scheduled jobs |
| 2010-2015 | 10:1 | + API keys, cloud IAM roles, SaaS integrations |
| 2015-2020 | 25:1 | + Container identities, CI/CD tokens, microservice accounts |
| 2020-2025 | 50:1 | + Serverless functions, IoT devices, ephemeral workloads |
| 2025-2030 (projected) | 100:1+ | + AI agents, autonomous systems, edge compute |

---

## Cross-Reference: Roadmaps 7-12 Shift Summary

| # | Domain | Origin | Then (Pre-2010) | Now (2024-2026) | Next (2027+) |
|---|--------|--------|-----------------|-----------------|--------------|
| 7 | API Security | HTTP Basic (1996) | Policy agents, API keys | OAuth + JWT at gateway, mTLS mesh, DPoP | Transaction tokens, API-first identity |
| 8 | PAM | su/sudo (1971) | Shared root passwords, manual rotation | Credential vaulting, JIT access, session recording | Zero standing privileges, ephemeral access |
| 9 | Deployment | WAR monolith (2003) | J2EE app servers, clustered WAR | K8s Operators, single-binary, SaaS, edge | Identity mesh, GitOps, Wasm components |
| 10 | Passwordless/MFA | Passwords (1961) | Password + SMS OTP + TOTP | Passkeys + WebAuthn + conditional UI | Continuous auth, behavioral biometrics |
| 11 | Zero Trust | Firewall perimeter (1988) | DMZ + VPN + network zones | NIST 800-207, ZTNA, identity as perimeter | Continuous verification, NHI zero trust |
| 12 | Machine Identity | Service accounts (1990s) | Static keys, shared passwords | SPIFFE/SPIRE, Vault dynamic secrets, cloud WIF | WIMSE standardization, NHI management |

---

## Roadmap 13: Identity Threat Detection & Response (ITDR)

Identity has become the primary attack vector. Verizon's Data Breach Investigations Report consistently shows that over 80% of breaches involve compromised credentials, privilege misuse, or identity-based lateral movement. ITDR emerged as a distinct discipline because traditional security tools -- firewalls, endpoint detection, SIEM -- were not designed to detect identity-layer attacks. A valid credential used from an unusual location, a service account suddenly accessing resources it has never touched, a burst of MFA push notifications at 3 AM -- these signals are invisible to network-layer security and require identity-specific detection logic.

### Timeline

**2000s: Log Aggregation and Manual Correlation** `[OBSOLETE]`

The earliest identity threat detection was ad hoc. Security teams exported authentication logs from LDAP servers, web access management systems (OpenSSO, SiteMinder, Tivoli Access Manager), and application servers into flat files or syslog collectors. Correlation was manual: an analyst reviewing logs might notice that a user authenticated from two continents within an hour, but only if they happened to be looking at the right log at the right time.

OpenAM (and its OpenSSO predecessor) generated authentication event logs from the JAAS chain execution. These logs recorded authentication module name, success/failure, timestamp, and client IP. In the Sun/ForgeRock era, these logs were written to flat files (`/openam/debug/` directory) or forwarded via JUL (Java Util Logging) handlers. No structured event format. No correlation ID. No behavioral baseline. The logs existed, but they were forensic artifacts, not detection signals.

**2005--2010: SIEM Emergence** `[LEGACY]`

Security Information and Event Management (SIEM) platforms -- ArcSight (2000, acquired by HP 2010, now OpenText), Splunk (2003), QRadar (2005, acquired by IBM 2011), LogRhythm (2003) -- centralized log collection and added rule-based correlation. A SIEM rule might trigger when: >10 failed logins from a single IP within 5 minutes, or a VPN login from country X followed by a badge swipe in country Y within 2 hours.

SIEM integration with IAM was typically one-directional: IAM systems shipped logs to the SIEM; the SIEM applied rules; analysts investigated alerts. There was no feedback loop -- a SIEM alert did not automatically trigger session revocation, MFA step-up, or account lockout in the IAM system. The response was manual: an analyst opened a ticket, contacted the user, and potentially disabled the account via the IAM admin console. Mean time to detect (MTTD) for identity-based attacks was measured in days or weeks.

**2012--2015: User and Entity Behavior Analytics (UEBA)** `[LEGACY]`

UEBA platforms -- Exabeam (2013), Securonix (2008, UEBA pivot ~2013), Splunk UBA (2015, via Caspida acquisition), Microsoft Advanced Threat Analytics (2015) -- applied machine learning to establish behavioral baselines for user and entity activity. Instead of static rules ("more than 10 failed logins"), UEBA built per-user models: this user normally logs in from San Francisco between 8 AM and 6 PM, accesses these 5 applications, and downloads less than 50 MB of data per day. Deviations from the baseline -- login from Moscow at 2 AM, access to a file server never previously used, 5 GB data exfiltration -- generated risk scores.

The UEBA approach was a significant advance over rule-based SIEM, but it suffered from high false-positive rates (a user traveling internationally would trigger "impossible travel" alerts constantly), long baseline periods (weeks to months before the model was useful), and lack of integration with the identity infrastructure. UEBA told you something suspicious happened; it did not tell you what to do about it in the IAM layer.

**2015--2018: Specialized Identity Threat Tools** `[ACTIVE]`

Several companies recognized that identity-layer threats required identity-specific detection:

- **Preempt Security** (2014, acquired by CrowdStrike 2020) -- Focused on Active Directory threat detection: Kerberoasting, DCSync, Pass-the-Hash, Golden Ticket forgery. Integrated at the domain controller level to inspect Kerberos ticket requests in real time.
- **Attivo Networks** (2011, acquired by SentinelOne 2022) -- Identity-centric deception: deployed decoy accounts, fake credentials, and honeypot directory entries to detect lateral movement. When an attacker enumerated Active Directory and attempted to use a decoy credential, Attivo detected the intrusion.
- **Illusive Networks** (2014, acquired by Proofpoint 2022) -- Deployed deceptive identity artifacts (cached credentials, browser sessions, SSH keys) on endpoints to detect attackers who harvested credentials from compromised machines.

These tools represented the first generation of purpose-built identity threat detection. They understood Active Directory's Kerberos implementation, LDAP query patterns, and credential caching mechanisms at a depth that generic SIEM/UEBA tools did not.

**2019--2020: Silverfort and Unified Identity Protection** `[ACTIVE]`

Silverfort (founded 2016, emerged ~2019) introduced a novel architectural approach: agent-less, proxy-less integration at the Active Directory domain controller and identity provider level. By intercepting authentication decisions at the directory layer itself, Silverfort could:

- Enforce MFA on any resource -- including legacy systems, file shares, RDP, SSH, and command-line tools that never supported MFA natively. The MFA prompt is injected at the authentication decision point, not at the application.
- Apply behavioral baselining to every authentication event, not just those flowing through a modern IdP.
- Detect and block lateral movement in real time by correlating authentication patterns across all directory services (AD, LDAP, RADIUS, cloud IdPs).

Silverfort's architecture was significant because it did not require changes to the protected applications, the directory servers, or the network infrastructure. It operated as a software layer on or near the domain controllers, intercepting NTLM, Kerberos, and LDAP authentication traffic.

**2020--2022: Cloud IdP Native Protection** `[ACTIVE]`

Cloud identity providers built detection capabilities directly into their platforms:

- **Microsoft Entra ID Protection** (evolved from Azure AD Identity Protection, 2019+) -- Risk-based conditional access policies that evaluate sign-in risk (unfamiliar location, anonymous IP, malware-linked IP, atypical travel, token anomalies) and user risk (leaked credentials detected in dark web scans, anomalous user activity) using ML models trained on signals from billions of authentications across the Microsoft ecosystem. Risk levels (low, medium, high) feed into Conditional Access policies that can require MFA, block access, or require password reset. `[ACTIVE]`
- **Okta Identity Threat Protection** (announced 2023, GA 2024) -- Continuous assessment of user sessions based on behavioral signals. Integrates with the Okta Identity Engine to enable real-time session revocation and step-up authentication when risk signals change mid-session. `[ACTIVE]`
- **Google Workspace Security** -- Context-aware access policies, BeyondCorp-derived. Device trust, location, and user behavior inform access decisions for Google Workspace and GCP resources. `[ACTIVE]`

**2022: ITDR Becomes a Category** `[ACTIVE]`

Gartner formally defined "Identity Threat Detection and Response" as a distinct security category in its 2022 Hype Cycle for Identity and Access Management. The definition: "ITDR encompasses tools and best practices to protect identity infrastructure from attacks. ITDR can discover and detect threats, assess posture, and recommend responses."

The category definition recognized that identity security required both a detection discipline (finding identity-based attacks in progress) and a posture management discipline (finding identity infrastructure weaknesses before they are exploited). This dual focus -- runtime detection plus proactive posture -- distinguished ITDR from UEBA (which was purely detective) and from IGA (which was governance-focused, not threat-focused).

**2022--2024: Market Consolidation and Integration** `[ACTIVE]`

The ITDR market consolidated rapidly through acquisitions:

| Acquisition | Year | Acquirer | Target | ITDR Capability Gained |
|-------------|------|----------|--------|----------------------|
| Preempt Security | 2020 | CrowdStrike | Preempt | AD threat detection (now Falcon Identity Threat Detection) |
| Attivo Networks | 2022 | SentinelOne | Attivo | Identity deception, AD assessment |
| Illusive Networks | 2022 | Proofpoint | Illusive | Deceptive identity artifacts |
| Rezonate | 2024 | Silverfort | Rezonate | Cloud identity posture |
| Authomize | 2024 | Delinea | Authomize | Cloud identity detection |

Standalone ITDR vendors remaining as of 2026:

- **Silverfort** -- Unified identity protection, AD-centric, agent-less MFA injection. Series D, $116M raised. `[ACTIVE]`
- **Semperis** -- Active Directory-specific: disaster recovery, change detection, attack path analysis for AD forests. `[ACTIVE]`
- **Oort** (acquired by Cisco 2023) -- Identity-centric threat detection for cloud IdPs. Now integrated into Cisco Identity Intelligence. `[ACTIVE]`
- **Vectra AI** -- Network Detection & Response (NDR) with identity-layer detection for Active Directory and Azure AD attacks. `[ACTIVE]`

**2023--2024: Identity Security Posture Management (ISPM)** `[EMERGING]`

ISPM emerged as the preventive complement to ITDR's detective function. Where ITDR detects attacks in progress, ISPM finds identity hygiene issues before exploitation:

- Stale accounts with active privileges
- Service accounts with excessive permissions and no rotation
- Dormant admin accounts
- Missing MFA on privileged accounts
- Misconfigured conditional access policies
- Orphaned OAuth application registrations with broad scopes
- Shadow admin accounts (users with privilege-equivalent permissions without the "admin" label)

Products: Silverfort Identity Security Posture, CrowdStrike Falcon Identity Protection (posture features), Microsoft Entra Permissions Management (CIEM + posture), Zilla Security. `[EMERGING]`

**2024--2025: OIDC Shared Signals Framework (SSF)** `[EMERGING]`

The OpenID Shared Signals Framework (formerly RISC -- Risk and Incident Sharing and Coordination -- plus CAEP -- Continuous Access Evaluation Protocol) standardizes real-time security event sharing between providers using Security Event Tokens (SETs, RFC 8417). Two sub-specifications:

- **CAEP (Continuous Access Evaluation Protocol)** -- Enables an IdP to notify relying parties of session-level risk changes: session revoked, compliance status changed, device posture changed, credential changed. The relying party can immediately terminate the user's session without waiting for token expiry.
- **RISC (Risk Incident Sharing and Coordination)** -- Enables an IdP to share account-level risk events: account compromised, account disabled, credential compromised, recovery activated.

SSF uses SET (Security Event Token, RFC 8417) as the event format and defines push-based and poll-based delivery mechanisms (RFC 8935, RFC 8936). Google, Microsoft, Apple, and Okta are early adopters. The specification enables a future where identity-based threats detected by one provider trigger protective actions across all relying parties in real time.

**2025--2026: AI-Powered Identity Threat Detection** `[EMERGING]`

LLM-powered security operations centers are beginning to process identity threat signals:

- Natural language querying of identity security events ("show me all service accounts that authenticated to production databases from non-production networks in the last 30 days")
- Automated investigation summaries for identity-based alerts
- LLM-generated remediation recommendations for identity posture findings
- Behavioral anomaly explanation ("this service account's authentication pattern changed because the deployment pipeline was modified to add a new microservice")

These capabilities are in early adoption at large enterprises. The risk is LLM hallucination in security contexts -- a false negative (the LLM dismissing a real attack as benign) could have catastrophic consequences.

### Attack Pattern Detection Matrix

| Attack Pattern | Detection Signal | ITDR Technique | OpenAM Relevance |
|---------------|-----------------|----------------|------------------|
| Credential stuffing | High-volume login failures from distributed IPs | Rate analysis, IP reputation, credential breach database correlation | OpenAM auth failure logs; no native breach database check |
| Password spraying | Low-volume failures across many accounts from few IPs | Cross-account failure correlation | OpenAM `LoginState` failure tracking; no cross-account correlation |
| Kerberoasting | Unusual TGS requests for service accounts with SPNs | Kerberos traffic analysis at DC level | Not applicable (OpenAM uses Kerberos for authentication, not as KDC) |
| Golden Ticket | TGT with anomalous lifetime, encryption type, or PAC data | Kerberos ticket inspection | Not applicable |
| MFA fatigue / push bombing | Repeated MFA push notifications without user-initiated login | Push notification rate analysis | OpenAM push auth module; no fatigue detection |
| Token theft / replay | Access token used from IP/device different from issuance | Token binding analysis, DPoP validation | OpenAM issues bearer tokens; no sender-constraint enforcement |
| Lateral movement | Sequential authentication across multiple systems in short timeframe | Cross-system authentication correlation | OpenAM CTS session data could theoretically feed this, but no native correlation |
| DCSync attack | Replication requests from non-DC sources | AD replication traffic monitoring | Not applicable (OpenDJ replication is separate from AD) |
| Impossible travel | Authentication from geographically distant locations within impossible timeframe | Geo-IP correlation across authentication events | OpenAM adaptive auth checks IP; no cross-event geo correlation |

### OpenAM/OIP Implementation Notes

OpenAM's relationship to ITDR is that of a data source, not a detection engine. OpenAM generates the authentication events, session lifecycle events, and policy evaluation events that ITDR tools consume. The OIP fork's audit module (`OpenAM/openam-audit/`) provides structured JSON event logging with correlation IDs, which is the prerequisite for ITDR integration. However, OpenAM does not include:

- Behavioral baselining of user authentication patterns
- Cross-session anomaly detection
- Automated risk scoring based on authentication metadata
- Real-time session revocation triggered by external risk signals (no SSF/CAEP consumer implementation)
- Identity posture assessment of its own configuration

The adaptive authentication module (`openam-auth-adaptive`) evaluates device fingerprint, IP range, and authentication history at login time, which is a primitive form of risk-based authentication. But it operates at the individual authentication event level, not across a behavioral baseline.

For organizations running OpenAM, ITDR is best implemented by forwarding OpenAM's audit logs to a SIEM or ITDR platform (Splunk, Sentinel, CrowdStrike Falcon) and building detection rules on the authentication event stream. The CTS (Core Token Service) data in OpenDJ -- which contains active session metadata -- could serve as a real-time data source for session anomaly detection, but no integration exists out of the box.

---

## Roadmap 14: Privacy, Consent & Regulatory Evolution

Privacy regulation has transformed identity systems from authentication gateways into consent engines. The question is no longer just "is this user who they claim to be?" but also "has this user consented to this specific use of their data, and can we prove it?"

### Timeline

**1973: US Fair Information Practice Principles (FIPPs)** `[LEGACY]`

The US Department of Health, Education, and Welfare published "Records, Computers and the Rights of Citizens," proposing five principles that would shape every subsequent privacy framework: notice, consent, access, accuracy, and security. These principles -- sometimes called the "Fair Information Practice Principles" -- were not legally binding but established the conceptual vocabulary for data privacy. The OECD Guidelines (below) codified them internationally.

**1980: OECD Privacy Guidelines** `[LEGACY]`

The Organisation for Economic Co-operation and Development published "Guidelines on the Protection of Privacy and Transborder Flows of Personal Data," establishing eight principles: Collection Limitation, Data Quality, Purpose Specification, Use Limitation, Security Safeguards, Openness, Individual Participation, and Accountability. These principles became the foundation for privacy legislation in 38 OECD member countries and influenced GDPR's design decades later.

The OECD Guidelines had no enforcement mechanism. They were voluntary recommendations to member governments. Their influence was structural rather than coercive -- they established the conceptual framework that every subsequent privacy regulation adapted.

**1995: EU Data Protection Directive 95/46/EC** `[OBSOLETE]`

The European Union's first comprehensive data protection law established the concept of "data controllers" and "data processors," required explicit consent for data processing, granted data subjects the right to access and correct their data, and restricted transborder data flows to countries with "adequate" protection levels. Superseded by GDPR in 2018 but its structural concepts (controller/processor distinction, adequacy decisions, supervisory authorities) persisted.

Impact on IAM: identity systems became subject to regulatory requirements for the first time. Directory services (LDAP servers) storing personal data were classified as data processing systems requiring registration with national data protection authorities.

**1998: US Children's Online Privacy Protection Act (COPPA)** `[ACTIVE]`

COPPA (15 U.S.C. 6501-6506) restricts collection of personal information from children under 13. Requires verifiable parental consent before data collection. Updated by the FTC in 2013 to cover social networking, mobile apps, and behavioral advertising. Relevant to IAM: identity systems serving consumer applications must implement age verification and parental consent flows.

**2002: W3C Platform for Privacy Preferences (P3P)** `[OBSOLETE]`

P3P (W3C Recommendation, April 2002) was an XML-based protocol that allowed websites to declare their privacy practices in a machine-readable format. Browsers could automatically compare a site's P3P policy against the user's privacy preferences and warn or block accordingly.

P3P failed for multiple reasons: complex XML schema, no enforcement mechanism, websites declaring policies they did not follow, and Microsoft Internet Explorer's simplified implementation (compact policies in HTTP headers) that became the de facto standard while gutting the protocol's expressiveness. By 2010, P3P was effectively dead. The lesson: machine-readable privacy policies require enforcement, not just declaration.

**2003: HIPAA Security Rule** `[ACTIVE]`

The Health Insurance Portability and Accountability Act Security Rule (45 CFR Part 164, Subpart C) established minimum security standards for protected health information (PHI). Relevant to IAM: requires unique user identification, automatic logoff, audit controls, entity authentication, and transmission security for any system handling PHI. OpenAM deployments in healthcare must implement session timeouts, strong authentication, and comprehensive audit logging to meet HIPAA requirements. The OIP fork's audit module (`openam-audit`) provides the structured logging required for HIPAA compliance.

**2004: PCI DSS v1.0** `[ACTIVE]`

The Payment Card Industry Data Security Standard, developed by Visa, Mastercard, American Express, Discover, and JCB, established requirements for systems handling cardholder data. IAM-relevant requirements include: unique user IDs (Requirement 8), access control (Requirement 7), authentication factors (Requirement 8.3), session timeout (Requirement 8.1.8), and audit trail (Requirement 10). PCI DSS has been updated through v4.0.1 (June 2024), which requires multi-factor authentication for all access to the cardholder data environment (not just remote access) and phishing-resistant authentication where feasible.

**2017: Kantara Initiative Consent Receipt Specification v1.0** `[LEGACY]`

The Kantara Initiative developed the Consent Receipt specification -- a machine-readable record of consent that captures: data subject identity, data controller identity, purposes of processing, categories of personal data, consent timestamp, and withdrawal mechanism. The specification aimed to make consent portable and verifiable across service boundaries.

The concept influenced GDPR's consent requirements and modern consent management platforms, but the specific Kantara specification saw limited adoption. The idea of a structured, portable consent record -- essentially a "receipt" that proves consent was given -- has been absorbed into broader consent management architectures.

**2012: Do Not Track (DNT)** `[OBSOLETE]`

The W3C Tracking Protection Working Group developed the DNT HTTP header (value: `1`) to signal user preference against tracking. Browser vendors implemented the header; websites overwhelmingly ignored it. The Working Group closed in 2019 without achieving consensus on enforcement. Apple's Safari removed DNT support in 2019. The failure of DNT demonstrated that voluntary, unenforced privacy signals do not work -- a lesson that motivated GDPR's mandatory, enforceable consent requirements.

**2015: UMA 1.0 (User-Managed Access)** `[LEGACY]`

UMA 1.0 (Kantara Initiative, 2015) extended OAuth 2.0 to enable user-driven authorization -- the resource owner could set policies governing who could access their data, under what conditions, for what purposes. The "requesting party" (the person or system requesting access) was distinct from the "resource owner" (the person who owned the data), enabling Alice to grant Bob access to specific resources without involving the resource server's administrator.

OpenAM implemented UMA 1.0 support in the ForgeRock 13.0.0 era. The OIP fork maintains this implementation (`openam-uma/` module), making OpenAM one of the few open-source platforms with UMA support.

**2018: UMA 2.0** `[ACTIVE]`

UMA 2.0 (Kantara Initiative, 2018) simplified the protocol by aligning more closely with standard OAuth 2.0 grant types. Key changes: the UMA grant type replaced the custom authorization API, permission tickets became standard OAuth parameters, and the claims-gathering process was streamlined. UMA 2.0 positioned itself as a consent protocol -- the resource owner defines sharing policies, and the authorization server enforces them.

OpenAM/OIP: UMA 2.0 support is present in the OIP fork. The `openam-uma` module implements the resource server, authorization server, and policy management APIs. See [Chapter 4: Authorization Frameworks](04-authorization-frameworks.md) for protocol details.

**2018: GDPR (General Data Protection Regulation)** `[ACTIVE]`

Regulation (EU) 2016/679, effective May 25, 2018, transformed privacy from a best-practice recommendation to an enforceable legal obligation with severe penalties (up to 4% of global annual turnover or EUR 20 million, whichever is greater). Key IAM-impacting provisions:

| GDPR Article | IAM Requirement | OpenAM/OIP Implementation |
|--------------|-----------------|--------------------------|
| Art. 5 (Purpose limitation) | Consent must be specific to stated purposes | OpenAM consent module (per-scope consent in OAuth 2.0 flows) |
| Art. 6 (Lawful basis) | At least one lawful basis for processing | IAM must record which basis applies per data processing activity |
| Art. 7 (Conditions for consent) | Consent must be freely given, specific, informed, unambiguous | OAuth consent screen in OpenAM; no granular per-attribute consent |
| Art. 15 (Right of access) | Data subjects can request copies of their data | OpenDJ LDAP search by authenticated user; no self-service DSAR portal |
| Art. 17 (Right to erasure) | "Right to be forgotten" -- deletion on request | OpenIDM deprovisioning workflows; OpenDJ entry deletion |
| Art. 20 (Data portability) | Export personal data in machine-readable format | No native OpenAM/OIP data export API; SCIM could serve this role |
| Art. 25 (Data protection by design) | Privacy-preserving defaults | OpenAM's default consent screen; minimal by default |
| Art. 30 (Records of processing) | Maintain records of data processing activities | OpenAM audit module provides authentication/authorization logs |
| Art. 33 (Breach notification) | Notify supervisory authority within 72 hours | No native breach detection; depends on ITDR integration |
| Art. 35 (DPIA) | Data Protection Impact Assessment for high-risk processing | No tooling; organizational process |

GDPR's impact on IAM architecture was structural: identity systems could no longer treat user data as an internal implementation detail. Every piece of personal data in OpenDJ -- name, email, phone number, IP address, authentication history -- became subject to regulatory obligations around consent, access, portability, and deletion.

**2020: California Consumer Privacy Act (CCPA) / 2023: California Privacy Rights Act (CPRA)** `[ACTIVE]`

CCPA (effective January 1, 2020) and its successor CPRA (effective January 1, 2023) granted California residents the right to know what data is collected, the right to delete it, the right to opt out of its sale, and (under CPRA) the right to correct inaccurate data. CPRA created the California Privacy Protection Agency (CPPA) as a dedicated enforcement body and introduced the concept of "sensitive personal information" requiring additional protections.

CCPA/CPRA applies to businesses meeting revenue or data volume thresholds. For IAM: the "Do Not Sell My Personal Information" requirement means identity systems must support opt-out signals, and the data deletion right means OpenDJ/OpenIDM must support complete erasure of a user's identity records -- not just account deactivation but data destruction.

**2021: Global Privacy Control (GPC)** `[EMERGING]`

GPC is an HTTP header (`Sec-GPC: 1`) that signals a user's intent to opt out of data sale and sharing. Unlike DNT, GPC has legal backing: CCPA/CPRA and Colorado Privacy Act recognize GPC as a valid opt-out mechanism. Browsers that support GPC include Firefox, Brave, and DuckDuckGo. Chrome does not natively support it but extensions are available.

GPC's significance for IAM: identity systems receiving requests with `Sec-GPC: 1` must treat those requests as opt-out signals and restrict data processing accordingly. No OpenAM/OIP module processes GPC headers, but the OpenIG gateway could be configured to intercept and act on them.

**2021--2025: Global Privacy Regulation Proliferation** `[ACTIVE]`

Privacy regulation has become global:

| Regulation | Jurisdiction | Effective | Key Provisions |
|-----------|-------------|-----------|----------------|
| LGPD | Brazil | 2020 | GDPR-like; ANPD enforcement |
| POPIA | South Africa | 2021 | GDPR-like; Information Regulator |
| PIPL | China | 2021 | Consent required; data localization; cross-border transfer restrictions |
| Federal Law 242-FZ | Russia | 2015 | Personal data of Russian citizens must be stored on servers in Russia |
| PDPA | Thailand | 2022 | GDPR-modeled; consent-based |
| DPDPA | India | 2023 | Consent-based; data fiduciary concept; cross-border transfers via whitelist |
| PIPA | South Korea | 2011, amended 2023 | Strong consent requirements; pseudonymization provisions |
| Bill C-27 / CPPA | Canada | Expected 2025-2026 | Replacing PIPEDA; algorithmic transparency; interoperability with GDPR |
| US state laws | Colorado, Connecticut, Virginia, Utah, Montana, Oregon, Texas, others | 2023--2025 | Patchwork of CCPA-like state laws; no federal privacy law |

For IAM: organizations operating globally must implement consent management, data residency controls, and data subject rights across multiple jurisdictions with potentially conflicting requirements. China's PIPL requires data localization; GDPR requires adequate protections for cross-border transfers; India's DPDPA uses a government whitelist for permitted cross-border destinations. Identity systems -- OpenDJ in particular, as the persistent identity store -- must support regional data partitioning, jurisdiction-specific retention policies, and cross-border transfer restrictions.

**2023: ISO 31700 (Privacy by Design)** `[EMERGING]`

ISO 31700-1:2023 established international standards for privacy by design, operationalizing the concept that Ann Cavoukian introduced in the 1990s. The standard provides requirements for embedding privacy considerations into product and service design from the outset -- not as a retrofit. For IAM: identity systems should collect minimal data by default, support consent at the most granular level, implement data minimization in token claims, and default to privacy-protective configurations.

**2024: EU AI Act (Identity Implications)** `[EMERGING]`

The EU AI Act (Regulation (EU) 2024/1689) classifies AI systems into risk tiers. High-risk AI systems that process biometric data for identification are subject to strict requirements: transparency, human oversight, accuracy, robustness, and cybersecurity. Real-time remote biometric identification in public spaces is prohibited except for specific law enforcement purposes.

For IAM: behavioral biometrics (keystroke dynamics, mouse movement patterns) used for continuous authentication may be classified as biometric identification systems under the AI Act, triggering high-risk requirements including conformity assessments, registration in the EU database, and ongoing monitoring obligations. IAM vendors using ML for adaptive authentication must evaluate their compliance obligations under the AI Act's risk classification framework.

**2024: EU eIDAS 2.0 and Age Verification** `[EMERGING]`

Regulation (EU) 2024/1183 amending eIDAS established the European Digital Identity Wallet (EUDIW), which every EU member state must offer to citizens by 2026. The wallet enables selective disclosure of identity attributes -- a citizen can prove they are over 18 without revealing their exact birthdate, or prove their nationality without revealing their name. The technical architecture uses OID4VP (OpenID for Verifiable Presentations) for credential exchange and SD-JWT VC (Selective Disclosure JWT Verifiable Credentials) as the credential format.

Age verification regulations are proliferating: the EU Digital Services Act requires age verification for harmful content; the UK Online Safety Act requires age verification for pornographic content; US states (Louisiana, Virginia, Utah, Texas) require age verification for adult content. These regulations create new IAM requirements: privacy-preserving age verification that confirms age without disclosing exact birthdate or identity. Zero-knowledge proofs and selective disclosure credentials address this technically, but adoption is nascent.

**2025--2026: Consent-as-Code and Privacy Engineering** `[EMERGING]`

The emerging paradigm treats consent as a first-class engineering artifact:

- **Consent Management Platforms (CMPs)** -- OneTrust, Cookiebot, TrustArc, Osano provide UI-based consent collection and preference management. These platforms integrate with IAM systems to enforce consent-based access controls.
- **Consent receipts** -- Machine-readable records of consent that can be verified, audited, and revoked. W3C Data Privacy Vocabulary (DPV) provides vocabulary for expressing consent purposes, legal bases, and processing activities.
- **Privacy-preserving identity** -- Zero-knowledge proofs (ZKPs) enable proving attributes ("I am over 18," "I am a resident of the EU") without revealing the underlying data. ZK-SNARKs and ZK-STARKs are mathematically proven but computationally expensive; more practical approaches include SD-JWT (selective disclosure via salted hash comparison) and BBS+ signatures (enabling efficient selective disclosure from signed credential sets).
- **Purpose-bound data access** -- IAM policies that restrict data access not just by role or attribute, but by the stated purpose of access. A customer service agent can access a user's email address for support purposes but not for marketing purposes, and the IAM system enforces this distinction.

### OpenAM/OIP Implementation Notes

OpenAM's consent capabilities are limited to the OAuth 2.0 consent screen -- when a user authorizes a relying party, OpenAM displays requested scopes and records the user's approval. This is per-scope, per-client consent. It does not support:

- Granular per-attribute consent ("I consent to sharing my email but not my phone number")
- Purpose-bound consent ("I consent to this data use for support but not marketing")
- Consent withdrawal with downstream enforcement (revoking consent should trigger deprovisioning in downstream systems via OpenIDM)
- DSAR automation (no self-service data access request portal)
- GPC header processing
- Age verification flows
- Selective disclosure of identity attributes

For organizations subject to GDPR/CCPA/PIPL, OpenAM provides the authentication and authorization infrastructure, but consent management requires either a dedicated CMP (OneTrust, TrustArc) or custom development on top of OpenAM's OAuth consent screen and OpenIDM's workflow engine.

---

## Roadmap 15: Decentralized & Self-Sovereign Identity

Decentralized identity challenges the foundational assumption of every IAM system described in this research: that a centralized identity provider is the root of all trust. In the decentralized model, the individual -- not the IdP -- controls their identity credentials. The issuer attests to facts; the holder stores and presents credentials; the verifier validates cryptographic proofs without contacting the issuer. No central database. No single point of compromise. No vendor lock-in.

The vision is compelling. The reality is more complicated.

### Timeline

**1991: PGP Web of Trust** `[LEGACY]`

Phil Zimmermann's Pretty Good Privacy (PGP) introduced the "web of trust" model for public key authentication. Instead of a centralized certificate authority, users signed each other's public keys, creating a decentralized trust graph. If Alice signed Bob's key, and Charlie trusted Alice, then Charlie could transitively trust Bob's key.

The web of trust failed at scale for several reasons: key management was too complex for average users, the transitive trust model did not map to real-world trust relationships (Alice trusting Bob's identity does not mean Alice vouches for Bob's judgment about Charlie), and key revocation was unreliable. PGP itself remains in use for email encryption among security professionals, but the web of trust model has been largely abandoned in favor of Key Transparency (Google) and Autocrypt approaches. `[LEGACY]` for PGP encryption; `[OBSOLETE]` for the web of trust model.

**2005--2010: User-Centric Identity Movement** `[OBSOLETE]`

The user-centric identity movement -- driven by Kim Cameron's "Seven Laws of Identity" (Microsoft, 2005), the Identity Commons, and the Internet Identity Workshop (IIW, first held 2005) -- argued that users should control their own identity information. Cameron's laws included: user control and consent, minimal disclosure for a constrained use, justifiable parties, directed identity, pluralism of operators and technologies, human integration, and consistent experience across contexts.

These principles influenced OpenID 1.0/2.0 (2006--2007) `[OBSOLETE]`, which allowed users to authenticate using a URL they controlled. OpenID 2.0 failed commercially (poor UX, phishing susceptibility, no business model for identity providers) but seeded ideas that evolved into OpenID Connect and, later, decentralized identity.

**2016: Sovrin Foundation and Hyperledger Indy** `[LEGACY]`

The Sovrin Foundation (2016) launched the first blockchain-based decentralized identity network, built on the Hyperledger Indy codebase. The architecture: a permissioned distributed ledger (Sovrin Network) stored DID Documents and credential schemas; credential issuance and verification happened off-ledger using zero-knowledge proofs (Camenisch-Lysyanskaya signatures, implemented as Hyperledger Ursa/AnonCreds).

Sovrin demonstrated that decentralized identity was technically feasible at scale. The network launched in 2017 with a governance framework, 25 steward organizations running validator nodes, and integration with the Hyperledger Aries agent framework for credential exchange.

However, Sovrin struggled with sustainability (the foundation filed for reorganization in 2022), the blockchain dependency created regulatory concerns (immutable personal data on a ledger), and the AnonCreds zero-knowledge proof format was not interoperable with W3C VC standards. The project's influence was primarily conceptual -- it proved the model and trained a generation of decentralized identity engineers. `[LEGACY]`

**2017--2019: W3C DID and VC Specifications Begin** `[ACTIVE]`

The W3C Verifiable Credentials Working Group published the VC Data Model 1.0 as a W3C Recommendation in November 2019. Simultaneously, the W3C DID Working Group developed the Decentralized Identifiers (DIDs) specification.

Key concepts:

- **Verifiable Credential (VC):** A tamper-evident credential with cryptographic proof of authorship. Contains claims (attribute-value pairs), issuer identity, issuance/expiration dates, and cryptographic proof.
- **Decentralized Identifier (DID):** A URI (`did:method:identifier`) that resolves to a DID Document containing public keys and service endpoints, without relying on a centralized registry.
- **Verifiable Presentation (VP):** A container for one or more VCs, itself signed by the holder, enabling selective disclosure to a verifier.

**2019: W3C VC Data Model 1.0** `[ACTIVE]`

The first W3C Recommendation for Verifiable Credentials. Defined the data model, proof formats (JSON-LD with Linked Data Proofs, or JWT), and the issuer-holder-verifier trust triangle. Implementations appeared in multiple languages (JavaScript/TypeScript: Spruce, Digital Bazaar; Java: walt.id; Go: TrustBloc; Rust: SpruceID).

**2020--2022: DID Method Proliferation** `[ACTIVE]`

Over 150 DID methods were registered in the W3C DID Method Registry, but practical adoption concentrated on a few:

| DID Method | Anchor | Key Properties | Status |
|-----------|--------|---------------|--------|
| `did:web` | DNS/HTTPS | No blockchain; host DID Document at `https://domain/.well-known/did.json` | `[ACTIVE]` |
| `did:key` | Self-contained | Ephemeral; DID encodes the public key directly | `[ACTIVE]` |
| `did:jwk` | Self-contained | JWK-based; simple key representation | `[ACTIVE]` |
| `did:ion` | Bitcoin | Microsoft ION network; Sidetree protocol | `[LEGACY]` (Microsoft deprioritized) |
| `did:ethr` | Ethereum | ERC-1056 Ethereum identity | `[LEGACY]` |
| `did:sov` | Sovrin/Indy | Permissioned ledger | `[LEGACY]` |
| `did:peer` | Peer-to-peer | No anchor; direct exchange between parties | `[EMERGING]` |
| `did:tdw` | Trust over DNS | Verifiable history via DNS TXT records; proposed IETF spec | `[EMERGING]` |

The trend is away from blockchain-anchored DIDs and toward DNS/web-based approaches (`did:web`, `did:tdw`) that leverage existing internet infrastructure. The EU eIDAS 2.0 Architecture Reference Framework deliberately avoids mandating blockchain.

**2022: W3C DID Core 1.0 Recommendation** `[ACTIVE]`

W3C DID Core 1.0 became a W3C Recommendation on July 19, 2022, despite formal objections from Google and Mozilla (who argued that blockchain-based DID methods did not meet W3C's standards for decentralization and interoperability). The specification defines the DID syntax, DID Document data model, resolution process, and requirements for DID methods.

**2022: Passkey-Credential Convergence** `[EMERGING]`

Passkeys (FIDO2 synced credentials, see [Chapter 12: Modern Architecture](12-modern-architecture.md), section 7) and verifiable credentials share a conceptual model: both are cryptographic credentials stored in a user-controlled wallet, both use asymmetric key pairs, and both are bound to specific relying parties. The convergence is not yet realized in standards, but the architectural similarity suggests a future where a single wallet manages both authentication credentials (passkeys) and identity credentials (VCs).

**2022--2023: OpenID for Verifiable Credentials (OID4VC)** `[EMERGING]`

The OpenID Foundation developed a suite of specifications bridging the established OIDC ecosystem with verifiable credentials:

- **OID4VCI (OpenID for Verifiable Credential Issuance):** Defines how an authorization server (issuer) issues VCs to a wallet (holder) using OAuth 2.0 authorization code or pre-authorized code flows. The wallet requests a credential, authenticates to the issuer, and receives a signed VC.
- **OID4VP (OpenID for Verifiable Presentations):** Defines how a verifier requests and receives VCs from a wallet. The verifier sends a presentation request (specifying required credential types and claims); the wallet selects matching credentials, creates a VP, and returns it.
- **SIOPv2 (Self-Issued OpenID Provider v2):** The user's wallet acts as its own IdP, issuing self-signed ID tokens. This enables authentication without a centralized IdP -- the wallet proves control of a DID and presents VCs as authentication evidence.

OID4VC is the critical bridge specification because it allows existing OIDC-based IAM systems (including OpenAM, Keycloak, Okta, Entra ID) to issue and consume verifiable credentials without replacing their entire architecture.

**2023--2024: SD-JWT VC (Selective Disclosure JWT Verifiable Credentials)** `[EMERGING]`

SD-JWT (IETF draft-ietf-oauth-selective-disclosure-jwt) enables selective disclosure of JWT claims. Instead of revealing all claims in a JWT, the holder can selectively disclose individual claims to the verifier while proving that the undisclosed claims exist and were signed by the issuer.

Mechanism: the issuer creates a JWT with claims replaced by salted hashes. The holder can reveal individual claims by providing the salt and original value, which the verifier can verify against the hash in the JWT. Claims not revealed remain hidden but their presence is attested by the issuer's signature over the complete hash set.

SD-JWT VC (IETF draft-ietf-oauth-sd-jwt-vc) combines SD-JWT with the VC Data Model, producing verifiable credentials that support selective disclosure without zero-knowledge proofs. This is the credential format chosen by the EU eIDAS 2.0 Architecture Reference Framework for European Digital Identity Wallets.

**2024: EU eIDAS 2.0 and the European Digital Identity Wallet** `[EMERGING]`

Regulation (EU) 2024/1183 mandates that every EU member state must offer a European Digital Identity Wallet (EUDIW) to citizens by 2026. The wallet will store:

- National identity credentials (equivalent to national ID card)
- Mobile driver's licenses (ISO 18013-5 mDL)
- Professional qualifications
- Educational credentials (EU Digital Credentials for Learning)
- Health credentials
- Age verification attestations

The Architecture Reference Framework (ARF) specifies:

- **Credential format:** SD-JWT VC (primary) and ISO 18013-5 mdoc (for mDL)
- **Issuance protocol:** OID4VCI
- **Presentation protocol:** OID4VP
- **Trust framework:** OIDC Federation for automated trust chain validation
- **DID methods:** Not mandated; `did:web` and `did:key` supported; blockchain not required
- **Revocation:** Token Status List (bitstring)
- **Wallet attestation:** Device binding, wallet integrity attestation

This is the largest regulatory forcing function for decentralized identity adoption in history. 450 million EU citizens will have access to a digital identity wallet with legal equivalence to physical ID documents.

**2024: Mobile Driver's Licenses (mDL, ISO 18013-5)** `[EMERGING]`

ISO 18013-5 defines the standard for mobile driver's licenses, with implementations in production in several US states (Louisiana, Colorado, California, Arizona, Utah, Iowa) and Australia. The mDL uses NFC or QR+BLE for presentation, supports selective disclosure (present age without revealing birthdate or address), and stores the credential in a device-bound secure enclave.

Apple Wallet and Google Wallet both support mDL storage. TSA accepts mDL at 25+ US airports as of 2025. The mDL represents the first mainstream adoption of verifiable credential concepts, even though it uses the ISO standard rather than the W3C VC format.

**2025--2026: Current State and Trajectories** `[EMERGING]`

| Segment | Status | Key Developments |
|---------|--------|-----------------|
| Government digital ID | Production pilots, regulatory mandates | EU EUDIW (2026 mandate), US mDL (25+ states), Bhutan National Digital Identity |
| Enterprise credentials | Early exploration | Employee credential verification (MATTR, Dock), supply chain attestation |
| Consumer | Limited but growing | Google Wallet, Apple Wallet credential storage; limited verifier adoption |
| Interoperability | Pre-standardization | OID4VC interoperability profiles, SD-JWT VC standardization |
| Blockchain-based SSI | Declining | Sovrin restructured; most enterprise deployments moved to non-blockchain approaches |

### The Promise vs. Reality Assessment

| Claim | Reality (2026) |
|-------|---------------|
| "Users will control their own identity" | Partially true: users can store credentials in wallets, but issuers still determine what credentials exist and verifiers still determine what credentials they accept. Control is bounded by the trust framework. |
| "No more centralized IdPs" | False for enterprise: centralized IdPs (Okta, Entra ID, Keycloak, OpenAM) will coexist with VCs for the foreseeable future. VCs add credential portability, not IdP elimination. |
| "Blockchain-based decentralization" | Declining: the industry has moved toward `did:web` and DNS-based trust anchors. EU eIDAS 2.0 does not require blockchain. |
| "Privacy through selective disclosure" | Technically viable (SD-JWT VC, BBS+ signatures) but limited deployment. EU EUDIW will be the first large-scale test. |
| "Interoperability across wallets and verifiers" | Not yet: multiple credential formats (SD-JWT VC, mdoc, AnonCreds, JSON-LD VC), multiple presentation protocols (OID4VP, ISO 18013-5), and multiple trust frameworks create fragmentation. |

### OpenAM/OIP Implementation Notes

OpenAM does not implement W3C Verifiable Credentials, DIDs, OID4VC, or SD-JWT. The architecture is fundamentally centralized-IdP-based: OpenAM issues SAML assertions or OIDC ID tokens as a centralized authority, and relying parties trust OpenAM's assertions because they trust OpenAM.

Potential integration paths:

- **OpenAM as VC issuer:** OpenAM could issue VCs to authenticated users, leveraging its existing authentication chain (34+ modules) for identity proofing before credential issuance. This would require implementing the OID4VCI specification, which is OAuth 2.0-based and thus compatible with OpenAM's existing OAuth 2.0 provider.
- **OpenAM as VC verifier:** OpenAM could accept VP presentations as authentication evidence, similar to how it accepts SAML assertions from external IdPs. This would require implementing OID4VP as a new authentication module.
- **OpenDJ as DID resolver:** OpenDJ could store DID Documents as LDAP entries, providing a directory-based DID method (`did:ldap`?). This is speculative.

None of these integration paths exist today. For organizations deploying OpenAM that need VC capabilities, the recommended approach is to deploy a separate VC platform (walt.id, MATTR, Sphereon) alongside OpenAM, using OIDC as the bridge between the centralized IAM world and the decentralized credential world.

---

## Roadmap 16: Open-Source Identity Platform Evolution

This roadmap traces the evolution of open-source identity platforms from Sun Microsystems' first open-source commit in 2006 through the current landscape of 2026. The story is one of fragmentation, community resilience, and an expanding ecosystem that has grown from a single corporate-sponsored project to a diverse field of competing architectures and philosophies. For deeper analysis of the ForgeRock/OIP/Wren lineage specifically, see [Chapter 1: Historical Narrative](01-history.md).

### Timeline

**2003--2005: Sun Java System Identity Server and Sun Access Manager** `[OBSOLETE]`

Sun Microsystems shipped commercial identity products derived from Netscape's iPlanet platform. Sun Directory Server (commercial LDAPv3), Sun Identity Manager (provisioning), and Sun Access Manager (SSO, policy enforcement) formed the "Identity Management Suite." These products were proprietary and expensive.

**2005--2006: Project Lightbulb and OpenSSO** `[OBSOLETE]`

Sun open-sourced Access Manager as OpenSSO (Open Web Single Sign-On) under the CDDL license in October 2005. The code was hosted on `opensso.dev.java.net`. OpenSSO 1.0 shipped in 2006; version 8.0 (2008) added OAuth 1.0, OpenID 1.1, and SAML 2.0 support.

Simultaneously, Sun open-sourced its next-generation LDAP server as OpenDS (Open Directory Server) on June 28, 2006 -- the first commit of what would become OpenDJ, and the oldest codebase in this entire research corpus (24,107 commits over 19.6 years as of February 2026).

**2004: CAS (Central Authentication Service, Yale 2001, Jasig 2004)** `[LEGACY]`

CAS, originally developed at Yale University and later maintained by Apereo (formerly Jasig), provided SSO for web applications, particularly in higher education. CAS protocol is simple (ticket-based, XML or JSON validation) and widely deployed at universities. CAS 6.x/7.x (2023+) supports OIDC, SAML 2.0, OAuth 2.0, and MFA, but its primary user base remains academic. `[LEGACY]` -- still deployed widely in education but not gaining share in enterprise.

**2009: Gluu Server** `[LEGACY]`

Gluu (founded 2009) built an identity platform around the open-source oxAuth (OAuth/OIDC provider) and oxTrust (admin UI) components, integrating LDAP (OpenDJ or OpenLDAP), SCIM, and FIDO2. Gluu 5.x (2023, rewritten as "Janssen") moved to a cloud-native architecture with Kubernetes support. `[LEGACY]` -- Gluu/Janssen has a small but committed user base; overtaken by Keycloak in market share.

**2010: Oracle Acquisition and OpenSSO Abandonment** `[OBSOLETE]`

Oracle acquired Sun Microsystems for $7.4 billion (closed January 27, 2010). Oracle had no interest in open-source IAM -- it had Oracle Access Manager (OAM), Oracle Identity Manager (OIM), and Oracle Internet Directory (OID). OpenSSO, OpenDS, and nascent OpenIDM efforts were abandoned. See [Chapter 1](01-history.md) for the complete narrative.

**2010--2011: ForgeRock Founded** `[OBSOLETE]` (the company's open-source era)

Lasse Andresen, Jonathan Scudder, Hermann Svoren, and others left Sun/Oracle and incorporated ForgeRock AS in Norway (2010). They rescued the OpenSSO and OpenDS codebases from `java.net` and began the rebranding: OpenSSO to OpenAM, OpenDS to OpenDJ, and new projects OpenIDM, OpenIG, and OpenICF.

**2012--2016: ForgeRock Open-Source Golden Age** `[OBSOLETE]` (as an open-source effort)

Combined commit output: 5,376 (2012), 8,034 (2013), 10,744 (2014), 9,947 (2015), 6,631 (2016). Five to eight full-time engineers committing daily. Major releases: OpenAM 11.0.0 (Nov 2013), OpenAM 12.0.0 (Mar 2014), OpenAM 13.0.0 (Jan 2016). This era produced the codebase that both OIP and Wren still maintain.

Peak release: OpenAM 13.0.0 with OIDC Provider, SCIM 2.0 endpoints, UMA 1.0, adaptive authentication, and scripted authentication.

**2014: Keycloak 1.0** `[ACTIVE]`

Red Hat released Keycloak 1.0 in September 2014. Written in Java, initially on WildFly, Keycloak provided OIDC, SAML 2.0, social login, and user federation. Keycloak's timing was perfect: it launched while ForgeRock was still open-source, offering a GPL-friendly alternative (Apache 2.0 license) without ForgeRock's CDDL encumbrance.

Keycloak's advantages over ForgeRock OpenAM:

- Apache 2.0 license (vs. CDDL -- no GPL compatibility issues)
- Red Hat engineering backing (~20 full-time engineers)
- Modern admin UI (first GWT-based, then React from v22)
- Simpler deployment (standalone JAR, not WAR + servlet container + LDAP)
- Growing community (1,100+ contributors by 2026)

**November 2016: ForgeRock Source Closure** `[OBSOLETE]` (as a pivotal event)

ForgeRock closed its source code in November 2016 (the $88M Series D came later, September 2017). The last open tags: OpenAM 14.0.0-M2 (November 1, 2016), OpenDJ 4.0.0-M1 (September 30, 2016). Combined commits dropped from 6,631 (2016) to 401 (2017) -- a 94% decline. See [Chapter 1](01-history.md) for the full analysis, including the CDDL license dynamics that enabled community forks.

**2017: Open Identity Platform (OIP) Fork** `[ACTIVE]`

3A Systems, LLC (Moscow), led by Valery Kharseko, forked the ForgeRock repositories and released OpenAM 14.0.0 in February 2018. As of February 2026: 81 OpenAM releases, 82 OpenDJ releases, synchronized release waves across the full suite (OpenAM 16.0.5, OpenDJ 5.0.3, OpenIDM 7.0.2, OpenIG 6.0.2, OpenICF 2.0.2). Monthly release cadence, reactive CVE patching, and the broadest authentication module inventory of any open-source IAM platform (34+ modules).

**2017: Ory Hydra** `[ACTIVE]`

Ory GmbH (Germany) released Hydra, a certified OIDC provider written in Go. Unlike monolithic IAM platforms, Ory decomposed identity into four independent microservices:

| Component | Function | Analog |
|-----------|----------|--------|
| Hydra | OAuth 2.0 / OIDC provider | OpenAM OAuth2 module |
| Kratos | Identity management (registration, login, recovery) | OpenDJ + OpenAM auth |
| Keto | Authorization (Google Zanzibar model) | OpenAM XACML engine |
| Oathkeeper | API gateway / zero-trust proxy | OpenIG |

Ory's philosophy: headless, API-first, no built-in UI, Go binaries, each component independently deployable with its own database. Total GitHub stars: ~40,000 combined. Commercial offering: Ory Network (SaaS). `[ACTIVE]`

Critical gap: no SAML 2.0 support. Organizations with SAML federation requirements cannot use Ory as a complete OpenAM replacement.

**2018: Wren Security Fork (Wren:AM)** `[ACTIVE]`

Orchitech Solutions (Czech Republic), led by Pavel Horal, forked the ForgeRock repositories and rebranded: OpenAM to Wren:AM, OpenDJ to Wren:DS. First release: Wren:AM 15.0.0-M1 (February 2023) -- five years after OIP's first release, reflecting Wren's deliberate build modernization and dependency upgrade strategy before feature work.

Wren's philosophy: maintain fewer features at higher quality. Dropped WebAuthn, QR auth, reCAPTCHA, NTLMv2 modules. Added Duo Security MFA integration. Java 17+ requirement (vs. OIP's Java 11+). Structured CVE remediation program (PRs #123--#130). As of February 2026: Wren:AM 16.0.0-M1 (milestone, not GA). `[ACTIVE]`

**2020: Authentik** `[ACTIVE]`

Authentik (formerly passbook, renamed 2020), developed by Jens Langhammer, is a Python/Django-based identity provider with a modern UI, flow-based authentication (visual flow editor), OIDC, SAML 2.0, LDAP outpost, and SCIM support. Authentik's visual authentication flow editor -- where administrators drag and drop authentication stages (password, TOTP, WebAuthn, consent, deny) into a directed acyclic graph -- directly addresses a gap that no other open-source IAM platform has filled. ~15,000 GitHub stars by 2026. `[ACTIVE]`

**2021: Zitadel** `[ACTIVE]`

Zitadel (CAOS AG, Switzerland) launched as a cloud-native identity platform built on event sourcing and CQRS, written in Go. Single binary deployment with PostgreSQL or CockroachDB backend. Every state change is stored as an immutable event, making the audit trail the system's primary data model.

Key differentiators: OIDC and SAML 2.0 support, built-in SCIM, Terraform provider for infrastructure-as-code, multi-tenancy (instances, organizations, projects), JavaScript Actions for custom logic. ~9,500 GitHub stars. Commercial offering: Zitadel Cloud. `[ACTIVE]`

**2021: SuperTokens** `[ACTIVE]`

SuperTokens (founded 2020, open-sourced 2021) is a developer-focused auth platform written in Java (core) with SDKs for Node.js, Python, Go, and React/React Native. Focuses on session management, passwordless auth, social login, and MFA. ~14,000 GitHub stars. Managed offering: SuperTokens SaaS. `[ACTIVE]`

**2022: Logto, Hanko, Casdoor** `[ACTIVE]`

A wave of lightweight, developer-focused identity platforms appeared:

| Platform | Language | Focus | Stars | Status |
|----------|----------|-------|-------|--------|
| Logto | TypeScript | OIDC, social login, beautiful default UI | ~9,000 | `[ACTIVE]` |
| Hanko | Go | Passkey-native authentication | ~6,000 | `[ACTIVE]` |
| Casdoor | Go | Casbin-based authorization + OIDC/SAML | ~10,000 | `[ACTIVE]` |
| ZITADEL | Go | Event-sourced, cloud-native | ~9,500 | `[ACTIVE]` |

**2023: Keycloak CNCF Incubation** `[ACTIVE]`

Keycloak was accepted as a CNCF Incubating project in April 2023. This provided governance, security audits, vendor neutrality, and a path to graduation. The CNCF status cemented Keycloak's position as the de facto open-source IAM platform. Version 25 (2024) completed the WildFly-to-Quarkus migration, yielding ~50% faster startup and container-native immutable images. Version 26 (2024) introduced Organizations for B2B multi-tenancy. ~26,000 GitHub stars, ~1,100 contributors. `[ACTIVE]`

**2024: Keycloak's Dominance** `[ACTIVE]`

By 2024, Keycloak had become the default open-source IAM platform. Evidence:

- CNCF incubation governance and security audits
- Red Hat's ~20-engineer investment (Red Hat SSO / Red Hat Build of Keycloak)
- 26,000+ GitHub stars (vs. ~700 for OIP OpenAM)
- 1,100+ contributors (vs. ~30 for OIP)
- Official Kubernetes Operator
- Quarkus-native runtime with build-time optimization
- Realm export/import for configuration-as-code
- Declarative user profiles (v24)
- Certified OIDC provider
- Broad ecosystem: Terraform community providers, SPI extensions, themes

Where OpenAM retains advantage: XACML 3.0 policy engine, 34+ auth modules (Keycloak has ~15 built-in), SAML 2.0 maturity (20+ years of federation testing), RADIUS support, embedded LDAP (OpenDJ). See [Chapter 7: OpenAM Analysis](07-openam-analysis.md), section 5.1 for detailed comparison.

### Open-Source IAM Platform Comparison (2026)

| Dimension | OpenAM (OIP) | Keycloak | Ory Stack | Zitadel | Authentik |
|-----------|-------------|----------|-----------|---------|-----------|
| First release | 2005 (OpenSSO) | 2014 | 2017 | 2021 | 2020 |
| Language | Java | Java (Quarkus) | Go | Go | Python/Django |
| Architecture | Monolithic WAR | Single Quarkus JAR | 4 microservices | Single binary, event-sourced | Django monolith |
| OIDC | Yes | Yes (certified) | Yes (certified) | Yes | Yes |
| SAML 2.0 | Yes (IdP+SP) | Yes (IdP+SP) | No | Yes | Yes |
| Auth modules | 34+ | ~15 built-in | ~5 | ~8 | Flow-based (visual) |
| Authorization | XACML 3.0 | UMA 2.0 | Zanzibar (Keto) | RBAC | Policy engine |
| K8s Operator | No | Official | Helm | Helm | Helm |
| License | CDDL | Apache 2.0 | Apache 2.0 | Apache 2.0 | MIT-like |
| GitHub stars | ~700 | ~26,000 | ~40,000 | ~9,500 | ~15,000 |
| Contributors | ~30 | ~1,100 | ~500 | ~200 | ~300 |
| Commercial backing | 3A Systems | Red Hat | Ory GmbH | CAOS AG | Authentik Security |

### Fork Divergence Analysis (ForgeRock Lineage)

The three ForgeRock-descended codebases share ~8,096 commits of common ancestry (2012--2016) and then diverge:

| Metric | ForgeRock CE 11.0.3 | OIP OpenAM 16.0.5 | Wren:AM 16.0.0-M1 |
|--------|--------------------|--------------------|---------------------|
| Last commit | Nov 2017 | Feb 2026 | Feb 2026 |
| Post-fork commits | 5 (frozen) | ~1,489 | ~426 |
| Releases since fork | 0 | 81 | 24 |
| Java minimum | 7 | 11 | 17 |
| Guice version | 3.0 | 7.0.0 | 3.0 (wrapped) |
| Jakarta EE | No (javax) | 4.0+ | 5.0 |
| Auth modules | 20 | 34+ | 27 (+Duo) |
| Critical unpatched CVEs | 22+ | 0 current | 0 current |
| Status | `[OBSOLETE]` | `[ACTIVE]` | `[ACTIVE]` |

See [Chapter 1](01-history.md) for the complete fork analysis, including dependency divergence, contributor analysis, and release cadence comparison.

---

## Roadmap 17: Cloud Infrastructure Entitlement Management (CIEM)

CIEM emerged because cloud IAM is fundamentally different from on-premises IAM. On-premises, a single LDAP directory (OpenDJ, Active Directory) stores users and groups, and a single policy engine (OpenAM's XACML engine) evaluates access. In the cloud, every service has its own identity and permission model, permissions can be granted at the resource, account, organization, and service level, and the blast radius of a misconfigured policy is potentially unlimited.

### Timeline

**2006--2011: Cloud IAM Begins** `[ACTIVE]`

- **AWS IAM** (2011, GA): Amazon Web Services launched IAM as a free service for managing access to AWS resources. AWS IAM introduced concepts that became cloud IAM primitives: policies (JSON documents specifying permissions), roles (assumed by services or federated users), users, groups, and the critical concept of the "principal" -- the entity making a request (user, role, service, or federated identity). AWS IAM policies use a condition-action-resource model evaluated on every API call.
- **AWS Security Token Service (STS)** (2011): Provided temporary security credentials -- short-lived access keys for assumed roles -- establishing the pattern of ephemeral cloud credentials.

**2014--2016: Azure and GCP IAM** `[ACTIVE]`

- **Azure RBAC** (2014): Microsoft Azure introduced role-based access control for Azure resources. Azure's model assigns built-in or custom roles at four scope levels: management group, subscription, resource group, and resource. Azure Active Directory (now Entra ID) provided the identity plane.
- **GCP IAM** (2016): Google Cloud Platform IAM uses an allow-policy model where principals are granted roles on resources. GCP's IAM model is notable for its resource hierarchy (organization > folder > project > resource) and policy inheritance down the hierarchy. Cloud IAM Conditions (2020) added context-aware access rules.

**2017--2018: Multi-Cloud Identity Complexity Emerges** `[ACTIVE]`

As organizations adopted multi-cloud strategies (AWS + Azure + GCP), the identity and entitlement complexity exploded:

- Each cloud provider has its own IAM model, terminology, and policy language (AWS IAM JSON, Azure RBAC, GCP allow policies)
- Cross-cloud identity federation exists (OIDC federation, SAML) but cross-cloud entitlement management does not
- Permission models are incompatible: AWS `iam:PassRole` has no equivalent in Azure; GCP's resource hierarchy inheritance has no direct AWS analog
- The number of distinct permissions is staggering: AWS has 17,000+ individual actions across 300+ services; Azure has 10,000+ permissions; GCP has thousands more

**2019: AWS IAM Access Analyzer** `[ACTIVE]`

AWS introduced IAM Access Analyzer, which uses automated reasoning (formal methods / satisfiability modulo theories, or SMT solvers) to analyze IAM policies and identify resources shared with external entities. Access Analyzer can determine whether an S3 bucket policy, IAM role trust policy, KMS key policy, or Lambda function policy grants access to a principal outside the account. This was the first mainstream use of formal verification for cloud IAM policy analysis.

In 2024, AWS extended Access Analyzer with unused access analysis -- identifying permissions that have been granted but never used, enabling least-privilege recommendations.

**2020: CIEM as a Category (Gartner)** `[ACTIVE]`

Gartner defined CIEM as a distinct category in 2020, recognizing that managing cloud infrastructure permissions required specialized tooling beyond traditional IGA platforms. The CIEM definition: "CIEM offerings are specialized identity-centric SaaS solutions focused on managing cloud access risk via administration-time controls for the governance of entitlements in hybrid and multi-cloud IaaS."

CIEM's scope:

- **Discovery:** Enumerate all identities (human, service, cross-account, federated) across all cloud providers
- **Analysis:** Assess effective permissions (resolving policy inheritance, boundaries, SCPs, resource policies)
- **Right-sizing:** Identify over-provisioned permissions (granted but never used) and recommend least-privilege policies
- **Remediation:** Generate and apply right-sized policies
- **Monitoring:** Detect permission drift, anomalous permission changes, and privilege escalation paths

**2020--2021: CIEM Vendor Emergence** `[ACTIVE]`

Multiple vendors launched CIEM products:

| Vendor | Founded | CIEM Focus | Status (2026) |
|--------|---------|------------|---------------|
| Ermetic | 2019 | Multi-cloud entitlement analysis | Acquired by Tenable (2023) |
| CloudKnox | 2017 | Activity-based least privilege | Acquired by Microsoft (2021); now Entra Permissions Management |
| Sonrai Security | 2017 | Cloud identity governance | Independent |
| Wiz | 2020 | Cloud security platform (CIEM as component) | IPO-track (~$12B valuation) |
| CrowdStrike | 2011 | Falcon Cloud Security (CIEM module) | Independent |
| Prisma Cloud (Palo Alto) | 2018 | CNAPP with CIEM | Independent |
| Zscaler (CIEM) | 2008 | CIEM via Trustdome acquisition (2021) | Independent |

**2021: Microsoft Acquires CloudKnox** `[ACTIVE]`

Microsoft acquired CloudKnox Security and integrated it as **Microsoft Entra Permissions Management** -- a multi-cloud CIEM solution that analyzes permissions across AWS, Azure, and GCP from a single console. Key capabilities:

- Permission Creep Index: quantifies the gap between granted and used permissions
- Multi-cloud discovery: inventory of human/workload identities across AWS IAM, Azure RBAC, GCP IAM
- Just-in-Time access: users request elevated permissions for a time-bounded window, automatically revoked on expiry
- Automated right-sizing: ML-based recommendations for least-privilege policies

The acquisition validated CIEM as a strategic category and signaled that CIEM would converge with broader identity security platforms.

**2022--2023: CIEM Converges with CNAPP** `[ACTIVE]`

CIEM merged into Cloud-Native Application Protection Platforms (CNAPP), which combine cloud security posture management (CSPM), cloud workload protection (CWP), and CIEM into a unified platform. Major CNAPP vendors (Wiz, Prisma Cloud, Lacework/Fortinet, Orca) all include CIEM capabilities.

**2023: AWS Resource Control Policies and Service Control Policies Evolution** `[ACTIVE]`

AWS continued expanding its preventive controls:

- **Service Control Policies (SCPs):** Organization-level guardrails that limit the maximum permissions available within member accounts. SCPs do not grant permissions; they restrict them.
- **Permission Boundaries:** IAM-level limits on the maximum permissions a user or role can have, regardless of what identity-based policies grant.
- **Resource Control Policies (RCPs, 2024):** New organizational policy type that controls the maximum permissions grantable on resources within the organization, complementing SCPs (which control identity-side permissions).

These layered control mechanisms make effective permission calculation increasingly complex -- the effective permission is the intersection of identity policies, permission boundaries, SCPs, RCPs, resource policies, and session policies. CIEM tools must resolve this multi-layer intersection accurately.

**2024--2025: Identity-Based Blast Radius Analysis** `[EMERGING]`

Advanced CIEM tools now model attack paths through cloud identity graphs:

- If an attacker compromises IAM User A, what roles can A assume?
- What permissions do those roles grant?
- Can any of those permissions be used to escalate privileges (e.g., `iam:CreateRole`, `iam:AttachRolePolicy`, `sts:AssumeRole` with overly permissive trust policies)?
- What data can be accessed at the end of the attack chain?

This "identity blast radius" analysis treats cloud IAM as a directed graph where nodes are identities and edges are permission/assumption relationships. Wiz, Ermetic/Tenable, and CrowdStrike all provide attack path visualization. The approach extends ITDR concepts (Roadmap 13) into the cloud entitlement domain.

**2025--2026: Least-Privilege Automation** `[EMERGING]`

The frontier of CIEM is automated policy generation:

- Analyze CloudTrail/Activity Log/Audit Log data for 90+ days to establish actual usage
- Generate a minimum-privilege policy that covers observed usage plus a safety margin
- Apply the generated policy, replacing the over-permissive original
- Monitor for access denied errors and automatically expand the policy if legitimate new usage is detected

AWS IAM Access Analyzer's policy generation feature does this for individual roles. Entra Permissions Management does it cross-cloud. The goal is zero standing privileges in cloud environments -- every permission is just-in-time, just-enough, and time-bounded.

### OpenAM/OIP Relationship to CIEM

OpenAM and CIEM operate at different layers. OpenAM manages application-level authentication and authorization (who can access this web application, with what OAuth scopes). CIEM manages infrastructure-level entitlements (who can call `s3:GetObject` on this S3 bucket in this AWS account).

However, there are intersection points:

- **Federated access to cloud:** OpenAM can serve as the SAML/OIDC IdP that federates user identities into AWS IAM roles, Azure RBAC, or GCP IAM. The permissions those federated sessions receive are a CIEM concern.
- **Session attributes as entitlement context:** OpenAM's session attributes (authentication level, device fingerprint, adaptive risk score) could inform cloud entitlement decisions -- a high-risk session should receive fewer cloud permissions.
- **Shared identity lifecycle:** OpenIDM's provisioning workflows could manage cloud IAM users/roles alongside on-premises directory entries, providing unified lifecycle management across on-premises (LDAP) and cloud (AWS IAM, Azure RBAC) entitlements.

None of these integrations exist natively in the OIP stack. Organizations bridging OpenAM and cloud IAM typically use SAML federation (OpenAM as IdP, AWS IAM or Azure AD as SP) and manage cloud entitlements separately through cloud-native or CIEM tools.

---

## Roadmap 18: Identity Orchestration & Journey-Time Orchestration

Identity orchestration is the evolution of authentication from hardcoded linear flows to dynamically composed, context-aware decision graphs. The trajectory: hardcoded login pages (1990s) to configurable authentication chains (2005) to visual authentication trees (2018) to fully orchestrated identity journeys (2023+).

### Timeline

**1990s--2000s: Hardcoded Authentication** `[OBSOLETE]`

Early web applications implemented authentication directly in application code. A login page submitted username/password to a servlet, which validated against a database or LDAP server, created an HTTP session, and set a cookie. Authentication logic was intertwined with application logic. Changing the authentication flow required code changes, testing, and redeployment.

**2000--2005: JAAS and Centralized Authentication** `[LEGACY]`

Java Authentication and Authorization Service (JAAS), included in J2SE 1.4 (2002), provided a pluggable authentication framework based on PAM (Pluggable Authentication Modules) concepts. JAAS defined a standard interface (`LoginModule`) for authentication modules, with control flags (REQUIRED, REQUISITE, SUFFICIENT, OPTIONAL) governing how module results were combined.

Sun Access Manager (2005) and subsequently OpenSSO implemented authentication chains using JAAS. The chain model: a linear sequence of authentication modules, each with a control flag, executed in order. The chain's outcome was determined by the combination of module successes/failures according to the JAAS specification.

OpenAM inherits this architecture. The key classes -- `AuthContext`, `AMLoginContext`, `AMAuthenticationManager`, `AMLoginModule`, `LoginState` -- are documented in [Chapter 7: OpenAM Analysis](07-openam-analysis.md), section 2. Authentication chains are configured per realm and per service, stored as LDAP entries in the OpenDJ configuration store.

The chain model was powerful for its era: administrators could compose multi-factor authentication by stacking modules (LDAP password REQUIRED + TOTP REQUIRED), implement fallback paths (Kerberos SUFFICIENT, falling back to LDAP REQUIRED if Kerberos fails), and add post-authentication processing (session attribute injection, audit logging).

**Limitations of the chain model:**

- **Linear-only execution:** Chains execute in strict sequence. There is no conditional branching based on intermediate results. The chain cannot say "if the user is from a trusted network, skip MFA; otherwise, require it." Workarounds exist (the adaptive authentication module evaluates conditions and returns SUCCESS/FAILURE to influence the chain), but the chain itself is a flat list, not a decision graph.
- **No shared context between modules:** Each JAAS `LoginModule` receives callbacks and returns success/failure, but there is no structured mechanism for one module to pass data to a subsequent module. `LoginState` provides some shared state, but module-to-module communication is ad hoc.
- **Configuration in LDAP:** Chain definitions are stored as LDAP attributes, making version control, review, and rollback difficult. There is no export/import mechanism, no diff capability, and no approval workflow for chain changes.

**2012--2015: OAuth 2.0 Flows as Orchestration** `[ACTIVE]`

OAuth 2.0 (RFC 6749, 2012) introduced the concept of multi-party, multi-step authentication flows that were inherently more dynamic than JAAS chains. The authorization code flow involves the client, the authorization server, and the resource server in a choreographed sequence. OIDC extended this with an ID Token, adding an identity layer to the authorization flow.

The consent screen in OAuth 2.0 was a primitive form of journey-time orchestration: the authorization server dynamically decided whether to show a consent screen based on whether the user had previously consented to the requested scopes. This was the first mainstream example of a conditional step in an authentication flow.

**2018: ForgeRock Authentication Trees (Intelligent Authentication)** `[ACTIVE]` (in ForgeRock commercial)

ForgeRock AM 6.0 (2018, commercial, not open-source) introduced "authentication trees" -- a directed acyclic graph (DAG) model replacing linear chains. Each node in the tree performed one operation (collect username, validate password, evaluate device fingerprint, check risk score, prompt for MFA) and had multiple output edges leading to different next nodes based on the operation's result.

This was a fundamental architectural advance:

- **Conditional branching:** A risk score node could route low-risk users directly to success while routing high-risk users through additional verification.
- **Shared state:** A tree-level shared state object was available to all nodes, enabling data passing between steps.
- **Reusable components:** Nodes could be composed into sub-trees and reused across different authentication scenarios.
- **Visual editor:** ForgeRock's commercial product included a drag-and-drop tree editor in the admin console.

OpenAM (OIP fork) does **not** implement authentication trees. The OIP fork remains on the JAAS chain model from the ForgeRock CE era. This is one of the most significant feature gaps between the open-source forks and the ForgeRock commercial product.

**2021: Auth0 Actions** `[ACTIVE]`

Auth0 introduced Actions (2021, GA) -- serverless Node.js functions that execute at specific points in the authentication/authorization flow. Actions run on Auth0's infrastructure and can modify the flow by:

- Adding custom claims to tokens
- Triggering MFA based on custom logic
- Redirecting users to external services mid-flow
- Denying access based on custom rules
- Sending notifications on authentication events

Actions replaced Auth0's earlier "Rules" and "Hooks" mechanisms, providing a unified extensibility model. The key innovation was making flow customization a developer concern (write JavaScript) rather than an administrator concern (configure chains in an LDAP-backed console).

**2021: Ping Identity DaVinci** `[ACTIVE]` (commercial)

Ping Identity (later merged with ForgeRock post-acquisition) launched DaVinci, a visual no-code identity orchestration platform. DaVinci provides a drag-and-drop canvas where identity architects compose flows using pre-built connectors to IdPs, MFA providers, risk engines, fraud detection services, and third-party APIs. The orchestration is external to the IdP -- DaVinci sits above Ping Identity's authentication services and orchestrates calls across them.

DaVinci represents the purest form of journey-time orchestration: the flow is not hardcoded in the IdP, configured as a chain, or coded as a script. It is visually composed from reusable components and can be modified in real time without redeploying any identity infrastructure.

**2022: Strata Identity Maverics** `[ACTIVE]` (commercial)

Strata Identity's Maverics platform provides vendor-neutral identity orchestration. Maverics sits between applications and identity providers, abstracting the IdP dependency. Key use case: migrating from one IdP to another (e.g., from OpenAM to Keycloak) without modifying applications. Maverics handles protocol translation (SAML to OIDC, header-based to token-based), credential migration, and session management during the transition.

Maverics addresses a real pain point documented in [Chapter 7: OpenAM Analysis](07-openam-analysis.md), section 5.6: the migration cost of moving between IAM platforms. By abstracting the IdP behind an orchestration layer, Maverics reduces the migration from a "big bang" cutover to a gradual transition.

**2022: Authentik Flow Editor** `[ACTIVE]`

Authentik's visual flow editor brought authentication tree concepts to the open-source world. Administrators compose authentication flows as directed graphs: each stage (password prompt, TOTP verification, consent, email verification, captcha) is a node; edges connect stages based on pass/fail outcomes. This is the closest open-source equivalent to ForgeRock's authentication trees or Ping's DaVinci.

**2023: Keycloak Step-Up Authentication and Conditional Flows** `[ACTIVE]`

Keycloak's authentication flows have evolved from simple linear sequences to conditional sub-flows. Keycloak v22+ supports:

- **Conditional OTP:** MFA required only when the user's session does not have a trusted device cookie.
- **Conditional execution:** Sub-flows that execute only when a condition is met (e.g., user belongs to a specific group, or IP address is outside the corporate network).
- **WebAuthn conditional UI:** Passkey selection integrated into the login form via WebAuthn conditional mediation.

While not a full DAG-based tree like ForgeRock's or a visual editor like Authentik's, Keycloak's conditional flows provide meaningful branching logic within the OIDC/SAML authentication process.

**2023--2024: Journey-Time Orchestration** `[EMERGING]`

Gartner introduced "journey-time orchestration" to describe the next evolution: identity decisions are not confined to the authentication moment but span the entire user journey -- from first visit through registration, progressive profiling, step-up authentication, consent collection, session management, and eventual account deletion.

Journey-time orchestration principles:

- **Continuous, not point-in-time:** Authentication is not a gate; it is an ongoing assessment that evolves throughout the session based on context changes (device posture change, geographic anomaly, resource sensitivity, elapsed time).
- **Cross-channel:** The same orchestration logic applies whether the user is in a browser, mobile app, API client, or kiosk.
- **Vendor-neutral:** The orchestration layer is independent of the IdP, MFA provider, fraud engine, and consent management system.
- **Policy-driven:** Journey decisions are expressed as policies (if risk > threshold, then step-up; if consent missing, then collect; if session age > 1 hour and accessing PII, then re-authenticate).

**2024--2025: OIDC CIBA and Decoupled Authentication** `[ACTIVE]`

OIDC Client-Initiated Backchannel Authentication (CIBA, OpenID Foundation, 2021) enables authentication flows where the consumption device (e.g., a call center agent's workstation) is different from the authentication device (the user's mobile phone). The flow: the client sends a backchannel authentication request to the IdP; the IdP pushes an authentication prompt to the user's registered device; the user authenticates on their device; the IdP returns tokens to the client.

CIBA is relevant to orchestration because it decouples the authentication interaction from the application flow. The application does not need to redirect the user; it initiates authentication out-of-band and waits for the result. This enables authentication to be orchestrated independently of the user's application session.

OpenAM's push authentication module (`openam-auth-push`) implements a similar concept -- authentication via mobile push notification -- but it is tied to OpenAM's proprietary push mechanism rather than the OIDC CIBA standard.

**2025--2026: AI-Driven Orchestration** `[EMERGING]`

The frontier of identity orchestration is AI-driven flow optimization:

- ML models analyze authentication flow completion rates and optimize for conversion (reduce drop-off without reducing security)
- LLMs generate natural language explanations of why a user was challenged ("We noticed you're logging in from a new device. Please verify your identity.")
- Reinforcement learning adjusts MFA prompts based on user behavior patterns -- frequent users with consistent patterns see fewer challenges; users with anomalous patterns see more
- Adaptive flow selection: the orchestration engine selects the optimal authentication flow in real time based on available signals (device capability, network quality, user risk score, resource sensitivity)

### OpenAM/OIP Authentication Architecture vs. Modern Orchestration

| Capability | OpenAM (JAAS Chains) | ForgeRock (Trees) | Authentik (Flows) | Ping DaVinci | Auth0 Actions |
|-----------|---------------------|-------------------|-------------------|--------------|---------------|
| Flow model | Linear chain | DAG (tree) | DAG (visual) | DAG (visual, no-code) | Event hooks (JS) |
| Conditional branching | Via adaptive module only | Native (node outputs) | Native (stage outcomes) | Native (connectors) | Via code |
| Visual editor | No | Yes (commercial) | Yes (open-source) | Yes | No |
| Shared state | LoginState (ad hoc) | Tree shared state | Context pipeline | Flow variables | Event object |
| Extensibility | Java SPI (AMLoginModule) | Java/JS nodes | Python stages | Connectors (API) | Node.js Actions |
| Configuration store | LDAP | LDAP/REST | Database | Cloud | Cloud |
| Version control friendly | No (LDAP entries) | Partial (JSON export) | Yes (YAML) | No (cloud) | Yes (Deploy CLI) |
| Open source | Yes (CDDL) | No (commercial) | Yes (MIT-like) | No | No |

OpenAM's JAAS chain model is the oldest and least flexible orchestration approach in active use. The lack of conditional branching, visual editing, and configuration-as-code makes it increasingly difficult to implement the adaptive, risk-driven authentication flows that modern security requirements demand. For organizations running OpenAM that need orchestration capabilities, the options are:

1. **Adaptive authentication module:** Use `openam-auth-adaptive` as a chain module to evaluate risk signals and conditionally succeed/fail, influencing the chain outcome.
2. **Scripted authentication module:** Use `openam-auth-scripted` with Groovy scripts to implement custom branching logic within a single chain step.
3. **External orchestration:** Deploy Strata Maverics or a custom orchestration layer in front of OpenAM, treating OpenAM as a policy decision point that the orchestrator calls selectively.
4. **Migration to Authentik or Keycloak:** Adopt a platform with native flow/tree capabilities.

---

## Summary: The Grand Shift Table

The following table consolidates all 18 roadmaps into a single reference, tracing each identity security domain from its origin through the pre-2010 era, the current state (2024--2026), and the projected next evolution (2027+).

| # | Domain | Origin | Then (Pre-2010) | Now (2024--2026) | Next (2027+) | OpenAM/OIP Status |
|---|--------|--------|-----------------|------------------|--------------|-------------------|
| 1 | **Authentication Methods** | Passwords (1960s) | LDAP bind + RADIUS + OTP hardware tokens | Passkeys (FIDO2/WebAuthn), push MFA, conditional UI `[ACTIVE]` | Continuous behavioral auth, ambient authentication `[EMERGING]` | 34+ modules incl. WebAuthn, TOTP, push |
| 2 | **Federation Protocols** | Kerberos cross-realm (1988) | SAML 2.0, WS-Federation, Liberty ID-FF | OIDC + OIDC Federation, OAuth 2.1 draft `[ACTIVE]` | GNAP, Verifiable Presentations (OID4VP) `[EMERGING]` | Full SAML 2.0 IdP/SP + OIDC Provider |
| 3 | **Authorization Models** | Unix file permissions (1971) | RBAC (NIST 2004), XACML 1.0/2.0, ACLs | XACML 3.0, OPA/Rego, Cedar, Zanzibar/ReBAC `[ACTIVE]` | Policy-as-code universal, AI-generated policies `[EMERGING]` | XACML 3.0 entitlements engine |
| 4 | **Token Formats & Sessions** | Kerberos tickets (1988) | SAML assertions, server-side sessions, opaque cookies | JWT (RFC 7519), DPoP (RFC 9449), mTLS-bound tokens `[ACTIVE]` | Transaction Tokens (TxnTokens), VC-based sessions `[EMERGING]` | CTS sessions (LDAP/Cassandra), OAuth bearer tokens |
| 5 | **Directory Services** | X.500 (1988) | LDAPv3 (RFC 4510), Active Directory | SCIM 2.0, cloud directories, PostgreSQL backends `[ACTIVE]` | Event-sourced identity stores, LDAP as facade only `[EMERGING]` | OpenDJ (LDAPv3, multi-master replication) |
| 6 | **Identity Governance (IGA)** | Manual provisioning | Meta-directory sync, SPML, Sun IdM | SCIM 2.0, event-driven sync (SSF), AI access reviews `[ACTIVE]` | Autonomous IGA, real-time governance `[EMERGING]` | OpenIDM (OSGi, Activiti BPMN, OpenICF connectors) |
| 7 | **API Security & Gateways** | HTTP Basic Auth (1996) | Policy agents (OpenAM J2EE/web agents), API keys | API gateways + service mesh + mTLS, DPoP `[ACTIVE]` | Zero-trust API fabric, identity-native APIs `[EMERGING]` | OpenIG (filter/handler pipeline, credential replay) |
| 8 | **Privileged Access (PAM)** | su/sudo (1980s) | Shared account vaults, CyberArk | JIT access, Zero Standing Privileges, ephemeral creds `[ACTIVE]` | Autonomous PAM, AI-driven vault policies `[EMERGING]` | Not in OIP scope (OpenAM admin delegation only) |
| 9 | **Deployment Architecture** | On-prem WAR/EAR (2000s) | Clustered J2EE, sticky sessions | K8s Operators, single-binary, serverless auth, SaaS IDaaS `[ACTIVE]` | Edge-deployed identity, identity mesh `[EMERGING]` | WAR on Tomcat, Docker image, no K8s Operator |
| 10 | **Passwordless & MFA** | Passwords (1960s) | SMS OTP, RSA SecurID, HOTP/TOTP | Passkeys (synced + device-bound), platform authenticators `[ACTIVE]` | Ambient biometric auth, death of passwords `[EMERGING]` | HOTP, TOTP, WebAuthn, push auth modules |
| 11 | **Zero Trust** | Firewall perimeter (1990s) | DMZ architecture, VPN, network zones | NIST SP 800-207, ZTNA (Zscaler, Cloudflare), CISA ZT Maturity `[ACTIVE]` | Identity-native zero trust, continuous verification `[EMERGING]` | Adaptive auth + OpenIG gateway (partial ZT fit) |
| 12 | **Machine & Workload Identity** | Service accounts (1990s) | API keys, static credentials, OAuth client_credentials | SPIFFE/SPIRE, cloud workload identity, mTLS, Sigstore `[ACTIVE]` | WIMSE standard, non-human identity platforms `[EMERGING]` | OAuth client_credentials grant; no SPIFFE/SPIRE |
| 13 | **ITDR** | Log aggregation (2000s) | SIEM correlation (ArcSight, Splunk), manual investigation | Gartner ITDR category, CrowdStrike/Silverfort/Entra ID Protection `[ACTIVE]` | AI-powered identity SOC, automated remediation `[EMERGING]` | Audit module as data source; no native ITDR |
| 14 | **Privacy & Consent** | US FIPPs (1973) | EU Directive 95/46/EC, P3P, basic consent checkboxes | GDPR/CCPA/PIPL, consent-as-code, GPC, eIDAS 2.0 `[ACTIVE]` | Purpose-bound access, ZKP-based age verification `[EMERGING]` | OAuth consent screen; no CMP, no DSAR automation |
| 15 | **Decentralized Identity** | PGP web of trust (1991) | OpenID 2.0, user-centric identity movement | W3C VCs 2.0, DIDs 1.0, OID4VC, SD-JWT VC, EU EUDIW `[EMERGING]` | Wallet-native auth, VC-first enterprise IAM `[EMERGING]` | No VC/DID support; centralized IdP model |
| 16 | **Open-Source IAM Platforms** | Sun OpenSSO (2005) | ForgeRock OpenAM, CAS, Shibboleth | Keycloak (CNCF), Ory, Zitadel, Authentik, OIP, Wren `[ACTIVE]` | Composable identity fabric, platform consolidation `[EMERGING]` | OIP OpenAM 16.0.5 (CDDL, 34+ modules) |
| 17 | **CIEM** | AWS IAM (2011) | Single-cloud IAM policies, manual permission management | Multi-cloud CIEM (Entra Permissions Mgmt, Wiz), blast radius analysis `[ACTIVE]` | Autonomous least-privilege, zero standing cloud perms `[EMERGING]` | Not in scope; SAML/OIDC federation to cloud IAM |
| 18 | **Identity Orchestration** | Hardcoded login (1990s) | JAAS auth chains (OpenAM), linear module sequences | Auth trees (DAG), visual flow editors, no-code orchestration `[ACTIVE]` | AI-driven adaptive journeys, journey-time orchestration `[EMERGING]` | JAAS chain model; no tree/DAG, no visual editor |

### Cross-Roadmap Observations

**The Identity Security Expansion Pattern.** Each roadmap reveals the same meta-pattern: a domain starts narrow and technology-focused (passwords, LDAP, firewalls) and expands to encompass governance, risk, compliance, and operational dimensions. Authentication expanded from "validate a password" to "continuously assess trust across multiple factors and contexts." Authorization expanded from "check an ACL" to "evaluate policies across cloud, on-premises, and SaaS resources in real time." Provisioning expanded from "create an LDAP entry" to "orchestrate lifecycle across 100+ SaaS applications with consent tracking and regulatory compliance."

**Standards as the Integration Fabric.** The most successful identity technologies are those backed by open standards with broad implementer adoption. OIDC (OpenID Foundation), SCIM 2.0 (IETF RFC 7642--7644), FIDO2/WebAuthn (W3C/FIDO Alliance), SPIFFE (CNCF), and OID4VC (OpenID Foundation) are the integration seams that make composable identity architectures possible. Proprietary approaches (ForgeRock authentication trees, Ping DaVinci flows) offer superior UX but create vendor lock-in. OpenAM's XACML 3.0 engine is the exception that proves the rule: it implements an open standard (OASIS XACML) but the standard itself has failed to achieve broad adoption outside of OpenAM and a few commercial products.

**The OpenAM Gap Analysis.** Across all 18 roadmaps, OpenAM's capabilities cluster in the "Then" column (pre-2010 architectural patterns) with extensions into the "Now" column for authentication modules (WebAuthn, push MFA). The gaps are concentrated in: ITDR (no detection capability), CIEM (no cloud entitlement management), decentralized identity (no VC/DID support), identity orchestration (JAAS chains, not trees), privacy/consent (minimal consent engine), and deployment architecture (WAR-based, no Kubernetes Operator). The OIP fork's value proposition is not architectural modernity but breadth and stability -- 34+ authentication modules, XACML 3.0, combined SAML/OIDC/UMA, and a 20-year battle-tested codebase that handles edge cases newer platforms have not yet encountered.

**The Convergence Trajectory.** The 18 domains are converging. ITDR requires IAM data. CIEM requires IGA processes. Privacy requires orchestration. Zero trust requires ITDR, PAM, and continuous authentication simultaneously. The future is not 18 separate tools but an integrated identity security platform -- an "identity fabric" -- that combines these capabilities through standardized APIs and event-driven integration. Whether that fabric is assembled from best-of-breed components (Keycloak + OPA + SPIRE + CrowdStrike + OneTrust) or delivered as a monolithic platform (Entra ID, Okta IGA, SailPoint) is the central architectural decision organizations face.

---

**Sources:**
- Git commit history analysis (58,112 commits across 7 repositories, 2006--2026) -- see `/Users/kirane/projects/idp/docs/extracts/git-history-analysis.md`
- OpenAM codebase analysis (34+ authentication modules, XACML 3.0, OAuth 2.0/OIDC) -- see [Chapter 7](07-openam-analysis.md)
- Modern architecture patterns (14 shifts) -- see [Chapter 12](12-modern-architecture.md)
- Historical parallels (Seven Pillars of Trust) -- see [Chapter 15](15-historical-parallels.md)
- Historical narrative (ForgeRock closure, OIP/Wren forks) -- see [Chapter 1](01-history.md)
- W3C VC Data Model 2.0 (2024), W3C DID Core 1.0 (2022)
- IETF: RFC 6749 (OAuth 2.0), RFC 7519 (JWT), RFC 9449 (DPoP), RFC 7642-7644 (SCIM 2.0), RFC 8417 (SET), RFC 8935/8936 (SET delivery)
- OASIS: XACML 3.0 (2013), SAML 2.0 (2005)
- NIST: SP 800-207 (Zero Trust), SP 800-63B (Digital Identity Guidelines)
- EU: Regulation 2016/679 (GDPR), Regulation 2024/1183 (eIDAS 2.0), Regulation 2024/1689 (AI Act)
- Gartner: ITDR category definition (2022), CIEM category definition (2020)
- FIDO Alliance: WebAuthn L2/L3, CTAP 2.1, Passkeys
- OpenID Foundation: OIDC Core 1.0, OID4VCI, OID4VP, SIOPv2, OIDC SSF (CAEP + RISC)
