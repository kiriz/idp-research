# Identity & Access Management: Evolution, Architecture & Modern Landscape

## Executive Summary

This research analyzes the complete lineage of open-source identity management software descended from Sun Microsystems' OpenSSO (2005), through ForgeRock's commercial stewardship (2010-2016), to today's two active community forks: Open Identity Platform (OIP) and Wren Security. The analysis spans 7 Git repositories (250,000+ commits), 683 pages of reference documentation, 450 archived PDFs, 40+ implemented protocols, and 30+ CVEs across a 20-year timeline.

### Key Findings

**1. The ForgeRock closure (November 2016) was the defining event.** It caused a 94% drop in commit velocity within one year and split the community into two forks with divergent strategies. OIP prioritized feature breadth (52 modules, Guice 7.0, Cassandra HA). Wren Security prioritized dependency modernization (Java 17+, Jakarta EE 5.0, SLF4J 2.0) and intentional simplification.

**2. The OIP stack implements more protocols than any single modern alternative.** OpenAM alone has 34+ authentication modules, SAML 2.0 IdP/SP, OAuth 2.0/OIDC provider, XACML 3.0 policy engine, UMA 2.0, WS-Federation, and WS-Trust -- all in one WAR file. No modern platform (Keycloak, Auth0, Ory, Zitadel) matches this breadth, though most surpass it in specific areas (developer experience, cloud-native deployment, Kubernetes integration).

**3. The architecture is a time capsule of 2005-2016 enterprise Java.** Monolithic WAR deployment, JAAS authentication chains, OSGi service model (OpenIDM), Jato UI framework (OpenAM), and deep LDAP coupling. Modern IAM has moved to microservices (Ory), event sourcing (Zitadel), API-first design, and cloud-native deployment. The OIP stack's modular Maven structure hints at decomposition boundaries a rewrite could exploit.

**4. Security risk varies dramatically by fork.** ForgeRock CE 11.0.3 (frozen since 2017) has 4 unpatched critical RCE vulnerabilities including CVE-2021-35464 (CVSS 9.8, actively exploited, Metasploit module available). OIP and Wren:AM have patched all critical CVEs. 60%+ of CVEs across all forks are in third-party dependencies, not OpenAM's own code.

**5. LDAP persists but is being demoted.** OpenDJ remains one of the most capable open-source LDAPv3 implementations (multi-master replication, REST-to-LDAP gateway, RxJava reactive client). But modern platforms use PostgreSQL or CockroachDB as their identity store, with SCIM 2.0 as the wire protocol. LDAP is becoming a compatibility interface rather than the primary store.

**6. The IAM market has bifurcated into composable services and integrated platforms.** The Ory stack represents the composable extreme (4 independent Go binaries). Keycloak and Zitadel represent modern integrated platforms. Auth0/Okta/Cognito represent managed SaaS. The OIP stack fits none of these categories cleanly, which is both its weakness (no modern operational model) and its strength (no vendor lock-in, full protocol coverage).

### Recommendations

| Scenario | Recommendation |
|----------|---------------|
| Running ForgeRock CE 11.0.3 | **Migrate immediately.** Multiple pre-auth RCE exploits with public tooling. |
| Running OIP OpenAM in production | Viable. Pin to latest, monitor CVEs, plan gradual modernization. |
| Greenfield project, cloud-native | Keycloak (self-hosted) or Auth0/Okta (SaaS) unless WS-Federation or XACML required. |
| Greenfield, microservices architecture | Ory stack for maximum decomposition; Zitadel for single-binary simplicity. |
| Legacy app integration needed | OpenIG's credential replay has no modern equivalent. Use it as a bridge. |
| Enterprise IGA (provisioning, workflows) | Commercial (SailPoint, Saviynt) for features; OpenIDM + OpenICF for budget/air-gap. |
| LDAP still required | OpenDJ or 389 DS. Avoid building new LDAP dependencies. |

---

## Document Structure

### Source Extracts (Phase 1 -- Raw Data)

| File | Description | Lines |
|------|-------------|-------|
| [extracts/protocol-inventory.md](extracts/protocol-inventory.md) | Complete inventory of 40+ protocols across all 7 repos | 464 |
| [extracts/version-evolution.md](extracts/version-evolution.md) | Three-way comparison: ForgeRock CE vs OIP vs Wren:AM | 837 |
| [extracts/component-architectures.md](extracts/component-architectures.md) | Architectural analysis of all 5 OIP components | 1,360 |
| [extracts/modern-landscape.md](extracts/modern-landscape.md) | Modern IAM landscape (Keycloak, Ory, Auth0, etc.) | ~500 |
| [extracts/standards-timeline.md](extracts/standards-timeline.md) | Identity standards evolution (LDAP through passkeys) | ~400 |
| [extracts/git-history-analysis.md](extracts/git-history-analysis.md) | Commit velocity, contributors, release timeline across 7 repos | 425 |
| [extracts/security-cve-history.md](extracts/security-cve-history.md) | 30+ CVEs, patch matrix, risk assessment per fork | 155 |
| [extracts/pre-computer-auth-research.md](extracts/pre-computer-auth-research.md) | 5,000 years of authentication patterns | ~350 |

### Analytical Chapters (Phase 2 -- Synthesis)

| Chapter | Title | Lines | Audience |
|---------|-------|-------|----------|
| [01-history.md](chapters/01-history.md) | Historical Narrative | 500 | Everyone |
| [02-authentication-protocols.md](chapters/02-authentication-protocols.md) | Authentication Protocols | 658 | Security architects |
| [03-federation-protocols.md](chapters/03-federation-protocols.md) | Federation Protocols | 879 | Integration engineers |
| [04-authorization-frameworks.md](chapters/04-authorization-frameworks.md) | Authorization Frameworks | 1,002 | Policy architects |
| [05-directory-services.md](chapters/05-directory-services.md) | Directory Services | 1,191 | Infrastructure engineers |
| [06-token-formats.md](chapters/06-token-formats.md) | Token Formats & Sessions | 1,407 | Security engineers |
| [07-openam-analysis.md](chapters/07-openam-analysis.md) | OpenAM Analysis | 504 | Evaluators, architects |
| [08-opendj-analysis.md](chapters/08-opendj-analysis.md) | OpenDJ Analysis | 502 | Directory administrators |
| [09-openidm-analysis.md](chapters/09-openidm-analysis.md) | OpenIDM Analysis | 579 | IGA planners |
| [10-openig-analysis.md](chapters/10-openig-analysis.md) | OpenIG Analysis | 541 | Gateway engineers |
| [11-openicf-analysis.md](chapters/11-openicf-analysis.md) | OpenICF Analysis | 651 | Integration developers |
| [12-modern-architecture.md](chapters/12-modern-architecture.md) | Modern Architecture Patterns | 517 | CTOs, architects |
| [13-comparison-matrices.md](chapters/13-comparison-matrices.md) | Comparison Matrices (8 tables) | 539 | Procurement, evaluators |
| [14-lessons-from-history.md](chapters/14-lessons-from-history.md) | Lessons from History | 500 | Researchers, designers |

### Presentation

| File | Description |
|------|-------------|
| [presentations/iam-evolution-deck.pptx](presentations/iam-evolution-deck.pptx) | 25-slide executive deck covering full research |

**Total: ~10,000+ lines across 14 chapters + 8 extract files + 1 presentation.**

---

## Reading Guide

**For leadership (30 minutes):** This README, then Ch.01 (history) and Ch.13 (comparison matrices).

**For security architects (2 hours):** Ch.02 (auth protocols), Ch.03 (federation), Ch.06 (tokens), then `extracts/security-cve-history.md`.

**For migration planners (2 hours):** Ch.07-11 (component analyses), Ch.13 (comparison matrices), then `extracts/version-evolution.md`.

**For deep technical understanding (full read):** Start with Ch.01, proceed sequentially through Ch.14. The extracts directory provides raw data backing the analysis.

---

## Methodology

This research was conducted by analyzing:

1. **7 Git repositories** -- OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF (OIP), openam-community-edition (ForgeRock CE), wrenam (Wren Security). Full commit history unshallowed and mined for velocity, contributors, security fixes, and release timelines.

2. **Source code analysis** -- Module structures, POM dependencies, authentication module inventories, architectural patterns, and protocol implementations examined across all three forks.

3. **683-page reference PDF** -- ForgeRock OpenAM 12 Reference documentation extracted and structured into 9 chapters.

4. **CVE databases** -- NVD, GitHub Security Advisories, and git commit history cross-referenced to build a complete vulnerability timeline with patch status per fork.

5. **Modern landscape research** -- Current documentation, release notes, and feature matrices for Keycloak, Ory, Auth0, Okta, Cognito, Zitadel, Authentik, 389 DS, FreeIPA, SailPoint, Saviynt, Kong, Envoy, and others.

6. **Standards body publications** -- RFCs, OASIS specifications, W3C recommendations, FIDO Alliance specifications, and NIST publications for protocol evolution timeline.
