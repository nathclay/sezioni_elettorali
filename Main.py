import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import pydeck as pdk
from matplotlib.colors import ListedColormap
import random

#il path dove sono i dati.
path_folder = ""
st.set_page_config(layout='wide')

#dizionario per standardizzare nome dei partiti/candidati sindaco
standard={'GIORGIA MELONI FRATELLI D\'ITALIA':'FRATELLI D\'ITALIA',
      'CALENDA SINDACO': 'AZIONE',
      'PD PARTITO DEMOCRATICO': 'PARTITO DEMOCRATICO',
      'MOVIMENTO CINQUE STELLE "2050"': 'MOVIMENTO 5 STELLE',
      'LEGA SALVINI PREMIER': 'LEGA',
      'ROCCA FRANCESCO': 'ROCCA',
      'D\'AMATO ALESSIO': 'D\'AMATO',
      'ENRICO MICHETTI': 'MICHETTI',
      'ROBERTO GUALTIERI': 'GUALTIERI',
      'FABIOLA CENCIOTTI': 'ALTRI DX',
      'CARLO CALENDA': 'CALENDA',
      'VIRGINIA RAGGI': 'RAGGI',
      'LISTA CIVICA "VIRGINIA RAGGI"': 'ALTRI M5S',
      'POTERE AL POPOLO': 'POTERE AL POPOLO',
      'SINISTRA CIVICA ECOLOGISTA': 'SX CIVICA ECOLOGISTA',
      'LISTA CIVICA GUALTIERI SINDACO': 'ALTRI SX',
      'DEMOS DEMOCRAZIA SOLIDALE': 'DEMOS',
      'NOI MODERATI': 'NOI MODERATI',
      'GIORGIA MELONI-FRATELLI D\'ITALIA': 'FRATELLI D\'ITALIA',
      'PD PARTITO DEMOCRATICO D\'AMATO PRESIDENTE': 'PARTITO DEMOCRATICO',
      'MOVIMENTO 5 STELLE 2050': 'MOVIMENTO 5 STELLE',
      'VERDI E SINISTRA-EUROPA VERDE POSSIBILE': 'VERDI-SINISTRA',
      'PARTITO POPOLARE EUROPEO-FORZA ITALIA BERLUSCONI': 'FORZA ITALIA',
      'AZIONE-ITALIA VIVA-CALENDA-RENEW EUROPE': 'AZIONE ITALIA VIVA'}


#funzione che ritorna il path specifico per l'elezione in questione
def func_path(anno, elezione, com_mun=None, municipio=None):
    #caso elezioni amministrative
    if com_mun is not None:
        if municipio is not None:
            path=path_folder+anno+"/"+anno+"_"+elezione+"_"+com_mun+"_municipio"+str(municipio)
        else:
            path=path_folder+anno+"/"+anno+"_"+elezione+"_"+com_mun

    #caso elezioni camera
    elif elezione=='camera':
        path=path_folder+anno+"/"+anno+"_"+elezione+".csv"

    #caso elezioni regionali
    elif elezione=='regionali':
        path=path_folder+anno+"/"+anno+"_"+elezione

    return path

#funzione che ritorna il dataframe con i dati elettorali
def dati(piu_vot, anno, elezione, tipologia=None, com_mun=None, municipio=None, partito=None, presidente=None, sindaco=None, candidato=None):
    path=func_path(anno, elezione, com_mun, municipio)

    #caso specifico candidato/sindaco/presidente
    #il dataframe nel caso candidato è del tipo: sezione, candidato, voti, lista. La colonna lista e candidato contengono per tutte le righe il nome del candidato e la lista associata
    #In tutti gli altri casi: sezione, tutti i partiti/sindaci/presidenti con quello specifico rinominato Voti, Totale, affluenza, 
    # colonna aggiunta "partito/sindaco/presidnete" con tutti i valori uguali al presidente/sindaco/partito scelto
    if piu_vot==False:
        #caso elezioni amministrative
        if elezione=='amministrative':
            if tipologia !='affluenza':
                df=pd.read_csv(path+"_"+tipologia+".csv")
            #a seconda della tipologia bisogna aggiungere una colonna e rinominare il dato dei voti per avere sempre lo stesso nome da usare nelle altre funzioni
            #Se ci fosse un partito/sindaco/presidente chiamato "Voti" darebbe errore
            if tipologia=='affluenza':
                #nel caso dell'affluenza i dati li prendiamo dal file partito.csv
                df=pd.read_csv(path+"_partito.csv")
                df.rename(columns={'AFFLUENZA':'Voti'}, inplace=True)
            elif tipologia=='sindaco':
                df['Sindaco']=sindaco
                df.rename(columns={sindaco: 'Voti'}, inplace=True)
            elif tipologia=='presidente':
                df['Presidente']=presidente
                df.rename(columns={presidente: 'Voti'}, inplace=True) 
            elif tipologia=='partito':
                df['Partito']=partito
                df.rename(columns={partito: 'Voti'}, inplace=True) 
            elif tipologia=='candidato':
                df = df[df["CANDIDATO"] == candidato]
                df.rename(columns={"PREFERENZE": 'Voti'}, inplace=True) 
            elif tipologia=='ballottaggio':
                df=df.iloc[:,:-2]

        #caso elezioni camera
        elif elezione=='camera':
            df=pd.read_csv(path) 
            if tipologia=='affluenza':
                df.rename(columns={'AFFLUENZA':'Voti'}, inplace=True)
            else:
                df.rename(columns={partito: 'Voti'}, inplace=True)

        #caso elezioni regionali
        elif elezione=='regionali':
            if tipologia!='affluenza':
                df=pd.read_csv(path+"_"+tipologia+".csv")
            if tipologia=='affluenza':
                #nel caso dell'affluenza i dati li prendiamo dal file partito.csv
                df=pd.read_csv(path+"_partito.csv")
                df.rename(columns={'AFFLUENZA':'Voti'}, inplace=True)
            elif tipologia=='presidente':
                df=pd.read_csv(path+"_"+tipologia+".csv")
                df['Preisdente']=presidente
                df.rename(columns={presidente: 'Voti'}, inplace=True)
            elif tipologia=='candidato':
                df=pd.read_csv(path+"_"+tipologia+".csv")
                df = df[df["CANDIDATO"] == candidato]
                df.rename(columns={"PREFERENZE": 'Voti'}, inplace=True) 
            elif tipologia=='partito':
                df['Partito']=partito
                df.rename(columns={partito: 'Voti'}, inplace=True)

    elif piu_vot==True:
        value_to_subtract=-2
        #caso elezioni amministrative
        if com_mun is not None:
            df=pd.read_csv(path+"_"+tipologia+".csv")
            if tipologia=='partito' and municipio is not None:
                value_to_subtract=-3
            elif tipologia=='ballottaggio' and municipio is not None:
                value_to_subtract=-3
        #caso elezioni camera
        elif elezione=='camera':
            df=pd.read_csv(path)
        #caso elezioni regionali
        elif elezione=='regionali':
            df=pd.read_csv(path+"_"+tipologia+".csv")
            if tipologia=='presidente':
                value_to_subtract=-3

        #trova per ogni sezione il candidato/sindaco/presidente/partito piu votato, salvalo in una colonna "piu votato" e in una "voti" i suoi voti
        df["Più votato"] = df.iloc[:, 1:value_to_subtract].idxmax(axis=1)
        df["Voti"] = df.iloc[:, 1:value_to_subtract].max(axis=1)

    return (df)
    


def find_partiti(anno, elezione, com_mun=None, municipio=None):
    path=func_path(anno, elezione, com_mun, municipio)
    subtract=-2
    #caso elezioni amministrative
    if com_mun is not None:
        path=path+"_partito.csv"
        if municipio is not None:
            subtract=-3

    #caso elezioni camera o regionali
    elif elezione=='regionali':
        path=path+"_partito.csv"

    df = pd.read_csv(path)
    header = df.columns[1:subtract].tolist()  
    header.insert(0,'Più votato')

    return header


def find_candidati(anno, elezione, partito, com_mun=None, municipio=None):
    path=func_path(anno, elezione, com_mun, municipio)
    #caso elezioni amministrative o regionali
    if com_mun is not None or elezione=='regionali':
        path=path+"_candidato.csv"
        
    df = pd.read_csv(path)
    distinct_candidati = df.drop_duplicates(subset='CANDIDATO')[['LISTA', 'CANDIDATO']]
    filtered_df = distinct_candidati[df["LISTA"] == partito]
    distinct_candidati = filtered_df["CANDIDATO"].unique().tolist()
    return distinct_candidati

def find_sindaci(anno, elezione, tipologia, com_mun=None, municipio=None):
    path=func_path(anno, elezione, com_mun, municipio)
    path=path+"_"+tipologia+".csv"
    df = pd.read_csv(path)
    header = df.columns[1:-2].tolist()  
    header.insert(0,'Più votato')
    return header



#SIDEBAR SCELTA ELEZIONE
anno = st.sidebar.selectbox('Scegli l\'anno',['2021','2022','2023'])
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

com_mun=None
piu_vot=False
affl=False


#caso elezioni regionali
if elezione=='regionali':
    tipologia=st.sidebar.selectbox('Che dato ti interessa?', ['affluenza', 'presidente', 'partito', 'candidato'])
    if tipologia =='affluenza':
        affl=True
        data=dati(piu_vot, anno, elezione, tipologia)
    elif tipologia == 'candidato':
        values=find_partiti(anno, elezione)
        values.pop(0)
        partito=st.sidebar.selectbox('Seleziona il partito',values)
        values=find_candidati(anno, elezione, partito)
        candidato=st.sidebar.selectbox('Seleziona il candidato',values)
        data=dati(piu_vot, anno, elezione, tipologia, candidato=candidato)
    elif tipologia == 'presidente':
        values=find_sindaci(anno, elezione, tipologia)
        presidente=st.sidebar.selectbox('Seleziona', values)
        if presidente=='Più votato':
            piu_vot=True
            data=dati(piu_vot, anno, elezione, tipologia)
        else:
            data=dati(piu_vot, anno, elezione, tipologia, presidente=presidente)
    elif tipologia == 'partito':
        values=find_partiti(anno, elezione)
        partito=st.sidebar.selectbox('Seleziona', values)
        if partito=='Più votato':
            piu_vot=True
            data=dati(piu_vot, anno, elezione, tipologia)
        else:
            data=dati(piu_vot, anno, elezione, tipologia, partito=partito)

#caso elezioni camera
elif elezione=='camera':
    com_mun=None
    piu_vot=False
    affl=False
    tipologia=st.sidebar.selectbox('Che dato ti interessa?', ['affluenza','partito'])

    if tipologia =='affluenza':
        affl=True
        data=dati(piu_vot, anno, elezione, tipologia)
    else:
        values=find_partiti(anno, elezione)
        partito=st.sidebar.selectbox('Seleziona', values)
        if partito=='Più votato':
            piu_vot=True
            data=dati(piu_vot, anno, elezione, tipologia)
        else:
            data=dati(piu_vot, anno, elezione, partito=partito)


#caso elezioni amministrative
elif elezione=='amministrative':
    #selezione elezione municipale o comunale
    com_mun=st.sidebar.selectbox('Municipali o comunali?',['comunali', 'municipali'])
    if com_mun=='municipali':
        municipio=st.sidebar.selectbox('Seleziona il municipio', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
        tipologia=st.sidebar.selectbox('Che dato ti interessa?', ['affluenza','presidente','partito','candidato', 'ballottaggio'])
    else:
        tipologia=st.sidebar.selectbox('Che dato ti interessa?', ['affluenza','sindaco','partito','candidato', 'ballottaggio'])
        municipio=None
    
    if tipologia == 'affluenza':
        turno=st.sidebar.selectbox('Primo turno o ballottaggio?', ['primo turno', 'ballottaggio'])
        data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio)
        affl=True
    elif tipologia == 'candidato':
        values=find_partiti(anno, elezione, com_mun, municipio)
        values.pop(0)
        partito=st.sidebar.selectbox('Seleziona il partito',values)
        values=find_candidati(anno, elezione, partito, com_mun, municipio)
        candidato=st.sidebar.selectbox('Seleziona il candidato',values)
        data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio, candidato=candidato)
    elif tipologia == 'presidente':
        values=find_sindaci(anno, elezione, tipologia, com_mun, municipio)
        presidente=st.sidebar.selectbox('Seleziona', values)
        if presidente=='Più votato':
            piu_vot=True
            data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio)
        else:
            data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio, presidente=presidente)
    elif tipologia == 'sindaco':
        values=find_sindaci(anno, elezione, tipologia, com_mun, municipio)
        sindaco=st.sidebar.selectbox('Seleziona', values)
        if sindaco=='Più votato':
            piu_vot=True
            data=dati(piu_vot, anno, elezione, tipologia, com_mun)
        else:
            data=dati(piu_vot, anno, elezione, tipologia, com_mun, sindaco=sindaco)
    elif tipologia == 'partito':
        values=find_partiti(anno, elezione, com_mun, municipio)
        partito=st.sidebar.selectbox('Seleziona', values)
        if partito=='Più votato':
            piu_vot=True
            data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio)
        else:
            data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio, partito=partito)
    elif tipologia == 'ballottaggio':
        piu_vot=True
        data=dati(piu_vot, anno, elezione, tipologia, com_mun, municipio)


#qui il main
#cambio i nomi dei sindaci/partiti con standard
data = data.rename(columns=standard)
if piu_vot==True:
    for row_index in range(len(data)):
        value = data.loc[row_index, "Più votato"]
        if value in standard:
            data.loc[row_index, "Più votato"] = standard[value]


left_column, right_column = st.columns([0.75, 0.2])

if elezione=='camera' or com_mun=='comunali' or elezione=='regionali':
            selezione=st.sidebar.selectbox('Vuoi visualizzare la mappa di tutta Roma o di un singolo municipio?', ['Tutta Roma', 'Municipio 1', 'Municipio 2', 'Municipio 3', 'Municipio 4', 'Municipio 5', 'Municipio 6', 'Municipio 7', 'Municipio 8', 'Municipio 9', 'Municipio 10', 'Municipio 11', 'Municipio 12', 'Municipio 13', 'Municipio 14', 'Municipio 15'])
            values_municipi={'Tutta Roma':0, 'Municipio 1': 1, 'Municipio 2': 2, 'Municipio 3': 3, 'Municipio 4': 4, 'Municipio 5': 5, 'Municipio 6': 6, 'Municipio 7': 7, 'Municipio 8': 8, 'Municipio 9': 9, 'Municipio 10': 10, 'Municipio 11': 11, 'Municipio 12': 12, 'Municipio 13': 13, 'Municipio 14': 14, 'Municipio 15':15}
            municipio = values_municipi[selezione]

#bottone per far partire il download solo dopo la selezione 
boolean = st.sidebar.button('Invia')
if not boolean:
    st.header('Tool grafico dati elettorali di Roma')
    st.write('Seleziona un\'elezione nel menu a sinistra')

if boolean:
    with left_column:
        #coordinate dei centroidi dei municipi. Start from 0=tutta roma
        centroids={'Lon':[12.4964,12.4770581,12.4917441, 12.5301001, 12.5403471, 12.5565151, 12.6148051, 12.5171351, 
                        12.4819491, 12.4601261, 12.2868461, 12.4467971, 12.4584861, 12.4129485, 12.4089303, 12.4478257], 
                'Lat': [41.9028, 41.8963649, 41.919371, 41.941734, 41.908605, 41.8851969, 41.8827769, 41.8783239, 
                        41.8653769, 41.81898, 41.743652, 41.852685, 41.8771455, 41.8974907, 41.9254917, 41.943352]}
        
        latitude= centroids['Lat'][municipio]
        longitude=centroids['Lon'][municipio]
        
        sezioni_elettorali = gpd.read_file(path_folder+"sezioni_elettorali/tutta_roma.shp")

        #centroidi delle sezioni elettorali
        sezioni_elettorali['Lat']=sezioni_elettorali.geometry.centroid.y
        sezioni_elettorali['Lon']=sezioni_elettorali.geometry.centroid.x

        borders_municipi=gpd.read_file(path_folder+"borders_municipi/borders_municipi.shp")

        #caso comunali e visualizzazione di tutta roma
        if municipio==0:
            zoom=10
            opacity=0.5
            #nel caso di tutta roma il layer 1 è dato dalle sezioni elettorali
            layer1 = pd.merge(sezioni_elettorali, data, left_on="sezione", right_on="SEZIONE")

        #caso visualizzazione di un solo municipio
        else:
            zoom=13
            opacity=1
            buildings = gpd.read_file(path_folder+"buildings/buildings_municipio_"+str(municipio)+".shp")
            #prendiamo i palazzi e le sezioni solo del municipio
            buildings=buildings[buildings['municipio']==municipio]
            sezioni_elettorali=sezioni_elettorali[sezioni_elettorali['municipio']==municipio]
            #il layer1 in questo caso sono i palazzi
            layer1 = pd.merge(buildings, data, left_on="sezione", right_on="SEZIONE")

        #def max, min, median
        max = layer1["Voti"].max()
        min = layer1["Voti"].min()
        median = layer1["Voti"].median()

        #def colori per scala graduata
        color_scale = [[255, 255, 255, 100],  # White
            [0, 0, 255, 100],      # Blue
            [255, 0, 0, 100]       # Red
            ]
        
        #funzione che scala i colori tra bianco e rosso (scala tra color_scale, basta cambiare li per cambiare gli estremi)
        def get_fill_color(v):
                if pd.isna(v):
                    return [0, 0, 0, 0]  
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
        
        #caso affluenza, valori tra 0 e 1, applicare scala graduata
        if affl==True:
            #aggiungi una colonna per i colori e una per il voto percentuale
            layer1['fill_color'] = layer1['Voti'].apply(get_fill_color)
            layer1['voti_percent'] = layer1['Voti'].apply(lambda x: f'{x:.2%}')

            #cosa visualizzare quando passi sopra con il mouse
            tooltip = {
                    "html": "<b>Sezione:</b> {SEZIONE}<br> <b>Affluenza:</b> {voti_percent}<br> ",
                    "style": {
                        "backgroundColor": "white",
                        "color": "black"
                        },
                    "layer": 0
                }

            #qui la legenda
            legend_html = "<table style='border-collapse: collapse;'>"
            legend_html += "<tr>"
            legend_html += "<td style='text-align: left; color: white;'> Affluenza: {:.2%}</td>".format(min)
            legend_html += "<td style='text-align: center; color: blue;'> Affluenza: {:.2%}</td>".format(median)
            legend_html += "<td style='text-align: right; color: red;'> Affluenza: {:.2%}</td>".format(max)
            legend_html += "</tr>"
            legend_html += "<tr>"
            legend_html += "<td colspan='3' style='height: 20px; width: 500px; background: linear-gradient(to right, "
            for i, color in enumerate(color_scale):
                legend_html += f"rgba({color[0]}, {color[1]}, {color[2]}, {i / (len(color_scale) - 1)}), "
            legend_html = legend_html.rstrip(", ")
            legend_html += ");'></td>"
            legend_html += "</tr>"
            legend_html += "</table>"
            st.markdown(legend_html, unsafe_allow_html=True)
            

        #caso specifico candidato/presidente/partito
        elif piu_vot==False:
            #Aggiungiamo una colonna valori normalizzati (se tutti i valori sono uguali ritorniamo 0)
            if max != 0:
                layer1['normalized_voti'] = layer1['Voti'] / max
            else:
                layer1['normalized_voti'] = 0
            
            layer1['fill_color'] = layer1['normalized_voti'].apply(get_fill_color)
            tooltip = {
                    "html": "<b>Sezione:</b> {SEZIONE}<br> <b>Voti:</b> {Voti}<br> ",
                    "style": {
                        "backgroundColor": "white",
                        "color": "black"
                        },
                    "layer": 0
                }
            
            #qui la legenda
            legend_html = "<table style='border-collapse: collapse;'>"
            legend_html += "<tr>"
            legend_html += "<td style='text-align: left; color: white;'>{} voti</td>".format(int(min))
            legend_html += "<td style='text-align: center; color: blue;'>{} voti</td>".format(int(median))
            legend_html += "<td style='text-align: right; color: red;'>{} voti</td>".format(int(max))
            legend_html += "</tr>"
            legend_html += "<tr>"
            legend_html += "<td colspan='3' style='height: 20px; width: 500px; background: linear-gradient(to right, "
            for i, color in enumerate(color_scale):
                legend_html += f"rgba({color[0]}, {color[1]}, {color[2]}, {i / (len(color_scale) - 1)}), "
            legend_html = legend_html.rstrip(", ")
            legend_html += ");'></td>"
            legend_html += "</tr>"
            legend_html += "</table>"
            st.markdown(legend_html, unsafe_allow_html=True)
            
           
        
        #caso piu votato
        else:
            predefined_colors = {
                "Red": [255, 0, 0, 100],
                "Green": [0, 255, 0, 100],
                "Blue": [0, 0, 255, 100],
                "Purple": [128, 0, 128, 100],
                "Yellow": [255, 255, 0, 100],
                "Blue2": [0, 0, 139, 100],
                "Blue3": [152,245,255,100]
            }

            distinct_values = layer1['Più votato'].unique()

            color_dictionary = {'MICHETTI': 'Blue', 'GUALTIERI': 'Red', 'CALENDA': 'Purple', 'RAGGI': 'Yellow',
                                'D\'AMATO':'Red', 'ROCCA': 'Blue',
                             'FRATELLI D\'ITALIA': 'Blue', 'PARTITO DEMOCRATICO': 'Red', 'AZIONE': 'Purple', 'AZIONE ITALIA VIVA': 'Purple',
                             'MOVIMENTO 5 STELLE': "Yellow", 'LEGA': 'Blue2', 'FORZA ITALIA': 'Blue3'}
            color_mapping={}

            for name in distinct_values:
                if name in color_dictionary:
                    color_mapping[name]=predefined_colors[color_dictionary[name]]
            
            def get_fill_color(p):
                return color_mapping.get(p['Più votato'], [255, 255, 255, 100])  # Default to white color if value not found
            
            layer1['fill_color'] = layer1.apply(get_fill_color, axis=1)

            tooltip = {
                "html": "<b>Sezione:</b> {SEZIONE}<br> <b>Più votato:</b> {Più votato}<br> ",
                "style": {
                    "backgroundColor": "white",
                    "color": "black"
                }
            }
            #qui la legenda
            legend_html = "<div>"
            legend_html += "<table>"
            legend_html += "<tr>"
            for value, color in color_mapping.items():
                if value in color_dictionary:
                    color_string = f"rgba({color[0]}, {color[1]}, {color[2]}, {color[3]/255})"
                    legend_html += f"<td style='text-align: center;'>"
                    legend_html += f"<span style='color: white;'>{value}</span>"
                    legend_html += f"<div style='width: 100px; height: 10px; background-color: {color_string};'></div>"
                    legend_html += "</td>"
            legend_html += "</tr>"
            legend_html += "</table>"
            legend_html += "</div>"
            st.markdown(legend_html, unsafe_allow_html=True)


        Layer0 = pdk.Layer(
            "GeoJsonLayer",
            data=sezioni_elettorali,
            get_line_color=[0, 0, 0],  # Black border color
            filled=False,
            stroked=True,
            auto_highlight=True,
            pickble=True,
            line_width_min_pixels=0.5,
        )
        Layer1 = pdk.Layer(
            "GeoJsonLayer",
            data=layer1,
            get_fill_color='fill_color',
            auto_highlight=True,
            opacity=opacity,
            pickable=True,
        )
        Layer2 = pdk.Layer(
            "GeoJsonLayer",
            data=borders_municipi,
            get_fill_color=[0, 0, 0, 0],  # Transparent fill color
            get_line_color=[255, 0, 0, 100],  # Red border color
            filled=True,
            stroked=True,
            extruded=False,
            wireframe=False,
            line_width_min_pixels=2,
        )
        # Create a view state to set the initial map center and zoom level
        view_state = pdk.ViewState(
            latitude= latitude,
            longitude= longitude,
            zoom=zoom,
        )
        # Create the Deck object with the layer and view state
        deck = pdk.Deck(
            layers=[Layer0, Layer1, Layer2], 
            initial_view_state=view_state, 
            map_style="mapbox://styles/nathclay1/clilc9k49006w01r82tvm8ud2",
            tooltip=tooltip
        )
        st.pydeck_chart(deck)

    with right_column:
        if affl==True:
            layer1 = layer1.drop_duplicates(subset=(['sezione']))
            layer1['Voti']=(layer1['Voti'].fillna(0)*100).round(2).astype(str)+"%"
            layer1.rename(columns={'Voti': 'Affluenza'}, inplace=True) 
            st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
            st.write('Clicca su una colonna per ordinarla')
            st.dataframe(layer1[['SEZIONE', 'municipio', 'Affluenza']], hide_index=True,use_container_width=True)
        elif piu_vot==False:
            layer1 = layer1.drop_duplicates(subset=(['sezione']))
            st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
            st.write('Clicca su una colonna per ordinarla')
            st.dataframe(layer1[['SEZIONE', 'municipio', 'Voti']], width=200, hide_index=True,use_container_width=True)

        elif piu_vot==True:
            layer1 = layer1.drop_duplicates(subset=(['sezione']))
            st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
            st.write('Clicca su una colonna per ordinarla')
            st.dataframe(layer1[['SEZIONE', 'municipio', 'Più votato']], width=200, hide_index=True,use_container_width=True)
    


    

