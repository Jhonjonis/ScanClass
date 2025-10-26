document.addEventListener("DOMContentLoaded", () => {
  const formLogin = document.getElementById("formLogin");
  const inputText = document.getElementById("inputText");
  const password = document.getElementById("password");
  const errorInputText = document.getElementById("fidelErrorInputText");
  const errorPassword = document.getElementById("fidelErrorPassword");

  formLogin.addEventListener("submit", (e) => {
    e.preventDefault(); // previne envio padrão temporariamente

    let erros = {};
    const valorUsuario = inputText.value.trim();
    const valorSenha = password.value.trim();

    if (!valorUsuario) erros.usuario = "Campo obrigatório";
    if (!valorSenha) erros.senha = "Campo obrigatório";

    errorInputText.textContent = erros.usuario || "";
    errorPassword.textContent = erros.senha || "";

    // se não houver erros, envia o form tradicional
    if (Object.keys(erros).length === 0) {
      formLogin.submit(); // **envia POST para Flask**
    }
  });
});
