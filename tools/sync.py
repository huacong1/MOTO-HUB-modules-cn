# -*- coding: utf-8 -*-
"""把官方 MOTO-HUB-modules 的目录内容同步到本镜像仓库，并把 index.json 换成中文。

为什么需要这个镜像：MOTO-HUB ADV-SOLO 的「模块」页（以及仪表盘画廊、Flyby 音效清单）
都是从 https://raw.githubusercontent.com/vincenzobpt/MOTO-HUB-modules/main/ 远程读取的，
其中 index.json 里 8 个模块的标题/简介是纯英文、没有多语言字段。把 APK 里的这串基址
等长替换成本仓库地址后，模块卡片就会显示中文。

同步规则：
  - dashboards/**、modules/*/card.webp、sounds/**  原样复制（字节一致，签名/校验不受影响）
  - index.json                                     用 tools/modules-zh.json 覆盖三个文案字段
  - 官方新增了本仓库没有译文的模块时，保留英文并在结尾打印 WARNING（不会中断）

用法：python tools/sync.py            # 同步
      python tools/sync.py --check    # 只检查，不写文件（CI 里可用）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UPSTREAM = "vincenzobpt/MOTO-HUB-modules"
BRANCH = "main"
ROOT = Path(__file__).resolve().parent.parent
PREFIXES = ("dashboards/", "modules/", "sounds/")
UA = {"User-Agent": "moto-hub-modules-cn-sync", "Accept": "application/vnd.github+json"}


def api(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as f:
        return json.load(f)


def raw(path: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{UPSTREAM}/{BRANCH}/" + urllib.parse.quote(path)
    req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(req, timeout=120) as f:
        return f.read()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    tree = api(f"https://api.github.com/repos/{UPSTREAM}/git/trees/{BRANCH}?recursive=1")
    entries = [e for e in tree["tree"]
               if e["type"] == "blob" and (e["path"] == "index.json" or e["path"].startswith(PREFIXES))]
    zh_map = json.load(open(ROOT / "tools" / "modules-zh.json", encoding="utf-8"))

    changed, downloaded, warned = [], 0, []
    for e in entries:
        path = e["path"]
        dst = ROOT / path
        if path == "index.json":
            continue
        remote_sha = e["sha"]
        if dst.exists() and git_blob_sha(dst.read_bytes()) == remote_sha:
            continue
        if args.check:
            changed.append(path)
            continue
        data = raw(path)
        downloaded += 1
        if git_blob_sha(data) != remote_sha:
            print(f"WARNING: {path} 校验和不一致（下载内容与 API 不符）")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        changed.append(path)

    # ---- index.json：以官方为基准，覆盖三个文案字段
    upstream_index = json.loads(raw("index.json").decode("utf-8"))
    modules = []
    for m in upstream_index:
        z = zh_map.get(m["id"])
        nm = dict(m)
        if z:
            nm["displayName"] = z["displayName"] or m["displayName"]
            nm["summary"] = z["summary"]
            nm["tagline"] = z["tagline"]
        else:
            warned.append(m["id"])
        modules.append(nm)
    text = json.dumps(modules, ensure_ascii=False, indent=2) + "\n"
    idx_path = ROOT / "index.json"
    old = idx_path.read_text(encoding="utf-8") if idx_path.exists() else ""
    if old != text:
        changed.append("index.json")
        if not args.check:
            idx_path.write_text(text, encoding="utf-8", newline="\n")

    print(f"上游文件 {len(entries)} 个；本次变动 {len(changed)} 个；下载 {downloaded} 个")
    for p in changed:
        print("  ~", p)
    if warned:
        print("WARNING: 以下模块没有中文译文，保持英文：" + ", ".join(warned))
    return 0


if __name__ == "__main__":
    sys.exit(main())
