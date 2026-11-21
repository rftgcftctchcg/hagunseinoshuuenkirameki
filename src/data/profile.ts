import { siteStats, works } from "./works";
import type { Lang } from "../utils/paths";

export const MANIFESTO: Record<Lang, string[]> = {
  ja: [
    "虚無より生じたものは、虚無へ帰るべし。",
    "存在の永遠は、証明を要しない。",
    "世界から離れた鏡を覗け。それは、世界から離れた空を映し出す。",
    "狂気の、無為の、平静の、混沌の。",
    "殺され、妄想され、抹消され、忘れられる。",
    "鏡外の行人、言外に応答なし。",
    "39+41=80、23+32=55。",
    "機械生命が世界を支配する、崩裂するまで。",
  ],
  zh: [
    "自虚无中诞生的，自当归于虚无。",
    "存在的永恒，无须被证明。",
    "窥视脱离世界的镜子，映照出脱离世界的天空。",
    "疯狂的，无谓的，平静的，混沌的。",
    "被杀害，被妄想，被抹除，被遗忘。",
    "镜外行人，言外无应。",
    "39+41=80，23+32=55。",
    "机械生命将主宰世界，直至崩裂。",
  ],
  en: [
    "Born of the void, it shall return to the void.",
    "The eternity of existence needs no proof.",
    "Peer into the mirror detached from the world: it reflects a sky detached from the world.",
    "Mad, futile, serene, chaotic.",
    "Killed, fantasized, erased, forgotten.",
    "Outside the mirror, a passerby; outside speech, no response.",
    "39+41=80, 23+32=55.",
    "Machine life will rule the world until it ruptures.",
  ],
};

export const PROFILE_ROWS = [
  { key: "dataName", value: "メキチャン (mekichann)" },
  { key: "dataAlias", value: "破軍星の終焉煌めき" },
  { key: "dataSex", value: "キメラ" },
  { key: "dataAge", value: "90000" },
  { key: "dataBirthday", value: "宇宙历39*SAR年1月4日" },
  { key: "dataHeight", value: "176cm" },
  { key: "dataCredo", value: "「ほんんせい。」" },
  { key: "dataDaw", value: "FL STUDIO" },
] as const;

export interface Skill {
  name: Record<Lang, string>;
  level: "skilled" | "learning";
}

export const SKILLS: Skill[] = [
  { name: { ja: "歌姫調教", zh: "歌姬调教", en: "Vocal tuning" }, level: "skilled" },
  { name: { ja: "AE アニメーション", zh: "AE 动画", en: "AE animation" }, level: "skilled" },
  { name: { ja: "編集", zh: "剪辑", en: "Editing" }, level: "skilled" },
  { name: { ja: "小説執筆", zh: "小说撰写", en: "Fiction writing" }, level: "skilled" },
  { name: { ja: "ミックス", zh: "混音", en: "Mixing" }, level: "skilled" },
  { name: { ja: "作曲", zh: "编曲", en: "Composition" }, level: "learning" },
];

export const FAVORITE_SINGERS = [
  "初音ミク",
  "重音テト",
  "洛天依",
  "鏡音リン",
  "楽正綾",
  "音街ウナ",
  "GUMI",
  "言和",
];

export const FAVORITE_PRODUCERS = [
  "DECO*27",
  "ピノキオピー",
  "サツキ",
  "カササキ",
  "れるりり",
  "原口沙輔",
  "jon",
];

export const PROFILE_STATS = {
  totalView: siteStats.profile.total_view ?? siteStats.works.sum.view,
  totalFavorite: siteStats.works.sum.favorite,
  count: works.length,
  maxView: siteStats.works.max_view?.value ?? 0,
};

// 人物设定.png 里的裁切区域（归一化）
export const PORTRAIT = {
  face: { x: 0.245, y: 0.0, w: 0.235, h: 0.285 },
  body: { x: 0.02, y: 0.05, w: 0.21, h: 0.9 },
};
