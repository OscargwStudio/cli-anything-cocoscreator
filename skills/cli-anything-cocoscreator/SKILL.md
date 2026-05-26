---
name: cli-anything-cocoscreator
description: 通过命令行操作 Cocos Creator 3.8.8 项目，支持资产查询和构建。
---

# cli-anything-cocoscreator

用于自动化 Cocos Creator 3.8.8 项目的 CLI 工具。封装编辑器可执行文件，支持 `--json` 输出。

## 全局参数

| 参数 | 说明 |
|------|------|
| `--json` | 输出机器可读的 JSON |
| `--creator-path PATH` | 指定 CocosCreator 可执行文件路径（优先于 `COCOS_CREATOR` 环境变量） |

## 命令

### info

```bash
cli-anything-cocoscreator info
```

### project

```bash
cli-anything-cocoscreator project info <项目路径>
cli-anything-cocoscreator project assets <项目路径> --limit 50
```

### asset

```bash
# 读取资产的 .meta 文件
cli-anything-cocoscreator asset meta <项目路径> <资产路径>

# 打印资产 UUID
cli-anything-cocoscreator asset uuid <项目路径> <资产路径>

# 查询该资产依赖哪些资产（出向引用）
cli-anything-cocoscreator asset deps <项目路径> <资产路径> [--hide-unresolved]

# 查询哪些文件引用了该资产（入向引用）
# 支持 .ts/.js 脚本：自动在 prefab/scene 中搜索压缩 UUID
cli-anything-cocoscreator asset refs <项目路径> <资产路径> [--verbose] [--include-meta]
cli-anything-cocoscreator asset refs <项目路径> --uuid <uuid> [--verbose]
```

`asset refs` 默认输出文件列表和 UUID；加 `--verbose` 显示行号和匹配文本。

### build

```bash
cli-anything-cocoscreator build <项目路径> --platform web-mobile [--debug] [--dry-run] [--timeout 300]
cli-anything-cocoscreator build <项目路径> --platform android --option key=value
```

建议先用 `--dry-run` 确认构建命令后再正式执行。

### run（透传）

```bash
cli-anything-cocoscreator run -- --help
cli-anything-cocoscreator run -- --project /path/to/proj --build platform=web-mobile
```

## 备注

- 资产路径支持绝对路径或相对于项目根目录的相对路径。
- Cocos Creator 3.x 在 prefab/scene 中以 23 位压缩 UUID 存储脚本引用，`asset refs` 已自动处理。
- `asset deps` 扫描资产文件内容中的 UUID，并通过 `.meta` 文件解析为实际路径。
