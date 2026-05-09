# PDF Tool

PDF Tool 是一个本地运行的 PDF 工具集，提供 Flask Web 页面，适合在 Windows 电脑上快速处理常见 PDF 任务。文件只在本机处理，不需要上传到第三方服务。

维护者：U2Tool39

## 功能

- 图片转 PDF：支持多张图片合成为一个 PDF，可选择统一横向页面。
- PDF 合并：按上传顺序合并多个 PDF 文件。
- 删除页面：支持输入单页、连续页和混合页码范围，例如 `1,3-5,8`。
- 插入 PDF：把一个 PDF 插入到另一个 PDF 的开头、结尾、指定页前或指定页后。
- 页面重排：把 PDF 页面重新排列为先奇数页、再偶数页的顺序，适合部分扫描件整理。
- 统一尺寸：把 PDF 页面统一到横向 A4 尺寸，页面内容居中缩放。
- PDF 转图片：使用 PyMuPDF 将指定页范围导出为 PNG 或 JPEG，并可设置 DPI、最大图片大小和压缩质量。

## 环境要求

- Windows 10/11
- Python 3.10 或更新版本
- 首次运行需要联网安装 Python 依赖

主要依赖见 [requirements.txt](requirements.txt)：

- Flask
- pypdf
- Pillow
- PyMuPDF
- pdf2image

## 快速开始

### Windows 一键启动

双击 `启动.bat`。

脚本会自动完成：

1. 检查 Python 版本。
2. 创建本地虚拟环境 `.venv`。
3. 安装依赖。
4. 启动 Web 服务。
5. 打开浏览器访问本地页面。

如果浏览器没有自动打开，复制终端里显示的地址访问，一般是：

```text
http://127.0.0.1:5000
```

如果 5000 端口被占用，程序会自动寻找可用端口。

### 手动启动

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

## 使用说明

1. 打开本地 Web 页面。
2. 选择需要的功能标签。
3. 上传 PDF 或图片文件。
4. 填写页码、插入位置、导出格式等参数。
5. 点击处理按钮。
6. 下载生成的文件。

页码从 1 开始。删除页面等功能支持如下格式：

```text
1
1,3,5
1-5
1,3-5,8
```

## PDF 转图片说明

Web 页面中的 PDF 转图片功能使用 PyMuPDF，不需要额外安装 Poppler。

`cli/to_picture.py` 是命令行辅助脚本，使用 `pdf2image`，可能需要 Poppler。脚本会按以下顺序查找 Poppler：

1. 环境变量 `POPPLER_PATH`
2. 项目目录下的 `poppler/Library/bin`
3. 项目目录下的 `poppler/bin`
4. 系统 `PATH`

如果只使用 Web 页面，可以忽略 Poppler。

## 项目结构

```text
pdf-tool/
├── app.py              # Flask Web UI 和 PDF 处理接口
├── requirements.txt    # Python 依赖
├── 启动.bat            # Windows 一键启动脚本
├── cli/                # 命令行辅助脚本
└── archive/            # 本地工作目录，不提交个人 PDF 或图片
```

## 发布注意

`archive/` 是本地临时工作目录，用于放置个人 PDF、图片和导出结果。公开仓库只保留目录说明，不包含用户文件。

`.venv/`、`__pycache__/`、导出的 PDF/图片和压缩包等文件已通过 `.gitignore` 排除。

## 常见问题

### 启动时提示找不到 Python

安装 Python 3.10 或更新版本，并在安装时勾选 `Add python.exe to PATH`，然后重新运行 `启动.bat`。

### 首次运行依赖安装失败

首次运行需要联网下载依赖。检查网络后重新运行 `启动.bat`。

### 上传大文件失败

当前 Web 服务默认限制上传大小为 100MB。可以在 `app.py` 中调整：

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
```

### PDF 处理失败

可能原因包括文件损坏、加密 PDF、页码范围无效、输出图片尺寸过大等。请先用小文件测试，确认 PDF 可正常打开。

## 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
