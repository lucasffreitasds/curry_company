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

st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')

#===================================
# Funções
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

#==========================================================================

def order_metric(df):
    #Quantidade de pedidos por dia
    df_aux = df.groupby('Order_Date')['ID'].count().reset_index(name = 'Quantidade de Entregas')
    fig = px.bar(df_aux, x = 'Order_Date', y = 'Quantidade de Entregas')
    
    return fig

def traffic_order_share(df):                
    df_aux = df.groupby('Road_traffic_density')['ID'].count().reset_index(name = 'Quantidade de Entregas')
    df_aux['entregas_perc'] = df_aux['Quantidade de Entregas'] / df_aux['Quantidade de Entregas'].sum()
    fig = px.pie(df_aux, values='Quantidade de Entregas', names = 'Road_traffic_density')
    
    return fig

def traffic_order_city(df):
    df_aux = df.groupby(['City', 'Road_traffic_density'])['ID'].count().reset_index(name = 'Quantidade de Entregas')
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'Quantidade de Entregas', color = 'City')
    
    return fig

def order_by_week(df):
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
    df_aux = df.groupby('week_of_year')['ID'].count().reset_index(name = 'Quantidade de Entregas')
    fig = px.line(df_aux, x = 'week_of_year', y = 'Quantidade de Entregas')
    
    return fig

def order_share_by_week(df):
    df_aux01 = df.groupby('week_of_year')['ID'].count().reset_index(name = 'Quantidade de Entregas')
    df_aux02 = df.groupby('week_of_year')['Delivery_person_ID'].nunique().reset_index(name = 'Qtd Entregadores Unicos')
    df_aux = pd.merge(df_aux01, df_aux02, how = 'inner', on = 'week_of_year')
    df_aux['pedidos_por_delivery'] = df_aux['Quantidade de Entregas'] / df_aux['Qtd Entregadores Unicos']
    fig = px.line(df_aux, x = 'week_of_year', y = 'pedidos_por_delivery')
    
    return fig

def country_maps(df):
    df.groupby(['City', 'Road_traffic_density'])[['Delivery_location_latitude', 'Delivery_location_longitude']].median().reset_index()
    mapa = folium.Map()
    for index, location_info in df.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']]).add_to(mapa)
        folium_static(mapa, width = 1024, height = 600)

    return None
#===================================
# Importando os dados
#===================================

df_raw = pd.read_csv('dataset/train.csv')
df = df_raw.copy()

#===================================
# Limpeza dos dados
#===================================

df = clean_code(df)


#====================================================
# Barra Lateral
#====================================================

st.header('Marketplace - Visão Cliente')
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    #criando containers para receber os gráficos de maneira mais organizado
    with st.container():
        st.markdown('### Quantidade de Pedidos por Dia')
        fig = order_metric(df)
        st.plotly_chart(fig, use_container_width = True)        
              
    with st.container():
        #criando 2 colunas lado a lado
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### % Entregas por densidade transito')
            fig = traffic_order_share(df)
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.markdown('### Volume de pedidos por cidade e tipo de tráfego')
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width = True)                
            
with tab2:
    with st.container():
        st.markdown('# Pedidos por Semana')
        fig = order_by_week(df)
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.markdown('# Pedidos por por entregador por semana')
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_container_width = True)

with tab3:
    with st.container():
        st.markdown('### A localização central de cada cidade por tipo de tráfego')
        country_maps(df)























