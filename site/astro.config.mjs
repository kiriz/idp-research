import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://kiriz.github.io",
  base: "/idp-research",
  integrations: [
    starlight({
      title: "IAM Deep Dive",
      description:
        "20 years of open-source identity management: Sun OpenSSO to ForgeRock to the modern IAM landscape. Source analysis of 7 repos, 250K+ commits, 40+ protocols.",
      customCss: ["./src/styles/custom.css"],

      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/kiriz/idp-research",
        },
      ],
      sidebar: [
        { label: "Overview", autogenerate: { directory: "history" } },
        { label: "Protocol Deep Dives", autogenerate: { directory: "protocols" } },
        { label: "OpenAM Lineage", autogenerate: { directory: "openam-lineage" } },
        { label: "Modern Landscape", autogenerate: { directory: "modern-landscape" } },
        { label: "Decision Guide", autogenerate: { directory: "decision-guide" } },
        { label: "Reference Data", autogenerate: { directory: "reference" } },
      ],
    }),
  ],
});
