---
name: paper-banana
description: 学术插图生成 - 使用 PaperBanana 多智能体框架从方法文本自动生成框架图和统计图
allowed-tools: Bash, Read, Write
user-invocable: true
---

# Paper Banana - 学术插图生成

使用 PaperBanana 多智能体框架（Planner → Visualizer → Critic 循环）从论文方法章节文本自动生成学术插图。

## 前置安装

```bash
# 1. 克隆 PaperBanana
git clone https://github.com/paperbanana/PaperBanana.git ~/PaperBanana

# 2. 安装依赖
cd ~/PaperBanana
pip install -r requirements.txt

# 3. 配置模型（编辑 configs/model_config.yaml）
# 设置 OpenAI 兼容的 API base URL、API key 和模型名
```

## 核心命令

```bash
SCRIPT=~/.claude/skills/auto-research/skills/paper-banana/scripts/generate_figure.py

# 基本用法
python3 $SCRIPT \
  --content "方法文本（Markdown格式）" \
  --caption "Figure 1: 框架图标题" \
  --output ./figure.png

# 从文件读取内容
python3 $SCRIPT \
  --content @method_section.md \
  --caption "Figure 1: Pipeline overview" \
  --output ./fig1.png

# 高质量模式（完整管线 + 更多迭代）
python3 $SCRIPT \
  --content @method.md \
  --caption "Figure 2: Architecture" \
  --output ./fig2.png \
  --exp-mode demo_full \
  --critic-rounds 5

# 生成统计图
python3 $SCRIPT \
  --content "实验结果数据..." \
  --caption "Figure 3: Performance comparison" \
  --output ./fig3.png \
  --task plot
```

## CLI 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--content` | (必填) | 方法文本，支持 `@filepath` 从文件读取 |
| `--caption` | (必填) | 图表标题 / 视觉意图描述 |
| `--output` | (必填) | 输出图片路径（.png / .jpg） |
| `--task` | `diagram` | 任务类型：`diagram`（框架图）或 `plot`（统计图） |
| `--aspect-ratio` | `16:9` | 宽高比 |
| `--exp-mode` | `demo_planner_critic` | 管线模式 |
| `--retrieval-setting` | `none` | 参考检索策略 |
| `--critic-rounds` | `3` | 最大 Critic 迭代轮数 |
| `--image-model-name` | (配置文件) | 覆盖图像生成模型 |
| `--paperbanana-dir` | `~/PaperBanana` | PaperBanana 项目路径 |

## 管线模式对比

| 模式 | 流程 | 适用场景 |
|------|------|----------|
| `demo_planner_critic` | Planner → Visualizer → Critic × N | 快速生成，推荐默认 |
| `demo_full` | Retriever → Planner → Stylist → Visualizer → Critic × N | 更精美，含风格优化 |

## 输出格式

脚本输出 JSON 到 stdout：

```json
{
  "status": "success",
  "output": "/absolute/path/to/figure.png",
  "format": "PNG",
  "size": "1920x1080",
  "exp_mode": "demo_planner_critic",
  "task": "diagram"
}
```

失败时：

```json
{
  "status": "error",
  "message": "错误描述"
}
```

## 与 drawio 的区别

| 维度 | paper-banana | drawio |
|------|-------------|--------|
| 输出类型 | 位图（PNG/JPG），AI 生成 | 矢量图（XML），手动/规则生成 |
| 适用场景 | 论文方法图、框架图、示意图 | 流程图、ER图、架构图 |
| 可编辑性 | 不可编辑（位图） | 完全可编辑（XML） |
| 视觉质量 | 高（AI风格化） | 中（工程图风格） |
| 生成速度 | 慢（多轮 AI 调用） | 快（直接生成 XML） |
