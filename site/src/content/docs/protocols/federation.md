---
title: Federation Protocols
description: "SAML 2.0, WS-Federation, OpenID Connect, and the federation landscape — how cross-domain identity works."
sidebar:
  order: 3
---

# Chapter 3: Federation Protocols

Federation protocols enable cross-domain single sign-on and identity assertion exchange without credential replication. The Open Identity Platform implements three generations of federation standards: SAML (dominant enterprise protocol since 2005), WS-Federation (Microsoft ecosystem), and OpenID Connect (modern cloud-native standard). This chapter examines each protocol's technical architecture, implementation in the OIP codebase, current deployment patterns, and the industry's ongoing SAML-to-OIDC migration trajectory.

![Protocol Evolution Timeline](/idp-research/diagrams/05-protocol-evolution.svg)

## SAML 2.0: The Enterprise Federation Standard

**Problem Solved:** Cross-organizational single sign-on without shared credential databases. User authenticates once at Identity Provider (IdP), accesses multiple Service Providers (SPs) via cryptographically signed assertions. Eliminates password synchronization, reduces password sprawl, centralizes authentication policy enforcement.

![SAML 2.0 SP-Initiated SSO Flow](/idp-research/diagrams/07-saml-sso-flow.svg)

### Protocol Architecture

SAML 2.0 merges SAML 1.1, Liberty Alliance ID-FF 1.2, and Shibboleth contributions into unified federation framework. Published March 2005 by OASIS, remains dominant enterprise federation protocol two decades later.

**Core Specifications:**

- `saml-core-2.0-os` - Assertions and protocol messages
- `saml-bindings-2.0-os` - Transport mechanisms (HTTP-POST, HTTP-Redirect, HTTP-Artifact, SOAP, PAOS)
- `saml-profiles-2.0-os` - Use cases (Web Browser SSO, Single Logout, Enhanced Client/Proxy)
- `saml-metadata-2.0-os` - Configuration exchange format
- `saml-authn-context-2.0-os` - Authentication strength taxonomy

### Assertion Structure

SAML assertions are XML documents containing authentication/authorization/attribute statements. Digitally signed (XML Signature) and optionally encrypted (XML Encryption).

**Three Statement Types:**

1. **AuthnStatement:** Proof of authentication event
   - Subject (NameID identifying user)
   - AuthnContext (authentication method: password, X.509, Kerberos, etc.)
   - AuthnInstant (timestamp)
   - SessionIndex (IdP session identifier)

2. **AttributeStatement:** User attributes
   - Attribute elements with Name and FriendlyName
   - Multi-valued attributes supported
   - Common attributes: email, displayName, eduPersonPrincipalName, organizationName

3. **AuthzDecisionStatement:** Authorization decision (permit/deny)
   - Resource URI
   - Action (read, write, execute)
   - Decision (Permit, Deny, Indeterminate)
   - Rarely used in practice (authorization typically handled at SP)

**Assertion Example (simplified):**

```xml
<saml:Assertion ID="_abc123" IssueInstant="2024-01-15T10:30:00Z" Version="2.0">
  <saml:Issuer>https://idp.example.com/openam</saml:Issuer>
  <ds:Signature>...</ds:Signature>
  <saml:Subject>
    <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">
      ae5f37d9-8c2b-4f1a-9e3d-7b4c1a6f8e2d
    </saml:NameID>
    <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
      <saml:SubjectConfirmationData NotOnOrAfter="2024-01-15T10:35:00Z"
                                     Recipient="https://sp.example.com/acs"/>
    </saml:SubjectConfirmation>
  </saml:Subject>
  <saml:Conditions NotBefore="2024-01-15T10:30:00Z" NotOnOrAfter="2024-01-15T10:35:00Z">
    <saml:AudienceRestriction>
      <saml:Audience>https://sp.example.com</saml:Audience>
    </saml:AudienceRestriction>
  </saml:Conditions>
  <saml:AuthnStatement AuthnInstant="2024-01-15T10:30:00Z" SessionIndex="_session456">
    <saml:AuthnContext>
      <saml:AuthnContextClassRef>
        urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
      </saml:AuthnContextClassRef>
    </saml:AuthnContext>
  </saml:AuthnStatement>
  <saml:AttributeStatement>
    <saml:Attribute Name="mail" FriendlyName="Email">
      <saml:AttributeValue>user@example.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="eduPersonAffiliation">
      <saml:AttributeValue>employee</saml:AttributeValue>
      <saml:AttributeValue>member</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

### Bindings (Transport Mechanisms)

SAML bindings define how protocol messages map to communication protocols.

#### HTTP-POST Binding

**Flow:**

1. IdP generates SAML Response containing assertion
2. Base64-encodes response, embeds in HTML form
3. Returns auto-submitting form to user's browser
4. Browser POSTs form to SP's Assertion Consumer Service (ACS) endpoint
5. SP validates signature, extracts assertion, establishes session

**Advantages:** Supports large assertions (no URL length limits), more secure (data in POST body, not URL).

**Disadvantages:** Requires JavaScript for auto-submit, breaks browser back button.

#### HTTP-Redirect Binding

**Flow:**

1. SP generates SAML AuthnRequest
2. Deflates request (zlib compression), Base64-encodes
3. Constructs redirect URL: `https://idp.example.com/sso?SAMLRequest=<encoded>&SigAlg=<alg>&Signature=<sig>`
4. Browser redirects to IdP
5. IdP validates signature, processes authentication
6. Returns response via HTTP-POST binding (responses too large for URL)

**Advantages:** Simple, no JavaScript required, stateless.

**Disadvantages:** URL length limits (typically 2048 chars), signature parameters visible in URL/logs.

#### HTTP-Artifact Binding

**Flow:**

1. IdP generates assertion, stores server-side
2. Creates artifact (opaque reference, e.g., `AAQAAMh48/1oXIM+sDo7Dh2qMp1HM4IF5DaRNmDj6RdUmllwn9jJHyEgIi8=`)
3. Returns artifact to SP via redirect
4. SP makes back-channel SOAP request to IdP's Artifact Resolution Service with artifact
5. IdP returns assertion via SOAP response
6. SP validates assertion, establishes session

**Advantages:** Assertion never passes through browser (reduced exposure), supports large assertions.

**Disadvantages:** Requires back-channel connectivity (IdP must be reachable from SP), additional round-trip latency.

#### SOAP Binding

**Flow:**

1. Direct SOAP request/response between IdP and SP
2. Used for back-channel operations: Artifact Resolution, Attribute Queries, Single Logout (back-channel variant)

**Advantages:** Synchronous request/response, no browser involvement.

**Disadvantages:** Requires network connectivity between IdP and SP, firewall rules.

#### PAOS Binding (Enhanced Client or Proxy)

**Flow:**

1. Reverse SOAP over HTTP for ECP (Enhanced Client/Proxy) profile
2. Client (typically mobile app or CLI tool) initiates with PAOS header
3. SP responds with SOAP envelope containing AuthnRequest
4. Client extracts request, sends to IdP via SOAP
5. IdP responds with assertion in SOAP envelope
6. Client forwards assertion to SP

**Advantages:** Enables non-browser clients (mobile apps, command-line tools).

**Disadvantages:** Complex implementation, limited adoption.

### NameID Formats

NameID identifies the authenticated subject. Format indicates identifier structure and persistence.

| Format | URN | Semantics | Use Case |
|--------|-----|-----------|----------|
| **Persistent** | `urn:oasis:names:tc:SAML:2.0:nameid-format:persistent` | Opaque pseudonym, stable across sessions | Privacy-preserving identifier, survives account changes |
| **Transient** | `urn:oasis:names:tc:SAML:2.0:nameid-format:transient` | Session-specific, changes each authentication | Maximum privacy, prevents cross-session tracking |
| **Email** | `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress` | Email address | Common for SaaS applications requiring email |
| **X.509 Subject** | `urn:oasis:names:tc:SAML:1.1:nameid-format:X509SubjectName` | Certificate DN | Certificate-based authentication |
| **Windows Domain** | `urn:oasis:names:tc:SAML:1.1:nameid-format:WindowsDomainQualifiedName` | `DOMAIN\username` | Active Directory integration |
| **Kerberos** | `urn:oasis:names:tc:SAML:2.0:nameid-format:kerberos` | `username@REALM` | Kerberos principal |
| **Entity** | `urn:oasis:names:tc:SAML:2.0:nameid-format:entity` | EntityID (for SP identification) | Entity-to-entity federation |
| **Unspecified** | `urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified` | IdP chooses format | Flexible, IdP decides based on policy |

**Name Identifier Management:** SAML supports `ManageNameIDRequest` for updating NameID (e.g., email address change) and `NameIDMappingRequest` for pseudonym resolution (restricted to authorized SPs).

### Metadata

SAML metadata is XML document describing entity configuration: endpoints, certificates, supported bindings, contact information.

**IdP Metadata Example:**

```xml
<EntityDescriptor entityID="https://idp.example.com/openam">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <KeyDescriptor use="signing">
      <ds:KeyInfo>
        <ds:X509Data>
          <ds:X509Certificate>MIIDXTCCAkWgAwIBAgI...</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>
    <SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                         Location="https://idp.example.com/openam/IDPSloRedirect/metaAlias/idp"/>
    <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                         Location="https://idp.example.com/openam/SSORedirect/metaAlias/idp"/>
    <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                         Location="https://idp.example.com/openam/SSOPOST/metaAlias/idp"/>
  </IDPSSODescriptor>
  <Organization>
    <OrganizationName>Example Corp</OrganizationName>
    <OrganizationURL>https://www.example.com</OrganizationURL>
  </Organization>
  <ContactPerson contactType="technical">
    <EmailAddress>saml-admin@example.com</EmailAddress>
  </ContactPerson>
</EntityDescriptor>
```

**Metadata Exchange:** IdP and SP exchange metadata out-of-band (manual upload, HTTP fetch, federation registry). Metadata signed to prevent tampering.

**Metadata Aggregates:** Federation operators (InCommon, eduGAIN) publish signed metadata aggregates containing hundreds of entities. Participants download aggregate, trust entities based on federation operator's signature.

### Single Logout (SLO)

**Problem Solved:** Terminate sessions at all SPs when user logs out at IdP (or vice versa).

**Front-Channel SLO (browser-mediated):**

1. User initiates logout at SP1
2. SP1 sends LogoutRequest to IdP
3. IdP identifies all active sessions (SessionIndex tracking)
4. IdP sends LogoutRequest to each SP (SP2, SP3, ...) via browser redirects
5. Each SP terminates session, responds with LogoutResponse
6. IdP receives all responses, terminates own session
7. IdP responds to SP1 with final LogoutResponse

**Challenges:** Requires all SPs reachable via browser redirects, fragile (if SP2 unavailable, chain breaks), slow (serial redirects).

**Back-Channel SLO (SOAP):**

1. User initiates logout at SP1
2. SP1 sends LogoutRequest to IdP
3. IdP sends LogoutRequest to each SP via SOAP (parallel back-channel requests)
4. Each SP terminates session, responds via SOAP
5. IdP aggregates responses, terminates own session
6. IdP responds to SP1

**Advantages:** Parallel execution, more reliable (failures don't block other SPs), no browser involvement.

**Disadvantages:** Requires network connectivity from IdP to all SPs.

**Hybrid Approach:** Front-channel for some SPs, back-channel for others based on capability.

### OIP Implementation

**Module Path:** `OpenAM/openam-federation/openam-federation-library/` and `OpenAM/openam-federation/OpenFM/`

**Key Classes:**

- `com.sun.identity.saml2.common.SAML2ConfigService` - Configuration management
- `com.sun.identity.saml.servlet.SAMLPOSTProfileServlet` - HTTP-POST binding handler
- `com.sun.identity.saml.servlet.SAMLSOAPReceiver` - SOAP binding handler
- `SAML2AssertionValidator` - Signature/encryption validation, condition checking
- `SAML2Token` - Assertion representation
- `SAML2CTSPersistentStore` - Assertion storage in Core Token Service (CTS)

**Session Replication:** SAML assertions stored in CTS (LDAP or Cassandra backend) for distributed session management. Persistent search mechanism replicates session state across OpenAM cluster nodes.

**Metadata Generation:** OpenAM auto-generates metadata at runtime via endpoint `/metadata` or CLI tool `ssoadm create-metadata-templ`.

**Certificate Management:** Signing/encryption certificates stored in Java KeyStore (JKS). Configurable per entity, per realm. Certificate rollover supported via metadata update.

**Protocol Extensions:**

- **Holder-of-Key (HoK) Profile:** Subject confirmation via TLS client certificate. Binds assertion to specific client, prevents bearer token theft.
- **Delegation Profile:** Assertion chaining for multi-tier delegation (rare in practice).
- **Attribute Query:** Back-channel request for user attributes post-authentication. Enables just-in-time attribute retrieval.

### Current Relevance

SAML 2.0 remains dominant enterprise federation protocol. Estimated adoption:

- **Enterprise B2B:** 80%+ of enterprise SaaS providers support SAML (Salesforce, Workday, ServiceNow, Box, Zoom)
- **Education:** InCommon Federation (US higher education) has 1,000+ member institutions, exclusively SAML
- **Government:** FedRAMP, FICAM, eIDAS (Europe) mandate SAML support
- **Healthcare:** HIPAA-regulated systems predominantly use SAML for provider federation

**Why SAML Persists:**

1. **Entrenched Infrastructure:** Enterprises invested heavily in SAML deployments (2005-2015)
2. **Compliance Requirements:** Regulations specify SAML explicitly
3. **Attribute Richness:** SAML AttributeStatements support complex attribute structures (multi-valued, namespaced)
4. **Metadata Federations:** Established trust frameworks (InCommon, eduGAIN) built on SAML metadata
5. **Vendor Support:** All major IdPs (Okta, Ping, Microsoft ADFS, Shibboleth) support SAML

**SAML Weaknesses:**

1. **XML Complexity:** Verbose payloads, complex signature validation, XXE/XML entity expansion vulnerabilities
2. **Poor Mobile/Native App Support:** Designed for browser flows; PAOS binding rarely implemented
3. **No Token Refresh:** Assertions expire; no refresh token equivalent (requires re-authentication)
4. **Limited API Integration:** REST APIs prefer OAuth2 bearer tokens over SAML assertions

### OIDC Migration Trajectory

Industry trend: OIDC for new integrations, SAML for legacy compatibility.

**Migration Drivers:**

- **Cloud-Native:** OIDC designed for API access, microservices, mobile apps
- **Developer Experience:** JSON vs. XML, simple JWT validation vs. XML Signature
- **Modern Protocols:** OIDC integrates with OAuth2 ecosystem (token exchange, DPoP, PKCE)

**Migration Timeline:**

- **Consumer SaaS (B2C):** 70%+ migrated to OIDC
- **Enterprise SaaS (B2B):** 40% OIDC, 60% SAML (estimate, accelerating)
- **Education/Government:** 90%+ still SAML (slow migration due to metadata federations)
- **Projection:** SAML dominant for enterprise through 2030, gradual decline thereafter

**Dual-Protocol Strategy:** Most IdPs support both SAML and OIDC. New SPs implement OIDC; legacy SPs retain SAML. Metadata conversion tools (SAML metadata to OIDC Discovery JSON) emerging.

## SAML 1.1 (Legacy)

**Problem Solved:** First-generation cross-domain SSO (2003). Web Browser SSO Profile and Artifact/POST bindings.

**Why Still Present:** Backward compatibility for ancient enterprise applications deployed 2003-2005. SAML 1.1 assertions structurally incompatible with SAML 2.0 (different XML schema).

**OIP Implementation:**

- **Module Path:** `OpenAM/openam-federation/openam-federation-library/`
- **Key Classes:**
  - `com.sun.identity.saml.SAMLClient`
  - `SAML11AssertionValidator`
  - `com.sun.identity.federation.message.FSSAMLRequest`
- **Hot Deployment:** SAML 1.1 support disabled by default; enabled via configuration flag

**Current Relevance:** Deprecated. Estimated <1% usage. Only organizations with 20+ year-old SPs.

**What Replaces It:** SAML 2.0 or OIDC.

**Migration Considerations:** Upgrade legacy applications to SAML 2.0 or implement OIDC integration. Sunset SAML 1.1 support to reduce attack surface (older XML parsing libraries, fewer security updates).

## WS-Federation (Microsoft Ecosystem)

**Problem Solved:** Federation for Microsoft-centric enterprises. Active Directory Federation Services (ADFS) implements WS-Federation for SSO to SharePoint, Office 365, Dynamics, third-party SaaS.

### Protocol Architecture

WS-Federation defines passive (browser-based) and active (SOAP-based) federation. Built on WS-Trust security token model.

**Passive Requestor Profile (Browser SSO):**

1. User accesses resource at Relying Party (RP, equivalent to SP)
2. RP redirects to IP/STS (Identity Provider / Security Token Service) with `wa=wsignin1.0`, `wtrealm=<RP-ID>`, `wctx=<context>`
3. User authenticates at IP/STS (typically ADFS with Windows Integrated Authentication)
4. IP/STS issues RequestSecurityTokenResponse (RSTR) containing signed security token (SAML 1.1 or SAML 2.0 assertion)
5. IP/STS returns HTML form auto-posting RSTR to RP
6. RP validates token, establishes session

**Request Parameters:**

- `wa` - Action (wsignin1.0, wsignout1.0, wsignoutcleanup1.0)
- `wtrealm` - RP identifier (URI)
- `wctx` - Opaque context (RP uses for state tracking)
- `wresult` - Response token (in POST body)

**Active Requestor Profile (SOAP):**

Used for non-browser scenarios (desktop apps, services). Client makes SOAP request to STS with RequestSecurityToken (RST), receives RSTR with token.

### Token Types

WS-Federation supports multiple token formats:

- **SAML 1.1 Assertion** (most common with ADFS)
- **SAML 2.0 Assertion**
- **JWT** (modern ADFS versions)
- **Custom tokens** (via WS-Trust extensibility)

### Metadata

WS-Federation metadata describes IP/STS and RP configuration: endpoints, supported token types, certificates.

**FederationMetadata.xml Example:**

```xml
<EntityDescriptor entityID="http://adfs.example.com/adfs/services/trust">
  <RoleDescriptor xsi:type="fed:SecurityTokenServiceType"
                  protocolSupportEnumeration="http://docs.oasis-open.org/wsfed/federation/200706">
    <KeyDescriptor use="signing">
      <KeyInfo>
        <X509Data>
          <X509Certificate>MIIDXTCCAkWgAwIB...</X509Certificate>
        </X509Data>
      </KeyInfo>
    </KeyDescriptor>
    <fed:PassiveRequestorEndpoint>
      <EndpointReference>
        <Address>https://adfs.example.com/adfs/ls/</Address>
      </EndpointReference>
    </fed:PassiveRequestorEndpoint>
  </RoleDescriptor>
</EntityDescriptor>
```

### Home Realm Discovery

**Problem:** User's browser reaches RP; RP must determine which IP/STS to redirect to.

**Solutions:**

1. **Email Domain Mapping:** User enters email; RP extracts domain, looks up associated IP/STS
2. **WS-Federation Home Realm Discovery Service:** Dedicated endpoint returns IP/STS URL for given user identifier
3. **Client-Side Selection:** User chooses organization from dropdown

**ADFS Implementation:** ADFS provides Home Realm Discovery page where user selects organization or enters email address.

### Single Logout

**WS-Federation Logout:**

1. User initiates logout at RP
2. RP redirects to IP/STS with `wa=wsignout1.0`, `wreply=<RP-logout-URL>`
3. IP/STS terminates session
4. Optional: IP/STS redirects to other RPs for logout (similar to SAML front-channel SLO)
5. IP/STS redirects back to RP logout URL

**Cleanup:** `wa=wsignoutcleanup1.0` embeds cleanup request in 1x1 pixel iframe, enabling silent logout notification to other RPs.

### OIP Implementation

**Module Path:** `OpenAM/openam-federation/openam-federation-library/` and `OpenAM/openam-federation/OpenFM/`

**Key Classes:**

- `com.sun.identity.wsfederation.servlet.WSFederationService` - Protocol handler
- `WSFederationClient` - RP-side client
- `WSFederationConstants` - Protocol constants (wa parameters, namespaces)
- `WSFederationMetaManager` - Metadata management
- `WSFederationMetaSecurityUtils` - Signature/encryption
- `CreateWSFedMetaDataTemplate` - Metadata generation
- `WSFederationSingleLogoutHandler` - SLO coordination

**ADFS Interoperability:** OpenAM WS-Federation module tested against Microsoft ADFS 2.0, 3.0, 4.0. Supports SAML 1.1 and SAML 2.0 token formats.

### Current Relevance

**Active but Declining:** WS-Federation usage tied to Microsoft ADFS deployments. Estimated adoption:

- **On-Premises Microsoft Shops:** 60% still use ADFS + WS-Federation
- **Hybrid Cloud (Azure AD):** 40% retain ADFS for on-premises apps, federate to Azure AD
- **Greenfield:** <5% (new deployments use OIDC)

**Microsoft's Direction:** Azure AD (now Entra ID) supports WS-Federation for backward compatibility but recommends OIDC/SAML 2.0 for new integrations. ADFS development effectively frozen; feature parity with Azure AD prioritized.

**What Replaces It:** OpenID Connect. Azure AD offers OIDC endpoints; modern Microsoft apps (Teams, Office 365) use OIDC internally.

**Migration Considerations:**

- Migrate ADFS-reliant applications to Azure AD with OIDC
- Use ADFS as interim gateway: WS-Federation from legacy apps to ADFS, OIDC from ADFS to Azure AD
- Plan ADFS decommissioning within 5 years (Microsoft signals via lack of ADFS feature updates)
- OpenAM WS-Federation support enables non-Microsoft IdPs to service Microsoft ecosystems

## Liberty Alliance / ID-FF (Historical)

**Problem Solved:** Pre-SAML 2.0 federation standard (2003-2005). Contributed circle-of-trust model, single logout, and name identifier management to SAML 2.0.

**Architecture:**

- **Circle of Trust:** Established trust relationships between IdP and SPs via metadata exchange. Pre-configured trust eliminates per-SP runtime negotiation.
- **Liberty ID-FF Profiles:** Authentication, Single Logout, Federation Termination, Name Registration

**OIP Implementation:**

**Module Path:** `OpenAM/openam-federation/openam-federation-library/`

**Key Classes:**

- `com.sun.liberty.jaxrpc.*` - JAX-RPC SOAP bindings
- `com.sun.identity.liberty.ws.common.wsse.*` - WS-Security header processing
- `WSX509KeyManager` - X.509 key management for SOAP message signing

**Current Relevance:** Deprecated. Liberty Alliance dissolved into Kantara Initiative (2009). ID-FF contributions absorbed into SAML 2.0. No new deployments.

**What Replaces It:** SAML 2.0 (direct successor).

**Migration Considerations:** Migrate any lingering Liberty ID-FF deployments to SAML 2.0. OpenAM retains Liberty support for backward compatibility only.

## Web Services Security (WS-Security, WS-Trust)

**Problem Solved:** SOAP message-level security. SAML/WS-Federation operate at HTTP transport layer; WS-Security secures SOAP message content via XML Signature and XML Encryption.

### WS-Security (Message Protection)

**Capabilities:**

- **XML Signature:** Sign SOAP header, body, or specific elements. Ensures integrity and non-repudiation.
- **XML Encryption:** Encrypt message content. Protects confidentiality beyond TLS (survives intermediaries).
- **Security Tokens:** Embed SAML assertions, X.509 certificates, username tokens, Kerberos tickets in SOAP header.
- **Timestamp:** Prevents replay attacks (message valid within time window).

**SOAP Header Example:**

```xml
<soap:Envelope>
  <soap:Header>
    <wsse:Security>
      <wsu:Timestamp>
        <wsu:Created>2024-01-15T10:30:00Z</wsu:Created>
        <wsu:Expires>2024-01-15T10:35:00Z</wsu:Expires>
      </wsu:Timestamp>
      <wsse:BinarySecurityToken ValueType="...#X509v3">
        MIIDXTCCAkWgAwIBAgI...
      </wsse:BinarySecurityToken>
      <ds:Signature>
        <ds:SignedInfo>
          <ds:Reference URI="#body">...</ds:Reference>
        </ds:SignedInfo>
        <ds:SignatureValue>...</ds:SignatureValue>
      </ds:Signature>
    </wsse:Security>
  </soap:Header>
  <soap:Body wsu:Id="body">
    <RequestSecurityToken>...</RequestSecurityToken>
  </soap:Body>
</soap:Envelope>
```

### WS-Trust (Security Token Service)

**Problem Solved:** Token transformation and brokering. Security Token Service (STS) issues, renews, validates, and exchanges security tokens.

**Operations:**

- **Issue:** Client requests token (SAML, JWT, custom). STS authenticates client, issues token.
- **Renew:** Extend token validity without re-authentication.
- **Validate:** Verify token authenticity and validity.
- **Cancel:** Revoke token before expiration.
- **Exchange:** Transform token type (e.g., X.509 certificate → SAML assertion, SAML → OAuth2 access token).

**RequestSecurityToken (RST):**

Client sends RST to STS specifying:

- `TokenType` - Desired token type (SAML 1.1, SAML 2.0, JWT)
- `RequestType` - Issue, Renew, Validate, Cancel
- `AppliesTo` - Target service (RP/SP)
- `Claims` - Requested attributes
- `OnBehalfOf` - Delegation scenario (act-as vs. on-behalf-of)

**RequestSecurityTokenResponse (RSTR):**

STS responds with issued token, lifetime, proof-of-possession key (optional).

### OIP Implementation

**Module Path:** `OpenAM/openam-federation/OpenFM/`

**Key Classes:**

- `com.sun.identity.wss.security.ConfiguredWSCSecurityMech` - WS-Security client config
- `ConfiguredWSPSecurityMech` - WS-Security provider config
- `WSSAuthModule` - JAAS auth module for WS-Security
- `WSSPolicyManager` - Policy-based message protection
- `SAML2AssertionValidator` - Validates SAML tokens in SOAP messages
- `SAML2Token`, `SAML2TokenUtils` - Token handling
- `com.sun.identity.wss.trust.WSTrustFactory` - STS client factory

**Token Transformation:** OpenAM STS supports SAML→OAuth2, X.509→SAML transformations. Configured via policy definitions.

### Current Relevance

**Deprecated for New Projects:** WS-* stack (WS-Security, WS-Trust, WS-Policy, WS-SecureConversation) declined with SOAP's fall from dominance. REST/JSON replaced SOAP for most web services (2010-2015).

**Where It Persists:**

- **Legacy Enterprise SOA:** Banking, insurance, healthcare with 10-20 year-old SOAP services
- **Government Systems:** Compliance requirements specify WS-Security
- **B2B Integration:** EDI/XML message exchange (shrinking footprint)

**What Replaces It:**

- **API Security:** OAuth 2.0 + JWT for REST APIs
- **Message-Level Security:** JWT/JWS/JWE for JSON payloads
- **Token Exchange:** OAuth 2.0 Token Exchange (RFC 8693) replaces WS-Trust

**Migration Considerations:**

- Migrate SOAP services to REST/JSON with OAuth2 authorization
- Retain WS-Security only for legacy system integration
- Use API gateways (OpenIG) to translate WS-Security→OAuth2 at boundary
- Sunset WS-* services within 5-10 years

![OAuth2/OIDC Authorization Code + PKCE Flow](/idp-research/diagrams/08-oauth2-oidc-flow.svg)

## OpenID Connect as Federation Protocol

**Problem Solved:** Modern alternative to SAML for cross-domain SSO. Built on OAuth2, designed for web/mobile/API-centric architectures. Simpler than SAML (JSON vs. XML), native mobile support, token refresh built-in.

### OIDC vs. SAML Comparison

| Aspect | SAML 2.0 | OpenID Connect |
|--------|----------|----------------|
| **Format** | XML | JSON |
| **Transport** | HTTP-POST, HTTP-Redirect, SOAP | OAuth2 redirect, token endpoint |
| **Tokens** | SAML Assertion (XML) | ID Token (JWT) + Access Token |
| **Signature** | XML Signature (RSA-SHA256) | JWS (RS256, ES256) |
| **Metadata** | XML (SAML metadata schema) | JSON (OIDC Discovery) |
| **Mobile Support** | Poor (PAOS rarely implemented) | Native (Authorization Code + PKCE) |
| **API Access** | Not designed for APIs | OAuth2 access tokens for APIs |
| **Token Refresh** | No (re-authenticate) | Yes (refresh tokens) |
| **Adoption Curve** | Mature (peaked ~2015) | Growing (majority of new integrations) |

### Core Protocol Flow (Authorization Code)

1. **Discovery:** Client fetches OIDC configuration from `https://idp.example.com/.well-known/openid-configuration`
2. **Authorization Request:** Redirect to `/authorize?response_type=code&client_id=...&scope=openid email profile&redirect_uri=...&state=...&nonce=...`
3. **Authentication:** User authenticates at IdP (if not already authenticated)
4. **Consent:** User approves requested scopes
5. **Authorization Code:** IdP redirects to `redirect_uri?code=...&state=...`
6. **Token Request:** Client POSTs to `/token` with code, client_id, client_secret (or client assertion)
7. **Token Response:** IdP returns `{ "id_token": "<JWT>", "access_token": "<opaque>", "refresh_token": "<opaque>", "expires_in": 3600 }`
8. **ID Token Validation:** Client validates JWT signature, issuer, audience, expiration, nonce
9. **UserInfo Request (optional):** Call `/userinfo` with access token for additional claims
10. **Session Establishment:** Client establishes session based on ID token claims

### ID Token Structure

ID token is signed JWT (JWS) containing claims about authenticated user.

**Example (decoded):**

```json
{
  "iss": "https://idp.example.com",
  "sub": "ae5f37d9-8c2b-4f1a-9e3d-7b4c1a6f8e2d",
  "aud": "client_abc123",
  "exp": 1705319700,
  "iat": 1705316100,
  "nonce": "n-0S6_WzA2Mj",
  "auth_time": 1705316095,
  "acr": "urn:mace:incommon:iap:silver",
  "amr": ["pwd", "mfa"],
  "email": "user@example.com",
  "email_verified": true,
  "name": "Jane Doe",
  "picture": "https://cdn.example.com/avatars/jane.jpg"
}
```

**Standard Claims:**

- `iss` - Issuer (IdP URL)
- `sub` - Subject (unique user identifier, equivalent to SAML NameID)
- `aud` - Audience (client_id)
- `exp` - Expiration timestamp
- `iat` - Issued-at timestamp
- `nonce` - Replay prevention (client-provided random value)
- `auth_time` - Authentication timestamp
- `acr` - Authentication Context Class Reference (authentication strength)
- `amr` - Authentication Methods References (password, MFA, biometric)

**Profile Claims:** `name`, `given_name`, `family_name`, `middle_name`, `nickname`, `preferred_username`, `profile`, `picture`, `website`, `email`, `email_verified`, `gender`, `birthdate`, `zoneinfo`, `locale`, `phone_number`, `phone_number_verified`, `address`, `updated_at`

### OIDC Discovery

**Well-Known Configuration Endpoint:** `https://idp.example.com/.well-known/openid-configuration`

**Response Example:**

```json
{
  "issuer": "https://idp.example.com",
  "authorization_endpoint": "https://idp.example.com/oauth2/authorize",
  "token_endpoint": "https://idp.example.com/oauth2/token",
  "userinfo_endpoint": "https://idp.example.com/oauth2/userinfo",
  "jwks_uri": "https://idp.example.com/oauth2/jwks",
  "registration_endpoint": "https://idp.example.com/oauth2/register",
  "scopes_supported": ["openid", "profile", "email", "address", "phone"],
  "response_types_supported": ["code", "id_token", "token id_token"],
  "grant_types_supported": ["authorization_code", "refresh_token", "client_credentials"],
  "subject_types_supported": ["public", "pairwise"],
  "id_token_signing_alg_values_supported": ["RS256", "ES256"],
  "claims_supported": ["sub", "iss", "auth_time", "acr", "name", "email"],
  "code_challenge_methods_supported": ["S256"]
}
```

**Benefits:** Eliminates manual endpoint configuration. Clients auto-configure by fetching discovery document.

### Dynamic Registration

**Client Registration Endpoint:** `POST https://idp.example.com/oauth2/register`

**Request:**

```json
{
  "redirect_uris": ["https://client.example.com/callback"],
  "client_name": "Example Application",
  "logo_uri": "https://client.example.com/logo.png",
  "contacts": ["admin@client.example.com"],
  "scope": "openid profile email"
}
```

**Response:**

```json
{
  "client_id": "abc123",
  "client_secret": "secret_xyz789",
  "client_id_issued_at": 1705316100,
  "client_secret_expires_at": 1736852100,
  "redirect_uris": ["https://client.example.com/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "client_secret_basic"
}
```

**Benefits:** Eliminates manual client onboarding. Applications self-register, receive credentials programmatically.

**Security Consideration:** Dynamic registration often disabled in production (abuse risk). Used in development/testing or with client attestation.

### Logout

**RP-Initiated Logout:**

1. Client redirects to IdP's `end_session_endpoint`: `https://idp.example.com/logout?id_token_hint=<JWT>&post_logout_redirect_uri=https://client.example.com/goodbye`
2. IdP terminates session
3. IdP redirects to `post_logout_redirect_uri`

**Back-Channel Logout:**

1. IdP sends logout token (JWT) to client's registered `backchannel_logout_uri` via HTTP POST
2. Logout token contains `sid` (session ID) or `sub` (subject)
3. Client terminates sessions matching logout token
4. Client responds with HTTP 200

**Front-Channel Logout:**

1. IdP embeds logout request in hidden iframes on IdP logout page
2. Each iframe points to client's `frontchannel_logout_uri`
3. Clients clear cookies, terminate sessions
4. User sees IdP logout confirmation page

### OIP Implementation

**Module Paths:**

- **OIDC Provider:** `OpenAM/openam-oauth2/` (OAuth2 server with OIDC extensions)
- **OIDC Authentication Module:** `OpenAM/openam-authentication/openam-auth-oidc/` (OIDC RP functionality)

**Key OIDC Provider Classes:**

- `org.forgerock.oauth2.core.OAuth2Request` - Request abstraction
- `org.forgerock.openam.oauth2.OAuth2Utils` - Utility functions
- `OAuth2ProviderSettings` - Configuration
- `OAuth2Jwt` - JWT handling

**OIDC Authentication Module Classes:**

- `org.forgerock.openam.authentication.modules.oidc.OpenIdConnectConfig` - RP configuration
- `JwtHandlerConfig` - JWT validation
- `JwtAttributeMapper` - Claim mapping
- `OpenIdConnectToken` - ID token representation

**Discovery Endpoint:** `https://openam.example.com/oauth2/.well-known/openid-configuration`

**ID Token Signing:** RS256 (RSA SHA-256), ES256 (ECDSA SHA-256). Keys published at JWKS endpoint: `https://openam.example.com/oauth2/jwks`

### OIDC Federation (Draft Specification)

**Problem Solved:** Automatic trust establishment. Traditional OIDC requires manual client registration and IdP configuration. OIDC Federation enables automatic metadata discovery and trust chain validation.

**Architecture:**

1. **Trust Anchors:** Root entities publish trusted intermediates
2. **Trust Chains:** Each entity publishes signed statements from parent entity
3. **Metadata Resolution:** Client fetches entity metadata, validates trust chain to anchor
4. **Dynamic Trust:** No pre-configured metadata; trust established at runtime

**Example Use Case:** EU Digital Identity Wallet (eIDAS 2.0). National identity providers establish trust via OIDC Federation, eliminating manual bilateral metadata exchange.

**Status:** Draft specification (2024). Limited production deployment. EU eIDAS 2.0 pilot projects testing OIDC Federation.

**Current Relevance:** Emerging. Solves metadata management scalability problem (federation with thousands of entities). Watch for adoption in government/education federations.

## Protocol Evolution and Migration Paths

### SAML → OIDC Migration

**Why Migrate:**

1. **Developer Experience:** JSON simpler than XML; JWT libraries ubiquitous
2. **Mobile/Native Apps:** OIDC designed for Authorization Code + PKCE; SAML PAOS rarely implemented
3. **API Integration:** Access tokens native to OIDC; SAML assertions awkward for REST APIs
4. **Token Refresh:** Refresh tokens eliminate re-authentication; SAML requires new assertion
5. **Modern Standards:** OIDC integrates with OAuth2 ecosystem (DPoP, RAR, PAR)

**Migration Strategies:**

**1. Dual-Protocol IdP:**

- Configure OpenAM as both SAML IdP and OIDC Provider
- Legacy SPs continue using SAML
- New applications integrate via OIDC
- Gradual SP migration over 3-5 years

**2. Protocol Translation Gateway:**

- OpenIG intercepts SAML requests
- Translates to OIDC for backend IdP
- Converts OIDC ID token to SAML assertion for SP
- Enables OIDC-only IdP to service SAML SPs

**3. Metadata Conversion:**

- Convert SAML metadata to OIDC Discovery JSON
- Map SAML entityID → OIDC issuer
- Map ACS endpoint → redirect_uri
- Automated tools: `saml-to-oidc-metadata-converter`

**4. Claim Mapping:**

- SAML AttributeStatement → OIDC ID token claims
- Common mappings:
  - `urn:oid:0.9.2342.19200300.100.1.3` (mail) → `email`
  - `urn:oid:2.5.4.42` (givenName) → `given_name`
  - `urn:oid:2.5.4.4` (sn) → `family_name`
  - `eduPersonPrincipalName` → `sub` or custom claim

**Migration Timeline:**

- **Year 1:** Dual-protocol IdP deployment, pilot OIDC integration with 2-3 applications
- **Year 2-3:** Migrate 50% of SPs to OIDC, document patterns, train developers
- **Year 4-5:** Migrate remaining SPs, decommission SAML IdP functionality
- **Year 6+:** OIDC-only operations

**Challenges:**

- **Attribute Richness:** SAML AttributeStatement more flexible than OIDC claims (nested structures, namespaced attributes)
- **Metadata Federations:** InCommon, eduGAIN built on SAML metadata aggregates; OIDC equivalents immature
- **Legacy SP Lock-In:** Vendors slow to update SAML-only SPs (SharePoint, older SaaS)

### Enterprise Adoption Curves

**SAML 2.0:**

- 2005: Specification published
- 2006-2010: Early adopters (universities, large enterprises)
- 2011-2015: Peak adoption (InCommon grows to 1,000+ members, SaaS explosion)
- 2016-2020: Mature deployment (90%+ Fortune 500 use SAML)
- 2021-present: Plateau (new integrations prefer OIDC, existing SAML stable)

**OpenID Connect:**

- 2014: Specification published
- 2015-2017: Early adopters (Google, Microsoft migrate from OpenID 2.0)
- 2018-2020: Rapid growth (Auth0, Okta default to OIDC, developer preference shifts)
- 2021-2023: Enterprise acceleration (50%+ new SaaS integrations use OIDC)
- 2024-present: Dominant for new projects (SAML for legacy only)

**Projection:**

- 2025: 60% OIDC / 40% SAML for new integrations
- 2030: 80% OIDC / 20% SAML
- 2035: 95% OIDC / 5% SAML (legacy hold-outs)

### Federation Metadata Management

**SAML Metadata Federations:**

- **InCommon (US Education):** 1,000+ IdPs/SPs, central metadata aggregate, annual membership
- **eduGAIN (Global Education):** 70+ national federations, 8,000+ entities, interfederation metadata exchange
- **FedRAMP (US Government):** SAML required for cloud service authorization
- **FICAM (US Federal ICAM):** SAML for federal employee access to partner systems

**OIDC Federation (Emerging):**

- **EU eIDAS 2.0:** OIDC Federation for digital identity wallets (27 EU member states)
- **OpenID Connect Federation 1.0 (draft):** Automatic trust chain validation, eliminates manual metadata exchange
- **Challenge:** Replacing established SAML metadata federations requires critical mass migration

## Cross-References

- **Authentication Protocols:** See Chapter 2 for SAML/OIDC as authentication modules (consuming federation assertions)
- **Token Formats:** See Chapter 6 for SAML assertion XML schema, JWT structure, signature algorithms
- **Authorization:** See Chapter 4 for OAuth2 authorization flows, scope-based access control
- **API Gateways:** See Chapter 10 for OpenIG protocol translation (SAML→OIDC, WS-Security→OAuth2)
- **Modern Architecture:** See Chapter 12 for federation's role in continuous verification, CAEP session revocation
