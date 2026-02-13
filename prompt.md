# Research Orchestration Plan: Identity & AAA Deep Analysis

## Context

We have 7 cloned repos representing the full lineage of open-source IAM from Sun Microsystems to present day, plus a 683-page ForgeRock OpenAM 12 Reference PDF. The goal is to produce a comprehensive research document covering the history of Identity, Authentication, Authorization, and Accounting (AAA) — analyzing each artifact in detail, its modern relevance, and what replaces it.

**Output:** `docs/` folder with interconnected markdown files + executive slide deck
**Audience:** Security architects (deep technical) + Engineering leadership (strategic)

## References

| # | Source | Description |
|---|--------|-------------|
| 1 | https://github.com/OpenIdentityPlatform | OIP GitHub org (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF) |
| 2 | https://github.com/ForgeRock/openam-community-edition-11.0.3 | ForgeRock Community Edition (frozen at 11.0.3) |
| 3 | https://github.com/WrenSecurity/wrenam | Wren:AM fork |
| 4 | https://docs.pingidentity.com/archive/ | PingIdentity/ForgeRock archive docs |
| 5 | `OpenAM-12-Reference.pdf` (local, 683 pages) | ForgeRock OpenAM 12 Reference |

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
- Phase 2 agents MUST read extracts from `docs/extracts/` by file path
- Read executive summaries first, then drill into relevant detail sections
- Each Phase 2 task specifies which extract files and sections are inputs

---

## Phase 0: Document Acquisition (sequential, before all other phases)

### 0A. Download PingIdentity Archive PDFs
**Tool:** Bash (curl/wget)
**Task:** Download all relevant PDFs from `https://docs.pingidentity.com/archive/` using the CDN catalog at `https://cdn-docs.pingidentity.com/archive/pdf/catalog.json`. Base URL for downloads: `https://cdn-docs.pingidentity.com/archive/pdf/`

**Target product families (prioritized):**

| Priority | Family | Versions | Key docs |
|----------|--------|----------|----------|
| P0 | OpenAM | 10–13.5 | Admin Guide, Dev Guide, Reference, Install Guide |
| P0 | AM (ForgeRock) | 5–7.2 | OAuth2, OIDC, SAML2, UMA, Auth Nodes, Sessions, REST |
| P1 | DS / OpenDJ | 6.5–7.1 | LDAP Guide, REST Guide, Config Guide, Security Guide |
| P1 | IG / OpenIG | all | Gateway guides |
| P1 | IDM / OpenIDM | all | Admin, Dev, Install guides |
| P2 | ForgeRock Platform | 5–7.1 | Platform Guide, Setup Guide |
| P2 | Policy Agents (Web/Java) | all | Install, User Guide |
| P3 | Amster | 5–7.2 | User Guide, Entity Reference |

**Steps:**
1. Fetch `catalog.json` and parse all entries for the families above
2. Download PDFs to `docs/archive/{family}/{version}/` preserving original filenames
3. Skip Javadoc ZIPs (too large, not needed for text analysis)
4. Log download manifest to `docs/archive/manifest.md`

**Output:** `docs/archive/` directory with all downloaded PDFs + manifest

---

## Phase 1: Data Extraction (parallel, ~6 agents)

Extract raw knowledge from all sources before any analysis begins.

### 1A. PDF Corpus Extraction — Two-Tier (Bash/Python)
**Tool:** `uv run python3` script (pypdf + pdfplumber)
**Input:** All PDFs from Phase 0 (`docs/archive/`) + local `OpenAM-12-Reference.pdf`

**Tier 1 — Per-PDF structured extraction:**
For each PDF, extract to `docs/extracts/pdf/{family}/{version}/{doc-name}.md`:
- Title, version, product
- Section headings (table of contents)
- Key content: config references, CLI tools, endpoints, tables, schemas
- Keep each file ~500–2000 lines (summarize dense sections, preserve tables verbatim)

Example outputs:
```
docs/extracts/pdf/openam/12/reference.md
docs/extracts/pdf/openam/13.5/admin-guide.md
docs/extracts/pdf/am/7.2/oauth2-guide.md
docs/extracts/pdf/ds/7.1/ldap-guide.md
docs/extracts/pdf/ig/7.1/gateway-guide.md
docs/extracts/pdf/idm/7.2/admin-guide.md
```

**Tier 2 — Topic-based cross-reference indexes:**
Scan all Tier 1 extracts and build topic indexes that map content to source files:

| Index file | Topics covered |
|-----------|----------------|
| `docs/extracts/pdf-index-authentication.md` | Auth modules, auth chains, MFA, adaptive auth, social auth |
| `docs/extracts/pdf-index-federation.md` | SAML 2.0, OIDC, WS-Federation, federation config |
| `docs/extracts/pdf-index-authorization.md` | XACML, policy agents, entitlements, OAuth scopes, UMA |
| `docs/extracts/pdf-index-directory.md` | LDAP config, schema, replication, REST2LDAP, backends |
| `docs/extracts/pdf-index-provisioning.md` | IDM sync, reconciliation, connectors, managed objects |
| `docs/extracts/pdf-index-operations.md` | Install, deploy, upgrade, maintenance, monitoring, tuning |

Each index contains: topic → source file path → relevant section → brief summary. This allows Phase 2 agents to read the index first, then drill into specific extracts.

**Output:** `docs/extracts/pdf/` (Tier 1) + `docs/extracts/pdf-index-*.md` (Tier 2)

### 1B. Protocol Inventory (Explore agent)
**Task:** Scan all 7 repos to build a complete inventory of every protocol/standard implemented:
- Authentication: LDAP bind, RADIUS, Kerberos, SAML 2.0, OAuth 2.0, OIDC, WebAuthn/FIDO2, HOTP/TOTP, X.509 certs
- Authorization: XACML 3.0, OAuth scopes, UMA 2.0, policy agents
- Directory: LDAPv3, DSML, REST2LDAP
- Federation: SAML 2.0, WS-Federation, Liberty Alliance, OIDC Federation
- Token formats: SAML assertions, JWT, CTS tokens, opaque tokens
- Provisioning: SCIM-like patterns, OpenICF SPI
**Source files:** `OpenAM/openam-authentication/*/`, `OpenAM/openam-federation/`, `OpenAM/openam-oauth2/`, `OpenAM/openam-entitlements/`, `OpenDJ/opendj-core/`, `OpenICF/OpenICF-java-framework/`
**Output:** `docs/extracts/protocol-inventory.md`

### 1C. Version Evolution Diff (Explore agent)
**Task:** Compare ForgeRock CE 11.0.3 against OIP OpenAM 16.0.5 against WrenAM 16.0.0-M1:
- Which modules were added/removed/renamed?
- Which auth modules are new post-fork?
- How did the technology stack change (Java, deps, frameworks)?
- What features were added by OIP that ForgeRock CE didn't have?
**Source:** `openam-community-edition/pom.xml` vs `OpenAM/pom.xml` vs `wrenam/pom.xml`, module listings, auth module directories
**Output:** `docs/extracts/version-evolution.md`

### 1D. Architecture Extraction per Component (Explore agent)
**Task:** For each of the 5 OIP components, extract the core architectural patterns:
- OpenAM: Auth chain model, session management, policy engine, plugin SPI
- OpenDJ: Backend abstraction, replication protocol, REST2LDAP mapping
- OpenIDM: OSGi service model, sync/recon engine, managed objects, workflow integration
- OpenIG: Filter/handler pipeline, route configuration model, credential replay
- OpenICF: Connector SPI/API split, operation interfaces, remote connector server
**Output:** `docs/extracts/component-architectures.md`

### 1E. Modern Landscape Research (WebSearch — multiple queries)
**Task:** Research current state of IAM landscape for comparison:

**Established players:**
- Keycloak (features, architecture, version)
- Ory stack (Hydra, Kratos, Keto, Oathkeeper)
- Auth0/Okta (capabilities, pricing model)
- AWS Cognito, Azure AD B2C, Google Identity Platform
- Authelia, Authentik, Zitadel
- FreeIPA, 389 DS, Ping Identity
- SailPoint, Saviynt (IGA)

**Next-generation OSS entrants:**
- Casdoor (Go-based, UI-first IAM, Casbin ecosystem)
- Logto (TypeScript, OIDC-native, developer-experience focused)
- SuperTokens (self-hosted Auth0 alternative, session mgmt, prebuilt UI)
- Hanko (passkey-first, WebAuthn/FIDO2 native, passwordless-forward)

**Standards & patterns:**
- OPA/Rego (policy engine)
- SCIM 2.0 (provisioning standard)
- Passkeys/WebAuthn adoption
**Output:** `docs/extracts/modern-landscape.md`

### 1F. Standards Timeline Research (WebSearch)
**Task:** Build a timeline of identity standards evolution:
- LDAP (1993) → LDAPv3 (1997) → virtual directories → cloud directories
- SAML 1.0 (2002) → 2.0 (2005) → still dominant in enterprise
- OAuth 1.0 (2007) → 2.0 (2012) → 2.1 (draft) → GNAP
- OpenID 1.0 (2005) → 2.0 (2007) → Connect (2014) → OIDC Federation
- XACML 1.0 (2003) → 3.0 (2013) → OPA/Rego, Cedar
- SCIM 1.0 (2011) → 2.0 (2015) → adoption status
- FIDO U2F (2014) → FIDO2/WebAuthn (2019) → Passkeys (2022+)
- Passwordless evolution: SMS OTP → TOTP → push notifications → platform authenticators → synced passkeys → device-bound passkeys
- FIDO Alliance adoption: Apple/Google/Microsoft passkey support, conditional UI, enterprise rollout patterns
- WS-Federation, WS-Trust, Liberty Alliance → mostly deprecated
- UMA 1.0 (2015) → 2.0 (2018) → limited adoption
- Zero Trust architecture evolution
**Output:** `docs/extracts/standards-timeline.md`

### 1G. Git History Analysis (Bash — parallel across repos)
**Tool:** Bash (`git log`, `git tag`, `git branch`, `git shortlog`)
**Task:** Mine the git history of all 7 repos to extract development insights.

**Per repo (OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF, openam-community-edition, wrenam):**

| Analysis | Command basis | Insight |
|----------|--------------|---------|
| Commit velocity | `git log --format='%ai' \| cut -d- -f1-2 \| sort \| uniq -c` | Development speed over time (commits/month) |
| Release timeline | `git tag --sort=creatordate --format='%(creatordate:short) %(refname:short)'` | Version milestones, release cadence |
| Branch inventory | `git branch -a --sort=-committerdate` | Feature branches → roadmap/planned/abandoned work |
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

### 1H. Security & CVE History (general-purpose agent — WebSearch + git grep)
**Tool:** WebSearch (NVD/NIST, GitHub advisories) + Bash (git log grep)
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
- Patch matrix: CVE × fork showing patched/unpatched status
- Risk summary for each fork (especially frozen CE 11.0.3)
- OWASP category breakdown

**Output:** `docs/extracts/security-cve-history.md`

---

## Phase 2: Analysis & Synthesis (parallel, ~5 agents)

Take extracted data and produce analytical documents.

### 2A. Historical Narrative (documentation-generation:docs-architect)
**Input:** Read `docs/extracts/version-evolution.md` (1C), `docs/extracts/standards-timeline.md` (1F), `docs/extracts/git-history-analysis.md` (1G), `docs/extracts/security-cve-history.md` (1H)
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

### 2B. Protocol Deep-Dive Chapters (security-compliance:security-auditor)
**Input:** Extracts from 1B, 1F
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

### 2C. Component Relevance Analysis (comprehensive-review:architect-review)
**Input:** Extracts from 1D, 1E
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

### 2D. Modern Architecture Patterns (backend-api-security:backend-architect)
**Input:** Extracts from 1E, 1F
**Task:** Write chapter on how IAM architecture has shifted:
- Monolithic IAM suite → decomposed microservices
- On-prem LDAP → cloud-native identity stores
- SAML federation → OIDC federation
- Policy agents → API gateways + sidecar proxies
- Provisioning connectors → SCIM + event-driven sync
- Session cookies → stateless JWT → token binding
- Password-based auth → Passwordless/Passkeys (FIDO2, platform authenticators, conditional UI, phishing-resistant MFA)
- Perimeter security → Zero Trust architecture (phishing-resistant auth as prerequisite)
- Human identity → machine identity (SPIFFE/SPIRE, workload identity)
- AI and identity: adaptive auth, behavioral biometrics, LLM-powered policy
**Output:** `docs/chapters/12-modern-architecture.md`

### 2E. Comparison Matrix (general-purpose agent)
**Input:** Extracts from 1E, analysis from 2C
**Task:** Build detailed feature comparison tables:
- Access Management: OpenAM vs Keycloak vs Auth0 vs Okta vs Cognito vs Ory vs Zitadel vs Authentik vs Casdoor vs Logto vs SuperTokens vs Hanko
- Directory: OpenDJ vs 389 DS vs FreeIPA vs Azure AD vs AWS Directory Service
- Provisioning: OpenIDM vs SailPoint vs Saviynt vs SCIM-native
- Gateway: OpenIG vs Kong vs Envoy/Istio vs AWS API Gateway
- Connectors: OpenICF vs SCIM vs native integrations

Tables should cover: auth protocols, MFA support, federation, self-service, scalability, deployment model, license, community activity, enterprise support
**Output:** `docs/chapters/13-comparison-matrices.md`

### 2F. Pre-Computer Authentication — Lessons from History (general-purpose agent — WebSearch)
**Input:** WebSearch for historical authentication, ancient security mechanisms, academic papers
**Task:** Write a chapter grounding modern IAM in 5,000 years of human trust mechanisms. Research with real historical data, citations, and primary source references.

**Historical trust mechanisms to research (with real examples and dates):**
- Mesopotamian cylinder seals (~3000 BC) → digital signatures, non-repudiation
- Roman tessera hospitalis (guest tokens) → bearer tokens, hardware tokens
- Shibboleth (Book of Judges 12:5-6) → knowledge-based auth, CAPTCHAs
- Wax seals & signet rings (medieval) → message integrity, private keys, HSMs
- Guild master marks & apprentice progression (12th–16th century) → RBAC, graduated access
- Royal letters of introduction / safe-conduct passes → federation, SAML assertions, delegated trust
- Military challenge-response watchwords → CRAM, SCRAM protocols
- Split-key banking vaults (Renaissance) → Shamir's Secret Sharing, MPC, threshold crypto
- Merchant reputation networks along Silk Road / Hanseatic League → web of trust, decentralized identity
- Secret society multi-step rituals (Freemasons, etc.) → multi-factor auth
- Diplomatic pouches (Vienna Convention 1961, but practice far older) → E2E encryption, secure enclaves

**Identify patterns that were NEVER translated to digital IAM:**

| Historical pattern | Why it's underused digitally | Opportunity |
|--------------------|------------------------------|-------------|
| Progressive trust (guild model) | Modern RBAC grants full role access instantly | Time-based + competence-based access escalation |
| Community attestation / vouching | Decentralized identity (DID) hasn't cracked usability | Social trust graphs for authorization |
| Physical proximity as trust | BLE/NFC auth exists but isn't a standard IAM factor | Proximity as continuous auth signal |
| Ritual as multi-party authorization | Threshold crypto exists but no IAM system uses it natively | N-of-M approval workflows beyond simple manager approval |
| Reputation decay over absence | Tokens expire but don't model trust erosion over inactivity | Continuous trust scoring that degrades without reinforcement |
| Lineage/provenance chains | Verifiable Credentials (W3C) emerging but early | Identity chains that prove delegation history |

**Requirements:**
- Every historical claim must cite a real source (book, paper, archaeological record, primary text)
- Map each mechanism to its closest modern IAM equivalent with specificity (not just "like MFA")
- For the "untranslated patterns" — research whether any academic papers, patents, or experimental systems have attempted them
- Conclude with: which forgotten patterns could solve problems modern IAM still struggles with (identity proofing, trust calibration, progressive authorization, decentralized trust)?

**Output:** `docs/chapters/14-lessons-from-history.md`

---

## Phase 3: Assembly & Presentation (sequential)

### 3A. Executive Summary & Index
**Task:** Write the master `docs/README.md` with:
- Executive summary (1-2 pages for leadership)
- Document structure and navigation
- Key findings and recommendations
- Reading guide for different audiences

### 3B. Slide Deck (document-skills:pptx)
**Task:** Create executive slide deck (~20-25 slides):
1. Title: "Identity & Access Management: Evolution, Architecture & Modern Landscape"
2. Timeline visualization (Sun → ForgeRock → OIP/Wren)
3. The 5 components and how they fit
4. Protocol evolution (1 slide per family)
5. Each component vs modern alternatives (5 slides)
6. Architecture shift: then vs now
7. Decision framework: when to use what
8. Recommendations

---

## Agent-to-Task Mapping

| Phase | Task | Agent Type | Parallelizable |
|-------|------|-----------|----------------|
| 1A | PDF extraction | Bash (uv run python) | Yes |
| 1B | Protocol inventory | Explore | Yes |
| 1C | Version evolution diff | Explore | Yes |
| 1D | Architecture extraction | Explore | Yes |
| 1E | Modern landscape research | general-purpose (WebSearch) | Yes |
| 1F | Standards timeline | general-purpose (WebSearch) | Yes |
| 1G | Git history analysis | Bash (git commands, parallel per repo) | Yes |
| 1H | Security/CVE history | general-purpose (WebSearch) + Bash (git grep) | Yes |
| 2A | Historical narrative | documentation-generation:docs-architect | Yes |
| 2B | Protocol deep-dives | security-compliance:security-auditor | Yes |
| 2C | Component relevance | comprehensive-review:architect-review | Yes |
| 2D | Modern architecture | backend-api-security:backend-architect | Yes |
| 2E | Comparison matrices | general-purpose | Yes |
| 2F | Pre-computer auth history | general-purpose (WebSearch) | Yes |
| 3A | Executive summary | Main agent (me) | Sequential |
| 3B | Slide deck | document-skills:pptx skill | Sequential |

**Max parallel agents per phase:**
- Phase 1: 8 agents (1A is Bash/Python, 1B-1D are Explore, 1E-1F are general-purpose, 1G is Bash/git, 1H is general-purpose+Bash)
- Phase 2: 6 agents (all different specialized types)
- Phase 3: Sequential (depends on Phase 2 outputs)

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
│   │   └── idm/{version}/*.md
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
│   └── security-cve-history.md
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
# 1. File existence — every expected output must exist
for f in docs/chapters/{01..13}-*.md docs/extracts/*.md docs/README.md; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done

# 2. Minimum content — no stub files (each chapter ≥100 lines, each extract ≥50 lines)
for f in docs/chapters/*.md; do
  lines=$(wc -l < "$f")
  [ "$lines" -ge 100 ] && echo "OK: $f ($lines lines)" || echo "SHORT: $f ($lines lines)"
done
for f in docs/extracts/*.md; do
  lines=$(wc -l < "$f")
  [ "$lines" -ge 50 ] && echo "OK: $f ($lines lines)" || echo "SHORT: $f ($lines lines)"
done

# 3. Cross-reference validation — check markdown links between chapters resolve
grep -roh '\](\.\.\/[^)]*\.md)' docs/chapters/ | sort -u | while read link; do
  target="docs/chapters/${link#](../}"
  target="${target%)}"
  [ -f "$target" ] && echo "OK: $target" || echo "BROKEN LINK: $target"
done

# 4. Comparison matrix completeness — verify all products appear
for product in OpenAM Keycloak Auth0 Okta Cognito Ory Zitadel Authentik Casdoor Logto SuperTokens Hanko; do
  grep -q "$product" docs/chapters/13-comparison-matrices.md && echo "OK: $product" || echo "MISSING: $product"
done

# 5. Code file references — spot-check that referenced source files exist
grep -oP '`[A-Za-z/._-]+\.java`' docs/chapters/*.md | while IFS=: read chapter ref; do
  file="${ref//\`/}"
  [ -f "$file" ] && echo "OK: $file" || echo "INVALID REF: $file in $chapter"
done
```

### Manual review checklist
1. Executive summary (`docs/README.md`) is coherent and serves both audiences
2. Historical narrative (Ch.01) includes git-derived milestones and CVE timeline
3. Passwordless/passkeys covered substantively in Ch.02 and Ch.12
4. Slide deck has ~20-25 slides with key visuals
5. Each Phase 1 extract has an Executive Summary section (≤50 lines)
6. Topic cross-reference indexes (pdf-index-*.md) correctly point to Tier 1 extracts
