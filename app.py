import streamlit as st
import pandas as pd
import json
import io

def transformar_datos(df):
    nuevos_datos = []

    # Verificar los nombres de las columnas
    st.write("Columnas del DataFrame:", df.columns.tolist())

    # Asegurarse de que todas las columnas necesarias estén presentes
    required_columns = ['Id', 'Ticket', 'Instalacion', 'Tecnicos', 'Material Usado', 'cliente', 'fecha']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"La columna '{col}' no está presente en el archivo CSV.")
            return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

    for index, row in df.iterrows():
        id_ = row['Id']
        ticket = row['Ticket']
        instalacion = row['Instalacion']
        tecnicos = json.loads(row['Tecnicos'])
        materiales_usados = json.loads(row['Material Usado'])
        cliente = row['cliente']
        fecha = row['fecha']

        tecnicos_nombres = ', '.join([tecnico['lbl'] for tecnico in tecnicos])

        for material in materiales_usados:
            nuevo_registro = {
                'Id': id_,
                'Ticket': ticket,
                'Instalacion': instalacion,
                'Tecnicos': tecnicos_nombres,
                'Material Usado': material['materiales'],
                'Cantidad': material['cantidad'],
                'Dueño del material': material['Dueño del material'],
                'cliente': cliente,
                'fecha': fecha
            }
            nuevos_datos.append(nuevo_registro)

    return pd.DataFrame(nuevos_datos)

st.title("Transformador de CSV a Excel")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, delimiter=';')
        # Mostrar los nombres de las columnas del CSV cargado
        st.write("Columnas del archivo CSV:", df.columns.tolist())

        df_nuevo = transformar_datos(df)

        if not df_nuevo.empty:
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df_nuevo.to_excel(writer, index=False, sheet_name='Registro fichas')
            writer.close()  # Usa close() en lugar de save()
            processed_data = output.getvalue()

            st.download_button(
                label="Descargar archivo Excel",
                data=processed_data,
                file_name="output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.dataframe(df_nuevo)
    except Exception as e:
        st.error(f"Error al procesar el archivo CSV: {e}")