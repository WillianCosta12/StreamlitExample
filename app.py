import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Análise de Subgrafo", layout="wide")
st.title("🔎 Rede com Subgrafo dos Top‑N Nós por Grau")

# Carrega CSV da raiz do repo
@st.cache_data
def load_data():
    return pd.read_csv("grafo.csv")

try:
    df = load_data()
    st.success("✅ CSV carregado!")
    cols = df.columns.tolist()
    st.write("Colunas disponíveis:", cols)

    # Détecta colunas padrão
    col_origem = 'Source' if 'Source' in cols else st.selectbox("Origem", cols)
    col_destino = 'Target' if 'Target' in cols else st.selectbox("Destino", cols)

    # Monta grafo base (direcionado se houver Type Directed)
    directed = 'Directed' in df.get('Type', [])
    G = nx.from_pandas_edgelist(df, col_origem, col_destino,
                                edge_attr=True,
                                create_using=nx.DiGraph() if directed else nx.Graph())

    # Parâmetros para subgrafo
    top_n = st.sidebar.slider("Número de nós mais conectados (Top N)", 5, min(len(G), 200), value=50)

    # Seleciona nós com maior grau
    degree_sorted = sorted(G.degree(), key=lambda x: x[1], reverse=True)
    top_nodes = [n for n, _ in degree_sorted[:top_n]]
    G_sub = G.subgraph(top_nodes).copy()  # Subgrafo próprio com cópia de atributos :contentReference[oaicite:1]{index=1}

    st.write(f"🎯 Subgrafo com os Top {top_n} nós por grau:")
    st.write(f"Nós: {G_sub.number_of_nodes()}, Arestas: {G_sub.number_of_edges()}")

    # Métricas do subgrafo
    st.write(f"Grau médio: {sum(dict(G_sub.degree()).values())/G_sub.number_of_nodes():.2f}")
    st.write(f"Coeficiente de agrupamento: {nx.average_clustering(G_sub):.2f}")

    # Visualização com Pyvis
    net = Network(height="600px", width="100%", notebook=True, directed=directed)
    net.from_nx(G_sub)
    net.show_buttons(filter_=['physics', 'nodes', 'edges'])
    net.save_graph("subgrafo.html")
    components.html(open("subgrafo.html", 'r', encoding='utf-8').read(), height=650)

except FileNotFoundError:
    st.error("❌ 'grafo.csv' não encontrado.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro: {e}")
