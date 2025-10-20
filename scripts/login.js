document.getElementById("formLogin").addEventListener("submit", (e) => {
  e.preventDefault();
  const inputText = document.getElementById("inputText").value.trim();
  const password = document.getElementById("password").value.trim();
  const fidelErrorInputText = document.getElementById("fidelErrorInputText")
  const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const regexName = /^[a-zA-Z\s]+$/;
  const erros = {};
  if (!inputText) erros.inputText = "Campo obrigatório";

  if (regexEmail.test(inputText)) {
    console.log("email valido");
  } else if (regexName.test(inputText)) {
    console.log("naome valido");
  } else {
    erros.inputText = "Digite um nome ou email válido";
  }
  fidelErrorInputText.textContent = erros.inputText || "";
  if (erros.length > 0) {
    console.error("Erros:", erros.join(", "));
  }
});
