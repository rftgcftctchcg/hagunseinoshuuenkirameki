import worksData from "../../data/works.json";
import statsData from "../../data/stats.json";
import { t } from "../i18n/ui";
import type { Lang } from "../utils/paths";
import { assetPath } from "../utils/paths";

export interface Credit {
  role: string;
  name: string;
  link?: string;
  self?: boolean;
}

export interface Staff {
  mid: number;
  name: string;
  title: string;
  face: string;
}

export interface StatBlock {
  view: number;
  like: number;
  coin: number;
  favorite: number;
  danmaku: number;
  reply: number;
  share: number;
}

export interface Work {
  no: number;
  bvid: string;
  aid: number;
  cid: number;
  title: string;
  desc: string;
  desc_display: string;
  pic: string;
  duration: number;
  length: string;
  pubdate: number;
  created_str: string;
  owner: { mid: number; name: string; face: string };
  staff: Staff[];
  copyright: number;
  stat: StatBlock;
  video_review: number;
  status: string;
  category: string;
  participation: string;
  credits: Credit[];
  featured: boolean;
  featured_order: number | null;
  hidden: boolean;
  tags: string[];
}

export interface SiteStats {
  generated_at: string;
  profile: {
    generated_at: string;
    fans: number | null;
    like_num: number | null;
    archive_count: number | null;
    total_view: number | null;
    total_likes: number | null;
    source: string;
    notes: string[];
  };
  works: {
    count: number;
    sum: StatBlock;
    max_view: { bvid: string; title: string; value: number } | null;
    max_favorite: { bvid: string; title: string; value: number } | null;
    max_interaction: { bvid: string; title: string; value: number } | null;
    earliest: { bvid: string; title: string; created_str: string } | null;
    latest: { bvid: string; title: string; created_str: string } | null;
  };
  categories: Record<string, number>;
  unclassified: number;
}

export const works = [...(worksData as { videos: Work[] }).videos].sort((a, b) => a.no - b.no);
export const siteStats = statsData as SiteStats;

export const CATEGORY_ORDER = ["二创剪辑", "VOCALOID", "原创曲", "搬运", "其他"] as const;

export const CATEGORY_META: Record<
  string,
  { key: string; ja: string; zh: string; en: string }
> = {
  二创剪辑: { key: "fan", ja: "二次創作", zh: "二创剪辑", en: "Fan Edit" },
  VOCALOID: { key: "vocaloid", ja: "VOCALOID", zh: "VOCALOID", en: "VOCALOID" },
  原创曲: { key: "original", ja: "オリジナル", zh: "原创曲", en: "Original" },
  搬运: { key: "repost", ja: "転載", zh: "搬运", en: "Repost" },
  其他: { key: "other", ja: "その他", zh: "其他", en: "Other" },
  未分类: { key: "unclassified", ja: "未分類", zh: "未分类", en: "Uncategorized" },
};

export function categoryLabel(category: string, lang: Lang): string {
  return CATEGORY_META[category]?.[lang] ?? category;
}

export function categoryTabs(lang: Lang): { value: string; label: string; count: number }[] {
  const all = works.length;
  const tabs = [{ value: "ALL", label: t("worksAll", lang), count: all }];
  for (const category of CATEGORY_ORDER) {
    tabs.push({
      value: category,
      label: categoryLabel(category, lang),
      count: works.filter((w) => w.category === category).length,
    });
  }
  const unclassified = works.filter((w) => !CATEGORY_ORDER.includes(w.category as never)).length;
  if (unclassified > 0) {
    tabs.push({ value: "未分类", label: categoryLabel("未分类", lang), count: unclassified });
  }
  return tabs;
}

export function displaySorted(list: Work[]): Work[] {
  return [...list].sort((a, b) => {
    const af = a.featured ? 1 : 0;
    const bf = b.featured ? 1 : 0;
    if (af !== bf) return bf - af;
    const ao = a.featured_order ?? 999;
    const bo = b.featured_order ?? 999;
    if (ao !== bo) return ao - bo;
    if (b.stat.view !== a.stat.view) return b.stat.view - a.stat.view;
    return b.pubdate - a.pubdate;
  });
}

export function worksFor(category = "ALL"): Work[] {
  const filtered =
    category === "ALL" ? works : works.filter((w) => w.category === category);
  return displaySorted(filtered);
}

export function getWork(bv: string): Work | undefined {
  return works.find((w) => w.bvid === bv);
}

export function getTopFeatured(): Work[] {
  return [...works]
    .filter((w) => w.featured)
    .sort((a, b) => (a.featured_order ?? 999) - (b.featured_order ?? 999))
    .slice(0, 4);
}

export function getLatest(count = 3): Work[] {
  return [...works].sort((a, b) => b.pubdate - a.pubdate).slice(0, count);
}

export function getPrevNext(work: Work): { prev?: Work; next?: Work } {
  const index = works.findIndex((w) => w.bvid === work.bvid);
  return {
    prev: index > 0 ? works[index - 1] : undefined,
    next: index >= 0 && index < works.length - 1 ? works[index + 1] : undefined,
  };
}

export function getRelated(work: Work, count = 4): Work[] {
  return works
    .filter((w) => w.bvid !== work.bvid && w.category === work.category)
    .sort((a, b) => b.stat.view - a.stat.view)
    .slice(0, count);
}

export function isSelf(work: Work): boolean {
  return work.owner.mid === 1016873598 || work.owner.name === "破軍星の終焉煌めき";
}

export function ownerLabel(work: Work, lang: Lang): string {
  return isSelf(work) ? t("self", lang) : work.owner.name;
}

export type ParticipationKind = "full" | "partial" | "proxy" | "joint" | "repost";

export function participationKind(value: string): ParticipationKind {
  if (value.includes("代投")) return "proxy";
  if (value.includes("转载")) return "repost";
  if (value.includes("联合投稿")) return "joint";
  if (value.includes("全部制作") || value === "全制作") return "full";
  return "partial";
}

export function participationLabel(value: string, lang: Lang): string {
  const kind = participationKind(value);
  const key =
    kind === "full"
      ? "participationFull"
      : kind === "proxy"
        ? "participationProxy"
        : kind === "joint"
          ? "participationJoint"
          : kind === "repost"
            ? "participationRepost"
            : "participationPartial";
  return t(key, lang);
}

export function formatView(value: number): string {
  return new Intl.NumberFormat("en-US").format(value || 0);
}

export function formatDate(value: string): string {
  return (value || "").slice(0, 10).replaceAll("-", ".");
}

export function formatDuration(seconds: number): string {
  const m = Math.floor((seconds || 0) / 60);
  const s = Math.floor((seconds || 0) % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function coverUrl(pic: string, size: "card" | "hero" = "card"): string {
  if (!pic) return assetPath("ring-placeholder.svg");
  const base = pic.replace(/@.*$/, "");
  const suffix = size === "card" ? "@480w_270h_1c.webp" : "@960w_540h_1c.webp";
  return `${base}${suffix}`;
}

export function bilibiliUrl(work: Work): string {
  return `https://www.bilibili.com/video/${work.bvid}/`;
}

export function playerUrl(work: Work): string {
  return `https://player.bilibili.com/player.html?isOutside=true&aid=${work.aid}&bvid=${work.bvid}&cid=${work.cid}&p=1`;
}

export const statsDate = formatDate(siteStats.generated_at);
