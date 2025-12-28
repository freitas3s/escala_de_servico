import streamlit as st
pg = st.navigation([
    st.Page("main.py", title="Home"),
    st.Page("verificarTrocas.py", title="Verificar Trocas"),

],
    position = "top"
)

pg.run()