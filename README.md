# MOTO-HUB-modules-cn

官方模块目录 [vincenzobpt/MOTO-HUB-modules](https://github.com/vincenzobpt/MOTO-HUB-modules) 的**简体中文镜像**。

## 为什么存在

MOTO-HUB ADV-SOLO 的「模块」页卡片、仪表盘画廊、Flyby 音效清单，都是运行时从
`https://raw.githubusercontent.com/vincenzobpt/MOTO-HUB-modules/main/` 拉取的：

- `index.json` — 8 个模块的 `displayName` / `summary` / `tagline`，**官方只有英文、没有 i18n 字段**，
  所以任何汉化 APK 都改不到这些卡片文字；
- `dashboards/**` — 仪表盘目录、预览图与 `.mhd` 文件；
- `modules/*/card.webp` — 卡片配图；
- `sounds/**` — Flyby 音效清单（含 `.sig` 验签文件）。

本仓库把上述内容原样镜像（字节一致，因此签名校验不受影响），只把 `index.json` 里的三处文案
换成简体中文。配合把 APK 内的基址替换成本仓库地址（等长替换），模块卡片即可显示中文，
其余功能与官方完全一致——模块本体仍从官方仓库下载、签名校验照旧。

## 内容

| 路径 | 说明 |
|---|---|
| `index.json` | 中文版模块目录（由 `tools/modules-zh.json` 覆盖生成） |
| `dashboards/` | 官方仪表盘目录/预览图/`.mhd`，原样同步 |
| `modules/*/card.webp` | 模块卡片图，原样同步 |
| `sounds/` | Flyby 音效清单与签名，原样同步 |
| `tools/sync.py` | 同步脚本（官方有更新就跑一次） |
| `tools/modules-zh.json` | 模块 ID → 中文文案（新增模块时在这里补译文） |
| `.github/workflows/sync.yml` | 每天自动同步上游 |

## 手动同步

```bash
python3 tools/sync.py            # 拉取上游变更 + 重新生成中文 index.json
git add -A && git commit -m "sync" && git push
```

## 注意

- 目录结构与官方**必须保持一致**：APK 里被替换的只是基址，`dashboards/`、`modules/`、`sounds/` 等相对路径照旧。
- 若官方改了 `index.json` 的字段（新增字段/改结构），`tools/sync.py` 仍以官方为基准整体复制，
  只在有三处文案的字段上覆盖中文，不会丢字段。
- 上游如新增模块，同步脚本会打印 WARNING 并保留英文，补 `tools/modules-zh.json` 即可。
- 本仓库仅用于个人使用的中文本地化镜像，不修改任何模块本体。
