import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import s3fs
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def app():
    # Cargar los datos desde el S3 bucket
    bucket_name = "clean-data-ve-eu-central-1"

    def read_data_from_s3(bucket_name):
        aws_credentials = st.secrets["aws_credentials"]
        # Create an S3 file system object
        fs = s3fs.S3FileSystem(
            key=aws_credentials["aws_access_key_id"],
            secret=aws_credentials["aws_secret_access_key"]
        )

        file_paths = fs.glob(f"{bucket_name}/*")
        
        # Read the objects and process the data
        data_frames = []
        for file_path in file_paths:
            with fs.open(file_path, "rb") as file:
                # Read the object content, a csv file
                df = pd.read_csv(file)
                data_frames.append(df)

        # Concatenate all data frames
        df = pd.concat(data_frames)

        return df

    # Cargar los datos
    df = read_data_from_s3(bucket_name)

    def predecir_ventas_coches_electricos(df,selected_years):
        # Calcular las ventas anuales sumando el total de coches eléctricos por cada año
        df_anual = df.groupby('año')['total_coches'].sum().reset_index()

        # Dividir los datos en variables de entrada (X) y variable objetivo (y)
        X = df_anual['año'].values.reshape(-1, 1)
        y = df_anual['total_coches'].values.reshape(-1, 1)

        # Crear una instancia del modelo de regresión lineal
        regression_model = LinearRegression()

        # Entrenar el modelo con los datos
        regression_model.fit(X, y)

        # # Generar las fechas futuras
        future_dates = np.arange(selected_years[0], selected_years[1] + 1).reshape(-1, 1)

        # Realizar las predicciones
        future_predictions = regression_model.predict(future_dates)

        # Crear un DataFrame para las predicciones
        df_pred = pd.DataFrame({'año': future_dates.flatten(), 'Predicciones': future_predictions.flatten()})

        # Combinar datos históricos y predicciones
        df_combined = pd.concat([df_anual, df_pred])

        # Crear el gráfico interactivo
        fig = go.Figure()

        # Agregar línea para ventas históricas
        fig.add_trace(go.Scatter(x=df_anual['año'], y=df_anual['total_coches'], mode='lines', name='Ventas Históricas'))

        # Agregar línea para predicciones
        fig.add_trace(go.Scatter(x=df_pred['año'], y=df_pred['Predicciones'], mode='lines', name='Predicciones'))

        # Configurar el diseño del gráfico
        fig.update_layout(
            title='Predicción de ventas de coches eléctricos',
            xaxis=dict(title='Año'),
            yaxis=dict(title='Ventas de Coches Eléctricos')
        )
        return fig


    def predecir_ventas_coches_por_comunidad(df,selected_years_comunidad):
        # Calcular las ventas anuales sumando el total de coches eléctricos por cada comunidad autónoma y año
        df_anual = df.groupby(['comunidad_autonoma', 'año'])['total_coches'].sum().reset_index()

        # Obtener la lista de comunidades autónomas
        comunidades_autonomas = df_anual['comunidad_autonoma'].unique()

        # Crear un widget de selección múltiple para las comunidades autónomas
        selected_comunidades = st.multiselect('Selecciona las Comunidades Autónomas', comunidades_autonomas)

        if len(selected_comunidades) == 0:
            # Devolver un gráfico vacío cuando no hay selecciones
            return go.Figure()

        # Filtrar los datos según las comunidades autónomas seleccionadas
        df_filtered = df_anual[df_anual['comunidad_autonoma'].isin(selected_comunidades)]

            # Crear una lista vacía para almacenar los DataFrames de predicciones por comunidad autónoma
        prediction_dfs = []

            # Iterar sobre cada comunidad autónoma seleccionada
        for comunidad_autonoma in selected_comunidades:
                # Filtrar los datos solo para la comunidad autónoma actual
            df_comunidad = df_filtered[df_filtered['comunidad_autonoma'] == comunidad_autonoma]

                # Dividir los datos en variables de entrada (X) y variable objetivo (y)
            X = df_comunidad['año'].values.reshape(-1, 1)
            y = df_comunidad['total_coches'].values.reshape(-1, 1)

            # Crear una instancia del modelo de regresión lineal
            regression_model = LinearRegression()

            # Entrenar el modelo con los datos
            regression_model.fit(X, y)

            # Generar las fechas futuras
            
            future_dates = np.arange(selected_years_comunidad[0], selected_years_comunidad[1] + 1).reshape(-1, 1)

                # Realizar las predicciones
            future_predictions = regression_model.predict(future_dates)

                # Crear un DataFrame para las predicciones
            df_pred = pd.DataFrame({'año': future_dates.flatten(), 'Predicciones': future_predictions.flatten()})

                # Convertir los valores de las predicciones a enteros
            df_pred['Predicciones'] = df_pred['Predicciones'].astype(int)

                # Agregar una columna para la comunidad autónoma
            df_pred['comunidad_autonoma'] = comunidad_autonoma

                # Agregar el DataFrame de predicciones a la lista
            prediction_dfs.append(df_pred)

            # Concatenar todos los DataFrames de predicciones por comunidad autónoma
            df_pred_combined = pd.concat(prediction_dfs)

            # Convertir los valores de las ventas anuales a enteros
            df_filtered['total_coches'] = df_filtered['total_coches'].astype(int)

            # Combinar datos históricos y predicciones por comunidad autónoma
            df_combined = pd.concat([df_filtered, df_pred_combined])

            # Crear el gráfico interactivo por comunidad autónoma
            fig = px.line(df_combined, x='año', y='total_coches', color='comunidad_autonoma', title='Predicción de ventas de coches eléctricos por Comunidad Autónoma')

            # Agregar las predicciones al gráfico
            for comunidad_autonoma in selected_comunidades:
                df_pred_comunidad = df_pred_combined[df_pred_combined['comunidad_autonoma'] == comunidad_autonoma]
                fig.add_trace(go.Scatter(x=df_pred_comunidad['año'], y=df_pred_comunidad['Predicciones'], mode='lines', name=f'Predicciones - {comunidad_autonoma}'))

            # Configurar el diseño del gráfico
            fig.update_layout(
                xaxis=dict(title='Año'),
                yaxis=dict(title='Ventas de Coches Eléctricos')
            )
        return fig


    st.markdown('---')

    # Crear las columnas
    col1, col2 = st.columns((5,5))

    # Mostrar el gráfico de ventas anuales en la columna 1
    with col1:
        st.header("Predicción de ventas anuales de coches eléctricos en España")
        selected_years = st.slider('Selecciona los años', df['año'].min(), df['año'].max() + 11, (df['año'].min(), df['año'].max()),key='coches_electricos')
        predecir_ventas_coches = predecir_ventas_coches_electricos(df,selected_years)
        st.plotly_chart(predecir_ventas_coches, use_container_width=True)

    # Mostrar el gráfico de ventas por región en la columna 2
    with col2:
        st.header("Predicción de ventas de coches eléctricos por Comunidad Autónoma")
        selected_years_comunidad = st.slider('Selecciona los años', df['año'].min(), df['año'].max() + 11, (df['año'].min(), df['año'].max()),key='coches_electricos_comunidad')
        predecir_ventas_coches_comunidad = predecir_ventas_coches_por_comunidad(df, selected_years_comunidad)
        st.plotly_chart(predecir_ventas_coches_comunidad, use_container_width=True)


    st.markdown('---')


