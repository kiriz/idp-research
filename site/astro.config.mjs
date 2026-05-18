import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// Remark plugin: convert ```mermaid blocks to <div class="mermaid"> BEFORE
// expressive-code processes them. expressive-code restructures code block DOM
// so a client-side querySelector('code.language-mermaid') never finds anything.
// Transforming to raw HTML at the remark phase sidesteps this entirely.
function remarkMermaid() {
  return function (tree) {
    function walk(node, parent, index) {
      if (node.type === "code" && node.lang === "mermaid") {
        parent.children[index] = {
          type: "html",
          value: `<div class="mermaid">\n${node.value}\n</div>`,
        };
        return;
      }
      if (Array.isArray(node.children)) {
        node.children.forEach((child, i) => walk(child, node, i));
      }
    }
    if (tree.children) tree.children.forEach((child, i) => walk(child, tree, i));
  };
}

export default defineConfig({
  site: "https://kiriz.github.io",
  base: "/idp-research",
  markdown: {
    remarkPlugins: [remarkMermaid],
  },
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
        // Inter + JetBrains Mono from Google Fonts
        {
          tag: "link",
          attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" },
        },
        {
          tag: "link",
          attrs: { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" },
        },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
          },
        },
        // Mermaid: diagrams are already <div class="mermaid"> via remarkMermaid plugin
        {
          tag: "script",
          attrs: { type: "module" },
          content: `
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({ startOnLoad: true, theme: 'neutral', securityLevel: 'loose' });
`,
        },
        // Sidebar collapse toggle buttons
        {
          tag: "script",
          content: `
(function() {
  var html = document.documentElement;

  // Restore saved state before first paint
  if (localStorage.getItem('sl-hide-left')  === '1') html.classList.add('sl-hide-left');
  if (localStorage.getItem('sl-hide-right') === '1') html.classList.add('sl-hide-right');

  function makeToggle(id, label, title, cls, key) {
    var btn = document.createElement('button');
    btn.id = id;
    btn.className = 'sl-panel-toggle';
    btn.title = title;
    btn.textContent = label;
    btn.addEventListener('click', function() {
      html.classList.toggle(cls);
      localStorage.setItem(key, html.classList.contains(cls) ? '1' : '0');
    });
    return btn;
  }

  document.addEventListener('DOMContentLoaded', function() {
    document.body.appendChild(
      makeToggle('sl-toggle-left',  '☰', 'Toggle navigation sidebar',    'sl-hide-left',  'sl-hide-left')
    );
    document.body.appendChild(
      makeToggle('sl-toggle-right', '≡', 'Toggle table of contents',      'sl-hide-right', 'sl-hide-right')
    );
  });
})();
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
