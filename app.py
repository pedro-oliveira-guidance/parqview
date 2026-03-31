import io
import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="parqview",
    page_icon="🦆",
    layout="wide",
)

st.title("parqview")
st.caption("Arraste um arquivo Parquet para inspecionar schema, dados e estatísticas.")

FILE_TYPES = {
    "Parquet": ["parquet"],
    "CSV": ["csv"],
    "JSON": ["json"],
    "Excel": ["xlsx", "xls"],
}

file_type = st.selectbox("Tipo de arquivo", list(FILE_TYPES.keys()), index=0)
accepted_extensions = FILE_TYPES[file_type]

uploaded_file = st.file_uploader(
    f"Selecione ou arraste um arquivo .{'/'.join(accepted_extensions)}",
    type=accepted_extensions,
)

if uploaded_file is None:
    st.info("Nenhum arquivo carregado. Selecione o tipo e arraste o arquivo acima.")
    st.stop()


@st.cache_data
def get_excel_sheets(file_bytes: bytes) -> list[str]:
    return pd.ExcelFile(io.BytesIO(file_bytes)).sheet_names


@st.cache_data
def load_file(file_bytes: bytes, ftype: str, sheet: str | None = None) -> pd.DataFrame:
    buf = io.BytesIO(file_bytes)
    if ftype == "Parquet":
        return pd.read_parquet(buf)
    if ftype == "CSV":
        return pd.read_csv(buf)
    if ftype == "JSON":
        return pd.read_json(buf)
    if ftype == "Excel":
        return pd.read_excel(buf, sheet_name=sheet)
    raise ValueError(f"Tipo não suportado: {ftype}")


file_bytes = uploaded_file.read()
selected_sheet = None

if file_type == "Excel":
    sheets = get_excel_sheets(file_bytes)
    selected_sheet = st.selectbox("Aba", sheets, index=0)

df = load_file(file_bytes, file_type, selected_sheet)

# Header metrics
col1, col2, col3 = st.columns(3)
col1.metric("Linhas", f"{len(df):,}")
col2.metric("Colunas", len(df.columns))
memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
col3.metric("Memória", f"{memory_mb:.2f} MB")

tab_schema, tab_sample, tab_stats, tab_sql = st.tabs(["Schema", "Amostra (100 linhas)", "Estatísticas", "SQL"])

with tab_schema:
    schema_df = pd.DataFrame(
        {"coluna": df.dtypes.index, "tipo": df.dtypes.astype(str).values}
    ).reset_index(drop=True)
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

with tab_sample:
    st.dataframe(df.head(100), use_container_width=True)

with tab_stats:
    st.subheader("Nulos por coluna")
    null_counts = df.isnull().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    null_df = pd.DataFrame(
        {"coluna": null_counts.index, "nulos": null_counts.values, "% nulos": null_pct.values}
    ).reset_index(drop=True)
    st.dataframe(null_df, use_container_width=True, hide_index=True)

    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        st.subheader("Estatísticas descritivas (colunas numéricas)")
        st.dataframe(numeric_df.describe().T, use_container_width=True)
    else:
        st.info("Nenhuma coluna numérica encontrada.")

with tab_sql:
    st.caption("A tabela está registrada como `df`. Exemplo: `SELECT * FROM df LIMIT 10`")
    query = st.text_area("Query SQL", value="SELECT * FROM df LIMIT 10", height=120)
    if st.button("Executar"):
        try:
            result = duckdb.query_df(df, "df", query).df()
            st.success(f"{len(result):,} linha(s) retornada(s)")
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")
