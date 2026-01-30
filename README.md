# CiteCheck（文献管理与 DOI 元数据补全工具）

CiteCheck 是一个前后端分离的 Web 小项目：支持注册/登录、添加与管理文献条目，并提供 **DOI 元数据一键补全**（从开放元数据源获取标题/作者/年份等），同时生成 **GB/T 7714** 格式参考文献字符串，帮助写论文时更快整理参考文献。

> 技术栈：FastAPI + SQLModel(SQLite) + React + TypeScript + Vite

---

## ✨ 功能概览

- ✅ 用户注册/登录（JWT Token）
- ✅ 文献条目管理（新增 / 列表 / 删除）
- ✅ DOI 一键补全（从开放元数据源尝试获取文献元信息）
- ✅ 生成 GB/T 7714 参考文献格式（MVP）
- ✅ 前后端一键启动（开发环境）

---

## 📦 项目结构

```text
citecheck/
  backend/                # FastAPI 后端
    app/
    requirements.txt
  frontend/               # React + Vite 前端
    src/
    package.json
  package.json            # 根目录一键启动脚本（npm run dev）

```

## ✅ 运行环境要求

Node.js（建议 18+，你本机已安装）

Python 3.10+（建议）

Windows / macOS / Linux 均可（本项目以 Windows 开发测试）

## 🚀 本地开发运行（推荐）
### 1）后端（FastAPI）
```text
cd backend
若你已有 venv 可跳过创建
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

打开 API 文档：

http://127.0.0.1:8000/docs

### 2）前端（Vite）
```
cd frontend
npm install
npm run dev
```


打开网页：

http://localhost:5173

### ⚡ 根目录一键启动（可选）

在项目根目录执行：

```
npm install
npm run dev
```

该命令会并行启动：

后端： http://127.0.0.1:8000

前端： http://localhost:5173

## 🧭 使用说明

打开前端页面：http://localhost:5173

注册一个账号（邮箱+密码）

登录后进入 Dashboard

在“新建文献（MVP）”区域：

可手动填写 title / authors / year

或输入 DOI 后点击「DOI 一键补全」自动填充（部分 DOI 可能在开放元数据源查不到）

点击「保存」保存到“我的文献”

列表里可查看 GB/T 7714 结果并可删除条目

## 📝 说明与限制（MVP）

DOI 一键补全依赖开放元数据源：部分来自 CNKI 的 DOI 可能无法被开放库识别。

当前为 MVP：支持基本字段与基础格式化，后续可扩展更多文献类型、导入/导出（BibTeX/RIS）、多来源检索等。