import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Carrega a senha do banco de dados
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="Monitor de Preços", layout="wide")

@st.cache_data(ttl=60)
def buscar_dados():
    try:
        conexao = psycopg2.connect(DATABASE_URL)
        # Puxa os dados ordenados do mais recente para o mais antigo
        query = "SELECT data_coleta, produto, loja, preco, link_produto FROM historico_precos ORDER BY data_coleta DESC;"
        df = pd.read_sql(query, conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        return pd.DataFrame()

# --- VISUAL DA PÁGINA ---
st.title("📊 Monitoramento de Preços da Concorrência")
st.write("Acompanhe automaticamente a variação de preços de múltiplos produtos.")

df = buscar_dados()

if df.empty:
    st.warning("Nenhum dado encontrado no banco de dados.")
else:
    # Formata a data
    df['data_coleta'] = pd.to_datetime(df['data_coleta']).dt.strftime('%d/%m/%Y %H:%M')
    
    # --- FILTRO INTERATIVO ---
    produtos_unicos = df['produto'].unique()
    produto_selecionado = st.selectbox(
        "🔎 Selecione um produto para analisar:", 
        ["Visão Geral (Top 10 Mais Caros)"] + list(produtos_unicos)
    )
    
    st.divider() # Linha de separação
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Base de Dados")
        # Se escolheu um produto específico, filtra a tabela
        if produto_selecionado != "Visão Geral (Top 10 Mais Caros)":
            df_filtrado = df[df['produto'] == produto_selecionado]
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
            
    with col2:
        # Se escolheu um produto específico, mostra o gráfico de linha dele
        if produto_selecionado != "Visão Geral (Top 10 Mais Caros)":
            st.subheader(f"Evolução de Preço: {produto_selecionado}")
            df_grafico = df[df['produto'] == produto_selecionado]
            st.line_chart(data=df_grafico, x='data_coleta', y='preco')
        # Se está na visão geral, mostra um gráfico de barras dos mais caros
        else:
            st.subheader("Top 10 Livros Mais Caros")
            # Pega só os dados da raspagem mais recente
            ultima_data = df['data_coleta'].max()
            df_ultima_coleta = df[df['data_coleta'] == ultima_data]
            # Pega os 10 mais caros
            df_top10 = df_ultima_coleta.nlargest(10, 'preco')
            st.bar_chart(data=df_top10, x='produto', y='preco')