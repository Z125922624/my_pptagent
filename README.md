# ppt-agent（自动生成PPT）

这是一个「PPT Agent」示例项目：基于用户一句话需求，依次完成 **需求解析 → 大纲规划 → RAG 检索 → LLM 写 DeckSpec → 渲染 PPTX**。

本仓库包含：
- `backend/`：Python 后端（FastAPI）+ 你的 ppt_agent 生成链路
- `frontend/`：Web 前端（Vite + React）一键调用后端并下载 `.pptx`

## 一、整体流程（对应你当前代码的 Step1~4）

1. **Step1 需求解析（BriefSpec）**：将自然语言需求解析成结构化字段（topic/audience/slide_count/tone...）
2. **Step2 大纲规划（OutlineItem 列表）**：生成每一页标题、要点与是否需要检索
3. **Step3 RAG 检索（Evidence Packs）**：用 FAISS + Embedding 从知识库里拿到文本片段与候选图片
4. **Step4 写 DeckSpec + 渲染**：并发生成每页的 blocks（cards/bullets/fact/example/image...），最后用 `python-pptx` 生成 `pptx`

## 二、快速开始（本地运行）

### 1) 后端

```bash
cd backend
cp .env.example env_template.env
# 填入 DEEPSEEK_API_KEY（可选填 SEEDREAM_API_KEY）

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn api_server:app --reload --port 8000
```

健康检查：打开 `http://localhost:8000/api/health`

### 2) 前端

```bash
cd frontend
npm i
npm run dev
```

打开 `http://localhost:5173`，输入需求后点击「生成并下载 PPTX」。

> 说明：当前接口是“同步生成”以便演示；如果你要上线，建议做成异步任务队列（Celery/RQ）+ 轮询/WS。

## 三、API 说明

- `GET /api/health`：健康检查
- `POST /api/generate`：生成并直接返回 `pptx` 文件

请求 JSON：
```json
{
  "prompt": "生成一个关于机器人为主题的PPT...",
  "ensure_image": true,
  "concurrency": 4
}
```

返回：`application/vnd.openxmlformats-officedocument.presentationml.presentation`（文件下载）

## 四、为开源做的最小整理（你代码里值得顺手改的点）

- **统一导入路径**：原代码里有 `from write_one_slide import ...` 这种相对脚本导入，作为 package 使用时会失败；本仓库已做了最小修正。
- **环境变量**：建议只保留一个 `.env.example`，运行时读 `.env`（或 `env_template.env`）。
- **目录约定**：
  - 知识库索引放 `backend/kb_store/`
  - 图片缓存放 `backend/kb/images/`，并用 `images.json` 做索引
- **可观测性**：可以把每个 Step 的产物（brief/outline/deck.json）落盘，方便排查。

## License

按你的需要补充。
