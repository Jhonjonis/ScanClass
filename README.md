# 🧑‍🎓 Scan Class — Sistema de Controle de Presença com Reconhecimento Facial

## 🎯 Objetivo do Projeto
O **Scan Class** é um sistema web desenvolvido para **automatizar o controle de presença**
em ambientes educacionais, utilizando **reconhecimento facial** como principal forma
de autenticação.

O foco do projeto está no **Front-End**, proporcionando uma interface intuitiva,
responsiva e eficiente, integrada a uma **API REST** responsável pelo processamento
de dados, autenticação e comunicação com serviços externos.

---

## 🧩 Visão Geral da Arquitetura
O **front-end** atua como consumidor de uma **API REST desenvolvida em Flask**,
mantendo a separação entre interface e regras de negócio.

A **API** é responsável por:
- 🔐 Autenticação e gerenciamento de usuários
- 🧠 Processamento de reconhecimento facial
- 💾 Persistência de dados em banco PostgreSQL (Neon)
- 📡 Integração com serviços externos (Face++)
- 📊 Registro e consulta de presenças

---

## ⚙️ Funcionalidades
- 👤 Cadastro de usuários com autenticação segura
- 📷 Captura e armazenamento de imagem facial
- 🧠 Reconhecimento facial para registro de presença
- 🕒 Registro automático de entrada e saída
- 🖥️ Dashboard do usuário com estatísticas de presença
- 📊 Histórico de registros
- 🔐 Controle de sessão e rotas protegidas
- 🧑 Perfil do usuário com dados acadêmicos

---

## 🎨 Front-End (Foco do Projeto)
- 📱 Interface web responsiva
- 🎯 Fluxos claros de cadastro, login e presença
- 📷 Integração com câmera do dispositivo
- 🔗 Consumo de API REST via requisições HTTP
- 🧠 Feedback visual em tempo real (sucesso, erro, validações)
- 🔐 Autenticação baseada em sessão

> O front-end foi desenvolvido com foco em **usabilidade**, **acessibilidade**
> e **experiência do usuário**, garantindo fluidez no processo de reconhecimento facial.

---

## 🔌 Integrações
- 🤖 Face++ API (reconhecimento facial)
- 🗃️ PostgreSQL (Neon Database)
- 🌐 API REST Flask
- 🔐 Hash seguro de senhas (Werkzeug)

---

## 🛠️ Tecnologias Utilizadas

### 🎨 Front-End
- HTML5
- CSS3
- JavaScript

### ⚙️ Back-End 
- Python
- Flask
- PostgreSQL (Neon)
- Face++ API
- REST APIs

---

## 🔒 Segurança
- Hash de senhas com `werkzeug.security`
- Validação de imagens e dados de entrada
- Sessões protegidas
- Rotas restritas por autenticação

---

## 🚀 Considerações Finais
Este projeto demonstra a aplicação prática de **desenvolvimento Front-End integrado
a APIs modernas**, explorando reconhecimento facial, segurança e persistência de dados,
com foco em escalabilidade, organização e experiência do usuário.
