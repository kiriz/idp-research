---
task: "Build Astro Starlight IAM education site GitHub Pages"
slug: 20260518-iam-education-site
project: iam-education-site
effort: E4
effort_source: context-override
phase: observe
progress: 0/128
mode: interactive
started: 2026-05-18T00:00:00Z
updated: 2026-05-18T00:00:00Z
---

## Problem

The IAM deep-research archive at `~/projects/idp/docs/` (20K+ lines, 16 chapters, 8 extracts, 17 Excalidraw diagrams) is not publicly accessible or navigable. It exists as raw markdown files in a local directory — no structure, no search, no visual hierarchy, no way to share with colleagues. The most compelling story in the data (the ForgeRock closure cliff, 94% commit-velocity drop in a single year) is buried in a table. Technical education content of this depth deserves a surface that matches its quality.

## Vision

A reader arrives from a Google search for "ForgeRock OpenAM history" or "LDAP vs OAuth evolution." Within 30 seconds they understand: this is a comprehensive, primary-source analysis of 20 years of IAM open-source history. They see an interactive chart showing the ForgeRock closure moment viscerally — a cliff edge in commit velocity — annotated with context. They can follow their entry path: 30 minutes for the leadership summary, 2 hours for the security architect deep-dive. The CVE risk matrix answers "is ForgeRock CE safe to run?" instantly with color-coded evidence. The site is the kind of thing people bookmark, share in Slack, and reference in architecture discussions.

## Out of Scope

Not a product, not a SaaS, not a CI/CD pipeline for the research itself. No server-side code, no database, no authentication layer. No mobile native app. No CMS or visual editor — engineers update markdown files directly. No i18n. No comments or community features. The 683-page PDF and PPTX deck are not embedded (too large) but may be linked. Version 1 does not include full-text search beyond Starlight's built-in pagefind.

## Principles

- The data is the hero: structure serves comprehension, not decoration.
- Progressive disclosure: every page is readable without JS; interactive components add, not replace.
- One source of truth: the `docs/` folder is the authoritative research; the site is its presentation layer. A sync script keeps them connected.
- Build with the grain: Starlight handles navigation, search, dark mode — only customize where the defaults don't serve the content.
- Easy to maintain: a non-engineer who can edit markdown can update every content page.
- Bun-first: all scripts and package management use bun, never npm/npx.

## Constraints

- Framework: Astro + Starlight. Not negotiable.
- Package manager: bun. No npm/npx. Zero exceptions.
- Language: TypeScript for all scripts and components. No Python in build pipeline.
- Hosting: GitHub Pages (static). No server-side execution.
- Interactive charts: data hardcoded from research extracts. No external API calls at build or runtime.
- GitHub Actions: use only `GITHUB_TOKEN` — no additional secrets required.
- Excalidraw export: programmatic via `@excalidraw/utils` in a bun script. No manual web app export.
- Content copyright: all research is original analysis; source repos are Apache 2.0 and MIT.

## Goal

Build a production-ready Astro + Starlight site at `~/projects/idp/site/` that presents the IAM deep-research archive as a navigable technical education resource, with three interactive visualizations, all 17 Excalidraw diagrams exported to SVG, organized into a semantic six-section nav, deployable to GitHub Pages via a single GitHub Actions push.

## Criteria

### Site Scaffold & Config
- [ ] ISC-1: `~/projects/idp/site/` directory exists and is not empty
- [ ] ISC-2: `site/package.json` exists with `astro` and `@astrojs/starlight` in dependencies
- [ ] ISC-3: `site/astro.config.mjs` exists and imports `starlight` from `@astrojs/starlight`
- [ ] ISC-4: `site/tsconfig.json` exists and extends `astro/tsconfigs/strict`
- [ ] ISC-5: `bun run build` completes with exit code 0 from `site/` directory
- [ ] ISC-6: `bun run dev` starts a dev server (port 4321 default)
- [ ] ISC-7: `site/.gitignore` excludes `dist/`, `node_modules/`, `.astro/`

### GitHub Pages Deployment
- [ ] ISC-8: `.github/workflows/deploy.yml` exists at `idp/` repo root
- [ ] ISC-9: `deploy.yml` triggers on `push` to `main` branch
- [ ] ISC-10: `deploy.yml` uses `bun run build` (not npm)
- [ ] ISC-11: `deploy.yml` deploys built `site/dist/` to `gh-pages` branch via `peaceiris/actions-gh-pages` or equivalent
- [ ] ISC-12: `astro.config.mjs` `base` option is set to the repo name `/idp-research`
- [ ] ISC-13: `astro.config.mjs` `site` URL is set to `https://kiriz.github.io`

### Excalidraw SVG Export Script
- [ ] ISC-14: `site/scripts/export-diagrams.ts` exists
- [ ] ISC-15: Script imports `@excalidraw/utils` for SVG export
- [ ] ISC-16: Script reads all `.excalidraw` files from `../docs/diagrams/`
- [ ] ISC-17: Script writes SVG output to `site/public/diagrams/`
- [ ] ISC-18: `package.json` has a `diagrams` script: `bun run scripts/export-diagrams.ts`
- [ ] ISC-19: Script handles the 17 diagram files without crashing on any

### Content Structure — File Existence
- [ ] ISC-20: `src/content/docs/index.mdx` exists (landing page)
- [ ] ISC-21: `src/content/docs/history/index.md` exists
- [ ] ISC-22: `src/content/docs/protocols/authentication.md` exists
- [ ] ISC-23: `src/content/docs/protocols/federation.md` exists
- [ ] ISC-24: `src/content/docs/protocols/authorization.md` exists
- [ ] ISC-25: `src/content/docs/protocols/directory.md` exists
- [ ] ISC-26: `src/content/docs/protocols/tokens.md` exists
- [ ] ISC-27: `src/content/docs/openam-lineage/index.md` exists
- [ ] ISC-28: `src/content/docs/openam-lineage/openam.md` exists
- [ ] ISC-29: `src/content/docs/openam-lineage/opendj.md` exists
- [ ] ISC-30: `src/content/docs/openam-lineage/openidm.md` exists
- [ ] ISC-31: `src/content/docs/openam-lineage/openig.md` exists
- [ ] ISC-32: `src/content/docs/openam-lineage/openicf.md` exists
- [ ] ISC-33: `src/content/docs/modern-landscape/index.md` exists
- [ ] ISC-34: `src/content/docs/decision-guide/comparison.md` exists
- [ ] ISC-35: `src/content/docs/decision-guide/migration.md` exists
- [ ] ISC-36: `src/content/docs/decision-guide/lessons.md` exists
- [ ] ISC-37: `src/content/docs/reference/protocols.md` exists
- [ ] ISC-38: `src/content/docs/reference/cve-history.md` exists
- [ ] ISC-39: `src/content/docs/reference/git-analysis.md` exists
- [ ] ISC-40: `src/content/docs/reference/pre-computer.md` exists

### Landing Page Quality
- [ ] ISC-41: Landing page includes all 6 key findings from research README executive summary
- [ ] ISC-42: Landing page has "For leadership (30 min)" reading path callout box
- [ ] ISC-43: Landing page has "For security architects (2 hrs)" reading path callout box
- [ ] ISC-44: Landing page hero includes key stats (7 repos, 250K+ commits, 20-year timeline)
- [ ] ISC-45: Landing page has navigation links to each of the 6 major sections
- [ ] ISC-46: Antecedent: landing page hero section immediately signals "this is comprehensive primary-source research" on first glance without reading body text

### Navigation (Starlight Sidebar)
- [ ] ISC-47: Sidebar has "Overview" group containing at minimum history and landing links
- [ ] ISC-48: Sidebar has "Protocols" group with 5 items (auth, federation, authz, directory, tokens)
- [ ] ISC-49: Sidebar has "OpenAM Lineage" group with 6 items (index + 5 component analyses)
- [ ] ISC-50: Sidebar has "Modern Landscape" group
- [ ] ISC-51: Sidebar has "Decision Guide" group with 3 items
- [ ] ISC-52: Sidebar has "Reference Data" group with 4 items
- [ ] ISC-53: `astro.config.mjs` sidebar array reflects all 6 groups with correct slugs

### Commit Velocity Chart Component
- [ ] ISC-54: `src/components/CommitVelocityChart.astro` exists
- [ ] ISC-55: Component uses Chart.js (loaded via `client:load` island directive)
- [ ] ISC-56: Component renders a multi-line chart with years 2006–2025 on X-axis
- [ ] ISC-57: Component has distinct lines for OpenAM, OpenDJ, OpenIDM, Wren:AM, ForgeRock CE, OpenIG, OpenICF
- [ ] ISC-58: Chart has a "Total" reference line or annotation
- [ ] ISC-59: Chart has an annotation or vertical line marking 2016–2017 ForgeRock closure
- [ ] ISC-60: Chart has an annotation marking 2014 as the peak year (10,744 total commits)
- [ ] ISC-61: Component is embedded in `history/index.md` via MDX import or Astro component tag
- [ ] ISC-62: Component data arrays contain the actual numbers from git-history-analysis.md table
- [ ] ISC-63: Chart renders without console errors in browser (verified via build output or Interceptor)

### Protocol Evolution Timeline Component
- [ ] ISC-64: `src/components/ProtocolTimeline.astro` exists
- [ ] ISC-65: Component renders a CSS-driven or Chart.js timeline (no external deps beyond what's already used)
- [ ] ISC-66: Timeline includes ≥8 standards: LDAP (1993), Kerberos (1993), SAML 2.0 (2005), OAuth 2.0 (2012), OIDC (2014), FIDO2/WebAuthn (2019), Passkeys (2022), Zero Trust (NIST SP 800-207, 2020)
- [ ] ISC-67: Each entry shows year, protocol/standard name, and a one-sentence description
- [ ] ISC-68: Timeline visually groups entries into eras (e.g., "Directory Era", "Federation Era", "Modern Era")
- [ ] ISC-69: Component is embedded in `history/index.md` or `protocols/authentication.md`
- [ ] ISC-70: Timeline layout is readable at 375px viewport width

### CVE Risk Matrix Component
- [ ] ISC-71: `src/components/CVERiskMatrix.astro` exists
- [ ] ISC-72: Component renders an HTML table with CVE IDs in rows
- [ ] ISC-73: Table has 3 fork columns: ForgeRock CE, OIP OpenAM, Wren:AM
- [ ] ISC-74: Cells for unpatched critical CVEs in ForgeRock CE use a danger/red CSS class
- [ ] ISC-75: Patched cells use a success/green CSS class
- [ ] ISC-76: Unknown/partial cells use a warning/yellow CSS class
- [ ] ISC-77: Component data covers ≥10 CVEs from the patch matrix (cve-history.md)
- [ ] ISC-78: Each CVE row includes the CVSS score and a short description
- [ ] ISC-79: Component is embedded in `reference/cve-history.md`
- [ ] ISC-80: Component includes a legend below the table explaining color/icon meaning
- [ ] ISC-81: Color coding is not the only signal — text labels ("Unpatched", "Patched") are also present

### Diagram Embedding
- [ ] ISC-82: `public/diagrams/` directory exists (even if manually populated pending export script)
- [ ] ISC-83: At least one SVG placeholder or real SVG exists for `04-historical-timeline`
- [ ] ISC-84: `history/index.md` references a diagram SVG via `<img>` or `![]()` syntax
- [ ] ISC-85: `openam-lineage/index.md` references `06-fork-divergence` diagram
- [ ] ISC-86: `decision-guide/migration.md` references `14-iam-decision-tree` diagram
- [ ] ISC-87: All embedded diagram `<img>` tags have non-empty `alt` text

### Custom Styling
- [ ] ISC-88: `src/styles/custom.css` exists
- [ ] ISC-89: `astro.config.mjs` `customCss` array includes `./src/styles/custom.css`
- [ ] ISC-90: Site title in `astro.config.mjs` is set to "IAM Deep Dive" or equivalent descriptive title
- [ ] ISC-91: Custom CSS defines color tokens for the CVE matrix (danger, warning, success)

### Content Frontmatter Quality
- [ ] ISC-92: Every content `.md`/`.mdx` file has a `title:` frontmatter field
- [ ] ISC-93: Every content file has a `description:` frontmatter field (≥10 words)
- [ ] ISC-94: Sidebar ordering uses `sidebar.order` frontmatter on at least the top-level section index files

### Content Completeness
- [ ] ISC-95: `history/index.md` includes the ForgeRock closure narrative and the 6 key findings summary
- [ ] ISC-96: `protocols/authentication.md` body length > 200 lines (not truncated from source chapter)
- [ ] ISC-97: `decision-guide/comparison.md` includes ≥3 comparison tables from ch.13
- [ ] ISC-98: `reference/cve-history.md` includes the full CVE timeline table
- [ ] ISC-99: `reference/git-analysis.md` includes the per-repo summary table and commit velocity table

### Content Sync Script
- [ ] ISC-100: `site/scripts/sync-content.ts` exists
- [ ] ISC-101: Script maps source chapters to destination content paths (explicit mapping object)
- [ ] ISC-102: `package.json` has a `sync` script: `bun run scripts/sync-content.ts`
- [ ] ISC-103: Script copies files and logs each copied path to stdout

### Build Verification
- [ ] ISC-104: `dist/` directory created after `bun run build`
- [ ] ISC-105: `dist/index.html` exists after build
- [ ] ISC-106: `dist/` contains at least 15 HTML files (one per content page)
- [ ] ISC-107: Build output contains no TypeScript type errors

### Anti-criteria
- [ ] ISC-108: Anti: site does NOT require any backend, server process, or database to serve
- [ ] ISC-109: Anti: no `npm` or `npx` commands appear in `package.json` scripts or GitHub Actions workflow
- [ ] ISC-110: Anti: chart components do NOT fetch from any external URL at runtime
- [ ] ISC-111: Anti: GitHub Actions workflow does NOT require secrets beyond the built-in `GITHUB_TOKEN`
- [ ] ISC-112: Anti: landing page does NOT just render a raw dump of a chapter file with no structure
- [ ] ISC-113: Anti: `bun run build` does NOT succeed with broken internal links to non-existent content pages
- [ ] ISC-114: Anti: Excalidraw export script does NOT require opening a browser or the Excalidraw web app
- [ ] ISC-115: Anti: no hardcoded `~` or `/Users/kirane` paths appear in any source file in `site/`

### Antecedent (experiential)
- [ ] ISC-116: Antecedent: the commit velocity chart's ForgeRock closure annotation is visible on the chart without any interaction (not hidden in tooltip only)
- [ ] ISC-117: Antecedent: a reader with no prior context can determine the site's purpose within 10 seconds of landing (hero text + key stats are above the fold)

### Accessibility
- [ ] ISC-118: Interactive chart components include `aria-label` or a `<figcaption>` describing the chart
- [ ] ISC-119: CVE risk matrix table has `<th scope="col">` headers
- [ ] ISC-120: All `<img>` tags for SVG diagrams have descriptive `alt` text (not empty string)

### Git & Repo
- [ ] ISC-121: `site/` directory files are tracked in the `idp-research` git repo
- [ ] ISC-122: Initial commit message references "feat: add Astro Starlight education site"
- [ ] ISC-123: `.gitignore` at `site/` level (or root) excludes `site/dist/` and `site/node_modules/`
- [ ] ISC-124: `.github/workflows/deploy.yml` is committed and present in the repo

### Performance
- [ ] ISC-125: Chart.js script tag is NOT in the global layout — only loaded on pages that use a chart component
- [ ] ISC-126: Built CSS is < 500KB total (no bloated utility framework)
- [ ] ISC-127: Each HTML page in `dist/` is < 300KB uncompressed
- [ ] ISC-128: `bun run build` completes in < 120 seconds

## Test Strategy

| ISC | Type | Check | Threshold | Tool |
|-----|------|-------|-----------|------|
| ISC-1 | filesystem | `ls ~/projects/idp/site/` is non-empty | dir exists | Bash |
| ISC-2 | filesystem | `grep astro site/package.json` | match | Bash/grep |
| ISC-3 | filesystem | `grep starlight site/astro.config.mjs` | match | grep |
| ISC-4 | filesystem | `cat site/tsconfig.json` | file present | Read |
| ISC-5 | build | `cd site && bun run build` exit code | 0 | Bash |
| ISC-7 | filesystem | `grep "dist/" site/.gitignore` | match | grep |
| ISC-8 | filesystem | `ls .github/workflows/deploy.yml` | exists | Bash |
| ISC-12 | content | `grep 'base.*idp-research' site/astro.config.mjs` | match | grep |
| ISC-14 | filesystem | `ls site/scripts/export-diagrams.ts` | exists | Bash |
| ISC-20..40 | filesystem | `ls src/content/docs/**` | all exist | Bash |
| ISC-41..45 | content | `grep "key findings\|30 min\|security architect" src/content/docs/index.mdx` | matches | grep |
| ISC-47..53 | content | `grep "Protocols\|OpenAM\|Decision" site/astro.config.mjs` | matches | grep |
| ISC-54 | filesystem | `ls site/src/components/CommitVelocityChart.astro` | exists | Bash |
| ISC-62 | content | `grep "labels.*2006\|2007\|2008" CommitVelocityChart.astro` | match | grep |
| ISC-71 | filesystem | `ls site/src/components/CVERiskMatrix.astro` | exists | Bash |
| ISC-77 | content | `grep "CVE-2021-35464" CVERiskMatrix.astro` | match | grep |
| ISC-104..107 | build | `bun run build` output analysis | exit 0, no errors | Bash |
| ISC-108..115 | content | grep for `npm\|npx\|fetch(\|/Users/kirane` | 0 matches | grep |
| ISC-121..124 | git | `git status / git log` in idp/ | files tracked | Bash |
| ISC-125 | content | `grep "chart.js" site/src/layouts/` | 0 matches | grep |

## Features

| Name | Description | Satisfies | Depends On | Parallelizable |
|------|-------------|-----------|------------|----------------|
| scaffold | `bunx create-astro` + Starlight install, base config, tsconfig, gitignore | ISC-1..7 | — | false |
| github-pages-deploy | GitHub Actions workflow + astro.config base/site URLs | ISC-8..13, ISC-124 | scaffold | false |
| content-structure | Create all 21 content files with frontmatter + initial content from docs/ | ISC-20..40, ISC-92..99 | scaffold | true |
| landing-page | MDX landing page with hero, key findings, reading paths, stats, section links | ISC-41..46, ISC-112 | scaffold | false |
| nav-config | Starlight sidebar configuration in astro.config.mjs | ISC-47..53 | content-structure | false |
| commit-chart | CommitVelocityChart.astro with Chart.js, real data, ForgeRock annotation | ISC-54..63 | scaffold | true |
| protocol-timeline | ProtocolTimeline.astro with CSS/JS timeline, era grouping | ISC-64..70 | scaffold | true |
| cve-matrix | CVERiskMatrix.astro with colored patch status table | ISC-71..81 | scaffold | true |
| diagram-export | export-diagrams.ts script using @excalidraw/utils | ISC-14..19, ISC-82..87 | scaffold | false |
| custom-styling | custom.css with CVE color tokens, typography tweaks | ISC-88..91 | scaffold | true |
| sync-script | sync-content.ts mapping docs/ chapters to site content | ISC-100..103 | content-structure | false |
| build-verify | Run bun build, check dist/, commit all to git | ISC-104..128 | all | false |

## Decisions

- 2026-05-18: Chose Chart.js over D3 for commit velocity and protocol charts. Chart.js loads faster, requires less custom SVG math for line charts, and Astro island pattern works naturally with it. D3 earns its complexity for force-directed graphs; not needed here.
- 2026-05-18: Chose @excalidraw/utils for programmatic SVG export rather than manual web app export, per the Anti-criterion ISC-114. If @excalidraw/utils proves incompatible with bun, fallback is excalidraw-cli npm package (bunx-compatible).
- 2026-05-18: Content sync strategy: create site content files with initial content from docs/ chapters. A sync-content.ts script allows updating. The site content is the presentation layer; docs/ chapters are the research archive. They can diverge if the site needs editorial cleanup.
- 2026-05-18: GitHub Pages base URL: repo is `github.com/kiriz/idp-research` → `base: "/idp-research"`. Verified from git remote output.

## Changelog

_Empty until LEARN phase._

## Verification

_Empty until VERIFY phase._
