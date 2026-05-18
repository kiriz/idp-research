import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://kiriz.github.io",
  base: "/idp-research",
  integrations: [
    starlight({
      title: "IAM Deep Dive",
      description:
        "20 years of open-source identity management: Sun OpenSSO to ForgeRock to the modern IAM landscape. Source analysis of 7 repos, 58K+ commits, 40+ protocols.",
      customCss: ["./src/styles/custom.css"],

      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/kiriz/idp-research",
        },
      ],
      head: [
        {
          tag: "script",
          attrs: { type: "module" },
          content: `
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'loose' });
document.addEventListener('DOMContentLoaded', async () => {
  const blocks = document.querySelectorAll('pre > code.language-mermaid');
  for (const code of blocks) {
    const pre = code.parentElement;
    const definition = code.textContent;
    const id = 'mermaid-' + Math.random().toString(36).slice(2);
    const div = document.createElement('div');
    div.className = 'mermaid-diagram';
    div.style.cssText = 'overflow-x:auto;margin:1.5rem 0;';
    try {
      const { svg } = await mermaid.render(id, definition);
      div.innerHTML = svg;
    } catch(e) {
      div.textContent = 'Diagram error: ' + e.message;
    }
    pre.replaceWith(div);
  }
});
`,
        },
      ],
      sidebar: [
        { label: "Overview", autogenerate: { directory: "history" } },
        { label: "Protocol Deep Dives", autogenerate: { directory: "protocols" } },
        { label: "OpenAM Lineage", autogenerate: { directory: "openam-lineage" } },
        { label: "Modern Landscape", autogenerate: { directory: "modern-landscape" } },
        { label: "Decision Guide", autogenerate: { directory: "decision-guide" } },
        { label: "Reference Data", autogenerate: { directory: "reference" } },
        { label: "Future of Auth", autogenerate: { directory: "future-of-auth" } },
      ],
    }),
  ],
});
