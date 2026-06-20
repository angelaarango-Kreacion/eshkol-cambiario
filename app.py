import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import urllib.request
import json
import altair as alt
import io
import base64

# =========================================================================
# 🚨 1. CONFIGURACIÓN GLOBAL DE STREAMLIT (PRIMERA LÍNEA OBLIGATORIA)
# =========================================================================
st.set_page_config(
    page_title="Control Financiero - Eshkol Premium", 
    page_icon="🌿", 
    layout="wide"
)

# --- Instalación e importación automática de dependencias críticas ---
try:
    import pypdf
except ImportError:
    os.system("pip install pypdf")
    import pypdf

try:
    import openpyxl
except ImportError:
    os.system("pip install openpyxl")
    import openpyxl

# =========================================================================
# 🖼️ PROCESAMIENTO SEGURO DE RECURSOS GRÁFICOS (BASE64)
# =========================================================================
imagen_fondo_64 = ""
if os.path.exists("1.png"):
    try:
        with open("1.png", "rb") as f:
            imagen_fondo_64 = base64.b64encode(f.read()).decode()
    except:
        pass

nombres_posibles = ["logo.png", "logo.PNG", "logo.png.png", "logo.jpg", "LOGO FONDO NEGRO.jpg"]
logo_base64 = ""

for nombre in nombres_posibles:
    if os.path.exists(nombre):
        try:
            with open(nombre, "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
        except:
            pass
        break

# =========================================================================
# 🎨 INYECCIÓN DE ESTILOS CSS CLEAN-PREMIUM CORPORATIVOS
# =========================================================================
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAF9;
    }
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    .main .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    .banner-container {
        position: relative;
        width: 100%;
        height: 280px;
        background-size: cover;
        background-position: center;
        border-bottom: 5px solid #39B54A;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        display: flex;
        align-items: center;
        padding-left: 4%;
        box-sizing: border-box;
    }
    .banner-overlay-premium {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(22,37,27,1) 0%, rgba(22,37,27,1) 45%, rgba(22,37,27,0.85) 70%, rgba(0,0,0,0) 100%);
        z-index: 1;
    }
    .header-overlay-content {
        position: relative;
        z-index: 10;
        width: 92%;
    }
    .brand-divider-fixed {
        width: 3px;
        height: 90px;
        background-color: #39B54A;
        box-shadow: 0px 0px 8px rgba(57, 181, 74, 0.5);
    }
    .text-titles-block {
        color: #FFFFFF !important;
        font-family: sans-serif !important;
    }
    .app-main-title {
        font-size: 2.4rem !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        line-height: 1.15 !important;
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .app-sub-title {
        font-size: 0.95rem !important;
        color: #39B54A !important;
        font-weight: 700 !important;
        margin-top: 8px !important;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .eshkol-body {
        padding: 2.5rem 4rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: #16251b !important;
    }
    [data-testid="stMetricLabel"] {
        color: #556B5C !important;
        font-weight: 600;
        text-transform: uppercase;
    }
    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        color: #556B5C !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0.8rem 1.2rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #16251b !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #39B54A !important;
    }
    div.stButton > button {
        background-color: rgba(57, 181, 74, 0.03) !important;
        color: #16251b !important;
        font-weight: 600 !important;
        border: 1.5px solid rgba(22, 37, 27, 0.25) !important;
        padding: 0.6rem 1.8rem !important;
        border-radius: 6px !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #16251b !important;
        color: #FFFFFF !important;
        border-color: #16251b !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 🌿 MONTAJE INTEGRADO DEL BANNER Y STRIP CORPORATIVO
# =========================================================================
url_fondo = f"data:image/png;base64,{imagen_fondo_64}" if imagen_fondo_64 else ""
url_logo = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

html_banner = f"""
<div class="banner-container" style="background-image: url('{url_fondo}'); background-color: #16251b;">
    <div class="banner-overlay-premium"></div>
    <div class="header-overlay-content">
        <div style="display: flex; align-items: center; gap: 25px;">
"""

if logo_base64:
    html_banner += f'        <img src="{url_logo}" style="width: 170px; height: auto; max-height: 110px; object-fit: contain;" />'
    html_banner += '        <div class="brand-divider-fixed"></div>'

html_banner += """
            <div class="text-titles-block">
                <h1 class="app-main-title">CONTROL FINANCIERO<br>Y CAMBIARIO</h1>
                <p class="app-sub-title">ESHKOL PREMIUM S.A.S &nbsp;|&nbsp; MÓDULO CONTABLE v2.6</p>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(html_banner, unsafe_allow_html=True)

st.markdown('<div class="eshkol-body">', unsafe_allow_html=True)

FILE_TRM = "trm_almacen.txt"
FILE_GASTOS = "gastos_almacen.txt"

# =========================================================================
# 📈 MOTOR DE SINCRONIZACIÓN TRM MASIVA
# =========================================================================
def cargar_trm_locales():
    dicc = {}
    if os.path.exists(FILE_TRM):
        with open(FILE_TRM, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 2:
                    try:
                        dicc[partes[0]] = float(partes[1])
                    except:
                        pass
    return dicc

def guardar_trm_locales(dicc):
    with open(FILE_TRM, "w", encoding="utf-8") as f:
        for fecha in sorted(dicc.keys()):
            f.write(f"{fecha};{dicc[fecha]}\n")

def sincronizar_trm_en_bloque():
    dicc = cargar_trm_locales()
    try:
        url = "https://datos.gov.co/resource/mcec-87by.json?$order=vigenciadesde%20DESC&$limit=150"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as response:
            datos = json.loads(response.read().decode('utf-8'))
            for reg in datos:
                if 'valor' in reg and 'vigenciadesde' in reg and 'vigenciahasta' in reg:
                    valor = float(reg['valor'])
                    f_desde = reg['vigenciadesde'].split('T')[0]
                    f_hasta = reg['vigenciahasta'].split('T')[0]
                    
                    dt_desde = datetime.strptime(f_desde, "%Y-%m-%d")
                    dt_hasta = datetime.strptime(f_hasta, "%Y-%m-%d")
                    
                    paso = dt_desde
                    while paso <= dt_hasta:
                        dicc[paso.strftime("%Y-%m-%d")] = valor
                        paso += timedelta(days=1)
        guardar_trm_locales(dicc)
    except:
        pass
    return dicc

def obtener_trm_inteligente(dicc, fecha_str):
    if fecha_str in dicc and dicc[fecha_str] > 1000:
        return dicc[fecha_str]
    try:
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        for i in range(1, 15):
            f_ant = (dt -
