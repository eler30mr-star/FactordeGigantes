"""Cadencia pausada para documentales; solo FFmpeg y biblioteca estándar."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
import wave


def pause_centers(stderr: str, speed: float = 1.0, max_breaks: int = 3):
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", stderr)]
    return [((a + b) / 2) / speed for a, b in zip(starts, ends)
            if a > .4 and b - a >= .28][:max_breaks]


def add_pauses(pcm: bytes, rate: int, frame_bytes: int,
               times: list[float], pause_seconds: float):
    zeros = bytes(round(pause_seconds * rate) * frame_bytes)
    positions = sorted(min(len(pcm), max(0, round(t * rate) * frame_bytes))
                       for t in times)
    chunks, previous = [], 0
    for position in positions:
        chunks.extend([pcm[previous:position], zeros])
        previous = position
    chunks.append(pcm[previous:])
    return b"".join(chunks)


def run(source: Path, target: Path, speed=.94, pause_seconds=.16, max_breaks=3):
    if not source.is_file():
        raise FileNotFoundError(source)
    if not .85 <= speed <= 1.0 or not 0 <= pause_seconds <= .35 or not 0 <= max_breaks <= 8:
        raise ValueError("Cadencia fuera de límites seguros")
    scan = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(source),
                           "-af", "silencedetect=noise=-35dB:d=0.22", "-f", "null", "-"],
                          capture_output=True, text=True, check=True, timeout=40)
    times = pause_centers(scan.stderr, speed, max_breaks)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        slower = Path(folder) / "slower.wav"
        paused = Path(folder) / "paused.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source),
                        "-af", f"atempo={speed}", "-ac", "1", "-ar", "48000",
                        "-c:a", "pcm_s16le", str(slower)], check=True, timeout=80)
        with wave.open(str(slower), "rb") as reader:
            rate, width, channels = reader.getframerate(), reader.getsampwidth(), reader.getnchannels()
            pcm = reader.readframes(reader.getnframes())
        if (rate, width, channels) != (48000, 2, 1):
            raise RuntimeError("PCM inesperado")
        final = add_pauses(pcm, rate, width * channels, times, pause_seconds)
        with wave.open(str(paused), "wb") as writer:
            writer.setnchannels(channels)
            writer.setsampwidth(width)
            writer.setframerate(rate)
            writer.writeframes(final)
        codec = ["-c:a", "pcm_s16le"] if target.suffix.lower()==".wav" else ["-c:a", "libmp3lame", "-b:a", "160k"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(paused),
                        *codec, str(target)],
                       check=True, timeout=90)
    report = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(target)],
        text=True, timeout=20))
    return {"duration": float(report["format"]["duration"]), "speed": speed,
            "pauses": len(times), "pause_seconds": pause_seconds, "pitch_shift": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--speed", type=float, default=.94)
    parser.add_argument("--pause", type=float, default=.16)
    parser.add_argument("--max-breaks", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.target, args.speed, args.pause, args.max_breaks), indent=2))

