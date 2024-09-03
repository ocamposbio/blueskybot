# Configurações iniciais

## é necessário ter python instalado

configurações básicas:

- https://www.youtube.com/watch?v=-M4pMd2yQOM&pp=ygUVaW5zdGFsYXIgcHl0aG9uIGUgZ2l0

# Baixando e rodando o projeto

- git clone https://github.com/ocamposbio/blueskybot.git

Abra o CMD/Terminal/PowerShell no local baixado

- Instale o pip (baixador de bibliotecas do python)
  - py -m ensurepip --upgrade
- Rodar o seguinte comando: pip install -r requirements.txt
- para executar o bot é só digitar python main.py

# Configurando para o seu uso

O projeto faz a utilização de uma plataforma chamada Nitter para conseguir obter a visualização de uma conta do twitter uma vez que o uso de VPN é proíbido, essa foi a forma encontrada de fazer a checagem na conta original do pépito, por exemplo.

No link abaixo, você consegue verificar quais instâncias do Nitter estão funcionais, utilize a que satisfazer melhor as suas necessidades.

- https://github.com/zedeus/nitter/wiki/Instances

# Explicações do projeto

Para a criação do bot do pépito, eu optei por utilizar headers na página do Nitter, para evitar qualquer tipo de desconexão/problemas com autenticação.

- Como ver os headers com o developer tools: https://www.youtube.com/watch?v=hqQR1O2H_ck

- Caso você tenha dificuldade em colocar os headers, basta copiar a estrutura em baixo do comentário "# Configurações" em main.py, colocar no chatgpt, copiar todo o conteúdo do devloper tools e pedir para o chat adaptar para o seu header

# Configurações das variáveis de ambiente

Aqui você deve abrir o arquivo .env e colocar as informações lá

- BLUESKY_HANDLE=conta_destino
- BLUESKY_PASSWORD=Senha_conta_destino
- TWITTER_USERNAME=Conta_twitter_importar
- NITTER_INSTANCE=https://nitter.lucabased.xyz

- Só mude o Nitter instance caso necessário, a atual funciona bem
