import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Dashboard Financiero México", layout="wide")

# Título principal
st.title("📊 Dashboard Financiero: Empresas Mexicanas")

# Crear las pestañas
tab1, tab2 = st.tabs(["🏢 Análisis Financiero", "📈 Próximamente..."])

# ==========================================
# PESTAÑA 1: ANÁLISIS FINANCIERO
# ==========================================
with tab1:
    st.header("Comparativa de Empresas de la BMV")
    
    # Diccionario de empresas mexicanas y sus tickers en Yahoo Finance
    empresas_dict = {
        'Walmex': 'WALMEX.MX',
        'América Móvil': 'AMXL.MX',
        'Grupo Financiero Banorte': 'GFNORTEO.MX',
        'FEMSA': 'FEMSAUBD.MX',
        'Cemex': 'CEMEXCPO.MX',
        'Grupo México': 'GMEXICOB.MX',
        'Bimbo': 'BIMBOA.MX',
        'Alfa': 'ALFAA.MX'
    }

    # Lista desplegable (multiselect) para elegir hasta 5 empresas
    empresas_seleccionadas = st.multiselect(
        "Selecciona hasta 5 empresas para analizar:",
        options=list(empresas_dict.keys()),
        default=['Walmex', 'América Móvil', 'Grupo Financiero Banorte'],
        max_selections=5
    )

    if empresas_seleccionadas:
        st.subheader("1️⃣ Ingresos e Ingresos Netos (Últimos 3 años)")
        
        # Variables para guardar los datos
        datos_ingresos = {}
        datos_ratios = {}
        
        # Descargar datos de cada empresa
        for empresa in empresas_seleccionadas:
            ticker = yf.Ticker(empresas_dict[empresa])
            
            try:
                # Obtener Estado de Resultados (Ingresos) y Balance General
                financials = ticker.financials
                balance = ticker.balance_sheet
                
                # Tomar los últimos 3 años disponibles (las columnas están ordenadas de más reciente a más antigua)
                ultimos_3_anios = financials.columns[:3]
                años_str = [str(col.year) for col in ultimos_3_anios]
                
                # Extraer Ingresos Totales y Utilidad Neta
                ingresos = financials.loc['Total Revenue', ultimos_3_anios].values / 1e9 # En miles de millones
                neto = financials.loc['Net Income', ultimos_3_anios].values / 1e9
                
                datos_ingresos[empresa] = {
                    'Años': años_str,
                    'Ingresos Totales (MMD)': ingresos,
                    'Ingresos Netos (MMD)': neto
                }
                
                # Calcular ROA, ROE y EPS para el año más reciente
                # ROA = Utilidad Neta / Activos Totales
                activos = balance.loc['Total Assets', balance.columns[0]]
                roa = (neto[0] * 1e9) / activos * 100 if activos else 0
                
                # ROE = Utilidad Neta / Capital Contable
                capital = balance.loc['Stockholders Equity', balance.columns[0]]
                roe = (neto[0] * 1e9) / capital * 100 if capital else 0
                
                # EPS (UPA) = Utilidad Neta / Número de Acciones
                # Usamos el EPS directo de Yahoo Finance si está disponible, si no, lo calculamos
                info = ticker.info
                eps = info.get('trailingEps', 0)
                
                datos_ratios[empresa] = {
                    'ROA (%)': round(roa, 2),
                    'ROE (%)': round(roe, 2),
                    'EPS / UPA ($)': round(eps, 2)
                }
            except Exception as e:
                st.warning(f"No se pudieron obtener todos los datos de {empresa}. Revisa el ticker.")

        # --- MOSTRAR INGRESOS EN TABLA ---
        if datos_ingresos:
            # Crear DataFrame para mostrarlo bonito
            df_ingresos = []
            for emp, data in datos_ingresos.items():
                for i in range(3):
                    df_ingresos.append({
                        'Empresa': emp,
                        'Año': data['Años'][i],
                        'Ingresos Totales (MMD USD)': round(data['Ingresos Totales (MMD)'][i], 2),
                        'Ingresos Netos (MMD USD)': round(data['Ingresos Netos (MMD)'][i], 2)
                    })
            df_final = pd.DataFrame(df_ingresos)
            st.dataframe(df_final, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("2️⃣ Indicadores de Rentabilidad (Año más reciente)")
        
        # --- MOSTRAR ROA, ROE, EPS EN TABLA ---
        if datos_ratios:
            df_ratios = pd.DataFrame(datos_ratios).T
            df_ratios.index.name = 'Empresa'
            st.dataframe(df_ratios, use_container_width=True)

        # --- EXPLICACIÓN FINANCIERA SENCILLA ---
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