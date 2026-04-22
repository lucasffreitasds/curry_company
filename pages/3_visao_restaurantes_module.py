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
import numpy as np

st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')

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
def distance(df):
    colums = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    #criei uma coluna chamada distance que vai receber os valores das distancias entre as latitudes
    df['distance'] = df.loc[:, colums].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
    #fazendo a média
    dist_media = np.round(df.loc[:, 'distance'].mean(), 2)

    return dist_media

#-----------------------

def avg_and_std_time_deliveries(df, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            input:
                - df: Dataframe com os dados necessários para o cálculo
                - festival: se é em festival 'Yes' ou não 'No'
                - op: tipo de operação que precisa ser calculado
                    'media': calcula o tempo médio do tempo
                    'desvio': calcula o desvio padrão do tempo
            Output:
                - df: Dataframe com duas colunas e uma linha
    """
        
    df_aux = (df.groupby('Festival')['Time_taken(min)'].agg(media = 'mean',																				                                desvio = 'std').reset_index())
    df_aux = df_aux.loc[df_aux['Festival'] == festival, op]

    return df_aux

#-------------------------

def dist_avg_city(df):
    colums = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    #criei uma coluna chamada distance que vai receber os valores das distancias entre as latitudes
    df['distance'] = df.loc[:, colums].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)

    #fazendo a média dessa distancia por cidade
    avg_distance = df.groupby('City')['distance'].mean().reset_index()
    st.dataframe(avg_distance)

    fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.05, 0])])

    return fig

#-------------------------

def avg_std_time_graph(df):
    df_aux = df.groupby('City')['Time_taken(min)'].agg(tempo_medio = 'mean',
                                                       desvio_padrao = 'std').reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name = 'Control', 
            x = df_aux['City'], 
            y = df_aux['tempo_medio'],                       
            error_y = dict(type = 'data', array = df_aux['desvio_padrao'])
        )
    )
    fig.update_layout(barmode = 'group')

    return fig

#-------------------------

def avg_std_time_tipo_de_pedido(df):
    df_aux = df.groupby(['City', 'Type_of_order'])['Time_taken(min)'].agg(tempo_medio = 'mean',
                                                                          desvio_padrao = 'std')

    return df_aux

#-------------------------

def avg_std_time_tipo_de_trafego(df):
    df_aux = df.groupby(['City', 'Road_traffic_density'])['Time_taken(min)'].agg(tempo_medio = 'mean',
                                                                                desvio_padrao = 'std').reset_index()

    fig = px.sunburst(
        df_aux, path = ['City', 'Road_traffic_density'], 
        values = 'tempo_medio', color = 'desvio_padrao', 
        color_continuous_scale = 'RdBu', 
        color_continuous_midpoint = np.average(df_aux['desvio_padrao'])
    )

    return fig

#-------------------------



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

st.header('Marketplace - Visão Restaurantes')
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
    with st.container():

        st.markdown('# Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.markdown('##### Entregadores Únicos')
            qtd_entregadores = df.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Quantidade de entregadores unicos', qtd_entregadores)

        with col2:
            st.markdown('##### Distancia media')
            dist_media = distance(df)
            col2.metric('Distancia Media', dist_media)
                
        with col3:
            st.markdown('##### Tempo de entrega medio c/ festival')
            df_aux = avg_and_std_time_deliveries(df, 'Yes ', 'media') 
            col3.metric('Tempo de entrega medio c/ festival', df_aux)
              
        with col4:
            st.markdown('##### Desvio padrao de entrega c/ festival')
            df_aux = avg_and_std_time_deliveries(df, 'Yes ', 'desvio')
            col4.metric('Desvio padrão c/ festival', df_aux)

        with col5:
            st.markdown('##### Tempo de entrega medio s/ festival')
            df_aux = avg_and_std_time_deliveries(df, 'No ', 'media') 
            col5.metric('Tempo de entrega medio s/ festival', df_aux)

        with col6:
            st.markdown('##### Desvio padrao de entrega s/ festival')
            df_aux = avg_and_std_time_deliveries(df, 'No ', 'desvio')
            col6.metric('Desvio padrão c/ festival', df_aux)
        
    with st.container():

        st.markdown('''___''')
        st.markdown('# Distância media por cidade')
        fig = dist_avg_city(df)
        st.plotly_chart(fig)      
            
    with st.container():

        st.markdown('''___''')
        st.markdown('# Distribuição do tempo')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Distribuição do tempo por cidade')
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig) 

        with col2:
            st.markdown('##### Tempo medio por tipo de entrega')
            df_aux = avg_std_time_tipo_de_pedido(df) 
            st.dataframe(df_aux)                     
            
    with st.container():

        st.markdown('''___''')
        st.markdown('##### Tempo medio por cidade e por tipo de tráfico')
        fig = avg_std_time_tipo_de_trafego(df)
        st.plotly_chart(fig)




































