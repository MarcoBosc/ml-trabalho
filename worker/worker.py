import os
import redis
import time
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import json
from urllib.parse import urlparse

# --- Configurações do Redis ---
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
parsed = urlparse(redis_url)

REDIS_HOST = parsed.hostname
REDIS_PORT = parsed.port
QUEUE_NAME = "meme_queue"
OUTPUT_DIR = "/data/output"

# --- Conecta no Redis ---
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# --- Certifica que o diretório existe ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

def add_text_to_image(image_data_b64, text):
    """Recebe uma imagem em base64 e adiciona texto centralizado no topo"""
    image_data = base64.b64decode(image_data_b64)
    image = Image.open(BytesIO(image_data)).convert("RGBA")

    # Camada de texto
    txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    font_size = max(20, image.size[0] // 15)
    font = ImageFont.load_default()
    
    text_width, text_height = draw.textsize(text, font=font)
    x = (image.size[0] - text_width) // 2
    y = 10

    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    combined = Image.alpha_composite(image, txt_layer)
    return combined.convert("RGB")

print("Worker iniciado, aguardando imagens...")

while True:
    try:
        task = r.blpop(QUEUE_NAME, timeout=5)
        if task:
            _, payload = task
            data = json.loads(payload)
            image_b64 = data["image"]
            text = data["text"]

            final_image = add_text_to_image(image_b64, text)

            timestamp = int(time.time())
            filename = os.path.join(OUTPUT_DIR, f"meme_{timestamp}.png")
            final_image.save(filename)
            print(f"Meme salvo: {filename}")
        else:
            time.sleep(1)
    except Exception as e:
        print(f"Erro no worker: {e}")
        time.sleep(1)
