import streamlit as st
import pandas as pd
import plotly.express as px
from pyecharts.charts import Sankey
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts

# ================================================
# CONFIGURAÇÕES GERAIS
# ================================================

# Configuração inicial da página
st.set_page_config(
    page_title="Business Intelligence - Redetur",
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

@st.cache_data
def load_data():
    file_path = "Power_BI_Fornecedores _Agencias_2023_25.xlsx"
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df = df.dropna(subset=["Agencias"])
    for col in ["Vendas", "Receita"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if 'Tipo' not in df.columns:
        tipos_exemplo = ['Direto', 'Online', 'Indicação', 'Corporativo', 'Promocional']
        df['Tipo'] = pd.Series(tipos_exemplo * (len(df)//len(tipos_exemplo) + 1))[:len(df)]
    if 'Mês' in df.columns:
        df['Mês'] = df['Mês'].astype(str)
    return df

def create_corporate_bar_chart(df, x, y, color, title, barmode='group', orientation='v'):
    if orientation == 'h':
        # Para gráficos horizontais, trocamos x e y
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
    # Pegar top 5 agências
    top_agencies = df_ranking.head(5).copy()
    
    # Ordenar para o pódio (1º, 3º, 2º, 4º, 5º)
    podium_order = [0, 2, 1, 3, 4]  # Índices para 1º, 3º, 2º, 4º, 5º lugares
    top_agencies = top_agencies.iloc[podium_order]
    
    # Criar posições do pódio
    podium_positions = [1, 3, 2, 4, 5]
    podium_heights = [100, 60, 80, 40, 30]  # Alturas relativas para o pódio
    
    # Cores para as posições
    podium_colors = ['gold', '#cd7f32', 'silver', '#a9a9a9', '#a9a9a9']  # Ouro, bronze, prata, cinza, cinza
    
    # Criar DataFrame para o gráfico
    podium_df = pd.DataFrame({
        'Agência': top_agencies['Agencias'],
        'Posição': podium_positions,
        'Vendas': top_agencies['Vendas'],
        'Altura': podium_heights,
        'Cor': podium_colors
    })
    
    # Criar gráfico de pódio
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
    
    # Personalizar layout
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
    
    # Adicionar valores de vendas como anotações
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
# PÁGINAS DO DASHBOARD
# ================================================

def display_ranking_cards(df_ranking):
    cols = st.columns(3)
    medal_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    num_agencias = min(5, len(df_ranking))
    
    for idx in range(num_agencias):
        row = df_ranking.iloc[idx]
        rank = idx + 1
        if rank <= 3:
            with cols[rank-1]:
                st.metric(
                    label=f"{medal_icons[rank-1]} {rank}º Lugar",
                    value=row["Agencias"],
                    delta=f"R$ {row['Vendas']:,.2f}"
                )
        else:
            with st.container():
                cols_extra = st.columns(2)
                with cols_extra[rank-4]:
                    st.metric(
                        label=f"{medal_icons[rank-1]} {rank}º Lugar",
                        value=row["Agencias"],
                        delta=f"R$ {row['Vendas']:,.2f}"
                    )

import base64
from io import BytesIO
from fpdf import FPDF
import pandas as pd
import plotly.express as px

# Classe PDF personalizada para relatórios
class PDFReport(FPDF):
    def __init__(self, orientation='L', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format)
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Relatório Business Intelligence - Redetur', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

# Função para gerar PDF de agência em A4 paisagem
def generate_agency_pdf(agency_name, df_agency):
    pdf = PDFReport()
    pdf.add_page()
    
    # Configurações básicas
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(31, 119, 180)  # Azul corporativo
    
    # Cabeçalho do relatório
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Agência: {agency_name}", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Período: {df_agency['Mês'].min()} a {df_agency['Mês'].max()}", ln=1)
    pdf.ln(10)
    
    # Métricas principais
    total_sales = df_agency['Vendas'].sum()
    total_revenue = df_agency['Receita'].sum()
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Métricas Principais:", ln=1)
    pdf.set_font("Arial", size=10)
    
    col_width = pdf.w / 2.2
    pdf.cell(col_width, 10, f"Total Vendas: R$ {total_sales:,.2f}", border=1)
    pdf.cell(col_width, 10, f"Total Receita: R$ {total_revenue:,.2f}", border=1, ln=1)
    pdf.ln(15)
    
    # Gráfico de distribuição por tipo
    sales_by_type = df_agency.groupby('Tipo')['Vendas'].sum().reset_index()
    if not sales_by_type.empty:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Distribuição por Tipo de Venda:", ln=1)
        
        fig_pie = px.pie(sales_by_type, names='Tipo', values='Vendas')
        img_buffer = BytesIO()
        fig_pie.write_image(img_buffer, format='png', width=500, height=300)
        pdf.image(img_buffer, x=10, w=190)
        pdf.ln(5)
    
    # Gráfico de vendas mensais
    if 'Mês' in df_agency.columns:
        sales_by_month = df_agency.groupby('Mês')['Vendas'].sum().reset_index()
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Vendas Mensais:", ln=1)
        
        fig_bar = px.bar(sales_by_month, x='Mês', y='Vendas', 
                        labels={'Vendas': 'Total (R$)', 'Mês': 'Mês'},
                        text_auto=True)
        
        img_buffer = BytesIO()
        fig_bar.write_image(img_buffer, format='png', width=500, height=300)
        pdf.image(img_buffer, x=10, w=190)
        pdf.ln(5)
    
    # Tabela de detalhes
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detalhamento de Vendas:", ln=1)
    
    # Preparar dados para tabela
    table_data = df_agency[['Mês', 'Tipo', 'Fornecedor', 'Vendas', 'Receita']]
    table_data = table_data.sort_values(['Mês', 'Tipo'])
    
    # Configurar tabela
    col_widths = [30, 40, 50, 30, 30]
    pdf.set_font("Arial", size=8)
    
    # Cabeçalho da tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(col_widths[0], 8, "Mês", 1, 0, 'C', 1)
    pdf.cell(col_widths[1], 8, "Tipo", 1, 0, 'C', 1)
    pdf.cell(col_widths[2], 8, "Fornecedor", 1, 0, 'C', 1)
    pdf.cell(col_widths[3], 8, "Vendas", 1, 0, 'C', 1)
    pdf.cell(col_widths[4], 8, "Receita", 1, 1, 'C', 1)
    
    # Linhas da tabela
    pdf.set_fill_color(255, 255, 255)
    for _, row in table_data.iterrows():
        pdf.cell(col_widths[0], 8, str(row['Mês']), 1)
        pdf.cell(col_widths[1], 8, str(row['Tipo']), 1)
        pdf.cell(col_widths[2], 8, str(row['Fornecedor']), 1)
        pdf.cell(col_widths[3], 8, f"R$ {row['Vendas']:,.2f}", 1)
        pdf.cell(col_widths[4], 8, f"R$ {row['Receita']:,.2f}", 1, 1)
    
    return pdf.output(dest='S').encode('latin1')

# Função para gerar PDF de fornecedor em A4 paisagem
def generate_supplier_pdf(supplier_name, df_supplier):
    pdf = PDFReport()
    pdf.add_page()
    
    # Configurações básicas
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(31, 119, 180)  # Azul corporativo
    
    # Cabeçalho do relatório
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Fornecedor: {supplier_name}", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Período: {df_supplier['Mês'].min()} a {df_supplier['Mês'].max()}", ln=1)
    pdf.ln(10)
    
    # Métricas principais
    total_sales = df_supplier['Vendas'].sum()
    total_revenue = df_supplier['Receita'].sum()
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Métricas Principais:", ln=1)
    pdf.set_font("Arial", size=10)
    
    col_width = pdf.w / 2.2
    pdf.cell(col_width, 10, f"Total Vendas: R$ {total_sales:,.2f}", border=1)
    pdf.cell(col_width, 10, f"Total Receita: R$ {total_revenue:,.2f}", border=1, ln=1)
    pdf.ln(15)
    
    # Gráfico de distribuição por agência
    sales_by_agency = df_supplier.groupby('Agencias')['Vendas'].sum().reset_index()
    if not sales_by_agency.empty:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Distribuição por Agência:", ln=1)
        
        fig_pie = px.pie(sales_by_agency, names='Agencias', values='Vendas')
        img_buffer = BytesIO()
        fig_pie.write_image(img_buffer, format='png', width=500, height=300)
        pdf.image(img_buffer, x=10, w=190)
        pdf.ln(5)
    
    # Tabela de detalhes
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detalhamento de Vendas:", ln=1)
    
    # Preparar dados para tabela
    table_data = df_supplier[['Mês', 'Agencias', 'Tipo', 'Vendas', 'Receita']]
    table_data = table_data.sort_values(['Mês', 'Agencias'])
    
    # Configurar tabela
    col_widths = [25, 35, 30, 30, 30]
    pdf.set_font("Arial", size=8)
    
    # Cabeçalho da tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(col_widths[0], 8, "Mês", 1, 0, 'C', 1)
    pdf.cell(col_widths[1], 8, "Agência", 1, 0, 'C', 1)
    pdf.cell(col_widths[2], 8, "Tipo", 1, 0, 'C', 1)
    pdf.cell(col_widths[3], 8, "Vendas", 1, 0, 'C', 1)
    pdf.cell(col_widths[4], 8, "Receita", 1, 1, 'C', 1)
    
    # Linhas da tabela
    pdf.set_fill_color(255, 255, 255)
    for _, row in table_data.iterrows():
        pdf.cell(col_widths[0], 8, str(row['Mês']), 1)
        pdf.cell(col_widths[1], 8, str(row['Agencias']), 1)
        pdf.cell(col_widths[2], 8, str(row['Tipo']), 1)
        pdf.cell(col_widths[3], 8, f"R$ {row['Vendas']:,.2f}", 1)
        pdf.cell(col_widths[4], 8, f"R$ {row['Receita']:,.2f}", 1, 1)
    
    return pdf.output(dest='S').encode('latin1')

# Modificar a função show_agency_details para incluir o botão de impressão
def show_agency_details(df_filtrado):
    st.title("📊 Detalhamento por Agência")
    
    # ... (código existente de filtros) ...
    
    for _, agency_row in df_agencies.iterrows():
        agency_name = agency_row['Agencias']
        total_sales = agency_row['Vendas']
        
        with st.expander(f"**{agency_name}** - Vendas Totais: R$ {total_sales:,.2f}", expanded=True):
            # Botões de ação
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"📄 Gerar PDF - {agency_name}", key=f"pdf_agency_{agency_name}"):
                    with st.spinner('Gerando relatório PDF...'):
                        try:
                            df_agency = df_filtrado[df_filtrado['Agencias'] == agency_name]
                            pdf_bytes = generate_agency_pdf(agency_name, df_agency)
                            
                            b64 = base64.b64encode(pdf_bytes).decode()
                            href = f'''
                            <a href="data:application/pdf;base64,{b64}" 
                               download="relatorio_{agency_name.replace(' ', '_')}.pdf"
                               style="display: inline-block; padding: 0.5em 1em; 
                                      background: #1F77B4; color: white; 
                                      border-radius: 3px; text-decoration: none;">
                               Baixar PDF (A4 Paisagem)
                            </a>
                            '''
                            st.session_state[f'pdf_agency_{agency_name}'] = href
                            st.success("PDF gerado com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao gerar PDF: {str(e)}")
            
            with col2:
                if st.button(f"🖨️ Imprimir - {agency_name}", key=f"print_agency_{agency_name}"):
                    if f'pdf_agency_{agency_name}' in st.session_state:
                        st.markdown("""
                        <script>
                        function printPDF() {
                            var pdfWindow = window.open("");
                            pdfWindow.document.write(`
                                <html>
                                    <head>
                                        <title>Imprimir Relatório</title>
                                    </head>
                                    <body>
                                        <iframe 
                                            src="data:application/pdf;base64,{st.session_state['pdf_agency_${agency_name}']}" 
                                            style="width:100%; height:100vh;" 
                                            frameborder="0">
                                        </iframe>
                                        <script>
                                            setTimeout(() => {
                                                window.frames[0].print();
                                            }, 1000);
                                        <\/script>
                                    </body>
                                </html>
                            `);
                        }
                        printPDF();
                        </script>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Gere o PDF primeiro antes de imprimir")
            
            # Mostrar link de download se o PDF foi gerado
            if f'pdf_agency_{agency_name}' in st.session_state:
                st.markdown(st.session_state[f'pdf_agency_{agency_name}'], unsafe_allow_html=True)
            
            # ... (restante do código existente) ...

# Modificar a função show_supplier_details para incluir o botão de impressão
def show_supplier_details(df_filtrado):
    st.title("🏭 Detalhamento por Fornecedor")
    
    # ... (código existente) ...
    
    for _, supplier_row in df_suppliers.iterrows():
        supplier_name = supplier_row["Fornecedor"]
        total_sales = supplier_row["Vendas"]
        
        with st.expander(f"**{supplier_name}** - Vendas Totais: R$ {total_sales:,.2f}", expanded=False):
            # Botões de ação
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"📄 Gerar PDF - {supplier_name}", key=f"pdf_supplier_{supplier_name}"):
                    with st.spinner('Gerando relatório PDF...'):
                        try:
                            df_supplier = df_filtrado[df_filtrado['Fornecedor'] == supplier_name]
                            pdf_bytes = generate_supplier_pdf(supplier_name, df_supplier)
                            
                            b64 = base64.b64encode(pdf_bytes).decode()
                            href = f'''
                            <a href="data:application/pdf;base64,{b64}" 
                               download="relatorio_{supplier_name.replace(' ', '_')}.pdf"
                               style="display: inline-block; padding: 0.5em 1em; 
                                      background: #1F77B4; color: white; 
                                      border-radius: 3px; text-decoration: none;">
                               Baixar PDF (A4 Paisagem)
                            </a>
                            '''
                            st.session_state[f'pdf_supplier_{supplier_name}'] = href
                            st.success("PDF gerado com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao gerar PDF: {str(e)}")
            
            with col2:
                if st.button(f"🖨️ Imprimir - {supplier_name}", key=f"print_supplier_{supplier_name}"):
                    if f'pdf_supplier_{supplier_name}' in st.session_state:
                        st.markdown("""
                        <script>
                        function printPDF() {
                            var pdfWindow = window.open("");
                            pdfWindow.document.write(`
                                <html>
                                    <head>
                                        <title>Imprimir Relatório</title>
                                    </head>
                                    <body>
                                        <iframe 
                                            src="data:application/pdf;base64,{st.session_state['pdf_supplier_${supplier_name}']}" 
                                            style="width:100%; height:100vh;" 
                                            frameborder="0">
                                        </iframe>
                                        <script>
                                            setTimeout(() => {
                                                window.frames[0].print();
                                            }, 1000);
                                        <\/script>
                                    </body>
                                </html>
                            `);
                        }
                        printPDF();
                        </script>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Gere o PDF primeiro antes de imprimir")
            
            # Mostrar link de download se o PDF foi gerado
            if f'pdf_supplier_{supplier_name}' in st.session_state:
                st.markdown(st.session_state[f'pdf_supplier_{supplier_name}'], unsafe_allow_html=True)
            
            # ... (restante do código existente) ...


def show_agency_details(df_filtrado):
    st.title("📊 Detalhamento por Agência")
    
    # Adicionar filtros adicionais
    with st.container():
        st.subheader("Filtros Adicionais")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            consolidadora = st.checkbox("Consolidadora", value=True)
        with col2:
            operadora = st.checkbox("Operadora", value=True)
        with col3:
            seguradora = st.checkbox("Seguradora", value=True)
    
    # Aplicar filtros adicionais
    tipos_selecionados = []
    if consolidadora:
        tipos_selecionados.append("Consolidadora")
    if operadora:
        tipos_selecionados.append("Operadora")
    if seguradora:
        tipos_selecionados.append("Seguradora")
    
    df_filtrado_tipos = df_filtrado[df_filtrado["Tipo"].isin(tipos_selecionados)] if tipos_selecionados else df_filtrado
    
    df_agencies = df_filtrado_tipos.groupby("Agencias").agg({
        "Vendas": "sum",
        "Receita": "sum"
    }).reset_index().sort_values("Vendas", ascending=False)
    
    for _, agency_row in df_agencies.iterrows():
        agency_name = agency_row["Agencias"]
        total_sales = agency_row["Vendas"]
        
        with st.expander(f"**{agency_name}** - Vendas Totais: R$ {total_sales:,.2f}", expanded=True):
            # Primeira linha - Métricas e gráfico de pizza
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"### Total Vendas")
                st.metric("", f"R$ {total_sales:,.2f}")
                
                st.markdown(f"### Total Receita")
                st.metric("", f"R$ {agency_row['Receita']:,.2f}")
                
                # Mostrar filtros aplicados
                st.markdown("---")
                st.markdown("**Filtros Ativos:**")
                st.markdown(f"- Consolidadora: {'✅' if consolidadora else '❌'}")
                st.markdown(f"- Operadora: {'✅' if operadora else '❌'}")
                st.markdown(f"- Seguradora: {'✅' if seguradora else '❌'}")
            
            with col2:
                df_agency_type = df_filtrado_tipos[df_filtrado_tipos["Agencias"] == agency_name]
                sales_by_type = df_agency_type.groupby("Tipo")["Vendas"].sum().reset_index()
                
                if not sales_by_type.empty:
                    fig_pie = create_corporate_pie_chart(
                        sales_by_type,
                        names="Tipo",
                        values="Vendas",
                        title=f"Distribuição por Tipo - {agency_name}"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, 
                                  config={'displayModeBar': False})
                else:
                    st.warning("Nenhum dado disponível por tipo para esta agência")
            
            # Segunda linha - Gráfico de vendas por mês (ocupando toda a largura)
            st.markdown("---")
            st.subheader(f"Vendas Mensais - {agency_name}")
            
            df_agency_month = df_filtrado_tipos[df_filtrado_tipos["Agencias"] == agency_name]
            if not df_agency_month.empty and 'Mês' in df_agency_month.columns:
                sales_by_month = df_agency_month.groupby("Mês")["Vendas"].sum().reset_index()
                
                # Ordenar os meses corretamente
                meses_ordenados = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                sales_by_month['Mês'] = pd.Categorical(sales_by_month['Mês'], 
                                                      categories=meses_ordenados,
                                                      ordered=True)
                sales_by_month = sales_by_month.sort_values('Mês')
                
                # Criar gráfico de barras
                fig_month = px.bar(
                    sales_by_month,
                    x="Mês",
                    y="Vendas",
                    labels={"Vendas": "Total (R$)", "Mês": "Mês"},
                    text_auto=True,
                    color_discrete_sequence=[CORPORATE_COLORS['blue']]
                )
                
                fig_month.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color="#333"),
                    margin=dict(l=20, r=20, t=30, b=20),
                    xaxis_tickangle=-45,
                    height=400,
                    showlegend=False
                )
                
                fig_month.update_traces(
                    texttemplate='R$ %{y:,.2f}',
                    textposition='outside',
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5
                )
                
                st.plotly_chart(fig_month, use_container_width=True, 
                              config={'displayModeBar': False})
            else:
                st.warning("Nenhum dado disponível por mês para esta agência")

def show_supplier_details(df_filtrado):
    st.title("🏭 Detalhamento por Fornecedor")
    
    st.header("📈 Distribuição por Tipo de Venda")
    fig_tipo = create_corporate_bar_chart(
        df_filtrado.groupby("Tipo")["Vendas"].sum().reset_index().sort_values("Vendas", ascending=False),
        x="Tipo",
        y="Vendas",
        color="Tipo",
        title="Vendas por Tipo"
    )
    st.plotly_chart(fig_tipo, use_container_width=True)
    
    st.header("🔍 Detalhes por Fornecedor")
    df_suppliers = df_filtrado.groupby("Fornecedor").agg({
        "Vendas": "sum",
        "Receita": "sum"
    }).reset_index().sort_values("Vendas", ascending=False)
    
    for _, supplier_row in df_suppliers.iterrows():
        supplier_name = supplier_row["Fornecedor"]
        total_sales = supplier_row["Vendas"]
        
        with st.expander(f"**{supplier_name}** - Vendas Totais: R$ {total_sales:,.2f}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Vendas", f"R$ {total_sales:,.2f}")
                st.metric("Total Receita", f"R$ {supplier_row['Receita']:,.2f}")
            
            with col2:
                df_supplier_agency = df_filtrado[df_filtrado["Fornecedor"] == supplier_name]
                sales_by_agency = df_supplier_agency.groupby("Agencias")["Vendas"].sum().reset_index()
                
                if not sales_by_agency.empty:
                    fig = create_corporate_pie_chart(
                        sales_by_agency,
                        names="Agencias",
                        values="Vendas",
                        title=f"Distribuição por Agência - {supplier_name}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Nenhum dado disponível por agência para este fornecedor")
            
            st.subheader(f"🔹 Vendas por Agência - {supplier_name}")
            cols = st.columns(3)
            agency_sales = df_supplier_agency.sort_values("Vendas", ascending=False)
            
            for idx, agency_row in agency_sales.iterrows():
                with cols[idx % 3]:
                    st.metric(
                        label=agency_row["Agencias"],
                        value=f"R$ {agency_row['Vendas']:,.2f}"
                    )

def show_comparison(df):
    st.title("📊 Comparativo entre Agências")
    
    with st.expander("🔍 Filtros de Comparação", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agencias_disponiveis = sorted(df["Agencias"].unique())
            agencias_sel = st.multiselect(
                "Selecione as Agências para Comparar",
                options=agencias_disponiveis,
                default=agencias_disponiveis[:2] if len(agencias_disponiveis) >= 2 else agencias_disponiveis
            )
        
        with col2:
            tipos_disponiveis = ["Todos"] + sorted(df["Tipo"].unique())
            tipo_sel = st.selectbox("Tipo de Venda", options=tipos_disponiveis)
        
        with col3:
            anos_disponiveis = sorted(df["Ano"].unique())
            ano_sel = st.selectbox("Ano", options=["Todos"] + anos_disponiveis)
            
            if ano_sel != "Todos":
                meses_disponiveis = df[df["Ano"] == ano_sel]["Mês"].unique()
                meses_ordenados = sorted(meses_disponiveis, key=lambda x: ORDEM_MESES.index(x) if x in ORDEM_MESES else len(ORDEM_MESES))
                mes_sel = st.selectbox("Mês", options=["Todos"] + meses_ordenados)
            else:
                mes_sel = "Todos"
    
    df_filtrado = df.copy()
    
    if agencias_sel:
        df_filtrado = df_filtrado[df_filtrado["Agencias"].isin(agencias_sel)]
    
    if tipo_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_sel]
    
    if ano_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Ano"] == ano_sel]
        
        if mes_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Mês"] == mes_sel]
    
    if df_filtrado.empty or len(agencias_sel) < 2:
        st.warning("Selecione pelo menos duas agências para comparação")
        return
    
    if mes_sel == "Todos" and ano_sel == "Todos":
        df_comparacao = df_filtrado.groupby(["Agencias", "Ano"])["Vendas"].sum().reset_index()
        fig = create_corporate_bar_chart(
            df_comparacao,
            x="Ano",
            y="Vendas",
            color="Agencias",
            title=f"Comparativo Anual - Tipo: {tipo_sel}"
        )
    elif mes_sel == "Todos":
        df_comparacao = df_filtrado.groupby(["Agencias", "Mês"])["Vendas"].sum().reset_index()
        df_comparacao['Mês'] = pd.Categorical(df_comparacao['Mês'], categories=ORDEM_MESES, ordered=True)
        df_comparacao = df_comparacao.sort_values('Mês')
        
        fig = create_corporate_bar_chart(
            df_comparacao,
            x="Mês",
            y="Vendas",
            color="Agencias",
            title=f"Comparativo Mensal {ano_sel} - Tipo: {tipo_sel}"
        )
        fig.update_xaxes(categoryorder='array', categoryarray=ORDEM_MESES)
    else:
        df_comparacao = df_filtrado.groupby("Agencias")["Vendas"].sum().reset_index()
        fig = create_corporate_bar_chart(
            df_comparacao,
            x="Agencias",
            y="Vendas",
            color="Agencias",
            title=f"Comparativo - {mes_sel}/{ano_sel} - Tipo: {tipo_sel}"
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Dados Detalhados")
    
    if mes_sel == "Todos" and ano_sel == "Todos":
        pivot_table = df_comparacao.pivot(index="Agencias", columns="Ano", values="Vendas")
    elif mes_sel == "Todos":
        pivot_table = df_comparacao.pivot(index="Agencias", columns="Mês", values="Vendas")
    else:
        pivot_table = df_comparacao.set_index("Agencias")
    
    st.dataframe(
        pivot_table.style.format("{:,.2f}"),
        height=400
    )

# ================================================
# LAYOUT PRINCIPAL
# ================================================

# Carregar dados
df = load_data()

# Calcular totais por tipo
tipos_desejados = ["Consolidadora", "Operadora", "Seguradora", "Financeira"]
df_tipo = df[df["Tipo"].isin(tipos_desejados)]
totais_tipo = df_tipo.groupby("Tipo")[["Vendas", "Receita"]].sum().reset_index()

# Sidebar
with st.sidebar:
    st.image("logo original redetur.jpg", width=150)
    
    page = st.radio(
        "Menu",
        options=["Dashboard", "RANKING", "Detalhamento Agências", "Detalhamento Fornecedor", "Comparativo"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("## Filtros Principais")
    agencias = df["Agencias"].dropna().unique()
    agencia_sel = st.selectbox("Agência", options=["Todas"] + sorted(list(agencias)), index=0)
    anos = df["Ano"].dropna().unique()
    ano_sel = st.selectbox("Ano", options=["Todos"] + sorted(list(anos), reverse=True), index=0)
    if ano_sel != "Todos":
        meses_disponiveis = df[df["Ano"] == ano_sel]["Mês"].dropna().unique()
    else:
        meses_disponiveis = df["Mês"].dropna().unique()
    meses_ordenados = sorted(meses_disponiveis, key=lambda x: ORDEM_MESES.index(x) if x in ORDEM_MESES else len(ORDEM_MESES))
    mês_sel = st.selectbox("Mês", options=["Todos"] + meses_ordenados, index=0)
    fornecedores = df["Fornecedor"].dropna().unique()
    fornecedor_sel = st.selectbox("Fornecedor", options=["Todos"] + sorted(list(fornecedores)), index=0)

    tipos_unicos = df["Tipo"].dropna().unique()
    tipo_sel = st.selectbox("Tipo", options=["Todos"] + sorted(list(tipos_unicos)), index=0)

    st.markdown("---")
    st.markdown("## Totais por Tipo")
    for _, row in totais_tipo.iterrows():
        st.metric(label=row["Tipo"], value=f"R$ {row['Vendas']:,.2f}")

    st.markdown("---")
    st.markdown("### Informações")
    st.markdown(f"**Total de Registros:** {len(df)}")
    st.markdown(f"**Filtros aplicados:**")
    st.markdown(f"- Agência: {agencia_sel}")
    st.markdown(f"- Ano: {ano_sel}")
    st.markdown(f"- Mês: {mês_sel}")
    st.markdown(f"- Fornecedor: {fornecedor_sel}")
    st.markdown(f"- Tipo: {tipo_sel}")

# Aplicação dos filtros
df_filtrado = df.copy()
if agencia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Agencias"] == agencia_sel]
if ano_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Ano"] == ano_sel]
if mês_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mês"] == mês_sel]
if fornecedor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Fornecedor"] == fornecedor_sel]
if tipo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_sel]

# Navegação entre páginas
if page == "RANKING":
    st.title("🏆 Ranking de Agências")
    st.markdown("Top agências por volume de vendas (ordem decrescente)")
    
    df_ranking_filtrado = df_filtrado.groupby("Agencias")["Vendas"].sum().reset_index().sort_values("Vendas", ascending=False)
    
    st.subheader("Top 5 Agências")
    display_ranking_cards(df_ranking_filtrado)
    
    st.markdown("---")
    
    # Adicionando o gráfico de pódio
    st.subheader("Pódio das Agências")
    if len(df_ranking_filtrado) >= 3:
        podium_fig = create_podium_chart(df_ranking_filtrado)
        st.plotly_chart(podium_fig, use_container_width=True)
    else:
        st.warning("É necessário ter pelo menos 3 agências para exibir o pódio")
    
    st.markdown("---")
    
    st.subheader("Ranking Completo")
    
    # Gráfico de barras horizontais para o ranking completo
    fig = create_corporate_bar_chart(
        df_ranking_filtrado.head(20),
        x="Agencias",
        y="Vendas",
        color="Vendas",
        title="Ranking de Agências (Barras Horizontais)",
        orientation='h'
    )
    
    # Personalizar o gráfico horizontal
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title="Total de Vendas (R$)",
        yaxis_title="Agências",
        height=600  # Ajustar altura para melhor visualização
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados abaixo do gráfico
    st.dataframe(
        df_ranking_filtrado.style.format({"Vendas": "R$ {:.2f}"}),
        column_config={
            "Agencias": "Agência",
            "Vendas": st.column_config.NumberColumn("Total Vendas", format="R$ %.2f")
        },
        use_container_width=True,
        height=400
    )
    
    st.download_button(
        label="📥 Exportar Ranking",
        data=df_ranking_filtrado.to_csv(index=False).encode('utf-8'),
        file_name="ranking_agencias.csv",
        mime="text/csv"
    )

elif page == "Detalhamento Agências":
    show_agency_details(df_filtrado)

elif page == "Detalhamento Fornecedor":
    show_supplier_details(df_filtrado)

elif page == "Comparativo":
    show_comparison(df_filtrado)

else:
    st.title("📊 Business Intelligence - Redetur")
    st.markdown("Análise comparativa de desempenho por fornecedor e agência")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Vendas", f"R$ {df_filtrado['Vendas'].sum():,.2f}")
    col2.metric("Total Receita", f"R$ {df_filtrado['Receita'].sum():,.2f}")
    col3.metric("Fornecedores Ativos", df_filtrado['Fornecedor'].nunique())

    tab1, tab2 = st.tabs(["Visualizações", "Dados"])

    with tab1:
        st.subheader("Vendas por Tipo")
        if mês_sel == "Todos":
            df_filtrado['Mês'] = pd.Categorical(df_filtrado['Mês'], categories=ORDEM_MESES, ordered=True)
            df_filtrado = df_filtrado.sort_values('Mês')
        
        fig = create_corporate_bar_chart(
            df_filtrado,
            x="Mês" if mês_sel == "Todos" else "Agencias",
            y="Vendas",
            color="Tipo",
            title=f"Distribuição por Tipo ({'Todos meses' if mês_sel == 'Todos' else mês_sel})"
        )
        if mês_sel == "Todos":
            fig.update_xaxes(categoryorder='array', categoryarray=ORDEM_MESES)
        st.plotly_chart(fig, use_container_width=True)

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

        st.subheader("Fluxo de Vendas")
        def create_sankey_diagram(df):
            nodes = []
            links = []
            agencias = df["Agencias"].unique().tolist()
            fornecedores = df["Fornecedor"].unique().tolist()
            tipos = df["Tipo"].unique().tolist()
            all_nodes = agencias + fornecedores + tipos
            nodes = [{"name": node} for node in all_nodes]
            node_index = {node: idx for idx, node in enumerate(all_nodes)}
            ag_forn = df.groupby(["Agencias", "Fornecedor"])["Vendas"].sum().reset_index()
            links.extend([
                {
                    "source": node_index[row["Agencias"]],
                    "target": node_index[row["Fornecedor"]],
                    "value": float(row["Vendas"])
                }
                for _, row in ag_forn.iterrows()
            ])
            forn_tipo = df.groupby(["Fornecedor", "Tipo"])["Vendas"].sum().reset_index()
            links.extend([
                {
                    "source": node_index[row["Fornecedor"]],
                    "target": node_index[row["Tipo"]],
                    "value": float(row["Vendas"])
                }
                for _, row in forn_tipo.iterrows()
            ])
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
                    title_opts=opts.TitleOpts(pos_top="5%", pos_left="center"),
                    tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove"),
                )
            )
            return sankey

        if len(df_filtrado) > 0:
            sankey_chart = create_sankey_diagram(df_filtrado)
            st_pyecharts(sankey_chart)
        else:
            st.warning("Não há dados suficientes para exibir o gráfico Sankey com os filtros atuais.")

        st.subheader("Vendas Mensais (Histórico)")
        df_historico = df_filtrado.groupby(["Ano", "Mês"])["Vendas"].sum().reset_index()
        df_historico['Mês'] = pd.Categorical(df_historico['Mês'], categories=ORDEM_MESES, ordered=True)
        df_historico = df_historico.sort_values(['Ano', 'Mês'])
        fig = create_corporate_bar_chart(
            df_historico,
            x="Mês",
            y="Vendas",
            color="Ano",
            title="Vendas Mensais (Histórico)"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Distribuição Percentual")
        col1, col2 = st.columns(2)
        with col1:
            if agencia_sel == "Todas":
                fig = create_corporate_pie_chart(
                    df_filtrado.groupby("Agencias")["Vendas"].sum().reset_index(),
                    names="Agencias",
                    values="Vendas",
                    title="Por Agência"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Mostrando dados apenas para a agência selecionada")
        with col2:
            if fornecedor_sel == "Todos":
                fig = create_corporate_pie_chart(
                    df_filtrado.groupby("Fornecedor")["Vendas"].sum().reset_index(),
                    names="Fornecedor",
                    values="Vendas",
                    title="Por Fornecedor"
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
        st.download_button(
            label="📥 Exportar dados filtrados",
            data=df_filtrado.to_csv(index=False).encode('utf-8'),
            file_name=f"dados_redetur_filtrados.csv",
            mime="text/csv",
            key="download_button"
        )