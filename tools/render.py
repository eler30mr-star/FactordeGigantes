#!/usr/bin/env python3
"""Produce a technically reproducible preview: original slides + local Spanish speech.
No upload to YouTube. No remote media downloaded. This is not monetization-quality output.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request


def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError("Manifest debe ser objeto")
    title = data.get("title")
    angle = data.get("angle")
    if not isinstance(title, str) or not 8 <= len(title.strip()) <= 150:
        raise ValueError("Título inválido")
    if not isinstance(angle, str) or not 15 <= len(angle.strip()) <= 700:
        raise ValueError("Enfoque inválido")
    if data.get("format") not in ("short", "long"):
        raise ValueError("Formato inválido")
    sources = data.get("sources")
    if not isinstance(sources, list) or not 2 <= len(sources) <= 20 or not all(
        isinstance(s, str) and s.startswith("https://") for s in sources
    ):
        raise ValueError("Se requieren fuentes https verificadas por el editor")
    segments = data.get("segments")
    if not isinstance(segments, list) or not 2 <= len(segments) <= 18:
        raise ValueError("Se requieren 2-18 segmentos")
    for s in segments:
        if not isinstance(s, dict) or not isinstance(s.get("headline"), str) or not isinstance(s.get("voiceover"), str):
            raise ValueError("Segmento incompleto")
        if not 1 <= len(s["headline"].strip()) <= 110 or not 15 <= len(s["voiceover"].strip()) <= 900:
            raise ValueError("Longitud de segmento inválida")
    return data


def command(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def duration(wav):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(wav)],
        check=True, text=True, capture_output=True
    )
    return float(result.stdout.strip())


def wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def slide(path, title, headline, excerpt, index, count, fmt):
    from PIL import Image, ImageDraw, ImageFont

    width, height = (720, 1280) if fmt == "short" else (1280, 720)
    image = Image.new("RGB", (width, height), "#111318")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        shade = int(17 + 16 * y / height)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 1, shade + 5))
    # Original abstract brand graphics, not misleading footage of real events.
    cx, cy = int(width * .80), int(height * .32)
    for n in range(7):
        radius = int((min(width, height) * .23) + n * 16)
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius),
                     outline=(82 + n * 5, 61 + n * 4, 31 + n * 3), width=2)
    baseline = int(height * .80)
    for i in range(9):
        x = int(width * (.65 + i * .035))
        top = baseline - (i * 31 + (i % 3) * 45)
        draw.rectangle((x, top, x + 13, baseline), fill=(135 + i * 8, 101 + i * 8, 48 + i * 4))
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not Path(font_path).exists():
        raise FileNotFoundError("Se requiere instalar fonts-dejavu-core")
    small = ImageFont.truetype(bold_path, 20 if fmt == "short" else 19)
    head = ImageFont.truetype(bold_path, 43 if fmt == "short" else 60)
    body = ImageFont.truetype(font_path, 24 if fmt == "short" else 27)
    brand = ImageFont.truetype(bold_path, 25 if fmt == "short" else 26)
    margin = 53 if fmt == "short" else 78
    draw.text((margin, margin), "FACTOR DE GIGANTES", fill="#efc87e", font=brand)
    draw.text((margin, margin + 50), "DOCUMENTAL · PRUEBA", fill="#d7d9db", font=small)
    if fmt == "short":
        top = int(height * .25)
    else:
        top = int(height * .29)
    headline_lines = wrap(draw, headline.upper(), head, width - 2 * margin)
    if len(headline_lines) > 4:
        raise ValueError("Título demasiado largo para tarjeta")
    for line in headline_lines:
        draw.text((margin, top), line, fill="#f5e9d7", font=head)
        top += (65 if fmt == "short" else 80)
    top += 24
    excerpt = re.sub(r"\s+", " ", excerpt)[:210]
    max_lines = 5 if fmt == "short" else 3
    for line in wrap(draw, excerpt, body, width - 2 * margin)[:max_lines]:
        draw.text((margin, top), line, fill="#d6d3ce", font=body)
        top += 40
    draw.line((margin, height - 100, width-margin, height-100), fill="#bd9142", width=3)
    draw.text((margin, height - 76), f"ESCENA {index:02d} / {count:02d}  •  PRODUCCIÓN DE PRUEBA", fill="#d6ba85", font=small)
    image.save(path)


def render(manifest, output):
    validate_manifest(manifest)
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="factor-video-") as tmp:
        root = Path(tmp)
        clips = []
        total = 0
        for i, segment in enumerate(manifest["segments"], 1):
            audio = root / f"voice-{i:02}.wav"
            scene = root / f"slide-{i:02}.png"
            clip = root / f"clip-{i:02}.mp4"
            # Pass args as an array; script text cannot inject commands.
            command("espeak-ng", "-v", "es", "-s", "155", "-w", str(audio), segment["voiceover"])
            length = duration(audio) + .2
            total += length
            slide(scene, manifest["title"], segment["headline"], segment["voiceover"], i,
                  len(manifest["segments"]), manifest["format"])
            fps = "24"
            command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-loop", "1", "-framerate", fps, "-i", str(scene),
                    "-i", str(audio), "-t", f"{length:.2f}",
                    "-c:v", "libx264", "-preset", "ultrafast", "-r", fps,
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", "-shortest", str(clip))
            clips.append(clip)
            print(f"Escena {i}/{len(manifest['segments'])}: {length:.1f} s", flush=True)
        if manifest["format"] == "short" and total > 180:
            raise ValueError("Short supera 180 segundos; dividir o reducir guion")
        listing = root / "concat.txt"
        listing.write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
        command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(listing),
                "-c", "copy", "-movflags", "+faststart", str(output))
        print(f"Video producido: {output} ({total:.1f}s, {output.stat().st_size} bytes)")


def remote_manifest(job_id):
    base = os.environ.get("API_BASE_URL", "").rstrip("/")
    token = os.environ.get("RENDERER_TOKEN", "")
    if not base.startswith("https://") or len(token) < 24:
        raise RuntimeError("Configura secretos API_BASE_URL (HTTPS) y RENDERER_TOKEN")
    if not re.fullmatch(r"[0-9a-f-]{36}", job_id):
        raise ValueError("job_id inválido")
    url = base + "/api/renderer/jobs/" + job_id
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["manifest"]


def main():
    parser = argparse.ArgumentParser(description="Motor preliminar Factor de Gigantes")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--manifest", help="Archivo JSON local")
    src.add_argument("--remote", action="store_true", help="Leer trabajo aprobado del Worker")
    parser.add_argument("--job-id", default="", help="UUID aprobado, solo en modo --remote")
    parser.add_argument("--output", default="dist/video.mp4")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.remote and not args.job_id:
        parser.error("--remote requiere --job-id")
    content = remote_manifest(args.job_id) if args.remote else json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    validate_manifest(content)
    if args.validate_only:
        print("Manifest validado")
    else:
        render(content, args.output)


if __name__ == "__main__":
    main()
