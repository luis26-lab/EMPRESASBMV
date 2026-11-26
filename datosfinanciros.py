import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Dashboard Financiero IPC", layout="wide", page_icon="📊")

# Título principal
st.title("📊 Dashboard Financiero: Empresas del IPC (BMV)")

# Crear las pestañas
tab1, tab2 = st.tabs(["🏢 Análisis Financiero", "📈 Próximamente..."])

# ==========================================
# DICCIONARIO DE EMPRESAS DEL IPC
# ==========================================
empresas_ipc = {
    'Alfa': 'ALFAA.MX', 'América Móvil': 'AMXL.MX', 'Arca Continental': 'AC.MX',
    'Banco del Bajío': 'BBAJIO.MX', 'Bimbo': 'BIMBOA.MX', 'Bolsa Mexicana de Valores': 'BOLSAA.MX',
    'Cemex': 'CEMEXCPO.MX', 'Chedraui': 'CHDRAUIB.MX', 'CIE': 'CIEB.MX',
    'Consorcio Ara': 'ARA.MX', 'El Puerto de Liverpool': 'LIVEPOLC1.MX', 'FEMSA': 'FEMSAUBD.MX',
    'Genomma Lab': 'LABB.MX', 'Grupo Aeroportuario del Pacífico (GAP)': 'GAPB.MX',
    'Grupo Aeroportuario del Centro Norte (OMA)': 'OMAB.MX', 'Grupo Aeroportuario del Sureste (ASUR)': 'ASURB.MX',
    'Grupo Carso': 'GCARSOA1.MX', 'Grupo Elektra': 'ELEKTRA.MX', 'Grupo Financiero Banorte': 'GFNORTEO.MX',
    'Grupo Financiero Inbursa': 'GFINBURO.MX', 'Grupo México': 'GMEXICOB.MX', 'Grupo Simec': 'SIMECB.MX',
    'Gruma': 'GRUMA.MX', 'Herdez': 'HERDEZ.MX', 'Kimberly-Clark': 'KIMBERA.MX',
    'La Lala': 'LALA.MX', 'Megacable': 'MEGACPO.MX', 'Peñoles': 'PEÑOLES.MX',
    'Pinfra': 'PINFRA.MX', 'Rotoplas': 'AGUA.MX', 'Soriana': 'SORIANA.MX',
    'Televisa': 'TLEVISACPO.MX', 'Walmex': 'WALMEX.MX'
}

empresas_ipc = dict(sorted(empresas_ipc.items()))

# ==========================================
# PESTAÑA 1: ANÁLISIS FINANCIERO
# ==========================================
with tab1:
    st.header("Comparativa de Empresas del IPC")
    
    empresas_seleccionadas = st.multiselect(
        "Selecciona hasta 5 empresas para analizar:",
        options=list(empresas_ipc.keys()),
        default=['Walmex', 'América Móvil', 'Grupo Financiero Banorte'],
        max_selections=5
    )

    if empresas_seleccionadas:
        with st.spinner('Descargando datos financieros...'):
            
            data_ingresos = {}
            data_neto = {}
            data_ratios = {}
            años_cols = []

            for empresa in empresas_seleccionadas:
                ticker = yf.Ticker(empresas_ipc[empresa])
                
                try:
                    financials = ticker.financials
                    balance = ticker.balance_sheet
                    info = ticker.info
                    
                    if financials.empty or balance.empty:
                        continue
                        
                    ultimos_3 = financials.columns[:3]
                    if not años_cols:
                        años_cols = [str(col.year) for col in ultimos_3]
                    
                    # --- INGRESOS (Con validación para evitar errores como el de América Móvil) ---
                    if 'Total Revenue' in financials.index:
                        ingresos = financials.loc['Total Revenue', ultimos_3].values / 1e9
                        data_ingresos[empresa] = ingresos
                    else:
                        data_ingresos[empresa] = [np.nan, np.nan, np.nan]

                    if 'Net Income' in financials.index:
                        neto = financials.loc['Net Income', ultimos_3].values / 1e9
                        data_neto[empresa] = neto
                    else:
                        data_neto[empresa] = [np.nan, np.nan, np.nan]
                    
                    # --- RATIOS ---
                    activos = balance.loc['Total Assets', balance.columns[0]] if 'Total Assets' in balance.index else 0
                    roa = (neto[0] * 1e9) / activos * 100 if activos and not pd.isna(activos) else 0
                    
                    capital = balance.loc['Stockholders Equity', balance.columns[0]] if 'Stockholders Equity' in balance.index else 0
                    roe = (neto[0] * 1e9) / capital * 100 if capital and not pd.isna(capital) else 0
                    
                    eps = info.get('trailingEps', 0) or 0
                    
                    data_ratios[empresa] = {
                        'ROA (%)': round(roa, 2),
                        'ROE (%)': round(roe, 2),
                        'EPS / UPA ($)': round(eps, 2)
                    }
                except Exception:
                    pass

            # ==========================================
            # 1. INGRESOS TOTALES (TABLA + GRÁFICO DE LÍNEA)
            # ==========================================
            st.subheader("1️⃣ Ingresos Totales (Miles de Millones USD)")
            if data_ingresos:
                # Tabla: Empresas en filas, Años en columnas
                df_ingresos_tabla = pd.DataFrame(data_ingresos, index=años_cols).T
                df_ingresos_tabla.index.name = 'Empresa'
                st.dataframe(df_ingresos_tabla, use_container_width=True)
                
                # Gráfico de Línea: Años en el eje X, Empresas como líneas
                df_ingresos_linea = pd.DataFrame(data_ingresos, index=años_cols)
                st.line_chart(df_ingresos_linea)

            st.markdown("---")

            # ==========================================
            # 2. UTILIDAD NETA (TABLA + GRÁFICO DE BARRAS)
            # ==========================================
            st.subheader("2️⃣ Utilidad Neta (Miles de Millones USD)")
            if data_neto:
                df_neto_tabla = pd.DataFrame(data_neto, index=años_cols).T
                df_neto_tabla.index.name = 'Empresa'
                st.dataframe(df_neto_tabla, use_container_width=True)
                st.bar_chart(df_neto_tabla)

            st.markdown("---")

            # ==========================================
            # 3. RATIOS (TABLA + GRÁFICOS)
            # ==========================================
            st.subheader("3️⃣ Indicadores de Rentabilidad (Año más reciente)")
            if data_ratios:
                df_ratios = pd.DataFrame(data_ratios).T
                df_ratios.index.name = 'Empresa'
                st.dataframe(df_ratios, use_container_width=True)
                
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.markdown("**ROA vs ROE (%)**")
                    st.bar_chart(df_ratios[['ROA (%)', 'ROE (%)']])
                with col_chart2:
                    st.markdown("**EPS / UPA ($)**")
                    st.bar_chart(df_ratios[['EPS / UPA ($)']])

            # ==========================================
            # EXPLICACIÓN FINANCIERA
            # ==========================================
            st.markdown("---")
            st.subheader("💡 ¿Qué significan estos números? (Guía rápida)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🏭 ROA:** Mide la eficiencia con sus activos. Un 10% significa que por cada $100 en activos, generó $10 de utilidad.")
            with col2:
                st.markdown("**💰 ROE:** Mide el rendimiento para el accionista. Un 15% significa que por cada $100 invertidos, generó $15 de ganancia.")
            with col3:
                st.markdown("**📈 EPS / UPA:** Es la porción de utilidad que le toca a cada acción. Un EPS de $2.50 significa que cada acción generó $2.50.")

    else:
        st.info("👈 Por favor, selecciona al menos una empresa en el menú de arriba para ver los datos.")

# ==========================================
# PESTAÑA 2
# ==========================================
with tab2:
    st.header("Próximamente")
    st.write("Aquí agregaremos más análisis, como gráficas de precios de las acciones o comparativas de dividendos.")
