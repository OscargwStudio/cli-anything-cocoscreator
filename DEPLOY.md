# cli-anything-cocoscreator 部署指南

> 将本文档粘贴给 AI，AI 可自动完成部署。

## 任务目标

安装 `cli-anything-cocoscreator` CLI 工具，使其可在终端直接调用。

## 前置条件检查

在开始前，依次确认：

1. **Python 版本** ≥ 3.10
   ```bash
   python3 --version
   ```
2. **pip 可用**
   ```bash
   pip3 --version
   ```
3. **Cocos Creator 3.8.8 已安装**（仅构建功能需要，资产查询不依赖它）

## 第一步：克隆仓库

```bash
git clone git@github.com:OscargwStudio/cli-anything-cocoscreator.git
cd cli-anything-cocoscreator
```

> 如果没有 SSH Key，改用 HTTPS：
> ```bash
> git clone https://github.com/OscargwStudio/cli-anything-cocoscreator.git
> ```

## 第二步：安装

```bash
pip install -e .
```

安装完成后验证：

```bash
cli-anything-cocoscreator --help
```

出现帮助输出即安装成功。

## 第三步：配置 Cocos Creator 路径（按平台）

工具按以下优先级自动查找可执行文件：

1. `--creator-path` 命令行参数
2. 环境变量 `COCOS_CREATOR`
3. 平台默认路径（见下表）

| 平台 | 默认路径 |
|------|---------|
| macOS | `/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator` |
| Windows | `C:\CocosDashboard\resources\.editors\Creator\3.8.8\CocosCreator.exe` |
| Linux | 不适用（Cocos Creator 无官方 Linux 版） |

**macOS**：默认路径存在则无需额外配置。

**Windows**：建议设置环境变量（永久生效）：

```powershell
# PowerShell（当前用户）
[System.Environment]::SetEnvironmentVariable(
  "COCOS_CREATOR",
  "C:\CocosDashboard\resources\.editors\Creator\3.8.8\CocosCreator.exe",
  "User"
)
```

或在每次调用时指定：

```bash
cli-anything-cocoscreator --creator-path "C:\path\to\CocosCreator.exe" info
```

## 验证

```bash
# 查看工具信息
cli-anything-cocoscreator info

# 查看项目资产（替换为实际项目路径）
cli-anything-cocoscreator project assets /path/to/cocos-project --limit 10

# 查询资产引用
cli-anything-cocoscreator asset refs /path/to/project assets/MyScript.ts
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `command not found` | pip 安装路径不在 PATH | 运行 `pip show cli-anything-cocoscreator` 查看安装位置，将其 `bin/` 加入 PATH |
| `Cocos Creator executable not found` | 未找到编辑器 | 设置 `COCOS_CREATOR` 环境变量或使用 `--creator-path` |
| `Asset not found` | 路径错误 | 资产路径可以是绝对路径或相对于项目根目录的相对路径 |
| Python 版本不满足 | 系统 Python 过旧 | 用 `pyenv` 或官网安装 Python 3.10+ |

## 卸载

```bash
pip uninstall cli-anything-cocoscreator
```
