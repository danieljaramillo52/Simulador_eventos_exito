import re

cadena = "5%-10%"
numeros = tuple(map(int, re.findall(r"\d+", cadena)))
list_posbiles_dctos = [num for num in range(numeros[0], numeros[1] + 1)]
list_posbiles_dcto_por = [str(num) + "%" for num in list_posbiles_dctos]


import streamlit as st
import st_file_uploader as stf
import pandas as pd

st.title("Cargador de Archivos Personalizado")

# Crear una instancia del uploader personalizado
custom_uploader = stf.create_custom_uploader(
    uploader_msg="📎 Arrastra y suelta tu archivo aquí o haz clic para buscar.",
    limit_msg="Tamaño máximo: 200MB",
    button_msg="Seleccionar archivo",
    icon="MdFileUpload"
)

# Usar el uploader para cargar archivos
archivos = custom_uploader.file_uploader(
    "Sube tus archivos",
    type=["xlsx", "csv"],
    accept_multiple_files=True
)

# Procesar los archivos subidos
if archivos:
    for archivo in archivos:
        st.success(f"Archivo cargado: {archivo.name}")
        if archivo.name.endswith('.csv'):
            df = pd.read_csv(archivo)
            st.write(df.head())
        elif archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
            st.write(df.head())
