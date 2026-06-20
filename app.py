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

# --- Instalación e importación silenciosa de dependencias contables ---
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
# 🎨 INYECCIÓN DE ESTILOS CSS CLEAN-PREMIUM CORREGIDOS
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
                <p class="app-sub-title">ESHKOL PREMIUM S.A.S &nbsp;|&nbsp; MÓDULO CONTABLE v2.6</p>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(html_banner, unsafe_allow_html=True)

# Contenedor global del espacio de trabajo
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
    "📄 Procesar Extractos PDF", 
    "💰 Registrar Gasto Manual", 
    "📊 Consolidados e Informes Excel", 
    "⚙️ Migración CSV",
    "🧹 Reinicio Maestro"
])

with tab0:
    st.subheader("🕵️‍♂️ Extractor Avanzado Davivenda (Garantía de Unicidad por Fila)")
    archivos_pdf = st.file_uploader("Cargar extractos bancarios (.pdf)", type=["pdf"], accept_multiple_files=True)
    
    if archivos_pdf:
        gastos_encontrados_lote = []
        
        def clean_amount_internal(val_str: str) -> float:
            if not val_str: return 0.0
            cleaned = val_str.replace('\n', '').replace(' ', '')
            cleaned = re.sub(r'[^\d.,-]', '', cleaned)
            if not cleaned: return 0.0
            if cleaned.endswith('.') and cleaned.count('.') > 1: cleaned = cleaned[:-1]
            if ',' in cleaned and '.' in cleaned:
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) == 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            try: return float(cleaned)
            except: return 0.0

        summary_keywords = [
            "OVERDRAFT AND RETURN CHECK FEES", 
            "TOTAL OVERDRAFT", 
            "ACH, NSF AND RETURN ITEMS", 
            "YEAR-TO-DATE"
        ]
        
        for archivo in archivos_pdf:
            try:
                lector = pypdf.PdfReader(archivo)
                raw_pages_text = []
                for idx, page in enumerate(lector.pages):
                    page_text = page.extract_text()
                    if page_text:
                        raw_pages_text.append((idx + 1, page_text))
                
                cleaned_document_parts = []
                for page_num, page_content in raw_pages_text:
                    full_page_text = f"\n--- PAGE {page_num} ---\n" + page_content
                    
                    table_header_match = re.search(r'"DATE[^"]*"\s*,\s*(?:,\s*)?"DESCRIPTION[^"]*"', full_page_text, re.IGNORECASE)
                    totals_match = re.search(r'TOTAL[\s\n]*OVERDRAFT|OVERDRAFT AND RETURN CHECK FEES|TOTAL OVERDRAFT FEES', full_page_text, re.IGNORECASE)
                    has_summary_text = any(kw in full_page_text for kw in summary_keywords)
                    
                    if table_header_match or totals_match or has_summary_text:
                        truncation_point = len(full_page_text)
                        if table_header_match: truncation_point = min(truncation_point, table_header_match.start())
                        elif totals_match: truncation_point = min(truncation_point, totals_match.start())
                        elif has_summary_text:
                            for kw in summary_keywords:
                                kw_match = re.search(re.escape(kw), full_page_text)
                                if kw_match: truncation_point = min(truncation_point, kw_match.start())
                        full_page_text = full_page_text[:truncation_point]
                    cleaned_document_parts.append(full_page_text)
                
                full_cleaned_text = '\n'.join(cleaned_document_parts)
                
                # 🛠️ CORRECCIÓN DE SINTAXIS MÁXIMA EN CADENA LITERAL RAW:
                tx_pattern = r'"(\d{1,2}/\d{1,2}/\d{2,4})[^"]*"\s*,\s*(?:"(\d{1,2}/\d{1,2}/\d{2,4})[^"]*"\s*,\s*)?"([^"]*)"\s*,\s*(?:"([^"]*)"\s*,\s*)?(?:"([^"]*)"\s*,\s*)?"([^"]*)"'
                matches = re.finditer(tx_pattern, full_cleaned_text)
                
                for match in matches:
                    posting_date_str = match.group(1).strip()
                    description_raw = match.group(3).strip()
                    description_upper = description_raw.upper()
                    
                    is_ach = "ACH" in description_upper and "FEE" in description_upper
                    is_below = "BELOW" in description_upper and "BALANCE" in description_upper
                    
                    if not (is_ach or is_below):
                        continue
                        
                    concepto_final = "ACH FEES" if is_ach else "BELOW BALANCE FEE"
                    
                    g4, g5, g6 = match.group(4), match.group(5), match.group(6)
                    monto_usd = 0.0
                    if g4 and any(c.isdigit() for c in g4) and not any(k in g4.upper() for k in ["TOTAL", "BALANCE", "FORWARD"]):
                        monto_usd = clean_amount_internal(g4)
                    elif g5 and any(c.isdigit() for c in g5):
                        monto_usd = clean_amount_internal(g5)
                    elif g6 and any(c.isdigit() for c in g6):
                        monto_usd = clean_amount_internal(g6)
                        
                    if monto_usd == 0.0:
                        monto_usd = 0.50 if concepto_final == "ACH FEES" else 35.00
                        
                    try:
                        date_parts = posting_date_str.split('/')
                        m, d, y = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        if y < 100: y += 2000
                        fecha_gasto = f"{y}-{str(m).zfill(2)}-{str(d).zfill(2)}"
                    except:
                        fecha_gasto = fecha_base_str
                        
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
            st.success(f"💥 Se consolidaron **{len(df_enc)} movimientos reales** sin omisiones de fechas múltiples.")
            st.dataframe(df_enc[["Fecha", "Descripción", "USD", "TRM Aplicada", "Total COP", "Origen"]], use_container_width=True, hide_index=True)
            
            if st.button("💾 Inyectar y Consolidar Todo en el Libro Maestro"):
                with open(FILE_GASTOS, "a", encoding="utf-8") as fg:
                    for g in gastos_encontrados_lote:
                        fg.write(f"{g['Fecha']};{g['Descripción']};{g['USD']};{g['TRM Aplicada']};{g['Total COP']}\n")
                st.success("¡Todos los movimientos reales fueron integrados al histórico maestro!")
        else:
            st.warning("No se identificaron comisiones deducibles en ninguno de los archivos cargados.")

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
    st.subheader("📊 Reportes Financieros Consolidados e Histórico Cambiario")
    
    lineas_trm_hist = []
    for f_trm, v_trm in sorted(trm_datos.items(), reverse=True):
        lineas_trm_hist.append({"Fecha": f_trm, "TRM Oficial (COP)": v_trm})
    df_trm_maestro = pd.DataFrame(lineas_trm_hist)
    
    st.markdown("#### 🔍 Consultar Histórico de TRM por Mes")
    c_f1, c_f2 = st.columns(2)
    filtro_ano = c_f1.selectbox("Filtrar Año TRM", list(range(fecha_hoy_dt.year, 2015, -1)), key="f_ano")
    filtro_mes = c_f2.selectbox("Filtrar Mes TRM", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=fecha_hoy_dt.month - 1)
    
    meses_num = {"Enero":"01", "Febrero":"02", "Marzo":"03", "Abril":"04", "Mayo":"05", "Junio":"06", "Julio":"07", "Agosto":"08", "Septiembre":"09", "Octubre":"10", "Noviembre":"11", "Diciembre":"12"}
    prefijo_busqueda = f"{filtro_ano}-{meses_num[filtro_mes]}"
    
    df_trm_filtrado = df_trm_maestro[df_trm_maestro["Fecha"].str.startswith(prefijo_busqueda)]
    
    if not df_trm_filtrado.empty:
        st.caption(f"Mostrando tasas de cambio registradas para {filtro_mes} del {filtro_ano}")
        st.dataframe(df_trm_filtrado, use_container_width=True, hide_index=True)
    else:
        st.info("No se hallaron registros locales para el periodo seleccionado.")
        
    st.write("---")
    
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
                df_trm_maestro.to_excel(writer, sheet_name='📈 Histórico Completo TRM', index=False)
            
            excel_data = output_excel.getvalue()
            
            st.download_button(
                label="🟢 DESCARGAR AUDITORÍA COMPLETA EXCEL (.XLSX)",
                data=excel_data,
                file_name=f"Informe_Financiero_Eshkol_{datetime.now().strftime('%Y%m%d')}.xlsx",
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
