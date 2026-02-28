import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# --- NOSSO DEDO-DURO ---
if DATABASE_URL is None:
    print("ALERTA: O Python não conseguiu ler o arquivo .env! Verifique se o arquivo não ficou salvo como .env.txt sem querer.")
else:
    print("Sucesso: Arquivo .env lido com sucesso!")
# -----------------------

# --- SUAS NOVAS VARIÁVEIS ---
URL_PRODUTO = "https://www.mercadolivre.com.br/placa-de-video-nvidia-msi-gaming-x-trio-geforce-rtx-40-series-rtx-4090-24gb/p/MLB21036464"
NOME_PRODUTO = "RTX 4090 MSI Gaming X Trio 24GB"
LOJA = "Mercado Livre"

def pegar_preco_mercado_livre(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        preco_elemento = soup.find("span", class_="andes-money-amount__fraction")
        
        if preco_elemento:
            preco_texto = preco_elemento.text.replace(".", "")
            return float(preco_texto)
        else:
            print("Não foi possível encontrar o elemento de preço na página.")
            return None
    else:
        print(f"Erro ao acessar a página: Status {resposta.status_code}")
        return None

def salvar_no_banco(produto, loja, preco, link):
    conexao = None
    cursor = None
    try:
        print("Tentando conectar ao banco de dados Neon...")
        conexao = psycopg2.connect(DATABASE_URL)
        cursor = conexao.cursor()
        
        query = """
            INSERT INTO historico_precos (produto, loja, preco, link_produto)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (produto, loja, preco, link))
        conexao.commit()
        
        print(f"VITÓRIA! Preço de R$ {preco} da {produto} salvo no Neon.tech!")
        
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

if __name__ == "__main__":
    print(f"Iniciando coleta de dados para: {NOME_PRODUTO}...")
    preco_atual = pegar_preco_mercado_livre(URL_PRODUTO)
    
    if preco_atual:
        salvar_no_banco(NOME_PRODUTO, LOJA, preco_atual, URL_PRODUTO)