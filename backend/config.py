import os

# TOS (火山引擎对象存储)
TOS_ACCESS_KEY = os.getenv("TOS_ACCESS_KEY", "")
TOS_SECRET_KEY = os.getenv("TOS_SECRET_KEY", "")

# TOS 原生 endpoint（官方 SDK 使用原生域名，非 S3 协议域名）
TOS_ENDPOINT = os.getenv("TOS_ENDPOINT", "https://tos-cn-shanghai.volces.com")
TOS_REGION = os.getenv("TOS_REGION", "cn-shanghai")
TOS_BUCKET = os.getenv("TOS_BUCKET", "my-photo")

# SQLite
DB_PATH = os.getenv("DB_PATH", "photowall.db")

# Server
LISTEN_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "8000"))
