import json
import logging
import urllib.parse
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do Flask
app = Flask(__name__)

# Função para configurar o webdriver (Agora global)
driver = None

def config_driver():

    global driver
    if driver is None:
        options = Options()
        options.add_argument("--headless")  # Executar sem abrir o navegador
        options.add_argument("--disable-gpu")  # Desabilitar o uso de GPU
        options.add_argument("--window-size=1920x1080")  # Definir o tamanho da janela
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    return driver

# Função para extrair os dados de uma edição
def extrair_dados_da_edicao(edicao):
    """Extrai os dados de uma edição específica"""
    try:
        nome_edicao = edicao.find_element(By.XPATH, './/div[@class="label-edition"]/a').text
        preco_min = edicao.find_element(By.XPATH, './/div[@class="price price-min"]').text
        preco_medium = edicao.find_element(By.XPATH, './/div[@class="price price-medium"]').text
        preco_max = edicao.find_element(By.XPATH, './/div[@class="price price-max"]').text
        
        variants = edicao.find_elements(By.XPATH, './/div[contains(@class, "container-extras")]/div')
        dados = []
        
        for variacao in variants:
            tipo_edicao = variacao.text  # Extrair o tipo da edição (Normal, Foil, etc.)
            dados.append({
                "Edição": nome_edicao,
                "Tipo": tipo_edicao,
                "Preço Mínimo": preco_min,
                "Preço Médio": preco_medium,
                "Preço Máximo": preco_max
            })
        
        return dados
    except Exception as e:
        logging.error(f"Erro ao extrair dados de uma edição: {e}")
        return []

# Função para extrair os dados do card
def extrair_dados_do_card(card_name):
    """Extrai os dados do card pesquisado na página do Ligamagic."""
    card_name_url = urllib.parse.quote(card_name)
    url = f"https://www.ligamagic.com.br/?view=cards/card&card={card_name_url}&tipo=1"
    
    # Configura o driver
    driver = config_driver()
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        logging.error(f"Erro ao carregar a página: {e}")
        return json.dumps([])  # Retorna uma lista vazia em caso de erro
    
    dados = []  

    try:
        open_modal_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[1]/div[3]/div[2]/div/div/div[6]/div/div[1]/span'))
        )
        open_modal_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '/html/body/main/div[11]/div'))
        )
        
        editions = driver.find_elements(By.XPATH, '//div[contains(@class, "container-edition")]')
        
        # Criar barra de progresso com o tqdm
        with tqdm(total=len(editions), desc="Extraindo dados...", unit="edição") as pbar:
   
            with ThreadPoolExecutor() as executor:
                resultados = executor.map(extrair_dados_da_edicao, editions)
                for resultado in resultados:
                    dados.extend(resultado)  
                    pbar.update(1) 
    except Exception as e:
        logging.error(f"Erro ao tentar extrair os dados: {e}")
    
    finally:
        pass

    return json.dumps(dados, ensure_ascii=False, indent=4)

@app.route('/extrair-dados', methods=['POST'])
def extrair_dados_api():
    """Endpoint da API que recebe o nome da carta e retorna os dados em formato JSON."""
    try:
        data = request.get_json()
        card_name = data.get('card_name')
        
        if not card_name:
            return jsonify({"error": "O campo 'card_name' é obrigatório!"}), 400

        # Extrair dados do card
        json_dados = extrair_dados_do_card(card_name)

        # Retornar a resposta como JSON
        return jsonify(json.loads(json_dados)), 200

    except Exception as e:
        logging.error(f"Erro ao processar a solicitação: {e}")
        return jsonify({"error": "Ocorreu um erro ao processar a solicitação!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
