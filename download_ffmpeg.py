import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

tools_dir = Path("D:/tools")
tools_dir.mkdir(parents=True, exist_ok=True)
zip_path = tools_dir / "ffmpeg.zip"

print("Downloading FFmpeg...")
urllib.request.urlretrieve("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip", zip_path)

print("Extracting FFmpeg...")
unzip_dir = tools_dir / "unzip"
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(unzip_dir)

bin_dir = None
for p in unzip_dir.glob("**/bin/ffmpeg.exe"):
    bin_dir = p.parent
    break

if bin_dir and bin_dir.exists():
    ffmpeg_target = tools_dir / "ffmpeg"
    if ffmpeg_target.exists():
        shutil.rmtree(ffmpeg_target)
    shutil.move(str(bin_dir), str(ffmpeg_target))
    print(f"FFmpeg successfully placed at {ffmpeg_target}")
else:
    print("Could not find bin/ffmpeg.exe in extracted archive.")

if zip_path.exists():
    zip_path.unlink()
if unzip_dir.exists():
    shutil.rmtree(unzip_dir)
