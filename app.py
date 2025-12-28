import streamlit as st
pg = st.navigation([
    st.Page("main.py", title="Home"),
    st.Page("verificar_trocas.py", title="Verificar Trocas"),

],
    position = "top"
)

pg.run()