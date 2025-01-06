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
OCCUPATION_TYPE_MAPPING = {'Accountants': 0.046308043643745245, 'Cleaning staff': 0.0954290296712109, 
                           'Cooking staff': 0.10509754562617998, 'Core staff': 0.06382111981170506, 
                           'Drivers': 0.11262044967880086, 'HR staff': 0.06997742663656885, 
                           'High skill tech staff': 0.06279555702188497, 'IT staff': 0.06132075471698113, 
                           'Laborers': 0.10522153686255903, 'Low-skill Laborers': 0.18101415094339623, 
                           'Managers': 0.062236780533458116, 'Medicine staff': 0.06985882695386407, 
                           'Private service staff': 0.0659025787965616, 'Realty agents': 0.08080808080808081, 
                           'SIN VALOR': 0.06492071744216273, 'Sales staff': 0.09599312661095055, 
                           'Secretaries': 0.07163323782234957, 'Security staff': 0.10685033507073716, 
                           'Waiters/barmen staff': 0.1147227533460803}

ORGANIZATION_TYPE_MAPPING = {'Advertising': 0.08761329305135952, 'Agriculture': 0.10784810126582278, 
                             'Bank': 0.055, 'Business Entity Type 1': 0.08049792531120332, 
                             'Business Entity Type 2': 0.08634800142331871, 
                             'Business Entity Type 3': 0.09273275038577412, 
                             'Cleaning': 0.11320754716981132, 'Construction': 0.11946656788294129, 
                             'Culture': 0.060810810810810814, 'Electricity': 0.07397622192866579, 
                             'Emergency': 0.06986899563318777, 'Government': 0.06869679894497063, 
                             'Hotel': 0.06385696040868455, 'Housing': 0.0788696752425137, 
                             'Industry: type 1': 0.11229314420803782, 
                             'Industry: type 2': 0.08266666666666667, 
                             'Industry: type 3': 0.1079245283018868, 
                             'Industry: type 4': 0.0935754189944134, 
                             'Industry: type 5': 0.06652360515021459,
                             'Industry: type 6': 0.05747126436781609, 
                             'Industry: type 7': 0.07751196172248803, 
                             'Industry: type 8': 0.15789473684210525, 
                             'Industry: type 9': 0.06654411764705882,
                             'Industry: type 10': 0.07058823529411765, 
                             'Industry: type 11': 0.0834485938220378, 
                             'Industry: type 12': 0.040955631399317405, 
                             'Industry: type 13': 0.13725490196078433, 
                             'Insurance': 0.05672268907563025, 'Kindergarten': 0.07132564841498559, 
                             'Legal Services': 0.084, 'Medicine': 0.0674457429048414, 
                             'Military': 0.04921911973497397, 'Mobile': 0.084, 
                             'Other': 0.07492297287142105, 'Police': 0.049435787211176786, 
                             'Postal': 0.0805523590333717, 'Realtor': 0.11419753086419752, 
                             'Religion': 0.057971014492753624, 'Restaurant': 0.11650485436893204, 
                             'SIN VALOR': 0.0536891466370659, 'School': 0.05836467474578632, 
                             'Security': 0.10510164940544688, 'Security Ministries': 0.05068836045056321, 
                             'Self-employed': 0.10211958654978412, 'Services': 0.06374501992031872, 
                             'Telecom': 0.08185840707964602, 'Trade: type 1': 0.09854014598540146, 
                             'Trade: type 2': 0.06828627708470125, 'Trade: type 3': 0.10214285714285715, 
                             'Trade: type 4': 0.038461538461538464, 'Trade: type 5': 0.025, 
                             'Trade: type 6': 0.04065040650406504, 'Trade: type 7': 0.09434865900383142, 
                             'Transport: type 1': 0.05, 'Transport: type 2': 0.07857546636517806, 
                             'Transport: type 3': 0.15767634854771784, 'Transport: type 4': 0.09093017861285084, 
                             'University': 0.05218216318785579}

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