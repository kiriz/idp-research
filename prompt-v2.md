# Research Orchestration Plan: Identity & AAA Deep Analysis (v2)

## Context

We have 7 cloned repos representing the full lineage of open-source IAM from Sun Microsystems to present day, plus a 683-page ForgeRock OpenAM 12 Reference PDF and access to PingIdentity's complete archive of ForgeRock-era documentation. The goal is to produce a comprehensive research document covering the history of Identity, Authentication, Authorization, and Accounting (AAA) — analyzing each artifact in detail, its modern relevance, and what replaces it.

**Output:** `docs/` folder with interconnected markdown files + executive slide deck
**Audience:** Security architects (deep technical) + Engineering leadership (strategic)

## Global Context

| Item | Path |
|------|------|
| Project root | `/Users/kirane/projects/idp/` |
| Repos | `OpenAM/`, `OpenDJ/`, `OpenIDM/`, `OpenIG/`, `OpenICF/`, `openam-community-edition/`, `wrenam/` (all at project root) |
| Local PDF | `/Users/kirane/projects/idp/OpenAM-12-Reference.pdf` |
| Output base | `/Users/kirane/projects/idp/docs/` |
| Python env | `uv run` (deps in `pyproject.toml`: pypdf, pdfplumber) |

All paths in this document are relative to project root unless specified as absolute.

## References

| # | Source | Description |
|---|--------|-------------|
| 1 | https://github.com/OpenIdentityPlatform | OIP GitHub org (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF) |
| 2 | https://github.com/ForgeRock/openam-community-edition-11.0.3 | ForgeRock Community Edition (frozen at 11.0.3) |
| 3 | https://github.com/WrenSecurity/wrenam | Wren:AM fork |
| 4 | https://docs.pingidentity.com/archive/ | PingIdentity/ForgeRock archive docs |
| 5 | `/Users/kirane/projects/idp/OpenAM-12-Reference.pdf` (683 pages) | ForgeRock OpenAM 12 Reference |

---

## Global Constraints

### Extract Format & Size Limits
Every Phase 1 extract file MUST follow this structure:

```markdown
# {Extract Title}

## Executive Summary
<!-- ≤50 lines: key findings, suitable for quick scanning -->
<!-- Phase 2 agents read THIS FIRST before drilling into details -->

## Detailed Findings
<!-- Full content, organized by section -->
<!-- Target: ≤3000 lines per file -->
<!-- If content exceeds 3000 lines, split into multiple files with a master index -->
```

### Phase 2 Data Flow
- Phase 2 agents MUST read extracts from `docs/extracts/` by absolute file path
- Read executive summaries first, then drill into relevant detail sections
- Each Phase 2 task specifies exactly which extract files are inputs

### Cross-Chapter Reference Policy
- Each topic has ONE canonical chapter where it is explained in full depth
- Other chapters that mention the topic MUST cross-reference the canonical chapter rather than re-explaining. Use: `(see [Chapter N: Title](NN-slug.md#section))`
- Canonical ownership:
  - Authentication mechanisms → Ch.02
  - Federation protocols → Ch.03
  - Authorization frameworks → Ch.04
  - Directory services → Ch.05
  - Token formats → Ch.06
  - Component-specific analysis → Ch.07-11
  - Architecture patterns → Ch.12
  - Feature comparisons → Ch.13
- History (Ch.01) and Lessons (Ch.14) may summarize any topic briefly but must link to the deep-dive chapter

### Writing Style
- Voice: Third-person, technically precise, neutral tone
- Audience calibration: Write for a senior engineer who knows general security concepts but may not know IAM-specific protocols in depth
- Avoid: marketing language, superlatives ("best", "revolutionary"), first-person ("we found")
- Headings: Use `##` for major sections, `###` for subsections; max 4 levels deep
- Code references: Use backtick-wrapped file paths and inline code; use fenced blocks for configs/commands
- Tables: Preferred for comparisons; every table must have a caption or introductory sentence
- Length per chapter: 500-1500 lines target; flag if exceeding 2000
- Every chapter must open with a 3-5 sentence summary paragraph before diving into sections

### Terminology Standard

| Full name | Abbreviation | Rule |
|-----------|-------------|------|
| Open Identity Platform | OIP | Use "OIP" after first mention per chapter |
| ForgeRock Community Edition 11.0.3 | ForgeRock CE | Use "ForgeRock CE" after first mention |
| Wren:AM | Wren:AM | Always use colon form |
| OpenID Connect | OIDC | Use "OIDC" after first mention |
| Security Assertion Markup Language 2.0 | SAML 2.0 | Use "SAML 2.0" throughout |
| Lightweight Directory Access Protocol | LDAP | Use "LDAP" throughout |
| eXtensible Access Control Markup Language | XACML | Use "XACML" throughout |
| Identity Governance and Administration | IGA | Use "IGA" after first mention |
| Privileged Access Management | PAM | Use "PAM" after first mention |
| Identity Threat Detection and Response | ITDR | Use "ITDR" after first mention |

### Error Handling
- If an agent cannot complete a task, it MUST still produce the output file with:
  - What was completed successfully
  - A `## Known Gaps` section listing what failed and why
  - Suggested remediation for the orchestrator
- Downstream agents that depend on incomplete extracts should proceed with available data and note assumptions in their output
- The verification script checks for `## Known Gaps` sections and aggregates them into a completion report

---

## Phase 0: Environment Preparation (sequential, before all other phases)

### 0A. Download PingIdentity Archive PDFs
**Tool:** Bash (curl/wget)
**Task:** Download all relevant PDFs from `https://docs.pingidentity.com/archive/` using the CDN catalog at `https://cdn-docs.pingidentity.com/archive/pdf/catalog.json`. Base URL for downloads: `https://cdn-docs.pingidentity.com/archive/pdf/`

**Target product families (prioritized):**

| Priority | Family | Versions | Key docs |
|----------|--------|----------|----------|
| P0 | OpenAM | 10-13.5 | Admin Guide, Dev Guide, Reference, Install Guide |
| P0 | AM (ForgeRock) | 5-7.2 | OAuth2, OIDC, SAML2, UMA, Auth Nodes, Sessions, REST |
| P1 | DS / OpenDJ | 6.5-7.1 | LDAP Guide, REST Guide, Config Guide, Security Guide |
| P1 | IG / OpenIG | all | Gateway guides |
| P1 | IDM / OpenIDM | all | Admin, Dev, Install guides |
| P2 | ForgeRock Platform | 5-7.1 | Platform Guide, Setup Guide |
| P2 | Policy Agents (Web/Java) | all | Install, User Guide |
| P3 | Amster | 5-7.2 | User Guide, Entity Reference |

**Steps:**
1. Fetch `catalog.json` and validate it is well-formed JSON before proceeding
2. Download PDFs to `docs/archive/{family}/{version}/` preserving original filenames
3. Skip Javadoc ZIPs (too large, not needed for text analysis)
4. Log HTTP status code per download; continue on 404 but log as WARNING
5. Assert that all P0 family PDFs downloaded successfully; FAIL the task if any P0 PDF is missing
6. Log download manifest to `docs/archive/manifest.md` (include: file count, total size, any failures)

**Disk estimate:** ~2-5 GB total
**Output:** `docs/archive/` directory with all downloaded PDFs + manifest

### 0B. Unshallow Git Repositories
**Tool:** Bash (git)
**Task:** All 7 repos are shallow-cloned (`--depth 50`). Full history is required for git analysis (1G) and accurate code exploration (1B-1D). Run `git fetch --unshallow` on each.

**Repos:** `OpenAM`, `OpenDJ`, `OpenIDM`, `OpenIG`, `OpenICF`, `openam-community-edition`, `wrenam`

**Steps:**
1. For each repo: `cd {repo} && git fetch --unshallow`
2. Verify: `git rev-list --count HEAD` should show >1000 commits for OpenAM, >100 for smaller repos
3. If unshallow fails (rate limit, network): log the error, fall back to tag-based analysis only for that repo, and document the limitation in `## Known Gaps`

**Output:** Log results to stdout; no file output needed

---

## Task Dependency Graph

Tasks are organized into phases for readability, but execution follows this dependency DAG. A task can start as soon as all its dependencies are complete.

```
0A (download PDFs) ─────────────────────────┐
0B (unshallow repos) ───────────────────────┐│
                                            ││
Phase 1 (Data Extraction):                  ││
  1A-T1 (PDF Tier 1 extraction) ← 0A ──────┘│
  1A-T2 (PDF Tier 2 indexes) ← 1A-T1        │
  1B (protocol inventory) ← 0B ─────────────┘
  1C (version evolution) ← 0B
  1D (architecture extraction) ← 0B
  1E (modern landscape) ← no deps
  1F (standards timeline) ← no deps
  1G (git history) ← 0B
  1H (security/CVE) ← 0B (for git grep) + no deps (for WebSearch)
  1I (pre-computer auth) ← no deps

Phase 2 (Analysis & Synthesis):
  2A (history) ← 1C, 1F, 1G, 1H
  2B (protocol deep-dives) ← 1B, 1F, 1A-T2
  2C (component relevance) ← 1D, 1E
  2D (modern architecture) ← 1E, 1F
  2E (comparison matrices) ← 1E, 2C  ← NOTE: depends on Phase 2 task
  2F (lessons from history) ← 1I

Phase 3 (Assembly):
  3A (executive summary) ← all 2*
  3B (slide deck) ← 3A
```

**Practical parallelism:** If system limits prevent all agents running simultaneously, prioritize by dependency criticality:
- Phase 1 priority: 0B first (unblocks 1B-1D, 1G, 1H), then 1A-T1 (longest-running), then 1B, 1C, 1D, 1E, 1F, 1G, 1H, 1I in parallel
- Phase 2 priority: 2F (no Phase 1 deps via 1I), 2A, 2B, 2C, 2D in parallel, then 2E (depends on 2C)

---

## Phase 1: Data Extraction

Extract raw knowledge from all sources.

### 1A-T1. PDF Corpus Extraction — Tier 1 (Bash/Python)
**Tool:** `uv run python3` (pypdf + pdfplumber already in `pyproject.toml`)
**Depends on:** 0A
**Input:** All PDFs from `docs/archive/` + `/Users/kirane/projects/idp/OpenAM-12-Reference.pdf`
**Prerequisite check:** Verify `uv` is installed and Python >=3.13 available

**Per-PDF structured extraction:**
For each PDF, extract to `docs/extracts/pdf/{family}/{version}/{doc-name}.md`:
- Title, version, product
- Section headings (table of contents)
- Key content: config references, CLI tools, endpoints, tables, schemas
- Keep each file ~500-2000 lines (summarize dense sections, preserve tables verbatim)
- If a PDF fails to parse (corrupted, scanned-image-only), log it in `docs/extracts/pdf/extraction-errors.md` and skip

Example outputs:
```
docs/extracts/pdf/openam/12/reference.md
docs/extracts/pdf/openam/13.5/admin-guide.md
docs/extracts/pdf/am/7.2/oauth2-guide.md
docs/extracts/pdf/ds/7.1/ldap-guide.md
```

**Output:** `docs/extracts/pdf/` directory with per-PDF markdown files
**Done when:** Every successfully parsed PDF has a corresponding `.md` file; `extraction-errors.md` lists any failures

### 1A-T2. PDF Topic Index Construction — Tier 2 (general-purpose agent)
**Depends on:** 1A-T1
**Input:** All Tier 1 extracts in `docs/extracts/pdf/`
**Task:** Scan all Tier 1 extracts and build topic indexes that map content to source files:

| Index file | Topics covered |
|-----------|----------------|
| `docs/extracts/pdf-index-authentication.md` | Auth modules, auth chains, MFA, adaptive auth, social auth |
| `docs/extracts/pdf-index-federation.md` | SAML 2.0, OIDC, WS-Federation, federation config |
| `docs/extracts/pdf-index-authorization.md` | XACML, policy agents, entitlements, OAuth scopes, UMA |
| `docs/extracts/pdf-index-directory.md` | LDAP config, schema, replication, REST2LDAP, backends |
| `docs/extracts/pdf-index-provisioning.md` | IDM sync, reconciliation, connectors, managed objects |
| `docs/extracts/pdf-index-operations.md` | Install, deploy, upgrade, maintenance, monitoring, tuning |

Each index contains: topic -> source file path -> relevant section -> brief summary.

**Output:** `docs/extracts/pdf-index-*.md`
**Done when:** All 6 index files exist; each contains >=10 entries pointing to real Tier 1 files

### 1B. Protocol Inventory (Explore agent)
**Depends on:** 0B
**Task:** Scan all 7 repos to build a complete inventory of every protocol/standard implemented:
- Authentication: LDAP bind, RADIUS, Kerberos, SAML 2.0, OAuth 2.0, OIDC, WebAuthn/FIDO2, HOTP/TOTP, X.509 certs
- Authorization: XACML 3.0, OAuth scopes, UMA 2.0, policy agents
- Directory: LDAPv3, DSML, REST2LDAP
- Federation: SAML 2.0, WS-Federation, Liberty Alliance, OIDC Federation
- Token formats: SAML assertions, JWT, CTS tokens, opaque tokens
- Provisioning: SCIM-like patterns, OpenICF SPI
**Source files:** `OpenAM/openam-authentication/*/`, `OpenAM/openam-federation/`, `OpenAM/openam-oauth2/`, `OpenAM/openam-entitlements/`, `OpenDJ/opendj-core/`, `OpenICF/OpenICF-java-framework/`
**Output:** `docs/extracts/protocol-inventory.md`
**Done when:** Every protocol listed above has an entry with: module path, key Java classes, supported versions

### 1C. Version Evolution Diff (Explore agent)
**Depends on:** 0B
**Task:** Compare ForgeRock CE 11.0.3 against OIP OpenAM 16.0.5 against Wren:AM 16.0.0-M1:
- Which modules were added/removed/renamed?
- Which auth modules are new post-fork?
- How did the technology stack change (Java, deps, frameworks)?
- What features were added by OIP that ForgeRock CE didn't have?
**Source:** `openam-community-edition/pom.xml` vs `OpenAM/pom.xml` vs `wrenam/pom.xml`, module listings, auth module directories
**Output:** `docs/extracts/version-evolution.md`
**Done when:** Side-by-side module comparison table exists; tech stack diff table exists; >=5 new post-fork features identified

### 1D. Architecture Extraction per Component (Explore agent)
**Depends on:** 0B
**Task:** For each of the 5 OIP components, extract the core architectural patterns:
- OpenAM: Auth chain model, session management, policy engine, plugin SPI
- OpenDJ: Backend abstraction, replication protocol, REST2LDAP mapping
- OpenIDM: OSGi service model, sync/recon engine, managed objects, workflow integration
- OpenIG: Filter/handler pipeline, route configuration model, credential replay
- OpenICF: Connector SPI/API split, operation interfaces, remote connector server
**Output:** `docs/extracts/component-architectures.md`
**Done when:** Each component has: architecture diagram description, key interfaces/SPIs listed with file paths, data flow narrative

### 1E. Modern Landscape Research (general-purpose agent — WebSearch)
**Depends on:** no deps
**Task:** Research current state of IAM landscape. Split into sub-searches for depth:

**Sub-search 1: Established IAM platforms**
- Keycloak (features, architecture, latest version, community size)
- Ory stack (Hydra, Kratos, Keto, Oathkeeper)
- Auth0/Okta (capabilities, pricing model, market position)
- AWS Cognito, Azure AD B2C (Entra External ID), Google Identity Platform

**Sub-search 2: Next-generation OSS entrants**
- Casdoor (Go-based, UI-first IAM, Casbin ecosystem)
- Logto (TypeScript, OIDC-native, developer-experience focused)
- SuperTokens (self-hosted Auth0 alternative, session mgmt, prebuilt UI)
- Hanko (passkey-first, WebAuthn/FIDO2 native, passwordless-forward)
- Authelia, Authentik, Zitadel

**Sub-search 3: IGA, PAM, and ITDR**
- IGA: SailPoint, Saviynt (access certifications, SoD, joiner/mover/leaver lifecycle)
- PAM: CyberArk, Delinea, BeyondTrust, HashiCorp Vault (JIT access, session recording)
- ITDR: CrowdStrike, Silverfort, Microsoft Entra (identity threat detection)
- Directory: FreeIPA, 389 DS, Ping Identity

**Sub-search 4: Standards and patterns**
- OPA/Rego, Cedar (policy engines)
- SCIM 2.0 (provisioning standard, adoption status)
- Passkeys/WebAuthn adoption (enterprise rollout data)
- SPIFFE/SPIRE (workload identity)
- W3C Verifiable Credentials / DIDs (decentralized identity)

**Output:** `docs/extracts/modern-landscape.md`
**Done when:** Each product/standard has: description, key features, architecture summary, GitHub stars/community size (where applicable), last release date

### 1F. Standards Timeline Research (WebSearch)
**Depends on:** no deps
**Task:** Build a timeline of identity standards evolution:
- LDAP (1993) -> LDAPv3 (1997) -> virtual directories -> cloud directories
- SAML 1.0 (2002) -> 2.0 (2005) -> still dominant in enterprise
- OAuth 1.0 (2007) -> 2.0 (2012) -> 2.1 (draft) -> GNAP
- OpenID 1.0 (2005) -> 2.0 (2007) -> Connect (2014) -> OIDC Federation
- XACML 1.0 (2003) -> 3.0 (2013) -> OPA/Rego, Cedar
- SCIM 1.0 (2011) -> 2.0 (2015) -> adoption status
- FIDO U2F (2014) -> FIDO2/WebAuthn (2019) -> Passkeys (2022+)
- Passwordless evolution: SMS OTP -> TOTP -> push notifications -> platform authenticators -> synced passkeys -> device-bound passkeys
- FIDO Alliance adoption: Apple/Google/Microsoft passkey support, conditional UI, enterprise rollout patterns
- WS-Federation, WS-Trust, Liberty Alliance -> mostly deprecated
- UMA 1.0 (2015) -> 2.0 (2018) -> limited adoption
- Zero Trust architecture evolution
- W3C Verifiable Credentials (2019) -> DIDs -> decentralized identity trajectory
**Output:** `docs/extracts/standards-timeline.md`
**Done when:** Chronological table with year, standard, version, status, and successor for every entry above

### 1G. Git History Analysis (Bash — parallel across repos)
**Tool:** Bash (`git log`, `git tag`, `git branch`, `git shortlog`)
**Depends on:** 0B (repos must be unshallowed)
**Task:** Mine the git history of all 7 repos to extract development insights.

**Per repo (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF, openam-community-edition, wrenam):**

| Analysis | Command basis | Insight |
|----------|--------------|---------|
| Commit velocity | `git log --format='%ai' \| cut -d- -f1-2 \| sort \| uniq -c` | Development speed over time (commits/month) |
| Release timeline | `git tag --sort=creatordate --format='%(creatordate:short) %(refname:short)'` | Version milestones, release cadence |
| Branch inventory | `git branch -a --sort=-committerdate` | Feature branches -> roadmap/planned/abandoned work |
| Commit message mining | `git log --oneline --grep=<keyword>` for: fix, feat, security, CVE, OPENAM, OPENDJ, deprecat, upgrade, migration | Features, bugs, security fixes, thought process |
| Contributors | `git shortlog -sn --all` | Team size, core vs community, key developers |
| File churn hotspots | `git log --format=format: --name-only \| sort \| uniq -c \| sort -rn \| head -50` | Most modified files = complexity/problem areas |
| First/last commit | `git log --reverse --format='%ai' \| head -1` + `git log -1 --format='%ai'` | Project lifespan per repo |
| Fork divergence | `git merge-base` between CE, OIP, Wren (where available) | Point of divergence, drift magnitude |

**Cross-repo analysis:**
- Aggregate commit timelines into a unified development activity chart
- Identify periods of high/low activity (correlate with ForgeRock closure, fork events)
- Compare contributor overlap between OIP and Wren forks
- Extract security-related commits (grep for CVE, security, vulnerability, fix)

**Output:** `docs/extracts/git-history-analysis.md`
**Done when:** Per-repo summary table + cross-repo timeline + contributor analysis all present; commit counts verified >1000 for OpenAM

### 1H. Security & CVE History (general-purpose agent — WebSearch + git grep)
**Tool:** WebSearch (NVD/NIST, GitHub advisories) + Bash (git log grep)
**Depends on:** 0B (for git grep)
**Task:** Build a comprehensive vulnerability history across all forks.

**External sources (WebSearch):**
- NVD/NIST CVE database: search "openam", "opendj", "openidm", "openig", "forgerock"
- GitHub Security Advisories on each of the 7 repos
- ForgeRock archived security advisories (if available)
- Wren Security advisories

**Git-based extraction (Bash):**
- `git log --all --oneline --grep='CVE'` across all 7 repos
- `git log --all --oneline --grep='security'` (filter for actual fixes, not noise)
- `git log --all --oneline --grep='vulnerab'`

**Per CVE, capture:**
- CVE ID, severity (CVSS), affected component/version
- Which forks patched it and when (patch response time)
- Whether ForgeRock CE 11.0.3 (frozen) is affected and permanently unpatched
- OWASP category mapping (injection, broken auth, etc.)

**Produce:**
- CVE timeline: chronological list of all known vulnerabilities
- Patch matrix: CVE x fork showing patched/unpatched status
- Risk summary for each fork (especially frozen CE 11.0.3)
- OWASP category breakdown

**Output:** `docs/extracts/security-cve-history.md`
**Done when:** CVE table with >=5 entries; patch matrix covers all 3 forks; OWASP breakdown present

### 1I. Pre-Computer Authentication Research (general-purpose agent — WebSearch)
**Depends on:** no deps (can start immediately)
**Task:** Research historical authentication and trust mechanisms with real citations. This produces raw research data that Phase 2 task 2F will synthesize into a chapter.

**Research targets (with real examples, dates, and citations):**
- Mesopotamian cylinder seals (~3000 BC) -> digital signatures, non-repudiation
- Roman tessera hospitalis (guest tokens) -> bearer tokens, hardware tokens
- Shibboleth (Book of Judges 12:5-6) -> knowledge-based auth, CAPTCHAs
- Wax seals & signet rings (medieval) -> message integrity, private keys, HSMs
- Guild master marks & apprentice progression (12th-16th century) -> RBAC, graduated access
- Royal letters of introduction / safe-conduct passes -> federation, SAML assertions, delegated trust
- Military challenge-response watchwords -> CRAM, SCRAM protocols
- Split-key banking vaults (Renaissance) -> Shamir's Secret Sharing, MPC, threshold crypto
- Merchant reputation networks along Silk Road / Hanseatic League -> web of trust, decentralized identity
- Secret society multi-step rituals (Freemasons, etc.) -> multi-factor auth
- Diplomatic pouches (Vienna Convention 1961, but practice far older) -> E2E encryption, secure enclaves

**Also research:** academic papers, patents, or experimental systems that attempted to digitize the "untranslated patterns" (progressive trust, community attestation, reputation decay, proximity-as-auth, threshold authorization, lineage chains).

**Requirements:** Every historical claim must cite a real source (book, paper, archaeological record, primary text). No fabricated citations.

**Output:** `docs/extracts/pre-computer-auth-research.md`
**Done when:** >=10 historical mechanisms documented with citations; >=3 academic papers found on untranslated patterns

---

## Phase 2: Analysis & Synthesis

Take extracted data and produce analytical documents.

### 2A. Historical Narrative (documentation-generation:docs-architect)
**Depends on:** 1C, 1F, 1G, 1H
**Input:** Read `docs/extracts/version-evolution.md`, `docs/extracts/standards-timeline.md`, `docs/extracts/git-history-analysis.md`, `docs/extracts/security-cve-history.md`
**Task:** Write the historical narrative chapter:
- Sun Microsystems era (OpenSSO, Sun DS, Sun Identity Manager)
- Oracle acquisition and abandonment
- ForgeRock era (2010-2016): building the platform
- The closure event (Nov 2016) and its impact
- Community fork: OIP vs Wren Security divergence
- Current state and trajectory
- **Git-derived milestones:** Use commit velocity, release tags, contributor trends, and branch activity from 1G to ground the narrative with concrete data (e.g. "commits dropped 80% in Q4 2016", "first OIP release tagged on <date>")
- **Security track record:** Weave in CVE timeline from 1H to show how each fork handled security over time
**Output:** `docs/chapters/01-history.md`
**Done when:** 500-1500 lines; every era listed above has a section; >=5 git-derived data points cited; CVE timeline woven in

### 2B. Protocol Deep-Dive Chapters (documentation-generation:docs-architect)
**Depends on:** 1B, 1F, 1A-T2
**Input:**
- `docs/extracts/protocol-inventory.md` (1B)
- `docs/extracts/standards-timeline.md` (1F)
- `docs/extracts/pdf-index-authentication.md` (1A-T2) — for Ch.02
- `docs/extracts/pdf-index-federation.md` (1A-T2) — for Ch.03
- `docs/extracts/pdf-index-authorization.md` (1A-T2) — for Ch.04
- `docs/extracts/pdf-index-directory.md` (1A-T2) — for Ch.05
- Drill into Tier 1 extracts as needed via index references

**Task:** For each protocol family, write a chapter covering:
- What problem it solves
- How it works (technical)
- How it's implemented in the OIP codebase (with file references)
- Current relevance (still used? deprecated? superseded?)
- What replaces it and why
- Migration considerations

Chapters:
- `docs/chapters/02-authentication-protocols.md` (LDAP, RADIUS, Kerberos, certs, MFA/OTP, WebAuthn/FIDO2, Passkeys & passwordless: synced vs device-bound, phishing resistance, enterprise adoption, death of SMS OTP)
- `docs/chapters/03-federation-protocols.md` (SAML, WS-Fed, Liberty, OIDC)
- `docs/chapters/04-authorization-frameworks.md` (XACML, OAuth scopes, UMA, policy agents, OPA)
- `docs/chapters/05-directory-services.md` (LDAP, DSML, REST APIs, SCIM, cloud directories)
- `docs/chapters/06-token-formats.md` (SAML assertions, JWT, opaque, CTS, DPoP, token binding)

**Done when:** Each of the 5 files is 500-1500 lines; every protocol in the parenthetical has a subsection; >=3 OIP source file references per chapter; cross-references to related chapters via markdown links

### 2C. Component Relevance Analysis (comprehensive-review:architect-review)
**Depends on:** 1D, 1E
**Input:**
- `docs/extracts/component-architectures.md` (1D)
- `docs/extracts/modern-landscape.md` (1E)
- `docs/extracts/pdf-index-operations.md` (1A-T2) — for deployment/operational context

**Task:** For each of the 5 OIP components, analyze:
- What it does and why it was needed
- Is this component pattern still relevant today?
- Modern alternatives and how they compare
- Feature gap analysis (what OIP has that alternatives lack and vice versa)
- Build-vs-buy decision framework

Output:
- `docs/chapters/07-openam-analysis.md` (vs Keycloak, Auth0, Cognito)
- `docs/chapters/08-opendj-analysis.md` (vs 389 DS, cloud directories)
- `docs/chapters/09-openidm-analysis.md` (vs SailPoint, Saviynt, SCIM)
- `docs/chapters/10-openig-analysis.md` (vs Kong, Envoy, API gateways)
- `docs/chapters/11-openicf-analysis.md` (vs native cloud connectors, SCIM)

**Done when:** Each of the 5 files is 500-1500 lines; each has: component summary, >=3 alternatives compared, gap analysis table, build-vs-buy recommendation

### 2D. Modern Architecture Patterns (backend-api-security:backend-architect)
**Depends on:** 1E, 1F
**Input:**
- `docs/extracts/modern-landscape.md` (1E)
- `docs/extracts/standards-timeline.md` (1F)

**Task:** Write chapter on how IAM architecture has shifted:
- Monolithic IAM suite -> decomposed microservices
- On-prem LDAP -> cloud-native identity stores
- SAML federation -> OIDC federation
- Policy agents -> API gateways + sidecar proxies
- Provisioning connectors -> SCIM + event-driven sync
- Session cookies -> stateless JWT -> token binding
- Password-based auth -> Passwordless/Passkeys (FIDO2, platform authenticators, conditional UI, phishing-resistant MFA)
- Perimeter security -> Zero Trust architecture (phishing-resistant auth as prerequisite)
- Human identity -> machine identity (SPIFFE/SPIRE, workload identity)
- AI and identity: adaptive auth, behavioral biometrics, LLM-powered policy
- Compliance-driven IAM: audit trails, consent management (GDPR), data residency, right-to-be-forgotten implications for identity stores
- API security and identity: OAuth token validation at gateway, mTLS, service mesh identity
- Identity Threat Detection and Response (ITDR): credential stuffing detection, token theft, MFA fatigue attacks
- Decentralized identity: W3C Verifiable Credentials, DIDs, self-sovereign identity trajectory

**Output:** `docs/chapters/12-modern-architecture.md`
**Done when:** 500-1500 lines; every bullet above has a subsection; includes "then vs now" comparison table

### 2E. Comparison Matrix (general-purpose agent)
**Depends on:** 1E, 2C (must wait for 2C to complete)
**Input:**
- `docs/extracts/modern-landscape.md` (1E)
- `docs/chapters/07-openam-analysis.md` through `docs/chapters/11-openicf-analysis.md` (2C)

**Task:** Build detailed feature comparison tables:

**Access Management (Tier 1 — deep comparison):** OpenAM vs Keycloak vs Ory vs Auth0/Okta vs AWS Cognito
**Access Management (Tier 2 — brief notes):** Zitadel, Authentik, Casdoor, Logto, SuperTokens, Hanko
**Directory:** OpenDJ vs 389 DS vs FreeIPA vs Azure AD vs AWS Directory Service
**Provisioning/IGA:** OpenIDM vs SailPoint vs Saviynt vs SCIM-native
**Gateway:** OpenIG vs Kong vs Envoy/Istio vs AWS API Gateway
**Connectors:** OpenICF vs SCIM vs native integrations
**PAM:** CyberArk vs Delinea vs BeyondTrust vs HashiCorp Vault (brief)

Tables should cover: auth protocols, MFA support, federation, self-service, scalability, deployment model, license, community activity, enterprise support. Each cell should be a short phrase or rating (High/Medium/Low/None), not prose paragraphs.

**Output:** `docs/chapters/13-comparison-matrices.md`
**Done when:** All 7 category tables exist; Tier 1 products have all dimensions filled; no empty cells (use "N/A" or "Not supported")

### 2F. Pre-Computer Authentication — Lessons from History (documentation-generation:docs-architect)
**Depends on:** 1I
**Input:** `docs/extracts/pre-computer-auth-research.md` (1I)
**Task:** Synthesize the raw research from 1I into a polished chapter grounding modern IAM in 5,000 years of human trust mechanisms.

**Structure:**
1. Narrative tour through historical trust mechanisms (with citations from 1I research)
2. Mapping table: historical mechanism -> modern IAM equivalent -> status (solved/underused/untranslated)
3. Deep analysis of untranslated patterns:

| Historical pattern | Why it's underused digitally | Opportunity |
|--------------------|------------------------------|-------------|
| Progressive trust (guild model) | Modern RBAC grants full role access instantly | Time-based + competence-based access escalation |
| Community attestation / vouching | Decentralized identity (DID) hasn't cracked usability | Social trust graphs for authorization |
| Physical proximity as trust | BLE/NFC auth exists but isn't a standard IAM factor | Proximity as continuous auth signal |
| Ritual as multi-party authorization | Threshold crypto exists but no IAM system uses it natively | N-of-M approval workflows beyond simple manager approval |
| Reputation decay over absence | Tokens expire but don't model trust erosion over inactivity | Continuous trust scoring that degrades without reinforcement |
| Lineage/provenance chains | Verifiable Credentials (W3C) emerging but early | Identity chains that prove delegation history |

4. For each untranslated pattern: cite any academic papers, patents, or experimental systems found in 1I research
5. Conclude with: which forgotten patterns could solve problems modern IAM still struggles with?

**Output:** `docs/chapters/14-lessons-from-history.md`
**Done when:** 500-1500 lines; every historical mechanism has a real citation; >=3 untranslated patterns have academic paper references; concluding section with actionable insights

---

## Phase 3: Assembly & Presentation (sequential)

### 3A. Executive Summary & Index
**Depends on:** all Phase 2 tasks
**Task:** Write the master `docs/README.md` with:
- Executive summary (1-2 pages for leadership)
- Document structure and navigation
- Key findings and recommendations
- Reading guide for different audiences
- Aggregate any `## Known Gaps` sections from all chapters into a completion status table

**Done when:** README exists; links to all 14 chapters; no broken links

### 3B. Slide Deck (document-skills:pptx)
**Depends on:** 3A
**Task:** Create executive slide deck (~20-25 slides):

| Slides | Content | Source chapter |
|--------|---------|---------------|
| 1 | Title: "Identity & Access Management: Evolution, Architecture & Modern Landscape" | — |
| 2-4 | Timeline: Sun -> ForgeRock -> OIP/Wren with key dates and git-derived data | Ch.01 + 1G |
| 5 | The 5 OIP components and how they fit together | Ch.07-11 summaries |
| 6-9 | Protocol evolution (1 slide per family: auth, federation, authz, tokens) | Ch.02-06 key tables |
| 10-14 | Component vs modern alternatives (1 slide per component) | Ch.07-11 comparison summaries |
| 15-16 | Architecture shift: then vs now | Ch.12 key diagrams |
| 17-18 | Passwordless & passkeys future | Ch.02 + Ch.12 |
| 19-20 | Decision framework: when to use what | Ch.13 matrices condensed |
| 21-22 | Compliance, PAM, ITDR landscape | Ch.12 sections |
| 23 | Historical patterns we should revive | Ch.14 key insights |
| 24-25 | Recommendations + Q&A | README key findings |

**Done when:** PPTX file exists with 20-25 slides; each slide has content, not just titles

---

## Agent-to-Task Mapping

| Task | Description | Agent Type | Depends on |
|------|-----------|-----------|------------|
| 0A | Download archive PDFs | Bash (curl) | — |
| 0B | Unshallow git repos | Bash (git) | — |
| 1A-T1 | PDF Tier 1 extraction | Bash (uv run python) | 0A |
| 1A-T2 | PDF Tier 2 topic indexes | general-purpose | 1A-T1 |
| 1B | Protocol inventory | Explore | 0B |
| 1C | Version evolution diff | Explore | 0B |
| 1D | Architecture extraction | Explore | 0B |
| 1E | Modern landscape research | general-purpose (WebSearch) | — |
| 1F | Standards timeline | general-purpose (WebSearch) | — |
| 1G | Git history analysis | Bash (git commands) | 0B |
| 1H | Security/CVE history | general-purpose (WebSearch + git) | 0B |
| 1I | Pre-computer auth research | general-purpose (WebSearch) | — |
| 2A | Historical narrative | documentation-generation:docs-architect | 1C, 1F, 1G, 1H |
| 2B | Protocol deep-dives | documentation-generation:docs-architect | 1B, 1F, 1A-T2 |
| 2C | Component relevance | comprehensive-review:architect-review | 1D, 1E |
| 2D | Modern architecture | backend-api-security:backend-architect | 1E, 1F |
| 2E | Comparison matrices | general-purpose | 1E, 2C |
| 2F | Lessons from history | documentation-generation:docs-architect | 1I |
| 3A | Executive summary | Main agent | all 2* |
| 3B | Slide deck | document-skills:pptx | 3A |

---

## Output Structure

```
docs/
├── README.md                          # Executive summary + navigation
├── archive/                           # Downloaded PingIdentity archive PDFs (Phase 0)
│   ├── manifest.md
│   ├── openam/{version}/*.pdf
│   ├── am/{version}/*.pdf
│   ├── ds/{version}/*.pdf
│   ├── ig/{version}/*.pdf
│   └── idm/{version}/*.pdf
├── extracts/                          # Raw extracted data (Phase 1)
│   ├── pdf/                           # Tier 1: per-PDF extracts
│   │   ├── openam/{version}/*.md
│   │   ├── am/{version}/*.md
│   │   ├── ds/{version}/*.md
│   │   ├── ig/{version}/*.md
│   │   ├── idm/{version}/*.md
│   │   └── extraction-errors.md       # Failed PDF parses
│   ├── pdf-index-authentication.md    # Tier 2: topic cross-references
│   ├── pdf-index-federation.md
│   ├── pdf-index-authorization.md
│   ├── pdf-index-directory.md
│   ├── pdf-index-provisioning.md
│   ├── pdf-index-operations.md
│   ├── protocol-inventory.md
│   ├── version-evolution.md
│   ├── component-architectures.md
│   ├── modern-landscape.md
│   ├── standards-timeline.md
│   ├── git-history-analysis.md
│   ├── security-cve-history.md
│   └── pre-computer-auth-research.md
├── chapters/                          # Analytical chapters (Phase 2)
│   ├── 01-history.md
│   ├── 02-authentication-protocols.md
│   ├── 03-federation-protocols.md
│   ├── 04-authorization-frameworks.md
│   ├── 05-directory-services.md
│   ├── 06-token-formats.md
│   ├── 07-openam-analysis.md
│   ├── 08-opendj-analysis.md
│   ├── 09-openidm-analysis.md
│   ├── 10-openig-analysis.md
│   ├── 11-openicf-analysis.md
│   ├── 12-modern-architecture.md
│   ├── 13-comparison-matrices.md
│   └── 14-lessons-from-history.md
└── presentations/
    └── iam-evolution-deck.pptx        # Executive slide deck
```

---

## Verification

### Automated checks (Bash script)
Run after all phases complete:

```bash
#!/bin/bash
cd /Users/kirane/projects/idp

echo "=== 1. File existence ==="
for f in docs/chapters/{01..14}-*.md docs/README.md; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done
for f in docs/extracts/protocol-inventory.md docs/extracts/version-evolution.md \
         docs/extracts/component-architectures.md docs/extracts/modern-landscape.md \
         docs/extracts/standards-timeline.md docs/extracts/git-history-analysis.md \
         docs/extracts/security-cve-history.md docs/extracts/pre-computer-auth-research.md; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done
for f in docs/extracts/pdf-index-{authentication,federation,authorization,directory,provisioning,operations}.md; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done

echo "=== 2. Minimum content (chapters >=100 lines, extracts >=50 lines) ==="
for f in docs/chapters/*.md; do
  lines=$(wc -l < "$f" 2>/dev/null || echo 0)
  [ "$lines" -ge 100 ] && echo "OK: $f ($lines lines)" || echo "SHORT: $f ($lines lines)"
done
for f in docs/extracts/*.md; do
  lines=$(wc -l < "$f" 2>/dev/null || echo 0)
  [ "$lines" -ge 50 ] && echo "OK: $f ($lines lines)" || echo "SHORT: $f ($lines lines)"
done

echo "=== 3. Cross-reference validation ==="
grep -roh '\]([^)]*\.md[^)]*)' docs/chapters/ docs/README.md 2>/dev/null | \
  sed 's/\](//' | sed 's/)//' | sed 's/#.*//' | sort -u | while read link; do
  if [ -f "docs/chapters/$link" ] || [ -f "docs/$link" ] || [ -f "$link" ]; then
    echo "OK: $link"
  else
    echo "BROKEN LINK: $link"
  fi
done

echo "=== 4. Comparison matrix completeness ==="
for product in OpenAM Keycloak Auth0 Okta Cognito Ory Zitadel Authentik Casdoor Logto SuperTokens Hanko CyberArk SailPoint; do
  grep -q "$product" docs/chapters/13-comparison-matrices.md 2>/dev/null && echo "OK: $product" || echo "MISSING: $product"
done

echo "=== 5. Code file references spot-check ==="
grep -oE '`[A-Za-z][A-Za-z0-9/._-]+\.java`' docs/chapters/*.md 2>/dev/null | while IFS=: read chapter ref; do
  file="${ref//\`/}"
  [ -f "$file" ] && echo "OK: $file" || echo "INVALID REF: $file in $chapter"
done

echo "=== 6. Extract-to-chapter traceability ==="
declare -A EXPECTED_REFS=(
  ["01-history"]="version-evolution standards-timeline git-history-analysis security-cve-history"
  ["02-authentication"]="protocol-inventory pdf-index-authentication"
  ["03-federation"]="protocol-inventory pdf-index-federation"
  ["04-authorization"]="protocol-inventory pdf-index-authorization"
  ["05-directory"]="protocol-inventory pdf-index-directory"
  ["07-openam"]="component-architectures modern-landscape"
  ["12-modern"]="modern-landscape standards-timeline"
  ["14-lessons"]="pre-computer-auth-research"
)
for chapter in "${!EXPECTED_REFS[@]}"; do
  match=$(ls docs/chapters/${chapter}*.md 2>/dev/null | head -1)
  if [ -n "$match" ]; then
    for extract in ${EXPECTED_REFS[$chapter]}; do
      grep -q "$extract" "$match" && echo "OK: $chapter -> $extract" || echo "MISSING REF: $chapter should reference $extract"
    done
  fi
done

echo "=== 7. Known Gaps aggregation ==="
echo "Files with Known Gaps sections:"
grep -rl "## Known Gaps" docs/ 2>/dev/null || echo "None found (good)"
```

### Manual review checklist
1. Executive summary (`docs/README.md`) is coherent and serves both audiences
2. Historical narrative (Ch.01) includes git-derived milestones and CVE timeline
3. Passwordless/passkeys covered substantively in Ch.02 and Ch.12
4. Slide deck has ~20-25 slides with actual content (not just titles)
5. Each Phase 1 extract has an Executive Summary section (<=50 lines)
6. Topic cross-reference indexes (pdf-index-*.md) correctly point to Tier 1 extracts
7. No contradictions between Ch.07-11 (component analysis) and Ch.13 (comparison matrices)
8. Cross-chapter links resolve and point to correct sections
9. Consistent terminology throughout (per Terminology Standard table above)
10. Ch.14 (Lessons from History) has real citations, not fabricated sources
11. Known Gaps sections aggregated — are any critical?
12. No chapter exceeds 2000 lines without justification
13. Comparison matrices have no empty cells (every intersection has at least "N/A" or "Not supported")
14. Compliance/GDPR, PAM, and ITDR topics appear in Ch.12 and Ch.13
15. Slide deck content matches source chapters per the mapping table
