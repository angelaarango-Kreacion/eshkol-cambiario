import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import urllib.request
import json
import io
import base64

# =========================================================================
# 🚨 1. CONFIGURACIÓN GLOBAL DE STREAMLIT (PREMIUM CLEAN-GREEN UI)
# =========================================================================
st.set_page_config(
    page_title="Control Financiero - Eshkol Premium", 
    page_icon="🌿", 
    layout="wide"
)

# --- Instalación e importación silenciosa de dependencias ---
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
# 🎨 INYECCIÓN DE ESTILOS CSS CLEAN-PREMIUM
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
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 🌿 MONTAJE DEL BANNER CORPORATIVO
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
                <p class="app-sub-title">ESHKOL PREMIUM S.A.S &nbsp;|&nbsp; MÓDULO CONTABLE v3.0</p>
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
# 📈 MOTOR DE TRM (CAPTURA HISTÓRICA SUI GENERIS)
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
            f_ant = (dt - timedelta(days=i)).strftime("%Y-%m-%d")
            if f_ant in dicc and dicc[f_ant] > 1000:
                return dicc[f_ant]
    except:
        pass
    return None

with st.spinner("Sincronizando pasarela cambiaria del Estado..."):
    trm_datos = sincronizar_trm_en_bloque()

fecha_hoy_dt = datetime.now()
fecha_hoy_str = fecha_hoy_dt.strftime("%Y-%m-%d")

# ==========================================
# 📅 CONTROL DE TIEMPO INDEPENDIENTE
# ==========================================
st.markdown("### 📅 Eje de Tiempo Sincronizado")
c_ano, c_mes, c_dia = st.columns(3)
ano_sel = c_ano.selectbox("Año de Consulta", list(range(2026, 2015, -1)))
mes_sel = c_mes.selectbox("Mes de Consulta", list(range(1, 13)), index=fecha_hoy_dt.month - 1)
dia_sel = c_dia.selectbox("Día de Consulta", list(range(1, 32)), index=fecha_hoy_dt.day - 1)

try: 
    fecha_base_dt = datetime(ano_sel, mes_sel, dia_sel)
except: 
    fecha_base_dt = datetime(ano_sel, mes_sel, 1)
fecha_base_str = fecha_base_dt.strftime("%Y-%m-%d")

trm_hoy = obtener_trm_inteligente(trm_datos, fecha_hoy_str)
trm_inspeccionada = obtener_trm_inteligente(trm_datos, fecha_base_str)

st.write(" ")
col_r1, col_r2 = st.columns(2)
with col_r1: 
    st.metric(label=f"🟢 TRM EN VIVO HOY ({fecha_hoy_dt.strftime('%d/%m/%Y')})", value=f"$ {trm_hoy:,.2f}" if trm_hoy else "CONECTANDO...")
with col_r2: 
    st.metric(label="🔵 TRM FECHA SELECCIONADA", value=f"$ {trm_inspeccionada:,.2f}" if trm_inspeccionada else "SIN REGISTRO")

# ==========================================
# 🗂️ PANELES OPERATIVOS CONTABLES
# ==========================================
st.write(" ")
tab0, tab1, tab2 = st.tabs(["📄 Procesar Extractos PDF", "💰 Registrar Gasto Manual", "📊 Consolidados"])

with tab0:
    st.subheader("🕵️‍♂️ Extractor Avanzado Davivenda (Auditoría Anti-Duplicación por Máquina de Estados)")
    archivos_pdf = st.file_uploader("Cargar extractos bancarios (.pdf)", type=["pdf"], accept_multiple_files=True)
    
    if archivos_pdf:
        gastos_encontrados_lote = []
        patron_fecha = re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b')
        patron_ach_flexible = re.compile(r'ACH\s*FEES', re.IGNORECASE)
        patron_minimum_flexible = re.compile(r'BELOW\s*(?:MINIMUM\s*)?BALANCE\s*FEES?', re.IGNORECASE)
        
        for archivo in archivos_pdf:
            try:
                lector = pypdf.PdfReader(archivo)
                for num_pag, pagina in enumerate(lector.pages):
                    texto_original = pagina.extract_text()
                    if not texto_original:
                        continue
                    
                    lineas_pag = texto_original.splitlines()
                    in_summary_zone = False  # Reinicia estado por página para evitar falsos arrastres
                    fecha_actual_tracker = None
                    
                    for idx, linea in enumerate(lineas_pag):
                        linea_upper = linea.upper()
                        
                        # A. DISPARADORES DE EXCLUSIÓN TOTAL (Zona de Resúmenes/Acumulados Contables)
                        indicadores_cierre = [
                            "TOTAL DR'S", "ANNUAL PERCENT", "OVERDRAFT AND RETURN", 
                            "YEAR-TO-DATE", "INTEREST-BEARING", "FEES DESCRIPTION"
                        ]
                        if any(ind in linea_upper for ind in indicadores_cierre):
                            in_summary_zone = True
                        
                        # Si la máquina de estados detectó que estamos en el resumen del final, se descarta todo
                        if in_summary_zone:
                            continue
                        
                        # B. SEGUIMIENTO CRONOLÓGICO DE LA LÍNEA
                        match_fecha = patron_fecha.search(linea)
                        if match_fecha:
                            mes, dia, ano = match_fecha.group(1), match_fecha.group(2), match_fecha.group(3)
                            if len(ano) == 2: ano = f"20{ano}"
                            fecha_actual_tracker = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                        
                        # C. EVALUACIÓN DE GASTOS REALES
                        es_ach = bool(patron_ach_flexible.search(linea_upper))
                        es_min = bool(patron_minimum_flexible.search(linea_upper))
                        
                        if es_ach or es_min:
                            # Asignar fecha cronológica o fallback seguro
                            fecha_gasto = fecha_actual_tracker if fecha_actual_tracker else fecha_base_str
                            
                            concepto_final = "ACH FEES" if es_ach else "BELOW MINIMUM BALANCE FEE"
                            monto_usd = 0.50 if es_ach else 35.00
                            
                            trm_g = obtener_trm_inteligente(trm_datos, fecha_gasto)
                            if trm_g:
                                gastos_encontrados_lote.append({
                                    "Fecha": fecha_gasto,
                                    "Descripción": concepto_final,
                                    "USD": monto_usd,
                                    "TRM Aplicada": trm_g,
                                    "Total COP": monto_usd * trm_g,
                                    "Origen": archivo.name
                                })
            except Exception as e:
                st.error(f"Error procesando {archivo.name}: {e}")
                
        if gastos_encontrados_lote:
            df_enc = pd.DataFrame(gastos_encontrados_lote)
            st.success(f"💥 Se consolidaron **{len(df_enc)} movimientos reales** limpios de duplicados de resumen.")
            st.dataframe(df_enc[["Fecha", "Descripción", "USD", "TRM Aplicada", "Total COP", "Origen"]], use_container_width=True, hide_index=True)
            
            if st.button("💾 Inyectar y Consolidar Todo en el Libro Maestro"):
                with open(FILE_GASTOS, "a", encoding="utf-8") as fg:
                    for g in gastos_encontrados_lote:
                        fg.write(f"{g['Fecha']};{g['Descripción']};{g['USD']};{g['TRM Aplicada']};{g['Total COP']}\n")
                st.success("¡Libro maestro actualizado sin redundancias!")
        else:
            st.warning("No se identificaron comisiones deducibles reales en el archivo.")

with tab1:
    st.subheader("Cruce Manual de Gastos Bancarios")
    c_izq, c_der = st.columns(2)
    with c_izq:
        desc_gasto = st.selectbox("Concepto Contable", ["ACH FEES", "BELOW BALANCE FEE"])
        usd_gasto = st.number_input("Monto (USD)", min_value=0.0, step=0.01, value=0.50 if desc_gasto=="ACH FEES" else 35.00)
    with c_der:
        if trm_inspeccionada and usd_gasto > 0:
            cop_equivalente = usd_gasto * trm_inspeccionada
            st.success(f"TRM Aplicada: ${trm_inspeccionada:,.2f}")
            st.metric("Total Equivalente en COP", f"${cop_equivalente:,.2f}")
            if st.button("💾 Guardar Gasto Manual"):
                with open(FILE_GASTOS, "a", encoding="utf-8") as fg:
                    fg.write(f"{fecha_base_str};{desc_gasto};{usd_gasto};{trm_inspeccionada};{cop_equivalente}\n")
                st.success("¡Registrado!")

with tab2:
    st.subheader("📊 Histórico Contable")
    if os.path.exists(FILE_GASTOS):
        with open(FILE_GASTOS, "r", encoding="utf-8") as fg:
            st.text(fg.read())

st.markdown('</div>', unsafe_allow_html=True)
