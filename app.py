import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Análise de Grafo", layout="wide")
st.title("🔍 Analisador de Grafo (com colunas Source/Target)")

# Função para carregar o CSV
@st.cache_data
def load_data():
    return pd.read_csv("grafo.csv")

# Tenta carregar o arquivo
try:
    df = load_data()
    st.success("✅ 'grafo.csv' carregado com sucesso!")
    cols = df.columns.tolist()
    st.write("### Colunas disponíveis no dataset:")
    st.write(cols)

    # Se houver 'Source' e 'Target', selecione automaticamente
    if 'Source' in cols and 'Target' in cols:
        col_origem = 'Source'
        col_destino = 'Target'
        st.info("Usando 'Source' como origem e 'Target' como destino")
    else:
        # Senão, permita seleção manual
        col_origem = st.selectbox("Escolha a coluna de ORIGEM", cols, key='origem')
        col_destino = st.selectbox("Escolha a coluna de DESTINO", cols, key='destino')

    # Geração do grafo
    G = nx.from_pandas_edgelist(df, col_origem, col_destino, edge_attr=True, create_using=nx.DiGraph() if 'Directed' in df.get('Type', []) else nx.Graph())
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    st.write(f"📊 Número de nós: **{num_nodes}**  •  Arestas: **{num_edges}**")
    st.write(f"Grau médio: {sum(dict(G.degree()).values())/num_nodes:.2f}")
    st.write(f"Coeficiente de agrupamento: {nx.average_clustering(G):.2f}")

    # Visualização com Pyvis
    net = Network(height="600px", width="100%", notebook=True, directed='Directed' in df.get('Type', []))
    net.from_nx(G)
    net.show_buttons(filter_=['physics','nodes','edges'])
    net.save_graph("network.html")
    components.html(open("network.html", 'r', encoding='utf-8').read(), height=650)

except FileNotFoundError:
    st.error("❌ Arquivo 'grafo.csv' não encontrado.")
except Exception as e:
    st.error(f"❌ Erro ao processar o grafo: {e}")
