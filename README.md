Markdown

# 📈 End-to-End Data Pipeline: Monitoramento Automático de Preços

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon.tech-blue.svg)](https://neon.tech/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-red.svg)](https://streamlit.io/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF.svg)](https://github.com/features/actions)

**Acesse o Dashboard interativo na nuvem:** https://pipeline-precos-felipe.streamlit.app

## 🎯 Visão Geral do Projeto
Este projeto consiste em uma arquitetura completa de Engenharia de Dados (End-to-End) criada para monitorar, armazenar e analisar a variação de preços de produtos na web de forma 100% automatizada. 

O pipeline extrai dados diariamente, carrega-os em um banco de dados relacional na nuvem e os disponibiliza em um Dashboard analítico com métricas de negócio (KPIs).

## 🏗️ Arquitetura e Fluxo de Dados (ETL)
O projeto foi desenhado para rodar inteiramente na nuvem, sem necessidade de processamento local:

1. **Extração (Extract):** Um script em Python (`scrapper.py`) utiliza `requests` e `BeautifulSoup` para fazer o web scraping de múltiplos produtos do catálogo (Books to Scrape). O script contorna bloqueios simples utilizando Headers (`User-Agent`).
2. **Carga (Load):** Os dados brutos (Nome, Preço, Link) são inseridos em um banco de dados **PostgreSQL** hospedado na AWS através do serviço **Neon.tech**, utilizando a biblioteca `psycopg2`.
3. **Orquestração (Orchestrate):** O **GitHub Actions** atua como o motor de automação do projeto. Um arquivo de workflow (`automacao.yml`) utilizando sintaxe *Cron* cria uma máquina virtual Linux diariamente, instala as dependências e executa o script de extração no piloto automático.
4. **Visualização (Visualize):** Um aplicativo web desenvolvido com **Streamlit** consome os dados atualizados do banco via queries SQL e apresenta um painel interativo hospedado no **Streamlit Community Cloud**.

## 📊 Funcionalidades do Dashboard
- **Visão Geral:** Gráfico de barras destacando os Top 10 produtos mais caros do catálogo atual.
- **Análise Individual:** Menu interativo para selecionar produtos específicos.
- **Métricas Financeiras (KPIs):** Cálculo automático de Preço Atual, Maior/Menor Preço Histórico e **Variação Percentual** em relação à coleta anterior.
- **Gráfico de Evolução:** Acompanhamento temporal da flutuação de preços em gráficos de linha.
- **Exportação:** Botão para download dos dados brutos consolidados em formato `.csv` para análises em outras ferramentas.

## 💻 Tecnologias Utilizadas
- **Linguagem:** Python
- **Bibliotecas Base:** `pandas`, `requests`, `beautifulsoup4`, `psycopg2-binary`, `python-dotenv`
- **Banco de Dados:** PostgreSQL (Neon.tech)
- **Visualização de Dados:** Streamlit
- **Automação:** GitHub Actions CI/CD

## 🚀 Como executar este projeto localmente

### 1. Clone o repositório
```bash
git clone [https://github.com/Nittz/pipeline-precos.git](https://github.com/Nittz/pipeline-precos.git)
cd pipeline-precos
```

### 2. Crie um ambiente virtual e instale as dependências
```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto e adicione a string de conexão do seu banco de dados PostgreSQL:
```env
DATABASE_URL="postgresql://usuario:senha@seu_host.neon.tech/nome_do_banco?sslmode=require"
```

### 4. Execute a Extração de Dados
Para rodar o robô de raspagem e popular o banco de dados:
```bash
python scrapper.py
```

### 5. Inicie o Dashboard
Para visualizar o painel interativo localmente no seu navegador:
```bash
python -m streamlit run app.py
```

---
*Desenvolvido por Felipe para portfólio de Engenharia de Dados.*
