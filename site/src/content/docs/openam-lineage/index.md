---
title: The ForgeRock Story — OpenAM Lineage
description: "Sun OpenSSO → ForgeRock → three forks. The definitive account of the IAM software that defined enterprise identity for a decade, including the November 2016 closure and its aftermath."
sidebar:
  order: 1
---

![Fork divergence diagram: ForgeRock CE, OIP OpenAM, and Wren:AM post-closure](/idp-research/diagrams/06-fork-divergence.svg)

# Git History Analysis

> **Generated**: 2026-02-12
> **Repos analyzed**: OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF, openam-community-edition, wrenam
> **Combined commits**: 58,112 across 7 repositories

---

## Executive Summary

1. **OpenDJ is the oldest and most prolific repo** -- 24,107 commits starting Jun 2006 as Sun's OpenDS. It carries 20 years of unbroken history, the only repo predating Oracle's OpenSSO shutdown.

2. **ForgeRock's open-source era (2012-2016) was the high-water mark.** All repos show peak commit velocity in 2014-2016. The combined output across all repos exceeded 10,000 commits/year during 2014-2015.

3. **ForgeRock's closure (Nov 2016) is unmistakable in the data.** Every repo shows a dramatic cliff: OpenAM dropped from 1,816 commits (2016) to 226 (2017). OpenDJ from 1,148 to 66. OpenIDM went completely silent 2017-2018.

4. **Open Identity Platform (OIP) revived the repos starting 2017-2018.** Led by vharseko/Valery Kharseko, OIP has maintained steady low-volume activity (100-300 commits/year per repo) and produced 80+ releases across the suite since 2018.

5. **Wren Security (wrenam) has a different cadence.** Near-zero activity 2017-2021, then a burst starting 2022-2023 with the 15.0.0 milestone release. Led by Pavel Horal and the Orchitech team.

6. **Security posture is actively maintained.** OpenAM alone references 55 CVEs in commit messages. OIP repos show a clear pattern of dependency-upgrade commits addressing known vulnerabilities, especially from 2022 onward.

7. **openam-community-edition is frozen.** Last commit Nov 2017, only 2 tags. It serves purely as a historical snapshot of ForgeRock CE 11.0.3.

8. **Build system churn dominates file hotspots.** pom.xml is the #1 most-modified file in every single repo, often by 3-5x over the next file. This reflects continuous dependency management and version bumps across the Maven multi-module builds.

9. **OpenDJ has the deepest contributor bench** -- 128 unique contributors. OpenAM has 121. The smaller repos (OpenIG: 33, OpenICF: 45) reflect their more focused scope.

10. **The three OpenAM forks share 3,926+ commits of common ancestry** (2012-2014), then diverge. OIP's OpenAM has the most post-fork activity; wrenam has the most structured CVE remediation program.

---

## Detailed Findings

### Per-Repository Summary Table

| Repo | First Commit | Last Commit | Total Commits | Contributors | Tags | Lifespan |
|------|-------------|-------------|---------------|-------------|------|----------|
| **OpenDJ** | 2006-06-28 | 2026-02-11 | 24,107 | 128 | 82 | 19.6 yrs |
| **OpenAM** | 2012-07-06 | 2026-02-04 | 9,585 | 121 | 81 | 13.6 yrs |
| **wrenam** | 2012-07-06 | 2026-02-05 | 8,522 | 95 | 24 | 13.6 yrs |
| **OpenIDM** | 2011-03-17 | 2026-02-05 | 8,145 | 83 | 24 | 14.9 yrs |
| **openam-community-edition** | 2012-07-06 | 2017-11-28 | 4,121 | 57 | 2 | 5.4 yrs |
| **OpenIG** | 2011-10-13 | 2026-02-09 | 1,995 | 33 | 25 | 14.3 yrs |
| **OpenICF** | 2008-09-06 | 2026-02-04 | 1,637 | 45 | 13 | 17.4 yrs |

**Key observations:**
- OpenDJ has 2.5x the commits of the next largest repo, reflecting its origin as the foundational LDAP server
- Three repos share the same first commit date (2012-07-06) -- OpenAM, wrenam, and CE all trace to the same ForgeRock import
- All active OIP repos have commits in Feb 2026, confirming ongoing maintenance

---

### Commit Velocity

#### Commits per year (all repos)

| Year | OpenDJ | OpenAM | wrenam | OpenIDM | CE | OpenIG | OpenICF | **Total** |
|------|--------|--------|--------|---------|-----|--------|---------|-----------|
| 2006 | 1,294 | - | - | - | - | - | - | **1,294** |
| 2007 | 4,696 | - | - | - | - | - | - | **4,696** |
| 2008 | 2,036 | - | - | - | - | - | 241 | **2,277** |
| 2009 | 1,976 | - | - | - | - | - | 444 | **2,420** |
| 2010 | 678 | - | - | - | - | - | 41 | **719** |
| 2011 | 1,530 | - | - | 802 | - | 12 | 121 | **2,465** |
| 2012 | 1,408 | 762 | 762 | 1,502 | 762 | 120 | 60 | **5,376** |
| 2013 | 3,056 | 1,346 | 1,346 | 864 | 1,346 | 18 | 58 | **8,034** |
| 2014 | 2,660 | 1,966 | 1,965 | 1,618 | 1,818 | 565 | 152 | **10,744** |
| 2015 | 2,833 | 2,206 | 2,200 | 1,965 | 98 | 451 | 194 | **9,947** |
| **2016** | **1,148** | **1,816** | **1,816** | **1,218** | **5** | **504** | **124** | **6,631** |
| **2017** | **66** | **226** | **17** | **-** | **92** | **-** | **-** | **401** |
| 2018 | 219 | 291 | 3 | - | - | 57 | 65 | **635** |
| 2019 | 93 | 203 | - | 40 | - | 36 | 21 | **393** |
| 2020 | 73 | 150 | - | - | - | 33 | - | **256** |
| 2021 | 30 | 145 | 5 | - | - | 29 | - | **209** |
| 2022 | 67 | 144 | 51 | - | - | 48 | - | **310** |
| 2023 | 36 | 97 | 184 | - | - | 25 | - | **342** |
| 2024 | 103 | 117 | 43 | 88 | - | 43 | 81 | **475** |
| 2025 | 100 | 107 | 120 | 44 | - | 48 | 32 | **451** |
| 2026* | 5 | 9 | 10 | 4 | - | 6 | 3 | **37** |

*2026 is partial (through Feb 12)*

**Velocity analysis:**
- **Peak year**: 2014 with 10,744 combined commits -- ForgeRock's most productive open-source year
- **Cliff year**: 2017 saw a 94% drop (6,631 -> 401) -- the ForgeRock closure effect
- **Recovery**: Post-fork activity stabilized at 300-500 commits/year from 2022 onward
- **wrenam's revival**: 184 commits in 2023 (up from 5 in 2021) marks its 15.0.0 push
- **OpenIDM gap**: Zero commits 2017-2018, then zero again 2020-2023 before OIP revived it in 2024

---

### Release Timeline

#### Unified chronological timeline (major releases only)

'''
2006 .............. OpenDJ: initial OpenDS commit
2013 .............. OpenAM 11.0.0 | OpenDJ SDK 2.6.x series
2014 .............. OpenAM 12.0.0
2015 .............. OpenAM 13.0.0 | OpenDJ 3.0.0-Mx | CE 11.0.3 (sustaining)
2016 Jan .......... OpenAM 13.0.0 (GA)
2016 Oct-Nov ...... OpenAM 14.0.0-M1/M2 | OpenDJ 4.0.0-M1
     ------------ ForgeRock closes source (Nov 2016) ------------
2017 Apr .......... CE 11.0.3 (community edition tag)
2017 Jun .......... OpenDJ: last-common-commit-with-opendj-sdk-repo
2018 Feb-Mar ...... OpenDJ 4.0.x-4.1.x | OpenAM 14.0.x
2018 Mar .......... OpenIG 5.0.0-5.0.2
2018 Apr .......... OpenICF 1.5.0
2018-2019 ......... Rapid OIP releases: OpenAM 14.1.x (13 patches), OpenDJ 4.1-4.4
2019 Mar-Jul ...... OpenAM 14.2-14.4 | OpenIDM 5.5.0
2020 .............. OpenAM 14.5.x-14.6.x | OpenDJ 4.4.4-4.4.9
2021 .............. OpenAM 14.6.2-14.6.4 | OpenDJ 4.4.10-4.4.11
2022 .............. OpenAM 14.6.5-14.7.0 | OpenDJ 4.4.12-4.5.1
2023 Feb .......... wrenam 15.0.0-M1
2023 Oct .......... wrenam 15.0.0 (GA) | OpenAM 14.7.4-14.8.1
2024 May .......... OpenAM 15.0.0 | OpenIDM 6.0.0 | OpenICF 1.6.0
2024 Aug-Sep ...... OpenDJ 4.7.0-4.8.0 | OpenIG 5.2.4-5.3.0 | OpenICF 1.7.0
2024 May-Jun ...... wrenam 15.1.0-15.1.1
2025 Jan .......... wrenam 15.1.2-15.1.3

---

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

