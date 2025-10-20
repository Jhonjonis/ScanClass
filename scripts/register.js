document.getElementById("form_register").addEventListener("submit", (e) => {
  e.preventDefault();

  const name = document.getElementById("name").value.trim();
  const nameUser = document.getElementById("nameUser").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const passwordConfirm = document.getElementById("passwordConfirm").value;

  const fidelErrorName = document.getElementById("fidelErrorName");
  const fidelErrorNameUser = document.getElementById("fidelErrorNameUser");
  const fidelErrorEmail = document.getElementById("fidelErrorEmail");
  const fidelErrorPassword = document.getElementById("fidelErrorPassword");
  const fidelErrorPasswordConfirm = document.getElementById(
    "fidelErrorPasswordConfirm"
  );

  const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const regexPassword = /^.{8,}$/;

  const erros = {};


  if (!name) erros.name = "Nome obrigatório";
  if (!nameUser) erros.nameUser = "Nome de usuário obrigatório";
  if (!email) erros.email = "E-mail obrigatório";
  else if (!regexEmail.test(email)) erros.email = "Formato de e-mail inválido";

  if (!password) erros.password = "Senha obrigatória";
  else if (!regexPassword.test(password))
    erros.password = "Senha deve ter no mínimo 8 caracteres";

  if (!passwordConfirm)
    erros.passwordConfirm = "Confirmação de senha obrigatória";
  else if (password && passwordConfirm && password !== passwordConfirm)
    erros.passwordConfirm = "As senhas devem ser iguais";

  fidelErrorName.textContent = erros.name || "";
  fidelErrorNameUser.textContent = erros.nameUser || "";
  fidelErrorEmail.textContent = erros.email || "";
  fidelErrorPassword.textContent = erros.password || "";
  fidelErrorPasswordConfirm.textContent = erros.passwordConfirm || "";

  if (Object.keys(erros).length > 0) {
    console.error("Erros:", erros);
    return;
  }

  console.log("Formulário válido!");
});
