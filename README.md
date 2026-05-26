# cli-anything-cocoscreator

通过命令行操作 [Cocos Creator 3.8.8](https://www.cocos.com/creator) 项目，支持资产查询和构建。适用于 AI Agent 和自动化脚本。

## 安装

```bash
git clone git@github.com:OscargwStudio/cli-anything-cocoscreator.git
cd cli-anything-cocoscreator
pip install -e .
```

需要 Python 3.10+。

## 配置编辑器路径

工具按以下优先级查找 CocosCreator 可执行文件：

1. `--creator-path PATH` 命令行参数
2. `COCOS_CREATOR` 环境变量
3. macOS 默认路径：`/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator`
4. 系统 `PATH` 中的 `CocosCreator`

**Windows** 建议设置环境变量：

```powershell
[System.Environment]::SetEnvironmentVariable("COCOS_CREATOR", "C:\CocosDashboard\resources\.editors\Creator\3.8.8\CocosCreator.exe", "User")
```

> 资产查询命令（`asset meta/uuid/deps/refs`、`project assets`）**不依赖编辑器**，无需安装 Cocos Creator 即可使用。

## 命令

### `info`

查看工具和后端信息。

```bash
cli-anything-cocoscreator info
cli-anything-cocoscreator info --json
```

---

### `project info`

查看项目目录结构。

```bash
cli-anything-cocoscreator project info /path/to/project
```

---

### `project assets`

列出项目所有资产（不含 `.meta` 文件）。

```bash
cli-anything-cocoscreator project assets /path/to/project --limit 50
```

---

### `asset meta`

读取资产的 `.meta` 文件。

```bash
cli-anything-cocoscreator asset meta /path/to/project assets/MySprite.png
```

---

### `asset uuid`

打印资产的 UUID。

```bash
cli-anything-cocoscreator asset uuid /path/to/project assets/MyScript.ts
```

---

### `asset deps`

查询该资产依赖哪些资产（出向引用）。

```bash
cli-anything-cocoscreator asset deps /path/to/project assets/prefab/MyPrefab.prefab
# 隐藏无法解析的 UUID（引擎内置资产等）
cli-anything-cocoscreator asset deps /path/to/project assets/prefab/MyPrefab.prefab --hide-unresolved
```

---

### `asset refs`

查询哪些文件引用了该资产（入向引用）。

Cocos Creator 3.x 在 prefab/scene 中以 23 位压缩 UUID 存储脚本引用，工具已自动处理，无需手动转换。

```bash
# 默认：输出引用文件列表和 UUID
cli-anything-cocoscreator asset refs /path/to/project assets/script/MyComponent.ts

# 详细模式：显示行号和匹配文本
cli-anything-cocoscreator asset refs /path/to/project assets/script/MyComponent.ts --verbose

# 通过 UUID 直接搜索
cli-anything-cocoscreator asset refs /path/to/project --uuid 45987cf6-555a-4248-8005-8a04fa602d01

# 扫描范围包含 .meta 文件
cli-anything-cocoscreator asset refs /path/to/project assets/MyTexture.png --include-meta
```

---

### `build`

调用 CocosCreator 编辑器后端构建项目。

```bash
# 先预览命令，不实际执行
cli-anything-cocoscreator build /path/to/project --platform web-mobile --dry-run

# Debug 构建
cli-anything-cocoscreator build /path/to/project --platform web-mobile --debug

# Release 构建，附加参数
cli-anything-cocoscreator build /path/to/project --platform android --option outputName=myapp

# 设置超时（秒）
cli-anything-cocoscreator build /path/to/project --platform ios --timeout 600
```

支持平台：`web-mobile`、`web-desktop`、`android`、`ios`、`mac`、`windows` 等。

---

### `run`（透传）

直接将参数透传给 CocosCreator 可执行文件。

```bash
cli-anything-cocoscreator run -- --help
cli-anything-cocoscreator run -- --project /path/to/project --build platform=web-mobile
```

## 全局参数

| 参数 | 说明 |
|------|------|
| `--json` | 输出机器可读的 JSON |
| `--json-output` | `--json` 的别名 |
| `--creator-path PATH` | 指定 CocosCreator 可执行文件路径 |

## 资产路径说明

资产路径支持**绝对路径**或**相对于项目根目录的路径**：

```bash
# 绝对路径
cli-anything-cocoscreator asset uuid /Users/me/MyGame /Users/me/MyGame/assets/Hero.ts

# 相对路径（推荐）
cli-anything-cocoscreator asset uuid /Users/me/MyGame assets/Hero.ts
```
