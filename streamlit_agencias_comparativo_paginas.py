
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import unicodedata
import base64
import uuid

def normalize_col(col_name):
    col_name = str(col_name).strip().lower()
    col_name = ''.join(c for c in unicodedata.normalize('NFD', col_name) if unicodedata.category(c) != 'Mn')
    return col_name

@st.cache_data
def load_data():
    file_path = "Relatório de vendas agências x Fornecedores.xlsx"
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    all_data = []

    for sheet in sheet_names:
        df = excel_file.parse(sheet)
        header_row = df[df.iloc[:, 0].astype(str).str.contains("Agência", case=False, na=False)].index
        if not header_row.empty:
            header_index = header_row[0]
            df.columns = df.iloc[header_index]
            df = df[(header_index + 1):].copy()
            df['Fornecedor'] = sheet
            all_data.append(df)

    df_combined = pd.concat(all_data, ignore_index=True)
    df_combined.columns = [str(col).strip() for col in df_combined.columns]

    agencia_col = None
    for col in df_combined.columns:
        if "agencia" in normalize_col(col):
            agencia_col = col
            break
    if not agencia_col:
        st.error("Coluna com nome semelhante a 'Agência' não encontrada.")
        st.stop()

    meses = [col for col in df_combined.columns if any(mes in normalize_col(col) for mes in ['janeiro','fevereiro','marco','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'])]
    df_final = df_combined[[agencia_col] + meses + ['Fornecedor']]

    for mes in meses:
        df_final[mes] = pd.to_numeric(df_final[mes], errors='coerce')

    return df_final, agencia_col, meses

# ============ APP MULTIPÁGINA ============

st.set_page_config(layout="wide")
page = st.sidebar.radio("📄 Selecione a página", ["Relatório por Agência", "Comparativo de Agências"])

df, agencia_col, meses = load_data()
meses_filtrados = st.sidebar.multiselect("Meses a exibir", meses, default=meses)

if page == "Relatório por Agência":
    agencia_selecionada = st.sidebar.selectbox("Agência", df[agencia_col].dropna().unique())
    dados_agencia = df[df[agencia_col] == agencia_selecionada]
    dados_filtrados = dados_agencia[[agencia_col, 'Fornecedor'] + meses_filtrados]

    st.title(f"Relatório de Vendas - {agencia_selecionada}")

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

    for _, row in dados_filtrados.iterrows():
        fornecedor = row["Fornecedor"]
        valores = [row[mes] if pd.notna(row[mes]) else 0 for mes in meses_filtrados]
        total = sum(valores)

        html_content = f"<h3>Relatório - {fornecedor}</h3>"
        html_content += f"<p><strong>Total:</strong> R$ {total:,.2f}</p>"
        for mes in meses_filtrados:
            valor = row[mes] if pd.notna(row[mes]) else 0
            html_content += f"<p><strong>{mes}:</strong> R$ {valor:,.2f}</p>"

        b64 = base64.b64encode(html_content.encode('utf-8')).decode()
        file_uuid = str(uuid.uuid4())
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio_{fornecedor}_{file_uuid}.html">📄 Exportar Card como HTML (pode salvar como PDF)</a>'

        df_plot = pd.DataFrame({'Mês': meses_filtrados, 'Valor': valores})
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_plot["Mês"], y=df_plot["Valor"], name="Vendas", text=df_plot["Valor"], textposition='auto'))
        fig.add_trace(go.Scatter(x=df_plot["Mês"], y=df_plot["Valor"], mode='lines+markers', name="Tendência", line=dict(dash='dot', color='black')))
        fig.update_layout(title=fornecedor, yaxis_title="Valor", xaxis_title="Mês", height=300)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"### {fornecedor}")
            for mes in meses_filtrados:
                valor = row[mes] if pd.notna(row[mes]) else 0
                st.markdown(f"**{mes}:** R$ {valor:,.2f}")
            st.markdown(f"**Total:** R$ {total:,.2f}")
            st.markdown(href, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Exportar Dados")
    csv = dados_filtrados.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar como CSV", data=csv, file_name="relatorio_agencia.csv", mime='text/csv')

elif page == "Comparativo de Agências":
    st.title("📊 Comparativo entre Agências")

    df_agencia_total = df.copy()
    df_agencia_total["Total"] = df_agencia_total[meses_filtrados].sum(axis=1)
    comparativo = df_agencia_total.groupby(agencia_col)["Total"].sum().reset_index()

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=comparativo[agencia_col],
        y=comparativo["Total"],
        text=comparativo["Total"],
        textposition="auto"
    ))
    fig_comp.update_layout(title="Total de Vendas por Agência", yaxis_title="Total (R$)", xaxis_title="Agência")
    st.plotly_chart(fig_comp, use_container_width=True)

    st.subheader("🏆 Agências que bateram a meta")
    meta_valor = st.number_input("Meta mínima (R$)", value=500000)
    ag_bateram_meta = comparativo[comparativo["Total"] >= meta_valor]
    st.dataframe(ag_bateram_meta)
