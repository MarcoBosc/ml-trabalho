const form = document.getElementById("uploadForm");
const statusDiv = document.getElementById("status");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("file");
  const textInput = document.getElementById("text");

  if (!fileInput.files.length) {
    statusDiv.textContent = "⚠️ Por favor, selecione uma imagem!";
    statusDiv.style.color = "red";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("text", textInput.value);

  statusDiv.textContent = "⏳ Enviando meme...";
  statusDiv.style.color = "#0066cc";

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    if (response.ok) {
      statusDiv.textContent = "✅ Meme enviado com sucesso! Verifique o viewer em /viewer";
      statusDiv.style.color = "green";

      // Limpa o form
      fileInput.value = "";
      textInput.value = "";
    } else {
      statusDiv.textContent = "❌ Erro ao enviar meme.";
      statusDiv.style.color = "red";
    }
  } catch (err) {
    statusDiv.textContent = "❌ Erro ao conectar com o servidor.";
    statusDiv.style.color = "red";
  }
});