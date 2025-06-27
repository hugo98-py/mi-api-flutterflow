# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 16:26:18 2025

@author: Hugo
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import unicodedata
import os 

path_planillas = os.getcwd()

app = FastAPI()

# 👉 Ajusta aquí las rutas a tus archivos ----------------------------
RUTAS_EXCEL = {
    "fauna":    os.path.join(path_planillas, "BD_Fauna.xlsx"),
    "flora":    os.path.join(path_planillas, "BD_Flora.xlsx"),
    "usuarios": os.path.join(path_planillas, "BD_usuarios.xlsx"),
}
# -------------------------------------------------------------------

def quitar_tildes(texto: str) -> str:
    """Elimina tildes y diacríticos de una cadena."""
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ASCII", "ignore")
        .decode("utf-8")
        if isinstance(texto, str)
        else texto
    )

@app.get("/convert-excel-to-json/{categoria}/")
async def convert_excel_to_json(categoria: str):
    """
    Convierte el Excel correspondiente a *categoria* en JSON.
    Los valores válidos para *categoria* son: flora, fauna, usuarios.
    """
    # 1) Elegir la ruta correcta
    ruta_excel = RUTAS_EXCEL.get(categoria.lower())
    if ruta_excel is None:
        raise HTTPException(
            status_code=400,
            detail=f"Categoría '{categoria}' no reconocida. Usa flora, fauna o usuarios."
        )

    ruta_excel = Path(ruta_excel)

    # 2) Verificar que el archivo exista
    if not ruta_excel.exists():
        raise HTTPException(
            status_code=404,
            detail=f"El archivo '{ruta_excel}' no existe. Revisa la ruta en RUTAS_EXCEL."
        )

    try:
        # 3) Leer y limpiar el archivo
        df = pd.read_excel(ruta_excel, engine="openpyxl").applymap(quitar_tildes)

        # 4) Limpiar nombres de columnas
        columnas_limpias = [
            (quitar_tildes(col).strip().replace(" ", "_") if isinstance(col, str) else None)
            for col in df.columns
        ]
        df.columns = columnas_limpias                       # asigna columnas limpias
        df = df.loc[:, [col for col in df.columns if col]]   # descarta vacías

        # 5) Reemplazar NaN por None para compatibilidad JSON
        datos_json = df.where(pd.notnull(df), None).to_dict(orient="records")
        return JSONResponse(content=datos_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
