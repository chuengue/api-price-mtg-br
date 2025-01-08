# API para Extração de Dados de Cartas Magic: The Gathering

## Tecnologias Utilizadas

- **Flask**: Framework para construção da API.
- **Selenium**: Biblioteca para automação de navegação no navegador e extração de dados.
- **Webdriver Manager**: Para gerenciar a instalação do ChromeDriver.
- **TQDM**: Para exibir uma barra de progresso ao extrair dados de várias edições.

## Pré-requisitos

Para rodar o projeto, você precisará dos seguintes pré-requisitos instalados:

- Python 3.6 ou superior
- `pip` (gerenciador de pacotes do Python)

## Instalação

1. Clone este repositório:

2. Instale as dependências do projeto:

    pip install -r requirements.txt

3. Inicie o servidor Flask:

A API estará disponível em http://127.0.0.1:5000/

## Endpoints da API
    /extrair-dados

    Método: POST
    Body: JSON contendo o nome da carta.

## Exemplo de requisição:

    {
    "card_name": "Lightning Bolt"
    }
