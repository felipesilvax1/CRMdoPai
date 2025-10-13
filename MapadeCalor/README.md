Aplicação de Mapa de Prospecção em Tempo Real
Esta é uma aplicação web local que exibe os dados de prospecção do seu banco de dados em um mapa interativo e dinâmico.

Pré-requisitos
Python: Certifique-se de que o Python está instalado e funcionando no seu terminal.

Bibliotecas Python: Você precisará da biblioteca Flask e pandas.

Arquivo de Cache: Esta aplicação requer que o arquivo cache_coordenadas_bd.csv já exista na pasta data. Se ele não existir, execute o script anterior (HeatMap_CRM_Final.py) uma última vez para gerá-lo.

Como Executar
Siga estes passos com atenção:

1. Estrutura de Pastas (ATUALIZADA)

Sua nova estrutura de pastas está perfeita e o script foi adaptado para ela:

C:\Users\PwC\Documents\CRM
│
├───backend
│   └─── app_tempo_real.py         <-- O backend da aplicação
│
├───data
│   ├─── CNPJ_Processado.db        <-- Seu banco de dados
│   └─── cache_coordenadas_bd.csv  <-- O arquivo de cache
│
└───frontend
    └───templates
        └─── index.html           <-- O frontend do mapa

2. Instalar o Flask

Se você ainda não tem o Flask instalado, abra seu terminal e execute:

C:\Users\PwC\AppData\Local\Microsoft\WindowsApps\python3.12.exe -m pip install Flask

3. Iniciar a Aplicação (NOVO COMANDO)

Abra seu terminal.

Navegue até a pasta backend:

cd C:\Users\PwC\Documents\CRM\backend

Execute o script do backend de dentro desta pasta:

python.exe .\app_tempo_real.py

4. Acessar o Mapa

Após executar o comando acima, você verá mensagens no seu terminal, terminando com algo como:
Abra seu navegador e acesse: http://127.0.0.1:5000

Copie o endereço http://127.0.0.1:5000 e cole na barra de endereços do seu navegador.

Seu mapa interativo em tempo real irá carregar! Para desligar o servidor, volte ao terminal e pressione Ctrl + C.

