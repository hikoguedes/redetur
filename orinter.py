import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import io
import base64  # Added this import for base64 conversion

# Configuração da página
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Redetur",
    page_icon="📊"
)

# Paleta de cores profissional
COLOR_PALETTE = {
    "primary": "#2c3e50",
    "secondary": "#34495e",
    "accent": "#e74c3c",
    "background": "#f5f7fa",
    "text": "#333333",
    "success": "#27ae60",
    "warning": "#f39c12"
}

# Função auxiliar para converter imagem para base64 - MOVED TO TOP
def logo_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@st.cache_data
def load_data():
    # Carregar todas as abas do Excel
    dfs = pd.read_excel("orinnter.xlsx", sheet_name=None)
    
    # Criando dados de exemplo baseados na estrutura do Excel
    agencias = [
        "Travel Mix Sta Maria", "Free Viagens", "Sierra Tur", "Tri Viagens",
        "ZZZ Tour", "Guia Sul Turismo", "Positivo", "Universo do Turismo",
        "Vosar Agência de Viagens", "Viaggiolar CB Viagens", "Matte Viagens"
    ]
    
    vendas = [
        2113046.28, 1649781.82, 1388880.07, 1291238.26,
        1289226.23, 1148149.34, 1058681.13, 1052405.73,
        882704.24, 676291.66, 521668.21
    ]
    
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    vendas_mensais = [
        1699207.34, 1967122.52, 1740358.10, 1972212.16,
        1282723.28, 1398194.42, 1421570.38, 1928136.38,
        1992156.94, 2488355.02, 2100000.00, 1800000.00
    ]
    
    # Criando DataFrames
    df_vendas = pd.DataFrame({
        "Agência": agencias,
        "Vendas (R$)": vendas,
        "Participação (%)": [round(v/sum(vendas)*100, 2) for v in vendas]
    })
    
    df_mensal = pd.DataFrame({
        "Mês": meses,
        "Vendas (R$)": vendas_mensais,
        "Meta": [v * 1.1 for v in vendas_mensais]  # Adicionando metas (10% acima)
    })
    
    return df_vendas, df_mensal

# Carregar dados
df_vendas, df_mensal = load_data()

# Logo da Redetur
try:
    logo = Image.open("logo original redetur.jpg")
except:
    # Criar placeholder profissional
    logo = Image.new('RGB', (200, 60), color=COLOR_PALETTE["primary"])
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(logo)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default(24)
    draw.text((10, 15), "REDETUR", font=font, fill='white')

# Cabeçalho
st.markdown(f"""
    <div style="background-color:{COLOR_PALETTE['primary']};padding:20px;border-radius:10px;margin-bottom:30px">
        <div style="display:flex;align-items:center;justify-content:space-between">
            <img src="data:image/png;base64,{logo_to_base64(logo)}" width="200">
            <h1 style="color:white;text-align:center;margin:0">DASHBOARD DE VENDAS</h1>
            <div style="background-color:{COLOR_PALETTE['accent']};padding:10px 20px;border-radius:5px">
                <h3 style="color:white;margin:0">TOTAL</h3>
                <h2 style="color:white;margin:0">R$ {df_vendas["Vendas (R$)"].sum():,.2f}</h2>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Rest of your code remains the same...s

# Função auxiliar para converter imagem para base64
def logo_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Seção de filtros
st.markdown(f"""
    <div style="background-color:{COLOR_PALETTE['background']};padding:20px;border-radius:10px;margin-bottom:30px">
        <h2 style="color:{COLOR_PALETTE['primary']};margin-top:0">Filtros por Tipo de Fornecedor</h2>
    </div>
""", unsafe_allow_html=True)

# Tabs de filtros
tab1, tab2, tab3 = st.tabs(["🗃️ Consolidadores", "🛡️ Seguradoras", "✈️ Operadores"])

with tab1:
    cols = st.columns(2)
    with cols[0]:
        st.button("Skyteam", key="skyteam", 
                 help="Filtrar por operadora Skyteam")
    with cols[1]:
        st.button("Sakura", key="sakura",
                 help="Filtrar por operadora Sakura")

with tab2:
    cols = st.columns(2)
    with cols[0]:
        st.button("Affinity", key="affinity",
                 help="Filtrar por seguradora Affinity")
    with cols[1]:
        st.button("GTA - Global Travel Assist", key="gta",
                 help="Filtrar por seguradora GTA")

with tab3:
    cols = st.columns(4)
    buttons = [
        ("Orinter", "Operadora Orinter"),
        ("Agastur", "Operadora Agastur"),
        ("Sachaktour", "Operadora Sachaktour"),
        ("Personal", "Operadora Personal"),
        ("Cia Maritima", "Operadora Cia Maritima"),
        ("Bom Voiage", "Operadora Bom Voiage"),
        ("Utravel", "Operadora Utravel"),
        ("Mobility", "Operadora Mobility")
    ]
    
    for i, (btn, tooltip) in enumerate(buttons):
        with cols[i%4]:
            st.button(btn, key=btn.lower(), help=tooltip)

# Seção de análise de vendas
st.markdown(f"""
    <div style="background-color:{COLOR_PALETTE['background']};padding:20px;border-radius:10px;margin:30px 0">
        <h2 style="color:{COLOR_PALETTE['primary']};margin-top:0">📈 Análise de Vendas</h2>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([6, 4])

with col1:
    # Gráfico de barras - Vendas por Agência
    df_sorted = df_vendas.sort_values("Vendas (R$)")
    fig1 = px.bar(
        df_sorted,
        x="Vendas (R$)",
        y="Agência",
        orientation='h',
        title="<b>Vendas por Agência</b>",
        color="Vendas (R$)",
        color_continuous_scale=[COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"]],
        text="Vendas (R$)",
        labels={"Vendas (R$)": "Valor (R$)"}
    )
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder':'total ascending'},
        title_font=dict(size=20, color=COLOR_PALETTE["primary"]),
        font=dict(color=COLOR_PALETTE["text"])
    )
    fig1.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Gráfico de rosca - Percentual de vendas
    fig2 = px.pie(
        df_vendas,
        values="Participação (%)",
        names="Agência",
        title="<b>Participação de Mercado</b>",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color=COLOR_PALETTE["primary"]),
        font=dict(color=COLOR_PALETTE["text"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    fig2.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color=COLOR_PALETTE["background"], width=2))
    )
    st.plotly_chart(fig2, use_container_width=True)

# Seção de vendas mensais
st.markdown(f"""
    <div style="background-color:{COLOR_PALETTE['background']};padding:20px;border-radius:10px;margin:30px 0">
        <h2 style="color:{COLOR_PALETTE['primary']};margin-top:0">📅 Vendas Mensais</h2>
    </div>
""", unsafe_allow_html=True)

# Gráfico de linhas e barras combinado
fig3 = px.bar(
    df_mensal,
    x="Mês",
    y="Vendas (R$)",
    title="<b>Vendas Mensais vs Meta</b>",
    color_discrete_sequence=[COLOR_PALETTE["accent"]],
    labels={"Vendas (R$)": "Valor (R$)"}
)

# Adicionando linha de meta
fig3.add_scatter(
    x=df_mensal["Mês"],
    y=df_mensal["Meta"],
    mode='lines+markers',
    name='Meta',
    line=dict(color=COLOR_PALETTE["success"], width=3),
    marker=dict(size=8)
)

fig3.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    title_font=dict(size=20, color=COLOR_PALETTE["primary"]),
    font=dict(color=COLOR_PALETTE["text"]),
    xaxis=dict(tickangle=-45),
    barmode='group',
    hovermode="x unified"
)

# Adicionando anotações de desempenho
for i, row in df_mensal.iterrows():
    if row["Vendas (R$)"] >= row["Meta"]:
        fig3.add_annotation(
            x=row["Mês"],
            y=row["Vendas (R$)"],
            text="✅",
            showarrow=False,
            yshift=10
        )
    else:
        fig3.add_annotation(
            x=row["Mês"],
            y=row["Vendas (R$)"],
            text="⚠️",
            showarrow=False,
            yshift=10
        )

st.plotly_chart(fig3, use_container_width=True)

# Adicionando KPIs adicionais
st.markdown("---")
st.markdown(f"""
    <h2 style="color:{COLOR_PALETTE['primary']}">📊 KPIs Adicionais</h2>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_sale = df_vendas["Vendas (R$)"].mean()
    st.metric("Média por Agência", f"R$ {avg_sale:,.2f}")

with col2:
    max_sale = df_vendas["Vendas (R$)"].max()
    top_agency = df_vendas.loc[df_vendas["Vendas (R$)"] == max_sale, "Agência"].values[0]
    st.metric("Maior Vendedor", f"{top_agency}", f"R$ {max_sale:,.2f}")

with col3:
    growth = (df_mensal["Vendas (R$)"].iloc[-1] - df_mensal["Vendas (R$)"].iloc[-2]) / df_mensal["Vendas (R$)"].iloc[-2] * 100
    st.metric("Crescimento Mensal", f"{growth:.1f}%")

with col4:
    target_achievement = (df_mensal["Vendas (R$)"].sum() / df_mensal["Meta"].sum()) * 100
    st.metric("Atingimento de Meta", f"{target_achievement:.1f}%")

# Estilo CSS profissional
st.markdown(f"""
<style>
    /* Estilos gerais */
    .stApp {{
        background-color: {COLOR_PALETTE["background"]};
    }}
    
    /* Botões */
    .stButton>button {{
        width: 100%;
        border-radius: 8px;
        border: 2px solid {COLOR_PALETTE["primary"]};
        color: {COLOR_PALETTE["primary"]};
        background-color: white;
        padding: 12px;
        margin: 5px 0;
        transition: all 0.3s;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: {COLOR_PALETTE["primary"]};
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 5px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        padding: 0 25px;
        background-color: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid {COLOR_PALETTE["secondary"]};
        font-weight: bold;
        color: {COLOR_PALETTE["text"]};
        transition: all 0.3s;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_PALETTE["primary"]};
        color: white;
    }}
    
    /* Métricas */
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    [data-testid="stMetricLabel"] {{
        color: {COLOR_PALETTE["secondary"]};
        font-size: 1rem;
    }}
    [data-testid="stMetricValue"] {{
        color: {COLOR_PALETTE["primary"]};
        font-size: 1.5rem;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 1rem;
    }}
    
    /* Divisores */
    .stMarkdown hr {{
        margin: 30px 0;
        border: 1px solid {COLOR_PALETTE["secondary"]}20;
    }}
</style>
""", unsafe_allow_html=True)