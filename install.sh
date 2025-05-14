#/bin/sh
uv init
uv pip install yt_dlp anyio music-tag pillow pydub python-telegram-bot requests urllib3
mkdir ./cash
echo "Please tell me your token."
read token
echo '{"token":"$token"}' >> token.json
