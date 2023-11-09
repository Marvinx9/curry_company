#libraries

import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
from streamlit_folium import folium_static
import folium


#bibliotecas
import pandas as pd
import re
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍔', layout='wide' )
#---------------------------------------------
# Funções
#---------------------------------------------
def clean_code( df1 ):
    """ Esta função tem a responsabilidade 'de limpas o DataFrame
        
    Tipos de limpezas:
    1. Remoção dos 'NaN'
    2. Mudança do tipo de coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

    Input: DataFrame
    Output: Dataframe
    """
    #convertendo a coluna Age de texto para inteiro
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    #Removendo as linhas com valores vazios 'NaN '
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #convertendo delivery_person_ratings para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #convertendo a coluna order_date para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )

    #convertendo multiple_deliveries para inteiro
    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #limpando os espaços das colunas
    df1 = df1.reset_index(drop=True)
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
        
    #limpeza da columa time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    return df1

def distmedent(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_longitude', 'Restaurant_latitude']

    df1['distance'] = df1.loc[ :, cols ].apply( lambda x: 
                                            haversine(
                                                    (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1) 
    avg_distance = np.round( df1['distance'].mean(), 2 )
    return avg_distance


def sdt_avg_time(df1, op, festival):
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2 )
    return df_aux

def tempo_medio_cidade_trafego(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict( type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def tempo_medio_std_cidade_pedido(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    return df_aux

def distancia_cidade(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_longitude', 'Restaurant_latitude']
    df1['distance'] = df1.loc[ :, cols ].apply( lambda x: 
                                        haversine(
                                                (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1) 
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    # pull is given as a fraction od the pei radius
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.05, 0])])
    return fig

def densidade_trafego_cidade(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                    color='std_time', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    
    return fig
#-----------------------------------Início da Estrutura lógica do código
#-----------------------------------
# Import dataset
#-----------------------------------
data = pd.read_csv('dataset/train.csv')
df = pd.DataFrame(data)
df1 = df.copy()

#-----------------------------------
# Limpando dados
#-----------------------------------
df1 = clean_code(df)

#=========================================
#Barra Lateral
#=========================================  
st.header('Marketplace - Visão Restaurantes')

#image_path = 'C:/Users/afran/OneDrive - Educacional/DSA/repos/proj1/logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime( 2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6) ,
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")
st.header( date_slider)


traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low','Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown('### By @Marvinx9')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, : ]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#=========================================
#Layout no Streamlit
#=========================================
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '_', '_'] )
with tab1:
    with st.container():
        st.markdown('Overall Metrics')
        col1, col2, col3 = st.columns(3)
        with col1:
            uni = len( df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entrega Única', uni)
        with col2:
            df_aux = sdt_avg_time(df1, op='std_time', festival='Yes')
            col2.metric( 'Desvio Padrão de Entrega com Festa', df_aux)
        with col3:
            df_aux = sdt_avg_time(df1, op='avg_time', festival='Yes')
            col3.metric( 'Tempo Médio de Entrega com Festa', df_aux)
        col4, col5, col6 = st.columns(3)
        with col4:
            avg_distance = distmedent(df1)
            col4.metric('Distribuição Média de Entrega', avg_distance)
        with col5:
            df_aux = sdt_avg_time(df1, op='std_time', festival='No')
            col5.metric( 'Desvio Padrão de Entrega sem Festa', df_aux)
            
        with col6:
            df_aux = sdt_avg_time(df1, op='avg_time', festival='No')
            col6.metric( 'Tempo Médio de Entrega sem Festa', df_aux)
    with st.container():
        st.markdown("""---""")
        st.markdown('## Tempo Médio e Desvio Padrão')
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('#### Por Cidade e Tráfego')
            fig = tempo_medio_cidade_trafego(df1)
            st.plotly_chart( fig, use_container_width=True)
        with col2:
            st.markdown('#### Por Cidade e Pedido')
            df_aux = tempo_medio_std_cidade_pedido(df1)
            st.dataframe(df_aux)
    with st.container():
        st.markdown("""---""")
        st.markdown('## Distribuição do tempo')
        col1, col2 = st.columns( 2 )
        with col1:
            fig = distancia_cidade(df1)
            st.plotly_chart( fig, use_container_width=True )
        with col2:
            fig = densidade_trafego_cidade(df1)
            st.plotly_chart(fig)
        
