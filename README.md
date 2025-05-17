# This projec using uv

```
pip install uv
uv sync 
```


# Sending video with `jpeg`

### A simple and easy method, but the live broadcast effect is not good

```bash
uv run main.py
```


# Using HSL

Start the uvicron server

```bash
uvicron main_h265.py --host 0.0.0.0 --port 8789
```

### Download `ffmpeg` and run

```bash
ffmpeg -f v4l2 -i /dev/video0 \
    -vcodec libx264 -preset ultrafast -tune zerolatency \
    -f hls -hls_time 1 -hls_list_size 3 -hls_flags delete_segments \
    hls/stream.m3u8
```

