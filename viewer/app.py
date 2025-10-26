from flask import Flask, send_file, render_template_string
import os, glob

app = Flask(__name__)
MEME_DIR = "/data/output"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Último Meme Gerado</title>
<style>
  body { font-family: Arial, sans-serif; text-align:center; padding:50px; background:#f0f2f5; }
  h1 { color:#333; }
  img { max-width:500px; border-radius:10px; margin-top:20px; }
  a { display:inline-block; margin-top:15px; text-decoration:none; padding:10px 20px; background:#4CAF50; color:white; border-radius:5px; }
  a:hover { background:#45a049; }
  p { font-size:16px; color:#555; }
</style>
</head>
<body>
<h1>Último Meme Gerado 😎</h1>
{% if image %}
  <img src="/latest"><br>
  <a href="/download">Baixar Meme</a>
  <p>Meme gerado com sucesso! Clique em "Baixar Meme" ou atualize para ver novos memes.</p>
{% else %}
  <p>Nenhuma imagem gerada ainda. Envie uma no frontend.</p>
{% endif %}
</body>
</html>
"""

def get_latest_meme():
    files = glob.glob(os.path.join(MEME_DIR, "*"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

@app.route("/")
def index():
    latest = get_latest_meme()
    return render_template_string(HTML_TEMPLATE, image=latest)

@app.route("/latest")
def latest():
    latest_file = get_latest_meme()
    if latest_file:
        return send_file(latest_file, mimetype="image/png")
    return "Nenhuma imagem disponível", 404

@app.route("/download")
def download():
    latest_file = get_latest_meme()
    if latest_file:
        return send_file(latest_file, as_attachment=True)
    return "Nenhuma imagem disponível", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
