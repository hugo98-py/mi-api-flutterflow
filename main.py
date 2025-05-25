# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:37:45 2025

@author: Hugo
""" En este codigo se usa una versiona mas avanzada que la anterior, en donde se importa el archivo ecxel 
con las BD de pruebas y se exporta el JSON con GET. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()

@app.get("/convert-excel-to-json/")
async def convert_excel_to_json():
    """
    Lee un archivo Excel del servidor, lo convierte a JSON y lo retorna.
    """
    ruta_excel = "plantilla_BD.xlsx"  # Asegúrate de que esté en la misma carpeta o da la ruta completa

    try:
        df = pd.read_excel(ruta_excel, engine='openpyxl')
        datos_json = df.to_dict(orient='records')
        return JSONResponse(content=datos_json)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
