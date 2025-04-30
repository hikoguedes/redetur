import streamlit as st
import pandas as pd
import plotly.express as px

# ================================================
# CONFIGURAÇÕES GERAIS
# ================================================

# Configuração inicial da página
st.set_page_config(
    page_title="Business Intelligence - Orinter",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Paleta de cores corporativa
CORPORATE_COLORS = {
    'blue': '#1F77B4',
    'orange': '#FF7F0E',
    'green': '#2CA02C',
    'red': '#D62728',
    'purple': '#9467BD',
    'brown': '#8C564B',
    'pink': '#E377C2',
    'gray': '#7F7F7F',
    'yellow': '#BCBD22',
    'teal': '#17BECF'
}

# Estilos CSS personalizados
st.markdown(f"""
    <style>
        .main {{
            background-color: #f8f9fa;
        }}
        .stMetric {{
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stMetric label {{
            font-size: 14px !important;
            color: {CORPORATE_COLORS['gray']} !important;
            font-weight: 500 !important;
        }}
        .stMetric div[data-testid="stMetricValue"] {{
            font-size: 24px !important;
            color: {CORPORATE_COLORS['blue']} !important;
            font-weight: 700 !important;
        }}
        .stMetric div[data-testid="stMetricDelta"] svg {{
            width: 20px !important;
            height: 20px !important;
        }}
        .stExpander {{
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .stDataFrame {{
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stSelectbox, .stMultiselect {{
            margin-bottom: 15px;
        }}
        h1, h2, h3 {{
            color: {CORPORATE_COLORS['blue']} !important;
        }}
    </style>
""", unsafe_allow_html=True)

ORDEM_MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# ================================================
# FUNÇÕES AUXILIARES
# ================================================

def create_corporate_bar_chart(df, x, y, color, title, barmode='group', orientation='v'):
    if orientation == 'h':
        fig = px.bar(
            df,
            y=x,
            x=y,
            color=color,
            barmode=barmode,
            title=title,
            text_auto=True,
            color_discrete_sequence=list(CORPORATE_COLORS.values()),
            orientation='h'
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            barmode=barmode,
            title=title,
            text_auto=True,
            color_discrete_sequence=list(CORPORATE_COLORS.values())
        )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="x unified",
        font=dict(color="#333"),
        title_font=dict(size=18, color=CORPORATE_COLORS['blue']),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    if orientation == 'h':
        fig.update_traces(
            texttemplate='%{x:,.2f}', 
            textposition='outside',
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5
        )
    else:
        fig.update_traces(
            texttemplate='R$ %{y:,.2f}', 
            textposition='outside',
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5
        )
    
    return fig

def create_corporate_pie_chart(df, names, values, title):
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=0.3,
        color_discrete_sequence=list(CORPORATE_COLORS.values()))
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="#333"),
        title_font=dict(size=18, color=CORPORATE_COLORS['blue']),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

def create_podium_chart(df_ranking):
    top_agencies = df_ranking.head(5).copy()
    podium_order = [0, 2, 1, 3, 4]
    top_agencies = top_agencies.iloc[podium_order]
    
    podium_positions = [1, 3, 2, 4, 5]
    podium_heights = [100, 60, 80, 40, 30]
    podium_colors = ['gold', '#cd7f32', 'silver', '#a9a9a9', '#a9a9a9']
    
    podium_df = pd.DataFrame({
        'Agência': top_agencies['Agência'],
        'Posição': podium_positions,
        'Vendas': top_agencies['Total'],
        'Altura': podium_heights,
        'Cor': podium_colors
    })
    
    fig = px.bar(
        podium_df,
        x='Posição',
        y='Altura',
        color='Cor',
        color_discrete_map="identity",
        text='Agência',
        title='🏆 Pódio das Agências (Top 5)',
        labels={'Altura': '', 'Posição': 'Posição no Ranking'},
        hover_data={'Agência': True, 'Vendas': ':.2f', 'Posição': True, 'Altura': False},
        category_orders={'Posição': [1, 2, 3, 4, 5]}
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['🥇 1º', '🥈 2º', '🥉 3º', '4º', '5º']
        ),
        yaxis=dict(showticklabels=False),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    for i, row in podium_df.iterrows():
        fig.add_annotation(
            x=row['Posição'],
            y=row['Altura'] + 5,
            text=f"R$ {row['Vendas']:,.2f}",
            showarrow=False,
            font=dict(size=12, color='black')
        )
    
    return fig

# ================================================
# CARREGAMENTO E PROCESSAMENTO DOS DADOS
# ================================================

@st.cache_data
def load_data():
    # Dados da aba Orinter
    data = {
        "Agência": ["Travel Mix", "Free", "Sierratur", "Guia Sul/RG", "Zzz Tour", "Tri Viagens", 
                   "Universo/F.W.", "Positivo", "Multimarcas", "Vooar", "Viaggiotur", "Matte", 
                   "Magia", "Sete Nove", "Venatur", "Universo/S.A.", "BrA", "Spatur", "Eurolatina", 
                   "B&G /CWB", "Lex Viagens", "Aeroplus", "Sonho & Viagem", "Inova", "Cisplatur", 
                   "Rowam", "Leeatur", "Ma & Na", "Vamos Viajar", "Viva  +", "Bora Bora", "Savagra", 
                   "Viajatur", "Via Nova", "Dreams", "Gapen", "Vianatur (CV Viagens)", "RZ", "Argus", 
                   "Guia Sul/Pelotas", "Calábria", "Acatur", "Ícaro"],
        "Janeiro": [419505.23, 146521.44, 66510.92, 0, 135648.56, 192093.22, 73010.88, 55920.28, 
                   13204.34, 73982.95, 18405.45, 37587.71, 7622.67, 71776.9, 8449.85, 0, 0, 
                   44089.53, 7655.9, 0, 2389.9, 39483.43, 17652.57, 72916.63, 1090.24, 4915.87, 
                   49014.68, 16032.84, 39168.18, 0, 0, 0, 0, 0, 0, 5358.24, 34590, 3818.93, 850, 
                   0, 0, 0, 0],
        "Fevereiro": [248409.74, 112790.71, 124985.41, 0, 230273.43, 148058.4, 98215.1, 38074.02, 
                     44865.6, 37127.43, 76667.08, 79727.18, 6856.2, 47997.39, 29093.69, 0, 0, 
                     11649.54, 73516, 0, 24022.1, 31852.16, 0, 53671.14, 0, 0, 0, 11992.11, 0, 0, 
                     0, 36564.95, 0, 373.06, 0, 0, 0, 340.08, 0, 0, 0, 0, 0],
        "Março": [217215.46, 357294.73, 135800.19, 0, 118826.92, 70448.74, 0, 112451.47, 26962.66, 
                 127840.99, 117478.73, 70963.62, 0, 69247.32, 67011.48, 0, 0, 36999.25, 126234.1, 
                 0, 4609.23, 30339.91, 0, 0, 3734.67, 7962.61, 480.22, 19877.04, 0, 0, 0, 5119.5, 
                 5695.53, 0, 0, 0, 0, 7763.73, 0, 0, 0, 0, 0],
        "Abril": [176548.67, 440073.7, 174879.78, 198572.04, 146704.19, 141939.58, 64372.72, 
                 141425.58, 20789.47, 94835.54, 81804.66, 27819.99, 33382.99, 32292.02, 13206.39, 
                 0, 0, 14234.66, 18038.13, 0, 7118.25, 0, 3119.53, 7485.56, 725.33, 0, 4968.01, 
                 24012.42, 0, 58597.36, 0, 0, 0, 39635.98, 0, 0, 0, 0, 0, 0, 6629.61, 0, 0],
        "Maio": [320239.94, 1449.14, 62481.1, 86630.32, 120016.55, 112931.69, 8634.03, 87006.83, 
                6000.85, 39750.95, 85924.84, 11657.5, 353.54, 0, 120733.82, 0, 0, 9840.19, 8621.58, 
                0, 64700.4, 0, 49454.12, 11033.56, 3049.64, 0, 0, 21883.63, 0, 0, 0, 17316.94, 0, 
                10272.07, 0, 21364.19, 0, 1375.86, 0, 0, 0, 0, 0],
        "Junho": [197775.05, 127243.31, 149690.83, 62750.15, 129105.84, 37833.8, 120797.17, 109990.22, 
                 3103.19, 56266.88, 21739.48, 16254.41, 8291.89, 23637.85, 1832.05, 0, 0, 13587.88, 
                 25298.02, 0, 29230.28, 21496.22, 39647.72, 0, 72374.34, 0, 9579.44, 9126.76, 0, 
                 74647.72, 0, 0, 28565.94, 0, 0, 0, 0, 166.65, 0, 0, 1253.77, 6897.59, 0],
        "Julho": [91508.9, 268477.29, 132546.71, 161212.05, 98062.24, 171139.96, 99439.29, 98240.36, 
                 33836.26, 41396.04, 42196.93, 26648.23, 26050.36, 9500.99, 7654.83, 0, 0, 0, 
                 7678.01, 0, 5608.41, 8256.18, 11417.38, 0, 19294.5, 3234.96, 604.95, 6124.64, 0, 
                 0, 12784.69, 16134.24, 0, 0, 8867.17, 0, 0, 2412.54, 10560.56, 0, 681.71, 0, 0],
        "Agosto": [131893.62, 116974.47, 229215.09, 181284.46, 121961.7, 56701.66, 452509.77, 55077.89, 
                  49722.48, 89289.3, 85340.85, 33558.03, 0, 28250.9, 50074.07, 0, 0, 27485.57, 389.89, 
                  0, 17765.85, 62017.47, 47841.96, 0, 1460.37, 20174.52, 20040.87, 4808.89, 0, 0, 0, 
                  5161.03, 0, 10619.99, 19856.03, 0, 2644.36, 1544.91, 0, 0, 0, 4470.38, 0],
        "Setembro": [169182.86, 27978.65, 136810.57, 221176.21, 75469.6, 55118.15, 10746.38, 309484.75, 
                    133575.55, 294499.02, 92830.83, 76269.36, 44991.78, 10893.51, 50960.47, 31264.98, 
                    0, 11545.3, 24235.87, 0, 7807.6, 0, 14125.67, 0, 9969.92, 162808.59, 0, 13483.91, 
                    0, 0, 804.59, 0, 0, 0, 0, 0, 4520.84, 0, 687.62, 0, 0, 914.36, 0],
        "Outubro": [140766.81, 50978.38, 175959.47, 236524.11, 113157.2, 304973.06, 97680.39, 31009.73, 
                   101306.17, 27715.14, 53902.81, 141182.18, 243374.19, 52354.74, 8082.37, 238161.1, 
                   107500.69, 100334.09, 2657.92, 0, 46783.81, 14955.41, 11946.67, 156.4, 15773.63, 
                   0, 101708.96, 0, 29957.95, 0, 3281.86, 0, 0, 5312.93, 9033.51, 0, 3782.5, 18040.84, 
                   0, 0, 0, 0, 0],
        "Novembro": [384109.71, 141979.85, 131729.4, 286480.53, 145581.98, 63193.93, 188858.32, 168194.52, 
                    387334.3, 158005.11, 53002.72, 114645.6, 240660.02, 106052.27, 15400.59, 71263.61, 
                    183127.61, 79728.44, 9369.3, 0, 39398.05, 10429.4, 34454.89, 40862.1, 2957.05, 0, 
                    11375.27, 53184.08, 66643.47, 0, 76485.73, 4747.15, 50174.94, 0, 24450.77, 28186.79, 
                    0, 0, 12392.25, 0, 0, 0, 0],
        "Dezembro": [113625.55, 213105.05, 53372.85, 138810.45, 20160.22, 37882.98, 88719.69, 16016.67, 
                    333251.8, 31997.1, 18445.73, 31060.33, 25441.41, 25389.4, 89758.59, 110757.46, 
                    121652.14, 61676.71, 0, 291833.96, 0, 21529.58, 9781.71, 21610.53, 76509.15, 0, 
                    0, 6508.71, 6991.15, 0, 0, 0, 0, 5419.23, 0, 4245, 0, 0, 0, 14920.48, 5934.07, 
                    0, 1303.2],
        "Total": [2610780, 2004870, 1573980, 1573440, 1454970, 1392320, 1302980, 1222890, 1153950, 
                 1072710, 747740, 667374, 637025, 477393, 462258, 451447, 412280, 411171, 303695, 
                 291834, 249434, 240360, 239442, 207736, 206939, 199097, 197772, 187035, 142761, 
                 133245, 93356.9, 85043.8, 84436.5, 71633.3, 62207.5, 59154.2, 45537.7, 35463.5, 
                 24490.4, 14920.5, 14499.1, 12282.3, 1303.2]
    }
    
    df = pd.DataFrame(data)
    df_melted = df.melt(id_vars=["Agência"], var_name="Mês", value_name="Vendas")
    df_melted = df_melted[df_melted["Mês"] != "Total"]  # Remover a linha de totais
    
    # Converter meses para categoria ordenada
    df_melted['Mês'] = pd.Categorical(df_melted['Mês'], categories=ORDEM_MESES, ordered=True)
    df_melted = df_melted.sort_values('Mês')
    
    return df, df_melted

# ================================================
# LAYOUT PRINCIPAL
# ================================================

# Carregar dados
df, df_melted = load_data()

# Título principal
st.title("📊 Business Intelligence - Orinter")
st.markdown("Análise de desempenho das agências - Dados 2023")

# Métricas principais
col1, col2, col3 = st.columns(3)
col1.metric("Total Vendas", f"R$ {df['Total'].sum():,.2f}")
col2.metric("Agências Ativas", len(df))
col3.metric("Média por Agência", f"R$ {df['Total'].mean():,.2f}")

# Abas principais
tab1, tab2, tab3 = st.tabs(["Dashboard", "Ranking", "Detalhes por Agência"])

with tab1:
    st.header("Visão Geral")
    
    # Gráfico de vendas por mês (todas as agências)
    st.subheader("Vendas Mensais Consolidadas")
    vendas_mensais = df_melted.groupby("Mês")["Vendas"].sum().reset_index()
    fig_mensal = create_corporate_bar_chart(
        vendas_mensais,
        x="Mês",
        y="Vendas",
        color=None,
        title="Vendas Totais por Mês"
    )
    st.plotly_chart(fig_mensal, use_container_width=True)
    
    # Top 5 agências
    st.subheader("Top 5 Agências")
    top5 = df.sort_values("Total", ascending=False).head(5)
    fig_top5 = create_corporate_bar_chart(
        top5,
        x="Agência",
        y="Total",
        color="Agência",
        title="Top 5 Agências por Vendas Totais"
    )
    st.plotly_chart(fig_top5, use_container_width=True)
    
    # Distribuição por agência
    st.subheader("Distribuição por Agência")
    fig_pie = create_corporate_pie_chart(
        df.sort_values("Total", ascending=False).head(10),
        names="Agência",
        values="Total",
        title="Participação das Top 10 Agências no Total"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.header("🏆 Ranking de Agências")
    
    # Pódio
    df_ranking = df[["Agência", "Total"]].sort_values("Total", ascending=False)
    if len(df_ranking) >= 3:
        podium_fig = create_podium_chart(df_ranking)
        st.plotly_chart(podium_fig, use_container_width=True)
    else:
        st.warning("Número insuficiente de agências para exibir o pódio")
    
    # Ranking completo
    st.subheader("Ranking Completo")
    fig_ranking = create_corporate_bar_chart(
        df_ranking,
        x="Agência",
        y="Total",
        color="Total",
        title="Ranking de Agências por Vendas Totais",
        orientation='h'
    )
    fig_ranking.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    # Tabela de dados
    st.dataframe(
        df_ranking.style.format({"Total": "R$ {:.2f}"}),
        column_config={
            "Agência": "Agência",
            "Total": st.column_config.NumberColumn("Total Vendas", format="R$ %.2f")
        },
        use_container_width=True,
        height=400
    )

with tab3:
    st.header("🔍 Detalhamento por Agência")
    
    # Selecionar agência
    agencia_selecionada = st.selectbox(
        "Selecione uma Agência",
        options=sorted(df["Agência"].unique())
    )
    
    # Dados da agência selecionada
    dados_agencia = df_melted[df_melted["Agência"] == agencia_selecionada]
    total_agencia = df[df["Agência"] == agencia_selecionada]["Total"].values[0]
    
    st.subheader(f"Desempenho Mensal - {agencia_selecionada}")
    st.metric("Total no Período", f"R$ {total_agencia:,.2f}")
    
    # Gráfico de linhas - Evolução mensal
    fig_evolucao = px.line(
        dados_agencia,
        x="Mês",
        y="Vendas",
        title=f"Evolução Mensal - {agencia_selecionada}",
        markers=True
    )
    fig_evolucao.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="x unified",
        xaxis_title="Mês",
        yaxis_title="Vendas (R$)",
        xaxis={'categoryorder':'array', 'categoryarray':ORDEM_MESES}
    )
    fig_evolucao.update_traces(
        line=dict(color=CORPORATE_COLORS['blue'], width=3),
        marker=dict(size=8, color=CORPORATE_COLORS['orange'])
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Tabela de dados mensais
    st.subheader("Dados Mensais Detalhados")
    st.dataframe(
        dados_agencia.pivot(index="Mês", columns="Agência", values="Vendas")
        .style.format("{:,.2f}"),
        use_container_width=True
    )

# Rodapé
st.markdown("---")
st.markdown("**Relatório gerado em:** " + pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"))