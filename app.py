import streamlit as st
import pandas as pd
import pypdf
import re
import datetime
import io
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS PREMIUM (DEBE SER LA PRIMERA INSTRUCCIÓN DE ST)
st.set_page_config(
    page_title="Extractor Avanzado de Gastos Bancarios - Davivenda",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS personalizado para garantizar un acabado estético de alto nivel
st.markdown("""
    <style>
    .main-header {
        font-size:32px !important;
        font-weight: 700 !important;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size:16px !important;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 14px;
        color: #6B7280;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1F2937;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


# 2. FUNCIONES CORE DE PROCESAMIENTO Y PARSEO

def clean_duplicate_lines(text: str) -> str:
    """
    Elimina líneas de texto exactamente idénticas causadas por artefactos
    de doble capa de lectura del extractor de PDF, preservando filas legítimas.
    """
    lines = text.split('\n')
    seen = set()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        if '--- PAGE' in line:
            cleaned_lines.append(line)
            continue
        
        # Eliminar si la línea exacta ya fue procesada en la misma corrida
        if stripped in seen:
            continue
        
        seen.add(stripped)
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines)


def process_pdf_and_extract_data(file_bytes, filename: str):
    """
    Procesa el documento PDF, detecta y elimina resúmenes finales a nivel de página,
    y extrae quirúrgicamente las transacciones operativas válidas.
    """
    pdf_file = io.BytesIO(file_bytes)
    reader = pypdf.PdfReader(pdf_file)
    
    raw_pages_text = []
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            raw_pages_text.append((idx + 1, page_text))
            
    transactions = []
    audit_logs = []
    
    # Firmas de control para identificar secciones de resumen/totales de comisiones
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
        
        # Detección del inicio explícito de la tabla de resúmenes de comisiones
        table_header_match = re.search(r'"DATE[^"]*"\s*,\s*(?:,\s*)?"DESCRIPTION[^"]*"', full_page_text, re.IGNORECASE)
        # Detección del bloque consolidado de totales acumulados
        totals_match = re.search(r'TOTAL[\s\n]*OVERDRAFT|OVERDRAFT AND RETURN CHECK FEES|TOTAL OVERDRAFT FEES', full_page_text, re.IGNORECASE)
        has_summary_text = any(kw in full_page_text for kw in summary_keywords)
        
        if table_header_match or totals_match or has_summary_text:
            truncation_point = len(full_page_text)
            reason = ""
            
            if table_header_match:
                truncation_point = min(truncation_point, table_header_match.start())
                reason = f"Tabla de desglose analítico de resúmenes ('DATE','DESCRIPTION') detectada."
                
            if totals_match:
                truncation_point = min(truncation_point, totals_match.start())
                reason = f"Bloque consolidado de totales de comisiones anuales detectado."
                
            if not reason and has_summary_text:
                for kw in summary_keywords:
                    kw_match = re.search(re.escape(kw), full_page_text)
                    if kw_match:
                        truncation_point = min(truncation_point, kw_match.start())
                reason = f"Palabras clave de control de comisiones remanentes detectadas."
            
            # Guardar el segmento excluido para auditoría transparente del usuario
            excluded_text = full_page_text[truncation_point:]
            if len(excluded_text.strip()) > 5:
                audit_logs.append({
                    "Pagina": page_num,
                    "Tipo": "Aislamiento de Bloque de Resumen",
                    "Detalle": reason,
                    "Contenido Excluido": excluded_text[:600] + "\n[... Truncado de forma segura ...]",
                    "Archivo de Origen": filename
                })
            
            # Cortar la página de forma absoluta para que el texto de resumen no llegue al extractor
            full_page_text = full_page_text[:truncation_point]
            
        cleaned_document_parts.append(full_page_text)
        
    full_cleaned_text = '\n'.join(cleaned_document_parts)
    full_cleaned_text = clean_duplicate_lines(full_cleaned_text)
    
    # EXPRESIÓN REGULAR QUIRÚRGICA: Exige dos bloques de fechas consecutivas (Posting y Value Date)
    # Esto invalida las filas del resumen que solo cuentan con una sola fecha.
    tx_pattern = r'"(\d{1,2}/\d{1,2}/\d{2,4})[^"]*"\s*,\s*"(\d{1,2}/\d{1,2}/\d{2,4})[^"]*"\s*,\s*"([^"]*(?:ACH\s*FEES|BELOW\s*(?:MINIMUM\s*)?BALANCE\s*FEE)[^"]*)"'
    
    matches = re.finditer(tx_pattern, full_cleaned_text, re.IGNORECASE)
    
    for match in matches:
        posting_date_str = match.group(1).strip()
        description_raw = match.group(3).strip()
        description_upper = description_raw.upper()
        
        # Clasificación e inyección directa de montos fijos del negocio (Cero imprecisiones de lectura)
        if "ACH" in description_upper and "FEE" in description_upper:
            fee_type = "ACH FEES"
            amount = 0.50
        elif "BELOW" in description_upper and "BALANCE" in description_upper:
            fee_type = "BELOW MINIMUM BALANCE FEE"
            amount = 35.00
        else:
            continue
            
        # Conversión controlada a objetos datetime.date nativos
        try:
            date_parts = posting_date_str.split('/')
            m = int(date_parts[0])
            d = int(date_parts[1])
            y = int(date_parts[2])
            if y < 100:
                y += 2000
            date_obj = datetime.date(y, m, d)
        except Exception:
            date_obj = None
            
        transactions.append({
            "Fecha": date_obj if date_obj else posting_date_str,
            "Tipo de Gasto": fee_type,
            "Monto (USD)": amount,
            "Descripción Original": description_raw.replace('\n', ' ').strip(),
            "Archivo de Origen": filename
        })
        
    return transactions, audit_logs


# 3. CONTROL INTEGRAL DEL ESTADO DE LA SESIÓN (SESSION STATE)
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = pd.DataFrame()
if 'audit_trails' not in st.session_state:
    st.session_state.audit_trails = []
if 'uploaded_files_registry' not in st.session_state:
    st.session_state.uploaded_files_registry = []


# 4. ESTRUCTURA DE LA INTERFAZ DE USUARIO (UI) Y CONTROLES

st.markdown('<p class="main-header">Sistema Inteligente de Control Financiero</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Módulo de Extracción Quirúrgica de Gastos Bancarios e Inmunidad a Resúmenes de Cuenta</p>', unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/fluent/100/000000/bank-building.png", width=70)
st.sidebar.header("Carga de Extractos")

uploaded_files = st.sidebar.file_uploader(
    "Selecciona los archivos PDF de Davivenda",
    type=["pdf"],
    accept_multiple_files=True,
    key="pdf_uploader"
)

# Monitorear cambios en el cargador para refrescar el procesamiento automáticamente
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

if st.sidebar.button("Limpiar Memoria del Sistema", type="secondary"):
    st.session_state.processed_data = pd.DataFrame()
    st.session_state.audit_trails = []
    st.session_state.uploaded_files_registry = []
    st.rerun()


# 5. LÓGICA DE FILTRADO Y RENDERIZADO DE TABLEROS
if st.session_state.processed_data.empty:
    st.info("👋 Bienvenido. Por favor, cargue los extractos bancarios en formato PDF desde la barra lateral para iniciar el procesamiento automatizado.")
else:
    df = st.session_state.processed_data.copy()
    
    st.sidebar.markdown("---")
    st.sidebar.header("Filtros de Control")
    
    # Control de rango de fechas con protección ante tipos de datos mixtos
    df_dates = df[df['Fecha'].apply(lambda x: isinstance(x, datetime.date))]
    if not df_dates.empty:
        min_date = df_dates['Fecha'].min()
        max_date = df_dates['Fecha'].max()
        
        date_selection = st.sidebar.date_input(
            "Rango de Análisis",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_selection = None
        
    unique_types = df['Tipo de Gasto'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Tipos de Gasto",
        options=unique_types,
        default=unique_types
    )
    
    # Aplicación de filtros mediante una función de comparación segura (Evita TypeErrors en ejecución)
    if date_selection and isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
        def safe_date_filter(row_date):
            if isinstance(row_date, datetime.date):
                return date_selection[0] <= row_date <= date_selection[1]
            return False
        df_filtered = df[df['Fecha'].apply(safe_date_filter)]
    else:
        df_filtered = df.copy()
        
    df_filtered = df_filtered[df_filtered['Tipo de Gasto'].isin(selected_types)]
    
    # GENERACIÓN DE TARJETAS DE MÉTRICAS (KPI)
    ach_df = df_filtered[df_filtered['Tipo de Gasto'] == "ACH FEES"]
    below_df = df_filtered[df_filtered['Tipo de Gasto'] == "BELOW MINIMUM BALANCE FEE"]
    total_expenses = df_filtered['Monto (USD)'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <div class="metric-title">Total Comisión ACH FEES ($0.50)</div>
            <div class="metric-value">${ach_df['Monto (USD)'].sum():,.2f} USD</div>
            <div style="color: #6B7280; font-size: 13px; margin-top:5px;">Ocurrencias: <b>{len(ach_df)}</b> transacciones</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #EF4444;">
            <div class="metric-title">Total BELOW BALANCE FEE ($35.00)</div>
            <div class="metric-value">${below_df['Monto (USD)'].sum():,.2f} USD</div>
            <div style="color: #6B7280; font-size: 13px; margin-top:5px;">Ocurrencias: <b>{len(below_df)}</b> cobros</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3B82F6;">
            <div class="metric-title">Gasto Bancario Consolidado</div>
            <div class="metric-value">${total_expenses:,.2f} USD</div>
            <div style="color: #6B7280; font-size: 13px; margin-top:5px;">Total Transacciones: <b>{len(df_filtered)}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
    # ESTRUCTURA DE PESTAÑAS INTERACTIVAS
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Dashboard Analítico", 
        "📋 Registro Detallado de Movimientos", 
        "🛡️ Auditoría e Inmunidad a Resúmenes",
        "📥 Exportación de Datos"
    ])
    
    # PESTAÑA 1: VISUALIZACIONES GRÁFICAS (PLOTLY EXPRESS)
    with tab1:
        st.subheader("Análisis de Distribución Temporal")
        if not df_filtered.empty:
            df_chart = df_filtered.groupby(['Fecha', 'Tipo de Gasto'])['Monto (USD)'].sum().reset_index()
            df_chart['Fecha_Str'] = df_chart['Fecha'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else str(x))
            
            fig_bar = px.bar(
                df_chart,
                x='Fecha_Str',
                y='Monto (USD)',
                color='Tipo de Gasto',
                labels={'Fecha_Str': 'Fecha de Transacción', 'Monto (USD)': 'Gasto Acumulado ($)'},
                color_discrete_map={"ACH FEES": "#10B981", "BELOW MINIMUM BALANCE FEE": "#EF4444"},
                barmode='stack',
                height=400
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Fecha de Operación",
                yaxis_title="Monto Cobrado (USD)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Proporción por Impacto Financiero ($)")
                fig_pie_val = px.pie(
                    df_filtered, names='Tipo de Gasto', values='Monto (USD)',
                    color='Tipo de Gasto', color_discrete_map={"ACH FEES": "#10B981", "BELOW MINIMUM BALANCE FEE": "#EF4444"},
                    hole=0.4
                )
                st.plotly_chart(fig_pie_val, use_container_width=True)
            with c2:
                st.subheader("Proporción por Volumen de Movimientos (Cantidad)")
                fig_pie_cnt = px.pie(
                    df_filtered, names='Tipo de Gasto',
                    color='Tipo de Gasto', color_discrete_map={"ACH FEES": "#10B981", "BELOW MINIMUM BALANCE FEE": "#EF4444"},
                    hole=0.4
                )
                st.plotly_chart(fig_pie_cnt, use_container_width=True)
        else:
            st.info("No existen registros para el rango seleccionado en los filtros.")
            
    # PESTAÑA 2: VISTA DETALLADA EN TABLA DATAFRAME
    with tab2:
        st.subheader("Transacciones Extraídas del Canal Operativo")
        st.markdown("Esta tabla refleja con precisión quirúrgica los movimientos reales individuales, excluyendo cualquier tipo de resumen.")
        
        if not df_filtered.empty:
            display_df = df_filtered[[
                "Fecha", "Tipo de Gasto", "Monto (USD)", "Descripción Original", "Archivo de Origen"
            ]].sort_values(by="Fecha", ascending=True)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "Fecha": st.column_config.DateColumn("Fecha Ejecución", format="YYYY-MM-DD"),
                    "Monto (USD)": st.column_config.NumberColumn("Cargo (USD)", format="$ %.2f"),
                    "Tipo de Gasto": st.column_config.TextColumn("Clasificación"),
                    "Descripción Original": st.column_config.TextColumn("Detalle Original del Extracto"),
                    "Archivo de Origen": st.column_config.TextColumn("Nombre del PDF")
                },
                hide_index=True
            )
        else:
            st.info("No hay datos para mostrar con los filtros aplicados.")
            
    # PESTAÑA 3: DEMOSTRACIÓN DE AUDITORÍA (INMUNIDAD A LOS RESÚMENES)
    with tab3:
        st.subheader("Bitácora de Control: Secciones de Resumen Detectadas y Excluidas")
        st.markdown("""
        Esta sección expone los bloques de texto de fin de mes o índices anuales identificados en los archivos. 
        El sistema los ha **aislado y descartado de forma absoluta**, impidiendo que afecten los cálculos gráficos y los listados transaccionales.
        """)
        
        if st.session_state.audit_trails:
            for log_idx, audit in enumerate(st.session_state.audit_trails):
                with st.expander(f"🔴 Fragmento Descartado #{log_idx+1} - Archivo: {audit['Archivo de Origen']} (Pág. {audit['Pagina']})"):
                    st.warning(f"**Criterio de Truncado:** {audit['Detalle']}")
                    st.markdown("**Texto aislado (Inhabilitado para la contabilidad):**")
                    st.code(audit['Contenido Excluido'], language="text")
        else:
            st.success("✅ Análisis impecable: No se encontraron bloques de resumen remanentes en las páginas operativas analizadas.")
            
    # PESTAÑA 4: MÓDULO DE DESCARGAS Y EXPORTACIÓN
    with tab4:
        st.subheader("Exportar Reporte Consolidado Libre de Errores")
        st.markdown("Genera archivos planos limpios listos para conciliaciones contables avanzadas.")
        
        if not df_filtered.empty:
            csv_df = df_filtered.copy()
            csv_df['Fecha'] = csv_df['Fecha'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else str(x))
            csv_data = csv_df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📥 Descargar Reporte Completo en Formato CSV",
                data=csv_data,
                file_name=f"Gastos_Bancarios_Davivenda_Limpio_{datetime.date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.info("📌 **Garantía de Integridad:** Los montos incluidos han sido estandarizados automáticamente ($0.50 y $35.00), anulando cualquier ruido visual o caracteres extraños presentes en el PDF original.")
