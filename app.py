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
# 🚨 1. CONFIGURACIÓN GLOBAL DE STREAMLIT (DEBE SER LA PRIMERA LÍNEA)
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
        position: absolute;
        left: 4%;
        top: 50%;
        transform: translateY(-50%);
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
# 🌿 MONTAJE INTEGRADO DEL BANNER Y IDENTIDAD CORPORATIVA OVERLAY
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
                <p class="app-sub-title">ESHKOL PREMIUM S.A.S &nbsp;|&nbsp; MÓDULO CONTABLE v2.4</p>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(html_banner, unsafe_allow_html=True)

# Contenedor del espacio de trabajo contable
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
        for fecha, valor in dicc.items():
            f.write(f"{fecha};{valor}\n")

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
# 🗺️ CONTROLES CRONOLÓGICOS
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

# --- PANEL DE TENDENCIA SEMANAL ---
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

# --- RECUADROS DE SEGUIMIENTO ---
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
    "📄 Procesar Extracto PDF", 
    "💰 Registrar Gasto Manual", 
    "📊 Consolidados e Informes Excel", 
    "⚙️ Migración CSV",
    "🧹 Reinicio Maestro"
])

with tab0:
    st.subheader("🕵️‍♂️ Extractor Inteligente Davivenda (USD)")
    archivo_pdf = st.file_uploader("Cargar extracto bancario (.pdf)", type=["pdf"])
    
    if archivo_pdf is not None:
        try:
            lector = pypdf.PdfReader(archivo_pdf)
            texto_completo = ""
            for pagina in lector.pages:
                texto_completo += pagina.extract_text() + "\n"
            
            lineas = texto_completo.splitlines()
            gastos_encontrados = []
            vistos_en_este_pdf = set() # Estructura de control anti-duplicados por capa
            
            patron_ach_fees = re.compile(r'\bACH\s+FEES\b', re.IGNORECASE)
            patron_minimum = re.compile(r'\bBELOW\s+(?:MINIMUM\s+)?BALANCE\s+FEES?\b', re.IGNORECASE)
            patron_fecha = r'(\d{1,2})/(\d{1,2})/(\d{2,4})'
            
            for linea in lineas:
                linea_upper = linea.upper()
                
                if any(x in linea_upper for x in ["TOTAL", "SUMMARY", "RESUMEN", "YEAR-TO-DATE", "BROUGHT FORWARD", "FOR THIS PERIOD"]):
                    continue
                
                es_ach = bool(patron_ach_fees.search(linea))
                es_min = bool(patron_minimum.search(linea))
                
                if es_ach or es_min:
                    match_f = re.search(patron_fecha, linea)
                    if match_f:
                        mes, dia, ano = match_f.group(1), match_f.group(2), match_f.group(3)
                        if len(ano) == 2: ano = f"20{ano}"
                        fecha_gasto = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                    else:
                        fecha_gasto = fecha_base_str
                    
                    concepto = "ACH FEES" if es_ach else "BELOW BALANCE FEE"
                    valores = re.findall(r'\b\d*\.\d{2}\b', linea)
                    
                    monto_usd = None
                    if valores:
                        for v in valores:
                            try:
                                val_f = float(v)
                                if val_f in [0.50, 35.00]:
                                    monto_usd = val_f
                                    break
                            except: pass
                    
                    if monto_usd is None:
                        monto_usd = 0.50 if es_ach else 35.00
                    
                    # FILTRO DE UNICIDAD: Evita duplicar movimientos leídos en capas paralelas del PDF
                    clave_gasto = (fecha_gasto, concepto, monto_usd)
                    if clave_gasto in vistos_en_este_pdf:
                        continue
                        
                    trm_g = obtener_trm_inteligente(trm_datos, fecha_gasto)
                    if trm_g:
                        vistos_en_este_pdf.add(clave_gasto)
                        gastos_encontrados.append({
                            "Fecha": fecha_gasto, "Descripción": concepto, "USD": monto_usd,
                            "TRM Aplicada": trm_g, "Total COP": monto_usd * trm_g
                        })
            
            if gastos_encontrados:
                df_enc = pd.DataFrame(gastos_encontrados)
                st.success(f"💥 Se identificaron **{len(df_enc)} gastos bancarios** unificados sin duplicados.")
                st.dataframe(df_enc, use_container_width=True, hide_index=True)
                
                if st.button("💾 Inyectar y Consolidar en Libro Maestro"):
                    with open(FILE_GASTOS, "a", encoding="utf-8") as fg:
                        for g in gastos_encontrados:
                            fg.write(f"{g['Fecha']};{g['Descripción']};{g['USD']};{g['TRM Aplicada']};{g['Total COP']}\n")
                    st.success("¡Gastos incorporados exitosamente!")
            else:
                st.warning("No se encontraron comisiones deducibles en el documento.")
                
        except Exception as e:
            st.error(f"Error procesando el PDF: {e}")

with tab1:
    st.subheader("Cruce Manual de Gastos Bancarios")
    c_izq, c_der = st.columns(2)
    with c_izq:
        st.info(f"Fecha de liquidación: **{fecha_base_dt.strftime('%d/%m/%Y')}**")
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
                st.success("¡Gasto registrado con éxito!")

with tab2:
    st.subheader("📊 Reportes Financieros Consolidados")
    if os.path.exists(FILE_GASTOS):
        lineas_gastos = []
        with open(FILE_GASTOS, "r", encoding="utf-8") as fg:
            for line in fg:
                p = line.strip().split(";")
                if len(p) == 5:
                    lineas_gastos.append({
                        "Fecha": p[0], "Descripción": p[1], 
                        "USD": float(p[2]), "TRM Usada": float(p[3]), "Total COP": float(p[4])
                    })
        if lineas_gastos:
            df_gastos = pd.DataFrame(lineas_gastos)
            df_gastos['Fecha_DT'] = pd.to_datetime(df_gastos['Fecha'])
            
            df_semanal = df_gastos.set_index('Fecha_DT').resample('W').sum(numeric_only=True).reset_index()
            df_semanal['Corte Semana'] = df_semanal['Fecha_DT'].dt.strftime('%Y-%m-%d')
            df_semanal_final = df_semanal[['Corte Semana', 'USD', 'Total COP']]
            
            df_mensual = df_gastos.set_index('Fecha_DT').resample('ME').sum(numeric_only=True).reset_index()
            df_mensual['Corte Mes'] = df_mensual['Fecha_DT'].dt.strftime('%Y-%m')
            df_mensual_final = df_mensual[['Corte Mes', 'USD', 'Total COP']]
            
            df_detalles_final = df_gastos[["Fecha", "Descripción", "USD", "TRM Usada", "Total COP"]]

            c_rep1, c_rep2 = st.columns(2)
            with c_rep1:
                st.write("**📊 Consolidado Acumulado Semanal**")
                st.dataframe(df_semanal_final, use_container_width=True, hide_index=True)
            with c_rep2:
                st.write("**📊 Consolidado Acumulado Mensual**")
                st.dataframe(df_mensual_final, use_container_width=True, hide_index=True)
            
            st.write("📋 **Libro Diario de Detalles**")
            st.dataframe(df_detalles_final, use_container_width=True, hide_index=True)
            
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_detalles_final.to_excel(writer, sheet_name='📋 Detalle Diario', index=False)
                df_semanal_final.to_excel(writer, sheet_name='📅 Resumen Semanal', index=False)
                df_mensual_final.to_excel(writer, sheet_name='🗓️ Resumen Mensual', index=False)
            
            excel_data = output_excel.getvalue()
            
            st.download_button(
                label="🟢 DESCARGAR INFORME MULTIPESTAÑA EXCEL (.XLSX)",
                data=excel_data,
                file_name=f"Informe_Gastos_Eshkol_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else: st.info("No hay transacciones registradas en el ciclo activo.")
    else: st.info("No hay transacciones registradas en el ciclo activo.")

with tab3:
    st.subheader("⚙️ Inyección de Respaldos")
    archivo_subido = st.file_uploader("Cargar CSV maestro", type=["csv"])
    if archivo_subido is not None:
        try:
            lineas_texto = archivo_subido.getvalue().decode("utf-8").splitlines()
            if st.button("🚀 Procesar Históricos"):
                dicc_actual = cargar_trm_locales()
                contador = 0
                patron_fecha = r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})'
                for linea in lineas_texto:
                    celdas = linea.split(';')
                    fecha_actual = None
                    for celda in celdas:
                        celda_limpia = celda.strip()
                        if not celda_limpia: continue
                        match_fecha = re.search(patron_fecha, celda_limpia)
                        if match_fecha:
                            try:
                                d, m, a = match_fecha.group(1), match_fecha.group(2), match_fecha.group(3)
                                fecha_actual = f"{a}-{m.zfill(2)}-{d.zfill(2)}"
                                continue
                            except: fecha_actual = None
                        if fecha_actual and '$' in celda_limpia:
                            try:
                                t_str = celda_limpia.replace('$', '').replace(' ', '').strip()
                                if ',' in t_str and '.' in t_str: t_str = t_str.replace('.', '').replace(',', '.')
                                elif ',' in t_str: t_str = t_str.replace(',', '.')
                                t_clean = float(t_str)
                                if t_clean > 1000: 
                                    dicc_actual[fecha_actual] = t_clean
                                    contador += 1
                                    fecha_actual = None
                            except: pass
                guardar_trm_locales(dicc_actual)
                st.success(f"¡Sincronizados {contador:,} registros antiguos!")
        except Exception as e: st.error(f"Error: {e}")

with tab4:
    st.subheader("🧹 Formatear Aplicación (Cierre Fiscal)")
    st.warning("⚠️ ¡Atención Contable! Esta acción borrará de forma permanente los históricos calculados.")
    confirmacion = st.checkbox("Confirmo el formato absoluto.")
    if confirmacion:
        if st.button("🚨 EJECUTAR BORRADO DEFINITIVO"):
            with open(FILE_GASTOS, "w", encoding="utf-8") as f: f.write("") 
            with open(FILE_TRM, "w", encoding="utf-8") as f: f.write("") 
            st.cache_data.clear()
            st.success("¡Sistema purgado!")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
