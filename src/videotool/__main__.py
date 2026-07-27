"""videotool - Convert video files to image sequences.

Usage:
    videotool -f <interval> [-o <output_dir>] [--format <fmt>] <input_video>
    videotool -t <count> [-o <output_dir>] [--format <fmt>] <input_video>

Examples:
    videotool -f 10 video.mp4           # extract every 10th frame
    videotool -t 100 video.mp4          # extract 100 evenly-spaced frames
    videotool -f 30 -o ./frames video.mp4
"""

import argparse
import os
import sys
from pathlib import Path


def get_video_info(cap):
    """Read total frame count and fps from an opened VideoCapture."""
    total_frames = int(cap.get(7))  # cv2.CAP_PROP_FRAME_COUNT
    fps = cap.get(5)                # cv2.CAP_PROP_FPS
    return total_frames, fps


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
            f"{total_frames} frames. Outputting all {total_frames} frames."
        )
        return list(range(total_frames))

    indices = []
    for i in range(count):
        idx = int(i * total_frames / count)
        indices.append(idx)
    return indices


def extract_frames(video_path, frame_indices, output_dir, img_format="jpg"):
    """Extract specified frame indices from video and save as images."""
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: cannot open video file: {video_path}", file=sys.stderr)
        sys.exit(1)

    total_frames, fps = get_video_info(cap)
    duration = total_frames / fps if fps > 0 else 0

    print(f"Video: {video_path}")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Extracting: {len(frame_indices)} frames")
    print(f"  Output: {output_dir}")
    print()

    os.makedirs(output_dir, exist_ok=True)

    digit_count = max(6, len(str(len(frame_indices))) + 1)
    name_template = f"frame_{{:0{digit_count}d}}.{img_format}"

    for i, frame_idx in enumerate(frame_indices):
        cap.set(1, frame_idx)  # cv2.CAP_PROP_POS_FRAMES
        ret, frame = cap.read()
        if not ret:
            print(f"  Warning: failed to read frame {frame_idx}, skipping.")
            continue

        out_path = os.path.join(output_dir, name_template.format(i + 1))
        cv2.imwrite(out_path, frame)
        print(f"  [{i + 1}/{len(frame_indices)}] {out_path}")

    cap.release()
    print(f"\nDone! {len(frame_indices)} frames saved to {output_dir}")


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
        "input",
        type=str,
        help="Path to the input video file.",
    )

    args = parser.parse_args()

    video_path = Path(args.input)
    if not video_path.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    if not video_path.is_file():
        print(f"Error: not a file: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = f"{video_path.stem}_frames"

    # Compute frame indices
    import cv2
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: cannot open video file: {args.input}", file=sys.stderr)
        sys.exit(1)

    total_frames, _ = get_video_info(cap)
    cap.release()

    if args.frame_interval is not None:
        frame_indices = compute_frame_indices_by_interval(
            total_frames, args.frame_interval
        )
    else:
        frame_indices = compute_frame_indices_by_count(
            total_frames, args.total_frames
        )

    if not frame_indices:
        print("Error: no frames to extract.", file=sys.stderr)
        sys.exit(1)

    extract_frames(video_path, frame_indices, output_dir, args.format)


if __name__ == "__main__":
    main()
