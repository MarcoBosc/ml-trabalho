from fastapi import FastAPI, UploadFile, Form
import redis
import json
import base64

REDIS_HOST = "redis"
REDIS_PORT = 6379
QUEUE_NAME = "meme_queue"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile, text: str = Form(...)):
    # Lê a imagem e converte para base64
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Cria o payload
    payload = json.dumps({
        "image": image_b64,
        "text": text
    })

    # Envia para a fila Redis
    r.rpush(QUEUE_NAME, payload)
    
    return {"status": "Imagem enviada com sucesso! Verifique o viewer para baixar."}
