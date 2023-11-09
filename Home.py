import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='👨‍💻', layout='wide',
)


#image_path = 'C:/Users/afran/OneDrive - Educacional/DSA/repos/proj1/'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=150)

st.sidebar.markdown('# Marvis Company')
st.sidebar.markdown('## Marketplace FastFood')
st.sidebar.markdown("""---""")
st.sidebar.markdown('### by @afranio')
st.write('# Sobre esse projeto')    

st.markdown(
    """
    Marvis Company é uma plataforma fictícia de marketplace que contém vários restaurantes parceiros na Índia, a pedido do CEO foi realizado um estudo dos dados para acompanhar de modo concreto a evolução dos restaurantes parceiros, assim como uma análise sobre os entregadores e sobre empresa Marvis Company.
    ### Tópicos da análise
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    """
)
col1, col2 = st.columns(2)
with col1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("💻GitHub", "https://github.com/Marvinx9/marvis_company")
    with col2:
        st.link_button("👨‍⚖️Portfólio", "https://marvinx9.github.io/portfolio_projetos/")
    with col3:    
        st.link_button("LinkedIn", "https://www.linkedin.com/in/afranionunesdantas/")
