import streamlit as st
import pandas as pd
import json
import io

# Función para procesar la base de datos Flokzu a ADM/Bodega
def transformar_datos_flokzu_adm(df):
    nuevos_datos = []

    # Verificar los nombres de las columnas
    st.write("Columnas del DataFrame:", df.columns.tolist())

    # Asegurarse de que todas las columnas necesarias estén presentes
    required_columns = ['Id', 'Ticket', 'Instalacion', 'Tecnicos', 'Material Usado', 'cliente', 'serie', 'fecha']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"La columna '{col}' no está presente en el archivo.")
            return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

    for index, row in df.iterrows():
        id_ = row['Id']
        ticket = row['Ticket']
        instalacion = row['Instalacion']
        tecnicos = row['Tecnicos']
        materiales_usados = row['Material Usado']
        cliente = row['cliente']
        fecha = row['fecha']
        series = row['serie']

        # Verifica y carga JSON solo si no es NaN
        if pd.notna(tecnicos):
            tecnicos = json.loads(tecnicos)
        else:
            tecnicos = []

        if pd.notna(materiales_usados):
            materiales_usados = json.loads(materiales_usados)
        else:
            materiales_usados = []

        if pd.notna(series):
            series = json.loads(series)
        else:
            series = []

        numeros_de_serie = [serie["numero de serie"] for serie in series] if series else ["--"]
        tipos_de_serie = [serie["serie"] for serie in series] if series else ["--"]

        tecnicos_nombres = ', '.join([tecnico['lbl'] for tecnico in tecnicos]) if tecnicos else "--"

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
                'serie': '//'.join(numeros_de_serie),
                'tipo de serie': '//'.join(tipos_de_serie),
                'fecha': fecha
            }
            nuevos_datos.append(nuevo_registro)

        # Si no hay materiales, agregar un registro vacío para los materiales
        if not materiales_usados:
            nuevo_registro = {
                'Id': id_,
                'Ticket': ticket,
                'Instalacion': instalacion,
                'Tecnicos': tecnicos_nombres,
                'Material Usado': "--",
                'Cantidad': "--",
                'Dueño del material': "--",
                'cliente': cliente,
                'serie': '//'.join(numeros_de_serie),
                'tipo de serie': '//'.join(tipos_de_serie),
                'fecha': fecha
            }
            nuevos_datos.append(nuevo_registro)

    return pd.DataFrame(nuevos_datos)

# Agregar otras funciones de transformación para otros tipos de bases de datos aquí
# ...

st.title("Transformador de Bases de Datos")

# Selector de tipo de base de datos
tipo_bd = st.selectbox("Selecciona el tipo de base de datos que deseas subir", 
                       ["Flokzu a ADM/Bodega", "Otro tipo de base de datos"])

uploaded_file = st.file_uploader("Sube tu archivo CSV o Excel", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, delimiter=';')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        # Mostrar los nombres de las columnas del archivo cargado
        st.write("Columnas del archivo:", df.columns.tolist())

        # Seleccionar la función de transformación en base al tipo de base de datos
        if tipo_bd == "Flokzu a ADM/Bodega":
            df_nuevo = transformar_datos_flokzu_adm(df)
        else:
            st.error("Funcionalidad para este tipo de base de datos aún no implementada.")
            df_nuevo = pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

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
        st.error(f"Error al procesar el archivo: {e}")