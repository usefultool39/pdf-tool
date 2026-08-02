import io
import zipfile

import pytest
from PIL import Image
from pypdf import PdfReader, PdfWriter

import app as pdf_app


def make_pdf(page_sizes):
    output = io.BytesIO()
    writer = PdfWriter()
    for width, height in page_sizes:
        writer.add_blank_page(width=width, height=height)
    writer.write(output)
    output.seek(0)
    return output


def make_image(mode="RGB", size=(30, 50)):
    colors = {
        "RGB": (220, 30, 30),
        "RGBA": (220, 30, 30, 128),
        "L": 128,
    }
    output = io.BytesIO()
    Image.new(mode, size, colors[mode]).save(output, format="PNG")
    output.seek(0)
    return output


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_app, "UPLOAD_FOLDER", str(tmp_path))
    pdf_app.app.config.update(TESTING=True)
    with pdf_app.app.test_client() as test_client:
        yield test_client


def download_json_result(client, response):
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True, payload
    download = client.get(payload["download_url"])
    assert download.status_code == 200
    return payload, download.data


def test_index_and_pdf_info(client):
    assert client.get("/").status_code == 200
    response = client.post(
        "/api/pdf_info",
        data={"pdf": (make_pdf([(300, 500), (500, 300)]), "info.pdf")},
        content_type="multipart/form-data",
    )
    assert response.get_json()["info"] == "总页数：2 | 竖版：1 | 横版：1"


def test_images_to_pdf_handles_transparency_and_landscape(client):
    response = client.post(
        "/api/images_to_pdf",
        data={
            "images": (make_image("RGBA"), "transparent.png"),
            "force_landscape": "on",
        },
        content_type="multipart/form-data",
    )
    _, pdf_bytes = download_json_result(client, response)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) == 1
    page = reader.pages[0]
    assert float(page.mediabox.width) > float(page.mediabox.height)


def test_merge_pdfs(client):
    response = client.post(
        "/api/merge_pdfs",
        data={
            "pdfs": [
                (make_pdf([(300, 500)]), "first.pdf"),
                (make_pdf([(500, 300), (300, 500)]), "second.pdf"),
            ]
        },
        content_type="multipart/form-data",
    )
    _, pdf_bytes = download_json_result(client, response)
    assert len(PdfReader(io.BytesIO(pdf_bytes)).pages) == 3


def test_remove_pages_and_reject_empty_document(client):
    response = client.post(
        "/api/remove_pages",
        data={
            "pdf": (make_pdf([(300, 500)] * 4), "source.pdf"),
            "pages": "1,3-4",
        },
        content_type="multipart/form-data",
    )
    _, pdf_bytes = download_json_result(client, response)
    assert len(PdfReader(io.BytesIO(pdf_bytes)).pages) == 1

    rejected = client.post(
        "/api/remove_pages",
        data={
            "pdf": (make_pdf([(300, 500)]), "single.pdf"),
            "pages": "1",
        },
        content_type="multipart/form-data",
    )
    payload = rejected.get_json()
    assert payload["success"] is False
    assert "至少保留 1 页" in payload["message"]


@pytest.mark.parametrize("position,page_index", [("start", 1), ("end", 1), ("before", 2), ("after", 2)])
def test_insert_pdf_positions(client, position, page_index):
    response = client.post(
        "/api/insert_pdf",
        data={
            "main_pdf": (make_pdf([(300, 500)] * 2), "main.pdf"),
            "insert_pdf": (make_pdf([(500, 300)]), "insert.pdf"),
            "position": position,
            "page_index": str(page_index),
        },
        content_type="multipart/form-data",
    )
    _, pdf_bytes = download_json_result(client, response)
    assert len(PdfReader(io.BytesIO(pdf_bytes)).pages) == 3


def test_insert_pdf_rejects_invalid_position(client):
    response = client.post(
        "/api/insert_pdf",
        data={
            "main_pdf": (make_pdf([(300, 500)]), "main.pdf"),
            "insert_pdf": (make_pdf([(500, 300)]), "insert.pdf"),
            "position": "unknown",
        },
        content_type="multipart/form-data",
    )
    assert response.get_json() == {"success": False, "message": "插入位置无效"}


def test_reorder_pages_puts_portrait_first(client):
    response = client.post(
        "/api/reorder_pages",
        data={"pdf": (make_pdf([(500, 300), (300, 500)]), "mixed.pdf")},
        content_type="multipart/form-data",
    )
    _, pdf_bytes = download_json_result(client, response)
    pages = PdfReader(io.BytesIO(pdf_bytes)).pages
    assert float(pages[0].mediabox.height) > float(pages[0].mediabox.width)
    assert float(pages[1].mediabox.width) > float(pages[1].mediabox.height)


def test_normalize_landscape_sizes(client):
    response = client.post(
        "/api/normalize_landscape",
        data={
            "pdf": (make_pdf([(500, 300), (600, 400), (300, 500)]), "mixed.pdf")
        },
        content_type="multipart/form-data",
    )
    _, pdf_bytes = download_json_result(client, response)
    pages = PdfReader(io.BytesIO(pdf_bytes)).pages
    assert (float(pages[0].mediabox.width), float(pages[0].mediabox.height)) == (500, 300)
    assert (float(pages[1].mediabox.width), float(pages[1].mediabox.height)) == (500, 300)
    assert (float(pages[2].mediabox.width), float(pages[2].mediabox.height)) == (300, 500)


def test_pdf_to_images_streams_pages_into_zip(client):
    response = client.post(
        "/api/pdf_to_images",
        data={
            "pdf": (make_pdf([(200, 300)] * 2), "source.pdf"),
            "start_page": "1",
            "end_page": "2",
            "dpi": "72",
            "format": "jpg",
            "max_size": "0",
        },
        content_type="multipart/form-data",
    )
    _, zip_bytes = download_json_result(client, response)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        assert archive.namelist() == ["page_1.jpg", "page_2.jpg"]


@pytest.mark.parametrize("dpi", ["0", "-100", "601"])
def test_pdf_to_images_rejects_unsafe_dpi(client, dpi):
    response = client.post(
        "/api/pdf_to_images",
        data={
            "pdf": (make_pdf([(200, 300)]), "source.pdf"),
            "start_page": "1",
            "end_page": "1",
            "dpi": dpi,
            "format": "jpg",
            "max_size": "0",
        },
        content_type="multipart/form-data",
    )
    payload = response.get_json()
    assert payload["success"] is False
    assert "DPI 必须" in payload["message"]


def test_long_image_pixel_limit(client, monkeypatch):
    monkeypatch.setattr(pdf_app, "MAX_LONG_IMAGE_PIXELS", 100)
    response = client.post(
        "/api/pdf_to_images",
        data={
            "pdf": (make_pdf([(200, 300)]), "source.pdf"),
            "start_page": "1",
            "end_page": "1",
            "dpi": "72",
            "format": "png",
            "long_image": "on",
            "max_size": "0",
        },
        content_type="multipart/form-data",
    )
    payload = response.get_json()
    assert payload["success"] is False
    assert "长图像素过大" in payload["message"]


def test_parse_page_range():
    assert pdf_app.parse_page_range("1,3-5,9", 6) == {1, 3, 4, 5}
    assert pdf_app.parse_page_range("5-3", 6) == {3, 4, 5}
    assert pdf_app.parse_page_range("bad", 6) == set()
