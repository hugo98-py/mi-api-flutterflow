# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:37:45 2025

@author: Hugo
"""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openpyxl import load_workbook
import uuid
import os

app = FastAPI()

# Modelo de entrada
class DatosEntrada(BaseModel):
    nombre: str = "Sin nombre"
    edad: int | str = "N/A"

@app.post("/generar-excel/")
async def generar_excel(data: DatosEntrada):
    nombre = data.nombre
    edad = data.edad

    # Cargar plantilla
    plantilla_path = "plantilla.xlsx"
    wb = load_workbook(plantilla_path)
    ws = wb.active

    # Escribir los datos
    ws["A1"] = "Nombre"
    ws["B1"] = "Edad"
    ws["A2"] = nombre
    ws["B2"] = edad

    # Guardar el archivo temporalmente
    archivo_temp = f"{uuid.uuid4()}.xlsx"
    wb.save(archivo_temp)

    # Devolverlo como archivo descargable
    return FileResponse(
        archivo_temp,
        filename="reporte.xlsx",
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
