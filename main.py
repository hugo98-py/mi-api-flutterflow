# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:37:45 2025

@author: Hugo
"""
""" Este codigo lo uso para hacer la primera prueba de convert JSON to Data Type en FF. Para esto
necesito una API cualquiera que me entregue un JSON cualquiera para simplemente usar en la conversion
de JSON to Data Type"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Row(BaseModel):
    column1: str
    column2: int
    column3: float

class Table(BaseModel):
    data: List[Row]

# Predefined dummy data: 3 columns, 5 rows
dummy_data = Table(data=[
    Row(column1="A", column2=10, column3=1.1),
    Row(column1="B", column2=20, column3=2.2),
    Row(column1="C", column2=30, column3=3.3),
    Row(column1="D", column2=40, column3=4.4),
    Row(column1="E", column2=50, column3=5.5),
])

@app.get("/dummy", response_model=Table)
async def get_dummy_data():
    """
    Devuelve un JSON con 3 columnas y 5 filas de datos de ejemplo.
    """
    return dummy_data

# Para ejecutar:
# uvicorn main:app --reload
