import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Carrega a senha do banco de dados
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configura a página para ocupar a tela toda
st.set_page_config(page_title="Monitor de Preços", page_icon="📈", layout="wide")

@st.cache_data(ttl=60)
def buscar_dados():
    try:
        conexao = psycopg2.connect(DATABASE_URL)
        query = "SELECT data_coleta, produto, loja, preco, link_produto FROM historico_precos ORDER BY data_coleta ASC;"
        df = pd.read_sql(query, conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        return pd.DataFrame()

df = buscar_dados()

# --- TÍTULO DO DASHBOARD ---
st.title("📈 Dashboard de Monitoramento de Preços")
st.markdown("Acompanhe a variação de preços da concorrência de forma automatizada.")
st.divider()

if df.empty:
    st.warning("Nenhum dado encontrado no banco de dados ainda.")
else:
    # Garantir que a data é tratada corretamente
    df['data_coleta'] = pd.to_datetime(df['data_coleta'])
    
    # --- MENU LATERAL (SIDEBAR) ---
    st.sidebar.header("⚙️ Filtros e Buscas")
    produtos_unicos = df['produto'].unique()
    
    produto_selecionado = st.sidebar.selectbox(
        "Selecione um produto para análise detalhada:", 
        ["Visão Geral (Todos)"] + list(produtos_unicos)
    )

    st.sidebar.info("💡 Dica: Os dados são atualizados automaticamente todos os dias pelo nosso bot na nuvem!")

    # --- TELA 1: VISÃO GERAL ---
    if produto_selecionado == "Visão Geral (Todos)":
        # KPIs Gerais
        col1, col2 = st.columns(2)
        col1.metric("📦 Total de Produtos Monitorados", len(produtos_unicos))
        col2.metric("⏱️ Última Atualização do Robô", df['data_coleta'].max().strftime('%d/%m/%Y %H:%M'))
        
        st.subheader("Top 10 Produtos Mais Caros (Atualmente)")
        # 1. Ordena tudo do mais recente para o mais antigo
        df_recente = df.sort_values('data_coleta', ascending=False)
        # 2. Remove duplicatas mantendo apenas o preço mais novo de CADA produto
        df_ultima_coleta = df_recente.drop_duplicates(subset=['produto'], keep='first')
        # 3. Agora sim, pega os 10 mais caros dessa lista filtrada
        df_top10 = df_ultima_coleta.nlargest(10, 'preco')
        
        # Gráfico de barras ajustado
        st.bar_chart(data=df_top10.set_index('produto')['preco'])
    # --- TELA 2: PRODUTO ESPECÍFICO ---
    else:
        # Filtra os dados só para o produto escolhido
        df_prod = df[df['produto'] == produto_selecionado].copy()
        
        # Cálculos Inteligentes para os KPIs
        preco_atual = float(df_prod.iloc[-1]['preco'])
        max_preco = float(df_prod['preco'].max())
        min_preco = float(df_prod['preco'].min())
        
        # Calcula se o preço caiu ou subiu em relação à coleta anterior
        if len(df_prod) > 1:
            preco_anterior = float(df_prod.iloc[-2]['preco'])
            variacao = preco_atual - preco_anterior
        else:
            variacao = 0.0

        st.subheader(f"Análise de: {produto_selecionado}")
        
        # Mostra as Caixas de KPIs (Igual bolsa de valores)
        kpi1, kpi2, kpi3 = st.columns(3)
        # Se a variação for negativa, o Streamlit já pinta a setinha de verde para queda de preço! (Inverte o padrão se quiser usando delta_color)
        kpi1.metric(label="Preço Atual", value=f"£ {preco_atual:.2f}", delta=f"{variacao:.2f}", delta_color="inverse")
        kpi2.metric(label="Maior Preço Histórico", value=f"£ {max_preco:.2f}")
        kpi3.metric(label="Menor Preço Histórico", value=f"£ {min_preco:.2f}")
        
        # Gráfico de Linha do produto
        st.line_chart(data=df_prod.set_index('data_coleta')['preco'])

    st.divider()
    
    # --- ÁREA DE DADOS BRUTOS E EXPORTAÇÃO ---
    st.subheader("Tabela de Dados Brutos")
    # Formata a data bonitinha pra tabela
    df_exibicao = df.copy()
    df_exibicao['data_coleta'] = df_exibicao['data_coleta'].dt.strftime('%d/%m/%Y %H:%M:%S')
    st.dataframe(df_exibicao, use_container_width=True)
    
    # Botão Mágico para baixar Excel/CSV
    csv = df_exibicao.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Histórico Completo em CSV",
        data=csv,
        file_name='historico_precos_concorrencia.csv',
        mime='text/csv',
    )