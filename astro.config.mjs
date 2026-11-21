import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://rftgcftctchcg.github.io",
  base: "/hagunseinoshuuenkirameki",
  trailingSlash: "ignore",
  build: { format: "directory" },
  compressHTML: true,
  devToolbar: { enabled: false },
});
