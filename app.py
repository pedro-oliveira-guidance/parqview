import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="parqview",
    page_icon="🦆",
    layout="wide",
)

st.title("parqview")
st.caption("Arraste um arquivo Parquet para inspecionar schema, dados e estatísticas.")

uploaded_file = st.file_uploader("Selecione ou arraste um arquivo .parquet", type=["parquet"])

if uploaded_file is None:
    st.info("Nenhum arquivo carregado. Arraste um .parquet acima para começar.")
    st.stop()


@st.cache_data
def load_parquet(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(file_bytes))


df = load_parquet(uploaded_file.read())

# Header metrics
col1, col2, col3 = st.columns(3)
col1.metric("Linhas", f"{len(df):,}")
col2.metric("Colunas", len(df.columns))
memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
col3.metric("Memória", f"{memory_mb:.2f} MB")

tab_schema, tab_sample, tab_stats = st.tabs(["Schema", "Amostra (100 linhas)", "Estatísticas"])

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
