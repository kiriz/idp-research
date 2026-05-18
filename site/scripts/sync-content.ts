#!/usr/bin/env bun
/**
 * sync-content.ts
 * Copies/syncs source chapters from ../docs/ into src/content/docs/.
 * Run: bun run sync
 *
 * The site content files have frontmatter prepended; only the body (after
 * the first blank line past the chapter's own H1) is synced. This script
 * does a full overwrite — it is safe to run repeatedly.
 */

import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const ROOT = join(fileURLToPath(import.meta.url), "../../..");
const DOCS = join(ROOT, "docs");
const SITE_CONTENT = join(ROOT, "site/src/content/docs");

interface ContentMapping {
  src: string;          // relative to docs/
  dest: string;         // relative to site/src/content/docs/
  title: string;
  description: string;
  sidebarOrder: number;
}

const mappings: ContentMapping[] = [
  {
    src: "chapters/02-authentication-protocols.md",
    dest: "protocols/authentication.md",
    title: "Authentication Protocols",
    description: "LDAP, Kerberos, SAML, OAuth, OIDC, FIDO2 — complete analysis of 40+ authentication standards from 1993 to passkeys.",
    sidebarOrder: 2,
  },
  {
    src: "chapters/03-federation-protocols.md",
    dest: "protocols/federation.md",
    title: "Federation Protocols",
    description: "SAML 2.0, WS-Federation, OpenID Connect — how cross-domain identity works.",
    sidebarOrder: 3,
  },
  {
    src: "chapters/04-authorization-frameworks.md",
    dest: "protocols/authorization.md",
    title: "Authorization Frameworks",
    description: "XACML, OAuth scopes, OPA/Rego, Cedar — policy-based access control evolution.",
    sidebarOrder: 4,
  },
  {
    src: "chapters/05-directory-services.md",
    dest: "protocols/directory.md",
    title: "Directory Services",
    description: "LDAPv3, OpenDJ, 389 DS — the future of directory services.",
    sidebarOrder: 5,
  },
  {
    src: "chapters/06-token-formats.md",
    dest: "protocols/tokens.md",
    title: "Token Formats & Sessions",
    description: "JWT, SAML assertions, PASETO — 30 years of identity token evolution.",
    sidebarOrder: 6,
  },
  {
    src: "chapters/07-openam-analysis.md",
    dest: "openam-lineage/openam.md",
    title: "OpenAM Analysis",
    description: "Architecture, modules, CVEs — deep analysis of OIP's OpenAM fork.",
    sidebarOrder: 2,
  },
  {
    src: "chapters/08-opendj-analysis.md",
    dest: "openam-lineage/opendj.md",
    title: "OpenDJ Analysis",
    description: "LDAPv3 directory server: replication, REST gateway, reactive client.",
    sidebarOrder: 3,
  },
  {
    src: "chapters/09-openidm-analysis.md",
    dest: "openam-lineage/openidm.md",
    title: "OpenIDM Analysis",
    description: "Identity governance: OSGi provisioning engine, workflow integration.",
    sidebarOrder: 4,
  },
  {
    src: "chapters/10-openig-analysis.md",
    dest: "openam-lineage/openig.md",
    title: "OpenIG Analysis",
    description: "Identity gateway with credential replay — the capability with no modern equivalent.",
    sidebarOrder: 5,
  },
  {
    src: "chapters/11-openicf-analysis.md",
    dest: "openam-lineage/openicf.md",
    title: "OpenICF Analysis",
    description: "Identity connector framework: 50+ connectors for LDAP, AD, databases, SaaS.",
    sidebarOrder: 6,
  },
  {
    src: "chapters/13-comparison-matrices.md",
    dest: "decision-guide/comparison.md",
    title: "Platform Comparison Matrices",
    description: "8 comparison matrices across the IAM platform landscape.",
    sidebarOrder: 1,
  },
  {
    src: "extracts/protocol-inventory.md",
    dest: "reference/protocols.md",
    title: "Protocol Inventory (40+ Protocols)",
    description: "Complete inventory of all protocols across the 7 OpenAM-lineage repositories.",
    sidebarOrder: 1,
  },
  {
    src: "extracts/security-cve-history.md",
    dest: "reference/cve-history.md",
    title: "CVE History & Patch Matrix",
    description: "30+ CVEs — full timeline, CVSS scores, and patch status per fork.",
    sidebarOrder: 2,
  },
  {
    src: "extracts/git-history-analysis.md",
    dest: "reference/git-analysis.md",
    title: "Git History Analysis",
    description: "Commit velocity, contributors, and release timeline across 7 repositories.",
    sidebarOrder: 3,
  },
  {
    src: "extracts/pre-computer-auth-research.md",
    dest: "reference/pre-computer.md",
    title: "Pre-Computer Authentication History",
    description: "5,000 years of authentication patterns — cylinder seals to Cold War tradecraft.",
    sidebarOrder: 4,
  },
];

function buildFrontmatter(m: ContentMapping): string {
  return `---\ntitle: ${m.title}\ndescription: ${m.description}\nsidebar:\n  order: ${m.sidebarOrder}\n---\n\n`;
}

let synced = 0;
let skipped = 0;

for (const m of mappings) {
  const srcPath = join(DOCS, m.src);
  const destPath = join(SITE_CONTENT, m.dest);

  let body: string;
  try {
    body = readFileSync(srcPath, "utf-8");
  } catch {
    console.warn(`  SKIP (not found): ${m.src}`);
    skipped++;
    continue;
  }

  mkdirSync(dirname(destPath), { recursive: true });
  const content = buildFrontmatter(m) + body;
  writeFileSync(destPath, content, "utf-8");
  console.log(`  synced: ${m.src} → ${m.dest} (${body.split("\n").length} lines)`);
  synced++;
}

console.log(`\nDone: ${synced} synced, ${skipped} skipped.`);
