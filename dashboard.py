import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Título del Dashboard
st.title("Dashboard del Modelo")

# Archivo CSV predeterminado
CSV_FILE = 'registro.csv'

# Cargar datos del CSV
try:
    data = pd.read_csv(CSV_FILE)

    # Verificar que las columnas necesarias estén presentes
    columnas = ['prediction', 'OCCUPATION_TYPE_TEXT', 'CODE_GENDER_F', 'CODE_GENDER_M']
    faltantes = [col for col in columnas if col not in data.columns]
    if faltantes:
        st.error(f"El archivo CSV debe contener las columnas: {', '.join(faltantes)}")
    else:
    # Gráfico de barras comparativo entre resultados generados para 0 y 1
        st.subheader("Número de predicciones para 0 y 1")
        conteo_resultado = data['prediction'].value_counts().reset_index()
        conteo_resultado.columns = ['Prediction', 'Count']
        fig1 = px.bar(conteo_resultado,x='Prediction', y='Count', labels={"Prediction": "Predicción", 
                                                                          "Count": "Cantidad"})
        st.plotly_chart(fig1)
    # Gráfico de barras para OCCUPATION_TYPE_TEXT con columnas para 0 y 1
        st.subheader("Distribución por OCCUPATION_TYPE_TEXT")
        conteo_ocupacion = data.groupby(['OCCUPATION_TYPE_TEXT', 'prediction']).size().reset_index(name='Count')
        fig2 = px.bar(conteo_ocupacion, x='OCCUPATION_TYPE_TEXT', y='Count', barmode='group',
            labels={"OCCUPATION_TYPE_TEXT": "Tipo de Ocupación", "Count": "Cantidad", "prediction": "Predicción"})
        st.plotly_chart(fig2)
    # Comparación entre sexos mostrando columnas para cada género y predicción
        st.subheader("Distribución de Predicciones entre Generos")
        conteo_genero = {"Femenino 0": data[(data['CODE_GENDER_F'] == 1) & (data['prediction'] == 0)].shape[0],
                         "Femenino 1": data[(data['CODE_GENDER_F'] == 1) & (data['prediction'] == 1)].shape[0],
                         "Masculino 0": data[(data['CODE_GENDER_M'] == 1) & (data['prediction'] == 0)].shape[0],
                         "Masculino 1": data[(data['CODE_GENDER_M'] == 1) & (data['prediction'] == 1)].shape[0]}
        df_genero = pd.DataFrame(list(conteo_genero.items()), columns = ['Category', 'Count'])
        fig3 = px.bar(df_genero,x='Category', y='Count',labels={"Category": "Categoría", "Count": "Cantidad"})
        st.plotly_chart(fig3)

        st.success("¡Dashboard generado correctamente!")
except FileNotFoundError:
    st.error(f"El archivo '{CSV_FILE}' no se encontró. Por favor, asegúrate de que existe en el directorio.")