# """
# Run this ONCE from the project root (same folder as manage.py) to download
# the two OpenCV DNN model files used for face recognition:

#     models/face_detection_yunet_2023mar.onnx   (~350 KB)
#     models/face_recognition_sface_2021dec.onnx (~37 MB)

# Usage:
#     python download_models.py
# """

# import os
# import urllib.request

# MODELS_DIR = "models"

# FILES = {
#     "face_detection_yunet_2023mar.onnx":
#         "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
#         "face_detection_yunet_2023mar.onnx",
#     "face_recognition_sface_2021dec.onnx":
#         "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/"
#         "face_recognition_sface_2021dec.onnx",
# }


# def main():
#     os.makedirs(MODELS_DIR, exist_ok=True)

#     for filename, url in FILES.items():
#         dest = os.path.join(MODELS_DIR, filename)
#         if os.path.exists(dest):
#             print(f"[SKIP] {filename} already exists.")
#             continue

#         print(f"[DOWNLOAD] {filename} ...")
#         try:
#             urllib.request.urlretrieve(url, dest)
#             print(f"[OK] Saved to {dest}")
#         except Exception as e:
#             print(f"[ERROR] Could not download {filename}: {e}")
#             print(f"        You can also download it manually from:\n        {url}")
#             print(f"        and place it at: {dest}")

#     print("\nDone. Model files should now be inside the 'models/' folder.")


# if __name__ == "__main__":
#     main()

"""
Run this ONCE from the project root (same folder as manage.py) to download
the two OpenCV DNN model files used for face recognition:

    models/face_detection_yunet_2023mar.onnx   (~233 KB)
    models/face_recognition_sface_2021dec.onnx (~37 MB)

Usage:
    python download_models.py

NOTE: The opencv_zoo GitHub repo now stores these files with Git LFS, so
raw.githubusercontent.com only serves a tiny text "pointer" file instead of
the real weights. This script downloads from the Hugging Face mirror
instead (which serves the real bytes), and falls back to GitHub if needed.
Either way, every download is verified before it's kept.
"""

import os
import urllib.request

MODELS_DIR = "models"

# (filename, minimum expected size in bytes, list of URLs to try in order)
FILES = [
    (
        "face_detection_yunet_2023mar.onnx",
        200_000,  # real file is ~233 KB
        [
            "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx",
            "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        ],
    ),
    (
        "face_recognition_sface_2021dec.onnx",
        30_000_000,  # real file is ~37 MB
        [
            "https://huggingface.co/opencv/face_recognition_sface/resolve/main/face_recognition_sface_2021dec.onnx",
            "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
        ],
    ),
]

# Some hosts reject requests with no User-Agent header.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; model-downloader/1.0)"}


def _looks_like_lfs_pointer(path):
    """Detect a Git LFS pointer text file masquerading as the real model."""
    try:
        with open(path, "rb") as f:
            head = f.read(200)
        return head.startswith(b"version https://git-lfs")
    except OSError:
        return False


def _download(url, dest):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as response, open(dest, "wb") as out:
        while True:
            chunk = response.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    all_ok = True

    for filename, min_size, urls in FILES:
        dest = os.path.join(MODELS_DIR, filename)

        if os.path.exists(dest) and os.path.getsize(dest) >= min_size and not _looks_like_lfs_pointer(dest):
            print(f"[SKIP] {filename} already exists and looks valid.")
            continue

        downloaded = False
        for url in urls:
            print(f"[DOWNLOAD] {filename} from {url} ...")
            try:
                _download(url, dest)
            except Exception as e:
                print(f"[ERROR] Could not download from {url}: {e}")
                continue

            size = os.path.getsize(dest) if os.path.exists(dest) else 0

            if _looks_like_lfs_pointer(dest):
                print("[FAIL] Got a Git LFS pointer file instead of real data, trying next source...")
                os.remove(dest)
                continue

            if size < min_size:
                print(f"[FAIL] Downloaded file is only {size} bytes (expected >= {min_size}), trying next source...")
                if os.path.exists(dest):
                    os.remove(dest)
                continue

            print(f"[OK] Saved {filename} ({size:,} bytes) to {dest}")
            downloaded = True
            break

        if not downloaded:
            all_ok = False
            print(f"[MANUAL DOWNLOAD NEEDED] {filename} could not be downloaded automatically.")
            print(f"        Open this link in your browser and save the file to: {dest}")
            print(f"        {urls[0]}")

    print()
    if all_ok:
        print("Done. Both model files are in the 'models/' folder and ready to use.")
    else:
        print("Some files still need to be downloaded manually (see MANUAL DOWNLOAD NEEDED above).")


if __name__ == "__main__":
    main()