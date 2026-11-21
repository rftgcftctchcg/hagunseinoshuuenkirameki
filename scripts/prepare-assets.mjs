import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import sharp from "sharp";

const root = process.cwd();
const me = join(root, "ME");
const pub = join(root, "public");
await mkdir(pub, { recursive: true });

// 1) 品牌 / 头像 / 设定图
await sharp(join(me, "LOGO.png"))
  .resize(1024, 1024, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
  .webp({ quality: 90 })
  .toFile(join(pub, "logo-1024.webp"));

await sharp(join(me, "头像.png"))
  .resize(180, 180, { fit: "cover" })
  .png()
  .toFile(join(pub, "avatar.png"));

await sharp(join(me, "人物设定.png"))
  .resize({ width: 1600, withoutEnlargement: true })
  .webp({ quality: 82 })
  .toFile(join(pub, "character-sheet.webp"));

// 2) 断裂圆环（用于页头 / favicon / 装饰）
const ring = (stroke = "currentColor", dot = false) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <g fill="none" stroke="${stroke}" stroke-width="6" stroke-linecap="butt">
    <circle cx="50" cy="50" r="42" pathLength="360" stroke-dasharray="150 210" transform="rotate(-15 50 50)"/>
    <circle cx="50" cy="50" r="42" pathLength="360" stroke-dasharray="150 210" transform="rotate(165 50 50)"/>
  </g>
  ${dot ? '<circle cx="50" cy="50" r="4" fill="#CE1126"/>' : ""}
</svg>`;
const { writeFile } = await import("node:fs/promises");
await writeFile(join(pub, "ring.svg"), ring(), "utf8");
await writeFile(join(pub, "favicon.svg"), ring("#08080A", true), "utf8");
await writeFile(
  join(pub, "ring-placeholder.svg"),
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 270">
    <rect width="480" height="270" fill="#F2F2F3"/>
    <g fill="none" stroke="#A8A8B0" stroke-width="3">
      <circle cx="240" cy="118" r="46" pathLength="360" stroke-dasharray="150 210" transform="rotate(-15 240 118)"/>
      <circle cx="240" cy="118" r="46" pathLength="360" stroke-dasharray="150 210" transform="rotate(165 240 118)"/>
    </g>
    <text x="240" y="205" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" letter-spacing="6" fill="#6E6E78">NO SIGNAL</text>
  </svg>`,
  "utf8"
);

// 3) OG：YT 头图 + 白罩 + 品牌文字 + ECG
const yt = await sharp(join(me, "YT头图.png"))
  .resize(1200, 630, { fit: "cover", position: "centre" })
  .toBuffer();

const ogOverlay = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#FFFFFF" opacity="0.74"/>
  <g fill="none" stroke="#08080A" stroke-width="1.2" opacity="0.18">
    <circle cx="1010" cy="315" r="210" pathLength="360" stroke-dasharray="150 210" transform="rotate(-15 1010 315)"/>
    <circle cx="1010" cy="315" r="210" pathLength="360" stroke-dasharray="150 210" transform="rotate(165 1010 315)"/>
  </g>
  <text x="80" y="170" font-family="Arial Black, Arial, sans-serif" font-size="104" letter-spacing="2" fill="#08080A">RIPJune</text>
  <text x="80" y="230" font-family="Inter, Arial, sans-serif" font-size="22" letter-spacing="5" fill="#3A3A42">VOCALOID MUSIC CREATOR / メキチャン</text>
  <text x="80" y="286" font-family="'Yu Mincho', 'MS Mincho', serif" font-size="30" letter-spacing="2" fill="#08080A">破軍星の終焉煌めき</text>
  <text x="80" y="470" font-family="'Yu Mincho', 'MS Mincho', serif" font-size="28" letter-spacing="3" fill="#08080A">終焉は、最も美しく煌めく。</text>
  <path d="M80 560 H260 L278 560 L292 536 L306 584 L320 560 H470 L486 560 L500 520 L514 596 L528 560 H760 L776 560 L790 540 L804 580 L818 560 H1120"
        fill="none" stroke="#08080A" stroke-width="1.4" opacity="0.7"/>
  <text x="80" y="606" font-family="JetBrains Mono, Consolas, monospace" font-size="13" letter-spacing="3" fill="#6E6E78">rftgcftctchcg.github.io/hagunseinoshuuenkirameki</text>
</svg>`;

await sharp(yt)
  .composite([{ input: Buffer.from(ogOverlay) }])
  .jpeg({ quality: 88, mozjpeg: true })
  .toFile(join(pub, "og-image.jpg"));

console.log("assets ready:", pub);
