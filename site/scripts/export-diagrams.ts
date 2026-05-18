#!/usr/bin/env bun
/**
 * export-diagrams.ts
 * Exports Excalidraw diagrams to SVG using @excalidraw/utils.
 * Run: bun run diagrams
 *
 * Note: @excalidraw/utils requires a DOM environment. If running in bun
 * without DOM shims, it will log a warning and skip to the fallback.
 *
 * Fallback: writes placeholder SVG files so the build doesn't break.
 * Replace with real SVGs by exporting from https://excalidraw.com manually
 * and dropping the SVG files into public/diagrams/.
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from "fs";
import { join, basename } from "path";
import { fileURLToPath } from "url";

const ROOT = join(fileURLToPath(import.meta.url), "../../..");
const SOURCE_DIR = join(ROOT, "docs/diagrams");
const OUTPUT_DIR = join(ROOT, "site/public/diagrams");

mkdirSync(OUTPUT_DIR, { recursive: true });

const diagramFiles = readdirSync(SOURCE_DIR).filter((f) => f.endsWith(".excalidraw"));
console.log(`Found ${diagramFiles.length} Excalidraw diagrams`);

// Attempt @excalidraw/utils export (requires DOM)
let useExcalidraw = false;
let exportToSvg: ((scene: object, opts?: object) => Promise<SVGSVGElement>) | undefined;

try {
  const mod = await import("@excalidraw/utils");
  exportToSvg = mod.exportToSvg as typeof exportToSvg;
  useExcalidraw = true;
  console.log("@excalidraw/utils loaded — using native SVG export");
} catch {
  console.warn(
    "Warning: @excalidraw/utils not available (expected in bun without DOM shims).\n" +
    "Falling back to placeholder SVGs. To get real exports:\n" +
    "  1. Open https://excalidraw.com\n" +
    "  2. Load each .excalidraw file from docs/diagrams/\n" +
    "  3. Export as SVG to site/public/diagrams/<name>.svg"
  );
}

for (const file of diagramFiles) {
  const srcPath = join(SOURCE_DIR, file);
  const name = basename(file, ".excalidraw");
  const destPath = join(OUTPUT_DIR, `${name}.svg`);

  // Skip if real SVG already exists (don't overwrite manual exports)
  if (existsSync(destPath)) {
    const existing = readFileSync(destPath, "utf-8");
    if (!existing.includes("placeholder")) {
      console.log(`  skip (real SVG exists): ${name}.svg`);
      continue;
    }
  }

  if (useExcalidraw && exportToSvg) {
    try {
      const scene = JSON.parse(readFileSync(srcPath, "utf-8")) as {
        elements: object[];
        appState?: object;
        files?: object;
      };
      const svgEl = await exportToSvg({
        elements: scene.elements,
        appState: { ...(scene.appState ?? {}), exportWithDarkMode: false },
        files: scene.files ?? {},
      });
      // svgEl is an SVGSVGElement — serialize it
      const { XMLSerializer } = await import("xmldom" as string) as { XMLSerializer: new () => { serializeToString(node: object): string } };
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(svgEl as unknown as object);
      writeFileSync(destPath, svgString, "utf-8");
      console.log(`  exported: ${name}.svg`);
      continue;
    } catch (e) {
      console.warn(`  warn: export failed for ${name}: ${e}`);
    }
  }

  // Placeholder SVG — visually communicates the diagram exists but needs manual export
  const placeholder = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <!-- placeholder: ${name} -->
  <rect width="800" height="200" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2" rx="8"/>
  <text x="400" y="85" font-family="system-ui, sans-serif" font-size="16" fill="#64748b" text-anchor="middle" font-weight="600">${name}</text>
  <text x="400" y="115" font-family="system-ui, sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">Excalidraw diagram — export manually from docs/diagrams/${file}</text>
  <text x="400" y="140" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">Open excalidraw.com, load the file, export as SVG to site/public/diagrams/${name}.svg</text>
</svg>`;

  writeFileSync(destPath, placeholder, "utf-8");
  console.log(`  placeholder: ${name}.svg`);
}

console.log(`\nDone. SVGs written to: ${OUTPUT_DIR}`);
console.log("Run 'bun run diagrams' again after installing @excalidraw/utils to get real exports.");
