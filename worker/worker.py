# producer/main.py
import os
import redis
import json
from fastapi import FastAPI, UploadFile, Form
from base64 import b64encode

app = FastAPI()

# --- Configurações ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # nome do serviço Redis no cluster
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "meme_queue"
INPUT_DIR = "/data/input"

os.makedirs(INPUT_DIR, exist_ok=True)

# --- Conecta no Redis ---
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@app.post("/upload")
async def upload(file: UploadFile, text: str = Form(...)):
    # Salva arquivo localmente
    file_path = os.path.join(INPUT_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Converte imagem para base64
    with open(file_path, "rb") as f:
        image_b64 = b64encode(f.read()).decode("utf-8")

    # Cria payload JSON
    payload = json.dumps({
        "image": image_b64,
        "text": text
    })

    # Enfileira no Redis
    r.rpush(QUEUE_NAME, payload)

    print(f"Meme recebido: {file.filename}, enviado para fila '{QUEUE_NAME}'")
    return {"message": f"Meme '{file.filename}' enviado para processamento!"}
