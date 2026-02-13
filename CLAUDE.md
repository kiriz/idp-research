# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Workspace Is

A multi-repo research workspace containing the full lineage of open-source Identity & Access Management (IAM) software descended from Sun Microsystems' OpenSSO. All repos are Java/Maven projects under the CDDL license.

### Three Lineages of OpenAM

| Repo | Fork | Version | Java | Status |
|------|------|---------|------|--------|
| `openam-community-edition/` | ForgeRock CE | 11.0.3 | 7 | Frozen (Nov 2017) |
| `OpenAM/` | Open Identity Platform | 16.0.5 | 11+ | Active |
| `wrenam/` | Wren Security | 16.0.0-M1 | 17+ | Active |

### Open Identity Platform Suite (active, primary focus)

| Repo | Role | Version | Java |
|------|------|---------|------|
| `OpenAM/` | Access management (SSO, AuthN, AuthZ, Federation) | 16.0.5 | 11+ |
| `OpenDJ/` | LDAPv3 directory server (identity store) | 5.0.3 | 11+ |
| `OpenIDM/` | Identity lifecycle management (provisioning, sync) | 7.0.2 | 17+ |
| `OpenIG/` | Identity gateway (reverse proxy, policy enforcement) | 6.0.2 | 11+ |
| `OpenICF/` | Connector framework (LDAP, DB, CSV, SSH connectors) | 2.0.2 | 11+ |

### Reference Material

- `OpenAM-12-Reference.pdf` - ForgeRock OpenAM 12 reference documentation

## How the Components Fit Together

```
Users/Apps --> OpenIG (gateway) --> OpenAM (SSO/auth) --> OpenDJ (LDAP store)
                                    OpenIDM (provisioning) --> OpenICF (connectors) --> External Systems
```

- **OpenIG** intercepts HTTP requests, enforces policies, delegates auth to OpenAM
- **OpenAM** handles authentication (34+ modules), authorization, SSO, OAuth2/OIDC, SAML 2.0
- **OpenDJ** stores identity data; supports multi-master replication, SQL/Cassandra backends
- **OpenIDM** manages identity lifecycle (joiner/mover/leaver) via sync and reconciliation
- **OpenICF** provides connectors between OpenIDM and external systems (LDAP, databases, etc.)

## Build Commands

All projects use Maven. Each repo builds independently:

```bash
# OIP repos (all follow same pattern)
mvn install -f OpenAM
mvn install -f OpenDJ
mvn install -f OpenIDM
mvn install -f OpenIG
mvn install -f OpenICF

# WrenAM
cd wrenam && mvn clean package

# ForgeRock CE (requires JDK 7)
cd openam-community-edition && mvn clean install
```

### Running After Build

```bash
# OpenAM - requires FQDN in /etc/hosts (127.0.0.1 login.domain.com)
mvn cargo:run -f OpenAM/openam-server
# -> http://login.domain.com:8080/openam

# OpenDJ
cd OpenDJ/opendj-server-legacy/target/package/opendj && ./setup && bin/start-ds

# OpenIDM
unzip OpenIDM/openidm-zip/target/openidm-*.zip && ./openidm/startup.sh
# -> http://localhost:8080/ (openidm-admin/openidm-admin)

# OpenIG
mvn -f OpenIG/openig-war clean package cargo:run
# -> http://localhost:8080

# OpenICF
unzip OpenICF-java-framework/openicf-zip/target/openicf-*.zip && openicf/bin/ConnectorServer.sh /run
```

### Running Tests

```bash
# Run all tests for a specific repo
mvn test -f OpenAM

# Run tests for a specific module
mvn test -f OpenAM/openam-oauth2

# Run a single test class
mvn test -f OpenAM/openam-oauth2 -Dtest=OAuth2TokenStoreTest

# Skip tests during build
mvn install -f OpenAM -DskipTests
```

## Key Architectural Details

### OpenAM Module Layout (~60 modules)
- `openam-authentication/` - 34+ pluggable auth modules (LDAP, OAuth2, SAML, WebAuthn, HOTP, etc.)
- `openam-core/` - Session management, policy evaluation, audit
- `openam-oauth2/` - OAuth 2.0 authorization server
- `openam-federation/` - SAML 2.0, WS-Federation
- `openam-entitlements/` - XACML 3.0 policy engine
- `openam-rest/` - REST API endpoints
- `openam-cassandra/` - Cassandra session/token store
- `openam-distribution/` - WAR, Docker, tools packaging

### OpenDJ Module Layout (~21 modules)
- `opendj-core/` - LDAP APIs (uses RxJava 3 reactive streams)
- `opendj-server-legacy/` - Main server implementation (1,927 Java files)
- `opendj-rest2ldap/` - REST-to-LDAP gateway
- `opendj-packages/` - DEB, RPM, MSI, Docker, OpenShift

### OpenIDM Architecture (OSGi-based, ~37 modules)
- Uses **Apache Felix** OSGi framework (unlike the others which are WAR-based)
- `openidm-core/` - Sync engine, reconciliation, managed objects
- `openidm-provisioner-openicf/` - OpenICF connector integration
- `openidm-workflow-activiti/` - BPMN 2.0 workflow engine
- `openidm-repo-jdbc/` and `openidm-repo-orientdb/` - Dual repository support
- Routes: `/system/*`, `/managed/*`, `/repo/*`, `/sync/*`, `/recon/*`, `/workflow/*`

### OpenIG Architecture (filter/handler pipeline)
- `openig-core/` - RouterHandler, filters (39 types), handlers (16 types)
- JSON-based route configuration with Expression Language support
- Modules: `openig-oauth2/`, `openig-saml/`, `openig-uma/`, `openig-openam/`

### OpenICF Architecture (SPI/API split)
- `OpenICF-java-framework/` - Core framework (19 sub-modules, Protobuf RPC)
- Built-in connectors: LDAP, CSV, database, XML, SSH, Kerberos, Groovy scripted

## Dependency Chain Between Repos

OpenDJ is the foundation. The inter-repo dependency order for builds:

```
commons (parent POM) -> OpenDJ -> OpenICF -> OpenIDM
                     -> OpenAM -> OpenIG
```

OpenAM depends on OpenDJ (embeddable LDAP). OpenIDM depends on OpenICF. OpenIG depends on OpenAM libs.

## Wren Security vs Open Identity Platform

Both are active forks of ForgeRock. Key differences:
- Wren renamed everything: OpenDJ -> Wren:DS, OpenIDM -> Wren:IDM, etc.
- WrenAM uses `wrensec-commons` and `wrends`; OIP uses `openidentityplatform.commons` and `opendj`
- WrenAM requires Java 17+; OIP OpenAM supports Java 11+
- WrenAM uses Guice 3.0; OIP uses Guice 7.0.0
- Both use Jakarta EE (migrated from Java EE)

## Historical Context

Sun Access Manager (2005) -> Oracle OpenSSO (2010) -> ForgeRock OpenAM (2010-2016, open source) -> ForgeRock closed source (Nov 2016) -> Two community forks: Open Identity Platform (2017) and Wren Security (2018)
