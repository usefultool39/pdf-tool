import os
from pathlib import Path

from pdf2image import convert_from_path


def _detect_poppler_path():
    """Return a Poppler bin path if one is configured locally; otherwise use PATH."""
    candidates = [
        os.environ.get("POPPLER_PATH"),
        Path(__file__).resolve().parents[1] / "poppler" / "Library" / "bin",
        Path(__file__).resolve().parents[1] / "poppler" / "bin",
    ]
    for item in candidates:
        if not item:
            continue
        path = Path(item)
        if path.exists():
            return str(path)
    return None


POPPLER_PATH = _detect_poppler_path()


def pdf_range_to_images(pdf_path, start_page, end_page,
                        out_dir="out_images", fmt="png", dpi=300):
    """
    把 PDF 的连续页导出为图片：
    [start_page, end_page]（包含）
    """
    if start_page > end_page:
        raise ValueError("start_page 不能大于 end_page")

    # 让输出目录固定在【当前脚本所在目录】下面
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    options = {
        "pdf_path": pdf_path,
        "dpi": dpi,
        "fmt": fmt,
        "first_page": start_page,
        "last_page": end_page,
    }
    if POPPLER_PATH:
        options["poppler_path"] = POPPLER_PATH

    try:
        images = convert_from_path(**options)
    except Exception as exc:
        raise RuntimeError(
            "PDF 转图片需要 Poppler。请把 Poppler 放到项目目录下的 poppler/Library/bin，"
            "或设置环境变量 POPPLER_PATH，或把 Poppler bin 加入系统 PATH。"
        ) from exc

    for offset, img in enumerate(images):
        page_num = start_page + offset  # 真实页码
        out_path = os.path.join(out_dir, f"page_{page_num}.{fmt}")
        img.save(out_path, fmt.upper())
        print(f"✅ 已保存: {out_path}")

    print(f"总共导出 {len(images)} 页（第 {start_page} 页 到 第 {end_page} 页）。")
    print(f"图片都在这个文件夹里：{out_dir}")


if __name__ == "__main__":
    from paths import enter_archive_cwd

    enter_archive_cwd()
    # ===== 只改这里这几个参数就行 =====
    # pdf 用相对路径时：相对当前工作目录 archive/（把 PDF 放在 archive/ 下）
    pdf_path   = "output_final.pdf"
    start_page = 15               # 起始页（包含）
    end_page   = 29               # 结束页（包含）
    # 输出目录由 pdf_range_to_images 内部固定为「本脚本所在目录 cli/」下的子文件夹，不是 cwd
    out_dir    = "export_15_28"

    pdf_range_to_images(pdf_path, start_page, end_page, out_dir, fmt="png", dpi=300)
