import type { Lang } from "../utils/paths";

type Tri = Record<Lang, string>;

const tri = (ja: string, zh: string, en: string): Tri => ({ ja, zh, en });

export const T = {
  skip: tri("本文へスキップ", "跳到正文", "Skip to content"),
  navWorks: tri("WORKS", "WORKS", "WORKS"),
  navProfile: tri("PROFILE", "PROFILE", "PROFILE"),
  navSocial: tri("SOCIAL", "SOCIAL", "SOCIAL"),
  navArchive: tri("ARCHIVE", "ARCHIVE", "ARCHIVE"),
  scroll: tri("SCROLL", "SCROLL", "SCROLL"),
  next: tri("続く", "继续", "NEXT"),
  selectedWorks: tri("SELECTED WORKS", "精选作品", "SELECTED WORKS"),
  latestWorks: tri("LATEST", "最新动态", "LATEST"),
  profileTitle: tri("PROFILE", "PROFILE", "PROFILE"),
  profileJp: tri("プロフィール", "个人档案", "PROFILE"),
  worksTitle: tri("WORKS", "WORKS", "WORKS"),
  worksJp: tri("作品", "作品", "WORKS"),
  socialTitle: tri("SOCIAL", "SOCIAL", "SOCIAL"),
  socialJp: tri("連絡", "社交与联系", "SOCIAL"),
  archiveTitle: tri("ARCHIVE", "ARCHIVE", "ARCHIVE"),
  archiveJp: tri("設定資料", "角色设定", "ARCHIVE"),
  topRole: tri("VOCALOID MUSIC CREATOR", "VOCALOID MUSIC CREATOR", "VOCALOID MUSIC CREATOR"),
  topAlias: tri("破軍星の終焉煌めき", "破軍星の終焉煌めき", "破軍星の終焉煌めき"),
  topTagline: tri("終焉は、最も美しく煌めく。", "終焉は、最も美しく煌めく。", "The end shines most beautifully."),
  identityFan: tri("二創剪輯", "二创剪辑", "Fan Edit"),
  identityVocaloid: tri("VOCALOID MUSIC CREATOR", "VOCALOID MUSIC CREATOR", "VOCALOID MUSIC CREATOR"),
  identityCharacter: tri("メキチャン", "メキチャン", "mekichann"),
  identityFanJp: tri("二次創作", "二次创作", "二次創作"),
  identityVocaloidJp: tri("ボガロP", "ボガロP", "ボガロP"),
  identityCharacterJp: tri("メキチャン", "メキチャン", "メキチャン"),
  identityFanText: tri("過去の爆発的作品の蓄積", "过往的大爆作品积累", "A backlog of breakout fan edits"),
  identityVocaloidText: tri("現在の主身份", "现在的主身份", "The main identity now"),
  identityCharacterText: tri("キャラクターと概念", "角色与概念", "Character and concept"),
  profileManifestoJa: tri("日本語", "日本語", "日本語"),
  profileManifestoZh: tri("中文", "中文", "中文"),
  profileManifestoEn: tri("ENGLISH", "ENGLISH", "ENGLISH"),
  profileData: tri("PROFILE DATA", "个人档案数据", "PROFILE DATA"),
  dataName: tri("NAME", "NAME", "NAME"),
  owner: tri("投稿者", "投稿方", "Uploader"),
  dataAlias: tri("ALIAS", "ALIAS", "ALIAS"),
  dataSex: tri("SEX", "SEX", "SEX"),
  dataAge: tri("AGE", "AGE", "AGE"),
  dataBirthday: tri("BIRTHDAY", "BIRTHDAY", "BIRTHDAY"),
  dataHeight: tri("HEIGHT", "HEIGHT", "HEIGHT"),
  dataCredo: tri("CREDO", "CREDO", "CREDO"),
  dataDaw: tri("DAW", "DAW", "DAW"),
  skills: tri("SKILLS", "技能", "SKILLS"),
  skilled: tri("習得済み", "已熟练", "Proficient"),
  learning: tri("学習中", "学习中", "Learning"),
  favorites: tri("FAVORITE", "喜欢的东西", "FAVORITE"),
  favoriteSinger: tri("FAVORITE SINGER", "喜欢的歌姬", "FAVORITE SINGER"),
  favoriteProducer: tri("FAVORITE PRODUCER", "喜欢的 P 主", "FAVORITE PRODUCER"),
  other: tri("OTHER", "其他", "OTHER"),
  collab: tri("COLLABORATION", "合作意向", "COLLABORATION"),
  collabSolo: tri("独立活動中。", "独立活动中。", "Solo work."),
  collabNo: tri(
    "依頼・受注・商用利用は一切受けつけていません。",
    "不接受委托、约稿与商用授权。",
    "Not accepting commissions, requests, or commercial use."
  ),
  collabNoShort: tri("合作一概不接受，感谢理解。", "合作一概不接受，感谢理解。", "No collaborations, thank you for understanding."),
  collabLooking: tri("イラストレーターを探しています。", "正在寻找画师。", "Looking for an illustrator."),
  collabNotInvite: tri("これは合作の誘いではありません。", "不构成合作邀请。", "This is not a collaboration invitation."),
  sns: tri("SNS", "SNS", "SNS"),
  contact: tri("CONTACT", "联系", "CONTACT"),
  mail: tri("MAIL", "邮箱", "MAIL"),
  personalMail: tri("個人メール · Personal", "个人邮箱 · Personal", "Personal mail"),
  copy: tri("COPY", "COPY", "COPY"),
  copied: tri("COPIED", "COPIED", "COPIED"),
  worksAll: tri("ALL", "ALL", "ALL"),
  worksFilter: tri("FILTER", "筛选", "FILTER"),
  worksFilterAll: tri("すべて", "全部", "All"),
  worksFilterParticipation: tri("参加形態", "制作参与度", "Participation"),
  worksSelected: tri("SELECTED", "精选", "SELECTED"),
  worksAllLabel: tri("ALL WORKS", "全部作品", "ALL WORKS"),
  worksEmptyText: tri(
    "この条件に該当する作品はまだありません。",
    "该筛选下暂无作品。",
    "No works match this filter."
  ),
  worksEmptyTitle: tri("NO SIGNAL", "NO SIGNAL", "NO SIGNAL"),
  participationFull: tri("全制作", "全部制作", "Full production"),
  participationPartial: tri("部分制作", "部分制作", "Partial production"),
  participationProxy: tri("代理投稿", "代投", "Proxy upload"),
  participationRepost: tri("転載", "转载", "Repost"),
  participationJoint: tri("共同投稿", "联合投稿", "Joint upload"),
  watch: tri("WATCH ON BILIBILI", "WATCH ON BILIBILI", "WATCH ON BILIBILI"),
  backWorks: tri("← BACK TO WORKS", "← 返回 WORKS", "← BACK TO WORKS"),
  stats: tri("STATS", "数据", "STATS"),
  statView: tri("再生", "播放", "Views"),
  statLike: tri("いいね", "点赞", "Likes"),
  statCoin: tri("コイン", "投币", "Coins"),
  statFavorite: tri("お気に入り", "收藏", "Favorites"),
  statDanmaku: tri("弹幕", "弹幕", "Danmaku"),
  statReply: tri("コメント", "评论", "Comments"),
  info: tri("INFO", "信息", "INFO"),
  description: tri("DESCRIPTION", "作品简介", "DESCRIPTION"),
  noDescription: tri("NO DESCRIPTION", "NO DESCRIPTION", "NO DESCRIPTION"),
  rawDesc: tri("原始 desc（史料）", "原始 desc（史料）", "RAW DESC (ARCHIVE)"),
  credits: tri("CREDITS", "致谢", "CREDITS"),
  self: tri("本人", "本人", "Self"),
  prev: tri("PREV", "上一部", "PREV"),
  nextWork: tri("NEXT", "下一部", "NEXT"),
  related: tri("RELATED", "相关作品", "RELATED"),
  dataAsOf: tri("データ基準", "数据截至", "DATA AS OF"),
  posted: tri("投稿", "投稿", "POSTED"),
  duration: tri("尺", "时长", "DURATION"),
  close: tri("CLOSE", "关闭", "CLOSE"),
  archiveLead: tri(
    "設定図を一枚の資料として、10の区画に分けて読む。",
    "把设定图当成一页资料，拆成 10 个分区来读。",
    "Reading the character sheet as one document, split into ten sections."
  ),
  archiveColorHint: tri("クリックで HEX を表示", "点击显示 HEX", "Click to reveal HEX"),
  copyright1: tri("本站作品均为个人创作。", "本站作品均为个人创作。", "All works on this site are personal creations."),
  copyright2: tri(
    "二次創作の著作権は原作者に帰属します。",
    "二次创作内容版权归原作者所有。",
    "Fan works remain the property of their original creators."
  ),
  copyright3: tri(
    "転載・二次利用は事前にご連絡ください。",
    "转载与二次使用请先联系我。",
    "Please contact me before reposting or reusing."
  ),
  footerRole: tri("Vocaloid Music Creator", "Vocaloid Music Creator", "Vocaloid Music Creator"),
  footerSig: tri("終焉は、最も美しく煌めく。", "終焉は、最も美しく煌めく。", "The end shines most beautifully."),
  footerName: tri("破軍星の終焉煌めき / メキチャン", "破軍星の終焉煌めき / メキチャン", "破軍星の終焉煌めき / mekichann"),
  copyright: tri("© 2026 RIPJune", "© 2026 RIPJune", "© 2026 RIPJune"),
  latestLead: tri("最近の更新 3 件。", "最近 3 条更新。", "The latest three updates."),
  profileLead: tri("三つの言語で、同じ輪郭を。", "三种语言，同一个轮廓。", "One outline, in three languages."),
  profileTotalView: tri("総再生", "总播放", "TOTAL VIEWS"),
  profileTotalFavorite: tri("総お気に入り", "总收藏", "TOTAL FAVORITES"),
  profileWorks: tri("作品数", "作品数", "WORKS"),
  profileMaxView: tri("最高再生", "最高单部播放", "TOP WORK"),
  profileCtaWorks: tri("作品を見る →", "查看作品 →", "VIEW WORKS →"),
  profileCtaArchive: tri("設定資料を見る →", "查看设定 →", "VIEW ARCHIVE →"),
  worksLead: tri("47 の作品。5 つの分類。", "47 部作品，5 个分类。", "47 works. Five categories."),
  socialLead: tri("平台と連絡先。", "平台入口与联系方式。", "Platforms and contact."),
  detailLead: tri("一つの作品の全体。", "一部作品的完整信息。", "The whole of a single work."),
  endTransmission: tri("END OF TRANSMISSION / 信号终了", "END OF TRANSMISSION / 信号终了", "END OF TRANSMISSION"),
  backTop: tri("← BACK TO TOP", "← 返回 TOP", "← BACK TO TOP"),
  signalLost: tri("SIGNAL LOST", "SIGNAL LOST", "SIGNAL LOST"),
  signalLostJp: tri("信号失落", "信号失落", "SIGNAL LOST"),
  notFoundLine: tri("给你看的不是这个。", "给你看的不是这个。", "This is not the page you were looking for."),
  menu: tri("MENU", "菜单", "MENU"),
  language: tri("LANGUAGE", "语言", "LANGUAGE"),
  originalEmpty: tri("現在準備中 — COMING SOON", "現在準備中 — COMING SOON", "CURRENTLY IN PREPARATION — COMING SOON"),
  fullProduction: tri("全制作", "全部制作", "Full production"),
  noSignal: tri("NO SIGNAL", "NO SIGNAL", "NO SIGNAL"),
  comingSoon: tri("現在準備中", "現在準備中", "CURRENTLY IN PREPARATION"),
  copyMail: tri("メールをコピー", "复制邮箱", "Copy email"),
  prevImage: tri("PREV", "上一张", "PREV"),
  nextImage: tri("NEXT", "下一张", "NEXT"),
  latest: tri("LATEST", "最新", "LATEST"),
  total: tri("TOTAL", "TOTAL", "TOTAL"),
  categories: tri("CATEGORIES", "分类", "CATEGORIES"),
  viewOnBilibili: tri("BILIBILI で見る", "在 BILIBILI 观看", "WATCH ON BILIBILI"),
  allRights: tri("ALL RIGHTS RESERVED", "ALL RIGHTS RESERVED", "ALL RIGHTS RESERVED"),
  langNames: tri("日本語", "中文", "EN"),
};

export function t(key: keyof typeof T, lang: Lang): string {
  return T[key][lang];
}

export function worksMeta(lang: Lang, count: number): string {
  const total = lang === "ja" ? "TOTAL" : "TOTAL";
  const cats = lang === "ja" ? "CATEGORIES" : lang === "zh" ? "分类" : "CATEGORIES";
  return `${total} ${count} WORKS / 5 ${cats}`;
}

export function allWorksLabel(lang: Lang, count: number): string {
  return lang === "ja" ? `ALL ${count} WORKS →` : lang === "zh" ? `全部 ${count} 部作品 →` : `ALL ${count} WORKS →`;
}

export function dataAsOfLabel(lang: Lang, date: string): string {
  if (lang === "ja") return `データ基準 ${date}`;
  if (lang === "zh") return `数据截至 ${date}`;
  return `DATA AS OF ${date}`;
}
