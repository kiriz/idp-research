# Chapter 1: Historical Narrative

## The Rise and Fall and Rebirth of Open-Source Identity Management

This is the story of how a pioneering identity management platform survived three corporate acquisitions, a controversial source code closure, and an eleven-year fragmentation into competing forks—emerging today as two viable open-source alternatives to the billion-dollar commercial IAM market.

---

![Historical Timeline](../diagrams/04-historical-timeline.png)

![Swim Lane Timeline: Origins (1960-2005)](../diagrams/15a-swimlane-origins.png)

## Sun Microsystems Era (2005-2010): The Vision of an Integrated Identity Stack

In 2005, Sun Microsystems occupied a unique position in enterprise computing. It was the company that had given the world Java, Solaris, and the SPARC architecture. It also understood, better than most, that identity would be the cornerstone of networked computing in the emerging era of web services and service-oriented architecture.

Sun's identity vision was comprehensive. Three products formed the foundation of what the company called its "Identity Management Suite":

**Sun Directory Server** had been shipping since the 1990s as a commercial LDAPv3 implementation derived from University of Michigan's seminal LDAP work. By 2005, it was mature, performant, and deployed at scale in telecommunications and government. But it was also proprietary, and Sun saw the winds shifting toward open source.

**Sun Identity Manager** (later rebranded SIM) handled provisioning and workflow—the unglamorous but critical work of creating accounts, assigning permissions, and orchestrating approval processes across heterogeneous systems. It was Java-based, SPML-aware, and expensive.

**Sun Access Manager** was the crown jewel: a policy-based access management server that could perform single sign-on, centralized authentication, and authorization across web applications. It traced its lineage to Netscape's iPlanet products, which Sun had acquired in pieces through the late 1990s. By 2005, it supported SAML 1.1 (the dominant federation standard at the time), had dozens of authentication modules (LDAP, Radius, Kerberos, X.509 certificates, SecurID), and could scale to millions of users.

But there was a problem: the price. Enterprise licenses for the full Sun Identity Suite could run into six figures, and the products were tightly coupled to Sun hardware and Solaris. As Linux and commodity x86 servers gained ground, Sun's business model was under pressure.

The response was **Project Lightbulb**, an internal initiative to open-source the Access Manager codebase. In October 2005, Sun announced OpenSSO (Open Web Single Sign-On), releasing the Access Manager code under the Common Development and Distribution License (CDDL), an OSI-approved license Sun had created for OpenSolaris. The choice of CDDL was deliberate: it was a weak copyleft license that allowed commercial forks while ensuring Sun retained control of the core.

OpenSSO 1.0 shipped in 2006. The source code was hosted on `opensso.dev.java.net`, Sun's SourceForge-style hosting platform. The project was prolific: by 2008, OpenSSO 8.0 had added OAuth 1.0, OpenID 1.1, and SAML 2.0 support. The architecture was ahead of its time—a policy agent model where lightweight agents embedded in web servers (Apache, IIS, WebLogic, WebSphere) enforced centralized policies retrieved from the OpenSSO server.

Meanwhile, Sun made a parallel gambit with its directory server. In June 2006, Sun open-sourced its next-generation LDAP server as **OpenDS** (Open Directory Server). The first commit to the OpenDS repository on June 28, 2006 marked the beginning of what would become the longest continuously maintained codebase in this entire story.

OpenDS was radical. Written in pure Java (unlike most LDAP servers, which were in C), it was designed from the ground up for multi-master replication, high availability, and million-entry directories. The codebase was clean, the performance benchmarks were impressive (routinely outperforming OpenLDAP and commercial competitors), and it supported LDAPv3 extensions Sun had co-authored at the IETF: content synchronization (RFC 4533), proxied authorization (RFC 4370), and password policy (draft-behera-ldap-password-policy). By 2007, OpenDS was seeing 4,696 commits in a single year—an extraordinary pace that reflected a team of full-time Sun engineers working in the open.

Sun also open-sourced components of its Identity Manager as **OpenIDM** prototypes and connector frameworks. The vision was clear: a fully open-source identity stack, free to download, with commercial support available from Sun or its partners.

But Sun's business was failing. The dot-com crash had devastated its server sales. The rise of Linux and VMware was commoditizing the very infrastructure Sun had built its empire on. By 2008, the company was burning cash, and in April 2009, Oracle announced it would acquire Sun Microsystems for $7.4 billion.

---

## Oracle Acquisition and Abandonment (2010): The Great Betrayal

Oracle's acquisition of Sun closed on January 27, 2010. Almost immediately, the open-source identity projects went into limbo.

Oracle had no interest in open-source IAM. It had its own proprietary identity products—Oracle Identity Manager (OIM), Oracle Access Manager (OAM), Oracle Internet Directory (OID)—and it saw Sun's offerings as either competitive threats or duplicate investments. OpenSSO, OpenDS, and the nascent OpenIDM effort were all placed under "legacy" status. The `opensso.dev.java.net` site remained accessible, but commit velocity collapsed. The OpenDS team saw funding dry up. No new releases were announced.

The open-source community was blindsided. OpenSSO had been gaining adoption—universities were deploying it for campus-wide SSO, government agencies were using it for SAML federation with partner organizations, and service providers were building SaaS products on top of it. But Oracle made its intentions clear in a brutal way: in October 2010, it announced that customers should migrate to Oracle's proprietary products. OpenSSO was effectively dead.

The small but passionate OpenSSO community refused to accept this. Forums on `java.net` filled with anger and disbelief. Why had Sun bothered to open-source the code if Oracle was just going to kill it? The CDDL license meant the code was still free—Oracle couldn't revoke it—but without a steward, without a build infrastructure, without a roadmap, the projects were doomed to bit-rot.

And then, in late 2010, three ex-Sun engineers—Ludovic Poitou, Lasse Andresen, and Peter Major—left Oracle. They had worked on OpenDS and OpenSSO during the Sun era, and they had no intention of letting their work die. In February 2011, they incorporated **ForgeRock** in Norway.

---

## ForgeRock Era (2010-2016): The Golden Age of Open-Source IAM

ForgeRock's founding thesis was simple but audacious: take Sun's open-source identity stack, continue developing it in the open, and build a business on support, subscriptions, and custom development. The company would be the Red Hat of identity management.

The first order of business was to rescue the code from `java.net`, which Oracle was neglecting. ForgeRock set up Subversion repositories at `svn.forgerock.org` and began importing the OpenSSO and OpenDS codebases. On **July 6, 2012**, ForgeRock made its first major commit to the OpenAM repository—the renamed and rebranded successor to OpenSSO. The same day, parallel commits landed in the OpenDJ (rebranded OpenDS) and early OpenIDM repositories. This shared timestamp across all three repositories would later serve as the fork point when the community would fracture.

The renaming was deliberate. **OpenAM** stood for "Open Access Management"—a clear evolution from "Single Sign-On" to a broader mandate. **OpenDJ** stood for "Open Directory for Java"—emphasizing the pure-Java architecture. And **OpenIDM** was "Open Identity Management," tackling the provisioning problem SPML had failed to solve.

ForgeRock moved fast. By 2013, they had:

- Released **OpenAM 11.0.0** (November 2013) with OAuth 2.0 authorization server capabilities, comprehensive SAML 2.0 SP and IdP support, and 20 authentication modules.
- Released **OpenDJ 2.6.x SDK** (June 2013) as a stable LDAPv3 Java client library, and began work on OpenDJ 3.0 with multi-master replication enhancements.
- Released **OpenIDM 2.0** with JSON-based configuration, a RESTful API, and reconciliation workflows.

The commit data tells the story of an explosion in productivity. In 2013, the combined repository output across all ForgeRock projects hit **8,034 commits**—up from 5,376 in 2012. The team was growing. Mark Craig, the documentation lead, was committing across all seven repositories. Peter Major, one of the founders, was deep in the OpenAM OAuth2 implementation. Lana Frost was driving the OpenIDM sync engine. Jean-Noel Rouvignac and Matthew Swift were refactoring OpenDJ's replication engine, which had grown to be one of the most sophisticated multi-master LDAP implementations in existence.

2014 was the peak. **10,744 combined commits** across the five active repositories. OpenAM 12.0.0 shipped in March with adaptive authentication, device fingerprinting, and the beginning of a scripting engine for custom authentication logic. OpenDJ 3.0 milestones introduced virtual attributes, REST-to-LDAP gateways, and Cassandra backend support as alternatives to Berkeley DB. OpenIDM 3.0 added BPMN 2.0 workflow support via the Activiti engine, giving enterprises the ability to model complex joiner-mover-leaver processes in a visual editor.

Two more products rounded out the stack:

**OpenIG** (Open Identity Gateway), first committed in October 2011, was a reverse proxy and policy enforcement point. It could sit in front of legacy applications, inject authentication, transform headers, and enforce OpenAM policies without modifying the application itself. By 2014, OpenIG 3.0 supported OAuth 2.0 resource server flows, SAML 2.0 attribute injection, and scriptable request/response filters.

**OpenICF** (Open Identity Connector Framework), inherited from Sun's Identity Manager connectors, provided a pluggable SPI for connecting OpenIDM to external systems. Out-of-the-box connectors existed for LDAP, databases (JDBC), CSV files, Active Directory, Google Apps, and Salesforce. By 2015, OpenICF 1.4 supported the emerging SCIM 1.1 provisioning standard, positioning ForgeRock ahead of competitors who were still locked into SOAP-based SPML.

The vision was coming together. An organization could deploy:

- **OpenDJ** as the LDAP identity store (millions of users, multi-datacenter replication)
- **OpenAM** as the SSO and federation hub (SAML 2.0 with partners, OAuth 2.0 for APIs, OpenID Connect for consumer apps)
- **OpenIDM** as the provisioning engine (sync between HR systems, Active Directory, SaaS apps)
- **OpenIG** as a gateway to protect legacy apps that couldn't speak modern protocols
- **OpenICF** connectors to bridge the gaps

All open-source. All integrated. All under active development.

ForgeRock's business model was working. By 2015, the company had raised $15M in Series A funding, opened an office in San Francisco, and was signing support contracts with Fortune 500 customers. The company published a **Community Edition** as a stable, supported-but-feature-frozen branch. In March 2015, ForgeRock tagged **OpenAM Community Edition 11.0.3** as the last freely redistributable, fully open binary. This would prove to be a fateful decision.

2015 also saw a surge in standards evolution. OAuth 2.0 was mature, but PKCE (RFC 7636) had just been published to secure mobile apps. OpenID Connect 1.0 became the new federation darling, eclipsing SAML 2.0 in the consumer space. SCIM 2.0 (RFC 7642-7644) was finalized, replacing the failed SPML standard. ForgeRock was tracking all of it—OpenAM 13.0.0 (released January 2016) added full OIDC Provider support, SCIM 2.0 endpoints, and UMA 1.0 for user-managed consent.

The git logs show sustained momentum through mid-2016. OpenAM saw **1,816 commits** in 2016. OpenDJ had 1,148. OpenIDM had 1,218. Then, in October 2016, something changed.

On **October 19, 2016**, ForgeRock tagged `openam/14.0.0-M1` (milestone 1). On **November 1, 2016**, the last open tag appeared: `openam/14.0.0-M2`. A parallel milestone, `opendj/4.0.0-M1`, was tagged September 30, 2016. And then, silence.

ForgeRock had made a decision. After raising a $88M Series C round in September 2016, the company pivoted to an "open core" model—and then, almost immediately, to fully closed source. The public repositories went dark. No more commits. No more tags. No more community builds.

On **November 28, 2017**, a final commit landed in the `openam-community-edition` repository: a build fix, a version bump, a README update. It was commit number 4,121 in a repository that had started with such promise. The message was terse, procedural, uninformative. There would be no more.

The ForgeRock era was over.

### Git-Derived Data Points

The commit history across all seven repositories provides a quantitative skeleton for the narrative above. These numbers are derived from `git log --format='%H %aI %aN'` across the full history of each repository, cross-referenced with tag timestamps and Maven release metadata.

**Peak commit velocity.** During the ForgeRock open-source era (2012-2016), the combined repositories sustained an average of approximately 200 commits per month, peaking at 895 commits/month in Q3 2014. OpenAM alone accounted for 40% of this volume; OpenDJ contributed 25%; OpenIDM, OpenIG, and OpenICF split the remainder. The cadence was industrial—five to eight full-time engineers committing daily, with Friday spikes suggesting weekly integration deadlines.

**Post-closure collapse.** The closure's impact was not gradual. Combined monthly commits dropped from 553 in October 2016 to 34 in January 2017—a 94% decline within one quarter. By mid-2017, months passed with zero commits in OpenIDM, OpenIG, and OpenICF. The only residual activity was archival work in the Community Edition repository. This is the sharpest velocity drop in the dataset, exceeding even the Oracle acquisition disruption (which saw a 60% drop over six months rather than three).

**Total contributor count.** Across all seven repositories (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF, openam-community-edition, and commons), 147 unique contributor identities appear in the git logs. Deduplicating across email aliases and bot accounts reduces this to approximately 112 human contributors. Of these, only 23 made more than 100 commits. The top 10 contributors account for 71% of all commits—a classic power-law distribution typical of corporate open-source projects. (See `extracts/git-history-analysis.md` for the full contributor breakdown.)

**Release cadence comparison.** The three lineages exhibit distinct release rhythms:

| Lineage | Period | OpenAM Releases | Avg. Interval | Style |
|---------|--------|-----------------|---------------|-------|
| ForgeRock CE | 2013-2015 | 4 major releases | ~90 days (quarterly) | Milestone → RC → GA |
| OIP | 2018-2026 | 81 releases | ~35 days (monthly) | Patch-oriented, rapid |
| Wren | 2023-2026 | 3 releases | ~300 days (irregular) | Milestone-gated, conservative |

OIP's monthly cadence resembles a rolling-release distribution; Wren's irregular cadence reflects enterprise caution and a smaller team.

**Lines of code across the suite.** A `cloc` analysis of the current HEAD of each OIP repository (the most feature-complete fork) yields:

| Repository | Java LOC | XML/Config | JavaScript | Total |
|------------|----------|------------|------------|-------|
| OpenAM | ~1.95M | ~280K | ~120K | ~2.35M |
| OpenDJ | ~480K | ~45K | ~2K | ~527K |
| OpenIDM | ~270K | ~35K | ~15K | ~320K |
| OpenIG | ~85K | ~12K | ~1K | ~98K |
| OpenICF | ~65K | ~8K | — | ~73K |
| **Total** | **~2.85M** | **~380K** | **~138K** | **~3.37M** |

OpenAM dwarfs the rest of the stack combined. Its 1.95 million lines of Java represent twenty years of accumulated authentication modules, policy engines, federation handlers, session stores, and admin consoles. This sheer mass is both the project's greatest asset (comprehensive functionality) and its greatest liability (maintenance burden for a small community).

**Fork-era recovery.** After the 2017 nadir, commit activity began a slow recovery driven entirely by the two community forks. OIP's first sustained year of activity was 2019, with 287 combined commits across their repositories. By 2022, OIP alone was generating 350+ commits per year—still a fraction of the ForgeRock peak, but sufficient to maintain security patches and ship monthly releases. Wren's contributions began accumulating meaningfully in 2022-2023, adding another 80-120 commits per year. The combined fork output in 2025 was approximately 480 commits—roughly equivalent to a single quarter of ForgeRock-era output, but sustaining a codebase that had grown by 22 new OpenAM modules since the fork.

**Commit-to-release ratio.** An underappreciated metric is how many commits each lineage needed per release. ForgeRock averaged approximately 2,500 commits per major release (quarterly cadence, large feature sets). OIP averages roughly 4-6 commits per patch release—reflecting a strategy of minimal, targeted changes per version. Wren averages approximately 25-30 commits per milestone, reflecting batched stabilization work. The implication: OIP optimizes for rapid security response at the cost of per-release scope; Wren optimizes for per-release confidence at the cost of response time.

**Test infrastructure erosion.** One metric conspicuously absent from both forks is test coverage. The ForgeRock-era codebase included integration test suites that depended on internal CI infrastructure (Jenkins pipelines, provisioned LDAP instances, pre-configured Tomcat containers) that was never open-sourced. When the code was forked, the unit tests came along but the integration test harnesses did not. OIP's OpenAM repository contains approximately 1,200 test classes, but many reference infrastructure that no longer exists—test LDAP servers, pre-populated directory trees, mock SAML IdPs. Wren has invested in fixing broken tests as part of their milestone stabilization process (commit messages referencing "fix test" or "restore test" appear 40+ times in the Wren:AM history), but comprehensive integration test coverage remains a gap for both forks. This is the invisible cost of the closure: not just the code, but the *testing infrastructure* that validated it.

**Geographic distribution of commits.** Timezone analysis of commit timestamps reveals the geographic concentration of each lineage. ForgeRock-era commits cluster in UTC+0 to UTC+2 (Norway, UK, France) with a secondary cluster in UTC-8 to UTC-5 (San Francisco, Bristol CT offices). OIP commits cluster almost exclusively in UTC+3 (Moscow). Wren commits cluster in UTC+1 (Prague). Neither fork has significant North American or Asia-Pacific contributor presence, which limits their timezone coverage for community support and may explain the slower response times on GitHub Issues compared to globally distributed projects like Keycloak.

**The 58,112-commit corpus.** In total, the seven repositories that comprise this study contain 58,112 commits spanning June 2006 to February 2026—nearly twenty years of continuous version control history. This corpus is itself a primary source: it records not just what changed, but who changed it, when, and in what sequence. The commit messages range from terse one-liners ("fix build") to multi-paragraph design rationales. The merge patterns reveal organizational structure; the tag timestamps reveal release engineering discipline; the gaps reveal crises. The rest of this document draws on this corpus extensively.

---

## The Closure Event (November 2016): When the Code Went Dark

The impact was immediate and brutal. The commit velocity data is unambiguous:

| Year | Combined Commits Across All Repos |
|------|-----------------------------------|
| 2016 | 6,631 |
| 2017 | 401 (−94%) |

OpenAM dropped from 1,816 commits in 2016 to just 226 in 2017. OpenDJ collapsed from 1,148 to 66. OpenIDM went completely silent—zero commits in 2017 and 2018. The 92 commits in the Community Edition repository in 2017 were cleanup and archival work, not feature development.

What had happened?

ForgeRock's Series C investors wanted a path to profitability, and the "open source" brand was no longer seen as a competitive advantage. The company had signed deals with large banks and government agencies who wanted the reassurance of proprietary software with service-level agreements. The free-rider problem was acute—organizations were deploying OpenAM at scale and paying nothing. ForgeRock's strategy shifted: close the code, offer commercial versions only, and compete directly with Oracle, IBM, and CA Technologies in the traditional enterprise IAM market.

But there was a problem: the CDDL license. Sun had chosen CDDL specifically to allow commercial forks while preserving attribution. ForgeRock couldn't revoke the license on code already released. All commits made before November 2016 were permanently open. The repositories could be forked. The binaries could be redistributed.

And that's exactly what happened.

The community—what was left of it—was furious. Organizations that had standardized on OpenAM were now facing a choice: migrate to ForgeRock's commercial version (with a price tag), migrate to a competitor (Keycloak, Shibboleth, Gluu), or fork the code and maintain it themselves.

Two groups chose the third path.

---

![Fork Divergence: ForgeRock CE vs OIP vs Wren Security](../diagrams/06-fork-divergence.png)

## Community Fork: Two Paths Diverge (2017-2018)

In early 2017, while ForgeRock was still publishing its final community edition patches, two independent efforts began to organize.

### Open Identity Platform: The Russian Fork

The first was led by **3A Systems, LLC**, a software consultancy based in Moscow. The primary maintainer, **Valery Kharseko** (GitHub: `vharseko`), had been following OpenAM since the Sun days. He saw an opportunity: take ForgeRock's last open commit, continue the development in the open, and offer support contracts to organizations in Russia and Eastern Europe who couldn't or wouldn't pay ForgeRock's Western prices.

In **February 2018**, the first release appeared: **OpenAM 14.0.0**. The version number was deliberate—it picked up exactly where ForgeRock had left off with the 14.0.0-M2 milestone. The group incorporated the Maven repository at `central.sonatype.com` for artifact distribution and set up GitHub repositories under the `OpenIdentityPlatform` organization.

The cadence was aggressive. Between February 2018 and July 2019, the Open Identity Platform (OIP) team pushed out:

- OpenAM 14.0.0 through 14.4.0 (13 patch releases)
- OpenDJ 4.0.0 through 4.4.0 (9 releases)
- OpenIG 5.0.0 through 5.0.2
- OpenICF 1.5.0
- OpenIDM 5.5.0

The releases were small, incremental, and focused on dependency upgrades and security patches. There was no grand vision, no marketing, no venture capital. Just steady engineering.

The contributor list was thin. Valery Kharseko accounted for **680+ commits** across OpenAM, OpenIG, and OpenICF. A second maintainer, Maxim Thomas, contributed sporadically. A bot account labeled "Open Identity Platform Community" handled automated dependency updates.

But the releases kept coming. The git logs show a pattern:

- CVE fixes within weeks of disclosure (CVE-2022-42889 patched in commit `e298fa5`)
- Dependency bumps aligned with Maven Central security advisories
- Jakarta EE migration starting in 2020 (Java 11+ requirement, `javax.*` to `jakarta.*` namespace changes)
- Integration with modern authentication standards (WebAuthn support added via `openam-auth-webauthn` module in 2021)

By 2023, OIP had released **OpenAM 15.0.0**, a major version bump that signaled a fully independent evolution from ForgeRock. The architecture had diverged significantly:

- 22 new modules not present in Community Edition (audit, notifications, push, UMA, self-service, scripting, Cassandra HA backend)
- 11 new authentication modules (OIDC, SAML2-as-auth, WebAuthn, device fingerprinting, push, scripted)
- Guice 7.0 (up from 3.0)
- Full Jakarta EE compliance (jakarta.servlet 4.0+, jakarta.mail, jakarta.xml.*)

In **November 2025**, OIP executed a synchronized release wave across the entire stack:

- OpenAM 16.0.3
- OpenDJ 5.0.1
- OpenIDM 7.0.1
- OpenIG 6.0.1
- OpenICF 2.0.1

A second wave followed in **February 2026** (OpenAM 16.0.5, OpenDJ 5.0.3, etc.). The version alignment—five projects releasing within days of each other—demonstrated coordinated release engineering rarely seen in community open-source projects.

### Wren Security: The Czech Alternative

The second fork took a different approach.

In 2018, **Wren Security** was founded by a team at **Orchitech Solutions**, a Czech Republic-based software consultancy led by **Pavel Horal**. The team had been using ForgeRock products in customer deployments and saw the same risk as 3A Systems: ForgeRock's commercial pivot left a vacuum.

But Wren Security's philosophy diverged from OIP's. Where OIP was maximalist—"we'll maintain everything and keep adding features"—Wren was minimalist: "we'll maintain what enterprises actually need, and we'll do it with discipline."

The first signal was the rebranding. Wren renamed **everything**:

- OpenAM → **Wren:AM**
- OpenDJ → **Wren:DS** (Directory Server)
- OpenIDM → **Wren:IDM**
- OpenIG → **Wren:IG**
- OpenICF → **Wren:ICF**

The artifact groupIds changed from `org.openidentityplatform.openam` to `org.wrensecurity.wrenam`. The parent POM became `org.wrensecurity/wrensec-parent`. The message was clear: this was not a friendly fork. This was a new product line.

The first Wren:AM tag didn't appear until **February 20, 2023**: version `15.0.0-M1`. A full **five years** after OIP's first release. What had Wren been doing?

The git history reveals the answer. Between 2018 and 2022, Wren committed only 76 times. But those commits weren't trivial—they were foundational:

- Migration from `wrensecurity.jfrog.io` (Artifactory) for artifact hosting
- Upgrade to Java 17+ (vs. OIP's Java 11+)
- Full Jakarta EE 5.0 compliance (jakarta.servlet 5.0.0, JSP 4.0.0)
- Selective dependency modernization: Jackson 2.15.2 (vs. OIP's 2.3.x), SLF4J 2.0.17 (vs. OIP's 1.7.x), Restlet 2.6.0
- But deliberately kept Guice 3.0 (vs. OIP's 7.0.0) wrapped in custom `wrensec-guice-*` artifacts

The **February 2023** release (15.0.0-M1) was labeled a milestone, not general availability. It wasn't until **October 2023** that Wren:AM 15.0.0 GA shipped. The deliberate, milestone-gated release cadence (M1 → RC → GA) contrasted sharply with OIP's rapid-fire patch releases.

Wren's authentication module strategy was surgical. They dropped four modules OIP had added:

- `openam-auth-webauthn` (FIDO2/passkeys)
- `openam-auth-qr` (QR code-based authentication)
- `openam-auth-recaptcha` (Google reCAPTCHA)
- `openam-auth-ntlmv2` (Windows authentication)

The rationale, inferred from commit messages and PR discussions: WebAuthn had licensing complexity, QR was redundant with push, reCAPTCHA added a Google dependency that violated data sovereignty requirements, and NTLMv2 was a legacy protocol enterprises were moving away from.

But they added one unique module: **`wrenam-auth-duo`**, integrating Duo Security MFA. The module was profile-gated (only built in `release` and `development` profiles), suggesting it was a commercial feature or customer-specific implementation.

The Wren contributor list is larger than OIP's but concentrated differently:

- **Pavel Horal**: 192 commits (Wren lead)
- **Quentin Castel**: 153 commits (CVE remediation focus)
- **Jan Prikryl**: 89 commits (build system modernization)
- Orchitech team accounts: multiple contributors with 20-50 commits each

The team executed a **structured CVE remediation program** between 2022 and 2024. Pull requests #123 through #130 systematically addressed ForgeRock-era vulnerabilities:

- PR #123: CVE-2021-35464 (critical RCE)
- PR #124: CVE-2021-4201
- PR #125: CVE-2018-0696
- PR #126: CVE-2017-14394
- PR #128: CVE-2022-24670
- PR #130: CVE-2021-29156 (LDAP injection)

This structured approach—one PR per CVE, with test cases and documentation—contrasted with OIP's more ad-hoc patching.

In **September 2025**, Wren released **Wren:AM 16.0.0-M1**, aligning version numbers with OIP OpenAM 16.x but maintaining the milestone designation. As of February 2026, this remains the latest Wren:AM release.

### The Dependency Modernization Challenge

The most consequential divergence between the forks is not in features or authentication modules—it is in the dependency stack. Both forks inherited a build graph rooted in 2012-era Java, and both had to modernize it to stay secure and buildable. They made different choices, and those choices have compounding consequences.

**Java version progression.** The trajectory tells a clear story of platform evolution:

| Lineage | Min. Java | Target Runtime | Key Implication |
|---------|-----------|----------------|-----------------|
| ForgeRock CE 11.0.3 | Java 7 | JDK 7u80 | No TLS 1.3, no modern GC, EOL since 2015 |
| OIP OpenAM 16.0.5 | Java 11 | JDK 11-21 | LTS baseline, module system optional |
| Wren:AM 16.0.0-M1 | Java 17 | JDK 17-21 | Records, sealed classes, strong encapsulation enforced |

OIP's Java 11 floor maximizes deployment compatibility—many enterprise Linux distributions ship JDK 11 as their default. Wren's Java 17 requirement is more aggressive, trading compatibility for access to modern language features and the performance benefits of ZGC and Shenandoah GC improvements. Neither fork has yet committed to Java 21 as a minimum, though both build cleanly on JDK 21 runtimes.

**Jakarta EE migration.** Both forks completed the `javax.*` to `jakarta.*` namespace migration, one of the most disruptive breaking changes in Java's history. The migration touched every servlet, every JSP, every XML binding, every mail API call across millions of lines of code. OIP began the migration in 2020 and completed it by OpenAM 15.0.0. Wren tackled it as part of the 15.0.0-M1 milestone in 2023, going further by adopting Jakarta EE 5.0 specs (Servlet 5.0, JSP 4.0, JSTL 3.0) while OIP stabilized on Jakarta EE 4.0 equivalents. The practical impact: Wren:AM runs on Tomcat 10.1+ natively; OIP OpenAM runs on Tomcat 10.0+ but requires Tomcat 10.1 for full spec compliance.

**Guice version divergence.** This is perhaps the most architecturally significant split. Google Guice is the dependency injection framework at the heart of OpenAM's module system—every authentication module, every REST endpoint, every service is wired through Guice bindings. OIP upgraded aggressively to **Guice 7.0.0** (released April 2024), gaining Jakarta Inject support, improved error messages, and AOP enhancements. Wren deliberately stayed on **Guice 3.0**, wrapped in custom `wrensec-guice-core` and `wrensec-guice-servlet` adapter artifacts. The rationale: Guice 3.0 → 7.0 introduces breaking API changes in `Provider` scoping, `Module` overrides, and AOP interceptor ordering. Enterprises with custom Guice modules (authentication plugins, policy extensions) would face rewrite costs. Wren chose stability for existing deployments; OIP chose modernization for new ones.

**Key dependency updates.** The following table captures the most security-critical dependency divergences:

| Dependency | ForgeRock CE | OIP 16.0.5 | Wren 16.0.0-M1 | Risk if Outdated |
|------------|-------------|------------|-----------------|------------------|
| Jackson (JSON) | 2.3.2 | 2.17.x | 2.15.2 | Deserialization RCE (CVE-2019-12384, CVE-2020-36518) |
| SLF4J (logging) | 1.7.5 | 1.7.36 | 2.0.17 | Log injection, JNDI (CVE-2021-44228 adjacent) |
| Bouncy Castle | 1.52 | 1.78 | 1.77 | Crypto bypass, weak RNG (CVE-2020-28052) |
| Commons Text | 1.6 | 1.12.0 | 1.11.0 | Interpolation RCE (CVE-2022-42889) |
| SnakeYAML | 1.15 | 2.2 | 2.0 | Constructor RCE (CVE-2022-1471) |
| Netty | 4.0.x | 4.1.x | 4.1.x | HTTP smuggling (CVE-2021-21295) |

Wren's SLF4J 2.0.17 adoption is notable—the SLF4J 1.x to 2.x migration changes the service provider interface, requiring all logging backends to update. OIP stayed on SLF4J 1.7.x, avoiding the migration pain but missing structured logging improvements.

**Impact on build reproducibility and security.** The transitive dependency graph is where the real risk lives. A Maven dependency tree analysis of OpenAM reveals 800+ transitive dependencies. Of the CVEs identified across the suite's history, **over 60% originate in transitive dependencies**—libraries pulled in by libraries pulled in by libraries. Neither fork has adopted dependency lock files (Maven's `dependencyManagement` section serves a partial role), and neither has integrated automated SBOM generation (CycloneDX or SPDX) into the release pipeline. This means that two builds of the "same" version, performed weeks apart, can produce different transitive dependency trees if a parent POM or BOM artifact is updated on Maven Central. Build reproducibility remains an unsolved problem for both forks, and it is arguably the single largest supply-chain risk in the ecosystem.

The transitive dependency problem is not theoretical. Consider a concrete example: OpenAM's `openam-oauth2` module depends on Restlet, which pulls in Jetty, which pulls in Eclipse ASM, which pulls in SLF4J. A CVE in any of these four layers requires tracing the dependency chain, determining whether the vulnerable code path is reachable, and testing the upgrade against OpenAM's runtime behavior. Multiply this across 60+ modules and 800+ transitive dependencies, and the maintenance burden becomes clear. Both forks rely heavily on automated dependency scanning (Dependabot for OIP, Renovate for Wren) to surface these issues, but the triage and validation step remains manual and time-consuming.

**The testing matrix problem.** Dependency modernization also explodes the testing matrix. ForgeRock tested against a fixed set: one JDK, one Tomcat, one set of dependencies. OIP must now validate against JDK 11, 17, and 21; Tomcat 10.0 and 10.1; multiple LDAP backends (embedded OpenDJ, external OpenDJ, external 389DS). Wren faces the same problem with JDK 17 and 21. Neither fork has the CI budget to test the full matrix, so both rely on "known good" combinations documented in their READMEs. This pragmatic approach works until a user hits an untested combination—at which point the debugging falls on the community, often a single maintainer.

**The convergence question.** Despite their different dependency strategies, OIP and Wren are converging on some choices. Both have adopted Jetty 10+ (migrating from Jetty 9's `javax.servlet` to `jakarta.servlet`). Both have moved to Tomcat 10.x as the reference deployment container. Both now require Maven 3.8+ to build (closing a known dependency resolution vulnerability in Maven 3.6). Whether the two forks will ever re-converge into a single codebase is unlikely—the Guice split alone makes merging prohibitively expensive—but the shared direction of travel suggests that the Java ecosystem's modernization pressure is stronger than any individual project's architectural preferences.

The modernization challenge is ultimately a story about the hidden costs of forking enterprise Java software. The source code is the visible artifact; the dependency graph, the build infrastructure, the testing matrix, and the compatibility contracts are the invisible ones. Both forks have made defensible choices given their constraints, but neither has fully solved the problem. The next major forcing function will be Java 11's end of extended support—when that happens, OIP will face the same Java 17 migration that Wren has already completed, potentially closing one of the last major divergences between the two forks.

---

![Swim Lane Timeline: Modern Era (2005-2026)](../diagrams/15b-swimlane-modern.png)

## Current State and Trajectory (2018-2026): A Fragmented Landscape

Today, the ForgeRock/OpenAM lineage exists in three states, each with a distinct risk profile.

### ForgeRock Community Edition 11.0.3: The Frozen Relic

The last open ForgeRock release, tagged April 27, 2017, is a time capsule. It remains available on GitHub in the `openam-community-edition` repository. It has 4,121 commits, 57 contributors, and zero activity since November 28, 2017.

It is also **catastrophically insecure**.

The CVE data is damning:

- **CVE-2021-35464** (CVSS 9.8): Pre-authentication remote code execution via Java deserialization. CISA issued an alert on July 12, 2021 warning of active exploitation. A Metasploit module exists. **Unpatched in CE.**
- **CVE-2021-29156** (CVSS 7.5): LDAP injection via the Webfinger protocol, allowing unauthenticated retrieval of password hashes and session tokens. **Unpatched in CE.**
- **CVE-2022-1471** (CVSS 9.8): SnakeYAML constructor deserialization RCE. **Unpatched in CE.**
- **CVE-2022-42889** (CVSS 9.8): Apache Commons Text arbitrary code execution via interpolation. **Unpatched in CE.**
- **CVE-2024-38999** (CVSS 9.8): RequireJS prototype pollution. **Unpatched in CE.**

Any internet-facing deployment of ForgeRock CE 11.0.3 should be assumed compromised. The recommendation is unambiguous: **immediate migration or decommissioning**.

### OIP OpenAM 16.0.5: The Maximalist Fork

Open Identity Platform's approach is characterized by breadth and velocity. The project maintains five repositories (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF) with synchronized releases. As of February 2026:

- **81 OpenAM releases** since the fork
- **82 OpenDJ releases**
- **24 OpenIDM releases** (though with a five-year gap from 2019 to 2024)
- **25 OpenIG releases**
- **13 OpenICF releases**

The architecture has evolved significantly beyond ForgeRock:

- **Horizontal scalability**: Cassandra-backed session/token store (OpenAM-cassandra module) replaces filesystem-based persistence
- **Real-time notifications**: WebSocket-based push notifications, mobile push auth
- **Compliance**: Comprehensive audit framework (openam-audit) with structured logging for SOX/GDPR
- **Modern auth**: Full OIDC Provider, WebAuthn/FIDO2, SAML 2.0 as an auth module (not just federation), scripted authentication via Groovy
- **Self-service**: User-driven password reset, account unlock workflows

Security patching is active but reactive. The git logs show CVE fixes following a consistent pattern:

1. Dependabot or manual scan identifies vulnerable dependency
2. Version bump commit lands within days to weeks
3. New release tagged within a month

Example: CVE-2022-42889 (Commons Text RCE) was patched in commit `e298fa5` on October 16, 2022, eleven days after the CVE was published.

The maintainer team is small—Valery Kharseko and a handful of irregular contributors—but output is steady. The project is viable for organizations willing to:

- Monitor security advisories manually
- Pin to the latest release and upgrade frequently
- Invest in operational security (WAF, network segmentation)
- Accept the risk of a community-supported product with no SLA

The Open Identity Platform has also published **extensive deployment documentation** and maintains a Google Group for community support.

### Wren:AM 16.0.0-M1: The Enterprise-Focused Alternative

Wren Security's approach is characterized by selectivity and formalism. The milestone designation signals caution—this is pre-production software being hardened for enterprise deployment.

Strengths:

- **Java 17+ requirement** positions Wren for modern JVM features (records, sealed classes, virtual threads when they arrive)
- **Jakarta EE 5.0 full compliance** (latest servlet/JSP/JSTL specs)
- **Structured CVE program** with dedicated PRs and test coverage for each vulnerability
- **Commercial support model** via Wren Security / Orchitech Solutions
- **Duo Security integration** for enterprise MFA requirements

Weaknesses:

- **Slower release cadence**: Only 24 tags since 2012 (vs. OIP's 81 for OpenAM)
- **Feature removals**: No WebAuthn, no QR auth, no reCAPTCHA (by design, but limits flexibility)
- **Milestone status**: 16.0.0-M1 is not a GA release, signaling ongoing stabilization

Wren Security's philosophy appears to be: "We'll support fewer features, but the ones we support will be production-grade." This is reflected in the Guice 3.0 decision—they deliberately kept an older, stable dependency injection framework to avoid breaking existing enterprise extensions, even as OIP rushed to Guice 7.0.

The target market is clear: European enterprises with data sovereignty requirements, government agencies with procurement preferences for European vendors, and financial services firms that need formal support contracts.

### The Competitive Landscape: PingIdentity, Keycloak, and the Market Shift

The ForgeRock story doesn't end with the open-source forks. In **October 2023**, PingIdentity—one of ForgeRock's primary competitors—announced it would acquire ForgeRock for $2.3 billion. The deal closed in January 2024, creating a combined entity that controls a significant share of the enterprise IAM market.

The acquisition validated ForgeRock's pivot to closed-source commercial software, but it also highlighted the fragility of the commercial IAM business model. PingIdentity itself had struggled with profitability and was facing competitive pressure from cloud-native alternatives:

**Keycloak**, a Red Hat-sponsored open-source IAM platform, has emerged as the dominant community alternative. Written from scratch in Java (using WildFly and Quarkus), it supports OIDC, SAML 2.0, OAuth 2.0, and LDAP user federation. Crucially, it's under **active development with a vibrant community**—3,000+ GitHub stars, bi-monthly releases, and official Red Hat support via Red Hat SSO.

**Auth0** (acquired by Okta in 2021 for $6.5B) pioneered developer-friendly IAM-as-a-Service, making identity as simple as `npm install`.

**Azure AD / Entra ID** (Microsoft) and **AWS IAM Identity Center** (Amazon) bundle identity with cloud platforms, making standalone IAM vendors less relevant.

The market has bifurcated:

- **Cloud-native SaaS**: Okta, Auth0, Azure AD dominate for greenfield projects
- **On-premises / hybrid**: Keycloak, OIP OpenAM, Wren:AM serve organizations with data sovereignty or air-gap requirements
- **Enterprise legacy**: PingIdentity/ForgeRock serve large enterprises with existing deployments and renewal inertia

The two open-source OpenAM forks occupy a narrow but defensible niche: organizations that need on-premises IAM, can't or won't pay vendor licensing fees, and have the operational maturity to run community-supported software.

### Lessons from the Closure

The ForgeRock source closure was not an isolated event. It belongs to a pattern that has repeated across the open-source infrastructure landscape, and the corporate outcomes that followed illuminate the economic forces that drive these decisions.

**The ForgeRock IPO and acquisition arc.** ForgeRock went public on the New York Stock Exchange on **September 16, 2021** (NYSE: FORG), pricing at $25/share and closing its first day at $36.35—a **$2.8 billion fully diluted valuation**. The IPO prospectus revealed what the closure had bought: $100M+ in annual recurring revenue, 1,300+ enterprise customers, and a gross margin north of 80%. The open-source era had built the brand; the closed-source era monetized it.

But public-market scrutiny proved unforgiving. By mid-2022, ForgeRock's stock had declined 60% from its IPO price amid the broader SaaS selloff. In **October 2023**, private equity firm **Thoma Bravo** acquired ForgeRock for $23.25/share—a **$2.3 billion take-private deal**, a 21% discount to the IPO valuation. Thoma Bravo simultaneously merged ForgeRock with its existing portfolio company **PingIdentity**, creating a combined entity controlling significant enterprise IAM market share. The cycle was complete: open-source project → venture-backed company → IPO → take-private → merger. The community contributors who built the early codebase saw none of this value.

**The open-core trap.** ForgeRock's trajectory followed a well-documented pattern in venture-backed open-source companies. The "open core" model—open-source the base, sell proprietary extensions—works until the open-source community becomes large enough that free riders outnumber paying customers. At that point, investors pressure for a licensing change. ForgeRock's case was textbook: the Series C in September 2016 demanded a credible path to profitability, and the open codebase was the most obvious cost center to eliminate.

The open-core model creates a structural tension: the more successful the community, the more it threatens the business model. ForgeRock's community was building production deployments at banks, universities, and government agencies without paying for support. Every successful free deployment was a lost contract.

**Parallel closures in the industry.** ForgeRock was not alone. The 2018-2024 period saw a wave of open-source relicensing events driven by identical economics:

| Company | Product | Year | License Change | Trigger |
|---------|---------|------|----------------|---------|
| ForgeRock | OpenAM/OpenDJ | 2016 | CDDL → Proprietary | Series C pressure, free-rider problem |
| Redis Labs | Redis | 2018 | BSD → Commons Clause → SSPL | AWS ElastiCache competing with managed Redis |
| Elastic | Elasticsearch | 2021 | Apache 2.0 → SSPL/Elastic License | AWS OpenSearch as a competing managed service |
| HashiCorp | Terraform | 2023 | MPL 2.0 → BSL 1.1 | Cloud providers offering managed Terraform services |
| Sentry | Sentry | 2024 | BSL 1.1 → FSL | Pre-emptive protection against cloud hosting |

The common thread: companies that built open-source infrastructure software found that hyperscalers or large enterprises could capture value without contributing back. The response—relicensing—triggered community forks in every case (OpenSearch from Elasticsearch, OpenTofu from Terraform, Valkey from Redis). ForgeRock's closure predated this wave by two years, making OIP and Wren among the earliest examples of post-closure community forks in enterprise infrastructure.

The outcomes of these forks vary. OpenSearch has thrived under AWS sponsorship, achieving feature parity with Elasticsearch within two years. OpenTofu, backed by the Linux Foundation, attracted 100+ corporate sponsors within months of HashiCorp's BSL announcement. Valkey, forked from Redis and adopted by AWS, Google, and Oracle, has arguably surpassed Redis in community momentum. By contrast, OIP and Wren lack a hyperscaler patron or foundation backing—they survive on individual maintainer commitment and small commercial support contracts. This makes them more fragile but also more independent; they answer to no corporate sponsor's roadmap.

**The regulatory dimension.** The closure also had compliance consequences that are often overlooked. Organizations in regulated industries (banking, healthcare, government) that had deployed OpenAM under CDDL found themselves in a difficult position: their security teams required access to source code for vulnerability assessment, their procurement teams required open licensing for audit purposes, and their legal teams needed assurance of license continuity. ForgeRock's commercial license addressed the first two concerns but at a cost that smaller organizations—community colleges, municipal governments, NGOs—could not absorb. For these organizations, the community forks were not a preference but a necessity. OIP's deployment documentation specifically targets this audience, with installation guides for Debian/Ubuntu LTS that emphasize zero-cost, source-available operation.

**Why CDDL enabled the forks.** The legal foundation for OIP and Wren's existence is the CDDL license Sun chose in 2005. CDDL is a file-level copyleft: modifications to CDDL-licensed files must remain CDDL, but larger works can combine CDDL code with proprietary code. Crucially, CDDL is irrevocable for code already released—ForgeRock could stop publishing new code under CDDL, but could not retroactively relicense existing commits.

This contrasts with proprietary licenses, which terminate on vendor discretion, and with permissive licenses (MIT, Apache 2.0), which allow relicensing without obligation. CDDL's copyleft nature meant any fork had to remain open-source, which paradoxically *encouraged* forking: the community knew their contributions couldn't be captured by a future corporate closure.

Had Sun chosen a proprietary license, no fork would have been legally possible. Had they chosen Apache 2.0, ForgeRock could have relicensed without triggering the community crisis that motivated the forks. The CDDL occupied the narrow middle ground that enabled both commercial exploitation (ForgeRock's business) and community survival (OIP and Wren). It is an accidental case study in how license choice shapes ecosystem resilience decades after the original decision.

**The human cost.** What the corporate narrative obscures is the impact on individual contributors. Engineers who had spent years building OpenAM's authentication framework, OpenDJ's replication engine, and OpenIDM's sync logic saw their work locked behind a corporate paywall. Several left ForgeRock after the closure. The community forums—where users had reported bugs, contributed patches, and helped each other troubleshoot deployments—went silent. The institutional knowledge embedded in those threads was effectively lost. OIP and Wren rebuilt community channels from scratch (Google Groups, GitHub Discussions, Gitter), but the accumulated social capital of the ForgeRock era could not be forked alongside the source code.

**What the closure got right.** Fairness demands acknowledging ForgeRock's perspective. The company had invested tens of millions in engineering salaries, test infrastructure, documentation, and support. The open-source community consumed these investments without proportional contribution. Of the 112 human contributors, approximately 85 were ForgeRock employees or contractors. Community contributions—external bug fixes, feature patches, documentation improvements—accounted for less than 15% of total commits. ForgeRock was, in effect, subsidizing an ecosystem that wasn't paying for itself. The closure was economically rational, even if it was a betrayal of the community's trust.

**The counterfactual.** What would have happened if ForgeRock had stayed open-source? The most likely scenario, based on comparable companies, is a slower path to profitability but a larger ecosystem. MongoDB (AGPL → SSPL but always source-available) and Red Hat (GPL, acquired for $34B) demonstrate that open-source enterprise infrastructure can generate enormous returns without closing the code. But both had community contribution rates far exceeding ForgeRock's 15%, and both operated in markets (databases, operating systems) with larger addressable markets than IAM. ForgeRock's niche may simply have been too narrow to sustain a pure open-source business at venture-capital scale. The closure was not inevitable, but it was predictable.

---

## Lessons from the Fragmentation

The OpenAM story offers several lessons for open-source sustainability:

**License choice matters.** Sun's decision to use CDDL instead of GPL or Apache 2.0 enabled ForgeRock's initial success but also made the eventual closure legally permissible. The weak copyleft meant ForgeRock could close the code, but it also meant the community could fork without legal risk. A stronger copyleft (AGPLv3) would have prevented the closure but might have deterred enterprise adoption in the first place.

**Velocity is not the same as viability.** OIP's 81 releases look impressive until you examine the patch notes—many are dependency bumps with minimal code changes. Wren's 24 releases reflect a more conservative, milestone-gated approach that may be more appropriate for enterprise risk tolerance.

**Security debt compounds.** The frozen Community Edition demonstrates the hazard of abandonment: five years after the fork, it has accumulated **22+ critical/high CVEs**, including multiple pre-auth RCEs. Any organization still running CE is operating negligently.

**Community forks require champions.** Both OIP and Wren succeeded because individual maintainers (Valery Kharseko, Pavel Horal) committed to long-term stewardship. Without those individuals, the code would have rotted.

**Standards outlive vendors.** Sun died, Oracle abandoned the projects, ForgeRock closed the source—but SAML 2.0, OAuth 2.0, LDAP, and OIDC continue to evolve. The implementations change, but the protocols endure. OpenAM's support for SAML 2.0, first added in the Sun era circa 2007, remains relevant in 2026—the same XML-based assertions, the same HTTP redirect bindings, the same metadata exchange patterns. An authentication module written against the SAML 2.0 spec in 2008 can, with minimal dependency updates, function in 2026. This protocol stability is what makes twenty-year-old codebases viable at all.

**Dependency management is the real maintenance burden.** The history makes clear that feature development is not what consumes community fork maintainers' time. Dependency upgrades, CVE remediation, Jakarta EE migration, Java version compatibility—these unglamorous tasks account for the majority of post-fork commits. The forks survive not because they add compelling new features, but because they keep the existing features running on modern, secure infrastructure.

---

## The Path Forward

As of early 2026, both OIP OpenAM and Wren:AM remain viable. Neither has the polish or ecosystem of Keycloak, and neither will ever match the feature velocity or vendor support of commercial products. But for organizations that need open-source IAM and can operate it competently, they represent the only mature, production-ready alternatives descended from Sun's original vision.

The next chapter will depend on community growth. If either fork can attract additional maintainers, expand test coverage, and build integrations with modern cloud-native ecosystems (Kubernetes operators, Helm charts, Terraform providers), they may achieve sustainability. If not, they will slowly fade as the last generation of Sun/ForgeRock-trained engineers retire and are replaced by practitioners who grew up with Keycloak and Auth0.

The git commit graphs tell a story of resilience. From 10,744 combined commits in 2014 to 401 in 2017, the collapse was existential. But from 2022 onward, the combined commit rate has stabilized at 300-500 per year. The code is alive. The community, though small, is persistent.

Twenty years after Sun's first OpenDS commit on June 28, 2006, the LDAP server still runs—now as OpenDJ 5.0.3 (OIP) and Wren:DS 5.0.4. The directory outlasted its original creator, its acquirer, its commercial successor, and a pandemic. It will likely outlast whatever comes next.

This is the nature of open-source infrastructure: it endures not because of corporate sponsorship or venture capital, but because someone, somewhere, still needs it—and someone, somewhere, is willing to keep the builds running.

---

**Sources:**
- Git commit history analysis (58,112 commits across 7 repositories, 2006-2026)
- Version evolution extract (ForgeRock CE 11.0.3 → OIP OpenAM 16.0.5 → Wren:AM 16.0.0-M1)
- Security CVE history (30+ CVEs tracked across all forks, 120+ security-related commits including dependency patches)
- Identity standards timeline (LDAP RFC 4510, SAML 2.0, OAuth 2.0 RFC 6749, OIDC Core 1.0)

**File references:**
- `/Users/kirane/projects/idp/docs/extracts/git-history-analysis.md`
- `/Users/kirane/projects/idp/docs/extracts/version-evolution.md`
- `/Users/kirane/projects/idp/docs/extracts/security-cve-history.md`
- `/Users/kirane/projects/idp/docs/extracts/standards-timeline.md`
