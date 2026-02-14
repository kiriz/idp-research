# Chapter 6: Token Formats and Session Management

Tokens are the currency of modern identity systems, conveying authentication proof, authorization grants, and session state across network boundaries. This chapter examines the major token formats used in IAM: SAML assertions (XML-based federation tokens), JWT (JSON Web Tokens for OAuth2 and OIDC), CTS tokens (OpenAM's opaque session tokens), OAuth2 access/refresh tokens, and emerging formats for enhanced security. Each format reflects different design philosophies around token transparency, security properties, and interoperability trade-offs.

![Token Format Evolution and Lifecycle](../diagrams/10-token-lifecycle.png)

## SAML Assertions: XML-Based Federation Tokens

Security Assertion Markup Language (SAML) assertions are XML-encoded security tokens that convey authentication statements, authorization decisions, and user attributes. SAML 2.0 (OASIS, 2005) remains the dominant enterprise federation protocol nearly two decades after standardization.

### XML Structure and Components

SAML assertions are digitally signed XML documents following a formal schema. The top-level structure:

```xml
<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                ID="_abc123def456"
                Version="2.0"
                IssueInstant="2025-02-13T14:30:00Z">
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <!-- XML Digital Signature (XML-DSig) -->
  </ds:Signature>
  <saml:Subject>
    <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
      alice@example.com
    </saml:NameID>
    <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
      <saml:SubjectConfirmationData NotOnOrAfter="2025-02-13T14:35:00Z"
                                    Recipient="https://sp.example.com/acs"
                                    InResponseTo="_request123"/>
    </saml:SubjectConfirmation>
  </saml:Subject>
  <saml:Conditions NotBefore="2025-02-13T14:30:00Z"
                   NotOnOrAfter="2025-02-13T14:35:00Z">
    <saml:AudienceRestriction>
      <saml:Audience>https://sp.example.com</saml:Audience>
    </saml:AudienceRestriction>
  </saml:Conditions>
  <saml:AuthnStatement AuthnInstant="2025-02-13T14:30:00Z"
                       SessionIndex="_session123">
    <saml:AuthnContext>
      <saml:AuthnContextClassRef>
        urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
      </saml:AuthnContextClassRef>
    </saml:AuthnContext>
  </saml:AuthnStatement>
  <saml:AttributeStatement>
    <saml:Attribute Name="email">
      <saml:AttributeValue>alice@example.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="groups">
      <saml:AttributeValue>Engineering</saml:AttributeValue>
      <saml:AttributeValue>Managers</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="employeeNumber">
      <saml:AttributeValue>12345</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

**Core assertion components:**

**Issuer**: Identity provider (IdP) that created the assertion. Identifies the authority vouching for the assertion's validity.

**Subject**: The principal (user) the assertion is about. Contains:

- **NameID**: Principal identifier. Format options:
  - `emailAddress`: Email address (alice@example.com)
  - `persistent`: Opaque persistent identifier (same user, same identifier across sessions)
  - `transient`: Session-specific identifier (changes per session, privacy-preserving)
  - `unspecified`: Free-form identifier
  - `X509SubjectName`: X.509 certificate subject DN
  - `WindowsDomainQualifiedName`: Windows domain account (DOMAIN\user)
  - `Kerberos`: Kerberos principal name (user@REALM)
  - `entity`: Entity identifier (for non-human subjects)

- **SubjectConfirmation**: Proof that the subject legitimately holds the assertion. Methods:
  - `bearer`: Holder of assertion is the subject (no additional proof required). Most common for web SSO.
  - `holder-of-key`: Subject must prove possession of a cryptographic key. Used for advanced security scenarios.
  - `sender-vouches`: Third party vouches for subject (rare).

**Conditions**: Constraints on assertion validity:

- **NotBefore**: Earliest time assertion is valid (prevents premature use)
- **NotOnOrAfter**: Expiration time (typically 5 minutes after issuance)
- **AudienceRestriction**: Service provider(s) for which assertion is intended. SP must verify it is in audience list.
- **OneTimeUse**: Assertion can only be consumed once (prevents replay attacks)
- **ProxyRestriction**: Limits how many times assertion can be re-issued (prevents infinite delegation chains)

**Statements**: Assertions can contain three types of statements:

**AuthnStatement**: Authentication event information:

- **AuthnInstant**: When user authenticated to IdP
- **SessionIndex**: IdP session identifier (used for Single Logout)
- **AuthnContext**: Authentication method:
  - `PasswordProtectedTransport`: Username/password over TLS
  - `TLSClient`: Client certificate authentication
  - `Kerberos`: Kerberos authentication
  - `MobileOneFactorUnregistered`: SMS OTP to unregistered number
  - `MobileTwoFactorUnregistered`: Two-factor mobile auth
  - Custom URIs for proprietary authentication methods

**AttributeStatement**: User attributes (claims):

- Name-value pairs conveying user profile data
- Attributes: email, groups, roles, employeeNumber, department, etc.
- Multi-valued attributes supported (e.g., multiple group memberships)
- Service provider uses attributes for authorization, personalization, provisioning

**AuthzDecisionStatement**: Authorization decision (rarely used):

- Resource being accessed
- Action requested (read, write, execute)
- Decision: Permit, Deny, Indeterminate
- Largely superseded by policy engines (XACML, OPA)

### XML Digital Signature (XML-DSig)

SAML assertions are secured via XML Digital Signature (XML-DSig, W3C Recommendation). The signature:

- **Authenticates** the issuer (proves assertion came from claimed IdP)
- **Provides integrity** (detects tampering)
- **Enables non-repudiation** (issuer cannot deny creating assertion)

XML-DSig structure within SAML assertion:

```xml
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
  <ds:SignedInfo>
    <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
    <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
    <ds:Reference URI="#_abc123def456">
      <ds:Transforms>
        <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      </ds:Transforms>
      <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
      <ds:DigestValue>base64-encoded-digest</ds:DigestValue>
    </ds:Reference>
  </ds:SignedInfo>
  <ds:SignatureValue>base64-encoded-signature</ds:SignatureValue>
  <ds:KeyInfo>
    <ds:X509Data>
      <ds:X509Certificate>base64-encoded-certificate</ds:X509Certificate>
    </ds:X509Data>
  </ds:KeyInfo>
</ds:Signature>
```

**Signature verification process:**

```
1. Extract <ds:Signature> element from assertion
2. Retrieve signing certificate from <ds:KeyInfo> or metadata
3. Validate certificate:
   - Check certificate chain to trusted root CA
   - Verify certificate not expired
   - Check certificate revocation status (CRL/OCSP)
4. Extract <ds:SignedInfo> (canonical form of signed content)
5. Compute digest of signed content using DigestMethod algorithm (SHA-256)
6. Compare computed digest with <ds:DigestValue>
7. Verify signature using public key from certificate:
   - Decrypt <ds:SignatureValue> using public key
   - Compare decrypted hash with computed digest
8. If all checks pass: signature valid, assertion trusted
```

**Canonicalization (c14n)**: XML allows multiple equivalent representations (whitespace, attribute order, namespace prefixes). Canonicalization normalizes XML to a unique byte sequence before hashing. Essential for consistent signature verification. Exclusive C14N (`xml-exc-c14n`) is preferred for SAML.

**Algorithm choices:**

- **Signing algorithm**: RSA-SHA256 (most common), RSA-SHA512, ECDSA-SHA256
- **Digest algorithm**: SHA-256 (current standard), SHA-512 (higher security)
- **Legacy algorithms** (deprecated): RSA-SHA1, MD5 (cryptographically broken)

### XML Encryption (XML-Enc)

Sensitive attributes can be encrypted using XML Encryption (XML-Enc, W3C Recommendation). Encryption prevents intermediaries (browsers, proxies) from reading assertion contents.

**Encrypted assertion structure:**

```xml
<saml:EncryptedAssertion>
  <xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"
                      Type="http://www.w3.org/2001/04/xmlenc#Element">
    <xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes256-cbc"/>
    <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <xenc:EncryptedKey>
        <xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"/>
        <xenc:CipherData>
          <xenc:CipherValue>base64-encoded-encrypted-key</xenc:CipherValue>
        </xenc:CipherData>
      </xenc:EncryptedKey>
    </ds:KeyInfo>
    <xenc:CipherData>
      <xenc:CipherValue>base64-encoded-encrypted-assertion</xenc:CipherValue>
    </xenc:CipherData>
  </xenc:EncryptedData>
</saml:EncryptedAssertion>
```

**Encryption process (hybrid cryptography):**

```
1. Generate random symmetric key (AES-256)
2. Encrypt assertion XML with symmetric key (AES-256-CBC)
3. Retrieve SP's public key from metadata
4. Encrypt symmetric key with SP's public key (RSA-OAEP)
5. Embed encrypted key and encrypted assertion in <EncryptedAssertion>
```

**Decryption process:**

```
1. SP extracts <EncryptedKey>
2. SP decrypts symmetric key using SP's private key (RSA-OAEP)
3. SP decrypts assertion using recovered symmetric key (AES-256-CBC)
4. SP parses decrypted XML and validates signature
```

**Selective encryption**: Instead of encrypting entire assertion, specific attributes can be encrypted:

```xml
<saml:Assertion>
  <!-- Unencrypted issuer, subject, conditions -->
  <saml:AttributeStatement>
    <saml:Attribute Name="email">
      <saml:AttributeValue>alice@example.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:EncryptedAttribute>
      <!-- Encrypted SSN attribute -->
    </saml:EncryptedAttribute>
    <saml:Attribute Name="department">
      <saml:AttributeValue>Engineering</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

This minimizes encryption overhead while protecting sensitive claims.

### OpenAM SAML Assertion Handling

OpenAM's SAML implementation is located in `OpenAM/openam-federation/openam-federation-library/` and `OpenAM/openam-federation/OpenFM/`.

**Core classes:**

**SAML2AssertionValidator** (`com.sun.identity.saml.servlet.`): Validates incoming SAML assertions:

- Signature verification (XML-DSig)
- Audience validation (Conditions/AudienceRestriction)
- Expiration check (NotBefore/NotOnOrAfter)
- Issuer trust validation (metadata-based)
- Subject confirmation validation (bearer, holder-of-key)

**SAML2Token** (`com.sun.identity.saml2.common.`): Object representation of SAML assertion. Provides API for:

- Extracting subject (NameID)
- Retrieving attributes
- Accessing authentication context
- Validating conditions

**SAML2CTSPersistentStore** (`org.forgerock.openam.cts.impl.`): Stores SAML artifacts and assertions in Core Token Service. Enables:

- Artifact resolution (POST Artifact binding)
- Assertion reuse (subject to OneTimeUse conditions)
- Session correlation (link SAML assertion to OpenAM session)

**SAML assertion creation flow in OpenAM:**

```
1. SP initiates SSO: redirect user to IdP with AuthnRequest
2. OpenAM receives AuthnRequest, authenticates user
3. OpenAM creates SAML assertion:
   a. Generate assertion ID (UUID)
   b. Set issuer: OpenAM entity ID from metadata
   c. Set subject: user's NameID (from attribute mapping config)
   d. Add AuthnStatement with authentication method and time
   e. Add AttributeStatement with user attributes (from LDAP, policy)
   f. Set conditions: NotBefore (now), NotOnOrAfter (now + 5 min)
   g. Add AudienceRestriction: SP entity ID
4. OpenAM signs assertion:
   a. Load IdP signing certificate from keystore
   b. Canonicalize assertion XML (Exclusive C14N)
   c. Compute SHA-256 digest
   d. Sign digest with RSA private key
   e. Embed signature in <ds:Signature> element
5. [Optional] Encrypt assertion with SP's public key
6. OpenAM creates SAMLResponse containing assertion
7. OpenAM signs SAMLResponse (second signature on response wrapper)
8. OpenAM POST SAMLResponse to SP's Assertion Consumer Service (ACS)
9. SP validates response signature, decrypts assertion, validates assertion
10. SP creates local session for user
```

**CTS storage for SAML artifacts:**

```
Token type: SAML2_ARTIFACT
Key: artifact ID (random opaque string)
Value: SAML assertion (XML serialized)
TTL: 5 minutes (matches assertion expiration)
```

When SP receives artifact (POST Artifact binding), it calls OpenAM's artifact resolution endpoint. OpenAM looks up artifact in CTS, retrieves assertion, returns to SP.

### Use Cases and Current Relevance

SAML assertions remain dominant for:

**1. Enterprise B2B SSO**: Cross-organization federation (partners, customers, suppliers). Long-term trust relationships with formal metadata exchange.

**2. Education federation**: InCommon (US), eduGAIN (global) use SAML for academic resource access. Millions of students authenticate via SAML to library databases, learning management systems, and research tools.

**3. Government federation**: FICAM (Federal Identity Credential and Access Management), eIDAS (EU) rely on SAML. SAML provides formal trust framework required by government regulations.

**4. Healthcare federation**: HEART working group profiles SAML for FHIR resource access. Patient consent, provider authentication, and health information exchange use SAML.

**5. SaaS application integration**: Thousands of SaaS applications (Salesforce, ServiceNow, Box, GitHub Enterprise) support SAML SSO as the primary enterprise integration method.

SAML is not declining. New SAML integrations continue to be deployed. However, greenfield consumer applications and API-first architectures prefer OIDC (lighter weight, JSON-based, better mobile support).

## JWT: JSON Web Tokens

JSON Web Token (JWT, RFC 7519, 2015) is a compact, URL-safe token format for conveying claims between parties. JWTs are used extensively in OAuth 2.0 (access tokens, ID tokens in OIDC) and modern session management.

### Structure: Header, Payload, Signature

JWT consists of three Base64URL-encoded sections separated by periods:

```
<header>.<payload>.<signature>
```

Example JWT:

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImlzcyI6Imh0dHBzOi8vaWRwLmV4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9hcGkuZXhhbXBsZS5jb20iLCJleHAiOjE3NjY0MTkyMDAsImlhdCI6MTc2NjQxNTYwMCwic2NvcGUiOiJyZWFkIHdyaXRlIn0.signature-bytes-base64url
```

**Header (decoded):**

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-2025-02"
}
```

- `alg`: Signing algorithm (RS256 = RSA-SHA256)
- `typ`: Token type ("JWT")
- `kid`: Key ID (identifies which key was used for signing, enables key rotation)

**Payload (decoded):**

```json
{
  "sub": "alice",
  "iss": "https://idp.example.com",
  "aud": "https://api.example.com",
  "exp": 1766419200,
  "iat": 1766415600,
  "scope": "read write",
  "groups": ["Engineering", "Managers"],
  "email": "alice@example.com"
}
```

- `sub` (subject): Principal identifier (user ID)
- `iss` (issuer): Token issuer (authorization server URL)
- `aud` (audience): Intended recipient(s) (resource server URL or client ID)
- `exp` (expiration): Unix timestamp after which token is invalid
- `iat` (issued at): Unix timestamp when token was created
- `nbf` (not before): Earliest time token is valid (optional)
- `jti` (JWT ID): Unique token identifier (for one-time use tokens)
- Custom claims: `scope`, `groups`, `email`, etc. (application-specific)

**Signature (RS256):**

```
signature = RSA-SHA256(
  base64url(header) + "." + base64url(payload),
  private_key
)
```

The signature binds header and payload, preventing tampering.

### Signing Algorithms (JWS)

JWT signing uses JSON Web Signature (JWS, RFC 7515). Common algorithms:

**Symmetric (HMAC):**

- **HS256** (HMAC-SHA256): Shared secret between issuer and verifier. Fast, but requires secure secret distribution. Suitable for single-application scenarios (issuer = verifier).
- **HS384**, **HS512**: Variants with SHA-384, SHA-512.

**Asymmetric (RSA):**

- **RS256** (RSA-SHA256): RSA signature with SHA-256. Most common for OAuth2/OIDC. Public key for verification can be distributed via JWKS (JSON Web Key Set) endpoint.
- **RS384**, **RS512**: Variants with SHA-384, SHA-512.
- **PS256** (RSA-PSS-SHA256): RSA signature with PSS padding. More secure than PKCS#1 v1.5 padding (used by RS256). Increasingly recommended.

**Asymmetric (ECDSA):**

- **ES256** (ECDSA-P256-SHA256): Elliptic curve signature. Smaller signatures than RSA (same security level). Preferred for bandwidth-constrained environments (mobile, IoT).
- **ES384** (P-384), **ES512** (P-521): Higher security curves.

**EdDSA:**

- **EdDSA** (RFC 8032): Ed25519 elliptic curve. Faster than ECDSA, deterministic signatures (no random number generation risk). Growing adoption (supported in RFC 8037).

**None algorithm:**

- **none**: No signature (unsecured JWT). Header: `{"alg":"none"}`. Payload and header are Base64URL-encoded, but signature is empty string. Used for debugging or public (non-sensitive) data. **Security risk**: Verifiers must explicitly reject `alg=none` unless unsecured JWTs are intentionally allowed.

**Signature verification process (RS256):**

```
1. Split JWT into header, payload, signature
2. Base64URL-decode header, parse JSON
3. Extract `alg` (RS256), `kid` (key ID)
4. Retrieve public key:
   - Fetch JWKS from issuer's /.well-known/jwks.json
   - Find key matching `kid`
   - Parse RSA public key (n, e modulus/exponent)
5. Base64URL-decode signature
6. Compute signing input: base64url(header) + "." + base64url(payload)
7. Verify signature:
   RSA_verify(signing_input, signature, public_key, SHA256)
8. If signature valid:
   - Base64URL-decode payload, parse JSON
   - Validate claims (exp, iss, aud)
   - Extract user info and scopes
```

### Encryption (JWE)

JSON Web Encryption (JWE, RFC 7516) encrypts JWT payload, preventing intermediaries from reading claims. JWE structure (five sections):

```
<header>.<encrypted_key>.<iv>.<ciphertext>.<authentication_tag>
```

**Encryption process:**

```
1. Generate Content Encryption Key (CEK, random symmetric key)
2. Encrypt JWT payload with CEK (AES-GCM)
3. Encrypt CEK with recipient's public key (RSA-OAEP)
4. Construct JWE:
   - header: {"alg":"RSA-OAEP","enc":"A256GCM"}
   - encrypted_key: encrypted CEK
   - iv: initialization vector for AES-GCM
   - ciphertext: encrypted payload
   - authentication_tag: GCM authentication tag
```

**Common encryption algorithms:**

**Key encryption (alg):**

- **RSA-OAEP**: RSA with OAEP padding (asymmetric)
- **RSA-OAEP-256**: OAEP with SHA-256
- **ECDH-ES**: Elliptic Curve Diffie-Hellman Ephemeral Static (key agreement, generates shared secret without encrypting a key)
- **A256KW**: AES-256 Key Wrap (symmetric, requires shared secret)

**Content encryption (enc):**

- **A256GCM**: AES-256 in Galois/Counter Mode (authenticated encryption, most common)
- **A128GCM**, **A192GCM**: AES-128, AES-192 variants
- **A256CBC-HS512**: AES-256 in CBC mode with HMAC-SHA512 authentication (legacy, GCM preferred)

**Decryption process:**

```
1. Parse JWE header, extract alg and enc
2. Base64URL-decode encrypted_key
3. Decrypt CEK using recipient's private key (RSA-OAEP)
4. Base64URL-decode iv, ciphertext, authentication_tag
5. Decrypt payload using CEK and iv (AES-256-GCM)
6. Verify authentication tag (integrity check)
7. Parse decrypted payload (JWT claims)
```

**Nested JWT (signed then encrypted):**

For maximum security, create a signed JWT (JWS), then encrypt it (JWE). This provides both integrity (signature) and confidentiality (encryption).

```
1. Create signed JWT (JWS)
2. Use JWS as payload for JWE
3. Recipient decrypts JWE to get JWS
4. Recipient verifies JWS signature
```

Header for nested JWT:

```json
{
  "alg": "RSA-OAEP",
  "enc": "A256GCM",
  "cty": "JWT"
}
```

`cty` (content type) = "JWT" signals nested JWT.

### Standard Claims

JWT defines standard claims (RFC 7519):

**Registered claims** (reserved names, well-defined semantics):

- `iss` (issuer): Entity that created token (URI)
- `sub` (subject): Principal the token is about (user ID, client ID)
- `aud` (audience): Intended recipient(s) (string or array of strings)
- `exp` (expiration): Unix timestamp, token invalid after this time
- `nbf` (not before): Unix timestamp, token invalid before this time
- `iat` (issued at): Unix timestamp, token creation time
- `jti` (JWT ID): Unique identifier for token (prevents replay)

**Public claims**: Defined in public registries (IANA JWT Claims Registry) or collision-resistant namespaces (URIs). Examples:

- `name`, `given_name`, `family_name` (OIDC UserInfo)
- `email`, `email_verified` (OIDC)
- `roles`, `groups` (authorization)

**Private claims**: Application-specific, agreed between issuer and consumer. Examples:

- `scope`: OAuth2 scopes (space-delimited string)
- `tenant_id`: Multi-tenancy identifier
- `permissions`: Fine-grained permissions array

**Claim validation:**

```
1. Verify `exp`: reject if current_time >= exp
2. Verify `nbf`: reject if current_time < nbf
3. Verify `iss`: reject if not in trusted issuer list
4. Verify `aud`: reject if intended audience not present
5. Verify `jti`: (optional) check if token already used (one-time tokens)
```

### Stateless Sessions with JWT

JWTs enable stateless session management: the token itself contains session state (user ID, roles, expiration), eliminating server-side session storage.

**Traditional session architecture:**

```
Client -> Server (with session cookie)
  -> Server looks up session ID in database/cache
  -> Retrieves session data (user ID, roles, login time)
  -> Processes request
  -> Returns response
```

**Stateless JWT session architecture:**

```
Client -> Server (with JWT in cookie or Authorization header)
  -> Server validates JWT signature
  -> Server extracts claims from JWT payload
  -> Processes request (no database lookup)
  -> Returns response
```

**Advantages:**

- **Horizontal scalability**: No shared session state. Any server can validate token.
- **Lower latency**: No database query for session data.
- **Reduced infrastructure**: No session database (Redis, Memcached).
- **Offline validation**: Resource servers validate tokens without calling authorization server.

**Disadvantages:**

- **Token revocation complexity**: Cannot invalidate token before expiration without server-side tracking (blacklist). Strategies:
  - Short expiration (5-15 minutes) + refresh token flow
  - Revocation list (tracks revoked JTIs, defeats stateless benefit)
  - Event-driven invalidation (push invalidation events to resource servers)
- **Token size**: JWTs are larger than opaque session IDs (400-1500 bytes vs 32 bytes). Cookies may hit size limits (4KB). Use Authorization header to avoid cookie size limits.
- **Sensitive data exposure**: JWT payload is Base64-encoded (not encrypted). Avoid embedding sensitive data unless using JWE.
- **Immutability**: Cannot update claims after issuance. User role changes require token re-issuance.

**OpenAM stateless session implementation:**

OpenAM supports stateless sessions via JWT (`OpenAM/openam-core/src/main/java/org/forgerock/openam/session/stateless/`):

**JwtSessionMapper**: Converts OpenAM session to JWT and vice versa. Maps:

- Session ID -> `jti`
- User ID -> `sub`
- Session creation time -> `iat`
- Session expiration -> `exp`
- Session properties (roles, attributes) -> custom claims

**StatelessJWTCache**: Optional in-memory cache of recent JWT signatures. Speeds up validation by avoiding repeated signature verification. Cache keyed by JWT signature hash; value is validation result (valid/invalid).

**Configuration (admin console)**:

- Enable stateless sessions per realm
- Configure JWT signing key (HS256 shared secret or RS256 key pair)
- Set JWT expiration (typically 5-30 minutes)
- Configure claim mappings (session properties -> JWT claims)

**JWT session creation flow:**

```
1. User authenticates to OpenAM
2. OpenAM creates session (InternalSession object)
3. StatelessSessionActivator converts session to JWT:
   a. Generate JWT claims from session properties
   b. Sign JWT with configured key (RS256)
   c. Store JWT in cookie (or return to client as bearer token)
4. Client includes JWT in subsequent requests
5. OpenAM validates JWT:
   a. Verify signature
   b. Check expiration
   c. Extract claims, reconstruct session context
6. OpenAM processes request with session context
```

**Session blacklisting for stateless JWT:**

To revoke tokens before expiration, OpenAM can maintain a blacklist in CTS:

```
Token type: JWT_BLACKLIST
Key: jti claim
Value: revocation reason
TTL: remaining lifetime of token (exp - now)
```

When validating JWT, OpenAM checks if `jti` is in blacklist. If present, reject token. Blacklist entries auto-expire after token expiration, minimizing storage.

## CTS Tokens: OpenAM's Core Token Service

Core Token Service (CTS) is OpenAM's persistent token storage layer, abstracting token lifecycle management from backend storage. CTS stores OAuth2 tokens, SAML artifacts, session tokens, and other ephemeral data.

### Token Storage Backends

CTS supports pluggable storage backends (`OpenAM/openam-core/src/main/java/org/forgerock/openam/cts/`):

**LDAP (OpenDJ)**: Default backend. Tokens stored as LDAP entries under `ou=tokens,dc=openam,dc=org`. Schema:

```
dn: coreTokenId=<token_id>,ou=tokens,dc=openam,dc=org
objectClass: frCoreToken
coreTokenType: SESSION
coreTokenId: <UUID>
coreTokenUserId: alice
coreTokenExpirationDate: 20250213150000Z
coreTokenString01: <serialized_session_data>
coreTokenString02: <additional_data>
```

LDAP backend provides:

- Multi-master replication (tokens replicate across OpenDJ servers)
- Persistent search (real-time change notifications)
- TTL-based expiration (cleanup daemon removes expired tokens)

**Cassandra**: Distributed, linearly scalable backend (`OpenAM/openam-cassandra/`). Schema:

```
CREATE TABLE tokens (
  token_id text PRIMARY KEY,
  token_type text,
  user_id text,
  expiration timestamp,
  data blob
) WITH default_time_to_live = 3600;
```

Cassandra backend provides:

- Horizontal scalability (add nodes without downtime)
- Eventual consistency (tunable consistency levels)
- Geographic distribution (multi-datacenter replication)
- TTL-based expiration (automatic row deletion)

**Redis** (experimental, via extensions): In-memory cache with persistence. Ultra-fast token lookup (microseconds). Suitable for high-throughput scenarios where token access latency is critical.

**Backend selection considerations:**

| Backend | Read latency | Write latency | Scalability | Replication | Use case |
|---------|--------------|---------------|-------------|-------------|----------|
| OpenDJ | 1-10 ms | 5-20 ms | Vertical | Multi-master | Single datacenter, <100k tokens |
| Cassandra | 1-5 ms | 1-5 ms | Horizontal | Multi-datacenter | Global deployment, millions of tokens |
| Redis | <1 ms | <1 ms | Horizontal | Master-replica | High throughput, <10M tokens |

### CTS Token Types

CTS stores multiple token types:

**SESSION**: OpenAM session tokens (stateful sessions). Contains:

- Session ID
- User ID
- Session properties (authentication level, attributes)
- Creation time, last access time, expiration

**OAUTH2_GRANT_SET**: OAuth2 authorization grant (authorization code, implicit grant state). Short-lived (1-10 minutes).

**OAUTH2_ACCESS_TOKEN**: OAuth2 access token (opaque or JWT). TTL: 1-60 minutes.

**OAUTH2_REFRESH_TOKEN**: OAuth2 refresh token. Long-lived (days to years). Used to obtain new access tokens without re-authentication.

**SAML2_ASSERTION**: SAML assertions for artifact resolution. TTL: 5 minutes.

**SAML2_ARTIFACT**: SAML artifact mapping to assertion. TTL: 5 minutes.

**REST_OAUTH2_SESSION**: OAuth2 session token (authorization server session). Tracks consent, authentication state during OAuth2 flow.

**UMA_RESOURCE_SET**: UMA resource registration. Persistent until resource deleted.

**UMA_PERMISSION_TICKET**: UMA permission ticket. TTL: 5-60 minutes.

**UMA_REQUESTING_PARTY_TOKEN**: UMA RPT (Requesting Party Token). TTL: 5-60 minutes.

**JWT_BLACKLIST**: Revoked JWT identifiers. TTL: remaining lifetime of revoked token.

### Token Lifecycle and Expiry

CTS tokens have lifecycle managed by TTL (Time-To-Live):

**Creation:**

```java
// Create OAuth2 access token
TokenId tokenId = new TokenId(UUID.randomUUID().toString());
Token token = new Token(tokenId, TokenType.OAUTH2_ACCESS_TOKEN);
token.setUserId("alice");
token.setExpiryTimestamp(System.currentTimeMillis() + 3600000); // 1 hour
token.setAttribute("scope", "read write");
token.setBlob(accessTokenBytes);

CTSPersistentStore cts = ...;
cts.create(token);
```

**Retrieval:**

```java
TokenId tokenId = new TokenId(accessTokenString);
Token token = cts.read(tokenId);

if (token == null || token.isExpired()) {
    throw new InvalidTokenException("Token not found or expired");
}

String userId = token.getUserId();
String scope = token.getAttribute("scope");
```

**Deletion (explicit revocation):**

```java
TokenId tokenId = new TokenId(refreshTokenString);
cts.delete(tokenId);
```

**Expiry (automatic cleanup):**

CTS runs background cleanup tasks (query workers) that periodically scan for expired tokens:

```
SELECT coreTokenId FROM frCoreToken
WHERE coreTokenExpirationDate < CURRENT_TIMESTAMP
LIMIT 1000
```

Expired tokens are deleted in batches (default 1000/batch). Cleanup frequency: every 5 minutes (configurable).

**Connection pooling:**

CTS uses async connection pooling (`CTSAsyncConnectionModule`) to handle concurrent token operations:

```
Thread pool:
  Min connections: 10
  Max connections: 100 (configurable)
  Connection timeout: 10 seconds
  Idle timeout: 60 seconds
```

Each CTS operation (create, read, update, delete) acquires a connection from pool, executes LDAP/Cassandra operation, returns connection to pool. Async operations use reactive callbacks (RxJava) to avoid blocking threads.

### Query and Filtering

CTS supports token queries:

**Find tokens by user ID:**

```java
Collection<Token> tokens = cts.query(new TokenFilter()
    .withAttribute("coreTokenUserId", "alice")
    .withType(TokenType.OAUTH2_ACCESS_TOKEN));
```

Mapped to LDAP query:

```
base: ou=tokens,dc=openam,dc=org
scope: subtree
filter: (&(coreTokenType=OAUTH2_ACCESS_TOKEN)(coreTokenUserId=alice))
```

**Find expiring tokens:**

```java
long cutoffTime = System.currentTimeMillis() + 300000; // 5 minutes from now
Collection<Token> tokens = cts.query(new TokenFilter()
    .withExpiryBefore(cutoffTime)
    .withType(TokenType.SESSION));
```

Used for proactive session timeout notifications.

### Current Usage

CTS is central to OpenAM's token management:

- **Session storage**: Stateful sessions (when not using stateless JWT)
- **OAuth2 token storage**: Access, refresh, authorization codes
- **SAML artifacts**: Artifact binding in federation
- **UMA tokens**: Resource sets, permission tickets, RPTs
- **Blacklists**: Revoked tokens, blocked users

For high-scale deployments (millions of tokens, thousands of requests/second), Cassandra backend is recommended. For single-site deployments (tens of thousands of tokens), OpenDJ backend suffices.

## OAuth2 Token Types

OAuth 2.0 defines multiple token types for different stages of the authorization flow. OpenAM implements all standard OAuth2 tokens via `OpenAM/openam-oauth2/`.

### Access Tokens

Access tokens grant access to protected resources. Bearer tokens (RFC 6750) are most common.

**Opaque access tokens**: Random string, no embedded information. Resource server calls introspection endpoint to validate token and retrieve metadata.

Example:

```
Access-Token: 2YotnFZFEjr1zCsicMWpAA
```

Introspection request (RFC 7662):

```
POST /oauth2/introspect HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

token=2YotnFZFEjr1zCsicMWpAA&
token_type_hint=access_token
```

Response:

```json
{
  "active": true,
  "scope": "read write",
  "client_id": "webapp",
  "username": "alice",
  "token_type": "Bearer",
  "exp": 1766419200,
  "iat": 1766415600,
  "sub": "alice",
  "aud": "https://api.example.com"
}
```

**JWT access tokens**: Self-contained, resource server validates signature without introspection call. OpenAM can issue JWT access tokens if configured.

**Access token lifecycle:**

```
1. Client obtains access token via authorization grant
2. Client includes token in API requests: Authorization: Bearer <token>
3. Resource server validates token (introspection or JWT signature)
4. Resource server authorizes request based on scopes
5. Token expires after TTL (typically 1-60 minutes)
6. Client uses refresh token to obtain new access token (if available)
```

### Refresh Tokens

Refresh tokens are long-lived credentials for obtaining new access tokens without user interaction.

**Refresh token flow:**

```
1. Client obtains refresh token during initial authorization (alongside access token)
2. Access token expires
3. Client sends refresh token to token endpoint:
   POST /oauth2/token
   grant_type=refresh_token&
   refresh_token=tGzv3JOkF0XG5Qx2TlKWIA&
   client_id=webapp&
   client_secret=secret123
4. Authorization server validates refresh token:
   - Check token exists in CTS
   - Check not expired
   - Check not revoked
   - Authenticate client
5. Authorization server issues new access token (and optionally new refresh token)
6. Client uses new access token
```

**Refresh token rotation**: Security best practice. Each time a refresh token is used, the authorization server issues a new refresh token and invalidates the old one. Prevents refresh token reuse if stolen.

**Refresh token binding**: Tokens can be bound to client instance (PKCE code_challenge, DPoP proof, mTLS cert). Prevents stolen tokens from being used by attackers.

**Refresh token TTL**: Typically days to months. Shorter lifetimes reduce risk but increase user re-authentication frequency. Balance security vs. user experience.

OpenAM stores refresh tokens in CTS with type `OAUTH2_REFRESH_TOKEN`. Attributes:

- Token ID (random string)
- User ID
- Client ID
- Scope
- Issued at, expiration
- Rotation counter (how many times token has been refreshed)

### Authorization Codes

Authorization codes are short-lived (1-10 minutes), single-use tokens exchanged for access tokens.

**Authorization code flow:**

```
1. Client redirects user to authorization endpoint
2. User authenticates and consents
3. Authorization server issues authorization code
4. Authorization server redirects user back to client with code
5. Client exchanges code for access token:
   POST /oauth2/token
   grant_type=authorization_code&
   code=SplxlOBeZQQYbYS6WxSbIA&
   redirect_uri=https://client.example.com/callback&
   code_verifier=<PKCE_verifier>&
   client_id=webapp&
   client_secret=secret123
6. Authorization server validates code:
   - Check code exists
   - Check not expired
   - Check not already used
   - Verify redirect_uri matches original request
   - Verify PKCE code_verifier (if PKCE used)
   - Authenticate client
7. Authorization server issues access token, marks code as used
8. If code presented again: reject (replay attack detection)
```

**PKCE (Proof Key for Code Exchange, RFC 7636):** Protects authorization code flow from interception attacks. Client generates random `code_verifier`, computes `code_challenge = SHA256(code_verifier)`, includes challenge in authorization request. When exchanging code for token, client provides `code_verifier`. Server verifies `code_challenge == SHA256(code_verifier)`.

OpenAM stores authorization codes in CTS with type `OAUTH2_GRANT_SET`. TTL: 1-10 minutes. Single-use enforced: code marked as used after first exchange attempt.

### Token Introspection (RFC 7662)

Token introspection allows resource servers to query token metadata. Essential for opaque tokens.

**Introspection endpoint:**

```
POST /oauth2/introspect
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

token=<access_token>&
token_type_hint=access_token
```

**Response (active token):**

```json
{
  "active": true,
  "scope": "read write",
  "client_id": "webapp",
  "username": "alice",
  "token_type": "Bearer",
  "exp": 1766419200,
  "iat": 1766415600,
  "nbf": 1766415600,
  "sub": "alice",
  "aud": "https://api.example.com",
  "iss": "https://auth.example.com",
  "jti": "at-12345"
}
```

**Response (inactive token, expired or revoked):**

```json
{
  "active": false
}
```

**Authentication**: Introspection endpoint requires client authentication (HTTP Basic, client credentials, mTLS). Prevents unauthorized token inspection.

**Performance**: Introspection adds latency (network round trip). Mitigation:

- Cache introspection results (short TTL, e.g., 60 seconds)
- Use JWT access tokens with local validation (no introspection needed)
- Use persistent connections (HTTP/2, connection pooling)

OpenAM introspection implementation (`OpenAM/openam-oauth2/src/main/java/org/forgerock/oauth2/core/`):

```java
// IntrospectableToken interface
public interface IntrospectableToken {
    boolean isActive();
    String getTokenType();
    long getExpiryTime();
    String getScope();
    String getClientId();
    String getResourceOwnerId();
    // ... additional metadata
}
```

Introspection handler queries CTS, retrieves token, checks expiration, constructs response.

## Emerging Token Formats

Modern security threats drive evolution toward enhanced token formats with proof-of-possession, sender constraints, and selective disclosure.

### DPoP (Demonstrating Proof-of-Possession)

DPoP (RFC 9449, 2023) binds access tokens to cryptographic keys, preventing token theft and replay attacks. Unlike bearer tokens (anyone possessing token can use it), DPoP tokens require cryptographic proof of key ownership.

**DPoP flow:**

```
1. Client generates ephemeral key pair (RSA or ECDSA)
2. Client creates DPoP proof JWT:
   Header:
     {
       "typ": "dpop+jwt",
       "alg": "ES256",
       "jwk": { <client_public_key> }
     }
   Payload:
     {
       "jti": "<unique_id>",
       "htm": "POST",
       "htu": "https://auth.example.com/oauth2/token",
       "iat": 1766415600
     }
   Signed with client's private key

3. Client sends DPoP proof to token endpoint:
   POST /oauth2/token
   DPoP: <dpop_proof_jwt>
   Authorization: Basic <client_credentials>

   grant_type=authorization_code&
   code=<code>&
   ...

4. Authorization server validates DPoP proof:
   - Verify JWT signature using embedded public key
   - Check htm (HTTP method) matches request
   - Check htu (HTTP URI) matches endpoint
   - Check jti not reused (replay detection)

5. Authorization server issues access token bound to public key:
   {
     "access_token": "<token>",
     "token_type": "DPoP",
     "expires_in": 3600,
     "refresh_token": "<refresh_token>"
   }

6. Client presents DPoP-bound access token to resource server:
   GET /api/data
   Authorization: DPoP <access_token>
   DPoP: <new_dpop_proof_jwt_for_this_request>

   New DPoP proof:
     {
       "jti": "<new_unique_id>",
       "htm": "GET",
       "htu": "https://api.example.com/api/data",
       "iat": 1766415700,
       "ath": "<hash_of_access_token>"
     }

7. Resource server validates:
   - Extract public key from access token (introspection or JWT claim)
   - Verify DPoP proof signature using public key
   - Check htm, htu match current request
   - Check ath (access token hash) matches presented token
   - Check jti not reused
```

**DPoP advantages:**

- **Stolen token useless**: Attacker cannot use token without private key
- **Replay protection**: Each request requires new DPoP proof with unique jti
- **No client-side secrets**: Public key cryptography, no shared secrets
- **TLS agnostic**: Works over TLS or in multi-hop scenarios (API gateway -> backend)

**DPoP challenges:**

- **Complexity**: More complex than bearer tokens, requires key management
- **Compatibility**: Limited support (emerging standard, not universally implemented)
- **Key rotation**: Clients must manage ephemeral keys and rotation

**Adoption status (2025)**: DPoP gaining traction in banking (Open Banking, FAPI), enterprise APIs requiring high assurance. Limited adoption in consumer applications.

### Token Binding

Token binding (RFC 8473, 2018) cryptographically binds tokens to TLS connections, preventing token export attacks. Token can only be used over the TLS connection where it was issued.

**Mechanism:**

```
1. TLS handshake with Token Binding extension
2. TLS connection establishes token binding key (TLS layer)
3. Client obtains access token over this TLS connection
4. Token includes token binding ID (fingerprint of TLS key)
5. Client uses token only over same TLS connection
6. Resource server validates token binding:
   - Extract token binding ID from TLS connection
   - Compare with token binding ID in token
   - Reject if mismatch
```

**Status**: Token binding failed to achieve adoption. Browser support was limited (only Chrome and Edge implemented). TLS resumption and HTTP/2 multiplexing complicated the model. Deprecated by major browsers in 2020. **DPoP supersedes token binding** with simpler, TLS-independent approach.

### Verifiable Credentials (W3C)

Verifiable Credentials (W3C Recommendation, 2024) are cryptographically verifiable digital credentials. Use cases: digital identity, diplomas, licenses, certifications.

**VC structure (simplified):**

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "DriverLicenseCredential"],
  "issuer": "did:example:12345",
  "issuanceDate": "2025-01-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:example:alice",
    "name": "Alice Anderson",
    "licenseNumber": "DL-12345",
    "expirationDate": "2030-01-01"
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2025-01-01T00:00:00Z",
    "verificationMethod": "did:example:12345#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "base64-signature"
  }
}
```

**Key properties:**

- **Issuer**: DID (Decentralized Identifier) of credential issuer
- **Subject**: DID of credential holder
- **Claims**: Credential attributes (name, license number, etc.)
- **Proof**: Digital signature (issuer's signature over credential)

**Selective disclosure (SD-JWT VC):** Holder can reveal only specific claims to verifier without disclosing entire credential. Example: Prove age > 18 without revealing exact birthdate.

**VC relationship to traditional tokens:**

| Dimension | OAuth2/OIDC Tokens | Verifiable Credentials |
|-----------|-------------------|------------------------|
| Format | JWT, opaque | JSON-LD, JWT, SD-JWT |
| Issuer | Centralized IdP | Can be decentralized (DIDs) |
| Verification | Call IdP or verify signature | Verify signature (no IdP call) |
| Revocation | Token expiry, introspection | Revocation lists, status lists |
| Use case | API access, SSO | Identity proofing, attestations |
| Maturity | Mature (20+ years) | Emerging (pilots) |

**Adoption status (2025):** Government-driven (EU Digital Identity Wallet mandated by 2026, US state mobile driver's licenses). Enterprise adoption limited to pilot projects. Expect growth as regulations mandate digital identity credentials.

### Selective Disclosure JWTs (SD-JWT)

SD-JWT (IETF draft, 2024) enables selective disclosure of JWT claims. Holder can reveal subset of claims without exposing all data.

**Mechanism:**

```
1. Issuer creates JWT with claims
2. For each disclosable claim, issuer generates random salt
3. Issuer replaces claim with hash: hash(salt + claim_name + claim_value)
4. Issuer signs JWT with hashed claims
5. Issuer provides disclosures (salt + claim_name + claim_value) separately
6. Holder selects which disclosures to reveal to verifier
7. Holder sends JWT + selected disclosures
8. Verifier:
   - Computes hashes of disclosed claims using provided salts
   - Compares computed hashes with hashes in JWT
   - Verifies JWT signature
```

**Example:**

JWT payload (hashed claims):

```json
{
  "iss": "https://issuer.example.com",
  "sub": "alice",
  "_sd": [
    "hash_of_birthdate",
    "hash_of_ssn",
    "hash_of_address"
  ],
  "_sd_alg": "sha-256"
}
```

Disclosures (separate from JWT):

```
disclosure_birthdate = base64url(salt_1 + "birthdate" + "1985-05-15")
disclosure_ssn = base64url(salt_2 + "ssn" + "123-45-6789")
disclosure_address = base64url(salt_3 + "address" + "123 Main St")
```

Holder reveals only birthdate:

```
JWT: <signed_jwt_with_hashes>
Disclosures: <disclosure_birthdate>
```

Verifier sees:

- Birthdate: 1985-05-15 (verified via hash)
- Other claims: present but not revealed (verifier knows claims exist but not values)

**Use case:** Privacy-preserving identity verification. Example: Age verification without revealing birthdate. KYC (Know Your Customer) without over-sharing personal data.

## Session Management Strategies

Modern IAM systems employ hybrid session strategies balancing stateless scalability with revocation requirements.

### Stateful Sessions (CTS-Based)

Traditional session model: Server stores session state in database (CTS).

**Flow:**

```
1. User authenticates
2. Server creates session, stores in CTS
3. Server issues session cookie (session ID)
4. Client includes cookie in requests
5. Server looks up session ID in CTS
6. Server retrieves session data (user ID, roles)
7. Server processes request
8. Server updates session last access time in CTS
```

**Advantages:**

- **Immediate revocation**: Delete session from CTS, user logged out instantly
- **Small cookies**: Session ID is 32-byte opaque string
- **Mutable state**: Update session properties without re-authentication

**Disadvantages:**

- **Database bottleneck**: Every request queries CTS
- **Horizontal scaling complexity**: Requires session replication or sticky sessions
- **Latency**: Database round trip adds milliseconds

### Stateless Sessions (JWT-Based)

Stateless model: Session state embedded in signed JWT token.

**Flow:**

```
1. User authenticates
2. Server creates JWT with claims (user ID, roles, expiration)
3. Server signs JWT
4. Server returns JWT to client (cookie or Authorization header)
5. Client includes JWT in requests
6. Server validates JWT signature (no database lookup)
7. Server extracts claims from JWT
8. Server processes request
```

**Advantages:**

- **No database**: Eliminates CTS lookup latency and scalability bottleneck
- **Horizontal scaling**: Any server validates token, no shared state
- **Offline validation**: Resource servers validate tokens without calling authorization server

**Disadvantages:**

- **Revocation complexity**: Cannot immediately invalidate token (must wait for expiration or maintain blacklist)
- **Large tokens**: 400-1500 bytes (vs 32 bytes for opaque session ID)
- **Immutable state**: Cannot update claims mid-session

### Hybrid Approach: Short-Lived JWT + Refresh Token

Best-of-both-worlds strategy:

```
1. User authenticates
2. Server issues:
   - Short-lived JWT access token (5-15 minutes)
   - Long-lived refresh token (stored in CTS)
3. Client uses JWT for API requests (stateless, fast)
4. When JWT expires:
   a. Client presents refresh token to token endpoint
   b. Server validates refresh token (CTS lookup)
   c. Server checks if session revoked
   d. Server issues new JWT access token
```

**Benefits:**

- **Fast API requests**: JWT validation, no CTS lookup
- **Revocation support**: Revoke refresh token in CTS, user cannot get new access tokens
- **Balance**: Revocation delay = JWT lifetime (5-15 min), acceptable for most use cases

**OpenAM hybrid session configuration:**

- Stateless JWT access tokens (5-15 min expiration)
- Stateful refresh tokens in CTS (7-30 day expiration)
- Session blacklist in CTS (for emergency revocation)

### Session Blacklisting

Blacklisting enables early token revocation for stateless JWT sessions.

**Mechanism:**

```
1. Admin revokes user session
2. Server adds JWT jti (token ID) to blacklist (CTS)
3. Blacklist entry TTL = remaining JWT lifetime
4. On subsequent request with JWT:
   a. Server validates JWT signature (fast path)
   b. Server checks if jti in blacklist (CTS lookup)
   c. If blacklisted: reject token
   d. If not blacklisted: allow request
```

**Blacklist growth mitigation:**

- Store only revoked tokens (not all tokens)
- TTL auto-expires entries after JWT expiration
- Bloom filter for fast negative lookups (most tokens not blacklisted)

**Trade-off:** Adds CTS lookup for revoked tokens only. Most requests bypass CTS (not in blacklist).

### Distributed Sessions and Replication

Multi-datacenter deployments require session replication:

**LDAP replication (OpenDJ multi-master):**

```
User authenticates in US datacenter
  -> Session stored in US OpenDJ
  -> Change replicated to EU OpenDJ (CSN-based)
  -> User accesses EU datacenter
  -> Session available in EU OpenDJ
  -> Eventual consistency (replication delay: milliseconds to seconds)
```

**Cassandra replication:**

```
User authenticates in US datacenter
  -> Session stored in Cassandra (LOCAL_QUORUM)
  -> Replicated to EU datacenter (async)
  -> User accesses EU datacenter
  -> Session available (tunable consistency)
```

**JWT stateless sessions:**

```
User authenticates in US datacenter
  -> JWT issued, no database storage
  -> User accesses EU datacenter
  -> JWT validated locally, no replication needed
  -> Zero replication latency
```

Stateless JWT sessions are ideal for multi-region deployments with geographically distributed users.

## Summary

Token formats reflect trade-offs between interoperability, security, size, and flexibility. SAML assertions provide XML-based federation with formal trust frameworks, dominant in enterprise B2B. JWT offers compact, self-contained tokens ideal for OAuth2/OIDC and stateless sessions. CTS tokens (OpenAM's opaque format) enable centralized token management with flexible backends (LDAP, Cassandra). OAuth2 access/refresh tokens implement delegation patterns with introspection for validation. Emerging formats (DPoP, SD-JWT, Verifiable Credentials) address modern security requirements: proof-of-possession, selective disclosure, and decentralized trust.

Session management strategies range from stateful (CTS-backed, immediate revocation, database bottleneck) to stateless (JWT, horizontal scalability, revocation complexity). Hybrid approaches (short JWT + refresh token) balance performance and control. Modern best practice: stateless JWT for API performance, refresh tokens for revocation, session blacklisting for emergency scenarios.

References: OpenAM source code at `/Users/kirane/projects/idp/OpenAM/openam-core/src/main/java/org/forgerock/openam/cts/`, `/Users/kirane/projects/idp/OpenAM/openam-oauth2/`, `/Users/kirane/projects/idp/OpenAM/openam-federation/`. SAML 2.0 (OASIS), JWT RFCs (7519, 7515, 7516), OAuth2 RFCs (6749, 6750, 7662), DPoP (RFC 9449), W3C Verifiable Credentials.
