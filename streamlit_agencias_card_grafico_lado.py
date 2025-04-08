
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Carregar os dados
@st.cache_data
def load_data():
    file_path = "Relatório de vendas agências x Fornecedores.xlsx"
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    all_data = []
    for sheet in sheet_names:
        df = excel_file.parse(sheet)
        df['Fornecedor'] = sheet
        all_data.append(df)
    df_combined = pd.concat(all_data, ignore_index=True)
    df_combined = df_combined[~df_combined.iloc[:, 0].astype(str).str.contains("Agência:|nan", case=False, na=True)]
    df_combined.columns = ['Agencia', 'Janeiro', 'Fevereiro', 'Março', 'Fornecedor']
    for mes in ['Janeiro', 'Fevereiro', 'Março']:
        df_combined[mes] = pd.to_numeric(df_combined[mes], errors='coerce')
    return df_combined

df = load_data()

# Sidebar para seleção de agência
agencias = df['Agencia'].dropna().unique()
agencia_selecionada = st.sidebar.selectbox("Selecione uma agência", agencias)

# Filtrar os dados da agência selecionada
dados_agencia = df[df['Agencia'] == agencia_selecionada]

st.title(f"Relatório de Vendas - {agencia_selecionada}")

# Estilo dos cards com cores alternadas
st.markdown(
    '''
    <style>
    .card {
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        background-color: #f9f9f9;
        margin-bottom: 20px;
    }
    .card:nth-child(even) {
        background-color: #e8f0fe;
    }
    .card:nth-child(odd) {
        background-color: #fef3e8;
    }
    .card h4 {
        margin: 0 0 10px 0;
        font-size: 1.1rem;
        color: #333;
    }
    .card p {
        margin: 5px 0;
        font-size: 1rem;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# Mostrar cada card com gráfico ao lado
for idx, (_, row) in enumerate(dados_agencia.iterrows()):
    fornecedor = row["Fornecedor"]
    janeiro = row["Janeiro"] or 0
    fevereiro = row["Fevereiro"] or 0
    marco = row["Março"] or 0

    # Tendência
    valores = [v for v in [janeiro, fevereiro, marco] if pd.notna(v)]
    tendencia = ""
    if len(valores) >= 2:
        if valores[-1] > valores[0]:
            tendencia = "⬆️"
        elif valores[-1] < valores[0]:
            tendencia = "⬇️"
        else:
            tendencia = "➡️"

    # Dados para gráfico
    df_plot = pd.DataFrame({
        'Mês': ['Janeiro', 'Fevereiro', 'Março'],
        'Valor': [janeiro, fevereiro, marco]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_plot["Mês"], y=df_plot["Valor"], name="Vendas", text=df_plot["Valor"],
                         textposition='auto'))
    fig.add_trace(go.Scatter(x=df_plot["Mês"], y=df_plot["Valor"], mode='lines+markers', name="Tendência",
                             line=dict(dash='dot', color='black')))
    fig.update_layout(title=f"{fornecedor}", yaxis_title="Valor", xaxis_title="Mês", height=300)

    # Layout em duas colunas: card e gráfico
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'''
        <div class="card">
            <h4>{fornecedor} {tendencia}</h4>
            <p><strong>Janeiro:</strong> R$ {janeiro:,.2f}</p>
            <p><strong>Fevereiro:</strong> R$ {fevereiro:,.2f}</p>
            <p><strong>Março:</strong> R$ {marco:,.2f}</p>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.plotly_chart(fig, use_container_width=True)
