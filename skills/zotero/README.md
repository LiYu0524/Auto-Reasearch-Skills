# Zotero 文献库管理

通过 [zotero-mcp](https://github.com/54yyyu/zotero-mcp) 连接 Zotero 文献库与 Claude Code。

## 安装

```bash
pip install zotero-mcp
claude mcp add-json "zotero" '{"command":"zotero-mcp","env":{"ZOTERO_LOCAL":"true"}}'
```

## 前置要求

- Zotero 桌面版正在运行
- 安装 [Better BibTeX](https://retorque.re/zotero-better-bibtex/) 插件（推荐）

## 功能

### 文献搜索（MCP 工具）
- 按关键词、作者、标签搜索
- 语义向量搜索（需配置 embedding model）

### PDF 注释提取
- 提取高亮文本、手写/文本笔记、批注和评论
- 支持图片注释

### 元数据管理
- 获取论文元数据（标题、作者、摘要、DOI）
- 列出收藏夹和标签
- 导出引用（BibTeX、CSL-JSON）

### 论文保存（zotero_save.py）

通过 Zotero Web API 保存论文，支持多种输入方式：

```bash
# 通过 arXiv ID 保存
python zotero_save.py --arxiv 2301.12345 --collection "Egocentric Video"

# 通过 DOI 保存
python zotero_save.py --doi 10.1234/example --collection "Survey"

# 通过 URL 自动识别保存
python zotero_save.py --url https://arxiv.org/abs/2301.12345

# 从 arxiv_survey.py 的 JSONL 批量导入
python zotero_save.py --from-jsonl ./arxiv.jsonl --collection "Survey"

# 手动指定元数据
python zotero_save.py --title "Paper Title" --authors "First Last; Second Author" --year 2024

# 列出所有文献集
python zotero_save.py --list-collections

# 查看配置指南
python zotero_save.py --setup
```

## 配置

### Zotero MCP Server（本地模式，推荐）

直接连接本地 Zotero 数据库，无需网络：
```json
{"command": "zotero-mcp", "env": {"ZOTERO_LOCAL": "true"}}
```

### Zotero MCP Server（Cloud 模式）

通过 Zotero Web API 连接：
```json
{"command": "zotero-mcp", "env": {"ZOTERO_API_KEY": "your-key", "ZOTERO_USER_ID": "your-id"}}
```

### zotero_save.py 环境变量

`zotero_save.py` 通过 Zotero Web API 保存论文，需要配置以下环境变量：

```bash
export ZOTERO_API_KEY="your-api-key"      # 从 https://www.zotero.org/settings/keys 获取
export ZOTERO_LIBRARY_ID="your-library-id" # 同一页面可见的数字 ID
```

运行 `python zotero_save.py --setup` 查看详细配置指南。

## 使用示例

直接在 Claude Code 中用自然语言请求：

```
"搜索我 Zotero 里关于 egocentric video understanding 的论文"
"提取 'Smith 2024' 这篇论文的所有 PDF 注释"
"列出 'ACM MM 2026' 收藏夹里的论文"
"导出选中论文的 BibTeX"
"把这篇 arXiv 论文保存到 Zotero 的 Survey 文献集"
```
