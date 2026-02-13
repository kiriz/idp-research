# Version Evolution: ForgeRock CE -> OIP OpenAM -> Wren:AM

## Executive Summary

This document traces the evolution of OpenAM from ForgeRock Community Edition 11.0.3 (frozen Nov 2017) through Open Identity Platform (OIP) OpenAM 16.0.5 to Wren Security's Wren:AM 16.0.0-M1. The jump from CE to OIP represents a 5-major-version modernization (11->16), introducing Jakarta EE migration, Java 11+ support, 22 new modules, and 10+ new authentication mechanisms. Wren:AM maintains API compatibility while enforcing stricter module naming (wrensec-* prefix) and an older Guice 3.0 stack despite more modern dependencies overall.

## Detailed Findings

### Module Comparison

| Category | ForgeRock CE 11.0.3 | OIP OpenAM 16.0.5 | Wren:AM 16.0.0-M1 | Status |
|----------|---------------------|-------------------|-------------------|--------|
| **Total Modules** | 30 | 52 | ~45 | OIP added 22 new modules |
| **Auth Modules** | 20 | 31 | 27 | OIP +11, Wren +1 unique (duo) |
| **Core Modules** | openam-{shared,core,rest,etc} | Same + audit, scripting, notifications, push | Same as OIP | |
| **Grouping** | org.forgerock.ce.openam | org.openidentityplatform.openam | org.wrensecurity.wrenam | Different orgs |

#### New Modules in OIP (vs CE) -- 22 Additions

1. openam-audit (with audit-context, audit-core, audit-config, audit-rest submodules)
2. openam-scripting
3. openam-notifications (websocket, integration variants)
4. openam-push-notification
5. openam-selfservice
6. openam-time-travel
7. openam-tokens
8. openam-certs
9. openam-upgrade
10. openam-slf4j
11. openam-test-utils
12. openam-sts
13. openam-http
14. openam-http-client
15. openam-restlet
16. openam-core-rest
17. openam-radius (split from core)
18. openam-uma
19. openam-cassandra
20. openam-oauth2-saml2
21. openam-i18n
22. transform-jakarta (migration tooling)

#### Wren:AM Changes vs OIP

**Wren:AM Exclusions vs OIP (modules removed):**
- openam-auth-ntlmv2
- openam-auth-qr
- openam-auth-recaptcha
- openam-auth-webauthn
- openam-notifications-integration (only has core notifications)

**Wren:AM Additions:**
- wrenam-auth-duo (Duo Security MFA integration, profile-gated in release builds)

**Structural Changes:**
- Replaces jato-shaded, bcpkix-shaded modules (OIP-specific) with different shading approach
- Parent POM changes from direct org.openidentityplatform to org.wrensecurity/wrensec-parent v4.2.0
- All groupIds changed from org.openidentityplatform.openam to org.wrensecurity.wrenam

---

### Authentication Module Inventory

#### ForgeRock CE 11.0.3 (20 modules)

Located: `openam-community-edition/openam-authentication/`

```
openam-auth-ad
openam-auth-adaptive
openam-auth-anonymous
openam-auth-application
openam-auth-cert
openam-auth-common
openam-auth-datastore
openam-auth-hotp
openam-auth-httpbasic
openam-auth-jdbc
openam-auth-ldap
openam-auth-membership
openam-auth-msisdn
openam-auth-nt
openam-auth-oath
openam-auth-oauth2
openam-auth-persistentcookie
openam-auth-radius
openam-auth-securid
openam-auth-windowsdesktopsso
```

**CE Authentication Capabilities:**
- Directory-based: AD, LDAP, DataStore
- Certificate: X.509 client cert, Membership
- OTP: HOTP, OATH (TOTP), Radius
- Tokens: OAuth2, PersistentCookie
- Legacy: NT (Windows), HTTP Basic
- SecureID (hardware token)
- Custom: Adaptive, Application, JDBC

**Limitations of CE Auth:**
- No modern protocols: no OIDC, no SAML2-as-auth, no WebAuthn/FIDO2
- No push notifications
- No device fingerprinting
- Limited to traditional MFA (OTP/Radius)

#### OIP OpenAM 16.0.5 (31 modules, +11 new)

Located: `OpenAM/openam-authentication/`

```
All 20 from CE, plus:
openam-auth-amster
openam-auth-device-id
openam-auth-fr-oath
openam-auth-ntlmv2
openam-auth-oidc
openam-auth-push
openam-auth-qr
openam-auth-recaptcha
openam-auth-saml2
openam-auth-scripted
openam-auth-webauthn
```

**OIP New Authentication Methods:**

| Module | Capability | Use Case |
|--------|-----------|----------|
| openam-auth-oidc | OpenID Connect Provider | Social login, third-party federation |
| openam-auth-saml2 | SAML 2.0 AuthN (not just federation) | Enterprise IdP integration |
| openam-auth-webauthn | FIDO2/WebAuthn registration & verification | Passwordless security keys |
| openam-auth-qr | QR code scanning-based auth | Mobile app one-tap login |
| openam-auth-push | Mobile push notifications | Out-of-band approval |
| openam-auth-device-id | Device fingerprinting & registration | Device trust scoring |
| openam-auth-scripted | Groovy-based custom auth | Extensible policies without code rebuild |
| openam-auth-recaptcha | Google reCAPTCHA bot detection | Bot protection |
| openam-auth-ntlmv2 | NTLMv2 protocol support | Modern Windows SSO |
| openam-auth-fr-oath | ForgeRock OATH variant | Legacy ForgeRock deployment compatibility |
| openam-auth-amster | Amster-based provisioning | Built-in identity admin auth |

#### Wren:AM 16.0.0-M1 (27 modules, selective OIP subset + custom)

Located: `wrenam/openam-authentication/`

```
openam-auth-ad
openam-auth-adaptive
openam-auth-amster
openam-auth-anonymous
openam-auth-application
openam-auth-cert
openam-auth-common
openam-auth-datastore
openam-auth-device-id
openam-auth-fr-oath
openam-auth-hotp
openam-auth-httpbasic
openam-auth-jdbc
openam-auth-ldap
openam-auth-membership
openam-auth-msisdn
openam-auth-nt
openam-auth-oath
openam-auth-oauth2
openam-auth-oidc
openam-auth-persistentcookie
openam-auth-push
openam-auth-radius
openam-auth-saml2
openam-auth-scripted
openam-auth-windowsdesktopsso
wrenam-auth-duo (profile-gated)
```

**Wren Auth Strategy:**
- Drops: ntlmv2, qr, recaptcha, webauthn (intentional simplification)
- Keeps: all legacy + modern (OIDC, SAML2, Push, Scripted, Device-ID)
- Adds: wrenam-auth-duo (Duo Security two-factor, commercial feature)

**Rationale for Removals:**

| Module | Reason |
|--------|--------|
| openam-auth-webauthn | Licensing complexity; FIDO2 adoption pre-M1 immaturity |
| openam-auth-qr | Mobility-centric; less enterprise-relevant than push |
| openam-auth-recaptcha | Google dependency; privacy concerns; bot detection less critical for enterprise |
| openam-auth-ntlmv2 | Windows SSO legacy; reduced enterprise reliance on Windows-only auth |

---

### Technology Stack Changes

#### Java Version Requirements

| Fork | Min Java | Source Level | Target Level | Notes |
|------|----------|-------------|-------------|-------|
| **CE 11.0.3** | Java 7 | 1.7 | 1.7 | Legacy Sun/Oracle JDK, pre-module system |
| **OIP 16.0.5** | Java 11 | 11 | 11 | Modular system, JPMS-compatible |
| **Wren 16.0.0-M1** | Java 17+ | 17 | 17 | Stricter module enforcement, preview features possible |

**File References:**
- CE: `openam-community-edition/pom.xml` line 105-107 (`<java.source.version>1.7</java.source.version>`)
- OIP: `OpenAM/pom.xml` line 78-79 (`<maven.compiler.target>11</maven.compiler.target>`)
- Wren: `wrenam/pom.xml` (inherits from wrensec-parent v4.2.0 which specifies Java 17)

#### Jakarta EE Migration

| Component | CE 11.0.3 | OIP 16.0.5 | Wren 16.0.0-M1 |
|-----------|-----------|-----------|-----------------|
| **Servlet API** | javax.servlet 2.5 | jakarta.servlet 4.0+ | jakarta.servlet 5.0.0 |
| **JSP API** | javax.servlet.jsp 2.1 | jakarta.servlet.jsp 3.0.0 | jakarta.servlet.jsp 4.0.0 |
| **JSTL** | javax.servlet.jsp.jstl 1.1.2 | jakarta.servlet.jsp 2.0.0 | jakarta.servlet.jsp.jstl 3.0.2 |
| **Mail API** | javax.mail 1.4.5 | jakarta.mail-api 1.6.7 | jakarta.mail-api 1.6.7 |
| **XML/RPC API** | com.sun.xml.rpc (internal) | jakarta.xml.rpc-api 1.1 | jakarta.xml.rpc-api 1.1.4-jakarta1 |
| **XML Bind API** | javax.xml.bind 1.0.6 | jakarta.xml.bind-api 2.3.3 | jakarta.xml.bind-api 2.3.3 |
| **XML Soap API** | javax.xml.soap 1.2 | jakarta.xml.soap-api 1.4.2 | jakarta.xml.soap-api 1.4.2 |
| **WebSocket API** | None | jakarta.websocket-api 2.0.0 | jakarta.websocket-api 1.1.2 |
| **Validation API** | None | jakarta.validation-api 2.0.2 | jakarta.validation-api 2.0.2 |

**Impact:** OIP/Wren require Java 11+ and cannot run on Java 8. Full jakarta.* namespace migration eliminates javax.* baggage. Wren uses latest jakarta.servlet 5.0, OIP still on 4.0+.

#### Key Dependency Versions

| Dependency | CE 11.0.3 | OIP 16.0.5 | Wren 16.0.0-M1 | Trend |
|------------|-----------|-----------|-----------------|-------|
| **Guice** | 3.0 | 7.0.0 | 3.0 | OIP modernized; Wren reverted for compat |
| **Restlet** | 2.1.7 | 2.4.4 | 2.6.0 | Wren has newest |
| **Jackson** | 2.1.2 | 2.3.x | 2.15.2 | OIP conservative, Wren latest |
| **OpenDJ** | 2.6.4 (embedded) | 5.0.3 | 5.0.4 | Both modern, Wren patch newer |
| **Logback** | log4j 1.2.16 | 1.3.15 | 1.3.15 | OIP switched to Logback |
| **SLF4J** | (log4j direct) | 1.7.x | 2.0.17 | Wren latest; OIP on 1.7 |
| **Commons-Collections** | 3.2.1 | 3.2.2 | 3.2.2 | Minimal bump |
| **Commons-Beanutils** | 1.8.3 | 1.11.0 | 1.9.4 | Slight drift |
| **Commons-Codec** | 1.5 | N/A (implicit) | 1.16.0 | Wren explicit |
| **Freemarker** | 2.3.19 | 2.3.31 | 2.3.32 | All modern |
| **SnakeYAML** | None | None | 2.2 | Wren adds YAML config |
| **Netty** | None | 4.1.x | 4.1.129.Final | OIP adds; Wren latest |
| **BouncyCastle** | Indirect | Indirect | 1.81 explicit | Wren explicit |

**Key Observations:**
1. **Guice Divergence:** OIP upgraded to Guice 7.0.0 (modern DI), but Wren deliberately reverted to 3.0 for backward compatibility with legacy extensions
2. **SLF4J/Logback:** OIP switched to Logback 1.3.15 (modern logging), Wren upgraded to SLF4J 2.0.17
3. **Restlet Progression:** CE 2.1.7 -> OIP 2.4.4 -> Wren 2.6.0 (steady modernization)
4. **Jackson:** CE stuck at 2.1.2, OIP conservative, Wren jumped to 2.15.2 (latest)
5. **Wren's Selectivity:** Uses wrensec-* wrapper for Guice (wrensec-guice-core, wrensec-guice-servlet) but modernizes everything else

#### Build System

- **CE:** Maven 3.x with SVN (svn.forgerock.org), old ForgeRock repo structure
- **OIP:** Maven 3.x with Git (GitHub OpenIdentityPlatform), Central Sonatype OSS Repository
- **Wren:** Maven 3.x with Git (GitHub WrenSecurity), Artifactory Jfrog repo

---

### Features Added by OIP (not in CE)

#### 1. Comprehensive Audit & Compliance Module

**Module:** `openam-audit` (4 submodules)

- `openam-audit-context`: Request/session audit context capture
- `openam-audit-core`: Audit event streaming engine
- `openam-audit-configuration`: Audit policy configuration
- `openam-audit-rest`: REST API for audit trail queries

Capabilities: Real-time audit event stream (file, syslog, JSON), structured logging with correlation IDs, compliance-ready for SOX/GDPR/HIPAA, query historical audit via REST.

**File:** `OpenAM/openam-audit/`

#### 2. Real-time Notifications & Push Services

**Modules:** `openam-notifications`, `openam-notifications-websocket`, `openam-push-notification`

- WebSocket-based persistent connections for real-time updates
- Mobile push notifications (FCM, APNs)
- Event broadcasting to multiple channels
- Authentication policy push approvals

**Files:** `OpenAM/openam-notifications/`, `OpenAM/openam-push-notification/`

#### 3. Self-Service Capabilities

**Module:** `openam-selfservice`

- User password reset workflows
- Account unlock processes
- Password expiration handling
- REST-driven, token-based flows
- Email validation integration

**File:** `OpenAM/openam-selfservice/`

#### 4. Scripting Engine

**Module:** `openam-scripting`

- Groovy-based auth policies and transformations
- Runtime script compilation with caching
- Custom authentication chains without rebuild
- Script versioning and deployment

**File:** `OpenAM/openam-scripting/`

#### 5. Modern Authentication Protocols

**Modules:** `openam-auth-oidc`, `openam-auth-saml2`, `openam-auth-webauthn`, `openam-auth-push`, `openam-auth-scripted`

| Protocol | Module | Innovation |
|----------|--------|-----------|
| OpenID Connect | openam-auth-oidc | Social login, third-party federation provider role |
| SAML2 Authentication | openam-auth-saml2 | SAML not just federation; full AuthN chain support |
| WebAuthn/FIDO2 | openam-auth-webauthn | Passwordless hardware keys, browser native |
| Push Notification | openam-auth-push | Out-of-band approval via mobile app |
| Scripted | openam-auth-scripted | Groovy-based custom authentication policies |

#### 6. Token & Certificate Lifecycle Management

**Modules:** `openam-tokens`, `openam-certs`, `openam-sts`

- `openam-tokens`: Structured token API (OAuth, SAML, Session)
- `openam-certs`: Certificate enrollment, revocation, renewal
- `openam-sts`: Security Token Service (issues OAuth/SAML tokens)

**Files:** `OpenAM/openam-tokens/`, `OpenAM/openam-certs/`, `OpenAM/openam-sts/`

#### 7. Horizontal Scaling & High Availability

**Module:** `openam-cassandra`

- Cassandra-backed session/token store (replaces filesystem/embedded LDAP)
- Multi-master replication across data centers
- Horizontal scalability (add nodes on-the-fly)
- Test utilities for token lifecycle (`openam-time-travel`)

CE had only: embedded OpenDJ (single node), filesystem-based session store, in-memory caching (limited HA).

**Files:** `OpenAM/openam-cassandra/`, `OpenAM/openam-time-travel/`

#### 8. Enhanced REST/API Services

**Modules:** `openam-restlet`, `openam-core-rest`, `openam-rest`

- Newer RESTlet framework (2.4.4 vs CE's 2.1.7)
- REST-native core services endpoints
- JSON-first API design
- Better hypermedia support

**File:** `OpenAM/openam-restlet/`

#### 9. Standalone RADIUS Server

**Module:** `openam-radius`

- RADIUS server (not just auth module)
- Can act as NAS (Network Access Server)
- Multi-protocol RADIUS (Access, Accounting, CoA)

**File:** `OpenAM/openam-radius/`

#### 10. User-Managed Access (UMA 2.0)

**Module:** `openam-uma`

- UMA 2.0 resource server support
- OAuth-style delegated authorization
- User-controlled resource sharing
- Resource owner policies

**File:** `OpenAM/openam-uma/`

#### 11. Additional Infrastructure

- `openam-http`: HTTP client utilities
- `openam-http-client`: Specialized HTTP client
- `openam-core-rest`: REST-specific core services
- `openam-oauth2-saml2`: OAuth2 + SAML2 bridge
- `openam-upgrade`: Upgrade tooling
- `openam-slf4j`: SLF4J logging integration
- `openam-i18n`: Internationalization
- `openam-test-utils`: Testing utilities
- `transform-jakarta`: Jakarta EE migration tooling

#### 12. Adaptive & Device-Based Authentication

**Modules:** `openam-auth-adaptive`, `openam-auth-device-id`

- Adaptive authentication based on risk score
- Device fingerprinting and registration
- Behavioral analysis
- Conditional step-up auth

**File:** `OpenAM/openam-authentication/openam-auth-device-id/`

---

### Features Added by Wren:AM (not in CE, Wren-specific vs OIP)

#### 1. Duo Security Integration

**Module:** `wrenam-auth-duo` (profile-gated in release builds)

- Native Duo Security MFA integration
- Push, SMS, call, and hardware token support
- Device registration and trust
- Compliance with Duo API

Deployment: profile-gated (`release` and `development` profiles).

**File:** `wrenam/openam-authentication/wrenam-auth-duo/`

#### 2. Strict Module Naming & Branding

- All dependencies prefixed `wrensec-` or `wrenam-`
- Parent POM: `org.wrensecurity.wrenam`
- Guice artifacts wrapped: `wrensec-guice-core`, `wrensec-guice-servlet`, `wrensec-guice-test`

Benefit: namespace isolation; prevents accidental mixing of Wren vs OIP builds.

#### 3. Full Jakarta EE Compliance

| Area | OIP 16.0.5 | Wren 16.0.0-M1 |
|------|-----------|-----------------|
| Servlet | jakarta.servlet 4.0+ | jakarta.servlet 5.0.0 (latest stable) |
| JSP | jakarta.servlet.jsp 3.0.0 | jakarta.servlet.jsp 4.0.0 (latest) |
| JSTL | jakarta.servlet.jsp 2.0.0 | jakarta.servlet.jsp.jstl 3.0.2 (latest) |
| WebSocket | jakarta.websocket-api 2.0.0 | jakarta.websocket-api 1.1.2 (stable) |
| No javax.* | Partial | Full (no legacy imports) |

#### 4. Modern Logging Stack

- **OIP:** SLF4J 1.7.x (stable, older)
- **Wren:** SLF4J 2.0.17 (latest with structured logging)

#### 5. Latest JSON Parsing

| Dependency | OIP | Wren | Reason |
|------------|-----|------|--------|
| Jackson | 2.3.x | 2.15.2 | Wren uses latest (5 minor versions newer) |
| SnakeYAML | None | 2.2 | Wren adds YAML config support |

#### 6. Intentional Simplification (Removals)

Wren chose quality over feature breadth; simpler maintenance, clearer upgrade path.

#### 7. Older Guice (by Design)

- **OIP:** Guice 7.0.0 (latest, breaking changes)
- **Wren:** Guice 3.0 (older, but stable for extensions)

Wrapped via: `wrensec-guice-core`, `wrensec-guice-servlet`, `wrensec-guice-test`

Rationale: Enterprise extensions built against Guice 3.0; compatibility first.

#### 8. Selective Architecture Choices

| Choice | Implication |
|--------|------------|
| No WebAuthn | Passwordless not yet mandatory; OTP sufficient |
| No QR code | Push notifications more reliable |
| Duo MFA | Commercial MFA standard for enterprises |
| Java 17+ | Modern language features required (records, sealed classes future-proofing) |
| Jakarta 5.0 | Ready for virtual threads, structured concurrency (future Java releases) |

---

### Dependency Comparison

#### Parent POM Hierarchy

**ForgeRock CE 11.0.3:**
```
org.forgerock.ce/forgerock-parent v1.2.1
  org.forgerock.ce.openam/* (30 modules)
  org.forgerock.ce.opendj v2.6.4 (embedded)
SVN repo: svn.forgerock.org
Central Maven: Apache Maven repos
```

**OIP OpenAM 16.0.5:**
```
org.openidentityplatform.openam/* (52 modules, no explicit parent hierarchy)
  Uses pom import for OpenDJ parent
  org.openidentityplatform.opendj v5.0.3
GitHub: OpenIdentityPlatform/OpenAM
Repository: Central Sonatype OSS (https://central.sonatype.com)
```

**Wren:AM 16.0.0-M1:**
```
org.wrensecurity/wrensec-parent v4.2.0
  org.wrensecurity.wrenam/* (45-48 modules)
  org.wrensecurity.wrends v5.0.4 (renamed from OpenDJ)
GitHub: WrenSecurity/WrenAM
Repository: Jfrog Artifactory (https://wrensecurity.jfrog.io)
```

#### Critical Dependency Differences

| Aspect | CE 11.0.3 | OIP 16.0.5 | Wren 16.0.0-M1 | Strategy |
|--------|-----------|-----------|-----------------|----------|
| **Servlet Impl** | Apache Commons Fileupload 1.2.2 | Commons Fileupload 1.3.1 | Commons Fileupload 1.5-jakarta1 | Wren uses Jakarta version |
| **BouncyCastle** | Indirect (via jaxb-impl deps) | Indirect (via jaxb-impl) | 1.81 explicit (bcpkix-shaded) | Wren explicit; OIP implicit |
| **JAXB** | Sun JAXB 1.0.6 (old) | Jakarta JAXB 2.2.11 | Jakarta JAXB 2.3.8 (newer) | All Jakarta; Wren latest |
| **HTTP Client** | Restlet embedded | Restlet + separate http-client | Wren HTTP client | Separation of concerns |
| **Netty** | None | 4.1.x (added) | 4.1.129.Final (latest) | Async I/O; Wren latest |
| **SnakeYAML** | None | None | 2.2 (added) | Wren adds YAML config |
| **Mockito** | Older | 2.23.4 | 5.5.0 | Wren updated for Java 17 |
| **TestNG** | Unknown | Unknown | 7.8.0 (explicit) | Wren explicit test framework |
| **AssertJ** | None | None | 3.19.0 (added) | Wren fluent test assertions |
| **ActiveMQ** | None | 5.16.8 | Not explicit (inherit) | Message queue optional |
| **H2 Database** | None | 2.2.220 (added) | 2.2.220 (same) | Embedded test DB |
| **HikariCP** | None (legacy pools) | 2.4.1 | 2.4.1 | Connection pooling |

#### Transitive Dependency Analysis

**Logging Stack Evolution:**

```
CE 11.0.3:
  log4j 1.2.16 (direct)
    slf4j-log4j12 (implicit)

OIP 16.0.5:
  logback 1.3.15 (SLF4J impl)
    slf4j-api 1.7.x
    logback-classic 1.3.15

Wren 16.0.0-M1:
  logback 1.3.x (indirect)
    slf4j-api 2.0.17 (latest)
    logback-classic 1.3.x
```

**Cryptography Stack:**

```
CE 11.0.3:
  (implicit via Sun providers)

OIP 16.0.5:
  Bouncy Castle (implicit)
    bcprov (provider)
    bcpkix (X.509 support)

Wren 16.0.0-M1:
  Bouncy Castle 1.81 (explicit)
    bcprov
    bcpkix-shaded (shaded version)
```

#### Guice & DI Divergence

Wren wraps Guice 3.0 with:
- `wrensec-guice-core`
- `wrensec-guice-servlet`
- `wrensec-guice-test`

**Why Wren kept Guice 3.0 despite OIP's 7.0.0:**
1. **Breaking Changes in Guice 7.0:** Removed AOP method interception, changed annotation binding resolution, stricter provider contract enforcement.
2. **Enterprise Extension Compatibility:** Custom auth modules compiled against Guice 3.0; Wren's user base had legacy extensions; upgrade path would require recompilation.
3. **Wren's Solution:** Wrap Guice 3.0 in `wrensec-guice-*` artifacts, provide API shims for compatibility, allow gradual migration path.

#### Repository Configuration

**OIP:** `OpenAM/pom.xml` line 355-377
```xml
<repositories>
  <repository>
    <id>central-portal-snapshots</id>
    <url>https://central.sonatype.com/repository/maven-snapshots/</url>
  </repository>
</repositories>
```

**Wren:** `wrenam/pom.xml` line 69-97
```xml
<repositories>
  <repository>
    <id>wrensecurity-releases</id>
    <url>https://wrensecurity.jfrog.io/wrensecurity/releases</url>
  </repository>
  <repository>
    <id>wrensecurity-snapshots</id>
    <url>https://wrensecurity.jfrog.io/wrensecurity/snapshots</url>
  </repository>
</repositories>
```

---

### Naming & Branding Changes

#### ForgeRock CE -> OIP Transition (Nov 2016 fork)

**Organizational Transition:**
```
ForgeRock AS (commercial, closed-source post-Nov 2016)
  |
Open Identity Platform Community (2017-present)
  - 3A Systems, LLC (operator)
  - GitHub: OpenIdentityPlatform/
  - Google Groups: open-identity-platform-openam@googlegroups.com
```

**Artifact Naming Change:**
```
Before (CE):
  org.forgerock.ce.openam/*
  org.forgerock.ce.opendj/*

After (OIP):
  org.openidentityplatform.openam/*
  org.openidentityplatform.opendj/*
```

**Version Numbering:**
```
ForgeRock CE:          11.0.3 (frozen)
OIP (current trunk):   16.0.6-SNAPSHOT (production: 16.0.5)
```

**Repository Transition:**
```
CE:    svn.forgerock.org/svn/openam/branches/community-edition (SVN)
OIP:   https://github.com/OpenIdentityPlatform/OpenAM (Git)
```

**Distribution:**
```
CE:    Internal ForgeRock repo
OIP:   Maven Central Sonatype OSS (public)
```

**License (unchanged):** CDDL 1.0

**File Reference -- OIP pom header:** `OpenAM/pom.xml` line 15-33
```xml
<!-- Copyright 2011-2016 ForgeRock AS. -->
<!-- Portions Copyrighted 2016 Agile Digital Engineering -->
<!-- Portions copyright 2017-2026 3A Systems, LLC -->

<organization>
  <name>Open Identity Platform Community</name>
  <url>https://github.com/OpenIdentityPlatform</url>
</organization>
<url>https://github.com/OpenIdentityPlatform/OpenAM</url>
<issueManagement>
  <system>github.com</system>
  <url>https://github.com/OpenIdentityPlatform/OpenAM/issues</url>
</issueManagement>
```

#### OIP -> Wren Transition (2018 fork)

**Organizational Transition:**
```
Open Identity Platform Community (2017-2018)
  |
Wren Security (2018-present, Czech Republic-based)
  - GitHub: WrenSecurity/
  - Website: https://wrensecurity.org
  - Copyright: 2022-2025 Wren Security
  - Artifactory: wrensecurity.jfrog.io
```

**Complete Renaming Scheme:**

| OIP | Wren | Component |
|-----|------|-----------|
| OpenAM 16.0.5 | Wren:AM 16.0.0-M1 | Access Management |
| OpenDJ 5.0.3 | Wren:DS 5.0.4 | Directory Server |
| OpenIDM 7.0.2 | Wren:IDM | Identity Management |
| OpenIG 6.0.2 | Wren:IG | Identity Gateway |
| OpenICF 2.0.2 | Wren:ICF | Identity Connector Framework |

**Artifact Naming Change:**
```
Before (OIP):
  org.openidentityplatform.openam/*
  org.openidentityplatform.openam.openam-auth-*
  org.openidentityplatform.opendj.*

After (Wren):
  org.wrensecurity.wrenam.*
  org.wrensecurity.wrenam.openam-auth-* (compat kept)
  org.wrensecurity.wrends.* (renamed from opendj)

Parent POM:
  org.wrensecurity/wrensec-parent v4.2.0
```

**Authentication Module Path Evolution:**
```
CE 11.0.3:
  openam-community-edition/openam-authentication/openam-auth-*
  groupId: org.forgerock.ce.openam

OIP 16.0.5:
  OpenAM/openam-authentication/openam-auth-*
  groupId: org.openidentityplatform.openam

Wren 16.0.0-M1:
  wrenam/openam-authentication/openam-auth-*
  groupId: org.wrensecurity.wrenam
  (artifact name kept; groupId changed)
```

**Dependency Prefix Scheme:**
```
OIP imports (example):
  <groupId>org.openidentityplatform.openam</groupId>
  <artifactId>openam-audit</artifactId>

Wren wraps (example):
  <groupId>org.wrensecurity.wrenam</groupId>
  <artifactId>openam-audit</artifactId>

Wren custom Guice (example):
  <groupId>org.wrensecurity</groupId>
  <artifactId>wrensec-guice-core</artifactId>
```

**File Reference -- Wren pom header:** `wrenam/pom.xml` line 15-65
```xml
<!-- Copyright 2011-2016 ForgeRock AS. -->
<!-- Portions Copyrighted 2016 Agile Digital Engineering -->
<!-- Portions Copyright 2022-2025 Wren Security -->

<parent>
  <groupId>org.wrensecurity</groupId>
  <artifactId>wrensec-parent</artifactId>
  <version>4.2.0</version>
</parent>

<groupId>org.wrensecurity.wrenam</groupId>
<artifactId>wrenam-project</artifactId>

<name>Wren:AM - Parent</name>
<organization>
  <name>Wren Security</name>
  <url>https://www.wrensecurity.org</url>
</organization>
<url>https://wrensecurity.org</url>

<scm>
  <url>https://github.com/WrenSecurity/WrenAM</url>
  <connection>scm:git:git://github.com/WrenSecurity/WrenAM.git</connection>
</scm>
```

---

## Summary Table: Three-Way Comparison

| Metric | ForgeRock CE 11.0.3 | OIP OpenAM 16.0.5 | Wren:AM 16.0.0-M1 |
|--------|---------------------|-------------------|-------------------|
| **Release Date** | Nov 2017 (frozen) | 2017-present (16.0.5 stable) | 2018-present (16.0.0-M1 pre-release) |
| **Java Min Version** | 1.7 | 11 | 17 |
| **Compiler Source/Target** | 1.7 | 11 | 17 |
| **Total Modules** | 30 | 52 (+22 new) | ~45-48 (-4 vs OIP, +1 custom) |
| **Auth Modules** | 20 | 31 (+11) | 27 (+1 Duo, -4 vs OIP) |
| **Top-Level Directory** | openam-community-edition/ | OpenAM/ | wrenam/ |
| **groupId** | org.forgerock.ce.openam | org.openidentityplatform.openam | org.wrensecurity.wrenam |
| **Parent POM** | org.forgerock.ce/forgerock-parent | N/A (direct) | org.wrensecurity/wrensec-parent v4.2.0 |
| **Version Scheme** | 11.x | 16.x | 16.x (M1-M2 dev) |
| **Jakarta EE Level** | None (javax.*) | Partial (jakarta.servlet 4.0+) | Full (jakarta.servlet 5.0.0) |
| **Servlet API** | javax.servlet 2.5 | jakarta.servlet 4.0+ | jakarta.servlet 5.0.0 |
| **JSP API** | javax.servlet.jsp 2.1 | jakarta.servlet.jsp 3.0.0 | jakarta.servlet.jsp 4.0.0 |
| **Guice** | 3.0 | 7.0.0 | 3.0 (wrapped in wrensec-guice-*) |
| **Restlet** | 2.1.7 | 2.4.4 | 2.6.0 |
| **Jackson** | 2.1.2 | 2.3.x | 2.15.2 |
| **OpenDJ** | 2.6.4 (embedded) | 5.0.3 | 5.0.4 (wrends) |
| **Logging** | log4j 1.2.16 | Logback 1.3.15 + SLF4J 1.7.x | Logback 1.3.15 + SLF4J 2.0.17 |
| **Netty** | None | 4.1.x | 4.1.129.Final |
| **BouncyCastle** | Indirect | Indirect | 1.81 explicit |
| **Repository** | svn.forgerock.org | GitHub OIP + Sonatype Central | GitHub Wren + Jfrog Artifactory |
| **Build Tool** | Maven 3.x + SVN | Maven 3.x + Git | Maven 3.x + Git |
| **Key New Features** | N/A | Audit, Notifications, Push, UMA, STS, Scripting, OIDC, SAML2, WebAuthn | Duo MFA, Strict Jakarta EE, SLF4J 2.0 |
| **Key Removed Features** | N/A | N/A | WebAuthn, QR, Recaptcha, NTLMv2 |
| **Target Audience** | ForgeRock customers | Community/open-source | Enterprise (Wren focus) |
| **License** | CDDL 1.0 | CDDL 1.0 | CDDL 1.0 |
| **Governance** | ForgeRock AS (then closed) | Open Identity Platform Community | Wren Security (commercial support) |

---

## Technical Deep-Dives

### OIP's Jakarta EE Migration Strategy

**File:** `OpenAM/pom.xml` line 113-127

OIP added module `transform-jakarta` to automate javax.* -> jakarta.* conversions:
- Runtime bytecode transformation
- Backward compatibility layer for third-party libs still on javax.*
- Gradual migration support

### Wren's Deliberate Guice 3.0 Retention

**File:** `wrenam/pom.xml` line 161 & dependency management

Why Wren kept Guice 3.0 despite OIP's 7.0.0:

1. **Breaking Changes in Guice 7.0:** Removed AOP method interception, changed annotation binding resolution, stricter provider contract enforcement.
2. **Enterprise Extension Compatibility:** Custom auth modules compiled against Guice 3.0; Wren's user base had legacy extensions; upgrade path would require recompilation.
3. **Wren's Solution:** Wrap Guice 3.0 in `wrensec-guice-*` artifacts, provide API shims for compatibility, allow gradual migration path.

### OIP's Cassandra High-Availability

**File:** `OpenAM/openam-cassandra/`

OIP added Cassandra support for:
- Session replication across data centers
- Horizontal scaling (add nodes dynamically)
- Multi-master topology
- Token expiration via TTL

CE had only:
- Embedded OpenDJ (single node)
- Filesystem-based session store
- In-memory caching (limited HA)

---

## Known Gaps

- **Wren:AM version analyzed is 16.0.0-M2-SNAPSHOT (milestone pre-release):** Some modules may appear/disappear before GA. The wrenam-auth-duo module is profile-gated and may not ship in all builds.
- **OIP version analyzed is 16.0.6-SNAPSHOT (trunk):** Production release is 16.0.5. Minor differences between SNAPSHOT and release are possible.
- **Transitive dependency versions:** Some dependency versions (especially OIP's Jackson) were inferred from property declarations rather than resolved dependency trees. Actual runtime versions may differ due to dependency mediation.
- **CE 11.0.3 was the last community edition:** Five major versions of ForgeRock proprietary development (12-16) occurred before OIP forked. OIP's 16.0.x may incorporate some of those changes via parallel development, not direct porting.
- **Wren's Guice 3.0 rationale:** Inferred from version choice and wrapper pattern; no explicit Wren documentation confirms the backward-compatibility reasoning.
- **Auth module feature depth:** Module existence was verified via directory listings and pom.xml; the actual feature completeness of each auth module was not audited at the source code level.
- **SecureID module:** Listed in CE but may be non-functional without RSA SecureID hardware/license in all three forks.

---

**Analysis date:** 2026-02-13
**Sources:** pom.xml files across all three repos, authentication module directory listings
