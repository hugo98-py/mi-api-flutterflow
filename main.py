from pathlib import Path
from typing import Literal
import logging, unicodedata, pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Excel-to-JSON API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # cámbialo en producción
    allow_methods=["GET"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
RUTAS_EXCEL = {
    "fauna":    BASE_DIR / "BD_Fauna.xlsx",
    "flora":    BASE_DIR / "BD_Flora.xlsx",
    "usuarios": BASE_DIR / "BD_usuarios.xlsx",
}

def quitar_tildes(texto: str) -> str:
    return (unicodedata.normalize("NFKD", texto)
            .encode("ASCII", "ignore")
            .decode("utf-8")) if isinstance(texto, str) else texto

@app.get(
    "/convert-excel-to-json/{categoria}/",
    summary="Convierte un Excel a JSON",
    description="Valores válidos: flora, fauna, usuarios",
    response_model=list[dict]
)
async def convert_excel_to_json(categoria: Literal["flora", "fauna", "usuarios"]):
    ruta_excel = RUTAS_EXCEL[categoria]

    if not ruta_excel.exists():
        raise HTTPException(404, f"El archivo '{ruta_excel.name}' no existe.")

    try:
        df = await run_in_threadpool(pd.read_excel, ruta_excel, engine="openpyxl")
        df = await run_in_threadpool(df.applymap, quitar_tildes)

        cols = [(quitar_tildes(c).strip().replace(" ", "_") if isinstance(c, str) else None)
                for c in df.columns]

        if len(set(filter(None, cols))) != len(list(filter(None, cols))):
            raise RuntimeError("Columnas duplicadas tras la limpieza.")

        df.columns = cols
        df = df.loc[:, [c for c in df.columns if c]]

        datos = df.where(pd.notnull(df), None).to_dict(orient="records")
        return JSONResponse(content=datos)

    except Exception:
        logging.exception("Error procesando %s", ruta_excel)
        raise HTTPException(500, "Error interno procesando el archivo.")

