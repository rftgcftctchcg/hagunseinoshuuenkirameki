export type Lang = "ja" | "zh" | "en";

export const BASE = import.meta.env.BASE_URL.endsWith("/")
  ? import.meta.env.BASE_URL
  : `${import.meta.env.BASE_URL}/`;

export const SITE_ORIGIN = "https://rftgcftctchcg.github.io";
export const SITE_BASE = "/hagunseinoshuuenkirameki/";

export function homePath(lang: Lang): string {
  return lang === "ja" ? BASE : `${BASE}${lang}/`;
}

export function workPath(lang: Lang, bv: string): string {
  return `${homePath(lang)}works/${bv}/`;
}

export function assetPath(path: string): string {
  return `${BASE}${path.replace(/^\/+/, "")}`;
}

export function sectionHref(lang: Lang, id: string): string {
  return `${homePath(lang)}#${id}`;
}

export function absoluteUrl(path = ""): string {
  return new URL(path.replace(/^\/+/, ""), `${SITE_ORIGIN}${SITE_BASE}`).href;
}

export function langFromPath(pathname: string): Lang {
  if (pathname.includes("/zh/")) return "zh";
  if (pathname.includes("/en/")) return "en";
  return "ja";
}
