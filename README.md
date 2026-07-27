# videotool

A CLI tool to convert video files to image sequences.

## Installation

### 方法一：pip 在线安装（推荐，需 pip >= 22）

```bash
pip install git+https://github.com/zhiming040518/vediotool.git
```

### 方法二：git clone + 本地安装（网络受限环境）

```bash
git clone git@github.com:zhiming040518/vediotool.git
cd vediotool
pip install .
```

### 方法三：如果 pip 有代理/SSL 问题

```bash
git clone git@github.com:zhiming040518/vediotool.git
cd vediotool
python setup.py install        # 或 python setup.py develop
```

> `python setup.py install` 完全不走 pip 网络栈，适合内网/代理环境。

### 方法四：没有 git？直接下载 zip

浏览器打开 https://github.com/zhiming040518/vediotool → Code → Download ZIP，解压后：

```bash
cd vediotool
python setup.py install
```

---

## Usage

```bash
videotool -<opt> <value> [-o <output_dir>] [--format <fmt>] <input_video>
```

| Option | Description |
|--------|-------------|
| `-f N` | Extract one frame every N frames |
| `-t N` | Extract exactly N evenly-spaced frames |
| `-o DIR` | Output directory (default: `<video_name>_frames/`) |
| `--format` | Output image format: `jpg` (default) or `png` |

### Examples

```bash
# Extract every 10th frame
videotool -f 10 video.mp4

# Extract exactly 100 evenly-spaced frames
videotool -t 100 video.mp4

# Custom output directory and format
videotool -f 30 -o ./my_frames --format png video.mp4
```

## Requirements

- Python >= 3.8
- opencv-python >= 4.5（自动安装）

## Supported Video Formats

All formats supported by OpenCV/FFmpeg, including:
MP4, AVI, MOV, MKV, WMV, FLV, WebM, and more.

## Troubleshooting

| 问题 | 解决方法 |
|------|----------|
| `videotool: command not found` | 改用 `python -m videotool` |
| pip SSL / 代理报错 | 用方法三 `python setup.py install` |
| `ImportError: No module named cv2` | `pip install opencv-python` 或 `conda install opencv` |

## License

MIT
