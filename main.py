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

app = FastAPI()

@app.get("/convert-excel-to-json/")
async def convert_excel_to_json():
    cwd = os.getcwd()
    os.chdir(cwd)
    ruta_excel = "BD_FV_copia.xlsx"  

    try:
        df = pd.read_excel(ruta_excel, engine='openpyxl')
        df_clean = df.where(pd.notnull(df), None)  # <--- esta línea soluciona tu error
        datos_json = df_clean.to_dict(orient='records')
        return JSONResponse(content=datos_json)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
