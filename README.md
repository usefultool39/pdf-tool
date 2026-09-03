> **PDF 工具箱（PDF Tool）**：本地运行、无需上传的 PDF 处理工具集——图片转 PDF、合并、删页、插入、页面重排、PDF 转图片，全部在本机完成。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0%2B-lightgrey?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/tests-pytest-brightgreen" alt="Tests">
</p>

# PDF Tool

**PDF Tool** 是一个本地运行的 PDF 工具集，提供简洁的 Web 界面，无需上传文件到第三方服务，所有处理都在本机完成。

## 功能一览

| 功能 | 说明 |
|---|---|
| 🖼️ 图片转 PDF | 多张图片合成为一个 PDF，支持自动旋转为横向 |
| 🔗 PDF 合并 | 按顺序合并多个 PDF 文件 |
| ✂️ 删除页面 | 支持单页、连续页、混合范围（如 `1,3-5,8`） |
| 📄 插入 PDF | 在指定位置插入另一个 PDF（开头/结尾/指定页前/后） |
| 🔄 页面重排 | 竖版页面排到横版页面前面，适合混合方向文档 |
| 📐 统一尺寸 | 将所有横向页面统一为相同尺寸 |
| 🖨️ PDF 转图片 | 导出为 PNG/JPEG，可调 DPI、限制文件大小、合并为长图 |

## 快速开始

### Windows

双击 `启动.bat`，脚本自动完成：检查 Python → 创建虚拟环境 → 安装依赖 → 启动服务 → 打开浏览器。

### macOS / Linux

```bash
chmod +x start.sh && ./start.sh
```

也可双击 `启动.command`（macOS）。

### 手动启动

<details>
<summary>展开查看</summary>

**Windows**

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

</details>

启动后访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)（端口被占用时自动切换）。

## 使用指南

1. 打开 Web 页面，选择功能标签
2. 上传 PDF 或图片文件
3. 填写参数（页码、插入位置、导出格式等）
4. 点击处理，下载生成的文件

页码从 1 开始，支持格式：

```
1           → 第 1 页
1,3,5       → 第 1、3、5 页
1-5         → 第 1 至 5 页
1,3-5,8     → 混合格式
```

## 项目结构

```
pdf-tool/
├── app.py                 # Flask Web 应用入口
├── requirements.txt       # 运行依赖
├── requirements-dev.txt   # 测试依赖
├── tests/                 # pytest 自动化测试
├── 启动.bat               # Windows 一键启动
├── 启动.command           # macOS 一键启动
├── start.sh               # macOS / Linux 启动脚本
├── cli/                   # 命令行辅助工具
│   ├── fun.py             #   图片合成 PDF
│   ├── to_picture.py      #   PDF 导出图片
│   └── paths.py           #   路径工具
└── archive/               # 本地工作目录（不提交）
```

## 技术细节

### PDF 转图片

Web 端使用 **PyMuPDF（fitz）**，无需额外安装 Poppler。多页导出采用逐页渲染、逐页写盘策略，避免内存溢出。参数范围：

- DPI：36–600
- 文件大小限制：0–51200 KB（仅 JPG）
- 长图像素上限：6000 万像素

### CLI 工具

`cli/to_picture.py` 使用 `pdf2image`，按以下优先级查找 Poppler：

1. 环境变量 `POPPLER_PATH`
2. `poppler/Library/bin`
3. `poppler/bin`
4. 系统 `PATH`

## 测试

```bash
pip install -r requirements-dev.txt
pytest
```

CI 在 Ubuntu、macOS、Windows 上自动运行，覆盖 Python 3.10 / 3.12。

## 常见问题

<details>
<summary>找不到 Python</summary>

安装 Python 3.10+，Windows 需勾选 "Add python.exe to PATH"。
</details>

<details>
<summary>依赖安装失败</summary>

首次运行需要联网。检查网络后重试，或手动执行 `pip install -r requirements.txt`。
</details>

<details>
<summary>上传大文件失败</summary>

默认限制 100MB，修改 `app.py` 中的 `MAX_CONTENT_LENGTH` 可调整。
</details>

<details>
<summary>PDF 处理失败</summary>

可能原因：文件损坏、加密 PDF、页码范围无效、输出尺寸过大。先用小文件测试。
</details>

## 许可证

[MIT](LICENSE)