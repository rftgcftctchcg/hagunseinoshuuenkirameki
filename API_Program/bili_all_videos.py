# bili_all_videos.py
# 用法:
#   1) pip install -r requirements.txt
#   2) 复制 secrets.local.example.json 为 secrets.local.json，填入 SESSDATA
#      或设置环境变量 BILI_SESSDATA
#   3) python bili_all_videos.py

import hashlib
import json
import os
import random
import sys
import time
import urllib.parse
from functools import reduce
from pathlib import Path

import requests

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==================== 配置区 ====================
UID = "1016873598"
PAGE_SIZE = 50                    # 每页数量，接口上限 50
BASE_DIR = Path(__file__).resolve().parent
SECRETS_FILE = BASE_DIR / "secrets.local.json"
OUTPUT_FILE = BASE_DIR / "videos.json"       # 结果输出文件
CACHE_FILE = BASE_DIR / "wbi_cache.json"     # WBI 密钥缓存
CACHE_TTL = 12 * 3600             # 缓存有效期 12 小时
REQUEST_DELAY = (0.8, 1.8)        # 每页请求间隔（秒），避免触发风控
MAX_RETRY = 3                     # 单页最大重试次数


def load_sessdata() -> str:
    """读取 SESSDATA：环境变量优先，其次本地 secrets.local.json；找不到就明确报错。"""
    env_value = os.environ.get("BILI_SESSDATA", "").strip()
    if env_value:
        return env_value
    if SECRETS_FILE.exists():
        try:
            data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
            value = str(data.get("sessdata", "")).strip()
        except Exception as exc:
            raise SystemExit(f"[!] 读取 {SECRETS_FILE} 失败: {exc}") from exc
        if value:
            return value
    raise SystemExit(
        "[!] 缺少 SESSDATA。请设置环境变量 BILI_SESSDATA，"
        f"或复制 secrets.local.example.json 为 {SECRETS_FILE.name} 并填写。"
    )

API_ARC_SEARCH = "https://api.bilibili.com/x/space/wbi/arc/search"
API_NAV = "https://api.bilibili.com/x/web-interface/nav"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# B站固定 64 位重排表
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61,
    26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36,
    20, 34, 44, 52,
]


# ==================== Session & WBI ====================
def create_session() -> requests.Session:
    """创建带 Cookie 与基础请求头的 Session，并先访问首页获取 buvid3 等指纹 Cookie。"""
    sessdata = load_sessdata()
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Referer": f"https://space.bilibili.com/{UID}/video",
        "Origin": "https://www.bilibili.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    try:
        s.get("https://www.bilibili.com/", timeout=10)  # 获取 buvid3 / buvid4 等
    except Exception as e:
        print(f"[!] 访问首页失败（不影响主流程）: {e}")
    s.cookies.set("SESSDATA", sessdata, domain=".bilibili.com")
    return s


def _load_cache():
    try:
        d = json.loads(Path(CACHE_FILE).read_text(encoding="utf-8"))
        if time.time() - d["ts"] < CACHE_TTL and d.get("img_key") and d.get("sub_key"):
            return d["img_key"], d["sub_key"]
    except Exception:
        pass
    return None


def _save_cache(img_key: str, sub_key: str):
    Path(CACHE_FILE).write_text(
        json.dumps({"img_key": img_key, "sub_key": sub_key, "ts": time.time()}, ensure_ascii=False),
        encoding="utf-8",
    )


def get_wbi_keys(session: requests.Session, force: bool = False):
    """获取 WBI 密钥（img_key, sub_key），带本地缓存。"""
    if not force:
        cached = _load_cache()
        if cached:
            return cached

    r = session.get(API_NAV, timeout=10).json()
    if r.get("code") != 0:
        raise RuntimeError(f"获取 nav 失败: {r}")
    wbi = r["data"].get("wbi_img") or {}
    img_url, sub_url = wbi.get("img_url", ""), wbi.get("sub_url", "")
    if not img_url or not sub_url:
        raise RuntimeError(f"nav 未返回 wbi_img，可能 Cookie 失效: {r}")

    img_key = img_url.rsplit("/", 1)[-1].split(".")[0]
    sub_key = sub_url.rsplit("/", 1)[-1].split(".")[0]
    _save_cache(img_key, sub_key)
    login = r["data"].get("isLogin", False)
    print(f"[i] WBI 密钥已获取 | 登录态: {login}")
    return img_key, sub_key


def _get_mixin_key(orig: str) -> str:
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, "")[:32]


def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """为参数添加 wts 和 w_rid 签名。"""
    mixin_key = _get_mixin_key(img_key + sub_key)
    params = dict(params)
    params["wts"] = round(time.time())
    params = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params)
    params["w_rid"] = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return params


# ==================== 拉取逻辑 ====================
def fetch_page(session, img_key, sub_key, pn: int):
    """拉取一页投稿，带风控重试。返回 (code, data_json)。"""
    for attempt in range(1, MAX_RETRY + 1):
        params = {
            "mid": UID,
            "pn": pn,
            "ps": PAGE_SIZE,
            "order": "pubdate",
            "platform": "web",
            "web_location": "1550101",
        }
        signed = enc_wbi(params, img_key, sub_key)
        try:
            resp = session.get(API_ARC_SEARCH, params=signed, timeout=15)
            data = resp.json()
        except Exception as e:
            print(f"  [!] 第 {pn} 页请求异常: {e}")
            time.sleep(2 * attempt)
            continue

        code = data.get("code")
        if code == 0:
            return code, data

        # -352 风控 / -412 请求被拦截 / -799 请求过于频繁 / -509 超频
        if code in (-352, -412, -799, -509):
            wait = attempt * 3
            print(f"  [!] 第 {pn} 页触发风控 code={code}，{wait}s 后重试 ({attempt}/{MAX_RETRY})")
            time.sleep(wait)
            # 重试时刷新一次 WBI 密钥
            try:
                img_key, sub_key = get_wbi_keys(session, force=True)
            except Exception:
                pass
            continue
        return code, data
    return -1, {"code": -1, "message": "重试耗尽"}


def extract_video(v: dict) -> dict:
    """从 vlist 元素中提取关键字段。"""
    return {
        "bvid": v.get("bvid"),
        "aid": v.get("aid"),
        "title": v.get("title"),
        "description": v.get("description"),
        "created": v.get("created"),              # 发布时间戳
        "created_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.get("created", 0))),
        "length": v.get("length"),                # 时长 mm:ss
        "play": v.get("play"),                    # 播放
        "comment": v.get("comment"),              # 评论
        "video_review": v.get("video_review"),    # 弹幕
        "favorites": v.get("favorites"),          # 收藏
        "pic": v.get("pic"),
        "url": f"https://www.bilibili.com/video/{v.get('bvid')}",
    }


def main():
    print(f"[i] 目标 UID: {UID}")
    session = create_session()
    img_key, sub_key = get_wbi_keys(session)

    all_videos, seen = [], set()
    pn, total = 1, None

    while True:
        code, data = fetch_page(session, img_key, sub_key, pn)
        if code != 0:
            print(f"[✗] 第 {pn} 页失败: {data}")
            break

        d = data["data"]
        page_info = d.get("page") or {}
        total = page_info.get("count", total)
        vlist = (d.get("list") or {}).get("vlist") or []

        for v in vlist:
            item = extract_video(v)
            if item["bvid"] and item["bvid"] not in seen:
                seen.add(item["bvid"])
                all_videos.append(item)

        print(f"[✓] 第 {pn} 页: 本页 {len(vlist)} 条 | 累计 {len(all_videos)}/{total}")

        if not vlist or (total is not None and len(all_videos) >= total):
            break

        pn += 1
        time.sleep(random.uniform(*REQUEST_DELAY))

    # 按发布时间倒序（与接口 order=pubdate 保持一致，稳妥起见再排一次）
    all_videos.sort(key=lambda x: x.get("created") or 0, reverse=True)

    result = {
        "mid": UID,
        "total": total if total is not None else len(all_videos),
        "fetched": len(all_videos),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "videos": all_videos,
    }
    Path(OUTPUT_FILE).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[完成] 共获取 {len(all_videos)} 个视频，已保存到 {OUTPUT_FILE}")
    if all_videos:
        print("示例前 3 条：")
        for v in all_videos[:3]:
            print(f"  - {v['bvid']} | {v['created_str']} | {v['title']}")


if __name__ == "__main__":
    main()