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
2025 Jul .......... OpenAM 15.2.0 | OpenDJ 4.10.0 | OpenIG 5.4.0 | OpenICF 1.8.0
2025 Sep .......... wrenam 16.0.0-M1
2025 Nov .......... OpenAM 16.0.3 | OpenDJ 5.0.1 | OpenIDM 7.0.1 | OpenIG 6.0.1 | OpenICF 2.0.1
2026 Feb .......... OpenAM 16.0.5 | OpenDJ 5.0.3 | OpenIDM 7.0.2 | OpenIG 6.0.2 | OpenICF 2.0.2
'''

**Release cadence observations:**
- **OIP releases in synchronized waves**: OpenAM, OpenDJ, OpenIDM, OpenIG, and OpenICF all got major version bumps in Nov 2025 and Feb 2026
- **OpenAM has the most tags**: 81 releases, averaging ~6 releases/year since 2018
- **wrenam releases less frequently** but with more deliberate milestone (M1, RC, GA) cadence
- **OpenIDM had a 5-year release gap** (5.5.0 in 2019 -> 6.0.0 in 2024)


---

### Contributor Analysis

#### Top 10 contributors across all repos (by total commits)

| Contributor | OpenDJ | OpenAM | wrenam | OpenIDM | CE | OpenIG | OpenICF | Total |
|------------|--------|--------|--------|---------|-----|--------|---------|-------|
| Mark Craig | 1,911 | 661 | 661 | 454 | 638 | 341 | 16 | 4,682 |
| Jean-Noel Rouvignac | 3,278+741 | - | - | - | - | - | - | 4,019 |
| Matthew Swift | 2,222+734 | - | - | - | - | 88 | - | 3,044 |
| jvergara | 1,632 | - | - | - | - | - | - | 1,632 |
| neil_a_wilson | 1,332 | - | - | - | - | - | - | 1,332 |
| Lana (+ Lana Frost) | - | - | - | 1,084+150 | 24+22 | - | - | 1,280 |
| Peter Major | - | 830 | 818 | - | 587 | - | - | 1,249* |
| Ludovic Poitou | 965+426 | - | - | - | - | - | - | 1,391 |
| Phill Cunnington | - | 585 | 590 | - | 211 | - | - | 1,386* |
| vharseko / Valera V.Harseko | - | 480+201 | - | - | - | 94+58+35 | 84+35+26 | 1,013 |

*Some counts overlap between OpenAM/wrenam/CE since they share history*

#### Contributor overlap between OpenAM forks

The three OpenAM-lineage repos (OpenAM, wrenam, openam-community-edition) share the same pre-fork contributors. Key post-fork distinctions:

- **OIP (OpenAM)**: vharseko/Valery Kharseko is the primary post-fork maintainer (680+ commits), supported by Maxim Thomas and the Open Identity Platform Community account
- **Wren Security (wrenam)**: Pavel Horal (192 commits) leads the Wren fork. Quentin Castel (153) and the Orchitech team contribute CVE fixes
- **CE**: No unique post-fork contributors of significance; frozen at the fork point

#### Cross-repo contributors (appearing in 3+ repos)

| Contributor | Repos |
|------------|-------|
| Mark Craig | OpenDJ, OpenAM, wrenam, OpenIDM, CE, OpenIG, OpenICF (all 7) |
| vharseko/Valery Kharseko | OpenAM, OpenIG, OpenICF, OpenDJ |
| Laszlo Hordos | OpenICF, OpenIDM |
| Mark de Reeper | OpenAM, wrenam, CE, OpenIG |
| Jason Lemay | OpenAM, wrenam, CE, OpenIDM |

Mark Craig is the only contributor appearing in all 7 repos -- primarily as a documentation writer (ForgeRock docs team).

---

### File Churn Hotspots

#### Most-modified files per repo (top 10, excluding blank lines)

**OpenAM** (9,585 commits)

| Rank | File | Changes | Category |
|------|------|---------|----------|
| 1 | pom.xml | 1,044 | Build |
| 2 | openam-server-only/pom.xml | 371 | Build |
| 3 | openam-core/pom.xml | 347 | Build |
| 4 | openam-clientsdk/pom.xml | 315 | Build |
| 5 | openam-server/pom.xml | 311 | Build |
| 6 | openam-distribution/.../ssoadmintools/pom.xml | 301 | Build |
| 7 | openam-oauth2/pom.xml | 298 | Build |
| 8 | openam-rest/pom.xml | 294 | Build |
| 9 | openam-shared/pom.xml | 288 | Build |
| 10 | openam-federation/.../pom.xml | 282 | Build |

> All top 30 files in OpenAM are pom.xml files. This is characteristic of a large Maven multi-module project with frequent dependency updates and version bumps.

**OpenDJ** (24,107 commits)

| Rank | File | Changes | Category |
|------|------|---------|----------|
| 1 | pom.xml | 438 | Build |
| 2 | opendj-server-legacy/pom.xml | 330 | Build |
| 3 | opends/build.xml | 266 | Build (legacy Ant) |
| 4 | opends/resource/schema/02-config.ldif | 251 | Schema |
| 5 | opends/resource/config/config.ldif | 210 | Config |
| 6 | .../core/DirectoryServer.java | 207 | Core server |
| 7 | opendj-rest2ldap-servlet/pom.xml | 203 | Build |
| 8 | .../replication/server/ReplicationServer.java | 180 | Replication |
| 9 | opendj-server/pom.xml | 179 | Build |
| 10 | .../replication/server/ReplicationServerDomain.java | 162 | Replication |

> OpenDJ shows more source code churn than other repos. DirectoryServer.java (207 changes) and replication classes are clear complexity hotspots.

**OpenIDM** (8,145 commits)

| Rank | File | Changes | Category |
|------|------|---------|----------|
| 1 | pom.xml | 563 | Build |
| 2 | openidm-zip/pom.xml | 294 | Build |
| 3 | .../managed/ManagedObjectSet.java | 219 | Core |
| 4 | .../locales/en/translation.json | 213 | UI/i18n |
| 5 | .../sync/impl/ObjectMapping.java | 203 | Sync engine |
| 6 | .../openicf/impl/OpenICFProvisionerService.java | 189 | Provisioning |
| 7 | src/main/docbkx/.../chap-samples.xml | 187 | Docs |
| 8 | src/main/docbkx/.../chap-synchronization.xml | 169 | Docs |
| 9 | openidm-zip/src/main/assembly/zip.xml | 162 | Packaging |
| 10 | .../audit/impl/AuditServiceImpl.java | 133 | Audit |

> OpenIDM hotspots are its core domain classes: ManagedObjectSet, ObjectMapping, and OpenICFProvisionerService -- the three pillars of identity lifecycle management.

**OpenIG** (1,995 commits)

| Rank | File | Changes | Category |
|------|------|---------|----------|
| 1 | pom.xml | 298 | Build |
| 2 | openig-core/pom.xml | 166 | Build |
| 3 | openig-war/pom.xml | 120 | Build |
| 4 | .../oauth2/client/OAuth2ClientFilter.java | 114 | OAuth2 |
| 5 | openig-saml/pom.xml | 88 | Build |
| 6 | openig-doc/pom.xml | 87 | Build |
| 7 | openig-oauth2/pom.xml | 81 | Build |
| 8 | .../GroovyScriptableFilterTest.java | 71 | Test |
| 9 | openig-uma/pom.xml | 70 | Build |
| 10 | .../handler/router/RouterHandler.java | 58 | Core |

> OAuth2ClientFilter (114 changes) is the clear complexity hotspot in OpenIG.

**OpenICF** (1,637 commits)

| Rank | File | Changes | Category |
|------|------|---------|----------|
| 1 | OpenICF-java-framework/pom.xml | 133 | Build |
| 2 | OpenICF-csvfile-connector/pom.xml | 90 | Build |
| 3 | OpenICF-groovy-connector/pom.xml | 89 | Build |
| 4 | .../bundles-parent/pom.xml | 82 | Build |
| 5 | OpenICF-ldap-connector/pom.xml | 71 | Build |
| 6 | .../connector-framework-internal/pom.xml | 70 | Build |
| 7 | .../openicf-zip/pom.xml | 64 | Build |
| 8 | .../connector-framework/pom.xml | 62 | Build |
| 9 | .../connector-framework-server/pom.xml | 62 | Build |
| 10 | .../connector_build.xml | 62 | Build (legacy Ant) |

**openam-community-edition** (4,121 commits)

| Rank | File | Changes | Category |
|------|------|---------|----------|
| 1 | pom.xml | 320 | Build |
| 2 | .../chap-rest.xml | 120 | Docs |
| 3 | .../chap-auth-services.xml | 95 | Docs |
| 4 | openam-server-only/pom.xml | 85 | Build |
| 5 | .../IdentityResource.java | 84 | REST API |

> CE hotspots include significant documentation churn -- ForgeRock invested heavily in docs during the 11.x era.

---

### Security Commit Analysis

#### CVE mentions per repo

| Repo | CVE Commits | Security Keyword Commits | Notable CVEs |
|------|------------|-------------------------|--------------|
| **OpenAM** | 55 | 34 | CVE-2021-35464 (RCE), CVE-2021-29156 (LDAP injection), CVE-2022-42889 (Commons Text RCE) |
| **OpenIG** | 20 | 3 | CVE-2020-13936 (Velocity sandbox bypass), CVE-2024-8184 (Jetty DoS) |
| **OpenIDM** | 17 | 77 | CVE-2023-22102 (MySQL connector), CVE-2025-25247 (Felix XSS) |
| **OpenDJ** | 10 | 153 | CVE-2025-27497 (alias loop DoS), CVE-2026-1225 (Logback RCE) |
| **OpenICF** | 9 | 1 | CVE-2016-6814 (Groovy deserialization), CVE-2020-13936 (Velocity) |
| **wrenam** | 9 | 18 | CVE-2021-35464 (RCE), CVE-2021-37154, CVE-2022-24670, CVE-2018-0696 |
| **CE** | 1 | 17 | (minimal -- frozen before CVE era) |

#### Security observations

1. **OpenAM has the highest CVE density** -- 55 CVE-referencing commits. As the authentication/authorization server, it has the largest attack surface and the most dependency exposure (jQuery, lodash, Netty, Commons libraries).

2. **OIP CVE remediation pattern**: Most CVE fixes follow a consistent pattern -- dependency bump commits with CVE IDs in the message. This started accelerating in 2022 and continues into 2026.

3. **wrenam structured CVE program**: The Orchitech team systematically addressed CVEs through dedicated PRs (#123-#130), each targeting a specific vulnerability. More organized than OIP approach.

4. **OpenDJ has 153 security keyword commits** despite only 10 CVE references -- many relate to TLS/SSL implementation, LDAP security mechanisms, and access control features (not vulnerability fixes).

5. **Critical CVEs shared across forks**: CVE-2021-35464 (ForgeRock AM RCE, actively exploited in the wild) was patched by both OIP OpenAM and wrenam independently.

6. **CVE-2025-27497 (alias loop DoS)** appears across OpenAM, OpenDJ, OpenIDM, OpenIG, and OpenICF -- indicating a coordinated multi-repo fix by OIP.

---

### Keyword Mining

| Keyword | OpenAM | OpenDJ | OpenIDM | OpenIG | OpenICF | CE | wrenam |
|---------|--------|--------|---------|--------|---------|-----|--------|
| **fix** | 753 | 3,287 | 659 | 133 | 124 | 430 | 669 |
| **feat** | 58 | 168 | 46 | 11 | 6 | 47 | 51 |
| **security** | 34 | 153 | 77 | 3 | 1 | 17 | 18 |
| **CVE** | 55 | 10 | 17 | 20 | 9 | 1 | 9 |
| **deprecat** | 33 | 38 | 14 | 17 | 3 | 16 | 30 |
| **upgrade** | 172 | 460 | 47 | 4 | 4 | 70 | 185 |
| **migration** | 25 | 64 | 22 | 5 | 7 | 4 | 24 |

#### Keyword analysis

- **Fix-to-feat ratio** reveals project maturity: OpenDJ has 19.6:1 (fix:feat), indicating a mature codebase in maintenance mode. OpenAM is 13:1. OpenIG at 12:1 is relatively more balanced.

- **OpenDJ dominates upgrade and fix** with 460 and 3,287 respectively -- reflecting its age and the massive ongoing effort to keep a 20-year-old codebase current.

- **security keyword is heavily concentrated in OpenDJ (153) and OpenIDM (77)** -- OpenDJ because it implements security protocols (TLS, SASL, access controls) as core functionality, OpenIDM because identity provisioning inherently involves security contexts.

- **deprecat counts are relatively low across all repos** (3-38), suggesting conservative API evolution rather than aggressive deprecation cycles.

- **wrenam has disproportionately high upgrade (185)** relative to its post-fork commit count, reflecting Wren Security focus on modernizing dependencies.

---

### Cross-Repo Insights

#### Periods of High/Low Activity

```
HIGH ACTIVITY PERIODS:
  2007         OpenDJ peak (4,696 commits) - OpenDS initial development sprint
  2013-2015    All-repos peak - ForgeRock open-source golden era
  2014         Combined peak (10,744 commits) - 5 repos active simultaneously

LOW ACTIVITY PERIODS:
  2017         Combined trough (401 commits) - Post-closure shock
  2020-2021    Pandemic slowdown + small community (~250 commits/year)

RECOVERY PERIODS:
  2018         OIP bootstrapping - rapid release cadence for OpenAM/OpenDJ
  2022-2023    wrenam revival + OIP steady state
  2024         OpenIDM/OpenICF revived after multi-year hiatus
```

#### Correlation with ForgeRock Closure (Nov 2016)

The data makes the impact of ForgeRock source-code closure unmistakably clear:

| Metric | 2016 | 2017 | Change |
|--------|------|------|--------|
| Combined commits | 6,631 | 401 | **-94%** |
| Active repos | 7 | 3 | **-57%** |
| OpenAM commits | 1,816 | 226 | **-88%** |
| OpenDJ commits | 1,148 | 66 | **-94%** |
| OpenIDM commits | 1,218 | 0 | **-100%** |

**Pre-closure (2016)**: ForgeRock last open tags were OpenAM 14.0.0-M2 (Oct 2016), OpenDJ 4.0.0-M1 (Sep 2016), and the final forgerock/master tag on wrenam (Nov 2016).

**Post-closure gap**: 14-16 months of near-silence before OIP first releases in Feb-Mar 2018.

**Fork divergence**: OIP picked up from ForgeRock last open commit and continued forward. Wren Security took a different approach, investing in build modernization and dependency upgrades before resuming feature work.

#### Fork Divergence Points

```
ForgeRock OpenAM history (2012-2016):
  ~8,096 shared commits (762+1346+1966+2206+1816)

  +-- OIP OpenAM (2017+): +1,489 post-fork commits
  |   Focus: continuous releases, CVE fixes, dependency updates
  |   Style: small incremental patches, maven-release-plugin driven
  |
  +-- wrenam (2017+): +426 post-fork commits
  |   Focus: build modernization, structured CVE remediation, Wren:DS migration
  |   Style: PR-based workflow, milestone releases
  |
  +-- CE (2017): +5 post-fork commits (frozen)
      Focus: community patches only, no active development
```

#### Cross-Repo Dependency Patterns

OIP coordinates releases across repos. Evidence from tag dates:

| Release Wave | OpenAM | OpenDJ | OpenIDM | OpenIG | OpenICF |
|-------------|--------|--------|---------|--------|---------|
| 2024-Sep | 15.1.0 | 4.8.0 | 6.2.0 | 5.3.0 | 1.7.0 |
| 2025-Jul | 15.2.0 | 4.10.0 | 6.3.0 | 5.4.0 | 1.8.0 |
| 2025-Nov | 16.0.3 | 5.0.1 | 7.0.1 | 6.0.1 | 2.0.1 |
| 2026-Feb | 16.0.5 | 5.0.3 | 7.0.2 | 6.0.2 | 2.0.2 |

All 5 OIP repos release within days of each other, confirming coordinated release management. The Nov 2025 wave was a major version bump across the entire suite.

#### File Churn Patterns

- **pom.xml dominance**: Root pom.xml is #1 in all 7 repos. For OpenAM, the top 30 are ALL pom.xml files. This is a clear signal that dependency management is the primary maintenance burden for these aging Java codebases.

- **Schema/config files in OpenDJ**: 02-config.ldif (251 changes) and config.ldif (210 changes) reflect the evolving LDAP schema -- every new feature or attribute requires schema updates.

- **Core domain classes as hotspots**: OpenIDM ManagedObjectSet.java (219 changes), ObjectMapping.java (203), and OpenDJ DirectoryServer.java (207) are the God-class risk areas that warrant refactoring attention.

- **Test file churn is notably low**: Very few test files appear in the top-30 for any repo, suggesting either stable tests or insufficient test coverage evolution.

---

### Appendix: Raw Release Tag Counts

| Repo | Total Tags | First Release | Latest Release |
|------|-----------|---------------|----------------|
| OpenDJ | 82 | sdk/2.6.0 (2013-06) | 5.0.3 (2026-02) |
| OpenAM | 81 | 11.0.0 (2013-11) | 16.0.5 (2026-02) |
| OpenIG | 25 | 5.0.0 (2018-03) | 6.0.2 (2026-02) |
| OpenIDM | 24 | 2.0.2-docs (2012-02) | 7.0.2 (2026-02) |
| wrenam | 24 | forgerock/11.0.0 (2013-11) | 16.0.0-M1 (2025-09) |
| OpenICF | 13 | 1.5.0 (2018-04) | 2.0.2 (2026-02) |
| CE | 2 | sustaining/11.0.3 (2015-03) | ce/11.0.3 (2017-04) |
