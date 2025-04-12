import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyecharts.charts import Sankey
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts  # Esta é a importação correta
from pyecharts.charts import Sankey
from streamlit_echarts import st_pyecharts


# Configuração inicial da página
st.set_page_config(
    page_title="Dashboard Redetur",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Ordem cronológica dos meses
ORDEM_MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# Função para carregar dados com cache
@st.cache_data
def load_data():
    file_path = "Power_BI_Fornecedores _Agencias_2023_24.xlsx"
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df = df.dropna(subset=["Agencias"])  # remove entradas sem agência
    
    # Convertendo colunas numéricas
    for col in ["Vendas", "Receita"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Criando coluna 'Tipo' se não existir (para o exemplo)
    if 'Tipo' not in df.columns:
        tipos_exemplo = ['Direto', 'Online', 'Indicação', 'Corporativo', 'Promocional']
        df['Tipo'] = pd.Series(tipos_exemplo * (len(df)//len(tipos_exemplo) + 1))[:len(df)]
    
    # Garantir que os meses estejam no formato correto
    if 'Mês' in df.columns:
        df['Mês'] = df['Mês'].astype(str)
    
    return df

# Carregar dados
df = load_data()

# ===========================================
# SIDEBAR - FILTROS UNIFICADOS
# ===========================================
with st.sidebar:
    st.image("logo original redetur.jpg", width=150)
    
    st.markdown("## Filtros Principais")
    
    # Filtro de Agências
    agencias = df["Agencias"].dropna().unique()
    agencia_sel = st.selectbox(
        "Agência",
        options=["Todas"] + sorted(list(agencias)),
        index=0,
        key="selectbox_agencia"
    )
    
    # Filtro de Ano
    anos = df["Ano"].dropna().unique()
    ano_sel = st.selectbox(
        "Ano", 
        options=["Todos"] + sorted(list(anos), reverse=True),
        index=0,
        key="selectbox_ano"
    )
    
    # Filtro de Mês (dinâmico baseado no ano selecionado)
    if ano_sel != "Todos":
        meses_disponiveis = df[df["Ano"] == ano_sel]["Mês"].dropna().unique()
    else:
        meses_disponiveis = df["Mês"].dropna().unique()
    
    # Ordenar meses cronologicamente
    meses_ordenados = sorted(
        meses_disponiveis,
        key=lambda x: ORDEM_MESES.index(x) if x in ORDEM_MESES else len(ORDEM_MESES)
    )
    
    mês_sel = st.selectbox(
        "Mês", 
        options=["Todos"] + meses_ordenados,
        index=0,
        key="selectbox_mes"
    )
    
    # Filtro de Fornecedores
    fornecedores = df["Fornecedor"].dropna().unique()
    fornecedor_sel = st.selectbox(
        "Fornecedor", 
        options=["Todos"] + sorted(list(fornecedores)),
        index=0,
        key="selectbox_fornecedor"
    )
    
    # Selecionar fornecedores para comparação no radar
    st.markdown("---")
    st.markdown("## Filtros para Gráfico de Radar")
    fornecedores_selecionados = st.multiselect(
        "Selecione fornecedores para comparar (máx. 5)",
        options=fornecedores,
        default=fornecedores[:3] if len(fornecedores) >= 3 else fornecedores,
        key="radar_fornecedores"
    )
    
    st.markdown("---")
    st.markdown("### Informações")
    st.markdown(f"**Total de Registros:** {len(df)}")
    st.markdown(f"**Filtros aplicados:**")
    st.markdown(f"- Agência: {agencia_sel}")
    st.markdown(f"- Ano: {ano_sel}")
    st.markdown(f"- Mês: {mês_sel}")
    st.markdown(f"- Fornecedor: {fornecedor_sel}")

# ===========================================
# APLICAÇÃO DOS FILTROS (PARA TODOS OS GRÁFICOS)
# ===========================================
df_filtrado = df.copy()

if agencia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Agencias"] == agencia_sel]

if ano_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Ano"] == ano_sel]

if mês_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mês"] == mês_sel]

if fornecedor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Fornecedor"] == fornecedor_sel]

# ===========================================
# CONTEÚDO PRINCIPAL
# ===========================================
st.title("📊 Dashboard de Vendas e Receita")
st.markdown("Análise comparativa de desempenho por fornecedor e agência")

# Métricas Resumidas
col1, col2, col3 = st.columns(3)
col1.metric("Total Vendas", f"R$ {df_filtrado['Vendas'].sum():,.2f}")
col2.metric("Total Receita", f"R$ {df_filtrado['Receita'].sum():,.2f}")
col3.metric("Fornecedores Ativos", df_filtrado['Fornecedor'].nunique())

# Gráficos e Visualizações
tab1, tab2 = st.tabs(["📊 Visualizações", "📈 Tabela"])

with tab1:
    # Gráfico de Barras - Vendas por Tipo
    st.subheader("Vendas por Tipo")
    
    # Ordenar meses cronologicamente nos dados
    if mês_sel == "Todos":
        df_filtrado['Mês'] = pd.Categorical(
            df_filtrado['Mês'],
            categories=ORDEM_MESES,
            ordered=True
        )
        df_filtrado = df_filtrado.sort_values('Mês')
    
    fig = px.bar(
        df_filtrado,
        x="Mês" if mês_sel == "Todos" else "Agencias",
        y="Vendas",
        color="Tipo",
        barmode="group",
        title=f"Distribuição por Tipo ({'Todos meses' if mês_sel == 'Todos' else mês_sel})",
        labels={"Vendas": "Valor (R$)"},
        text_auto=True,
        height=500
    )
    
    # Ajustes de layout para manter ordem cronológica
    if mês_sel == "Todos":
        fig.update_xaxes(categoryorder='array', categoryarray=ORDEM_MESES)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de Totais por Tipo (abaixo do gráfico)
    st.subheader("Totais por Tipo")
    vendas_por_tipo = df_filtrado.groupby("Tipo")[["Vendas", "Receita"]].sum().sort_values("Vendas", ascending=False)
    st.dataframe(
        vendas_por_tipo.style.format("{:,.2f}"),
        column_config={
            "Vendas": st.column_config.NumberColumn(format="R$ %.2f"),
            "Receita": st.column_config.NumberColumn(format="R$ %.2f")
        },
        use_container_width=True
    )
    
    # Gráfico de Radar (usando os mesmos filtros principais + seleção de fornecedores)
    st.subheader("📊 Análise Comparativa por Fornecedor")
    
    if len(fornecedores_selecionados) == 0:
        st.warning("Selecione pelo menos 1 fornecedor para gerar o gráfico de radar")
    else:
        # Processar dados para o radar
        dados_radar = []
        for fornecedor in fornecedores_selecionados[:5]:  # Limitar a 5 fornecedores
            df_fornecedor = df_filtrado[df_filtrado["Fornecedor"] == fornecedor]
            
            # Calcular métricas baseadas nos dados disponíveis
            metricas_calculadas = {
                "Fornecedor": fornecedor,
                "Total Vendas": df_fornecedor["Vendas"].sum(),
                "Total Receita": df_fornecedor["Receita"].sum(),
                "Tipos de Serviço": df_fornecedor["Tipo"].nunique(),
                "Meses Ativos": df_fornecedor["Mês"].nunique(),
                "Volume Médio": df_fornecedor["Vendas"].mean()
            }
            dados_radar.append(metricas_calculadas)

        df_radar = pd.DataFrame(dados_radar)

        # Definir métricas para o radar
        metricas_radar = ["Total Vendas", "Total Receita", "Tipos de Serviço", "Meses Ativos", "Volume Médio"]
        
        fig = go.Figure()

        colors = px.colors.qualitative.Plotly
        
        for idx, fornecedor in enumerate(fornecedores_selecionados[:5]):
            dados_fornecedor = df_radar[df_radar["Fornecedor"] == fornecedor]
            valores = [dados_fornecedor[metrica].values[0] for metrica in metricas_radar]
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=metricas_radar,
                fill='toself',
                name=fornecedor,
                line=dict(color=colors[idx % len(colors)]),
                opacity=0.7
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, df_radar[metricas_radar].max().max() * 1.1]
                )),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.1,
                xanchor="center",
                x=0.5
            ),
            height=600,
            margin=dict(l=50, r=50, b=50, t=50),
            title_text=f"Comparação de Fornecedores - Agência: {agencia_sel} | Mês: {mês_sel}",
            title_x=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela com os dados do radar
        st.subheader("Dados Detalhados - Radar")
        st.dataframe(
            df_radar.set_index("Fornecedor"),
            column_config={
                "Total Vendas": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total Receita": st.column_config.NumberColumn(format="R$ %.2f"),
                "Volume Médio": st.column_config.NumberColumn(format="R$ %.2f")
            },
            use_container_width=True
        )
    
    
    
    ############################################################################
    
 # Função para criar o Sankey diagram
def create_sankey_diagram(df):
    # Processar os dados para criar nós e links
    # Exemplo: Agência -> Fornecedor -> Tipo
    nodes = []
    links = []
    
    # Mapear categorias únicas para nós
    agencias = df["Agencias"].unique().tolist()
    fornecedores = df["Fornecedor"].unique().tolist()
    tipos = df["Tipo"].unique().tolist()
    
    # Criar lista de nós com índices
    all_nodes = agencias + fornecedores + tipos
    nodes = [{"name": node} for node in all_nodes]
    
    # Mapear nomes para índices
    node_index = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Criar links entre as categorias
    # Agência -> Fornecedor
    ag_forn = df.groupby(["Agencias", "Fornecedor"])["Vendas"].sum().reset_index()
    links.extend([
        {
            "source": node_index[row["Agencias"]],
            "target": node_index[row["Fornecedor"]],
            "value": float(row["Vendas"])
        }
        for _, row in ag_forn.iterrows()
    ])
    
    # Fornecedor -> Tipo
    forn_tipo = df.groupby(["Fornecedor", "Tipo"])["Vendas"].sum().reset_index()
    links.extend([
        {
            "source": node_index[row["Fornecedor"]],
            "target": node_index[row["Tipo"]],
            "value": float(row["Vendas"])
        }
        for _, row in forn_tipo.iterrows()
    ])
    
    # Criar o gráfico Sankey
    sankey = (
        Sankey(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add(
            series_name="Fluxo de Vendas",
            nodes=nodes,
            links=links,
            linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"),
            label_opts=opts.LabelOpts(position="right"),
            node_gap=10,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                
                pos_top="5%",  # Ajuste da posição vertical do título
                pos_left="center"  # Centralização horizontal
            ),
            tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove"),
        )
    )
    
    return sankey

# Adicionar ao seu dashboard existente
with tab1:
    st.subheader("Fluxo de Vendas por Agência, Fornecedor e Tipo")
    
    if len(df_filtrado) > 0:
        sankey_chart = create_sankey_diagram(df_filtrado)
        st_pyecharts(sankey_chart)
    else:
        st.warning("Não há dados suficientes para exibir o gráfico Sankey com os filtros atuais.")
    
    ##############################################################################
    
    # Gráfico de barras de vendas por mês (considerando histórico)
    st.subheader("Vendas Mensais (Histórico)")
    
    # Preparar dados históricos com base nos filtros principais
    df_historico = df_filtrado.groupby(["Ano", "Mês"])["Vendas"].sum().reset_index()
    
    # Ordenar meses cronologicamente
    df_historico['Mês'] = pd.Categorical(
        df_historico['Mês'],
        categories=ORDEM_MESES,
        ordered=True
    )
    df_historico = df_historico.sort_values(['Ano', 'Mês'])

    # Criar gráfico
    fig = px.bar(
        df_historico,
        x="Mês",
        y="Vendas",
        color="Ano",
        barmode="group",
        labels={"Vendas": "Vendas (R$)"},
        text_auto=True,
        height=500
    )

    # Personalizar layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Mês",
        yaxis_title="Vendas (R$)",
        xaxis={'categoryorder':'array', 'categoryarray':ORDEM_MESES},
        hovermode="x unified"
    )

    # Adicionar valores nas barras
    fig.update_traces(
        texttemplate='R$ %{y:,.2f}',
        textposition='outside',
        textfont_size=12,
        cliponaxis=False
    )

    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos de Pizza lado a lado
    st.subheader("Distribuição Percentual")
    col1, col2 = st.columns(2)
    
    with col1:
        if agencia_sel == "Todas":
            fig = px.pie(
                df_filtrado.groupby("Agencias")["Vendas"].sum().reset_index(),
                names="Agencias",
                values="Vendas",
                title="Por Agência",
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Mostrando dados apenas para a agência selecionada")
    
    with col2:
        if fornecedor_sel == "Todos":
            fig = px.pie(
                df_filtrado.groupby("Fornecedor")["Vendas"].sum().reset_index(),
                names="Fornecedor",
                values="Vendas",
                title="Por Fornecedor",
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Mostrando dados apenas para o fornecedor selecionado")

with tab2:
    st.subheader("Dados Detalhados")
    st.dataframe(
        df_filtrado.reset_index(drop=True),
        column_config={
            "Vendas": st.column_config.NumberColumn(format="R$ %.2f"),
            "Receita": st.column_config.NumberColumn(format="R$ %.2f")
        },
        hide_index=True,
        use_container_width=True,
        height=600
    )
    
    # Botão para exportar dados
    st.download_button(
        label="📥 Exportar dados filtrados",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name=f"dados_redetur_filtrados.csv",
        mime="text/csv",
        key="download_button"
    )