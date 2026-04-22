import streamlit as st
from PIL import Image

st.set_page_config(
    page_title ='Home'
)

#image_path = 'teste.png'
image = Image.open('teste.png')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''___''')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão da Empresa:
        - Visão Gerencial: métricas gerais de comportamento
        - Visão Tática: indicadores semanais de crescimento
        - Visão Geográfica: insights e geolocalização
    - Visão dos Entregadores:
        - Acompanhamento dos indicadores de cresciimento
    - Visão dos Restaurantes
        - Indicadores semanais de crescimento dos restaurantes
    '''
)