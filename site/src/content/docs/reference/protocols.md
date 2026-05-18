---
title: Protocol Inventory (40+ Protocols)
description: "Complete inventory of all protocols implemented across the 7 OpenAM-lineage repositories — authentication modules, federation protocols, authorization frameworks, and connectors."
sidebar:
  order: 1
---

# Protocol & Standards Inventory

## Executive Summary

The Open Identity Platform suite (OpenAM 16.0.5, OpenDJ 5.0.3, OpenIDM 7.0.2, OpenIG 6.0.2, OpenICF 2.0.2) plus legacy forks (ForgeRock CE 11.0.3, WrenAM 16.0.0-M1) implements 40+ authentication protocols, 3 major federation standards, OAuth2/OIDC authorization, XACML 3.0 policy enforcement, LDAPv3 directory services with REST gateway, and identity sync/provisioning via OpenICF connectors. Core patterns: stateless JWT sessions (OpenAM), reactive LDAPv3 via RxJava (OpenDJ), OSGi provisioning engine (OpenIDM), filter/handler pipeline (OpenIG), and SPI-based connector framework (OpenICF).

## Detailed Findings

### Authentication Protocols (31 modules in OpenAM)

#### LDAP Bind
- **Module Path**: `OpenAM/openam-authentication/openam-auth-ldap/`
- **Key Classes**: `com.sun.identity.authentication.modules.ldap.LDAP`, `LDAPAuthUtils`, `LDAPCallbacks`
- **Implementation**: Direct LDAPv3 bind with optional StartTLS; DN templates; password policies; SSL/TLS configuration; Active Directory-compatible auth. Supports LDAP_RESULT codes, SearchScope operations.
- **Repos**: OpenAM, WrenAM

#### RADIUS
- **Module Path**: `OpenAM/openam-authentication/openam-auth-radius/`
- **Key Classes**: `com.sun.identity.authentication.modules.radius.RADIUS`, `RADIUSServer`, `RadiusConn`, `ChallengeException`, `RejectException`
- **Implementation**: RADIUS protocol with challenge/response; challenge IDs for multi-round auth; Access-Accept/Access-Reject response handling; configurable timeouts (default 5s); primary/secondary server failover.
- **Repos**: OpenAM, WrenAM

#### Active Directory (AD)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-ad/`
- **Key Classes**: `com.sun.identity.authentication.modules.ad.AD`, `ADPrincipal`
- **Implementation**: Windows LDAP variant; integrates with LDAPAuthUtils; NTLM password encoding; AD-specific attributes.
- **Repos**: OpenAM, WrenAM

#### X.509 Certificates
- **Module Path**: `OpenAM/openam-authentication/openam-auth-cert/`
- **Key Classes**: `com.sun.identity.authentication.modules.cert.Cert`, `CertAuthPrincipal`
- **Implementation**: Client certificate extraction from TLS handshake; DN matching; certificate chain validation; CRL/OCSP support (framework-ready).
- **Repos**: OpenAM, WrenAM

#### SAML 2.0 (as Authentication)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-saml2/`
- **Key Classes**: `org.forgerock.openam.authentication.modules.saml2.SAML2`, `SAML2PostAuthenticationPlugin`, `SAML2Proxy`, `SAML2ResponseData`
- **Implementation**: SAML assertion consumption; XML signature validation; metadata parsing; POST/Artifact bindings support.
- **Repos**: OpenAM, WrenAM

#### OAuth 2.0 (as Authentication)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-oauth2/`
- **Key Classes**: `OAuthProxy`, `ProfileProvider`, `EmailGateway`
- **Implementation**: Social login via OAuth2; provider agnostic (Facebook, Google, GitHub via configurable endpoints); user profile attribute mapping; email verification; ESRA/ESIA support.
- **Repos**: OpenAM, WrenAM

#### OpenID Connect (OIDC)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-oidc/`
- **Key Classes**: `org.forgerock.openam.authentication.modules.oidc.OpenIdConnectConfig`, `JwtHandlerConfig`, `JwtAttributeMapper`, `OpenIdConnectToken`
- **Implementation**: JWT token validation; claim extraction (sub, email, name); issuer verification; key resolution caching.
- **Repos**: OpenAM, WrenAM

#### WebAuthn / FIDO2
- **Module Path**: `OpenAM/openam-authentication/openam-auth-webauthn/`
- **Key Classes**: `org.openidentityplatform.openam.authentication.modules.webauthn.WebAuthnAuthentication`, `WebAuthnRegistration`, `WebAuthnAuthenticationProcessor`, `WebAuthnRegistrationProcessor`, `Base64Utils`
- **Implementation**: FIDO2 assertion verification; credential registration; attestation validation; Base64 encoding for credential data.
- **Repos**: OpenAM

#### HOTP (HMAC-based One-Time Password)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-hotp/`
- **Key Classes**: `com.sun.identity.authentication.modules.hotp.HOTP`, `HOTPAlgorithm`, `DefaultSMSGatewayImpl`, `SMSGateway`
- **Implementation**: Time-independent OTP (counter-based); SMS delivery; phone number validation; configurable retry attempts.
- **Repos**: OpenAM, WrenAM

#### OATH (TOTP/HOTP)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-oath/`
- **Key Classes**: `org.forgerock.openam.authentication.modules.oath.OATH`, `TOTPAlgorithm`, `SharedSecretProvider`, `DefaultSharedSecretProvider`
- **Implementation**: Time-based OTP (TOTP, RFC 6238); shared secret storage; pluggable secret providers; configurable time window.
- **Repos**: OpenAM, WrenAM

#### Persistent Cookie
- **Module Path**: `OpenAM/openam-authentication/openam-auth-persistentcookie/`
- **Key Classes**: Classes for cookie-based stateless device recognition
- **Implementation**: Long-lived authentication cookies; device fingerprinting; cookie encryption.
- **Repos**: OpenAM, WrenAM

#### Device ID Match
- **Module Path**: `OpenAM/openam-authentication/openam-auth-device-id/`
- **Key Classes**: `org.forgerock.openam.authentication.modules.deviceprint.DeviceIdMatch`, `DevicePrintDao`, `ProfilePersister`, `PersistModuleProcessor`, `DeviceIdSave`
- **Implementation**: Device fingerprinting (device attributes); profile persistence; device recognition for step-up auth.
- **Repos**: OpenAM, WrenAM

#### Push Authentication
- **Module Path**: `OpenAM/openam-authentication/openam-auth-push/`
- **Key Classes**: `org.forgerock.openam.authentication.modules.push.AbstractPushModule`, `AuthenticatorPushRegistration`, `UserPushDeviceProfileManager`
- **Implementation**: Out-of-band push notifications; device registration; async approval flows.
- **Repos**: OpenAM, WrenAM

#### QR Code Authentication
- **Module Path**: `OpenAM/openam-authentication/openam-auth-qr/`
- **Key Classes**: `org.openidentityplatform.openam.authentication.modules.QR`, `QRPrincipal`
- **Implementation**: QR code generation; scanning/linking flow.
- **Repos**: OpenAM

#### Windows Desktop SSO / IWA
- **Module Path**: `OpenAM/openam-authentication/openam-auth-windowsdesktopsso/`
- **Key Classes**: `com.sun.identity.authentication.modules.windowsdesktopsso.WindowsDesktopSSO`, `WindowsDesktopSSOConfig`, `WindowsDesktopSSOPrincipal`
- **Implementation**: Kerberos/SPNEGO negotiation; Windows credential pass-through; browser integration.
- **Repos**: OpenAM, WrenAM

#### NTLMv2
- **Module Path**: `OpenAM/openam-authentication/openam-auth-ntlmv2/`
- **Key Classes**: NTLMv2-specific authentication handlers
- **Implementation**: NTLMv2 message exchange; NT hash computation.
- **Repos**: OpenAM, WrenAM

#### RSA SecureID
- **Module Path**: `OpenAM/openam-authentication/openam-auth-securid/`
- **Key Classes**: SecureID integration classes
- **Implementation**: RSA SecureID agent library integration; token validation.
- **Repos**: OpenAM, WrenAM

#### HTTP Basic Authentication
- **Module Path**: `OpenAM/openam-authentication/openam-auth-httpbasic/`
- **Key Classes**: HTTP Basic credential extraction
- **Implementation**: Base64 decode; Authorization header parsing; username/password validation.
- **Repos**: OpenAM, WrenAM

#### JDBC / Database
- **Module Path**: `OpenAM/openam-authentication/openam-auth-jdbc/`
- **Key Classes**: JDBC-based user lookup
- **Implementation**: SQL queries; prepared statements; configurable schemas; password hashing (MD5, SHA, etc.).
- **Repos**: OpenAM, WrenAM

#### Datastore (Identity Repository)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-datastore/`
- **Key Classes**: Plugin-based datastore abstraction
- **Implementation**: Pluggable user store (LDAP, custom); abstraction layer for identity lookup.
- **Repos**: OpenAM, WrenAM

#### Anonymous (Permit All)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-anonymous/`
- **Key Classes**: Anonymous authentication (no credentials required)
- **Implementation**: Passwordless auth; anonymous user creation.
- **Repos**: OpenAM, WrenAM

#### Membership (Group-based)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-membership/`
- **Key Classes**: Group membership validation
- **Implementation**: LDAP group queries; dynamic membership; role-based access.
- **Repos**: OpenAM, WrenAM

#### Application-Scoped Authentication
- **Module Path**: `OpenAM/openam-authentication/openam-auth-application/`
- **Key Classes**: Application-specific auth context
- **Implementation**: Multi-tenancy support; per-app auth chains.
- **Repos**: OpenAM

#### Adaptive Authentication
- **Module Path**: `OpenAM/openam-authentication/openam-auth-adaptive/`
- **Key Classes**: Risk-based adaptive auth
- **Implementation**: Risk scoring; context-aware auth decisions; ML-ready architecture.
- **Repos**: OpenAM, WrenAM

#### Scripted Authentication
- **Module Path**: `OpenAM/openam-authentication/openam-auth-scripted/`
- **Key Classes**: `org.forgerock.openam.authentication.modules.scripted.Scripted`, `ScriptIdentityRepository`, `ScriptedClientUtilityFunctions`, `ScriptHttpRequestWrapper`
- **Implementation**: Groovy/JavaScript execution; custom auth flows; extensible callbacks; HTTP request access.
- **Repos**: OpenAM, WrenAM

#### Amster (Utility / Meta-auth)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-amster/`
- **Key Classes**: Amster integration helpers
- **Implementation**: Configuration/management auth support.
- **Repos**: OpenAM, WrenAM

#### reCAPTCHA
- **Module Path**: `OpenAM/openam-authentication/openam-auth-recaptcha/`
- **Key Classes**: reCAPTCHA v2/v3 integration
- **Implementation**: Bot detection; challenge flow; risk scoring.
- **Repos**: OpenAM, WrenAM

#### NT / Legacy Windows
- **Module Path**: `OpenAM/openam-authentication/openam-auth-nt/`
- **Key Classes**: NT domain auth (legacy)
- **Implementation**: Windows NT domain controller queries; pre-NTLM support.
- **Repos**: OpenAM, WrenAM

#### MSISDN (Mobile Number)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-msisdn/`
- **Key Classes**: Mobile subscriber number auth
- **Implementation**: Telecom SIM-based identity; SMS gateway integration.
- **Repos**: OpenAM, WrenAM

#### FR OATH (ForgeRock Authenticator)
- **Module Path**: `OpenAM/openam-authentication/openam-auth-fr-oath/`
- **Key Classes**: ForgeRock OATH implementation
- **Implementation**: Proprietary OATH format; device app integration.
- **Repos**: OpenAM, WrenAM

### Authorization Frameworks

#### XACML 3.0 Policy Engine
- **Module Path**: `OpenAM/openam-entitlements/`
- **Key Classes**: `com.sun.identity.entitlement.xacml3.XACMLReaderWriter`, `XACMLPrivilegeUtils`, `XACMLConstants`, `org.forgerock.openam.xacml.v3.XACMLApplicationUtils`
- **Implementation**: XACML 3.0 schema parsing; policy rule evaluation; attribute-based access control (ABAC); JSON policy export/import; privilege conversion.
- **Repos**: OpenAM, WrenAM

#### OAuth 2.0 Scopes & Flows
- **Module Path**: `OpenAM/openam-oauth2/`
- **Key Classes**: `org.forgerock.oauth2.core.OAuth2Request`, `org.forgerock.openam.oauth2.OAuth2Utils`, `OAuth2ProviderSettings`, `OAuth2Jwt`
- **Implementation**: Authorization Code, Implicit, Resource Owner Password, Client Credentials flows; scope parsing (space-delimited); refresh token handling; JWT bearer assertions; introspection (RFC 7662).
- **Repos**: OpenAM, WrenAM

#### UMA 2.0 (User-Managed Access)
- **Module Path**: `OpenAM/openam-uma/`
- **Key Classes**: `org.forgerock.openam.uma.UmaGuiceModule`, `UMAServiceEndpointApplication`, `IdTokenClaimGatherer`, `UmaLabelsStore`
- **Implementation**: Resource owner delegation; permission tickets; AAT (authorization API token); resource sets; sharing policies.
- **Repos**: OpenAM, OpenIG (as filter), WrenAM

#### Policy Agents & Entitlements
- **Module Path**: `OpenAM/openam-core/` (policy evaluation), `OpenAM/openam-entitlements/`
- **Key Classes**: `PolicyConstants`, `PolicyMonitor`, `PolicyPrivilegeManager`
- **Implementation**: Policy decision points (PDP); privilege evaluation; resource-based access control; caching strategies.
- **Repos**: OpenAM, WrenAM

### Directory Protocols

#### LDAPv3
- **Module Path**: `OpenDJ/opendj-core/`
- **Key Classes**: `org.forgerock.opendj.ldap.LDAPListener`, `LDAPConnectionFactoryImpl`, `LDAPConnectionImpl`, `org.forgerock.opendj.ldap.ServerConnectionFactory`, `org.forgerock.opendj.ldap.SearchScope`
- **Implementation**: Full LDAPv3 server + client library; reactive streams (RxJava 3); persistent search (PSO); controls (ManageDesuper, GetEffectiveRights); StartTLS for encryption; TLS/SSL support via SSLContextBuilder; LDAP URLs (RFC 4516).
- **Repos**: OpenDJ, OpenAM (embedded client)

#### DSML v2 (Directory Services Markup Language)
- **Module Path**: `OpenDJ/opendj-dsml-servlet/`
- **Key Classes**: `org.opends.dsml.protocol.DSMLServlet`, `DSMLSearchOperation`, `DSMLModifyOperation`, `DSMLModifyDNOperation`, `DSMLDeleteOperation`, `DSMLAddOperation`, `DSMLCompareOperation`, `DSMLAbandonOperation`, `DSMLExtendedOperation`
- **Implementation**: XML SOAP-based LDAP gateway; HTTP/SOAP binding; full LDAP operation support via DSML.
- **Repos**: OpenDJ

#### REST2LDAP Gateway
- **Module Path**: `OpenDJ/opendj-rest2ldap/`, `OpenDJ/opendj-rest2ldap-servlet/`
- **Key Classes**: REST endpoints for LDAP queries; RFC 7662 token introspection support; CTS (Core Token Service) access token resolution; HTTP Basic auth; OAuth2 bearer tokens.
- **Implementation**: RESTful LDAP API; JSON request/response; JSON query syntax; authorization plugins (RFC 7662, CTS, HTTP Basic, direct LDAP bind); proxy auth; persistent search.
- **Repos**: OpenDJ

### Federation Protocols

#### SAML 2.0 (IdP + SP)
- **Module Path**: `OpenAM/openam-federation/openam-federation-library/`, `OpenAM/openam-federation/OpenFM/`
- **Key Classes**: `com.sun.identity.saml2.common.SAML2ConfigService`, `com.sun.identity.saml.servlet.SAMLPOSTProfileServlet`, `com.sun.identity.saml.servlet.SAMLSOAPReceiver`, `SAML2AssertionValidator`, `SAML2Token`, `SAML2CTSPersistentStore`
- **Implementation**: SAML 2.0 assertions (signed/encrypted); POST/Artifact/SOAP bindings; metadata generation & parsing; IdP-initiated & SP-initiated SSO; SLO (Single Logout); assertion attributes; NameID formats; AuthnContext; persistent search for session replication.
- **Repos**: OpenAM, WrenAM

#### SAML 1.1 (Legacy)
- **Module Path**: `OpenAM/openam-federation/openam-federation-library/`
- **Key Classes**: `com.sun.identity.saml.SAMLClient`, `SAML11AssertionValidator`, `com.sun.identity.federation.message.FSSAMLRequest`
- **Implementation**: Legacy SAML 1.1 assertion support; artifact binding; hot-deployment support for backward compatibility.
- **Repos**: OpenAM, WrenAM

#### WS-Federation (Microsoft)
- **Module Path**: `OpenAM/openam-federation/openam-federation-library/`, `OpenAM/openam-federation/OpenFM/`
- **Key Classes**: `com.sun.identity.wsfederation.servlet.WSFederationService`, `WSFederationClient`, `WSFederationConstants`, `WSFederationMetaManager`, `WSFederationMetaSecurityUtils`, `CreateWSFedMetaDataTemplate`, `WSFederationSingleLogoutHandler`
- **Implementation**: WS-Federation protocol; metadata management; security token service (STS) integration; passive auth flows; realm/home realm discovery.
- **Repos**: OpenAM, WrenAM

#### Liberty Alliance / ID-FF (Legacy)
- **Module Path**: `OpenAM/openam-federation/openam-federation-library/`
- **Key Classes**: `com.sun.liberty.jaxrpc.*`, `com.sun.identity.liberty.ws.common.wsse.*`, `WSX509KeyManager`
- **Implementation**: Liberty ID-FF protocol (pre-SAML2); JAX-RPC SOAP bindings; WS-Security headers; X.509 key management.
- **Repos**: OpenAM, WrenAM

#### Web Services Security (WSS)
- **Module Path**: `OpenAM/openam-federation/OpenFM/`
- **Key Classes**: `com.sun.identity.wss.security.ConfiguredWSCSecurityMech`, `ConfiguredWSPSecurityMech`, `WSSAuthModule`, `WSSPolicyManager`, `SAML2AssertionValidator`, `SAML2Token`, `SAML2TokenUtils`
- **Implementation**: WS-Security header processing; SAML token in SOAP messages; XML signature/encryption validation; policy-based message protection.
- **Repos**: OpenAM, WrenAM

#### WS-Trust (Security Token Service)
- **Module Path**: `OpenAM/openam-federation/OpenFM/`
- **Key Classes**: `com.sun.identity.wss.trust.WSTrustFactory`
- **Implementation**: Token transformation (SAML to OAuth2, etc.); RequestSecurityToken (RST) processing.
- **Repos**: OpenAM, WrenAM

### Token Formats

#### SAML Assertions
- **Format**: XML-based signed/encrypted assertions; AttributeStatement, AuthnStatement, AuthzDecisionStatement
- **Storage**: CTS (Core Token Service) via `org.forgerock.openam.cts.impl.SAML2CTSPersistentStore`
- **Usage**: Federation, SSO, authorization decisions
- **Repos**: OpenAM, WrenAM

#### JWT (JWS/JWE)
- **Module Path**: `OpenAM/openam-core/src/main/java/org/forgerock/openam/oauth2/`
- **Key Classes**: `org.forgerock.oauth2.core.OAuth2Jwt`, `org.forgerock.openam.session.stateless.JwtSessionMapper`, `StatelessJWTCache`
- **Implementation**: JWT Bearer tokens (RFC 6750); JWS (signed) & JWE (encrypted); stateless sessions via JWT; claims: sub, iss, exp, aud, iat, nonce
- **Repos**: OpenAM, WrenAM

#### CTS Tokens (Core Token Service)
- **Module Path**: `OpenAM/openam-core/src/main/java/org/forgerock/openam/cts/`
- **Key Classes**: `org.forgerock.openam.cts.CTSPersistentStore`, `CTSPersistentStoreImpl`, `org.forgerock.openam.cts.adapters.SAMLAdapter`, `SessionAdapter`, `org.forgerock.openam.cts.api.fields.SAMLTokenField`, `SessionTokenField`
- **Implementation**: Persistent token store (LDAP or Cassandra backend); opaque tokens with metadata; async connection pooling (CTSAsyncConnectionModule); token expiry management; query workers for cleanup.
- **Repos**: OpenAM, WrenAM

#### Opaque Tokens
- **Implementation**: CTS-backed OAuth2 access tokens; refresh tokens; authorization codes; PAR (Pushed Authorization Requests)
- **Repos**: OpenAM, WrenAM

### Provisioning & Sync

#### OpenIDM Sync Engine
- **Module Path**: `OpenIDM/openidm-core/src/main/java/org/forgerock/openidm/sync/`
- **Key Classes**: `org.forgerock.openidm.sync.impl.SynchronizationService`, `SyncMappings`, `SyncOperation`, `SourceSyncOperation`, `TargetSyncOperation`, `ExplicitSyncOperation`, `ReconciliationService`, `ReconciliationContext`, `SyncAuditEventLogger`
- **Implementation**: Bi-directional identity sync; mapping definitions (source -> target); reconciliation engine (full scan vs. audit); audit logging (SyncAuditEventBuilder); operation correlation; dry-run mode.
- **Repos**: OpenIDM

#### OpenICF Connector Framework
- **Module Path**: `OpenICF/OpenICF-java-framework/`
- **Key Classes**: SPI (Service Provider Interface) for custom connectors; Protobuf RPC communication
- **Implementation**: Connector SDK; ConnectorObject marshalling; attribute schema definitions; object class definitions; operation types (CREATE, UPDATE, DELETE, QUERY, TEST); pooling factory.
- **Repos**: OpenICF

#### Built-in Connectors
- **LDAP Connector**: `OpenICF/OpenICF-ldap-connector/` - LDAPv3 directory provisioning
- **CSV File Connector**: `OpenICF/OpenICF-csvfile-connector/` - CSV file read/write
- **Database Connector**: `OpenICF/OpenICF-databasetable-connector/` - JDBC-based DB provisioning
- **Groovy Connector**: `OpenICF/OpenICF-groovy-connector/` - Custom Groovy script connectors
- **SSH Connector**: `OpenICF/OpenICF-ssh-connector/` - Remote systems via SSH/Telnet
- **XML Connector**: `OpenICF/OpenICF-xml-connector/` - XML file provisioning
- **Kerberos Connector**: `OpenICF/OpenICF-kerberos-connector/` - Kerberos principal management
- **Implementation**: Connector Server (Protobuf RPC); connector bundles (JAR-based); operation adapters; attribute mapping
- **Repos**: OpenICF

#### OpenIDM Workflow (BPMN 2.0)
- **Module Path**: `OpenIDM/openidm-workflow-activiti/`
- **Key Classes**: `org.forgerock.openidm.workflow.activiti.impl.ActivitiServiceImpl`, `ActivitiContext`, `ActivitiUtil`
- **Implementation**: Apache Activiti BPMN 2.0 engine; workflow definitions (XML); task forms; process variables; event-driven triggers.
- **Repos**: OpenIDM

#### Provisioner / System Objects
- **Module Path**: `OpenIDM/openidm-provisioner/`, `OpenIDM/openidm-provisioner-openicf/`
- **Key Classes**: `org.forgerock.openidm.provisioner.ProvisionerService`, `ConnectorConfigurationHelper`, `SystemObjectSetService`, `SystemIdentifier`
- **Implementation**: System resource abstraction; connector lifecycle management; transformation scripts; operation scripts (source/target); dry-run mode.
- **Repos**: OpenIDM

### Transport & Security

#### TLS/SSL (Client/Server)
- **Implementation**:
  - OpenDJ: `org.forgerock.opendj.ldap.SSLContextBuilder`, `org.forgerock.opendj.ldap.requests.StartTLSExtendedRequest`
  - OpenAM: CTS connection pooling with TLS options
  - All: Configurable cipher suites, certificate validation
- **Repos**: All (OpenDJ, OpenAM, OpenIG, OpenIDM, OpenICF)

#### mTLS (Mutual TLS / Client Certificates)
- **Implementation**: Bi-directional certificate authentication; certificate chain validation; CRL/OCSP checks
- **Repos**: OpenDJ (connections), OpenAM (OAuth2 endpoints, CTS)

#### CORS (Cross-Origin Resource Sharing)
- **Implementation**: REST API CORS headers; configurable origins; preflight handling
- **Repos**: OpenAM (REST API), OpenIDM (REST API), OpenDJ (REST2LDAP)

#### HTTP Signatures / Request Signing
- **Implementation**: OAuth2 proof-of-possession (PoP); signed HTTP requests; request validation
- **Repos**: OpenAM

#### PKIX / X.509 Certificate Infrastructure
- **Implementation**: Certificate validation chains; DN parsing; attribute extraction; OID handling
- **Repos**: All (OpenDJ, OpenAM, OpenICF)

### OpenIG (Identity Gateway) Protocols & Handlers

#### Core Filters (39 types in filter/ directory)
- **Key Filter Classes**:
  - Authentication: `HttpBasicAuthFilter` (HTTP Basic)
  - Flow: `ChainFilterHeaplet`, `ConditionalFilterHeaplet`, `SwitchFilter`
  - Security: `CryptoHeaderFilter` (encryption), `PasswordReplayFilterHeaplet`
  - Modification: `HeaderFilter`, `CookieFilter`, `AssignmentFilter`, `EntityExtractFilter`
  - Data: `FileAttributesFilter`, `SqlAttributesFilter`
  - Observability: `HttpAccessAuditFilter`, `MdcRouteIdFilter`, `LogAttachedExceptionFilter`
  - Advanced: `ScriptableFilter`, `ConditionEnforcementFilter`, `LocationHeaderFilter`, `RequestCopyFilter`
- **Repos**: OpenIG

#### Core Handlers (8 types)
- **Key Handler Classes**: `ClientHandler` (HTTP client), `StaticResponseHandler`, `ScriptableHandler`, `SequenceHandler`, `ChainHandlerHeaplet`, `DispatchHandler`, `DesKeyGenHandler`, `WelcomeHandler`
- **Implementation**: Request/response processing pipeline; handler chaining; conditional dispatch; static responses; DES key generation for password replay
- **Repos**: OpenIG

#### OAuth2 Module (openig-oauth2)
- **Implementation**: OAuth2 authorization code flow; token acquisition; scope validation; grant type dispatch
- **Repos**: OpenIG

#### SAML Module (openig-saml)
- **Implementation**: SAML 2.0 federation; IdP/SP SSO; assertion consumption; metadata handling
- **Repos**: OpenIG

#### UMA Module (openig-uma)
- **Implementation**: User-Managed Access 2.0 integration; resource protection; permission validation
- **Repos**: OpenIG

#### OpenAM Integration Module (openig-openam)
- **Implementation**: OpenAM policy agent; session validation; policy enforcement; distributed session management
- **Repos**: OpenIG

### Legacy/Deprecated Protocols

#### ForgeRock CE (OpenAM 11.0.3, Java 7)
- **Status**: Frozen (Nov 2017)
- **Protocols Supported**: SAML 1.1/2.0, OAuth2, WS-Federation, Liberty ID-FF, LDAP, RADIUS, HOTP/TOTP, X.509, Windows Desktop SSO, persistent cookies
- **Location**: `openam-community-edition/`
- **Key Difference**: Older dependencies; Java 7 compatibility

#### WrenAM (16.0.0-M1, Java 17+)
- **Status**: Active alternative fork
- **Rebranding**:
  - `OpenDJ` -> `Wren:DS`
  - `OpenIDM` -> `Wren:IDM`
  - Package prefixes: `wrensec-commons`, `wrends`
- **Differences from OIP**: Guice 3.0 vs 7.0.0, Java 17+ required, same protocol support
- **Key Classes**: Renamed variants of OIP (e.g., `wrenam/openam-uma/src/main/java/org/forgerock/openam/uma/`)
- **Location**: `wrenam/`

### Token Introspection & Validation

#### RFC 7662 (OAuth2 Token Introspection)
- **Supported in**: `OpenDJ/opendj-rest2ldap/` via `rfc7662` resolver
- **Implementation**: Token validation endpoint; active/inactive token status; scope/expiry metadata
- **Repos**: OpenDJ, OpenAM (OAuth2 server)

#### CTS-based Token Introspection
- **Supported in**: `OpenDJ/opendj-rest2ldap/` via CTS resolver
- **Implementation**: Direct CTS lookup for OpenAM tokens; metadata retrieval
- **Repos**: OpenDJ, OpenAM

### Advanced Features

#### Session Management Strategies
- **Stateful (CTS-based)**: Distributed session replicas via LDAP persistent search
- **Stateless (JWT-based)**: Signed & encrypted JWTs; no server state; distributed trust
- **Classes**: `org.forgerock.openam.session.stateless.StatelessSessionManager`, `JwtSessionMapper`, `StatelessJWTCache`
- **Repos**: OpenAM

#### Policy Decision Point (PDP)
- **Implementation**: XACML 3.0 policy evaluation; resource type matching; attribute resolution; obligation handling
- **Repos**: OpenAM

#### Audit & Logging
- **Modules**: `OpenIDM/openidm-audit/`, `OpenAM/openam-core/` (audit filtering)
- **Implementation**: Audit event routing; CTS audit storage; REST API audit trail; JSON structured logs
- **Repos**: OpenIDM, OpenAM

---

## Key Implementation Observations

1. **Stateless Sessions**: OpenAM's JWT-based stateless sessions eliminate session replication bottlenecks via `JwtSessionMapper` + `StatelessJWTCache`.

2. **Reactive LDAP**: OpenDJ's LDAPv3 implementation uses RxJava 3 reactive streams for connection pooling and async operations.

3. **OSGi Architecture (OpenIDM)**: Felix OSGi container allows hot-deployment of provisioning modules; connector framework is plugin-based via SPI.

4. **Protocol Agnostic Connectors**: OpenICF's Connector Server uses Protobuf RPC, enabling polyglot connector implementations (Java, .NET, etc.).

5. **Filter/Handler Pipeline (OpenIG)**: Route-based configuration via JSON; Expression Language for conditional logic; composable filters enable complex policies.

6. **Multi-repo Token Storage**: CTS tokens can use LDAP or Cassandra backends; persistent search enables distributed session replication across data centers.

7. **Social Auth Extensibility**: OAuth2 auth module supports arbitrary providers via HTTP endpoint configuration; email verification plugins.

8. **Scripted Extensibility**: Groovy/JavaScript execution in auth modules, workflows, and OpenIG filters enable custom logic without recompilation.

---

**Note**: This inventory reflects the Open Identity Platform suite (OIP) plus legacy forks. WrenAM maintains protocol parity with OIP but uses Java 17+ and renamed packages. ForgeRock CE is frozen and represents OpenAM 11.0.3 baseline (pre-OAuth2 OIDC maturation).
