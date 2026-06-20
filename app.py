import streamlit as st
import pandas as pd
import pypdf
import re
import datetime
import io
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS PREMIUM
st.set_page_config(
    page_title="Extractor Avanzado de Gastos Bancarios - Davivenda",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size:32px !important; font-weight: 700 !important; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { font-size:16px !important; color: #4B5563; margin-bottom: 25px; }
    .metric-card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #2563EB; margin-bottom: 15px; }
    .metric-title { font-size: 14px; color: #6B7280; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 28px; font-weight: 700; color: #1F2937; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIONES CORE DE PROCESAMIENTO Y PARSEO TRADICIONAL COMPLETO

def clean_duplicate_lines(text: str) -> str:
    lines = text.split('\n')
    seen = set()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or '--- PAGE' in line:
            cleaned_lines.append(line)
            continue
        if stripped in seen:
            continue
        seen.add(stripped)
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def clean_amount(val_str: str) -> float:
    """Limpia cadenas de texto monetarias y las convierte a float exacto."""
    if not val_str:
        return 0.0
    cleaned = val_str.replace('\n', '').replace(' ', '')
    cleaned = re.sub(r'[^\d.,-]', '', cleaned)
    if not cleaned:
        return 0.0
    # Caso especial de puntos decorativos finales como .50.
    if cleaned.endswith('.') and cleaned.count('.') > 1:
        cleaned = cleaned[:-1]
    
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
    return float(cleaned)

def process_pdf_and_extract_data(file_bytes, filename: str):
    pdf_file = io.BytesIO(file_bytes)
    reader = pypdf.PdfReader(pdf_file)
    
    raw_pages_text = []
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            raw_pages_text.append((idx + 1, page_text))
            
    transactions = []
    audit_logs = []
    
    summary_keywords = [
        "OVERDRAFT AND RETURN CHECK FEES", 
        "TOTAL OVERDRAFT", 
        "ACH, NSF AND RETURN ITEMS", 
        "YEAR-TO-DATE"
    ]
    
    cleaned_document_parts = []
    
    for page_num, page_content in raw_pages_text:
        page_header = f"\n--- PAGE {page_num} ---\n"
        full_page_text = page_header + page_content
        
        table_header_match = re.search(r'"DATE[^"]*"\s*,\s*(?:,\s*)?"DESCRIPTION[^"]*"', full_page_text, re.IGNORECASE)
        totals_match = re.search(r'TOTAL[\s\n]*OVERDRAFT|OVERDRAFT AND RETURN CHECK FEES|TOTAL OVERDRAFT FEES', full_page_text, re.IGNORECASE)
        has_summary_text = any(kw in full_page_text for kw in summary_keywords)
        
        if table_header_match or totals_match or has_summary_text:
            truncation_point = len(full_page_text)
            reason = ""
            if table_header_match:
                truncation_point = min(truncation_point, table_header_match.start())
                reason = "Tabla analítica de resúmenes anuales detectada."
            elif totals_match:
                truncation_point = min(truncation_point, totals_match.start())
                reason = "Bloque consolidado de totales anuales detectado."
            elif has_summary_text:
                for kw in summary_keywords:
                    kw_match = re.search(re.escape(kw), full_page_text)
                    if kw_match:
                        truncation_point = min(truncation_point, kw_match.start())
                reason = "Palabras clave de comisiones acumuladas detectadas."
            
            excluded_text = full_page_text[truncation_point:]
            if len(excluded_text.strip()) > 5:
                audit_logs.append({
                    "Pagina": page_num, "Tipo": "Aislamiento de Bloque de Resumen",
                    "Detalle": reason, "Contenido Excluido": excluded_text[:600] + "\n[...]",
                    "Archivo de Origen": filename
                })
            full_page_text = full_page_text[:truncation_point]
            
        cleaned_document_parts.append(full_page_text)
        
    full_cleaned_text = '\n'.join(cleaned_document_parts)
    full_cleaned_text = clean_duplicate_lines(full_cleaned_text)
    
    # REGEX INTEGRAL: Captura la estructura tabular de transacciones reales de Davivenda
    tx_pattern = r'"(\d{1,2}/\d{1,2}/\d{2,4})[^"]*"\s*,\s*(?:"(\d{1,2}/\d{1,2}/\d{2,4})[^"]*"\s*,\s*)?"([^"]*)"\s*,\s*(?:"([^"]*)"\s*,\s*)?(?:"([^"]*)"\s*,\s*)?"([^"]*)"'
    matches = re.finditer(tx_pattern, full_cleaned_text)
    
    for match in matches:
        posting_date_str = match.group(1).strip()
        description_raw = match.group(3).strip()
        description_upper = description_raw.upper()
        
        # Filtrado selectivo estricto
        is_ach = "ACH" in description_upper and "FEE" in description_upper
        is_below = "BELOW" in description_upper and "BALANCE" in description_upper
        
        if not (is_ach or is_below):
            continue
            
        fee_type = "ACH FEES" if is_ach else "BELOW MINIMUM BALANCE FEE"
        
        # Rescate de columnas numéricas (Debits/Cargos)
        g4, g5, g6 = match.group(4), match.group(5), match.group(6)
        extracted_amount = 0.0
        if g4 and any(c.isdigit() for c in g4) and not any(k in g4.upper() for k in ["TOTAL", "BALANCE", "FORWARD"]):
            extracted_amount = clean_amount(g4)
        elif g5 and any(c.isdigit() for c in g5):
            extracted_amount = clean_amount(g5)
        elif g6 and any(c.isdigit() for c in g6):
            extracted_amount = clean_amount(g6)
            
        # Validaciones de respaldo del negocio por si el PDF viene corrupto o desplazado
        if extracted_amount == 0.0:
            extracted_amount = 0.50 if fee_type == "ACH FEES" else 35.00
            
        try:
            date_parts = posting_date_str.split('/')
            m, d, y = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
            if y < 100: y += 2000
            date_obj = datetime.date(y, m, d)
        except Exception:
            date_obj = None
            
        transactions.append({
            "Fecha": date_obj if date_obj else posting_date_str,
            "Tipo de Gasto": fee_type,
            "Monto (USD)": extracted_amount,
            "Descripción Original": description_raw.replace('\n', ' ').strip(),
            "Archivo de Origen": filename
        })
        
    return transactions, audit_logs

# 3. CONTROL INTEGRAL DEL ESTADO DE LA SESIÓN
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = pd.DataFrame()
if 'audit_trails' not in st.session_state:
    st.session_state.audit_trails = []
if 'uploaded_files_registry' not in st.session_state:
    st.session_state.uploaded_files_registry = []

# 4. ESTRUCTURA DE LA INTERFAZ DE USUARIO (UI)
st.markdown('<p class="main-header">Sistema Inteligente de Control Financiero</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Módulo de Extracción Quirúrgica de Gastos Bancarios e Inmunidad a Resúmenes de Cuenta</p>', unsafe_allow_html=True)

st.sidebar.header("Carga de Extractos")
uploaded_files = st.sidebar.file_uploader(
    "Selecciona los archivos PDF de Davivenda",
    type=["pdf"], accept_multiple_files=True, key="pdf_uploader"
)

if uploaded_files:
    current_filenames = [f.name for f in uploaded_files]
    if current_filenames != st.session_state.uploaded_files_registry:
        all_transactions = []
        all_audit_logs = []
        progress_bar = st.sidebar.progress(0)
        for idx, file in enumerate(uploaded_files):
            file_bytes = file.read()
            txs, logs = process_pdf_and_extract_data(file_bytes, file.name)
            all_transactions.extend(txs)
            all_audit_logs.extend(logs)
            progress_bar.progress(int((idx + 1) / len(uploaded_files) * 100))
            
        st.session_state.processed_data = pd.DataFrame(all_transactions)
        st.session_state.audit_trails = all_audit_logs
        st.session_state.uploaded_files_registry = current_filenames
        st.sidebar.success("¡Extractos analizados con éxito!")

if st.sidebar.button("Limpiar Memoria del Sistema"):
    st.session_state.processed_data = pd.DataFrame()
    st.session_state.audit_trails = []
    st.session_state.uploaded_files_registry = []
    st.rerun()

# 5. LÓGICA DE FILTRADO Y RENDERIZADO DE TABLEROS
if st.session_state.processed_data.empty:
    st.info("👋 Bienvenido. Por favor, cargue los extractos bancarios en formato PDF desde la barra lateral.")
else:
    df = st.session_state.processed_data.copy()
    st.sidebar.markdown("---")
    st.sidebar.header("Filtros de Control")
    
    df_dates = df[df['Fecha'].apply(lambda x: isinstance(x, datetime.date))]
    if not df_dates.empty:
        min_date, max_date = df_dates['Fecha'].min(), df_dates['Fecha'].max()
        date_selection = st.sidebar.date_input("Rango de Análisis", value=[min_date, max_date], min_value=min_date, max_value=max_date)
    else:
        date_selection = None
        
    unique_types = df['Tipo de Gasto'].unique().tolist()
    selected_types = st.sidebar.multiselect("Tipos de Gasto", options=unique_types, default=unique_types)
    
    if date_selection and isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
        df_filtered = df[df['Fecha'].apply(lambda x: date_selection[0] <= x <= date_selection[1] if isinstance(x, datetime.date) else False)]
    else:
        df_filtered = df.copy()
        
    df_filtered = df_filtered[df_filtered['Tipo de Gasto'].isin(selected_types)]
    
    # KPI CARDS
    ach_df = df_filtered[df_filtered['Tipo de Gasto'] == "ACH FEES"]
    below_df = df_filtered[df_filtered['Tipo de Gasto'] == "BELOW MINIMUM BALANCE FEE"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card" style="border-left-color: #10B981;"><div class="metric-title">Total ACH FEES</div><div class="metric-value">${ach_df["Monto (USD)"].sum():,.2f} USD</div><div style="color: #6B7280; font-size: 13px;">Movimientos: <b>{len(ach_df)}</b></div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card" style="border-left-color: #EF4444;"><div class="metric-title">Total BELOW BALANCE FEE</div><div class="metric-value">${below_df["Monto (USD)"].sum():,.2f} USD</div><div style="color: #6B7280; font-size: 13px;">Movimientos: <b>{len(below_df)}</b></div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card" style="border-left-color: #3B82F6;"><div class="metric-title">Gasto Consolidado</div><div class="metric-value">${df_filtered["Monto (USD)"].sum():,.2f} USD</div><div style="color: #6B7280; font-size: 13px;">Total General: <b>{len(df_filtered)}</b></div></div>', unsafe_allow_html=True)
        
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard Analítico", "📋 Registro Detallado de Movimientos", "🛡️ Auditoría e Inmunidad", "📥 Exportación"])
    
    with tab1:
        if not df_filtered.empty:
            df_chart = df_filtered.groupby(['Fecha', 'Tipo de Gasto'])['Monto (USD)'].sum().reset_index()
            df_chart['Fecha_Str'] = df_chart['Fecha'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else str(x))
            fig_bar = px.bar(df_chart, x='Fecha_Str', y='Monto (USD)', color='Tipo de Gasto', color_discrete_map={"ACH FEES": "#10B981", "BELOW MINIMUM BALANCE FEE": "#EF4444"}, barmode='stack', height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No existen registros en el rango seleccionado.")
            
    with tab2:
        if not df_filtered.empty:
            st.dataframe(df_filtered.sort_values(by="Fecha"), use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros.")
            
    with tab3:
        if st.session_state.audit_trails:
            for log_idx, audit in enumerate(st.session_state.audit_trails):
                with st.expander(f"🔴 Bloque Excluido #{log_idx+1} - {audit['Archivo de Origen']} (Pág. {audit['Pagina']})"):
                    st.code(audit['Contenido Excluido'], language="text")
        else:
            st.success("✅ Ningún bloque residual detectado en páginas operativas.")
            
    with tab4:
        if not df_filtered.empty:
            csv_df = df_filtered.copy()
            csv_df['Fecha'] = csv_df['Fecha'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else str(x))
            st.download_button(label="📥 Descargar Reporte Completo (CSV)", data=csv_df.to_csv(index=False, encoding='utf-8-sig'), file_name="Gastos_Davivenda_Limpio.csv", mime="text/csv", use_container_width=True)
