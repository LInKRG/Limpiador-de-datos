import streamlit as st
import pandas as pd
from io import BytesIO
#& "C:\Users\mat\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m streamlit run app.py            

# Configuración de la página
st.set_page_config(
    page_title="Limpiador Automático de Datos",
    page_icon="🧹",
    layout="centered"
)

st.title("🧹 Limpiador & Validador de Planillas")
st.write(
    "Sube cualquier planilla con datos de clientes o ventas (Excel o CSV). "
    "El sistema limpiará espacios sobrantes, eliminará duplicados y estandarizará el formato de forma automática."
)

# 1. Componente para subir archivo
archivo = st.file_uploader("Sube tu archivo sucio (.xlsx o .csv)", type=["xlsx", "csv"])

if archivo is not None:
    # Cargar datos según la extensión
    try:
        if archivo.name.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)
            
        st.subheader("📋 Vista Previa de los Datos Originales:")
        st.dataframe(df.head(), use_container_width=True)
        
        filas_iniciales = len(df)
        
        # 2. Botón para ejecutar la limpieza
        if st.button("🚀 Limpiar y Optimizar Datos", type="primary"):
            with st.spinner("Procesando y limpiando datos..."):
                
                # Copia para no alterar el original en memoria
                df_limpio = df.copy()
                
                # REGLA 1: Eliminar filas totalmente vacías
                df_limpio.dropna(how="all", inplace=True)
                
                # REGLA 2: Limpiar espacios de más y estandarizar strings en columnas de texto
                for col in df_limpio.select_dtypes(include=["object"]).columns:
                    # Elimina espacios al inicio/final y pasa a string por seguridad
                    df_limpio[col] = df_limpio[col].astype(str).str.strip()
                    # Opcional: estandarizar correos a minúsculas si la columna se llama email o correo
                    if "email" in col.lower() or "correo" in col.lower():
                        df_limpio[col] = df_limpio[col].str.lower()

                # REGLA 3: Eliminar duplicados exactos
                duplicados_eliminados = df_limpio.duplicated().sum()
                df_limpio.drop_duplicates(inplace=True)
                
                filas_finales = len(df_limpio)
                filas_eliminadas = filas_iniciales - filas_finales

            # 3. Mostrar métricas de éxito en pantalla
            st.success("¡Limpieza completada con éxito!")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Filas Originales", filas_iniciales)
            col2.metric("Duplicados Eliminados", duplicados_eliminados)
            col3.metric("Filas Finales Limpias", filas_finales)
            
            st.subheader("✨ Vista Previa de los Datos Limpios:")
            st.dataframe(df_limpio.head(), use_container_width=True)
            
            # 4. Preparar botón de descarga
            @st.cache_data
            def convertir_a_excel(df_resultado):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_resultado.to_excel(writer, index=False)
                return output.getvalue()
            
            excel_bytes = convertir_a_excel(df_limpio)
            
            st.download_button(
                label="📥 Descargar Archivo Limpio en Excel",
                data=excel_bytes,
                file_name="datos_limpios_reporte.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")