# videotool

A CLI tool to convert video files to image sequences.

## Installation

### From GitHub (recommended)

```bash
pip install git+https://github.com/zhiming040518/vediotool.git
```

### From local source

```bash
git clone git@github.com:zhiming040518/vediotool.git
cd vediotool
pip install .
```

### Editable development install

```bash
pip install -e .
```

## Usage

```bash
videotool -<opt> <value> [-o <output_dir>] [--format <fmt>] <input_video>
```

### Options

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

## Supported Video Formats

All formats supported by OpenCV/FFmpeg, including:
MP4, AVI, MOV, MKV, WMV, FLV, WebM, and more.

## License

MIT
