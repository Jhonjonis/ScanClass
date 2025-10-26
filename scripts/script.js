const dataToSend = {
  usuario: document.getElementById('nameUser').value,
  nome: document.getElementById('name').value,
  email: document.getElementById('email').value,
  senha: document.getElementById('password').value,
  imagem: dataURL
};

fetch('/salvar_rosto', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(dataToSend)
})
