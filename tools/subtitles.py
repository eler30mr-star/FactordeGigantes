"""Subtítulos de escena aproximados basados en la duración del audio generado."""
import re

def split_lines(text, max_chars=42, max_lines=2):
    words = re.sub(r"\s+", " ", text).strip().split()
    lines, current = [], ""
    for word in words:
        while len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        proposed = (current + " " + word).strip()
        if len(proposed) <= max_chars:
            current = proposed
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return ["\n".join(lines[i:i + max_lines]) for i in range(0, len(lines), max_lines)]

def timestamp(seconds):
    ms = max(0, int(round(seconds * 1000)))
    h, rem = divmod(ms, 3600000)
    minute, rem = divmod(rem, 60000)
    sec, milli = divmod(rem, 1000)
    return f"{h:02}:{minute:02}:{sec:02},{milli:03}"

def make_srt(segments, durations):
    if len(segments) != len(durations):
        raise ValueError("El número de escenas y duraciones no coincide")
    count, offset, entries = 0, 0.0, []
    for segment, sec in zip(segments, durations):
        if sec <= 0:
            raise ValueError("Duración de escena inválida")
        parts = split_lines(segment["voiceover"])
        weights = [len(re.sub(r"\s+", "", p)) for p in parts]
        total = sum(weights) or 1
        elapsed = 0
        usable = max(.1, sec - .15)
        for part, weight in zip(parts, weights):
            begin = offset + usable * elapsed / total
            elapsed += weight
            end = offset + usable * elapsed / total
            count += 1
            entries.append(f"{count}\n{timestamp(begin)} --> {timestamp(end)}\n{part}\n")
        offset += sec
    return "\n".join(entries) + ("\n" if entries else "")
