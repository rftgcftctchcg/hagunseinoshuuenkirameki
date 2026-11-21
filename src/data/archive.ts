import type { Lang } from "../utils/paths";

export type Tri = Record<Lang, string>;
export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface ArchiveImage {
  rect: Rect;
  alt: Tri;
}

export interface ArchiveExpression {
  rect: Rect;
  label: Tri;
}

export interface ArchiveColor {
  hex: string;
  label: Tri;
}

export interface ArchiveSection {
  no: string;
  id: string;
  label: string;
  jp: string;
  title: Tri;
  text: Tri;
  images?: ArchiveImage[];
  expressions?: ArchiveExpression[];
  colors?: ArchiveColor[];
}

const tri = (ja: string, zh: string, en: string): Tri => ({ ja, zh, en });

const expressionRects: Rect[] = [
  { x: 0.538, y: 0.015, w: 0.063, h: 0.125 },
  { x: 0.603, y: 0.015, w: 0.063, h: 0.125 },
  { x: 0.668, y: 0.015, w: 0.063, h: 0.125 },
  { x: 0.538, y: 0.15, w: 0.063, h: 0.125 },
  { x: 0.603, y: 0.15, w: 0.063, h: 0.125 },
  { x: 0.668, y: 0.15, w: 0.063, h: 0.125 },
];

export const ARCHIVE_SECTIONS: ArchiveSection[] = [
  {
    no: "01",
    id: "archive-profile",
    label: "PROFILE",
    jp: "基本資料",
    title: tri("メキチャン", "メキチャン", "mekichann"),
    text: tri(
      "メキチャン（mekichann）。破軍星の終焉煌めきの最後の二仮名を片仮名に、好きなボカロ MV 師 channel の頭五文字を片仮名にした名前。性別はキメラ、格言は「ほんんせい。」。",
      "メキチャン（mekichann）。取「破軍星の終焉煌めき」最后两个假名改为片假名，再加上喜欢的 VOCALOID MV 师 channel 的前五个字母。性别是キメラ，格言是「ほんんせい。」。",
      "mekichann — the last two kana of 破軍星の終焉煌めき, plus the first five letters of a favorite VOCALOID MV channel. Sex: kimera. Credo: “honnsei.”"
    ),
    images: [
      { rect: { x: 0.02, y: 0.02, w: 0.22, h: 0.96 }, alt: tri("全身立绘", "全身立绘", "Full-body portrait") },
      { rect: { x: 0.245, y: 0.0, w: 0.235, h: 0.285 }, alt: tri("面部特写", "面部特写", "Face close-up") },
    ],
  },
  {
    no: "02",
    id: "archive-expression",
    label: "EXPRESSION",
    jp: "表情差分",
    title: tri("六つの表情", "六种表情", "Six expressions"),
    text: tri(
      "同じ人物の六つの表情。",
      "同一个人的六种表情。",
      "Six expressions of one person."
    ),
    expressions: [
      { rect: expressionRects[0], label: tri("通常", "通常", "Neutral") },
      { rect: expressionRects[1], label: tri("微笑", "微笑", "Smile") },
      { rect: expressionRects[2], label: tri("狂気", "狂气", "Frenzy") },
      { rect: expressionRects[3], label: tri("驚き", "惊讶", "Surprise") },
      { rect: expressionRects[4], label: tri("泣き", "哭泣", "Cry") },
      { rect: expressionRects[5], label: tri("目閉じ", "闭眼", "Eyes closed") },
    ],
  },
  {
    no: "03",
    id: "archive-color",
    label: "COLOR",
    jp: "色板",
    title: tri("White / Gray / Black", "White / Gray / Black", "White / Gray / Black"),
    text: tri(
      "純白から深黒まで。キャラクターの基礎色。",
      "从纯白到深黑，角色的基础色彩。",
      "From pure white to deep black — the character's base palette."
    ),
    colors: [
      { hex: "#FFFFFF", label: tri("WHITE", "WHITE", "WHITE") },
      { hex: "#A8A8B0", label: tri("GRAY", "GRAY", "GRAY") },
      { hex: "#08080A", label: tri("BLACK", "BLACK", "BLACK") },
    ],
  },
  {
    no: "04",
    id: "archive-hair",
    label: "HAIR",
    jp: "髪型",
    title: tri("半鑽頭のローマ巻き", "半钻头式罗马卷", "Half-drill Roman curls"),
    text: tri(
      "純白の髪。右側は自然な髪、左側は半分のドリル。非対称が最大の特徴。",
      "纯白头发。右侧正常，左侧半钻头式罗马卷。不对称是最鲜明的外观特征。",
      "Pure white hair. The right side is natural; the left is a half-drill curl. The asymmetry is the clearest silhouette."
    ),
    images: [
      { rect: { x: 0.25, y: 0.28, w: 0.26, h: 0.22 }, alt: tri("髪の詳細", "发型细节", "Hair detail") },
    ],
  },
  {
    no: "05",
    id: "archive-earring",
    label: "EARRING",
    jp: "耳飾り",
    title: tri("十字架の耳飾り", "十字架耳饰", "Cross earring"),
    text: tri(
      "十字架の耳飾り。その意味は、後日公開。",
      "十字架耳饰。它的意义留待后续揭晓。",
      "A cross earring. Its meaning is yet to be revealed."
    ),
    images: [
      { rect: { x: 0.78, y: 0.25, w: 0.12, h: 0.3 }, alt: tri("耳飾り", "耳饰", "Earring") },
    ],
  },
  {
    no: "06",
    id: "archive-eye",
    label: "EYE",
    jp: "瞳",
    title: tri("黒い虹彩、白い瞳孔", "黑色虹膜、白色瞳孔", "Black iris, white pupil"),
    text: tri(
      "黒い虹彩と白い瞳孔。冷淡で空虚な眼差しも、この顔の一部。",
      "黑色虹膜，白色瞳孔。冷淡、空洞的眼神，是这张面孔的一部分。",
      "A black iris and a white pupil. The cold, hollow gaze is part of the face."
    ),
    images: [
      { rect: { x: 0.49, y: 0.31, w: 0.09, h: 0.1 }, alt: tri("瞳の詳細", "眼部细节", "Eye detail") },
    ],
  },
  {
    no: "07",
    id: "archive-instrument",
    label: "INSTRUMENT",
    jp: "楽器",
    title: tri("V 字ディストーション・ギター", "V 型失真电吉他", "V-shaped distortion guitar"),
    text: tri(
      "V 字のディストーション・ギターと折りたたみ式キーボード。耳に心地よい旋律より、音がどこまで歪められるかを気にしている。",
      "V 型失真电吉他与折叠键盘。比起悦耳的旋律，更在意声音能被扭曲到什么程度。",
      "A V-shaped distortion guitar and a folding keyboard. More interested in how far sound can be twisted than in pleasant melody."
    ),
    images: [
      { rect: { x: 0.25, y: 0.5, w: 0.19, h: 0.29 }, alt: tri("失電ギター", "失真电吉他", "Distortion guitar") },
      { rect: { x: 0.535, y: 0.365, w: 0.245, h: 0.11 }, alt: tri("折りたたみキーボード", "折叠键盘", "Folding keyboard") },
    ],
  },
  {
    no: "08",
    id: "archive-outfit",
    label: "OUTFIT",
    jp: "服装",
    title: tri("束帯とチェーン", "束带与铁链", "Straps and chains"),
    text: tri(
      "束帯、チェーン、ワイドパンツ、鋲付きブーツ。黒と白の組み合わせが輪郭をつくる。",
      "束带、铁链、宽带裤、铆钉靴。黑与白的组合构成外在轮廓。",
      "Straps, chains, wide trousers, studded boots. Black and white make the outline."
    ),
    images: [
      { rect: { x: 0.03, y: 0.5, w: 0.21, h: 0.45 }, alt: tri("服装の詳細", "服装细节", "Outfit detail") },
    ],
  },
  {
    no: "09",
    id: "archive-turnaround",
    label: "TURNAROUND",
    jp: "三面図",
    title: tri("正面・側面・背面", "正面 / 侧面 / 背面", "Front / side / back"),
    text: tri(
      "異なる角度から、同じ人物の完全な形を記録する。正面、側面、背面、そしてもう一つの側面。",
      "从不同角度，记录同一个人的完整形态。正面、侧面、背面，以及另一侧面。",
      "The same person from every angle: front, side, back, and the other side."
    ),
    images: [
      { rect: { x: 0.52, y: 0.5, w: 0.23, h: 0.43 }, alt: tri("三面図", "三面图", "Turnaround") },
    ],
  },
  {
    no: "10",
    id: "archive-props",
    label: "PROPS",
    jp: "随身物",
    title: tri("無。", "无。", "Nothing."),
    text: tri("無。", "无。", "Nothing."),
  },
];
