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
            f_ant = (dt - timedelta(days=i)).strftime("%Y-%m-%d")
            if f_ant in dicc and dicc[f_ant] > 1000:
                return dicc[f_ant]
    except:
        pass
    return None

with st.spinner("Sincronizando pasarela cambiaria en tiempo real..."):
    trm_datos = sincronizar_trm_en_bloque()

fecha_hoy_dt = datetime.now()
fecha_hoy_str = fecha_hoy_dt.strftime("%Y-%m-%d")

# ==========================================
# 🗺️ CONTROLES CRONOLÓGICOS SCONTRÓLICOS
# ==========================================
st.markdown("### 📅 Eje de Tiempo Sincronizado")
c_ano, c_mes, c_dia = st.columns(3)
ano_sel = c_ano.selectbox("Año de Consulta", list(range(fecha_hoy_dt.year, 2015, -1)))
mes_sel = c_mes.selectbox("Mes de Consulta", list(range(1, 13)), index=fecha_hoy_dt.month - 1)
dia_sel = c_dia.selectbox("Día de Consulta", list(range(1, 32)), index=fecha_hoy_dt.day - 1)

try: 
    fecha_base_dt = datetime(ano_sel, mes_sel, dia_sel)
except: 
    fecha_base_dt = datetime(ano_sel, mes_sel, 1)
fecha_base_str = fecha_base_dt.strftime("%Y-%m-%d")

trm_hoy = obtener_trm_inteligente(trm_datos, fecha_hoy_str)
trm_inspeccionada = obtener_trm_inteligente(trm_datos, fecha_base_str)

# --- PANEL DE TENDENCIA DE LA MONEDA ---
st.write(" ")
st.markdown("#### 📈 Tendencia de la Moneda Oficial (Ventana de 7 días)")
cols_dias = st.columns(7)
lista_fechas_semana = []
lista_valores_semana = []
dias_espanol = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

for i in range(0, 7):
    f_ant_dt = fecha_base_dt - timedelta(days=6-i)
    f_ant_str = f_ant_dt.strftime("%Y-%m-%d")
    trm_ant = obtener_trm_inteligente(trm_datos, f_ant_str)
    nombre_dia = dias_espanol[f_ant_dt.weekday()]
    
    etiqueta = f"{nombre_dia} {f_ant_dt.strftime('%d/%m')}"
    lista_fechas_semana.append(etiqueta)
    lista_valores_semana.append(trm_ant if trm_ant else 0.0)
    
    with cols_dias[i]:
        if trm_ant:
            st.metric(label=etiqueta, value=f"${trm_ant:,.2f}")
        else:
            st.metric(label=etiqueta, value="N/A")

valores_validos = [v for v in lista_valores_semana if v > 1000]
if valores_validos:
    df_grafico = pd.DataFrame({'Día': lista_fechas_semana, 'TRM ($)': lista_valores_semana})
    min_v, max_v = min(valores_validos), max(valores_validos)
    
    chart = alt.Chart(df_grafico).mark_line(point=True, color='#233d2c', strokeWidth=3).encode(
        x=alt.X('Día:N', sort=None, title='Días Evaluados'),
        y=alt.Y('TRM ($):Q', scale=alt.Scale(domain=[min_v - 25, max_v + 25], zero=False), title='COP Oficial')
    ).properties(height=160)
    st.altair_chart(chart, use_container_width=True)

st.write(" ")
col_r1, col_r2 = st.columns(2)
with col_r1: 
    st.metric(label=f"🟢 TRM EN VIVO HOY ({fecha_hoy_dt.strftime('%d/%m/%Y')})", value=f"$ {trm_hoy:,.2f}" if trm_hoy else "CONECTANDO...")
with col_r2: 
    st.metric(label="🔵 TRM FECHA SELECCIONADA", value=f"$ {trm_inspeccionada:,.2f}" if trm_inspeccionada else "SIN REGISTRO")

# ==========================================
# 🗂️ MÓDULOS OPERATIVOS CONTABLES
# ==========================================
st.write(" ")
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Procesar Extractos PDF", 
    "💰 Registrar Gasto Manual", 
    "📊 Consolidados e Informes Excel", 
    "⚙️ Migración CSV",
    "🧹 Reinicio Maestro"
])

with tab0:
    st.subheader("🕵️‍♂️ Extractor Avanzado Davivenda (Filtro Cronológico Puro)")
    archivos_pdf = st.file_uploader("Cargar extractos bancarios (.pdf)", type=["pdf"], accept_multiple_files=True)
    
    if archivos_pdf:
        gastos_encontrados_lote = []
        
        def clean_amount_internal(val_str: str) -> float:
            if not val_str: return 0.0
            cleaned = re.sub(r'[^\d.,-]', '', val_str.strip())
            if not cleaned: return 0.0
            if ',' in cleaned and '.' in cleaned:
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                if len(cleaned.split(',')[1]) == 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            try: return float(cleaned)
            except: return 0.0

        for archivo in archivos_pdf:
            try:
                lector = pypdf.PdfReader(archivo)
                fila_index = 0
                fuera_de_tiempo_diario = False # Interruptor para cortar la lectura al llegar a los cuadros informativos finales
                
                for num_pag, pagina in enumerate(lector.pages):
                    texto_pag = pagina.extract_text()
                    if not texto_pag:
                        continue
                    
                    lineas = texto_pag.splitlines()
                    for linea in lineas:
                        linea_upper = linea.upper()
                        
                        # 🚨 DETECTOR CRÍTICO DE CIERRE DE MOVIMIENTOS REALES
                        # Si la línea toca resúmenes anuales o tablas informativas acumuladas, se activa el freno permanente
                        if any(x in linea_upper for x in ["OVERDRAFT AND RETURN", "YEAR-TO-DATE", "ANNUAL PERCENT", "BROUGHT FORWARD"]):
                            fuera_de_tiempo_diario = True
                            
                        # Si ya salimos del diario de transacciones, ignoramos por completo cualquier coincidencia fantasma posterior
                        if fuera_de_tiempo_diario:
                            continue
                            
                        is_ach = "ACH" in linea_upper and "FEE" in linea_upper
                        is_below = "BELOW" in linea_upper and "BALANCE" in linea_upper
                        
                        if is_ach or is_below:
                            concepto_final = "ACH FEES" if is_ach else "BELOW BALANCE FEE"
                            
                            valores_numericos = re.findall(r'[\d,.]+', linea)
                            monto_usd = 0.0
                            
                            for val in valores_numericos:
                                if '/' in val or '-' in val or len(val) < 2:
                                    continue
                                parsed_val = clean_amount_internal(val)
                                if 0.10 <= parsed_val <= 45.00:
                                    monto_usd = parsed_val
                                    break
                            
                            if monto_usd == 0.0:
                                continue
                                
                            fila_index += 1
                            
                            match_fecha = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', linea)
                            if match_fecha:
                                m, d, y = match_fecha.group(1), match_fecha.group(2), match_fecha.group(3)
                                int_y = int(y)
                                if int_y < 100: int_y += 2000
                                fecha_gasto = f"{int_y}-{str(m).zfill(2)}-{str(d).zfill(2)}"
                            else:
                                fecha_gasto = fecha_base_str
                                
                            trm_g = obtener_trm_inteligente(trm_datos, fecha_gasto)
                            if trm_g:
                                gastos_encontrados_lote.append({
                                    "Fecha": fecha_gasto,
                                    "Descripción": concepto_final,
                                    "USD": monto_usd,
                                    "TRM Aplicada": trm_g,
                                    "Total COP": monto_usd * trm_g,
                                    "Origen": archivo.name,
                                    "Fila_PDF": fila_index
                                })
            except Exception as e:
                st.error(f"Error procesando el archivo {archivo.name}: {e}")
                
        if gastos_encontrados_lote:
            df_enc = pd.DataFrame(gastos
