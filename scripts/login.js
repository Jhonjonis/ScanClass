// ------------------------------
// Validação e envio do formulário de login
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const formLogin = document.getElementById("formLogin");
  const inputText = document.getElementById("inputText");
  const password = document.getElementById("password");
  const errorInputText = document.getElementById("fidelErrorInputText");
  const errorPassword = document.getElementById("fidelErrorPassword");
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const btnDarEntrada = document.getElementById("btnDarEntrada");

  // ------------------------------
  // Evento de envio do formulário
  // ------------------------------
  formLogin.addEventListener("submit", (e) => {
    e.preventDefault();

    let erros = {};
    const valorUsuario = inputText.value.trim();
    const valorSenha = password.value.trim();

    const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const regexName = /^[a-zA-Z\s]+$/;

    // Validações
    if (!valorUsuario) {
      erros.usuario = "Campo obrigatório";
    } else if (!regexEmail.test(valorUsuario) && !regexName.test(valorUsuario)) {
      erros.usuario = "Digite um nome ou e-mail válido";
    }

    if (!valorSenha) {
      erros.senha = "Campo obrigatório";
    }

    // Exibe erros
    errorInputText.textContent = erros.usuario || "";
    errorPassword.textContent = erros.senha || "";

    // Se não houver erros, envia o form
    if (Object.keys(erros).length === 0) {
      formLogin.submit(); // envia POST para /login no Flask
    }
  });

  // ------------------------------
  // Captura de rosto para dar entrada
  // ------------------------------
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => { alert("Erro ao acessar a câmera: " + err); });

  btnDarEntrada.addEventListener("click", () => {
    const usuario = inputText.value.trim();
    if (!usuario) {
      alert("Digite seu usuário antes de dar entrada.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const dataURL = canvas.toDataURL("image/jpeg");

    fetch("/verificar_rosto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ imagem: dataURL, usuario: usuario })
    })
      .then(res => res.json())
      .then(data => alert(data.mensagem))
      .catch(err => alert("Erro ao verificar rosto: " + err));
  });
});
