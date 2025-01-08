from flask import Flask, request, render_template
import pickle
import pandas as pd
import csv
from datetime import datetime
import os

# Cargar el modelo entrenado
with open('modelo_entrenado.pkl', 'rb') as file:
    model = pickle.load(file)

# Crear la aplicación Flask
app = Flask(__name__)

# Descripciones y nombres de las características
DESCRIPCION = {
    'Días desde el nacimiento (negativo)': 'DAYS_BIRTH',
    'Genero Femenino': 'CODE_GENDER_F',
    'Genero Masculino': 'CODE_GENDER_M',
    'Nivel educativo del solicitante': 'NAME_EDUCATION_TYPE',
    'Casado': 'NAME_FAMILY_STATUS_Married',
    'Material de la pared (Panel)': 'WALLSMATERIAL_MODE_Panel',
    'Mediana del área de vivienda': 'LIVINGAREA_MEDI',
    'Moda del área total de vivienda': 'TOTALAREA_MODE',
    'Población relativa de la región': 'REGION_POPULATION_RELATIVE',
    'Dirección permanente no coincide con dirección de contacto': 'REG_CITY_NOT_LIVE_CITY',
    'Valoración de la región con la ciudad': 'REGION_RATING_CLIENT_W_CITY',
    'Vehículo': 'FLAG_OWN_CAR',
    'Antigüedad del vehículo': 'OWN_CAR_AGE',
    'Precio de los bienes adquiridos': 'AMT_GOODS_PRICE',
    'Incumplimientos sociales en 30 días': 'DEF_30_CNT_SOCIAL_CIRCLE',
    'Incumplimientos sociales en 60 días': 'DEF_60_CNT_SOCIAL_CIRCLE',
    'Puntuación externa 1': 'EXT_SOURCE_1',
    'Puntuación externa 2': 'EXT_SOURCE_2',
    'Puntuación externa 3': 'EXT_SOURCE_3',
    'Consultas al Buró en 1 año': 'AMT_REQ_CREDIT_BUREAU_YEAR',
    'Tipo de organización laboral': 'ORGANIZATION_TYPE',
    'Tipo de ingreso': 'NAME_INCOME_TYPE_Working',
    'Tipo de ocupación': 'OCCUPATION_TYPE',
    'Ingresos totales': 'AMT_INCOME_TOTAL',
    'Días desde cambio de registro': 'DAYS_REGISTRATION',
    'Días desde último cambio telefónico': 'DAYS_LAST_PHONE_CHANGE',
    'Días desde inicio del empleo': 'DAYS_EMPLOYED',
    'Días desde modificación del ID': 'DAYS_ID_PUBLISH',
    'Documento 3 proporcionado': 'FLAG_DOCUMENT_3',
    'Hora inicial de la solicitud': 'HOUR_APPR_PROCESS_START',
    'Préstamo Revolvente': 'NAME_CONTRACT_TYPE_Revolving_loans',
    'Préstamo Efectivo': 'NAME_CONTRACT_TYPE_Cash_loans',
    'Monto total del crédito solicitado': 'AMT_CREDIT',
    'Anualidad del préstamo solicitado': 'AMT_ANNUITY'}

# Mapas de codificación
OCCUPATION_TYPE_MAPPING = {'Laborers': 1.115921,
    'Drivers': 1.453029,'Accountants': -1.568286,'SIN VALOR': -0.720258,
    'Sales staff': 0.695458,'High skill tech staff': -0.817084,'Medicine staff': -0.495269,
    'Core staff': -0.770358,'Security staff': 1.190132,'Managers': -0.842543,
    'Waiters/barmen staff': 1.548814,'Private service staff': -0.675523,'Cooking staff': 1.110272,
    'Low-skill Laborers': 4.569172,'IT staff': -0.884279,'Realty agents': 0.003599,
    'HR staff': -0.489865,'Secretaries': -0.414423,'Cleaning staff': 0.669757}

ORGANIZATION_TYPE_MAPPING = {
    'Business Entity Type 2': 0.280971,'Other': -0.290331,'Business Entity Type 3': 0.600236,
    'Restaurant': 1.788947,'SIN VALOR': -1.352116,'Transport: type 3': 3.847703,
    'Self-employed': 1.06962,'Agriculture': 1.356071,'Government': -0.601667,
    'Industry: type 3': 1.359893,'Medicine': -0.664226,'University': -1.427472,
    'School': -1.118319,'Transport: type 4': 0.5101,'Security': 1.218736,
    'Electricity': -0.337673,'Trade: type 2': -0.622195,'Transport: type 2': -0.10769,
    'Industry: type 9': -0.709311,'Construction': 1.937046,'Industry: type 11': 0.135988,
    'Legal Services': 0.16356,'Military': -1.575637,'Kindergarten': -0.470213,
    'Industry: type 12': -1.988848,'Business Entity Type 1': -0.011559,'Police': -1.564803,
    'Housing': -0.092979,'Bank': -1.286568,'Industry: type 7': -0.16087,
    'Telecom': 0.056471,'Industry: type 2': 0.096888,'Trade: type 7': 0.681039,
    'Security Ministries': -1.502169,'Trade: type 3': 1.070783,'Trade: type 6': -2.004111,
    'Postal': -0.008837,'Services': -0.849278,'Advertising': 0.344241,
    'Hotel': -0.843681,'Industry: type 4': 0.642374,'Insurance': -1.200426,
    'Industry: type 1': 1.578343,'Industry: type 5': -0.710337,'Emergency': -0.543052,
    'Realtor': 1.67357,'Industry: type 10': -0.507087,'Culture': -0.996002,
    'Cleaning': 1.624067,'Trade: type 1': 0.890632,'Industry: type 6': -1.162994,
    'Trade: type 4': -2.113564,'Transport: type 1': -1.53659,'Religion': -1.138004,
    'Industry: type 13': 2.826541,'Trade: type 5': -2.7867,'Industry: type 8': 3.858624}

# Crear archivo de registro
registro = 'registro.csv'

# Verificar si el archivo ya existe y crear encabezado si no
def estado_registro():
    # Encabezado del csv
    encabezado_correcto = ['timestamp', 'OCCUPATION_TYPE_TEXT', 'ORGANIZATION_TYPE_TEXT'] + list(DESCRIPCION.values()) + ['prediction']
    # Si el archivo no existe, crea el archivo con el encabezado correcto
    if not os.path.exists(registro):
        # Permite un contenido sin espacios y con cierto tipo de caracteres
        with open(registro, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(encabezado_correcto)
        print(f"Encabezado creado en el archivo {registro}.")
    else:
        # Leer el encabezado actual del archivo
        with open(registro, 'r', encoding='utf-8') as f:
            encabezado_actual = f.readline().strip().split(',')
        
        if encabezado_actual != encabezado_correcto:
            # Si el encabezado es incorrecto, actualízalo
            df = pd.read_csv(registro)
            # Ajustar solo las columnas existentes
            df.columns = encabezado_correcto[:len(df.columns)]  
            df.to_csv(registro, index=False, encoding='utf-8')
            print(f"Encabezado actualizado en el archivo {registro}.")
        else:
            print(f"El archivo {registro} ya tiene el encabezado correcto.")
estado_registro()

# Validar y convertir datos del formulario
def validar_info(form_data, features, descripciones):
    # Diccionario para almacenar las características con formato válido
    datos = {}
    # Lista para almacenar las características con formato inválido
    errores = []
    # Bucle que itera sobre las variables
    for feature in features:
        try:
            # Validación específica para la variable 'OCCUPATION_TYPE'.
            if feature == 'OCCUPATION_TYPE':
                ocupacion = form_data[feature]
                # Verifica si el valor ingresado está en el diccionario de mapeo.
                if ocupacion not in OCCUPATION_TYPE_MAPPING:
                    # Si no está, genera un error indicando ocupación inválida.
                    raise ValueError(f"Ocupación inválida: {ocupacion}")
                # Asigna el valor numérico codificado al diccionario de datos válidos.
                datos[feature] = OCCUPATION_TYPE_MAPPING[ocupacion]
                # Genera una clave diferente 
                datos[f'{feature}_TEXT'] = ocupacion
            # Validación específica para la variable 'ORGANIZATION_TYPE'.
            elif feature == 'ORGANIZATION_TYPE':
                organizacion = form_data[feature]
                # Verifica si el valor ingresado está en el diccionario de mapeo.
                if organizacion not in ORGANIZATION_TYPE_MAPPING:
                    # Si no está, genera un error indicando ocupación inválida.
                    raise ValueError(f"Tipo de organización inválido: {organizacion}")
                # Asigna el valor numérico codificado al diccionario de datos válidos.
                datos[feature] = ORGANIZATION_TYPE_MAPPING[organizacion]
                # Genera una clave diferente 
                datos[f'{feature}_TEXT'] = organizacion
             # Validación genérica para variables numéricas.
            else:
                datos[feature] = float(form_data[feature])
        # Valores inválidos
        except ValueError:
            descripcion = descripciones.get(feature, feature)
            errores.append(f"Entrada inválida para: {descripcion}")

    return datos, errores

# Ruta principal para aplicación Flask
@app.route('/')
def index():
    # Renderiza la plantilla HTML llamada `index.html`, que define el contenido de la página principal.
    # Determina los contenidos, a la par de relacionarlos con sus codificaciones depende el caso.
    return render_template('index.html', features=DESCRIPCION, 
                           OCCUPATION_TYPE_MAPPING=OCCUPATION_TYPE_MAPPING,
                            ORGANIZATION_TYPE_MAPPING=ORGANIZATION_TYPE_MAPPING)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # Renderiza el formulario en caso de acceso con GET
    if request.method == 'GET':
        # Determina que variables seran visualizadas
        return render_template('index.html',features=DESCRIPCION, OCCUPATION_TYPE_MAPPING=OCCUPATION_TYPE_MAPPING, 
                               ORGANIZATION_TYPE_MAPPING=ORGANIZATION_TYPE_MAPPING)
    # Generar predicciones con POST
    elif request.method == 'POST':
        # Validación de datos ingresados, buscando posibles errores
        data, errors = validar_info(request.form, list(DESCRIPCION.values()), {v: k for k, v in DESCRIPCION.items()})
        # En el caso de que existan errores, renderiza el html mostrando los errores
        if errors:
            return render_template('index.html',features=DESCRIPCION,OCCUPATION_TYPE_MAPPING=OCCUPATION_TYPE_MAPPING, 
                                   ORGANIZATION_TYPE_MAPPING=ORGANIZATION_TYPE_MAPPING,
                                    # Une los mensajes en uno solo
                                    error=', '.join(errors))
        try:
            # Convertir datos a DataFrame
            input_data = pd.DataFrame([data])

            # Filtrar solo las características esperadas por el modelo
            model_features = list(DESCRIPCION.values())  # Características usadas durante el entrenamiento
            input_data = input_data[model_features]

            # Realizar la predicción
            prediction = model.predict(input_data)

            # Registrar en registros.csv
            with open(registro, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Agregar fecha y hora de registro, Valores de texto, Valores de características y la prediccion
                writer.writerow([datetime.now(), data.get('OCCUPATION_TYPE_TEXT', 'Desconocido'), 
                                 data.get('ORGANIZATION_TYPE_TEXT', 'Desconocido')] + [data[feature] for feature in model_features] + 
                                 [int(prediction[0])])
            # Renderiza el html mostrando la predicción en el formulario.
            return render_template('index.html',features=DESCRIPCION, OCCUPATION_TYPE_MAPPING=OCCUPATION_TYPE_MAPPING,
                                   ORGANIZATION_TYPE_MAPPING=ORGANIZATION_TYPE_MAPPING,
                                    prediction=int(prediction[0]))
        except Exception as e:
            # En el caso de que se presente un error diferente a
            return render_template('index.html',features=DESCRIPCION, OCCUPATION_TYPE_MAPPING=OCCUPATION_TYPE_MAPPING, 
                                   ORGANIZATION_TYPE_MAPPING=ORGANIZATION_TYPE_MAPPING,
                                    error=f"Error inesperado: {str(e)}")
        
if __name__ == '__main__':
    app.run(debug=True, port=6060)