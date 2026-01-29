import os
import json
import hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark


# ========== 配置 ==========
load_dotenv("ppt_agent/env_template.env")  # 读取 env
for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(k, None)

BASE_DIR = Path(r"D:\mypptAgent")  # 项目根目录
SAVE_DIR = BASE_DIR / "kb" / "images"          # 图片保存目录
JSON_PATH = BASE_DIR / "kb" / "images" / "images.json"  # 你的 images.json

API_KEY = os.environ.get("SEEDREAN_API_KEY")  # 你环境变量名保持一致
MODEL = "doubao-seedream-4-5-251128"

PROMPT = "生成一个科技感很强的机器人图片，扁平插画风，商务PPT配图，16:9横版，留白，不要文字，不要水印。"
CAPTION = "科技感机器人概念图（封面/未来趋势/智能化）"   # ✅ 你想写入 images.json 的 caption


# ========== 工具函数 ==========
def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def guess_ext_from_url(url: str) -> str:
    # 从 url 路径猜扩展名，猜不到就 png
    path = urlparse(url).path.lower()
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        if path.endswith(ext):
            return ext
    return ".png"

def download_image(url: str, out_file: Path, timeout: int = 120) -> None:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    out_file.write_bytes(r.content)

def load_images_json(json_path: Path) -> list:
    if not json_path.exists():
        return []
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # JSON 损坏时可选择备份/重建
        raise RuntimeError(f"images.json 不是合法 JSON：{json_path}")

def save_images_json(json_path: Path, items: list) -> None:
    json_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def append_image_entry(json_path: Path, rel_path: str, caption: str, url: str | None = None) -> None:
    items = load_images_json(json_path)

    # 去重：同 path 不重复写
    if any(it.get("path") == rel_path for it in items):
        return

    entry = {"path": rel_path, "caption": caption}
    if url:
        entry["url"] = url  # 可选：保留原始来源，方便追溯

    items.append(entry)
    save_images_json(json_path, items)


# ========== 主流程 ==========
def main():
    ensure_dir(SAVE_DIR)

    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=API_KEY,
    )

    resp = client.images.generate(
        model=MODEL,
        prompt=PROMPT,
        size="2K",
        response_format="url",
        watermark=False,
    )

    img_url = resp.data[0].url
    print("generated url:", img_url)

    # 文件名：用 prompt 哈希 + 扩展名（避免冲突）
    h = hashlib.md5(PROMPT.encode("utf-8")).hexdigest()[:10]
    ext = guess_ext_from_url(img_url)
    filename = f"gen_{h}{ext}"

    out_file = SAVE_DIR / filename
    download_image(img_url, out_file)
    print("saved to:", out_file)

    # 写入 images.json：建议写相对路径（你原来就是 kb/images/xxx）
    rel_path = f"kb/images/{filename}"
    append_image_entry(JSON_PATH, rel_path, CAPTION, url=img_url)

    print("appended to images.json:", JSON_PATH)


if __name__ == "__main__":
    main()
