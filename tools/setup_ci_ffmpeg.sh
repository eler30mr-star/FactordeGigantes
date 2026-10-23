#!/usr/bin/env bash
# Binarios de prueba fijados a un release y digest; sin apt ni APIs de IA.
set -euo pipefail
task_ffmpeg_root="${RUNNER_TEMP:?RUNNER_TEMP requerido}/fdg-ffmpeg"
task_ffmpeg_sha='97ce978979194b5cf7e06a5e68020dbdaa7a4f3294c5452b6a1bc347100dbb79'
task_ffmpeg_url='https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-09-30-13-08/ffmpeg-n8.1.3-9-g29e619e767-linux64-gpl-8.1.tar.xz'
task_ffmpeg_archive="$task_ffmpeg_root/ffmpeg.tar.xz"
mkdir -p "$task_ffmpeg_root/install"
if [[ ! -f "$task_ffmpeg_archive" ]]; then
  task_ffmpeg_download=$(mktemp "$task_ffmpeg_root/download.XXXXXX")
  trap 'rm -f "$task_ffmpeg_download"' EXIT
  curl --fail --location --connect-timeout 10 --max-time 90 --retry 1 --retry-max-time 120 \
    "$task_ffmpeg_url" --output "$task_ffmpeg_download"
  printf '%s  %s\n' "$task_ffmpeg_sha" "$task_ffmpeg_download" | sha256sum --check --status
  mv "$task_ffmpeg_download" "$task_ffmpeg_archive"
fi
printf '%s  %s\n' "$task_ffmpeg_sha" "$task_ffmpeg_archive" | sha256sum --check --status
tar --extract --xz --file "$task_ffmpeg_archive" --directory "$task_ffmpeg_root/install" \
  --strip-components=1 --no-same-owner
"$task_ffmpeg_root/install/bin/ffmpeg" -version
"$task_ffmpeg_root/install/bin/ffprobe" -version
printf '%s\n' "$task_ffmpeg_root/install/bin" >> "${GITHUB_PATH:?GITHUB_PATH requerido}"
