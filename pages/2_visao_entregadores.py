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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚛', layout='wide' )
#---------------------------------------------
# Funções
#---------------------------------------------
def clean_code( df1 ):
    #convertendo a coluna Age de testo para inteiro
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

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

def top_delivers(df1, order_asc):
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 
    'Delivery_person_ID']).mean().sort_values( ['City', 'Time_taken(min)'], ascending=order_asc ).reset_index()

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3

def avaliacao_entregador(df1):
    df_ratings_empre = df1.loc[:, ['Delivery_person_ID',
    'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
    return df_ratings_empre

def avaliacao_transito(df1):
    df_avg_std_traf = (df1.loc[:, ['Road_traffic_density', 
                    'Delivery_person_Ratings']].groupby('Road_traffic_density')
                .agg({'Delivery_person_Ratings': ['mean','std']}))

    #mudança do nome das columas
    df_avg_std_traf.columns = ['delivery_mean', 'delivery_std']
    #reset do index
    df_avg_std_traf = df_avg_std_traf.reset_index()
    return df_avg_std_traf

def avaliacao_clima(df1):
    df_avg_std_weather = (df1.loc[:, ['Weatherconditions', 
                    'Delivery_person_Ratings']].groupby('Weatherconditions')
                .agg({'Delivery_person_Ratings': ['mean','std']}))

    #mudança do nome das columas
    df_avg_std_weather.columns = ['delivery_mean', 'delivery_std']
    #reset do index
    df_avg_std_weather = df_avg_std_weather.reset_index()
    return df_avg_std_weather

#-----------------------------------Início da Estrutura lógica do código
#---------------------- -------------
# Import dataset
#-----------------------------------
data = pd.read_csv('dataset/train.csv')
df = pd.DataFrame(data)
df1 = df.copy()

#-----------------------------------
# Limpando dados
#-----------------------------------
df1 = clean_code( df1 )

#=========================================
#Barra Lateral
#=========================================
st.header('Marketplace - Visão Entregadores')

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
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # maior idade entre os entregadores 
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
        with col2:
            # menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            # melhor condição do veículo
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_veiculo)
        with col4:
            # pior condição do veículo
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_veiculo)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações') 
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação Média por Entregador')
            df_ratings_empre = avaliacao_entregador(df1)
            st.dataframe(df_ratings_empre)           
        with col2:
            st.markdown('##### Avaliação Média por Transito')
            df_avg_std_traf = avaliacao_transito(df1)
            st.dataframe(df_avg_std_traf)

            st.markdown('##### Avaliação Média por Clima')
            df_avg_std_weather = avaliacao_clima(df1)
            st.dataframe(df_avg_std_weather)
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Entregadores mais Rápidos')
            df3 = top_delivers(df1, order_asc=True)
            st.dataframe(df3)
        with col2:
            st.markdown('##### Entregadores mais Lentos')
            df3 = top_delivers(df1, order_asc=False)
            st.dataframe(df3)
















