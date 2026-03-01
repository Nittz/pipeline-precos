import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

# Configurações do arquivo .env
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(diretorio_atual, '.env')
load_dotenv(caminho_env)

DATABASE_URL = os.getenv("DATABASE_URL")

# --- AGORA A URL É A PÁGINA PRINCIPAL DO CATÁLOGO ---
URL_CATALOGO = "http://books.toscrape.com/index.html"
LOJA = "Books to Scrape"

def pegar_varios_livros(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    resposta = requests.get(url, headers=headers)
    livros_coletados = [] # Uma lista vazia para guardarmos todos os livros que acharmos
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # O BeautifulSoup vai procurar TODOS os blocos de código que representam um livro na tela
        blocos_de_livros = soup.find_all("article", class_="product_pod")
        
        # Para cada livro que ele encontrar, vamos extrair os dados:
        for bloco in blocos_de_livros:
            # 1. Pega o título (fica escondido dentro da tag <a> do <h3>)
            titulo = bloco.h3.a["title"]
            
            # 2. Pega o preço
            preco_elemento = bloco.find("p", class_="price_color")
            if preco_elemento:
                preco_texto = preco_elemento.text.replace("£", "").replace("Â", "").strip()
                preco_float = float(preco_texto)
            else:
                preco_float = 0.0
                
            # 3. Pega o link do livro para salvar junto
            link_relativo = bloco.h3.a["href"]
            link_completo = f"http://books.toscrape.com/{link_relativo}"
            
            # Guarda as informações deste livro na nossa lista
            livros_coletados.append({
                "titulo": titulo,
                "preco": preco_float,
                "link": link_completo
            })
            
        return livros_coletados
    else:
        print(f"Erro ao acessar a página: Status {resposta.status_code}")
        return []

def salvar_no_banco(produto, loja, preco, link):
    conexao = None
    cursor = None
    try:
        conexao = psycopg2.connect(DATABASE_URL)
        cursor = conexao.cursor()
        query = """
            INSERT INTO historico_precos (produto, loja, preco, link_produto)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (produto, loja, preco, link))
        conexao.commit()
        print(f"✅ Salvo: {produto} - £ {preco}")
    except Exception as e:
        print(f"❌ Erro ao salvar '{produto}' no banco: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

if __name__ == "__main__":
    print(f"Iniciando coleta em massa no catálogo: {URL_CATALOGO}...")
    lista_de_livros = pegar_varios_livros(URL_CATALOGO)
    
    if lista_de_livros:
        print(f"Encontrados {len(lista_de_livros)} livros! Enviando para o banco de dados...")
        
        # Um laço de repetição para salvar cada livro da lista no banco de dados
        for livro in lista_de_livros:
            salvar_no_banco(livro["titulo"], LOJA, livro["preco"], livro["link"])
            
        print("Coleta e armazenamento concluídos com sucesso!")
    else:
        print("Nenhum livro foi encontrado na página.")