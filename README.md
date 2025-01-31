# Instructions to Run the Project

## Step 1: Clone the Repository

Clone the repository to your local environment:

```
git clone https://github.com/andresouza1807/Waha_Groq_langchain.git
```

## Step 2: Insert the LLM API Key

**Important:** Before starting the containers, you need to configure the **API Key** for the LLM (Large Language Model) that will be used in the bot.

1. Navigate to the configuration file that contains the API key (usually, this is in a `.env` file or something similar).
2. Insert your API Key in the corresponding field. For example:
   ```
   LLM_API_KEY=Your_API_KEY_here
   ```

## Step 3: Install Docker

Make sure you have the latest version of [Docker](https://www.docker.com/get-started) installed on your machine. If you don't have it, follow the instructions in the link to install it.

## Step 4: Start the Containers

After inserting the API Key and installing Docker, navigate to the folder where the project is saved and run the following commands in your command line (CLI):

```
docker-compose up --build api
docker-compose up --build waha
```

These commands will build and start the necessary containers for the project to function.

## Step 5: Access the Dashboard

After the containers are up, open your browser and go to the following URL:

```
http://[::1]:3000/dashboard/
```

## Step 6: Configure the Session

1. In the control panel, go to the **'Sessions'** tab and click on **'Configuration'**.
2. Configure the **'Webhook'** session with the URL `http://api:5000/chatbot/webhook`.
3. In **'Events'**, check only the **'Message'** option.
4. After configuring, click **'Update'** to save the changes.

## Step 7: Start the Session

1. Still in the **'Sessions'** tab, next to **'Configuration'**, click **'Start'**.
2. After clicking **'Start'**, the **'Status'** column will change to "Login".
3. Click the **'Login'** button, scan the QR code with your WhatsApp, and wait for the synchronization.

## Done!

Your environment is set up and running! You can now interact with the bot.

If you have any questions or suggestions, feel free to reach out! 

=================================================================================================

# Instruções para Rodar o Projeto

## Passo 1: Clonar o Repositório

Clone o repositório para o seu ambiente local:

```
git clone https://github.com/andresouza1807/Waha_Groq_langchain.git
```

## Passo 2: Inserir a API Key da LLM

**Importante:** Antes de inicializar os containers, você deve configurar a **API Key** da LLM (Large Language Model) que será usada no bot.

1. Navegue até o arquivo de configuração que contém a chave da API (geralmente, isso está em um arquivo `.env` ou algo semelhante).
2. Insira a API Key no campo correspondente. Por exemplo:
   ```
   LLM_API_KEY=Sua_API_KEY_aqui
   ```

## Passo 3: Instalar o Docker

Certifique-se de ter a versão mais recente do [Docker](https://www.docker.com/get-started) instalada em sua máquina. Se não tiver, siga as instruções no link para a instalação.

## Passo 4: Executar os Containers

Após inserir a API Key e instalar o Docker, navegue até a pasta onde o projeto está salvo e execute os comandos abaixo na sua linha de comando (CLI):

```
docker-compose up --build api
docker-compose up --build waha
```

Esses comandos vão construir e rodar os containers necessários para o funcionamento do projeto.

## Passo 5: Acessar o Dashboard

Após a inicialização dos containers, abra o seu navegador e acesse a URL abaixo:

```
http://[::1]:3000/dashboard/
```

## Passo 6: Configurar a Sessão

1. No painel de controle, vá até a aba **'Sessions'** e clique em **'Configuration'**.
2. Configure a sessão **'Webhook'** com a URL `http://api:5000/chatbot/webhook`.
3. Em **'Events'**, marque apenas a opção **'Message'**.
4. Após configurar, clique em **'Update'** para salvar as alterações.

## Passo 7: Iniciar a Sessão

1. Ainda na aba **'Sessions'**, ao lado de **'Configuration'**, clique em **'Start'**.
2. Após clicar em **'Start'**, você verá a coluna **'Status'** mudar para "Login".
3. Clique no botão **'Login'**, escaneie o QR code com o seu WhatsApp e aguarde a sincronização.

## Pronto!

Seu ambiente está configurado e funcionando! Agora você pode interagir com o bot.

Se tiver alguma dúvida ou sugestão, não hesite em entrar em contato! 

---
