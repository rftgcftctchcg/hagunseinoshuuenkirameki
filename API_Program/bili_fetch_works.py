#!/usr/bin/env python3
# bili_fetch_works.py
# 用法:
#   python bili_fetch_works.py --auto      # 拉 47 条 view 详情 + 主页统计，写 data/works.auto.json
#   python bili_fetch_works.py --merge     # 合并 works.manual.yaml -> works.json / stats.json / docs
#   python bili_fetch_works.py --offline   # 同 --merge，不联网
#
# 依赖: PyYAML（仅 --merge/--offline 需要；--auto 只用标准库）
# 建议: pip install -r requirements.txt

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None  # type: ignore

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import yaml
except ImportError:  # --auto 不需要 PyYAML
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
API_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
CACHE_DIR = DATA_DIR / ".cache" / "view"
VIDEOS_FILE = API_DIR / "videos.json"
SECRETS_FILE = API_DIR / "secrets.local.json"
AUTO_FILE = DATA_DIR / "works.auto.json"
AUTO_STATS_FILE = DATA_DIR / "stats.auto.json"
MANUAL_FILE = DATA_DIR / "works.manual.yaml"
PEOPLE_FILE = DATA_DIR / "people.yaml"
WORKS_FILE = DATA_DIR / "works.json"
STATS_FILE = DATA_DIR / "stats.json"
DOC_FILE = DOCS_DIR / "works.generated.md"

SELF_MID = 1016873598
SELF_NAME = "破軍星の終焉煌めき"
SELF_ALIASES = [
    "永存瑶光_烛照周天",
    "在瑶光中永存",
    "破軍星の终焉煌めき",
    "Hagunseishn_Krmk",
]
SELF_ALT_MIDS = [3707010312833870]
TTL = 12 * 3600
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
CATEGORY_ORDER = ["二创剪辑", "VOCALOID", "原创曲", "搬运", "其他"]
_CST = timezone(timedelta(hours=8), "Asia/Shanghai")


def local_tz():
    """优先用 IANA 时区；Windows 未装 tzdata 时退回固定 UTC+8。"""
    if ZoneInfo is not None:
        try:
            return ZoneInfo("Asia/Shanghai")
        except Exception:
            pass
    return _CST


def now_text() -> str:
    return datetime.now(local_tz()).strftime("%Y-%m-%d %H:%M:%S")


def ensure_dirs() -> None:
    for d in (DATA_DIR, DOCS_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)


def load_sessdata() -> str | None:
    env_value = os.environ.get("BILI_SESSDATA", "").strip()
    if env_value:
        return env_value
    if SECRETS_FILE.exists():
        try:
            data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
            value = str(data.get("sessdata", "")).strip()
            if value:
                return value
        except Exception as exc:
            print(f"[!] 读取 {SECRETS_FILE.name} 失败: {exc}")
    return None


def http_json(url: str, cookie: str | None = None, timeout: int = 20) -> Any:
    headers = {
        "User-Agent": UA,
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
    }
    if cookie:
        headers["Cookie"] = f"SESSDATA={cookie}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_pic(pic: str | None) -> str:
    if not pic:
        return ""
    pic = pic.strip()
    if pic.startswith("//"):
        pic = "https:" + pic
    elif pic.startswith("http://"):
        pic = "https://" + pic[len("http://"):]
    return pic


def parse_length(text: str | None) -> int | None:
    if not text:
        return None
    parts = text.split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 2:
        return nums[0] * 60 + nums[1]
    if len(nums) == 3:
        return nums[0] * 3600 + nums[1] * 60 + nums[2]
    return None


def ts_to_str(ts: int | None) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(ts, local_tz()).strftime("%Y-%m-%d %H:%M:%S")


def as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fetch_view(bv: str, refresh: bool = False) -> tuple[dict[str, Any] | None, str]:
    """返回 (view data, source)。source: live/cache/stale/error。"""
    cache_path = CACHE_DIR / f"{bv}.json"
    cached: dict[str, Any] | None = None
    if cache_path.exists():
        try:
            obj = json.loads(cache_path.read_text(encoding="utf-8"))
            cached = obj.get("data")
            if not refresh and time.time() - float(obj.get("ts", 0)) < TTL:
                return cached, "cache"
        except Exception:
            cached = None

    last_error = ""
    for attempt in range(1, 4):
        try:
            payload = http_json(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}")
            code = payload.get("code")
            if code == 0 and payload.get("data"):
                data = payload["data"]
                cache_path.write_text(
                    json.dumps({"ts": time.time(), "data": data}, ensure_ascii=False),
                    encoding="utf-8",
                )
                return data, "live"
            last_error = f"code={code} {payload.get('message', '')}".strip()
            if code in (-352, -412, -799, -509):
                wait = 2 * attempt
                print(f"  [!] {bv} 触发风控 {last_error}，{wait}s 后重试 ({attempt}/3)")
                time.sleep(wait)
                continue
            break
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * attempt)

    if cached:
        print(f"  [!] {bv} 拉取失败（{last_error}），使用过期缓存")
        return cached, "stale"
    return None, f"error: {last_error}"


def build_auto_record(vlist: dict[str, Any], view: dict[str, Any], status: str) -> dict[str, Any]:
    stat = view.get("stat") or {}
    pages = view.get("pages") or []
    cid = pages[0].get("cid") if pages else view.get("cid")
    video_review = as_int(vlist.get("video_review"))
    danmaku = stat.get("danmaku")
    if danmaku is None:
        danmaku = video_review
    duration = view.get("duration")
    if duration is None:
        duration = parse_length(vlist.get("length"))
    pubdate = view.get("pubdate") or vlist.get("created")
    owner = view.get("owner") or {}
    staff = view.get("staff") or []
    stat_out = {
        "view": as_int(stat.get("view", vlist.get("play"))),
        "like": as_int(stat.get("like")),
        "coin": as_int(stat.get("coin")),
        "favorite": as_int(stat.get("favorite")),
        "danmaku": as_int(danmaku),
        "reply": as_int(stat.get("reply", vlist.get("comment"))),
        "share": as_int(stat.get("share")),
    }
    return {
        "bvid": vlist.get("bvid"),
        "aid": view.get("aid") or vlist.get("aid"),
        "cid": cid,
        "title": view.get("title") or vlist.get("title") or "",
        "desc": view.get("desc") or vlist.get("description") or "",
        "pic": normalize_pic(view.get("pic") or vlist.get("pic")),
        "duration": duration,
        "length": vlist.get("length") or "",
        "pubdate": pubdate,
        "created_str": vlist.get("created_str") or ts_to_str(pubdate),
        "owner": {
            "mid": owner.get("mid"),
            "name": owner.get("name") or "",
            "face": owner.get("face") or "",
        },
        "staff": [
            {
                "mid": s.get("mid"),
                "name": s.get("name") or "",
                "title": s.get("title") or "",
                "face": s.get("face") or "",
            }
            for s in staff
            if isinstance(s, dict)
        ],
        "copyright": view.get("copyright"),
        "stat": stat_out,
        "video_review": video_review,
        "status": status,
    }


def fetch_profile_stats(cookie: str | None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "generated_at": now_text(),
        "fans": None,
        "like_num": None,
        "archive_count": None,
        "total_view": None,
        "total_likes": None,
        "source": "card/upstat",
        "notes": [],
    }
    try:
        card = http_json("https://api.bilibili.com/x/web-interface/card?mid=1016873598")
        if card.get("code") == 0 and card.get("data"):
            data = card["data"]
            out["fans"] = data.get("card", {}).get("fans", data.get("follower"))
            out["like_num"] = data.get("like_num")
            out["archive_count"] = data.get("archive_count")
        else:
            out["notes"].append(f"card code={card.get('code')} {card.get('message', '')}")
    except Exception as exc:
        out["notes"].append(f"card {type(exc).__name__}: {exc}")

    try:
        upstat = http_json(
            "https://api.bilibili.com/x/space/upstat?mid=1016873598",
            cookie=cookie,
        )
        if upstat.get("code") == 0 and upstat.get("data"):
            data = upstat["data"]
            out["total_view"] = data.get("archive", {}).get("view")
            out["total_likes"] = data.get("likes")
        else:
            out["notes"].append(
                "upstat 无数据；需要有效 SESSDATA（API_Program/secrets.local.json 或 BILI_SESSDATA）"
            )
    except Exception as exc:
        out["notes"].append(f"upstat {type(exc).__name__}: {exc}")

    return out


def run_auto(args: argparse.Namespace) -> int:
    if not VIDEOS_FILE.exists():
        print(f"[!] 找不到 {VIDEOS_FILE}，请先运行 bili_all_videos.py")
        return 1
    ensure_dirs()
    videos = json.loads(VIDEOS_FILE.read_text(encoding="utf-8")).get("videos") or []
    if not videos:
        print("[!] videos.json 没有视频")
        return 1

    cookie = load_sessdata()
    if not cookie:
        print("[!] 未读到 SESSDATA：upstat 总播放会缺失；view 详情仍可拉取")

    records: list[dict[str, Any]] = []
    for i, v in enumerate(videos, 1):
        bv = v.get("bvid")
        data, source = fetch_view(bv, refresh=args.refresh)
        status = "ok" if data else "unavailable"
        record = build_auto_record(v, data or {}, status)
        record["source"] = source
        if not data:
            print(f"[{i:02d}/{len(videos)}] {bv} 失败: {source}")
        else:
            print(
                f"[{i:02d}/{len(videos)}] {bv} {record['stat']['view']:,} 播放 "
                f"({source}) {record['title'][:36]}"
            )
        records.append(record)
        if not args.no_delay and i < len(videos):
            time.sleep(random.uniform(0.55, 1.0))

    records.sort(key=lambda r: (r.get("pubdate") or 0, r.get("bvid") or ""))
    for i, r in enumerate(records, 1):
        r["no"] = i

    payload = {
        "schema": 1,
        "generated_at": now_text(),
        "mid": str(SELF_MID),
        "count": len(records),
        "videos": records,
    }
    AUTO_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] 写入 {AUTO_FILE}（{len(records)} 部）")

    stats = fetch_profile_stats(cookie)
    AUTO_STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] 写入 {AUTO_STATS_FILE}")
    if stats.get("notes"):
        for note in stats["notes"]:
            print(f"  [!] {note}")
    print(
        f"    粉丝={stats.get('fans')} 总获赞={stats.get('like_num')} "
        f"总播放={stats.get('total_view')} 投稿数={stats.get('archive_count')}"
    )
    return 0


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"[!] 找不到 {path}")
    data = safe_load_yaml(path)
    if not isinstance(data, dict):
        raise SystemExit(f"[!] {path} 不是 YAML 映射")
    return data


def safe_load_yaml(path: Path) -> Any:
    """读 YAML；出错时给出文件、行列和常见原因，而不是抛 traceback。"""
    if yaml is None:
        raise SystemExit("[!] 需要 PyYAML：pip install -r requirements.txt")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
        where = f"第 {mark.line + 1} 行第 {mark.column + 1} 列" if mark else "未知位置"
        problem = getattr(exc, "problem", None) or str(exc)
        print(f"[!] {path} YAML 语法错误（{where}）：{problem}")
        print('    常见原因：flow 映射 { role: ..., link: "..." } 的冒号后要留空格；URL 用双引号包住。')
        raise SystemExit(1)


def is_self(name: str | None, mid: Any, self_cfg: dict[str, Any]) -> bool:
    if mid is not None:
        try:
            if int(mid) in {int(self_cfg["mid"]), *[int(x) for x in self_cfg.get("altMids", [])]}:
                return True
        except (TypeError, ValueError):
            pass
    names = {self_cfg.get("name", SELF_NAME), *self_cfg.get("aliases", [])}
    return (name or "").strip() in names


def self_url() -> str:
    return f"https://space.bilibili.com/{SELF_MID}"


def space_url(mid: Any) -> str | None:
    if mid in (None, ""):
        return None
    return f"https://space.bilibili.com/{mid}"


def normalize_role(role: str) -> str:
    role = (role or "").strip().strip("：:")
    if not role:
        return ""
    aliases = {
        "原作": "原作者",
        "原作者": "原作者",
        "本家": "原作者",
        "mix": "Mix",
        "混音": "Mix",
        "tuning": "Tuning",
        "调校": "Tuning",
        "调教": "Tuning",
        "词": "词",
        "填词": "词",
        "lyric": "词",
        "曲": "曲",
        "作曲": "曲",
        "特别鸣谢": "鸣谢",
        "鸣谢": "鸣谢",
        "ust": "UST",
        "原曲": "原曲",
        "视频制作": "视频制作",
        "动画": "动画",
        "editor": "Editor",
    }
    parts = [p.strip() for p in role.split("/") if p.strip()]
    out = []
    for p in parts:
        out.append(aliases.get(p.lower(), aliases.get(p, p)))
    return "/".join(out) if out else role


def extract_desc_credits(desc: str) -> list[dict[str, str]]:
    """只解析带「角色：@名字」前缀的行，返回 [{role,name}]。"""
    import re

    out: list[dict[str, str]] = []
    for line in (desc or "").splitlines():
        m = re.match(r"^\s*([^：:]{1,24})[：:]\s*(.+)$", line)
        if not m:
            continue
        role = normalize_role(m.group(1))
        value = m.group(2)
        for name in re.findall(r"@([^\s@，,。；;：:、/]+)", value):
            name = name.strip()
            if name:
                out.append({"role": role, "name": name})
    return out


def people_link(name: str, people: dict[str, Any]) -> str | None:
    entry = people.get(name)
    if not isinstance(entry, dict):
        return None
    if entry.get("mid") not in (None, ""):
        return space_url(entry["mid"])
    if entry.get("url"):
        return str(entry["url"])
    return None


def build_credits(
    record: dict[str, Any],
    manual_work: dict[str, Any],
    people: dict[str, Any],
    self_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    owner = record.get("owner") or {}
    staff = record.get("staff") or []
    self_roles: list[str] = []
    normal: list[dict[str, Any]] = []

    def add_self_role(role: str) -> None:
        for part in normalize_role(role).split("/"):
            part = part.strip()
            if part and part not in self_roles:
                self_roles.append(part)

    def add_normal(role: str, name: str, link: str | None = None, self_flag: bool = False) -> None:
        name = (name or "").strip().lstrip("@")
        if not name:
            return
        if self_flag or is_self(name, None, self_cfg):
            add_self_role(role)
            return
        if link is None:
            link = people_link(name, people)
        key = (role, name)
        for item in normal:
            if (item["role"], item["name"]) == key:
                if link and not item.get("link"):
                    item["link"] = link
                return
        normal.append({"role": role, "name": name, **({"link": link} if link else {})})

    if owner.get("name"):
        add_normal("投稿方", owner["name"], space_url(owner.get("mid")))

    for s in staff:
        title = (s.get("title") or "制作").strip()
        name = (s.get("name") or "").strip()
        if not name:
            continue
        if is_self(name, s.get("mid"), self_cfg):
            if title not in ("UP主", "up主", "投稿方"):
                add_normal(title, name, self_url(), self_flag=True)
            continue
        if name == (owner.get("name") or "") and title in ("UP主", "up主"):
            continue
        add_normal(title, name, space_url(s.get("mid")))

    for item in extract_desc_credits(record.get("desc") or ""):
        add_normal(item["role"], item["name"])

    for item in (manual_work.get("credits") or []):
        if not isinstance(item, dict):
            continue
        role = normalize_role(str(item.get("role", "")))
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        if item.get("self") or is_self(name, None, self_cfg):
            add_self_role(role)
            continue
        link = item.get("link") or people_link(name, people)
        key = (role, name)
        for existing in normal:
            if (existing["role"], existing["name"]) == key:
                if link and not existing.get("link"):
                    existing["link"] = str(link)
                break
        else:
            normal.append({"role": role, "name": name, **({"link": str(link)} if link else {})})

    credits: list[dict[str, Any]] = []
    if self_roles:
        credits.append(
            {
                "role": " / ".join(self_roles),
                "name": self_cfg.get("name", SELF_NAME),
                "self": True,
                "link": self_url(),
            }
        )
    credits.extend(normal)
    return credits


def suggest_participation(record: dict[str, Any], self_cfg: dict[str, Any]) -> str:
    if record.get("status") == "unavailable":
        return "待确认（数据不可用）"
    if record.get("copyright") == 2:
        return "转载"
    owner = record.get("owner") or {}
    owner_self = is_self(owner.get("name"), owner.get("mid"), self_cfg)
    roles: list[str] = []
    for s in record.get("staff") or []:
        if is_self(s.get("name"), s.get("mid"), self_cfg):
            title = (s.get("title") or "").strip()
            if title and title not in ("UP主", "up主", "投稿方") and title not in roles:
                roles.append(title)
    if roles:
        return "联合投稿（" + " / ".join(roles) + "）"
    if not owner_self:
        return "代投（待确认）"
    return "全部制作"


def replace_self_aliases(text: str, self_cfg: dict[str, Any]) -> str:
    text = text or ""
    aliases = sorted(
        {a for a in self_cfg.get("aliases", []) if a and a != self_cfg.get("name")},
        key=len,
        reverse=True,
    )
    for alias in aliases:
        text = text.replace(alias, self_cfg.get("name", SELF_NAME))
    return text


def fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return ""

def md_escape(text: Any) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def run_merge(args: argparse.Namespace) -> int:
    if not AUTO_FILE.exists():
        print(f"[!] 找不到 {AUTO_FILE}，请先运行 bili_fetch_works.py --auto")
        return 1
    auto = json.loads(AUTO_FILE.read_text(encoding="utf-8"))
    manual = load_yaml(MANUAL_FILE)
    people_data = load_yaml(PEOPLE_FILE) if PEOPLE_FILE.exists() else {"people": {}}
    people = people_data.get("people") or {}
    self_cfg = manual.get("self") or {
        "mid": SELF_MID,
        "altMids": SELF_ALT_MIDS,
        "name": SELF_NAME,
        "aliases": SELF_ALIASES,
    }
    valid_categories = list((manual.get("categories") or {}).keys()) or CATEGORY_ORDER
    manual_works = manual.get("works") or {}
    if not isinstance(manual_works, dict):
        print(f"[!] {MANUAL_FILE} 的 works 不是映射")
        return 1

    auto_stats = None
    if AUTO_STATS_FILE.exists():
        auto_stats = json.loads(AUTO_STATS_FILE.read_text(encoding="utf-8"))

    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    invalid_categories: list[str] = []
    for rec in auto.get("videos") or []:
        bv = rec.get("bvid")
        mw = manual_works.get(bv) or {}
        category = (mw.get("category") or "").strip()
        if not category:
            category = "未分类"
            warnings.append(f"{bv} 缺 category → 未分类")
        elif category not in valid_categories:
            invalid_categories.append(f"{bv} category={category!r}")
            category = "未分类"

        participation = (mw.get("participation") or "").strip() or suggest_participation(rec, self_cfg)
        credits = build_credits(rec, mw, people, self_cfg)
        out = dict(rec)
        out["no"] = rec.get("no")
        out["category"] = category
        out["participation"] = participation
        out["credits"] = credits
        out["desc_display"] = replace_self_aliases(rec.get("desc") or "", self_cfg)
        out["featured"] = bool(mw.get("featured"))
        order = mw.get("featuredOrder")
        out["featured_order"] = int(order) if isinstance(order, (int, float)) else None
        out["hidden"] = bool(mw.get("hidden"))
        out["tags"] = mw.get("tags") or []
        records.append(out)

    records.sort(key=lambda r: (r.get("no") or 9999, r.get("pubdate") or 0))

    if invalid_categories:
        print(f"[!] 非法分类 {len(invalid_categories)} 条，--merge 已停止：")
        for item in invalid_categories[:20]:
            print(f"  - {item}")
        if len(invalid_categories) > 20:
            print(f"  … 其余 {len(invalid_categories) - 20} 条")
        print("    可用分类：" + " / ".join(valid_categories))
        return 1

    generated_at = now_text()
    works_payload = {
        "schema": 1,
        "generated_at": generated_at,
        "count": len(records),
        "self": self_cfg,
        "videos": records,
    }
    WORKS_FILE.write_text(json.dumps(works_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    sums = {
        key: sum(int((r.get("stat") or {}).get(key) or 0) for r in records)
        for key in ("view", "like", "coin", "favorite", "danmaku", "reply", "share")
    }
    categories = Counter(r.get("category") or "未分类" for r in records)
    max_view = max(records, key=lambda r: (r.get("stat") or {}).get("view") or 0, default=None)
    max_favorite = max(records, key=lambda r: (r.get("stat") or {}).get("favorite") or 0, default=None)
    max_interaction = max(
        records,
        key=lambda r: ((r.get("stat") or {}).get("danmaku") or 0) + ((r.get("stat") or {}).get("reply") or 0),
        default=None,
    )
    with_pub = [r for r in records if r.get("pubdate")]
    earliest = min(with_pub, key=lambda r: r["pubdate"], default=None)
    latest = max(with_pub, key=lambda r: r["pubdate"], default=None)

    def short(rec: dict[str, Any] | None, metric: str = "view") -> dict[str, Any] | None:
        if not rec:
            return None
        stat = rec.get("stat") or {}
        if metric == "interaction":
            value = (stat.get("danmaku") or 0) + (stat.get("reply") or 0)
        else:
            value = stat.get(metric)
        return {
            "bvid": rec.get("bvid"),
            "title": rec.get("title"),
            "value": value,
            "favorite": stat.get("favorite"),
            "danmaku": stat.get("danmaku"),
            "reply": stat.get("reply"),
            "pubdate": rec.get("pubdate"),
            "created_str": rec.get("created_str"),
        }

    stats_payload = {
        "schema": 1,
        "generated_at": generated_at,
        "profile": auto_stats
        or {
            "fans": None,
            "like_num": None,
            "archive_count": None,
            "total_view": None,
            "total_likes": None,
            "source": "missing",
        },
        "works": {
            "count": len(records),
            "sum": sums,
            "max_view": short(max_view, "view"),
            "max_favorite": short(max_favorite, "favorite"),
            "max_interaction": short(max_interaction, "interaction"),
            "earliest": short(earliest),
            "latest": short(latest),
        },
        "categories": dict(categories),
        "unclassified": categories.get("未分类", 0),
    }
    STATS_FILE.write_text(json.dumps(stats_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 作品索引（自动生成）",
        "",
        f"> 生成时间：{generated_at}（Asia/Shanghai） · 共 {len(records)} 部",
        "> 本文件由 `bili_fetch_works.py --merge` 生成，不要手改。",
        "",
        "| NO. | BV | 标题 | 发布 | 时长 | 播放 | 分类 | 参与度 | 投稿方 | 归属 |",
        "|---:|---|---|---|---:|---:|---|---|---|---|",
    ]
    for r in records:
        owner_name = (r.get("owner") or {}).get("name") or ""
        owner_mid = (r.get("owner") or {}).get("mid")
        owner_display = "本人" if is_self(owner_name, owner_mid, self_cfg) else owner_name
        if r.get("copyright") == 2:
            kind = "转载"
        elif r.get("staff"):
            kind = "联合投稿"
        elif is_self(owner_name, owner_mid, self_cfg):
            kind = "自制"
        else:
            kind = "其他"
        lines.append(
            "| {no:03d} | {bv} | {title} | {date} | {length} | {view} | {cat} | {part} | {owner} | {kind} |".format(
                no=r.get("no") or 0,
                bv=r.get("bvid"),
                title=md_escape(r.get("title")),
                date=(r.get("created_str") or "")[:10],
                length=md_escape(r.get("length")),
                view=fmt_int((r.get("stat") or {}).get("view")),
                cat=md_escape(r.get("category")),
                part=md_escape(r.get("participation")),
                owner=md_escape(owner_display),
                kind=kind,
            )
        )
    lines += [
        "",
        "## 统计",
        "",
        f"- 作品总数：{len(records)}",
        f"- 分类：{', '.join(f'{k} {v}' for k, v in categories.items())}",
        f"- 未分类：{categories.get('未分类', 0)}",
        f"- 作品合计播放：{sums['view']:,}",
        f"- 作品合计收藏：{sums['favorite']:,}",
        f"- UP 主总播放：{(auto_stats or {}).get('total_view')}",
        f"- 粉丝：{(auto_stats or {}).get('fans')}",
        "",
    ]
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DOC_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"[✓] 写入 {WORKS_FILE}（{len(records)} 部）")
    print(f"[✓] 写入 {STATS_FILE}")
    print(f"[✓] 写入 {DOC_FILE}")
    if warnings:
        print(f"[!] 警告 {len(warnings)} 条：")
        for w in warnings[:15]:
            print(f"  - {w}")
        if len(warnings) > 15:
            print(f"  … 其余 {len(warnings) - 15} 条")
    print(
        f"    分类：{dict(categories)}；未分类 {categories.get('未分类', 0)} 部"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="拉取并合并 bilibili 作品数据")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auto", action="store_true", help="拉取 view 详情 + 主页统计")
    group.add_argument("--merge", action="store_true", help="合并手动标注")
    group.add_argument("--offline", action="store_true", help="同 --merge，不联网")
    parser.add_argument("--refresh", action="store_true", help="忽略 view 缓存")
    parser.add_argument("--no-delay", action="store_true", help="不等待（调试用）")
    args = parser.parse_args()

    if args.auto:
        return run_auto(args)
    if args.merge or args.offline:
        return run_merge(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
