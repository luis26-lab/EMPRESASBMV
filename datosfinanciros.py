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
# DICCIONARIO DE EMPRESAS DEL IPC (Oficiales)
# ==========================================
empresas_ipc = {
    'Alfa': 'ALFAA.MX',
    'América Móvil': 'AMXL.MX',
    'Arca Continental': 'AC.MX',
    'Banco del Bajío': 'BBAJIO.MX',
    'Bimbo': 'BIMBOA.MX',
    'Bolsa Mexicana de Valores': 'BOLSAA.MX',
    'Cemex': 'CEMEXCPO.MX',
    'Chedraui': 'CHDRAUIB.MX',
    'CIE': 'CIEB.MX',
    'Consorcio Ara': 'ARA.MX',
    'El Puerto de Liverpool': 'LIVEPOLC1.MX',
    'FEMSA': 'FEMSAUBD.MX',
    'Genomma Lab': 'LABB.MX',
    'Grupo Aeroportuario del Pacífico (GAP)': 'GAPB.MX',
    'Grupo Aeroportuario del Centro Norte (OMA)': 'OMAB.MX',
    'Grupo Aeroportuario del Sureste (ASUR)': 'ASURB.MX',
    'Grupo Carso': 'GCARSOA1.MX',
    'Grupo Elektra': 'ELEKTRA.MX',
    'Grupo Financiero Banorte': 'GFNORTEO.MX',
    'Grupo Financiero Inbursa': 'GFINBURO.MX',
    'Grupo México': 'GMEXICOB.MX',
    'Grupo Simec': 'SIMECB.MX',
    'Gruma': 'GRUMA.MX',
    'Herdez': 'HERDEZ.MX',
    'Kimberly-Clark': 'KIMBERA.MX',
    'La Lala': 'LALA.MX',
    'Megacable': 'MEGACPO.MX',
    'Peñoles': 'PEÑOLES.MX',
    'Pinfra': 'PINFRA.MX',
    'Rotoplas': 'AGUA.MX',
    'Soriana': 'SORIANA.MX',
    'Televisa': 'TLEVISACPO.MX',
    'Walmex': 'WALMEX.MX'
}

# Ordenar alfabéticamente para la lista desplegable
empresas_ipc = dict(sorted(empresas_ipc.items()))

# ==========================================
# PESTAÑA 1: ANÁLISIS FINANCIERO
# ==========================================
with tab1:
    st.header("Comparativa de Empresas del IPC")
    
    # Lista desplegable (multiselect)
    empresas_seleccionadas = st.multiselect(
        "Selecciona hasta 5 empresas para analizar:",
        options=list(empresas_ipc.keys()),
        default=['Walmex', 'América Móvil', 'Grupo Financiero Banorte'],
        max_selections=5
    )

    if empresas_seleccionadas:
        with st.spinner('Descargando datos financieros de Yahoo Finance...'):
            
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
                    
                    ingresos = financials.loc['Total Revenue', ultimos_3].values / 1e9
                    neto = financials.loc['Net Income', ultimos_3].values / 1e9
                    
                    data_ingresos[empresa] = ingresos
                    data_neto[empresa] = neto
                    
                    activos = balance.loc['Total Assets', balance.columns[0]]
                    roa = (neto[0] * 1e9) / activos * 100 if activos and not pd.isna(activos) else 0
                    
                    capital = balance.loc['Stockholders Equity', balance.columns[0]]
                    roe = (neto[0] * 1e9) / capital * 100 if capital and not pd.isna(capital) else 0
                    
                    eps = info.get('trailingEps', 0) or 0
                    
                    data_ratios[empresa] = {
                        'ROA (%)': round(roa, 2),
                        'ROE (%)': round(roe, 2),
                        'EPS / UPA ($)': round(eps, 2)
                    }
                except Exception:
                    pass

            st.subheader("1️⃣ Ingresos Totales (Miles de Millones USD)")
            if data_ingresos:
                df_ingresos = pd.DataFrame(data_ingresos, index=años_cols).T
                df_ingresos.index.name = 'Empresa'
                st.dataframe(df_ingresos, use_container_width=True)
                st.bar_chart(df_ingresos)

            st.markdown("---")

            st.subheader("2️⃣ Utilidad Neta (Miles de Millones USD)")
            if data_neto:
                df_neto = pd.DataFrame(data_neto, index=años_cols).T
                df_neto.index.name = 'Empresa'
                st.dataframe(df_neto, use_container_width=True)
                st.bar_chart(df_neto)

            st.markdown("---")

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

            st.markdown("---")
            st.subheader("💡 ¿Qué significan estos números? (Guía rápida)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **🏭 ROA (Retorno sobre Activos)**
                Mide qué tan eficiente es la empresa usando sus máquinas, edificios y recursos para ganar dinero.
                *Ejemplo:* Un ROA del **10%** significa que por cada **$100 pesos** en activos, la empresa generó **$10 pesos** de utilidad.
                """)
                
            with col2:
                st.markdown("""
                **💰 ROE (Retorno sobre Capital)**
                Mide cuánto rendimiento le está dando la empresa a los accionistas por su inversión.
                *Ejemplo:* Un ROE del **15%** significa que por cada **$100 pesos** que invertiste, la empresa te generó **$15 pesos** de ganancia.
                """)
                
            with col3:
                st.markdown("""
                **📈 EPS / UPA (Utilidad por Acción)**
                Es la porción de la utilidad neta que le "toca" a cada acción individual.
                *Ejemplo:* Un EPS de **$2.50** significa que cada acción de la empresa generó **$2.50 pesos** de utilidad neta.
                """)

    else:
        st.info("👈 Por favor, selecciona al menos una empresa en el menú de arriba para ver los datos.")

# ==========================================
# PESTAÑA 2: (VACÍA POR AHORA)
# ==========================================
with tab2:
    st.header("Próximamente")
    st.write("Aquí agregaremos más análisis, como gráficas de precios de las acciones o comparativas de dividendos.")
