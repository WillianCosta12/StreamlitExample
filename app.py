import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Análise de Grafo", layout="wide")
st.title("🔗 Analisador de Grafo – arquivo `grafo.csv` carregado automaticamente")

# Carrega o CSV da pasta raiz
@st.cache_data
def load_data():
    return pd.read_csv("grafo.csv")

try:
    df = load_data()
    st.success("✅ Arquivo 'grafo.csv' carregado com sucesso !")
    st.dataframe(df.head())
except FileNotFoundError:
    st.error("❌ Não encontrou o arquivo 'grafo.csv'. Certifique-se de que ele está na raiz do repositório.")

# Processa e exibe a rede
if 'df' in locals():
    expected_cols = {'origem','destino'}
    if expected_cols.issubset(df.columns):
        G = nx.from_pandas_edgelist(df, 'origem', 'destino', edge_attr=True)
        st.write(f"📊 Número de nós: {G.number_of_nodes()} — Arestas: {G.number_of_edges()}")
        st.write(f"Grau médio: {sum(dict(G.degree()).values())/G.number_of_nodes():.2f}")
        st.write(f"Coeficiente de agrupamento: {nx.average_clustering(G):.2f}")

        net = Network(height="600px", width="100%", notebook=True)
        net.from_nx(G)
        net.show_buttons(filter_=['physics','nodes','edges'])
        net.save_graph("network.html")

        HtmlFile = open("network.html", 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=650, scrolling=True)
    else:
        st.warning("O CSV deve conter as colunas 'origem' e 'destino' para geração do grafo.")
