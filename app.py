import streamlit as st
import pandas as pd
import psycopg2
import os
import numpy as np
from dotenv import load_dotenv

# Carrega a senha do banco de dados
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configura a página para ocupar a tela toda
st.set_page_config(page_title="Monitor de Preços", page_icon="📈", layout="wide")

# Mudámos o nome da função para FORÇAR o Streamlit a limpar o cache antigo da memória
@st.cache_data(ttl=60)
def carregar_dados_historico():
    try:
        conexao = psycopg2.connect(DATABASE_URL)
        query = "SELECT data_coleta, produto, loja, preco, link_produto FROM historico_precos ORDER BY data_coleta ASC;"
        df = pd.read_sql(query, conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        return pd.DataFrame()

df = carregar_dados_historico()

# --- TÍTULO DO DASHBOARD ---
st.title("📈 Dashboard de Monitoramento de Preços")
st.markdown("Acompanhe a variação de preços da concorrência de forma automatizada.")
st.divider()

if df.empty:
    st.warning("Nenhum dado encontrado no banco de dados ainda.")
else:
    # Garantir que a data é tratada corretamente
    df['data_coleta'] = pd.to_datetime(df['data_coleta'])
    
    # 🧹 LIMPEZA DE CHOQUE (Regex)
    # Substitui qualquer tipo de espaço bizarro de web scraping (\xa0, tabs, quebras de linha)
    # por um espaço normal, e limpa as bordas. 
    df['produto'] = df['produto'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # --- MENU LATERAL (SIDEBAR) ---
    st.sidebar.header("⚙️ Filtros e Buscas")
    
    # 🎲 TRUQUE DE PORTFÓLIO: Simulador de flutuações de mercado
    st.sidebar.markdown("---")
    modo_demo = st.sidebar.toggle("🎲 Modo Portfólio (Simular Variações)", value=False, help="Como o site alvo tem preços estáticos, ative isto para gerar flutuações artificiais nos dados e ver os gráficos a funcionar!")
    
    if modo_demo:
        # Fixamos a semente (seed) para que as variações sejam aleatórias, mas não mudem a cada clique
        np.random.seed(42)
        # Multiplica o preço original por um fator aleatório entre 0.8 (-20%) e 1.2 (+20%)
        df['preco'] = df['preco'] * np.random.uniform(0.8, 1.2, size=len(df))
        # Arredonda para 2 casas decimais
        df['preco'] = df['preco'].round(2)
        
        st.sidebar.success("Variações de mercado ativadas!")
    st.sidebar.markdown("---")

    # Ordena os produtos de A a Z para o menu ficar profissional
    produtos_unicos = sorted(df['produto'].unique())
    
    produto_selecionado = st.sidebar.selectbox(
        "Selecione um produto para análise detalhada:", 
        ["Visão Geral (Todos)"] + produtos_unicos
    )

    st.sidebar.info("💡 Dica: Os dados são atualizados automaticamente todos os dias pelo nosso bot na nuvem!")

    # --- TELA 1: VISÃO GERAL ---
    if produto_selecionado == "Visão Geral (Todos)":
        # KPIs Gerais
        col1, col2 = st.columns(2)
        col1.metric("📦 Total de Produtos Monitorados", len(produtos_unicos))
        col2.metric("⏱️ Última Atualização do Robô", df['data_coleta'].max().strftime('%d/%m/%Y %H:%M'))
        
        st.subheader("Top 10 Produtos Mais Caros (Atualmente)")
        
        # Filtra para pegar apenas o preço mais recente de cada produto limpo
        df_recente = df.sort_values('data_coleta', ascending=False)
        df_ultima_coleta = df_recente.drop_duplicates(subset=['produto'], keep='first')
        df_top10 = df_ultima_coleta.nlargest(10, 'preco')
        
        # Gráfico de barras sem repetições
        st.bar_chart(data=df_top10.set_index('produto')['preco'])

    # --- TELA 2: PRODUTO ESPECÍFICO ---
    else:
        # Filtra os dados só para o produto escolhido
        df_prod = df[df['produto'] == produto_selecionado].copy()
        
        # Cálculos de máximas e mínimas
        preco_atual = float(df_prod.iloc[-1]['preco'])
        max_preco = float(df_prod['preco'].max())
        min_preco = float(df_prod['preco'].min())
        
        # Cálculo Turbinado: Variação Absoluta e Porcentagem
        if len(df_prod) > 1:
            preco_anterior = float(df_prod.iloc[-2]['preco'])
            variacao = preco_atual - preco_anterior
            
            # Evita divisão por zero caso o preço anterior fosse 0
            if preco_anterior > 0:
                variacao_percentual = (variacao / preco_anterior) * 100
            else:
                variacao_percentual = 0.0
                
            # Monta o texto que vai aparecer no KPI (Ex: "£ -2.50 (-4.8%)")
            delta_texto = f"£ {variacao:.2f} ({variacao_percentual:.2f}%)"
        else:
            variacao = 0.0
            delta_texto = "£ 0.00 (0.00%)"

        st.subheader(f"Análise de: {produto_selecionado}")
        
        # Mostra as Caixas de KPIs 
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # delta_color="inverse" deixa a queda de preço verde (bom para comprar) e alta vermelha.
        kpi1.metric(label="Preço Atual", value=f"£ {preco_atual:.2f}", delta=delta_texto, delta_color="inverse")
        kpi2.metric(label="Maior Preço Histórico", value=f"£ {max_preco:.2f}")
        kpi3.metric(label="Menor Preço Histórico", value=f"£ {min_preco:.2f}")
        
        # Gráfico de Linha do produto
        st.line_chart(data=df_prod.set_index('data_coleta')['preco'])

    st.divider()
    
    # --- ÁREA DE DADOS BRUTOS E EXPORTAÇÃO ---
    st.subheader("Tabela de Dados Brutos (Mais Recentes no Topo)")
    
    # Organiza a tabela para mostrar o que o robô pegou hoje primeiro
    df_exibicao = df.sort_values('data_coleta', ascending=False).copy()
    df_exibicao['data_coleta'] = df_exibicao['data_coleta'].dt.strftime('%d/%m/%Y %H:%M:%S')
    
    # Exibe a tabela ocultando o índice numérico
    st.dataframe(df_exibicao, hide_index=True, use_container_width=True)
    
    # Botão para baixar Excel/CSV
    csv = df_exibicao.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Histórico Completo em CSV",
        data=csv,
        file_name='historico_precos_concorrencia.csv',
        mime='text/csv',
    )