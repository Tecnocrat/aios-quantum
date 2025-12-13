#!/usr/bin/env python
"""
GIF FRAME EXTRACTOR FOR AI VISION
=================================

Extracts frames from GIF/WebM files into individual images that can be
"read" by AI agents sequentially to reconstruct motion.

This enables:
1. AI agents to "see" animations frame-by-frame
2. Visual debugging of quantum visualizations
3. Portfolio documentation with motion capture
4. Future VSCode extension for visual media processing

Usage:
    python tools/gif_extractor.py input.gif --fps 10 --output frames/
    python tools/gif_extractor.py input.webm --format png --max-frames 100
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class ExtractionResult:
    """Metadata about extracted frames."""
    source_file: str
    output_dir: str
    total_frames: int
    fps: float
    duration_seconds: float
    frame_width: int
    frame_height: int
    format: str
    extraction_time: str
    frames: List[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_video_info(input_path: str) -> dict:
    """Get video/GIF metadata using ffprobe."""
    try:
        result = subprocess.run([
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Warning: Could not get video info: {e}")
    
    return {}


def extract_frames(
    input_path: str,
    output_dir: str,
    fps: float = 10.0,
    format: str = "png",
    max_frames: Optional[int] = None,
    scale: Optional[str] = None
) -> ExtractionResult:
    """
    Extract frames from GIF/video file.
    
    Args:
        input_path: Path to input GIF/WebM/MP4 file
        output_dir: Directory to save extracted frames
        fps: Frames per second to extract
        format: Output format (png, jpg, webp)
        max_frames: Maximum frames to extract (None = all)
        scale: Optional scale (e.g., "640:480", "iw/2:ih/2")
        
    Returns:
        ExtractionResult with metadata and frame list
    """
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir).resolve()
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get input info
    info = get_video_info(str(input_path))
    
    # Extract dimensions and duration
    width, height, duration = 0, 0, 0.0
    if info and "streams" in info:
        for stream in info["streams"]:
            if stream.get("codec_type") == "video":
                width = stream.get("width", 0)
                height = stream.get("height", 0)
                # Try to get duration
                if "duration" in stream:
                    duration = float(stream["duration"])
                elif "tags" in stream and "DURATION" in stream["tags"]:
                    # Parse duration string
                    dur_str = stream["tags"]["DURATION"]
                    parts = dur_str.split(":")
                    if len(parts) == 3:
                        duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
    
    if info and "format" in info and "duration" in info["format"]:
        duration = float(info["format"]["duration"])
    
    # Build ffmpeg command
    output_pattern = str(output_dir / f"frame_%05d.{format}")
    
    cmd = ["ffmpeg", "-i", str(input_path)]
    
    # Add FPS filter
    filters = [f"fps={fps}"]
    
    # Add scale filter if specified
    if scale:
        filters.append(f"scale={scale}")
    
    cmd.extend(["-vf", ",".join(filters)])
    
    # Add max frames limit
    if max_frames:
        cmd.extend(["-frames:v", str(max_frames)])
    
    # Output settings
    if format == "png":
        cmd.extend(["-c:v", "png"])
    elif format == "jpg":
        cmd.extend(["-q:v", "2"])  # High quality JPEG
    elif format == "webp":
        cmd.extend(["-c:v", "libwebp", "-quality", "90"])
    
    cmd.extend(["-y", output_pattern])
    
    print(f"🎬 Extracting frames from: {input_path.name}")
    print(f"   Output: {output_dir}")
    print(f"   FPS: {fps}")
    print(f"   Format: {format}")
    
    # Run extraction
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        raise RuntimeError(f"FFmpeg failed: {result.returncode}")
    
    # Collect extracted frames
    frames = sorted([
        f.name for f in output_dir.glob(f"frame_*.{format}")
    ])
    
    print(f"   ✓ Extracted {len(frames)} frames")
    
    # Create result
    extraction = ExtractionResult(
        source_file=str(input_path),
        output_dir=str(output_dir),
        total_frames=len(frames),
        fps=fps,
        duration_seconds=duration,
        frame_width=width,
        frame_height=height,
        format=format,
        extraction_time=datetime.now().isoformat(),
        frames=frames
    )
    
    # Save metadata
    metadata_path = output_dir / "extraction_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(extraction.to_dict(), f, indent=2)
    
    print(f"   📝 Metadata saved: {metadata_path.name}")
    
    return extraction


def create_frame_summary(output_dir: str, sample_count: int = 10) -> str:
    """
    Create a text summary of frames for AI consumption.
    
    Returns a formatted string describing the frame sequence
    that can be included in AI prompts.
    """
    output_dir = Path(output_dir)
    metadata_path = output_dir / "extraction_metadata.json"
    
    if not metadata_path.exists():
        return "No extraction metadata found."
    
    with open(metadata_path) as f:
        meta = json.load(f)
    
    # Select sample frames evenly distributed
    total = meta["total_frames"]
    if total <= sample_count:
        sample_indices = list(range(total))
    else:
        step = total / sample_count
        sample_indices = [int(i * step) for i in range(sample_count)]
    
    summary = f"""
# Frame Extraction Summary

**Source:** {Path(meta['source_file']).name}
**Total Frames:** {meta['total_frames']}
**FPS:** {meta['fps']}
**Duration:** {meta['duration_seconds']:.2f}s
**Resolution:** {meta['frame_width']}x{meta['frame_height']}

## Sample Frames (read in sequence to reconstruct motion)

"""
    
    for i, idx in enumerate(sample_indices):
        if idx < len(meta['frames']):
            frame_name = meta['frames'][idx]
            time_sec = idx / meta['fps']
            summary += f"- Frame {idx+1}/{total} (t={time_sec:.2f}s): `{frame_name}`\n"
    
    summary += f"""
## AI Vision Instructions

To reconstruct the animation mentally:
1. Read frames in numerical order
2. Each frame represents {1/meta['fps']*1000:.1f}ms of motion
3. Key transitions happen between frames
4. The full sequence loops continuously

Frame files are located in: `{output_dir}`
"""
    
    return summary


def batch_extract(
    input_dir: str,
    output_base: str,
    extensions: List[str] = [".gif", ".webm", ".mp4"],
    **kwargs
) -> List[ExtractionResult]:
    """Extract frames from all matching files in a directory."""
    input_dir = Path(input_dir)
    output_base = Path(output_base)
    results = []
    
    for ext in extensions:
        for input_file in input_dir.glob(f"*{ext}"):
            output_dir = output_base / input_file.stem
            try:
                result = extract_frames(
                    str(input_file),
                    str(output_dir),
                    **kwargs
                )
                results.append(result)
            except Exception as e:
                print(f"Failed to extract {input_file}: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract frames from GIF/video for AI vision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract at 10 FPS to PNG
    python gif_extractor.py animation.gif -o frames/
    
    # Extract at 30 FPS, max 100 frames
    python gif_extractor.py video.webm --fps 30 --max-frames 100
    
    # Batch extract all GIFs in a folder
    python gif_extractor.py --batch gifs/ -o extracted/
    
    # Create AI-readable summary
    python gif_extractor.py --summarize frames/
        """
    )
    
    parser.add_argument("input", nargs="?", help="Input file or directory")
    parser.add_argument("-o", "--output", default="./frames", help="Output directory")
    parser.add_argument("--fps", type=float, default=10.0, help="Frames per second")
    parser.add_argument("--format", choices=["png", "jpg", "webp"], default="png")
    parser.add_argument("--max-frames", type=int, help="Maximum frames to extract")
    parser.add_argument("--scale", help="Scale filter (e.g., '640:480')")
    parser.add_argument("--batch", action="store_true", help="Process all files in directory")
    parser.add_argument("--summarize", action="store_true", help="Create AI-readable summary")
    
    args = parser.parse_args()
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg not found. Please install ffmpeg:")
        print("   Windows: winget install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Linux: apt install ffmpeg")
        sys.exit(1)
    
    if args.summarize:
        # Just create summary for existing extraction
        if args.input:
            summary = create_frame_summary(args.input)
            print(summary)
            
            # Save summary
            summary_path = Path(args.input) / "AI_VISION_SUMMARY.md"
            with open(summary_path, "w") as f:
                f.write(summary)
            print(f"\n📝 Summary saved to: {summary_path}")
        else:
            print("Please specify the frames directory to summarize")
        return
    
    if not args.input:
        parser.print_help()
        return
    
    if args.batch:
        results = batch_extract(
            args.input,
            args.output,
            fps=args.fps,
            format=args.format,
            max_frames=args.max_frames,
            scale=args.scale
        )
        print(f"\n✅ Extracted {len(results)} files")
    else:
        result = extract_frames(
            args.input,
            args.output,
            fps=args.fps,
            format=args.format,
            max_frames=args.max_frames,
            scale=args.scale
        )
        
        # Auto-generate summary
        summary = create_frame_summary(args.output)
        summary_path = Path(args.output) / "AI_VISION_SUMMARY.md"
        with open(summary_path, "w") as f:
            f.write(summary)
        
        print(f"\n✅ Extraction complete!")
        print(f"   Frames: {result.total_frames}")
        print(f"   Summary: {summary_path}")


if __name__ == "__main__":
    main()
