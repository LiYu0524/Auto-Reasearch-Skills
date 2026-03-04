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

### 文献搜索
- 按关键词、作者、标签搜索
- 语义向量搜索（需配置 embedding model）

### PDF 注释提取
- 提取高亮文本
- 提取手写/文本笔记
- 提取批注和评论
- 支持图片注释

### 元数据管理
- 获取论文元数据（标题、作者、摘要、DOI）
- 列出收藏夹和标签
- 导出引用（BibTeX、CSL-JSON）

### 高级功能
- 相似论文推荐（基于向量搜索）
- 引用网络分析
- 批量操作

## 使用示例

直接在 Claude Code 中用自然语言请求：

```
"搜索我 Zotero 里关于 egocentric video understanding 的论文"
"提取 'Smith 2024' 这篇论文的所有 PDF 注释"
"列出 'ACM MM 2026' 收藏夹里的论文"
"导出选中论文的 BibTeX"
```

## 配置选项

### 本地模式（推荐）
直接连接本地 Zotero 数据库，无需网络：
```json
{"command": "zotero-mcp", "env": {"ZOTERO_LOCAL": "true"}}
```

### Cloud 模式
通过 Zotero Web API 连接（需要 API Key）：
```json
{"command": "zotero-mcp", "env": {"ZOTERO_API_KEY": "your-key", "ZOTERO_USER_ID": "your-id"}}
```
