---
title: Authentication Protocols
description: "LDAP, Kerberos, SAML, OAuth, OIDC, FIDO2 — complete analysis of 40+ authentication standards from 1993 to passkeys."
sidebar:
  order: 2
---

# Chapter 2: Authentication Protocols

Authentication protocols in the Open Identity Platform represent three decades of identity verification evolution, from LDAP bind operations to phishing-resistant FIDO2 credentials. OpenAM implements 34+ distinct authentication modules spanning directory-based, certificate-based, one-time password, legacy token, modern passwordless, social, and adaptive authentication mechanisms. This chapter examines each protocol family, its technical implementation, current relevance, migration paths, and position in the broader industry shift toward zero-trust architectures.

## Directory-Based Authentication

### LDAP Bind

**Problem Solved:** Direct credential verification against LDAP directories without intermediate authentication layers. Eliminates need for credential replication when directories already contain user passwords.

**Technical Flow:**

1. Client submits username/password to authentication module
2. Module constructs DN from username via template (e.g., `uid=%USERNAME%,ou=people,dc=example,dc=com`)
3. Establishes LDAP connection to configured server (supports failover between primary/secondary)
4. Issues LDAP Bind operation with DN and password
5. Directory validates credentials against password attribute (userPassword, typically SSHA-512 hash)
6. On success, optionally retrieves user attributes for session enrichment
7. Optional: StartTLS upgrade for encrypted credential transmission

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-ldap/`
- **Key Classes:**
  - `com.sun.identity.authentication.modules.ldap.LDAP` (extends `AMLoginModule`)
  - `LDAPAuthUtils` - DN construction, connection pooling, SSL/TLS configuration
  - `LDAPCallbacks` - Username/password callback handling
- **Backend Integration:** Uses OpenDJ LDAPv3 client libraries from `OpenDJ/opendj-core/`
- **Configuration:** LDAP URL, bind DN template, SSL keystore, password policies, search scope

**Current Relevance:** Active and ubiquitous. Every enterprise directory (Active Directory, OpenDJ, 389DS, OpenLDAP) supports LDAP bind. Remains the dominant authentication method for on-premises identity stores. However, plaintext password transmission (even over TLS) is increasingly problematic in zero-trust environments.

**What Replaces It:** OAuth2/OIDC authentication with directory acting as backing identity store rather than authentication endpoint. Passwordless methods (WebAuthn/passkeys) eliminate credential transmission entirely. Certificate-based authentication provides stronger cryptographic proof.

**Migration Considerations:**

- LDAP bind remains necessary for legacy application compatibility
- Wrap LDAP authentication behind OIDC provider (OpenAM serves as translation layer)
- Implement password policies (account lockout, complexity requirements) at directory level
- Use StartTLS or LDAPS for all LDAP communication
- Consider migrating to certificate-based bind for service accounts

### Active Directory (AD)

**Problem Solved:** Specialized LDAP variant addressing Windows domain controller authentication quirks, including NTLM password encoding and AD-specific attributes (sAMAccountName, userPrincipalName, memberOf).

**Technical Flow:**

Similar to LDAP bind but with AD-specific enhancements:

1. Accepts both UPN format (`user@domain.com`) and sAMAccountName (`DOMAIN\user`)
2. Converts username to AD DN search (e.g., via `(&(objectClass=user)(sAMAccountName=%USERNAME%))`)
3. Issues LDAP bind with discovered DN
4. Retrieves AD-specific attributes: memberOf (group DNs), tokenGroups (SIDs), pwdLastSet, accountExpires
5. Maps Windows security groups to OpenAM roles/privileges

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-ad/`
- **Key Classes:**
  - `com.sun.identity.authentication.modules.ad.AD`
  - `ADPrincipal` - Wraps AD user attributes
- **Integration:** Shares `LDAPAuthUtils` with LDAP module; extends with AD password encoding

**Current Relevance:** Essential for hybrid cloud environments. Azure AD Connect (now Entra ID Connect) replicates on-premises AD to cloud but many organizations retain AD as authoritative source. Windows Desktop SSO (Kerberos/SPNEGO) depends on AD infrastructure.

**What Replaces It:** Azure AD (Entra ID) for cloud-native applications. Hybrid authentication via OIDC federation between on-premises AD (via ADFS or OpenAM) and cloud IdPs. Certificate-based authentication for device trust.

**Migration Considerations:**

- AD remains unavoidable for Windows-centric enterprises
- Federate AD authentication to OIDC/SAML providers for modern apps
- Use Windows Hello for Business (certificate/biometric) instead of password authentication
- Implement Privileged Access Workstations (PAWs) for admin accounts
- Monitor deprecated NTLMv1 usage; enforce Kerberos or certificate authentication

### DataStore (Identity Repository Abstraction)

**Problem Solved:** Decouples authentication from specific directory implementations. Allows pluggable identity stores (LDAP, SQL, custom) without authentication module changes.

**Technical Flow:**

1. Module queries configured identity repository plugin via abstraction layer
2. Plugin translates query to backend-specific operations (LDAP search, SQL SELECT, REST API call)
3. Retrieves user object with hashed password
4. Module validates submitted password against hash (PBKDF2, bcrypt, SSHA-512)
5. Session established on validation success

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-datastore/`
- **Key Abstraction:** `com.sun.identity.idm.IdRepo` interface
- **Plugins:**
  - `AMSDKRepo` - Legacy OpenAM SDK
  - `LDAPRepo` - LDAP via opendj-core
  - `JDBCRepo` - SQL databases
  - Custom implementations via SPI

**Current Relevance:** Active for multi-repository environments. Enables gradual migration from legacy datastores to modern identity platforms without authentication interruption.

**What Replaces It:** Cloud identity platforms (Okta, Auth0, Azure AD) with SCIM provisioning for source-of-truth sync. Direct OIDC integration eliminates need for password storage in application-specific datastores.

**Migration Considerations:**

- Use DataStore as transitional abstraction during identity consolidation projects
- Migrate password hashing to modern algorithms (Argon2, scrypt) via gradual rehash-on-login
- Decommission redundant identity stores after federation establishes single authoritative source
- Avoid replicating passwords across multiple stores; use federation instead

## Certificate-Based Authentication

### X.509 Client Certificates

**Problem Solved:** Phishing-resistant mutual TLS authentication. Eliminates password transmission by proving possession of private key corresponding to certificate's public key. Binds authentication to specific device (hardware-backed keys prevent credential theft).

**Technical Flow:**

1. TLS handshake between client and server negotiates mutual authentication
2. Server requests client certificate via CertificateRequest message
3. Client presents certificate chain from browser/OS keystore
4. Server validates certificate: issuer trust (CA chain), validity period, revocation status (CRL/OCSP)
5. Client proves private key possession via CertificateVerify signature
6. Authentication module extracts certificate DN or Subject Alternative Name (SAN)
7. Maps certificate identity to user account (DN matching, LDAP lookup via serialNumber, email in SAN)

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-cert/`
- **Key Classes:**
  - `com.sun.identity.authentication.modules.cert.Cert`
  - `CertAuthPrincipal` - Principal representing certificate subject
- **Certificate Extraction:** From `javax.servlet.request.X509Certificate` attribute (requires TLS termination at OpenAM or reverse proxy passing cert headers)
- **Validation:** Java PKIX APIs (`CertPathValidator`), optional CRL/OCSP checks

**Current Relevance:** Resurging in zero-trust architectures. Device-bound certificates (TPM/Secure Enclave) prevent lateral movement after compromise. Federal agencies (PIV/CAC cards) and enterprises (YubiKey, smartcards) use certificate authentication for high-assurance access.

**What Replaces It:** WebAuthn/FIDO2 subsumes client certificate authentication with better UX (biometric unlock vs. PIN entry). However, traditional mTLS certificates remain dominant for service-to-service authentication in microservices (Istio, Linkerd service mesh).

**Migration Considerations:**

- Issue certificates with hardware-backed private keys (TPM 2.0, Secure Enclave, YubiKey)
- Use short validity periods (90 days) with automated rotation via ACME protocol
- Implement certificate-based step-up authentication for privileged operations
- Plan for WebAuthn migration for user-facing authentication while retaining mTLS for services
- Handle certificate revocation gracefully (OCSP stapling, short-lived certificates)

### Mutual TLS (mTLS)

**Problem Solved:** Bidirectional authentication for service-to-service communication. Both client and server prove identity via certificates, establishing encrypted authenticated channel without shared secrets.

**Technical Flow:**

Identical to X.509 client certificates but symmetric (both parties present certificates). In microservices:

1. Service A initiates connection to Service B
2. Service B presents server certificate (validates identity of backend)
3. Service B requests client certificate (validates identity of caller)
4. Both parties validate peer certificates against trusted CA bundles
5. Application-layer authorization checks certificate attributes (SANs, organization)

**OIP Implementation:**

Supported at infrastructure level rather than authentication module:

- **OpenAM OAuth2 Endpoints:** Client certificate binding for token issuance (RFC 8705 OAuth 2.0 mTLS)
- **OpenDJ Replication:** mTLS for changelog replication between data centers
- **OpenICF Connector Server:** mTLS for remote connector communication

**Current Relevance:** Standard practice in service mesh architectures. Kubernetes clusters use mTLS via SPIFFE/SPIRE for workload identity. Increasing adoption driven by zero-trust mandate for lateral movement prevention.

**What Replaces It:** Nothing. mTLS is the current state-of-the-art for service authentication. OAuth2 mTLS (RFC 8705) combines bearer tokens with certificate-bound proof-of-possession.

**Migration Considerations:**

- Automate certificate lifecycle via service mesh control plane or internal CA (cert-manager, Vault PKI)
- Use short-lived certificates (hours to days) rather than revocation
- Implement certificate rotation without service restart (hot reload)
- Monitor certificate expiry via Prometheus exporters
- Use mTLS for east-west traffic, OIDC/OAuth2 for north-south (user-to-service)

## One-Time Passwords (OTP)

### HOTP (HMAC-Based OTP, RFC 4226)

**Problem Solved:** Time-independent second factor. Counter-based OTP survives clock skew and offline validation. Prevents password replay attacks via single-use codes.

**Technical Flow:**

1. During enrollment, server generates random shared secret (160-256 bits)
2. Shared secret provisioned to user device (QR code, manual entry, hardware token)
3. Authentication attempt: user increments counter (device-side), computes HMAC-SHA1(secret, counter), truncates to 6-8 digits
4. Server-side validation: computes HMAC for counter window (current ± look-ahead window, e.g., 5)
5. On match, server updates stored counter to prevent replay
6. Failed validation: counter desynchronization requires resync procedure

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-hotp/`
- **Key Classes:**
  - `com.sun.identity.authentication.modules.hotp.HOTP`
  - `HOTPAlgorithm` - RFC 4226 HMAC truncation
  - `SMSGateway` interface, `DefaultSMSGatewayImpl` - SMS delivery for counter resync
- **Storage:** Shared secret and counter stored in user LDAP attributes

**Current Relevance:** Largely superseded by TOTP. HOTP hardware tokens (RSA SecurID, YubiKey OTP mode) still deployed in high-security environments where network isolation prevents time sync.

**What Replaces It:** TOTP (time-based, no counter desync issues), WebAuthn (phishing-resistant), push notifications (better UX).

**Migration Considerations:**

- Replace HOTP with TOTP for software tokens (Google Authenticator, Authy)
- Retain HOTP for hardware tokens until WebAuthn/FIDO2 keys available
- Implement counter resync UX (multi-code validation to detect offset)
- Plan sunset timeline aligned with hardware token refresh cycle (typically 3-5 years)

### TOTP (Time-Based OTP, RFC 6238) / OATH

**Problem Solved:** Time-synchronized OTP eliminates counter desynchronization. 30-second time window balances security (short validity) with usability (clock skew tolerance).

**Technical Flow:**

1. Enrollment: generate shared secret, provision to authenticator app via `otpauth://totp/` URI
2. Authentication: compute HMAC-SHA1(secret, floor(current_time / 30)), truncate to 6 digits
3. Server validation: accept codes from current time window and ±1 window (90-second total validity)
4. Time skew detection: track validation offsets, adjust server-side window if drift detected

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-oath/`
- **Key Classes:**
  - `org.forgerock.openam.authentication.modules.oath.OATH`
  - `TOTPAlgorithm` - RFC 6238 time-based computation
  - `SharedSecretProvider` interface, `DefaultSharedSecretProvider` - Secret storage abstraction
- **Configurable Parameters:** Time step (default 30s), code length (6 or 8 digits), HMAC algorithm (SHA-1/SHA-256/SHA-512)

**Current Relevance:** Dominant software-based second factor. Every major service (Google, Microsoft, GitHub, AWS) supports TOTP. Authenticator apps (Google Authenticator, Microsoft Authenticator, Authy, 1Password) achieve broad adoption.

**What Replaces It:** WebAuthn/passkeys provide phishing resistance TOTP lacks. TOTP remains vulnerable to real-time phishing (attacker proxies code immediately after user entry). However, TOTP persists due to zero infrastructure requirements (no push notification service, no WebAuthn browser support dependencies).

**Migration Considerations:**

- TOTP remains recommended second factor for next 5+ years
- Combine with adaptive authentication (risk-based step-up)
- Educate users on phishing risks (adversary-in-the-middle attacks bypass TOTP)
- Offer WebAuthn as alternative for security-conscious users
- Use TOTP as backup authentication method if primary WebAuthn credential lost

### Push Notifications

**Problem Solved:** Superior UX compared to code entry. User taps "Approve" on mobile device instead of typing 6-digit code. Enables context display (IP address, location, device) for informed approval decision.

**Technical Flow:**

1. User initiates login on desktop browser
2. OpenAM generates push challenge, stores pending authentication request
3. Push notification sent to registered mobile device (via APNs/FCM)
4. User sees login context: "Login from Chrome on Windows, IP 203.0.113.42, New York"
5. User approves/denies
6. Mobile app sends signed approval to OpenAM
7. Desktop session established on approval

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-push/`
- **Key Classes:**
  - `org.forgerock.openam.authentication.modules.push.AbstractPushModule`
  - `AuthenticatorPushRegistration` - Device enrollment
  - `UserPushDeviceProfileManager` - Multi-device management
- **Push Delivery:** APNs (iOS), FCM (Android), WebSockets (fallback)

**Current Relevance:** Active and growing. Microsoft Authenticator, Duo Mobile, Okta Verify, Authy achieve high enterprise adoption. Better UX than TOTP drives user preference.

**What Replaces It:** WebAuthn/passkeys eliminate separate approval step (biometric authentication embedded in primary authentication flow). However, push notifications remain valuable for high-risk transaction approval (financial transfers, privilege escalation).

**Migration Considerations:**

- Push notifications vulnerable to "notification fatigue" attacks (bombard user until accidental approval)
- Implement number matching (display 2-digit code on desktop, user enters on mobile)
- Use push as passwordless primary authentication (not just second factor)
- Plan WebAuthn migration for phishing resistance
- Retain push for out-of-band transaction approval

## Legacy Token Systems

### RADIUS

**Problem Solved:** Network access authentication for dial-up, VPN, Wi-Fi (802.1X). Centralizes credential validation for network infrastructure devices (switches, wireless controllers, VPN gateways) lacking integrated LDAP clients.

**Technical Flow:**

1. User attempts network connection (Wi-Fi association, VPN dial)
2. Network Access Server (NAS) sends Access-Request to RADIUS server (UDP port 1812)
3. OpenAM RADIUS module receives request, extracts username/password
4. Validates credentials against configured backend (LDAP, DataStore)
5. Returns Access-Accept (with VLAN assignment, session timeout) or Access-Reject
6. NAS grants/denies network access based on response
7. Accounting records sent to RADIUS accounting port (UDP 1813)

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-radius/`
- **Key Classes:**
  - `com.sun.identity.authentication.modules.radius.RADIUS`
  - `RADIUSServer` - Protocol handler
  - `RadiusConn` - UDP socket management
  - `ChallengeException`, `RejectException` - Multi-round auth flow
- **Configuration:** Primary/secondary server, shared secret, timeout (default 5s)

**Current Relevance:** Active but aging. RADIUS ubiquitous for Wi-Fi (WPA2-Enterprise via 802.1X), VPN, switch management. However, fundamental security issues (MD5-based, shared secrets, UDP) drive migration to modern protocols.

**What Replaces It:** RadSec (RFC 6614, RADIUS over TLS) addresses transport security. Long-term replacement: OAuth2/OIDC for application access, 802.1X with EAP-TLS (certificate-based) for network access, SAML/OIDC federation for VPN.

**Migration Considerations:**

- RADIUS remains essential for network infrastructure (switches, APs) lacking modern auth protocols
- Deploy RadSec gateways for encrypted RADIUS communication
- Use EAP-TLS (certificate-based) instead of EAP-PEAP (password-based) for Wi-Fi
- Migrate VPN authentication to OIDC/SAML (supported by modern VPN solutions like Zscaler, Cloudflare Access)
- Plan 5-10 year sunset timeline aligned with network hardware refresh

### RSA SecurID

**Problem Solved:** Hardware token-based OTP predating TOTP standardization. Time-synchronized token displays 6-digit code refreshing every 60 seconds. Server validates code against synchronized token seed.

**Technical Flow:**

1. User receives hardware token (key fob) with embedded seed value
2. Token displays time-based code (proprietary algorithm, not TOTP)
3. User enters PIN + token code during authentication
4. OpenAM forwards authentication request to RSA Authentication Manager via proprietary protocol
5. RSA server validates code against token database
6. Returns success/failure to OpenAM

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-securid/`
- **Integration:** RSA SecureID agent library (proprietary binary)
- **Limitation:** Requires RSA Authentication Manager infrastructure

**Current Relevance:** Declining. RSA SecurID still deployed in regulated industries (finance, defense) with legacy hardware token inventory. High TCO (token procurement, battery replacement, user training) drives migration.

**What Replaces It:** TOTP (software tokens eliminate hardware costs), WebAuthn/FIDO2 (security keys like YubiKey provide hardware-backed auth without battery issues), push notifications (better UX).

**Migration Considerations:**

- Replace hardware tokens at end-of-battery-life (typically 3-5 years)
- Offer TOTP/push/WebAuthn alternatives for new users
- Migrate RSA Authentication Manager dependency to OpenAM native TOTP module
- Plan complete sunset within 5 years to eliminate licensing costs

## Modern Passwordless

### WebAuthn / FIDO2

**Problem Solved:** Phishing-resistant passwordless authentication. Public key cryptography eliminates shared secrets (no password database to breach). Origin binding prevents credential use on phishing sites (cryptographic proof credential only valid for legitimate domain).

**Technical Flow:**

**Registration (Credential Creation):**

1. User initiates registration on website (clicks "Register passkey")
2. Server generates challenge (random bytes)
3. JavaScript invokes `navigator.credentials.create({ publicKey: { challenge, rp, user, ... } })`
4. Browser prompts user for biometric (Touch ID, Face ID, Windows Hello) or security key
5. Authenticator generates key pair (private key stored in hardware, public key returned)
6. Authenticator creates attestation signature proving authentic hardware
7. Server validates attestation, stores public key + credential ID

**Authentication (Assertion):**

1. User initiates login
2. Server generates challenge
3. JavaScript invokes `navigator.credentials.get({ publicKey: { challenge, allowCredentials, ... } })`
4. Browser/authenticator locates credential for origin
5. User performs biometric/PIN verification
6. Authenticator signs challenge with private key
7. Server validates signature using stored public key

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-webauthn/`
- **Key Classes:**
  - `org.openidentityplatform.openam.authentication.modules.webauthn.WebAuthnAuthentication`
  - `WebAuthnRegistration` - Credential enrollment flow
  - `WebAuthnAuthenticationProcessor` - Assertion validation
  - `WebAuthnRegistrationProcessor` - Attestation validation
  - `Base64Utils` - Credential data encoding
- **Storage:** Credential ID, public key, signature counter stored in user profile

**Current Relevance:** Rapid adoption trajectory. W3C Recommendation (2019), supported in all major browsers (Chrome, Safari, Firefox, Edge). Apple/Google/Microsoft shipped synced passkey support (2022-2023). GitHub, Google, Microsoft, PayPal, Best Buy, eBay, Shopify offer passkey login.

**What Replaces It:** Nothing imminent. WebAuthn represents current state-of-the-art for user authentication. Future enhancements (WebAuthn Level 3) add features without replacing core protocol.

**Migration Considerations:**

- Implement WebAuthn as optional authentication method alongside existing flows
- Offer security keys (YubiKey, Titan) for device-bound credentials (enterprise use cases)
- Enable synced passkeys (iCloud Keychain, Google Password Manager) for consumer convenience
- Require WebAuthn for privileged access (admin consoles, financial transactions)
- Plan 5-year timeline for password elimination in favor of passkeys
- Handle recovery scenarios (lost device, no backup passkey)

### Passkeys (Synced WebAuthn Credentials)

**Problem Solved:** WebAuthn credential portability. Traditional WebAuthn credentials tied to single device; passkeys sync across user's devices via platform credential manager (iCloud Keychain, Google Password Manager). Survives device loss without backup codes.

**Technical Flow:**

Identical to WebAuthn with credential synchronization layer:

1. User registers passkey on iPhone
2. Private key stored in iCloud Keychain (encrypted, synced to user's other Apple devices)
3. User logs in on Mac: credential available without re-enrollment
4. Cross-device authentication: QR code + Bluetooth proximity for non-synced devices

**Platform Support:**

- **Apple:** iOS 16+, macOS Ventura+, iCloud Keychain sync
- **Google:** Android 9+, Chrome, Google Password Manager sync
- **Microsoft:** Windows 11 23H2+, Windows Hello, Microsoft account sync
- **Third-party:** 1Password, Dashlane, Bitwarden (passkey storage/sync)

**OIP Implementation:**

Uses same WebAuthn module (`openam-auth-webauthn`). No protocol-level difference; passkey sync handled by platform.

**Current Relevance:** Mainstream adoption accelerating. Apple/Google ecosystem users automatically gain passkey support. Industry consensus: passkeys represent future of consumer authentication.

**What Replaces It:** Nothing on horizon. Passkeys solve WebAuthn's device portability limitation while preserving phishing resistance.

**Migration Considerations:**

- No implementation differences from WebAuthn (server-side)
- User education: "Save passkey" vs. "Register security key" terminology
- Offer both synced passkeys (convenience) and device-bound keys (high assurance)
- Monitor passkey adoption metrics to inform password sunset timeline
- Plan account recovery flows (device-bound backup passkey, TOTP fallback)

## Social and Federated Authentication

### OAuth2 Social Login

**Problem Solved:** Delegate authentication to existing identity providers (Google, Facebook, GitHub, Microsoft). Eliminates password management burden. Reduces registration friction (no new account creation).

**Technical Flow:**

1. User clicks "Sign in with Google" on application
2. Application redirects to Google OAuth2 authorization endpoint with client_id, redirect_uri, scope
3. User authenticates to Google (if not already logged in)
4. Google prompts consent for requested scopes (email, profile)
5. User approves; Google redirects to application callback with authorization code
6. Application exchanges code for access token (backend request with client_secret)
7. Application calls Google UserInfo endpoint with access token
8. Retrieves user profile (email, name, picture)
9. Application creates/updates local user account, establishes session

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-oauth2/`
- **Key Classes:**
  - `OAuthProxy` - Generic OAuth2 flow handler
  - `ProfileProvider` - Provider-specific profile mapping
  - `EmailGateway` - Email verification for account linking
- **Supported Providers:** Configurable endpoints support any OAuth2 provider (Google, Facebook, GitHub, Azure AD, Okta)
- **Configuration:** Client ID/secret, authorization/token/userinfo endpoints, scope, attribute mapping

**Current Relevance:** Dominant consumer authentication pattern. Estimated 70%+ of consumer websites offer social login. Enterprise adoption via "Login with Microsoft" for B2B SaaS.

**What Replaces It:** OpenID Connect (OAuth2 extension with standardized identity layer). OIDC provides ID tokens (JWT with user claims) instead of requiring separate UserInfo call. Most "social login" implementations now use OIDC instead of bare OAuth2.

**Migration Considerations:**

- Prefer OIDC over OAuth2 for new integrations (standardized claims, ID token validation)
- Implement account linking flow (associate existing account with social identity)
- Privacy considerations: minimize requested scopes, explain data usage
- Handle provider account deletion/deactivation (webhook notifications)
- Offer multiple social providers to avoid vendor lock-in

### OpenID Connect (OIDC) as Authentication Module

**Problem Solved:** Standardized authentication delegation. OIDC adds identity layer on OAuth2: ID token (signed JWT with user claims), UserInfo endpoint, Discovery metadata, Dynamic Registration. Enables authentication federation without SAML complexity.

**Technical Flow:**

Similar to OAuth2 social login with ID token addition:

1. Redirect to OIDC provider with `response_type=code`, `scope=openid email profile`
2. Provider authentication + consent
3. Authorization code returned to callback
4. Exchange code for access token + ID token (JWT)
5. Validate ID token signature, issuer, audience, expiration
6. Extract claims from ID token: `sub` (subject identifier), `email`, `name`, `picture`, etc.
7. Optional: call UserInfo endpoint for additional claims
8. Establish session based on validated identity

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-oidc/`
- **Key Classes:**
  - `org.forgerock.openam.authentication.modules.oidc.OpenIdConnectConfig`
  - `JwtHandlerConfig` - JWT signature validation
  - `JwtAttributeMapper` - Claim-to-attribute mapping
  - `OpenIdConnectToken` - ID token representation
- **Discovery:** Automatic configuration via `/.well-known/openid-configuration`

**Current Relevance:** Industry standard for federation. Replacing SAML for new integrations. Cloud IdPs (Okta, Auth0, Azure AD, Google Cloud Identity) default to OIDC. Education (InCommon, eduGAIN) adding OIDC alongside SAML.

**What Replaces It:** Nothing. OIDC is current-generation protocol. Future enhancements (OIDC Federation for automatic trust, SIOP for self-issued credentials) build on OIDC foundation.

**Migration Considerations:**

- Use OIDC for new authentication integrations (not SAML)
- Migrate existing SAML integrations to OIDC where provider supports both
- Implement OIDC Provider role in OpenAM to service OIDC clients
- Use Authorization Code + PKCE flow (never Implicit flow)
- Validate ID token signatures using provider's JWKS endpoint

## Adaptive and Risk-Based Authentication

### Risk-Based Authentication

**Problem Solved:** Context-aware authentication decisions. Low-risk scenarios (known device, known location) allow password-only authentication. High-risk scenarios (new device, suspicious location, impossible travel) trigger step-up authentication (MFA requirement).

**Technical Flow:**

1. User initiates authentication
2. Adaptive module collects context signals:
   - Device fingerprint (browser, OS, screen resolution)
   - IP address geolocation
   - Time of day
   - Velocity checks (location changes, login frequency)
   - Threat intelligence (known bot IPs, Tor exit nodes)
3. Risk scoring algorithm computes aggregate risk (0-100)
4. Policy decision based on risk score:
   - Low (0-30): password only
   - Medium (31-70): password + TOTP
   - High (71-100): password + TOTP + push approval, or deny access
5. Log risk score for analytics/tuning

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-adaptive/`
- **Risk Scoring:** Pluggable risk evaluators
- **Integration:** Combines with device fingerprinting module (`openam-auth-device-id`)

**Current Relevance:** Standard practice for consumer-facing applications. Microsoft, Google, Apple, financial institutions use adaptive authentication extensively. Regulatory drivers: PSD2 Strong Customer Authentication (SCA), NIST SP 800-63B Authenticator Assurance Levels.

**What Replaces It:** Continuous authentication (CAEP - Continuous Access Evaluation Protocol). Instead of point-in-time risk assessment, continuous monitoring revokes sessions on risk change (e.g., session token revocation when device reports compromise).

**Migration Considerations:**

- Start with logging mode (collect risk signals without enforcement)
- Tune risk thresholds based on observed false positive/negative rates
- Combine with CAEP/Shared Signals for real-time session termination
- Implement user feedback loop ("Not you? Secure your account")
- Privacy considerations: minimize PII collection for risk scoring

### Device Fingerprinting

**Problem Solved:** Device recognition without cookies or persistent storage. Combines browser/device attributes into stable identifier. Enables "trusted device" authentication bypass (no MFA on recognized devices).

**Technical Flow:**

1. JavaScript collects device attributes: User-Agent, screen resolution, timezone, fonts, canvas fingerprint, WebGL renderer, audio context, installed plugins
2. Attributes hashed into fingerprint (e.g., MurmurHash of concatenated values)
3. Fingerprint stored in user profile (LDAP attribute) or external datastore
4. Future authentication: compute fingerprint, compare against stored values
5. Match: recognize device, skip MFA
6. No match: new device, require full authentication

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-device-id/`
- **Key Classes:**
  - `org.forgerock.openam.authentication.modules.deviceprint.DeviceIdMatch`
  - `DevicePrintDao` - Fingerprint storage abstraction
  - `ProfilePersister` - Device profile persistence
  - `PersistModuleProcessor`, `DeviceIdSave` - Enrollment flow
- **Fingerprint Components:** User-Agent, screen dimensions, timezone, installed fonts, canvas/WebGL signatures

**Current Relevance:** Widespread but increasingly fragile. Privacy-focused browsers (Safari, Firefox, Brave) actively resist fingerprinting via randomization and API blocking. iOS/iPadOS fingerprinting severely limited.

**What Replaces It:** Platform-native device attestation (iOS App Attest, Android SafetyNet/Play Integrity, Windows TPM attestation). WebAuthn credentials provide cryptographic device binding without fingerprinting fragility.

**Migration Considerations:**

- Use device fingerprinting as weak signal (not security control)
- Combine with persistent cookie (Secure, HttpOnly, SameSite=Strict)
- Plan migration to WebAuthn device-bound credentials
- Handle fingerprint mismatch gracefully (don't lock out legitimate users)
- Privacy compliance: disclose fingerprinting in privacy policy

### Scripted Authentication

**Problem Solved:** Custom authentication flows without Java compilation. Groovy/JavaScript execution enables dynamic decision trees, external API calls, complex business logic unavailable in standard modules.

**Technical Flow:**

1. Administrator uploads Groovy/JavaScript authentication script via OpenAM console
2. Script has access to request context, session, HTTP client, LDAP queries
3. Authentication flow:
   - Script prompts for username/password via callbacks
   - Validates credentials against LDAP
   - Calls risk API to compute fraud score
   - Decides: allow, deny, or step-up to MFA based on API response
4. Script sets authentication level, session properties, user attributes

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-authentication/openam-auth-scripted/`
- **Key Classes:**
  - `org.forgerock.openam.authentication.modules.scripted.Scripted`
  - `ScriptIdentityRepository` - Identity store access from scripts
  - `ScriptedClientUtilityFunctions` - HTTP client for external API calls
  - `ScriptHttpRequestWrapper` - Request object access
- **Language Support:** Groovy, JavaScript (Nashorn/GraalVM)
- **Sandboxing:** Limited for security (no file I/O, restricted Java class access)

**Current Relevance:** Active for complex enterprise authentication flows. Enables rapid prototyping and business logic customization without deployment cycles.

**What Replaces It:** Authentication trees/journeys (visual flow designer). ForgeRock Access Management (commercial OpenAM successor) replaces scripted auth with declarative authentication trees. However, scripted auth remains necessary for edge cases tree model cannot express.

**Migration Considerations:**

- Use scripted authentication sparingly (difficult to test, debug, maintain)
- Prefer declarative configuration (authentication chains, policy conditions)
- Version control scripts in Git
- Implement script validation/testing pipeline
- Monitor script execution time (timeout-prone)
- Plan migration to authentication trees if upgrading to commercial ForgeRock AM

## Protocol Relevance Summary

| Protocol | Current Status | Migration Timeline | Replacement Technology |
|----------|----------------|-------------------|------------------------|
| LDAP Bind | Active, ubiquitous | 10+ years | OIDC with LDAP backing store |
| Active Directory | Active, essential | 10+ years (hybrid) | Azure AD/Entra ID federation |
| DataStore | Active, transitional | 5 years | Cloud IdP with SCIM sync |
| X.509 Certificates | Resurging (zero-trust) | Not applicable | WebAuthn for users, mTLS for services |
| HOTP | Declining | 3-5 years | TOTP, WebAuthn |
| TOTP | Dominant | 5-10 years | WebAuthn/passkeys |
| Push Notifications | Growing | Not applicable | WebAuthn (long-term) |
| RADIUS | Active, aging | 5-10 years | RadSec, OIDC for VPN |
| RSA SecurID | Declining | 3-5 years | TOTP, WebAuthn |
| WebAuthn/FIDO2 | Rapid adoption | Current standard | None imminent |
| Passkeys | Accelerating | Current standard | None imminent |
| OAuth2 Social | Dominant | Not applicable | OIDC (already transitioning) |
| OIDC | Industry standard | Current standard | None imminent |
| Adaptive Auth | Standard practice | Current standard | Continuous evaluation (CAEP) |
| Device Fingerprinting | Fragile | 3-5 years | WebAuthn device binding |
| Scripted Auth | Niche | Ongoing | Authentication trees/journeys |

## Cross-References

- **Token Formats:** See Chapter 6 for JWT, SAML assertion, and CTS token implementation details
- **Federation Protocols:** See Chapter 3 for SAML 2.0, OIDC as federation protocol (vs. authentication module)
- **Authorization:** See Chapter 4 for OAuth2 authorization flows, XACML policy evaluation
- **Modern Architecture:** See Chapter 12 for authentication's role in zero-trust continuous verification
