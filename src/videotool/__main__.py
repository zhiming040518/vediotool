"""videotool - Convert video files to image sequences.

Usage:
    videotool -f <interval> [-o <output_dir>] [-n <name>] [--format <fmt>] [<video> ...]
    videotool -t <count> [-o <output_dir>] [-n <name>] [--format <fmt>] [<video> ...]

    If no video is given, prompts interactively. Multiple videos can be
    specified (requires -o) — all frames go into one output directory
    with sequential numbering across videos.

Examples:
    videotool -f 10 video.mp4                     # single video
    videotool -t 100 video.mp4                    # evenly-spaced frames
    videotool -f 30 -o ./frames video.mp4          # custom output directory
    videotool -f 10 -n pic video.mp4               # output: pic_000001.jpg
    videotool -f 10                                # interactive mode
    videotool -f 10 -o ./all a.mp4 b.mp4 c.mp4     # multi-video → one folder
"""

import argparse
import os
import sys
from pathlib import Path

import cv2


def _imwrite_safe(path, frame):
    """Save an image to disk, handling non-ASCII paths on Windows.

    cv2.imwrite() does not support Unicode/non-ASCII paths on Windows.
    This function uses cv2.imencode() + Python's open() as a workaround.
    """
    ext = os.path.splitext(path)[1]  # e.g., '.jpg', '.png'
    success, buf = cv2.imencode(ext, frame)
    if not success:
        return False
    try:
        with open(path, "wb") as f:
            f.write(buf.tobytes())
        return True
    except OSError:
        return False


def get_video_info(cap):
    """Read total frame count and fps from an opened VideoCapture."""
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return total_frames, fps


def count_frames_by_reading(video_path):
    """Count total frames by reading through the entire video.

    Used as a fallback when OpenCV cannot determine the frame count
    from video metadata (returns -1 or 0).
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        return 0

    count = 0
    while True:
        ret, _ = cap.read()
        if not ret:
            break
        count += 1
    cap.release()
    return count


def compute_frame_indices_by_interval(total_frames, interval):
    """Return list of frame indices: one every `interval` frames."""
    if interval <= 0:
        raise ValueError(f"Interval must be > 0, got {interval}")
    return list(range(0, total_frames, interval))


def compute_frame_indices_by_count(total_frames, count):
    """Return list of `count` evenly-spaced frame indices."""
    if count <= 0:
        raise ValueError(f"Count must be > 0, got {count}")
    if count > total_frames:
        print(
            f"Warning: requested {count} frames but video only has "
            f"{total_frames} frames. Outputting all {total_frames} frames.",
            flush=True,
        )
        return list(range(total_frames))

    indices = []
    for i in range(count):
        idx = int(i * total_frames / count)
        indices.append(idx)
    return indices


def extract_frames(video_path, frame_indices, output_dir, img_format="jpg", img_name="frame", start_index=0):
    """Extract specified frame indices from video and save as images.

    Returns the number of frames successfully saved.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        print(
            f"Error: cannot open video file: {video_path}\n"
            f"  The path may contain characters that OpenCV cannot handle.\n"
            f"  Try moving the video to a path with only ASCII characters.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    total_frames, fps = get_video_info(cap)
    duration = total_frames / fps if fps > 0 else 0

    print(f"Video: {video_path}", flush=True)
    print(f"  Total frames: {total_frames}", flush=True)
    print(f"  FPS: {fps:.2f}", flush=True)
    print(f"  Duration: {duration:.2f}s", flush=True)
    print(f"  Extracting: {len(frame_indices)} frames", flush=True)
    print(f"  Output: {output_dir}", flush=True)
    print(flush=True)

    os.makedirs(output_dir, exist_ok=True)

    # Use a generous digit count to handle multi-video accumulation
    total_to_extract = len(frame_indices)
    digit_count = max(6, len(str(start_index + total_to_extract)) + 1)
    name_template = f"{img_name}_{{:0{digit_count}d}}.{img_format}"

    saved_count = 0
    for i, frame_idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            print(f"  Warning: failed to read frame {frame_idx}, skipping.", flush=True)
            continue

        out_path = os.path.join(output_dir, name_template.format(start_index + i + 1))
        success = _imwrite_safe(out_path, frame)
        if success:
            saved_count += 1
            print(f"  [{i + 1}/{total_to_extract}] {out_path}", flush=True)
        else:
            print(f"  Error: failed to write {out_path}", file=sys.stderr, flush=True)

    cap.release()
    print(f"  {saved_count}/{total_to_extract} frames saved from this video.", flush=True)
    return saved_count


def interactive_mode():
    """Prompt the user for video path(s) and output directory interactively.

    Returns (video_paths, output_dir, img_name, multi_video).
    """
    print("=" * 50, flush=True)
    print("  videotool - Interactive Mode", flush=True)
    print("=" * 50, flush=True)
    print(flush=True)

    # Collect video paths (support multiple)
    video_paths = []
    while True:
        if not video_paths:
            prompt = "请输入视频源路径 (可输入多个，空行结束): "
        else:
            prompt = f"  继续添加第 {len(video_paths) + 1} 个视频 (直接回车结束): "

        raw = input(prompt).strip().strip('"').strip("'")
        if not raw:
            if not video_paths:
                print("  路径不能为空，请重新输入。", flush=True)
                continue
            else:
                break

        vp = Path(raw)
        if not vp.exists():
            print(f"  文件不存在: {raw}", flush=True)
            continue
        if not vp.is_file():
            print(f"  不是有效的文件: {raw}", flush=True)
            continue
        video_paths.append(vp)
        print(f"    [OK] 已添加: {vp}", flush=True)

    print(flush=True)
    multi_video = len(video_paths) > 1

    if multi_video:
        print(f"  共 {len(video_paths)} 个视频文件。", flush=True)
        print(flush=True)

    # Prompt for output directory
    if multi_video:
        # Multi-video: output is required, no default
        while True:
            raw = input(f"请输入输出路径 (多视频模式下必填):\n  → ").strip().strip('"').strip("'")
            if not raw:
                print("  多视频模式下输出路径不能为空，请重新输入。", flush=True)
                continue
            output_dir = raw
            break
    else:
        default_output = str(video_paths[0].parent / f"{video_paths[0].stem}_frames")
        raw = input(f"请输入输出路径 (直接回车则默认):\n  → {default_output}\n  ").strip().strip('"').strip("'")
        if raw:
            output_dir = raw
        else:
            output_dir = default_output
            print(f"  使用默认路径: {output_dir}", flush=True)

    print(flush=True)

    # Prompt for output filename prefix
    default_name = "frame"
    raw = input(f"请输入输出文件名前缀 (直接回车则默认 \"{default_name}\"):\n  → ").strip().strip('"').strip("'")

    if raw:
        img_name = raw
    else:
        img_name = default_name
        print(f"  使用默认前缀: {img_name}", flush=True)

    print(flush=True)

    return video_paths, output_dir, img_name, multi_video


def process_video(video_path, args, output_dir, img_name, start_index=0):
    """Process a single video: open, compute frame indices, extract.

    Returns (saved_count, expected_count).
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        print(
            f"Error: cannot open video file: {video_path}\n"
            f"  The path may contain characters that OpenCV cannot handle.\n"
            f"  Try moving the video to a path with only ASCII characters.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    total_frames, _ = get_video_info(cap)
    cap.release()

    # Handle the case where OpenCV cannot determine frame count
    if total_frames <= 0:
        print(
            f"Warning: Cannot determine frame count from video metadata "
            f"(got {total_frames}). Counting frames by scanning the video...",
            flush=True,
        )
        total_frames = count_frames_by_reading(video_path)
        if total_frames <= 0:
            print(
                f"Error: Unable to read any frames from the video. "
                f"The video codec may not be supported by OpenCV.",
                file=sys.stderr,
                flush=True,
            )
            sys.exit(1)
        print(f"  Found {total_frames} frames by scanning.", flush=True)
        print(flush=True)

    # Compute frame indices
    if args.frame_interval is not None:
        frame_indices = compute_frame_indices_by_interval(
            total_frames, args.frame_interval
        )
    else:
        frame_indices = compute_frame_indices_by_count(
            total_frames, args.total_frames
        )

    if not frame_indices:
        print(f"Error: no frames to extract from {video_path}.", file=sys.stderr, flush=True)
        return 0, 0

    saved = extract_frames(video_path, frame_indices, output_dir, args.format, img_name, start_index)
    return saved, len(frame_indices)


def main():
    parser = argparse.ArgumentParser(
        prog="videotool",
        description="Convert video files to image sequences.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--frame-interval",
        type=int,
        metavar="N",
        help="Extract one frame every N frames.",
    )
    group.add_argument(
        "-t", "--total-frames",
        type=int,
        metavar="N",
        help="Extract exactly N evenly-spaced frames from the video.",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        metavar="DIR",
        help="Output directory (default: <video_name>_frames/).",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="jpg",
        choices=["jpg", "png"],
        help="Output image format (default: jpg).",
    )
    parser.add_argument(
        "-n", "--name",
        type=str,
        default="frame",
        metavar="NAME",
        help="Output image filename prefix (default: frame). e.g. --name pic → pic_000001.jpg",
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="*",
        default=None,
        help="Path to the input video file(s). Omit for interactive mode. "
             "Multiple videos can be specified (requires -o).",
    )

    args = parser.parse_args()

    # --- Determine mode: interactive, single-video, or multi-video ---
    if not args.input:
        # Interactive mode: prompt for video path(s)
        video_paths, output_dir, img_name, multi_video = interactive_mode()
    elif len(args.input) == 1:
        # Single video mode
        video_path = Path(args.input[0])
        if not video_path.exists():
            print(f"Error: file not found: {args.input[0]}", file=sys.stderr, flush=True)
            sys.exit(1)
        if not video_path.is_file():
            print(f"Error: not a file: {args.input[0]}", file=sys.stderr, flush=True)
            sys.exit(1)
        video_paths = [video_path]

        if args.output:
            output_dir = args.output
        else:
            output_dir = str(video_path.parent / f"{video_path.stem}_frames")

        img_name = args.name
        multi_video = False
    else:
        # Multi-video mode: require -o
        if args.output is None:
            print(
                "Error: -o/--output is required when processing multiple videos.",
                file=sys.stderr,
                flush=True,
            )
            sys.exit(1)

        video_paths = []
        for p in args.input:
            vp = Path(p)
            if not vp.exists():
                print(f"Error: file not found: {p}", file=sys.stderr, flush=True)
                sys.exit(1)
            if not vp.is_file():
                print(f"Error: not a file: {p}", file=sys.stderr, flush=True)
                sys.exit(1)
            video_paths.append(vp)

        output_dir = args.output
        img_name = args.name
        multi_video = True

    # --- Process all videos ---
    total_saved = 0
    global_index = 0

    print("=" * 50, flush=True)
    if multi_video:
        print(f"  Processing {len(video_paths)} videos → {output_dir}", flush=True)
    print("=" * 50, flush=True)
    print(flush=True)

    for idx, vp in enumerate(video_paths):
        if multi_video:
            print(f"--- Video {idx + 1}/{len(video_paths)} ---", flush=True)

        saved, expected = process_video(vp, args, output_dir, img_name, global_index)
        total_saved += saved
        global_index += expected  # Advance by expected count to avoid filename collisions

    # --- Summary ---
    if multi_video:
        print("=" * 50, flush=True)
        print(f"  All done! {total_saved} frames total → {output_dir}", flush=True)
        print("=" * 50, flush=True)
    else:
        print(f"Done! {total_saved} frames saved to {output_dir}", flush=True)


if __name__ == "__main__":
    main()
