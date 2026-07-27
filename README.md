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

### 命令行模式

```bash
videotool -<opt> <value> [-o <output_dir>] [-n <name>] [--format <fmt>] <input_video>
```

| Option | Description |
|--------|-------------|
| `-f N` | Extract one frame every N frames |
| `-t N` | Extract exactly N evenly-spaced frames |
| `-o DIR` | Output directory (default: `<video_name>_frames/` in the same folder as the video) |
| `-n NAME` | Output image filename prefix (default: `frame`). e.g. `-n pic` → `pic_000001.jpg` |
| `--format` | Output image format: `jpg` (default) or `png` |

### 交互模式（v1.1+）

如果省略视频路径，程序会进入交互模式，逐步提示你输入：

```bash
# 只指定参数，不指定视频路径 → 自动进入交互模式
videotool -f 10
videotool -t 100
```

交互流程：

1. **提示输入视频源路径** — 可以拖入文件，自动去掉引号
2. **提示输入输出路径** — 直接回车则默认在视频同级目录创建 `{视频名}_frames/` 文件夹

```
==================================================
  videotool - Interactive Mode
==================================================

请输入视频源路径: C:\Videos\demo.mp4
  [OK] 视频: C:\Videos\demo.mp4

请输入输出路径 (直接回车则默认):
  → C:\Videos\demo_frames
  使用默认路径: C:\Videos\demo_frames
```

### Examples

```bash
# 命令行模式：提取每 10 帧
videotool -f 10 video.mp4

# 命令行模式：提取 100 帧
videotool -t 100 video.mp4

# 命令行模式：自定义输出目录和格式
videotool -f 30 -o ./my_frames --format png video.mp4

# 自定义输出文件名前缀 → pic_000001.jpg, pic_000002.jpg, ...
videotool -f 10 -n pic video.mp4

# 交互模式：只给参数，交互输入路径
videotool -f 10
videotool -t 100
```

## Requirements

- Python >= 3.8
- opencv-python >= 4.5（自动安装）

## Supported Video Formats

All formats supported by OpenCV/FFmpeg, including:
MP4, AVI, MOV, MKV, WMV, FLV, WebM, and more.

> **Windows 中文路径兼容：** v1.1+ 已修复 `cv2.imwrite` 不支持非 ASCII 路径的问题，视频和输出路径可以包含中文等 Unicode 字符。

## Troubleshooting

| 问题 | 解决方法 |
|------|----------|
| `videotool: command not found` | 改用 `python -m videotool` |
| pip SSL / 代理报错 | 用方法三 `python setup.py install` |
| `ImportError: No module named cv2` | `pip install opencv-python` 或 `conda install opencv` |
| 运行了但没有输出图片 | 升级到最新版（v1.1 修复了中文路径和帧数检测问题） |
| 视频帧数无法检测 | v1.1+ 会自动逐帧扫描，稍慢但可正常转换 |

## License

MIT
