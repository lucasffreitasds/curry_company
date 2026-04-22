#=================================
# Bibliotecas
#=================================
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')

#===================================
# Funções Limpeza
#===================================

def clean_code(df):
    """Esta função tem a responsibilidade de limpar o dataframe
       
       Tipo de limpaza:
       1. Remoção dos dados NaN
       2. Mudança do tipo de coluna de dados
       3. Remoção dos espaços das variáveis de texto
       4. Formatação da coluna de datas
       5. Limpeza da coluna de tempo
       
       Input: Dataframe
       Output: Dataframe  
    """

    # removendo espaços da string
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].astype(str).str.strip()
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(str).str.strip()
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(str).str.strip()
    df['Order_Date'] = df['Order_Date'].astype(str).str.strip()
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(str).str.strip()
    
    # excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df['Delivery_person_Age'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    # conversão para inteiro
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    
    # conversão para float
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    
    # conversão para data
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    
    # removendo NaN da coluna multiple_deliveries
    linhas_vazias1 = df['multiple_deliveries'] != 'NaN'
    df = df.loc[linhas_vazias1, :]
    
    # conversão para inteiro
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    
    #limpando a coluna de time taken
    df['Time_taken(min)'] = df['Time_taken(min)'].str.extract(r'(\d+)').astype(int)
    
    return df

#===================================
# Funções Layout
#===================================
def top_deliveries_asc(df):
    df_aux = (df.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
                .sort_values('Time_taken(min)', ascending = True)
                .reset_index()
             )
    df_aux1 = df_aux.head(10)
    
    return df_aux1

def top_deliveries_desc(df):   
    df_aux = (df.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
                .sort_values('Time_taken(min)', ascending = False)
                .reset_index()
             )
            
    df_aux1 = df_aux.head(10)
    
    return df_aux1
#===================================
# Leitura dos dados
#===================================

df_raw = pd.read_csv('C:/Users/T.i/Documents/Repos/python_para_ds/dataset/train.csv')
df = df_raw.copy()

#===================================
# Limpeza dos dados
#===================================

df = clean_code(df)

#====================================================
# Barra Lateral
#====================================================

st.header('Marketplace - Visão Entregadores')
st.dataframe(df)


#image_path = 'teste.png'
image = Image.open('teste.png')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(   
    'Até qual valor?',
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.header(date_slider)
st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low ', 'Medium ', 'High ', 'Jam '],
    default = ['Low ', 'Medium ', 'High ', 'Jam ']
)
st.sidebar.markdown('''---''')

#filtro de datas
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#filtro de trânsito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]
st.dataframe(df)

#====================================================
# Layout no Steamlit
#====================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    #criando containers para receber os gráficos de maneira mais organizado
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        
        with col1:
            st.markdown('### Maior de idade')
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)

        with col2:
            st.markdown('### Menor de idade')
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Maior de idade', menor_idade)
            
        with col3:
            st.markdown('### Melhor condicao de veiculos')
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor_condicao)

        with col4:
            st.markdown('### Pior condicao de veiculos')
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condicao', pior_condicao)

    with st.container():
        st.markdown('''___''')
        st.title('Avalições')

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Avaliacoes medias por entregador')
            media_avaliacoes = df.groupby('Delivery_person_ID')['Delivery_person_Ratings'].mean().reset_index(name = 'media_notas_por_entregador')
            st.dataframe(media_avaliacoes)

        with col2:
            st.subheader('Avaliacoes medias e desvio padrao por transito')
            media_desvio = df.groupby('Road_traffic_density')['Delivery_person_Ratings'].agg(media = 'mean',
                                                                          desvio_padrao = 'std').reset_index()
            st.dataframe(media_desvio)
            
            st.subheader('Avaliacoes medias por clima')
            media_clima = df.groupby('Weatherconditions')['Delivery_person_Ratings'].agg(media = 'mean',
                                                                  desvio_padrao = 'std').reset_index()
            st.dataframe(media_clima)

    with st.container():
        st.markdown('''___''')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Top entregadores mais rápidos')
            top_10_rapidos = top_deliveries_asc(df)
            st.dataframe(top_10_rapidos)
                            
        with col2:
            st.subheader('Top entregadores mais lentos')
            top_10_lentos = top_deliveries_desc(df)
            st.dataframe(top_10_lentos)











