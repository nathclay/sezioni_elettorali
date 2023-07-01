import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import pydeck as pdk
from matplotlib.colors import ListedColormap
import random



#funzioni
def dati(anno, elezione, tipologia, com_mun=None, municipio=None, partito=None, presidente=None, sindaco=None, candidato=None):
    #caso elezione amministrative
    if municipio is not None:
        path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_municipio"+str(municipio)
    else:
        path=anno+"/"+anno+"_"+elezione+"_"+com_mun

    if presidente is not None:
        path=path+"_presidente.csv"
        df=pd.read_csv(path) 
        df['Presidente']=presidente
        filtered_df = df[["SEZIONE", 'Presidente',presidente]]
        filtered_df.rename(columns={presidente: 'Voti'}, inplace=True) 
    elif sindaco is not None:
        path=path+"_sindaco.csv"
        df=pd.read_csv(path)
        df['Sindaco']=sindaco
        filtered_df = df[["SEZIONE", 'Sindaco', sindaco]] 
        filtered_df.rename(columns={sindaco: 'Voti'}, inplace=True) 
    elif partito is not None:
        path=path+"_partito.csv"
        df=pd.read_csv(path)
        df['Partito']=partito
        filtered_df=df[["SEZIONE", 'Partito', partito]]
        filtered_df.rename(columns={partito: 'Voti'}, inplace=True) 
    elif candidato is not None:
        path=path+"_candidato.csv"
        df=pd.read_csv(path)
        filt = df[df["CANDIDATO"] == candidato]
        filt['Candidato']=candidato
        filtered_df=filt[["SEZIONE", 'Candidato', "PREFERENZE"]]
        filtered_df.rename(columns={"PREFERENZE": 'Voti'}, inplace=True) 
    else:
        path=path+"_ballottaggio.csv"
        df=pd.read_csv(path)
        filtered_df=df.iloc[:,:-2]
    return (filtered_df)
    
def piu_votato(anno, elezione, tipologia, com_mun=None, municipio=None, partito=None, presidente=None, sindaco=None, candidato=None):
    if municipio is not None:
        path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_municipio"+str(municipio)
    else:
        path=anno+"/"+anno+"_"+elezione+"_"+com_mun
    dict={'presidente': 'presidente piu votato', 'sindaco': 'sindaco piu votato', 'partito': 'partito piu votato', 'candidato': 'candidato piu votato'}

    value_to_subtract=-2

    if presidente is not None:
        path=path+"_presidente.csv"
        df=pd.read_csv(path)
        val=dict['presidente']
    elif sindaco is not None:
        path=path+"_sindaco.csv"
        df=pd.read_csv(path)
        val=dict['sindaco']
    elif partito is not None:
        if municipio is not None:
            value_to_subtract=-3
        path=path+"_partito.csv"
        df=pd.read_csv(path)
        val=dict['partito']
    elif candidato is not None:
        path=path+"_candidato.csv"
        df=pd.read_csv(path)
        val=dict['candidato']
    else:
        if municipio is not None:
            value_to_subtract=-3
        path=path+"_ballottaggio.csv"
        df=pd.read_csv(path)

    # Get the column with the highest value for each row
    df["Più votato"] = df.iloc[:, 1:value_to_subtract].idxmax(axis=1)
    df["Voti"] = df.iloc[:, 1:value_to_subtract].max(axis=1)
    # Create a new dataset with the desired columns
    new_df = df[["SEZIONE", "Più votato", "Voti"]]
    return(new_df)



def find_partiti(anno, elezione, com_mun=None, municipio=None):
    #caso elezioni amministrative
    if municipio is not None:
        path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_municipio"+str(municipio)+"_listapartiti.csv"
    else:
        path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_listapartiti.csv"
    df = pd.read_csv(path, header=None)
    df.loc[-1] = ["Più votato"]
    df.index = df.index + 1  # Shift the index by 1 to accommodate the new row
    df.sort_index(inplace=True)  # Sort the index
    return df.iloc[:, 0].tolist()

def find_candidati(anno, elezione, partito, com_mun=None, municipio=None):
    #caso elezioni amministrative
    if municipio is not None:
        file_path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_municipio"+str(municipio)+"_listacandidati.csv"
    else:
        file_path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_listacandidati.csv"
    df = pd.read_csv(file_path)
    filtered_df = df[df["LISTA"] == partito]
    distinct_candidati = filtered_df["CANDIDATO"].unique().tolist()
    return distinct_candidati

def find_presidenti(anno, elezione, com_mun, municipio):
    #solo caso municipali
    file_path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_municipio"+str(municipio)+"_listapresidenti.csv"
    df = pd.read_csv(file_path, header=None)
    df.loc[-1] = ["Più votato"]
    df.index = df.index + 1  # Shift the index by 1 to accommodate the new row
    df.sort_index(inplace=True)  # Sort the index
    return df.iloc[:, 0].tolist()

def find_sindaci(anno, elezione, com_mun):
    #solo caso comunali
    file_path=anno+"/"+anno+"_"+elezione+"_"+com_mun+"_listasindaci.csv"
    df = pd.read_csv(file_path, header=None)
    df.loc[-1] = ["Più votato"]
    df.index = df.index + 1  # Shift the index by 1 to accommodate the new row
    df.sort_index(inplace=True)  # Sort the index
    return df.iloc[:, 0].tolist()


#qui il codice del sidebar per scegliere l'elezione
anno = st.sidebar.selectbox('Scegli l\'anno',['2021'])
if anno == '2016' or anno=='2021':
    val=['amministrative']
elif anno == '2018':
    val=['camera', 'regionali']
elif anno == '2019':
    val=['europee']
elif anno == '2022':
    val=['camera']
elif anno == '2023':
    val=['regionali']

elezione=st.sidebar.selectbox('Scegli l\'elezione', val)

#caso elezioni amministrative
if elezione=='amministrative':
    piu_vot=False
    com_mun=st.sidebar.selectbox('Municipali o comunali?',['comunali', 'municipali'])
    #distionzione municipali/comunali
    if com_mun=='municipali':
        municipio=st.sidebar.selectbox('Seleziona il municipio', [1,2,3,4,5,6,7,8,9,10,11,12,13,15])
        tipologia=st.sidebar.selectbox('Che dato ti interessa?', ['presidente','partito','candidato', 'ballottaggio'])
    else:
        tipologia=st.sidebar.selectbox('Che dato ti interessa?', ['sindaco','partito','candidato', 'ballottaggio'])
        municipio=None

    if tipologia == 'candidato':
        values=find_partiti(anno, elezione, com_mun, municipio)
        values.pop(0)
        partito=st.sidebar.selectbox('Seleziona il partito',values)
        values=find_candidati(anno, elezione, partito, com_mun, municipio)
        candidato=st.sidebar.selectbox('Seleziona il candidato',values)
        if candidato=='Più votato':
            piu_vot=True
            data=piu_votato(anno, elezione, tipologia, com_mun, municipio, candidato=candidato)
        else:
            data=dati(anno, elezione, tipologia, com_mun, municipio, candidato=candidato)
    elif tipologia == 'presidente':
        values=find_presidenti(anno, elezione, com_mun, municipio)
        presidente=st.sidebar.selectbox('Seleziona', values)
        if presidente=='Più votato':
            piu_vot=True
            data=piu_votato(anno, elezione, tipologia, com_mun, municipio, presidente=presidente)
        else:
            data=dati(anno, elezione, tipologia, com_mun, municipio, presidente=presidente)
    elif tipologia == 'sindaco':
        values=find_sindaci(anno, elezione, com_mun)
        sindaco=st.sidebar.selectbox('Seleziona', values)
        if sindaco=='Più votato':
            piu_vot=True
            data=piu_votato(anno, elezione, tipologia, com_mun, sindaco=sindaco)
        else:
            data=dati(anno, elezione, tipologia, com_mun, sindaco=sindaco)
    elif tipologia == 'partito':
        values=find_partiti(anno, elezione, com_mun, municipio)
        partito=st.sidebar.selectbox('Seleziona', values)
        if partito=='Più votato':
            piu_vot=True
            data=piu_votato(anno, elezione, tipologia, com_mun, municipio, partito=partito)
        else:
            data=dati(anno, elezione, tipologia, com_mun, municipio, partito=partito)
    elif tipologia == 'ballottaggio':
        piu_vot=True
        data=piu_votato(anno, elezione, tipologia, com_mun, municipio)


#qui il main
st.header ("Tool grafico dati elettorali di Roma")

#se abbiamo scelto comunali possiamo visualizzare la mappa di tutta roma o di uno specifico municipio
if com_mun=='comunali':
    selezione=st.sidebar.selectbox('Vuoi visualizzare la mappa di tutta Roma o di un singolo municipio?', ['Tutta Roma', 'Municipio 1', 'Municipio 2', 'Municipio 3', 'Municipio 4', 'Municipio 5', 'Municipio 6', 'Municipio 7', 'Municipio 8', 'Municipio 9', 'Municipio 10', 'Municipio 11', 'Municipio 12', 'Municipio 13', 'Municipio 14', 'Municipio 15'])
    values_municipi={'Tutta Roma':0, 'Municipio 1': 1, 'Municipio 2': 2, 'Municipio 3': 3, 'Municipio 4': 4, 'Municipio 5': 5, 'Municipio 6': 6, 'Municipio 7': 7, 'Municipio 8': 8, 'Municipio 9': 9, 'Municipio 10': 10, 'Municipio 11': 11, 'Municipio 12': 12, 'Municipio 13': 13, 'Municipio 14': 14, 'Municipio 15':15}
    municipio = values_municipi[selezione]

#bottone per far partire il download solo dopo la selezione 
if st.sidebar.button('Invia'):
    #coordinate dei centroidi dei municipi
    centroids={'Lon':[12.4964, 12.47794957, 12.50118016, 12.55432441, 12.59134303, 12.57556528, 12.68711693, 
                      12.58189857, 12.52916829, 12.49781296, 12.36309958, 12.3767787, 12.4584861, 12.34611241, 12.34548312, 12.41567276], 
               'Lat': [41.9028, 41.89862783, 41.92070444, 41.99643881, 41.93216218, 41.88910484,
                41.88754993, 41.83904195, 41.82866719, 41.75764874, 41.7393902, 41.83066297, 41.8771455, 41.91044296, 41.97566369, 42.02972271]}
    
    #caso comunali e visualizzazione di tutta roma
    if municipio==0:
        zoom=10
        gdf = gpd.read_file("sezioni_elettorali\\tutta_roma.shp")
        sezioni_elettorali = gpd.read_file("sezioni_elettorali\\tutta_roma.shp")
        borders_municipi=gpd.read_file("borders_municipi\\borders_municipi.shp")
    
    #caso visualizzazione di un solo municipio
    else:
        zoom=13
        gdf = gpd.read_file("buildings/buildings.shp")
        gdf=gdf[gdf['municipio']==municipio]
        sezioni_elettorali = gpd.read_file("sezioni_elettorali/tutta_roma.shp")
        sezioni_elettorali=sezioni_elettorali[sezioni_elettorali['municipio']==municipio]
        sezioni_elettorali=pd.merge(sezioni_elettorali, data, left_on="sezione", right_on="SEZIONE")
        borders_municipi=gpd.read_file("borders_municipi/borders_municipi.shp")
        borders_municipi=borders_municipi[borders_municipi['municipio']==municipio]
    
    merged = pd.merge(gdf, data, left_on="sezione", right_on="SEZIONE")
    val={'Voti': 'Voti', 'Più votato': 'Più votato'}

    if piu_vot==False:
        valore=val['Voti']
        color_scale = [[255, 255, 255, 100],  # White
        [0, 255, 0, 100],      # Green
        [255, 0, 0, 100]       # Red
        ]
        # Define the maximum value of the "voti" column
        max_voti = merged['Voti'].max()
        # Normalize the "voti" values between 0 and 1
        if max_voti != 0:
            merged['normalized_voti'] = merged['Voti'] / max_voti
        else:
            merged['normalized_voti'] = 0
        # Define a function to convert a normalized value to a color
        def get_fill_color(v):
            # Interpolate the color based on the normalized value
            if v <= 0:
                return color_scale[0]
            elif v >= 1:
                return color_scale[-1]
            else:
                index = int(v * (len(color_scale) - 1))
                r = int(color_scale[index][0] * (1 - v) + color_scale[index+1][0] * v)
                g = int(color_scale[index][1] * (1 - v) + color_scale[index+1][1] * v)
                b = int(color_scale[index][2] * (1 - v) + color_scale[index+1][2] * v)
                a = int(color_scale[index][3] * (1 - v) + color_scale[index+1][3] * v)
                return [r, g, b, a]
        merged['fill_color'] = merged['normalized_voti'].apply(get_fill_color)
        tooltip = {
                "html": "<b>Sezione:</b> {SEZIONE}<br> <b>Voti:</b> {Voti}<br> ",
                "style": {
                    "backgroundColor": "white",
                    "color": "black"
                    },
                "layer": 0
            }
    else:
        valore=val['Più votato']
        predefined_colors = [[255, 0, 0, 100],   # Red
                [0, 255, 0, 100],   # Green
                [0, 0, 255, 100],   # Blue
                [128, 0, 128, 100], # Purple
                [255, 255, 0, 100]  # Yellow
                ]
        # Get distinct values from the "piu votato" column
        distinct_values = merged['Più votato'].unique()
        # Assign predefined colors to the first five distinct values
        color_mapping = dict(zip(distinct_values[:5], predefined_colors))
        # Generate random colors for additional distinct values, if any
        if len(distinct_values) > 5:
            random_colors = [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 100] for _ in range(len(distinct_values) - 5)]
            color_mapping.update(dict(zip(distinct_values[5:], random_colors)))
        # Define a function to get the fill color based on the "piu votato" value
        def get_fill_color(p):
            return color_mapping.get(p, [255, 255, 255, 100])  # Default to white color if value not found
        merged['fill_color'] = merged['Più votato'].apply(get_fill_color)
        tooltip = {
            "html": "<b>Sezione:</b> {SEZIONE}<br> <b>Più votato:</b> {Più votato}<br> ",
            "style": {
                "backgroundColor": "white",
                "color": "black"
            }
        }

    layer1 = pdk.Layer(
        "GeoJsonLayer",
        data=sezioni_elettorali,
        get_fill_color=[0, 0, 0, 0],  # Transparent fill color
        get_line_color=[0, 0, 0],  # Black border color
        filled=True,
        stroked=True,
        extruded=False,
        wireframe=False,
        line_width_min_pixels=1,
        pickable=True,
    )
    layer2 = pdk.Layer(
        "GeoJsonLayer",
        data=merged,
        get_fill_color='fill_color',
        auto_highlight=True,
        pickable=True,
    )
    layer3 = pdk.Layer(
        "GeoJsonLayer",
        data=borders_municipi,
        get_fill_color=[0, 0, 0, 0],  # Transparent fill color
        get_line_color=[255, 0, 0, 100],  # Black border color
        filled=True,
        stroked=True,
        extruded=False,
        wireframe=False,
        line_width_min_pixels=3,
    )
    # Create a view state to set the initial map center and zoom level
    view_state = pdk.ViewState(
        latitude= centroids['Lat'][municipio],
        longitude=centroids['Lon'][municipio],
        zoom=zoom,
    )
    # Create the Deck object with the layer and view state
    deck = pdk.Deck(
        layers=[layer1, layer2,layer3], 
        initial_view_state=view_state, 
        map_style="light",
        tooltip=tooltip
    )

    st.pydeck_chart(deck)



