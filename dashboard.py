import pandas as pd
import plotly.express as px
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
        # Primera gráfica: Número de predicciones
        st.subheader("Número de Predicciones para 0 y 1")
        conteo_resultado = data['prediction'].value_counts().reset_index()
        conteo_resultado.columns = ['Prediction', 'Count']
        color_mapping = {0: 'orange', 1: 'blue'}
        fig1 = px.bar(conteo_resultado, x='Prediction', y='Count', labels={"Prediction": "Predicción", "Count": "Cantidad"})
        fig1.update_traces(marker_color=[color_mapping[pred] for pred in conteo_resultado['Prediction']])
        st.plotly_chart(fig1)

        # Segunda gráfica: Ocupación con predicciones separadas
        st.subheader("Distribución de Predicciones por Tipo de Ocupación")
        conteo_ocupacion = data.groupby(['OCCUPATION_TYPE_TEXT', 'prediction']).size().reset_index(name='Count')

        # Separar las predicciones 0 y 1 en columnas distintas
        ocupacion_pivot = conteo_ocupacion.pivot(index='OCCUPATION_TYPE_TEXT', columns='prediction', values='Count').fillna(0)

        # Aplanar el DataFrame para su visualización
        ocupacion_pivot = ocupacion_pivot.reset_index().melt(id_vars=['OCCUPATION_TYPE_TEXT'], value_name='Count', var_name='Prediction')

        # Crear la gráfica con barras separadas
        fig2 = px.bar(ocupacion_pivot,x='OCCUPATION_TYPE_TEXT',y='Count',color='Prediction',barmode='group',  # Separar las barras
            color_discrete_map={0: 'orange', 1: 'blue'}, labels={"OCCUPATION_TYPE_TEXT": "Tipo de Ocupación",
                                                                "Count": "Cantidad","Prediction": "Predicción"})

        # Mejorar el diseño de la gráfica
        fig2.update_layout(xaxis={'categoryorder': 'total descending'}, legend_title_text="Predicción", xaxis_title="Tipo de Ocupación",
                           yaxis_title="Cantidad")
        st.plotly_chart(fig2)

        # Tercera gráfica: Distribución de predicciones entre géneros basada en comparación
        st.subheader("Distribución de Predicciones entre Géneros")

        # Determinar el género según el menor valor en las columnas CODE_GENDER_F y CODE_GENDER_M
        data['Gender'] = data.apply(lambda row: 'Femenino' if row['CODE_GENDER_F'] < row['CODE_GENDER_M'] else 'Masculino', axis=1)

        # Agrupar por género y predicción
        conteo_genero = data.groupby(['Gender', 'prediction']).size().reset_index(name='Count')

        # Separar las predicciones 0 y 1 en columnas distintas
        genero_pivot = conteo_genero.pivot(index='Gender', columns='prediction', values='Count').fillna(0)

        # Aplanar el DataFrame para su visualización
        genero_pivot = genero_pivot.reset_index().melt(id_vars=['Gender'], value_name='Count', var_name='Prediction')

        # Crear la gráfica con barras separadas
        fig3 = px.bar(genero_pivot,x='Gender',y='Count',color='Prediction',barmode='group',  # Separar las barras
            color_discrete_map={0: 'orange', 1: 'blue'},labels={"Gender": "Género","Count": "Cantidad","Prediction": "Predicción"})

        # Mejorar el diseño de la gráfica
        fig3.update_layout(xaxis={'categoryorder': 'total descending'},legend_title_text="Predicción",xaxis_title="Género",
            yaxis_title="Cantidad")
        st.plotly_chart(fig3)

        st.success("¡Dashboard generado correctamente!")
except FileNotFoundError:
    st.error(f"El archivo '{CSV_FILE}' no se encontró. Por favor, asegúrate de que existe en el directorio.")