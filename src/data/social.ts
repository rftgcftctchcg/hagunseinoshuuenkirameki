export interface SnsLink {
  key: "x" | "youtube" | "niconico" | "bilibili";
  label: string;
  handle: string;
  href: string;
}

export const SNS_LINKS: SnsLink[] = [
  { key: "x", label: "TWITTER / X", handle: "@ripjunep", href: "https://x.com/ripjunep" },
  {
    key: "youtube",
    label: "YOUTUBE",
    handle: "@ripjune_krmk",
    href: "https://www.youtube.com/@ripjune_krmk",
  },
  {
    key: "niconico",
    label: "NICONICO",
    handle: "144675660",
    href: "https://www.nicovideo.jp/user/144675660",
  },
  {
    key: "bilibili",
    label: "BILIBILI",
    handle: "1016873598",
    href: "https://space.bilibili.com/1016873598",
  },
];

export const MAIL = "wjy120308@gmail.com";
export const OTHER_TAGS = ["CK3", "EU4"];
