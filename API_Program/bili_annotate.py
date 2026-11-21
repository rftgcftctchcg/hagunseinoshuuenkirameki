#!/usr/bin/env python3
# bili_annotate.py
# 用法:
#   python bili_annotate.py --init    # 生成/补全 data/works.manual.yaml 骨架
#   python bili_annotate.py --check   # 校验分类/Credits/未解析人名
#
# 依赖: PyYAML

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    raise SystemExit("[!] 需要 PyYAML：pip install -r requirements.txt")

from bili_fetch_works import (
    AUTO_FILE,
    DATA_DIR,
    MANUAL_FILE,
    PEOPLE_FILE,
    SELF_ALIASES,
    SELF_ALT_MIDS,
    SELF_MID,
    SELF_NAME,
    build_credits,
    ensure_dirs,
    extract_desc_credits,
    is_self,
    people_link,
    safe_load_yaml,
    suggest_participation,
)

SPACE = lambda mid: f"https://space.bilibili.com/{mid}"

DEFAULT_CATEGORIES: dict[str, dict[str, str]] = {
    "二创剪辑": {"ja": "二次創作", "en": "Fan Edit"},
    "VOCALOID": {"ja": "VOCALOID", "en": "VOCALOID"},
    "原创曲": {"ja": "オリジナル", "en": "Original"},
    "搬运": {"ja": "転載", "en": "Repost"},
    "其他": {"ja": "その他", "en": "Other"},
}

DEFAULT_SELF: dict[str, Any] = {
    "mid": SELF_MID,
    "altMids": SELF_ALT_MIDS,
    "name": SELF_NAME,
    "aliases": SELF_ALIASES,
}

# TOP 4 初始精选：2 部全部制作播放前 2 + 全站第 3 + 最新 1
FEATURED_ORDER: dict[str, int] = {
    "BV17Q9fBcE8M": 1,
    "BV1jP5q6KE3k": 2,
    "BV1q3hA6nEnz": 3,
    "BV134sn6kEfJ": 4,
}

# 原 8 部的人工标注；其余 39 部由规则建议，等你逐条确认
KNOWN: dict[str, dict[str, Any]] = {
    "BV17Q9fBcE8M": {
        "category": "二创剪辑",
        "participation": "全部制作",
        "credits": [{"role": "原作者", "name": "圆桌动漫", "link": SPACE(654552)}],
    },
    "BV1jP5q6KE3k": {
        "category": "二创剪辑",
        "participation": "全部制作",
        "credits": [{"role": "原作者", "name": "圆桌动漫", "link": SPACE(654552)}],
    },
    "BV13tofBtEH1": {
        "category": "二创剪辑",
        "participation": "全部制作",
        "credits": [{"role": "原作者", "name": "圆桌动漫", "link": SPACE(654552)}],
    },
    "BV1bKab6CE4F": {
        "category": "二创剪辑",
        "participation": "全部制作",
        "credits": [{"role": "原作者", "name": "新不理鲁德多", "link": SPACE(1753688514)}],
    },
    "BV1aXuB69EoH": {
        "category": "二创剪辑",
        "participation": "全部制作",
        "credits": [
            {"role": "原作者", "name": "圆桌动漫", "link": SPACE(654552)},
            {"role": "鸣谢", "name": "新不理鲁德多", "link": SPACE(1753688514)},
        ],
    },
    "BV1q3hA6nEnz": {
        "category": "二创剪辑",
        "participation": "视频制作",
        "credits": [],
    },
    "BV1upLV6fEfN": {
        "category": "二创剪辑",
        "participation": "代投 · 填词/视频制作/策划",
        "credits": [
            {"role": "曲", "name": "夏玔瑶辉", "link": SPACE(675059275)},
            {"role": "曲", "name": "John Kell"},
            {"role": "特别鸣谢", "name": "夏玔瑶辉", "link": SPACE(675059275)},
            {"role": "特别鸣谢", "name": "xt喜糖", "link": SPACE(3493145937447264)},
            {"role": "特别鸣谢", "name": "圆桌动漫", "link": SPACE(654552)},
            {"role": "原曲", "name": "HEAVENLY JUMPSTYLE"},
            {"role": "策划", "name": SELF_NAME, "self": True},
        ],
    },
    "BV15fbR6pE7H": {
        "category": "VOCALOID",
        "participation": "Vocaloid 歌唱 / 中文填词 / Tuning",
        "credits": [
            {
                "role": "Original",
                "name": "サツキ",
                "link": "https://www.bilibili.com/video/BV15J4m1A7qy",
            },
            {"role": "Vocal", "name": "重音テト & 初音ミク（CV：星塵インフィニティ）"},
            {"role": "Lyric", "name": SELF_NAME, "self": True},
            {"role": "Tuning", "name": SELF_NAME, "self": True},
            {"role": "Mix", "name": "咕咕札"},
            {
                "role": "UST",
                "name": "アトリ科ヒワ属ゲン",
                "link": "https://bowlroll.net/user/317762",
            },
            {"role": "Editor", "name": "SynthesizerV Studio"},
        ],
    },
}

PEOPLE_SEED: dict[str, dict[str, Any]] = {
    "圆桌动漫": {"mid": 654552},
    "新不理鲁德多": {"mid": 1753688514},
    "夏玔瑶辉": {"mid": 675059275},
    "サツキ": {"url": "https://www.bilibili.com/video/BV15J4m1A7qy"},
    "アトリ科ヒワ属ゲン": {"url": "https://bowlroll.net/user/317762"},
    "xt喜糖": {"mid": 3493145937447264},
    "咕咕札": {},
}


def load_auto() -> dict[str, Any]:
    if not AUTO_FILE.exists():
        raise SystemExit(f"[!] 找不到 {AUTO_FILE}，请先运行 bili_fetch_works.py --auto")
    data = json.loads(AUTO_FILE.read_text(encoding="utf-8"))
    if not data.get("videos"):
        raise SystemExit(f"[!] {AUTO_FILE} 没有 videos")
    return data


def load_manual(required: bool = False) -> dict[str, Any] | None:
    if not MANUAL_FILE.exists():
        if required:
            raise SystemExit(f"[!] 找不到 {MANUAL_FILE}，请先运行 bili_annotate.py --init")
        return None
    data = safe_load_yaml(MANUAL_FILE)
    if not isinstance(data, dict):
        raise SystemExit(f"[!] {MANUAL_FILE} 不是 YAML 映射")
    return data


def load_people() -> dict[str, Any]:
    if not PEOPLE_FILE.exists():
        return {}
    data = safe_load_yaml(PEOPLE_FILE) or {}
    people = data.get("people") if isinstance(data, dict) else None
    return people if isinstance(people, dict) else {}


def backup(path: Path) -> None:
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak"))


def write_people() -> None:
    people = load_people()
    changed = not PEOPLE_FILE.exists()
    for name, entry in PEOPLE_SEED.items():
        if name not in people:
            people[name] = entry
            changed = True
    if not changed:
        return
    backup(PEOPLE_FILE)
    text = (
        "# 名字 → mid/url；没有链接的写 {}，站内纯文本 + --check 警告\n"
        + yaml.safe_dump(
            {"people": people},
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
    )
    PEOPLE_FILE.write_text(text, encoding="utf-8")
    print(f"[✓] 写入 {PEOPLE_FILE}")


def self_cfg_of(manual: dict[str, Any] | None) -> dict[str, Any]:
    if manual and isinstance(manual.get("self"), dict):
        cfg = dict(DEFAULT_SELF)
        cfg.update(manual["self"])
        return cfg
    return dict(DEFAULT_SELF)


def kind_of(rec: dict[str, Any], cfg: dict[str, Any]) -> str:
    owner = rec.get("owner") or {}
    if rec.get("copyright") == 2:
        return "转载"
    if rec.get("staff"):
        return "联合投稿"
    if is_self(owner.get("name"), owner.get("mid"), cfg):
        return "自制"
    return "其他"


def entry_for(rec: dict[str, Any], cfg: dict[str, Any], people: dict[str, Any]) -> dict[str, Any]:
    bv = rec.get("bvid")
    known = KNOWN.get(bv, {})
    entry: dict[str, Any] = {
        "category": known.get("category", ""),
        "participation": known.get("participation") or suggest_participation(rec, cfg),
    }
    credits = build_credits(rec, {"credits": known.get("credits", [])}, people, cfg)
    if credits:
        entry["credits"] = credits
    if bv in FEATURED_ORDER:
        entry["featured"] = True
        entry["featuredOrder"] = FEATURED_ORDER[bv]
    return entry


def yq(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_manual(auto: dict[str, Any], cfg: dict[str, Any], people: dict[str, Any]) -> str:
    lines: list[str] = [
        "# RIPJune 作品标注（唯一手改文件）",
        "# 1) 填 category（必填）：二创剪辑 / VOCALOID / 原创曲 / 搬运 / 其他",
        "# 2) 需要时改 participation / credits；featured 控制 WORKS 精选组",
        "# 3) 校验：python bili_annotate.py --check",
        "#    合并：python bili_fetch_works.py --merge",
        "",
        "schema: 1",
        "",
        "self:",
        f"  mid: {cfg['mid']}",
        f"  altMids: {yq(cfg.get('altMids', []))}",
        f"  name: {yq(cfg.get('name', SELF_NAME))}",
        "  aliases:",
    ]
    for alias in cfg.get("aliases", []):
        lines.append(f"    - {yq(alias)}")
    lines += ["", "categories:"]
    for key, meta in DEFAULT_CATEGORIES.items():
        lines.append(f"  {key}: {{ ja: {yq(meta['ja'])}, en: {yq(meta['en'])} }}")
    lines += ["", "works:"]

    for rec in sorted(auto["videos"], key=lambda r: r.get("no") or 9999):
        bv = rec.get("bvid") or ""
        title = (rec.get("title") or "").replace("\n", " ")
        stat = rec.get("stat") or {}
        lines += [
            "",
            f"  # NO.{int(rec.get('no') or 0):03d} · {(rec.get('created_str') or '')[:10]} · "
            f"{int(stat.get('view') or 0):,} 播放 · {kind_of(rec, cfg)}",
            f"  # {title}",
            f"  {bv}:",
        ]
        entry = entry_for(rec, cfg, people)
        cat = entry.get("category", "")
        if cat:
            lines.append(f"    category: {yq(cat)}")
        else:
            lines.append(
                '    category: ""  # TODO 必填：二创剪辑 / VOCALOID / 原创曲 / 搬运 / 其他'
            )
        lines.append(f"    participation: {yq(entry.get('participation', ''))}")
        if entry.get("featured"):
            lines.append("    featured: true")
            lines.append(f"    featuredOrder: {entry.get('featuredOrder')}")
        credits = entry.get("credits") or []
        if credits:
            lines.append("    credits:")
            for c in credits:
                parts = [f"role: {yq(c.get('role', ''))}", f"name: {yq(c.get('name', ''))}"]
                if c.get("link"):
                    parts.append(f"link: {yq(c['link'])}")
                if c.get("self"):
                    parts.append("self: true")
                lines.append("      - { " + ", ".join(parts) + " }")

    lines.append("")
    return "\n".join(lines)


def run_init() -> int:
    ensure_dirs()
    auto = load_auto()
    people = load_people()
    write_people()
    people = load_people()

    manual = load_manual(required=False)
    if manual is None:
        cfg = dict(DEFAULT_SELF)
        text = render_manual(auto, cfg, people)
        MANUAL_FILE.write_text(text, encoding="utf-8")
        print(f"[✓] 写入 {MANUAL_FILE}（{auto.get('count')} 部）")
        print("    下一步：填写 category；再运行 bili_annotate.py --check")
        return 0

    cfg = self_cfg_of(manual)
    works = manual.get("works") or {}
    if not isinstance(works, dict):
        print(f"[!] {MANUAL_FILE} 的 works 不是映射")
        return 1
    missing = [r for r in auto["videos"] if r.get("bvid") not in works]
    if not missing:
        print(f"[✓] {MANUAL_FILE} 已包含全部 {auto.get('count')} 部，无需补全")
        return 0

    for rec in missing:
        works[rec["bvid"]] = entry_for(rec, cfg, people)
    manual["works"] = works
    manual.setdefault("schema", 1)
    manual.setdefault("self", cfg)
    manual.setdefault("categories", DEFAULT_CATEGORIES)
    backup(MANUAL_FILE)
    header = (
        "# RIPJune 作品标注（唯一手改文件）\n"
        "# 由 bili_annotate.py --init 补全新 BV；已有字段未被覆盖，注释可能被重排。\n\n"
    )
    MANUAL_FILE.write_text(
        header
        + yaml.safe_dump(
            manual,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )
    print(f"[✓] 补全 {len(missing)} 部 → {MANUAL_FILE}（备份 .bak）")
    return 0


def run_check() -> int:
    auto = load_auto()
    manual = load_manual(required=True)
    assert manual is not None
    cfg = self_cfg_of(manual)
    people = load_people()
    works = manual.get("works") or {}
    if not isinstance(works, dict):
        print(f"[!] {MANUAL_FILE} 的 works 不是映射")
        return 1
    valid_categories = set((manual.get("categories") or DEFAULT_CATEGORIES).keys())
    auto_bvs = {r.get("bvid") for r in auto["videos"]}

    errors: list[str] = []
    warnings: list[str] = []
    missing_cat: list[tuple[str, str]] = []
    unlinked: set[str] = set()
    uncredited: set[str] = set()
    featured_count = 0

    for rec in auto["videos"]:
        bv = rec.get("bvid") or ""
        mw = works.get(bv)
        if not isinstance(mw, dict):
            warnings.append(f"{bv} 缺条目（请运行 --init）")
            continue
        cat = (mw.get("category") or "").strip()
        if not cat:
            missing_cat.append((bv, rec.get("title") or ""))
        elif cat not in valid_categories:
            errors.append(f"{bv} 非法 category={cat!r}")
        if mw.get("featured"):
            featured_count += 1

        credits = mw.get("credits") or []
        if not isinstance(credits, list):
            errors.append(f"{bv} credits 不是列表")
            continue
        credit_names: set[str] = set()
        for c in credits:
            if not isinstance(c, dict):
                errors.append(f"{bv} credits 项不是映射")
                continue
            name = str(c.get("name", "")).strip()
            role = str(c.get("role", "")).strip()
            if not name:
                errors.append(f"{bv} 有一条 credit 缺 name")
                continue
            credit_names.add(name)
            if not role:
                warnings.append(f"{bv} / {name} 缺 role")
            if c.get("self") or is_self(name, None, cfg):
                continue
            if c.get("link") or people_link(name, people):
                continue
            staff_names = {(s.get("name") or "") for s in rec.get("staff") or []}
            owner_name = (rec.get("owner") or {}).get("name") or ""
            if name in staff_names or name == owner_name:
                continue
            unlinked.add(name)

        for item in extract_desc_credits(rec.get("desc") or ""):
            name = item.get("name") or ""
            if not name or is_self(name, None, cfg):
                continue
            if name not in credit_names:
                uncredited.add(f"{bv} / {name}")

    for bv in works:
        if bv not in auto_bvs:
            warnings.append(f"{bv} 不在 videos.json / works.auto.json（下架？）")
    if featured_count == 0:
        warnings.append("没有 featured；WORKS 会纯按播放量排序")
    elif featured_count < 4:
        warnings.append(f"featured 只有 {featured_count} 部，TOP 精选可能不足 4 部")

    print(f"[check] 错误 {len(errors)} / 警告 {len(warnings) + len(missing_cat) + len(unlinked) + len(uncredited)}")
    if missing_cat:
        print(f"  缺 category（{len(missing_cat)} 部）：")
        for bv, title in missing_cat[:10]:
            print(f"    - {bv} {title[:48]}")
        if len(missing_cat) > 10:
            print(f"    … 其余 {len(missing_cat) - 10} 部")
    if unlinked:
        print(f"  无链接人名（{len(unlinked)}）：{', '.join(sorted(unlinked)[:12])}")
    if uncredited:
        print(f"  未进 Credits 的 @（{len(uncredited)}）：")
        for item in sorted(uncredited)[:10]:
            print(f"    - {item}")
        if len(uncredited) > 10:
            print(f"    … 其余 {len(uncredited) - 10} 条")
    if warnings:
        print(f"  其他警告（{len(warnings)}）：")
        for w in warnings[:10]:
            print(f"    - {w}")
        if len(warnings) > 10:
            print(f"    … 其余 {len(warnings) - 10} 条")
    if errors:
        print("  错误：")
        for e in errors[:20]:
            print(f"    - {e}")
        if len(errors) > 20:
            print(f"    … 其余 {len(errors) - 20} 条")
        return 1
    print("  → 可以运行 bili_fetch_works.py --merge")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="生成/校验作品标注")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="生成/补全 works.manual.yaml")
    group.add_argument("--check", action="store_true", help="校验标注")
    args = parser.parse_args()
    if args.init:
        return run_init()
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
