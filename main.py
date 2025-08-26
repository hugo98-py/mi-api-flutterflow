# -*- coding: utf-8 -*-
"""
Excel-to-JSON API 100 % FlutterFlow-Friendly
"""
from pathlib import Path
from typing import Literal
import logging, unicodedata, re, pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Excel-to-JSON API")

# ──────────────────────────────────── CORS ────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # ¡pon tu dominio en producción!
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ─────────────────────────────── Config rutas ────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
RUTAS_EXCEL = {
    "fauna":    BASE_DIR / "BD_Fauna.xlsx",
    "flora":    BASE_DIR / "BD_Flora.xlsx",
    "usuarios": BASE_DIR / "BD_usuarios.xlsx",
}

# ─────────────────────────── util: quitar tildes ─────────────────────────────
def quitar_tildes(texto: str) -> str:
    return (unicodedata.normalize("NFKD", texto)
            .encode("ASCII", "ignore")
            .decode("utf-8")) if isinstance(texto, str) else texto

# ───────────── util: sanitizar nombres de columnas (sin __ dobles) ───────────
def sanitizar_nombre(campo) -> str | None:
    if not isinstance(campo, str):
        return None
    s = quitar_tildes(campo).strip()
    # 1) cualquier no-alfa-numérico (incl. espacio y punto) → "_"
    s = re.sub(r"[^\w]", "_", s, flags=re.ASCII)   # \w = [A-Za-z0-9_]
    # 2) colapsar múltiples "_" → "_"
    s = re.sub(r"_+", "_", s)
    # 3) quitar "_" al inicio/fin
    s = s.strip("_")
    # (opcional) forzar minúsculas:
    # s = s.lower()
    return s or None

# ──────────────────────────────── ENDPOINT ───────────────────────────────────
@app.get(
    "/convert-excel-to-json",
    summary="Convierte un Excel a JSON",
    description="Valores válidos para 'categoria': flora, fauna, usuarios",
    response_model=list[dict],
)
async def convert_excel_to_json(
    categoria: Literal["flora", "fauna", "usuarios"] = Query(..., description="Tipo de BD")
):
    """Devuelve el Excel correspondiente convertido a JSON."""
    ruta_excel = RUTAS_EXCEL[categoria]

    if not ruta_excel.exists():
        raise HTTPException(404, f"El archivo '{ruta_excel.name}' no existe.")

    try:
        # 1) Leer y limpiar en un thread (NO bloquea el event-loop)
        df = await run_in_threadpool(pd.read_excel, ruta_excel, engine="openpyxl")
        df = await run_in_threadpool(df.applymap, quitar_tildes)

        # 2) Limpiar nombres de columnas (sin dobles guiones bajos)
        cols = [sanitizar_nombre(c) for c in df.columns]

        if len(set(filter(None, cols))) != len(list(filter(None, cols))):
            raise RuntimeError("Columnas duplicadas tras la limpieza.")

        df.columns = cols
        df = df.loc[:, [c for c in df.columns if c]]  # descarta vacías

        # 3) NaN → None y a JSON
        datos = df.where(pd.notnull(df), None).to_dict(orient="records")
        return JSONResponse(content=datos)

    except Exception:
        logging.exception("Error procesando %s", ruta_excel)
        raise HTTPException(500, "Error interno procesando el archivo.")



