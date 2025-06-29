import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Redes Avançada", layout="wide")
st.title("📊 Análise Estrutural e de Centralidade da Rede")

@st.cache_data
def load_data():
    return pd.read_csv("grafo.csv")

try:
    df = load_data()
    cols = df.columns.tolist()
    src = 'Source' if 'Source' in cols else st.sidebar.selectbox("Origem", cols)
    tgt = 'Target' if 'Target' in cols else st.sidebar.selectbox("Destino", cols)
    directed = 'Directed' in df.get('Type', [])
    G = nx.from_pandas_edgelist(df, src, tgt,
                                edge_attr=True,
                                create_using=nx.DiGraph() if directed else nx.Graph())

    
    subtype = st.sidebar.selectbox("Subgrafo", [
        "Rede completa",
        "Maior componente conectado (weak)",
        "Maior componente fortemente conectado",
    ])
    if subtype == "Rede completa":
        G_sub = G.copy()
    elif subtype == "Maior componente conectado (weak)":
        if directed:
            comp = max(nx.weakly_connected_components(G), key=len)
        else:
            comp = max(nx.connected_components(G), key=len)
        G_sub = G.subgraph(comp).copy()
    elif subtype == "Maior componente fortemente conectado":
        if directed:
            comp = max(nx.strongly_connected_components(G), key=len)
            G_sub = G.subgraph(comp).copy()
        else:
            st.warning("❗ Essa opção se aplica apenas a grafos direcionados. Exibindo rede completa.")
            G_sub = G.copy()
    else:
        G_sub = G.copy()


   
    n = G.number_of_nodes()
    e = G.number_of_edges()
    density = nx.density(G)
    assort = nx.degree_assortativity_coefficient(G)
    clustering = nx.transitivity(G)
    scc = nx.number_strongly_connected_components(G) if directed else None
    wcc = nx.number_weakly_connected_components(G) if directed else nx.number_connected_components(G)
    st.subheader("📌 Métricas Estruturais")
    st.markdown(f"""
    - **Densidade** (esparsidade): {density:.4f}  
    - **Assortatividade** (correlação de grau): {assort:.4f}  
    - **Clustering global**: {clustering:.4f}  
    - **Componentes fortemente conectados**: {scc if directed else 'N/A'}  
    - **Componentes fracamente conectados**: {wcc}
    """)

   
    st.subheader("📈 Distribuição de Grau")
    if directed:
        indeg = [d for _, d in G.in_degree()]
        outdeg = [d for _, d in G.out_degree()]
        fig, ax = plt.subplots(1,2, figsize=(10,4))
        ax[0].hist(indeg, bins=20, color='skyblue')
        ax[0].set_title("In-Degree")
        ax[1].hist(outdeg, bins=20, color='salmon')
        ax[1].set_title("Out-Degree")
        st.pyplot(fig)
    else:
        deg = [d for _, d in G.degree()]
        st.bar_chart(pd.Series(deg).value_counts().sort_index())

   
    st.subheader("⭐ Centralidade dos Nós")
    deg = nx.degree_centrality(G)
    eig = nx.eigenvector_centrality(G)
    clo = nx.closeness_centrality(G)
    bet = nx.betweenness_centrality(G)
    centralities = {'Degree': deg, 'Eigenvector': eig, 'Closeness': clo, 'Betweenness': bet}

    metric = st.selectbox("Selecione uma métrica", list(centralities.keys()))
    topk = st.slider("Top K nós", 3, min(50, n), 10)
    tops = sorted(centralities[metric].items(), key=lambda x: x[1], reverse=True)[:topk]
    st.write(f"Top {topk} por **{metric} centrality**")
    st.table(pd.DataFrame(tops, columns=['Node','Score']))

  
    if st.checkbox("Mostrar tamanho dos nós de acordo com centralidade"):
        vals = centralities[metric]
        net = Network(height="600px", width="100%", notebook=True, directed=directed)
        for node in G.nodes():
            net.add_node(node, size=5 + 45 * vals[node])
        for u, v in G.edges():
            net.add_edge(u, v)
        net.show_buttons(filter_=['physics'])
        net.save_graph("central_graph.html")
        components.html(open("central_graph.html",'r').read(), height=650)
    else:
        net = Network(height="600px", width="100%", notebook=True, directed=directed)
        net.from_nx(G)
        net.show_buttons(filter_=['physics'])
        net.save_graph("graph.html")
        components.html(open("graph.html",'r').read(), height=650)

except FileNotFoundError:
    st.error("❌ 'grafo.csv' não encontrado.")
