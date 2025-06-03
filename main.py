# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:37:45 2025
@author: Hugo
"""
""" En este codigo se usa una versiona mas avanzada que la anterior, en donde se importa el archivo ecxel 
con las BD de pruebas y se exporta el JSON con GET. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import os 
import unicodedata

app = FastAPI()

@app.get("/convert-excel-to-json/")
async def convert_excel_to_json():
    cwd = os.getcwd()
    os.chdir(cwd)
    ruta_excel = "BD_FV_copia.xlsx"  

    # Función para quitar tildes 
    def quitar_tildes(texto):
        if isinstance(texto, str):
            return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
        return texto  # Si no es string, no lo modifica

    # Leer el archivo original
    df = pd.read_excel(ruta_excel, engine='openpyxl')

    # Aplicar la función a todo el DataFrame (celdas y nombres de columnas)
    df_sin_tildes = df.applymap(quitar_tildes)
    df_sin_tildes.columns = [quitar_tildes(col) for col in df.columns]
    
    try:
        df_clean = df_sin_tildes.where(pd.notnull(df_sin_tildes), None)  # <--- esta línea maneja los datos nan y otros y los reemplaza por "None".
        datos_json = df_clean.to_dict(orient='records')
        return JSONResponse(content=datos_json)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
