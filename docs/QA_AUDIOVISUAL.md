# Control audiovisual — Factor de Gigantes

`tools/av_quality.py` lee el MP4 exportado, inspecciona sus pistas con ffprobe
y decodifica por completo audio y video con FFmpeg. No modifica el archivo,
no genera voz y no consume servicios de IA.

```sh
python -m tools.av_quality dist/video.mp4 --profile documentary --out dist/QA_AUDIOVISUAL.json
```

Perfiles: `documentary` exige 8–14 minutos y orientación horizontal; `short`
admite hasta 180 segundos en vertical; `preview` admite pruebas horizontales
de hasta 15 minutos. Pasar `preview` no acredita un documental completo.
`--expected-seconds` contrasta una duración conocida con tolerancia de 0,25 s.

Se exige una pista H.264/yuv420p y una pista AAC mono/estéreo de 44,1/48 kHz,
12–60 fps, al menos 1280×720 horizontal o 720×1280 vertical. Se comprueban
los comienzos de las pistas (diferencia máxima 0,15 s), sus finales (0,30 s)
y la decodificación completa; un archivo truncado no pasa sólo porque conserve
la cabecera y la duración declarada.

El escaneo señala congelamientos de al menos 2 s, silencios de al menos 2 s
bajo −45 dB y tramos negros de al menos 0,8 s. Son umbrales de detección de
defectos para este pipeline; un plano deliberadamente fijo o una pausa creativa
pueden requerir revisión. Los intervalos figuran en el informe. Un pico cercano
a 0 dBFS genera aviso para audición, no una afirmación de clipping ni una
normalización automática. Estos controles no miden sincronía labial ni
correspondencia semántica entre narración e imágenes.

Una salida correcta lleva `technical_gate_passed=true` y mantiene
`voice_identity_verified`, `rights_verified`, `factual_approval` y
`publication_authorized` en falso. La identidad vocal, naturalidad, exactitud
editorial y derechos siguen sujetos a revisión humana.

El workflow de render ejecuta esta puerta antes de subir la vista previa y
reportar el trabajo como `ready`; conserva el diagnóstico aunque falle.
El montaje de escena 01 también la ejecuta y conserva el reporte dentro de
su artefacto. La integración de esos workflows se prueba en su próxima
ejecución autorizada; los tests no sustituyen una ejecución de producción.

CI tiene un job independiente que codifica medios reales: movimiento con
audio, congelamiento/silencio, negro con audio, ausencia de audio y archivo
truncado. No ejecuta el radar ni crea nuevas tomas Qwen.

```sh
FDG_MEDIA_QA_INTEGRATION=1 python -m unittest tests.test_av_quality -v
```

Referencias de implementación: [ffprobe](https://ffmpeg.org/ffprobe.html) y
[filtros FFmpeg](https://ffmpeg.org/ffmpeg-filters.html) (`freezedetect`,
`blackdetect`, `silencedetect`, `volumedetect`). El hash SHA256 enlaza el
informe con el archivo examinado; cambiar el medio requiere repetir el QA.
