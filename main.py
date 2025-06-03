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
        return texto

    try:
        # Leer el archivo original
        df = pd.read_excel(ruta_excel, engine='openpyxl')

        # Quitar tildes de celdas
        df = df.applymap(quitar_tildes)

        # Limpiar nombres de columnas
        columnas_limpias = []
        for col in df.columns:
            if isinstance(col, str):
                col_limpio = quitar_tildes(col).strip().replace(" ", "_")
                columnas_limpias.append(col_limpio if col_limpio else None)
            else:
                columnas_limpias.append(None)

        # Asignar nombres temporales
        df.columns = columnas_limpias

        # Eliminar columnas con nombre vacío o None
        df = df.loc[:, [col for col in df.columns if col]]

        # Reemplazar NaN por None para JSON válido
        df_clean = df.where(pd.notnull(df), None)
        datos_json = df_clean.to_dict(orient='records')
        return JSONResponse(content=datos_json)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
