from functools import total_ordering
from pyexpat import model
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import s3fs
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from st_files_connection import FilesConnection
from prophet import Prophet


def app():
    # Cargar los datos desde el S3 bucket
    bucket_name = "clean-data-ve-eu-central-1"

    def read_data_from_s3(bucket_name, conn):
        # Create an S3 file system object
        fs = s3fs.S3FileSystem()

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

    # Conexión con S3 bucket
    conn = st.connection('s3', type=FilesConnection)
    # Cargar los datos
    df = read_data_from_s3(bucket_name, conn)
    
    def predecir_ventas_con_prophet(df, selected_years):
        df_grouped = df.groupby(['año', 'mes'], as_index=False)['total_coches'].sum().reset_index()
        df_grouped['ds'] = pd.to_datetime(df_grouped['año'].astype(str) + '-' + df_grouped['mes'].astype(str) + '-01')
        df_grouped.rename(columns={'total_coches': 'y'}, inplace=True)

        df_prophet = df_grouped[['ds', 'y']]

        model = Prophet()
        
        model.fit(df_prophet)

        future_dates = pd.date_range(start=df_prophet['ds'].max(), periods=selected_years * 12, freq='M')
        future_df = pd.DataFrame({'ds': future_dates})

        forecast = model.predict(future_df)

        fig = go.Figure()

        # Datos históricos
        fig.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], mode='lines', name='Ventas Históricas'))

        # Predicciones
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicciones'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Límite inferior', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Límite superior', line=dict(color='red')))

        # Configuración del diseño del gráfico
        fig.update_layout(
            title='Predicción de ventas',
            xaxis=dict(title='Fecha'),
            yaxis=dict(title='Ventas')
        )

        return fig, forecast

    st.markdown('---')
    st.title('Predicción ventas de coches eléctricos')
    selected_years = st.slider('Selecciona los años futuros', 1, 11, 5)
    fig, df_forecast = predecir_ventas_con_prophet(df, selected_years)

    st.plotly_chart(fig, use_container_width=True)

    df_forecast = df_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    df_forecast.rename(columns={'ds': 'Fecha', 'yhat': 'Predicciones', 'yhat_lower': 'Límite inferior', 'yhat_upper': 'Límite superior'}, inplace=True)
    st.subheader('Predicciones de Ventas')
    st.dataframe(df_forecast)
    st.markdown('---')

    def predecir_ventas_con_prophet_por_comunidad(df, selected_years, selected_comunidad):
        df_filtered = df[df['comunidad_autonoma'] == selected_comunidad]

        df_grouped = df_filtered.groupby(['año', 'mes'], as_index=False)['total_coches'].sum().reset_index()
        df_grouped['ds'] = pd.to_datetime(df_grouped['año'].astype(str) + '-' + df_grouped['mes'].astype(str) + '-01')
        df_grouped.rename(columns={'total_coches': 'y'}, inplace=True)

        df_prophet = df_grouped[['ds', 'y']]

        model = Prophet()
        
        model.fit(df_prophet)

        future_dates = pd.date_range(start=df_prophet['ds'].max(), periods=selected_years * 12, freq='M')
        future_df = pd.DataFrame({'ds': future_dates})

        forecast = model.predict(future_df)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], mode='lines', name='Ventas Históricas'))

        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicciones'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Límite inferior', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Límite superior', line=dict(color='red')))

        fig.update_layout(
            title=f'Predicción de ventas para {selected_comunidad}',
            xaxis=dict(title='Fecha'),
            yaxis=dict(title='Ventas')
        )

        return fig, forecast

    st.title('Predicción ventas de coches eléctricos por Comunidad Autónoma')

    comunidades_autonomas = df['comunidad_autonoma'].unique()
    selected_comunidad = st.selectbox('Selecciona una Comunidad Autónoma', comunidades_autonomas)

    selected_years = st.slider(f'Selecciona los años futuros para {selected_comunidad}', 1, 11, 5)

    fig, df_forecast = predecir_ventas_con_prophet_por_comunidad(df, selected_years, selected_comunidad)
    st.plotly_chart(fig, use_container_width=True)

    df_forecast = df_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    df_forecast.rename(columns={'ds': 'Fecha', 'yhat': 'Predicciones', 'yhat_lower': 'Límite inferior', 'yhat_upper': 'Límite superior'}, inplace=True)
    st.subheader('Predicciones de Ventas')
    st.dataframe(df_forecast)

    def predecir_ventas_coches_electricos(df, selected_years):
        df_anual = df.groupby('año')['total_coches'].sum().reset_index()

        # Dividir los datos en variables de entrada (X) y variable objetivo (y)
        X = df_anual['año'].values.reshape(-1, 1)
        y = df_anual['total_coches'].values.reshape(-1, 1)

        regression_model = LinearRegression()

        regression_model.fit(X, y)

        future_dates = np.arange(selected_years[0], selected_years[1] + 1).reshape(-1, 1)

        future_predictions = regression_model.predict(future_dates)

        df_pred = pd.DataFrame({'año': future_dates.flatten(), 'Predicciones': future_predictions.flatten()})

        # Combinar datos históricos y predicciones
        df_combined = pd.concat([df_anual, df_pred])

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df_anual['año'], y=df_anual['total_coches'], mode='lines', name='Ventas Históricas'))

        fig.add_trace(go.Scatter(x=df_pred['año'], y=df_pred['Predicciones'], mode='lines', name='Predicciones'))

        fig.update_layout(
            title='Predicción de ventas de coches eléctricos',
            xaxis=dict(title='Año'),
            yaxis=dict(title='Ventas de Coches Eléctricos')
        )
        return fig
    
    

    def predecir_ventas_coches_por_comunidad(df, selected_years_comunidad):
        df_anual = df.groupby(['comunidad_autonoma', 'año'])['total_coches'].sum().reset_index()

        comunidades_autonomas = df_anual['comunidad_autonoma'].unique()

        selected_comunidades = st.multiselect('Selecciona las Comunidades Autónomas', comunidades_autonomas)

        if len(selected_comunidades) == 0:
            # Devolver un gráfico vacío cuando no hay selecciones
            return go.Figure()

        df_filtered = df_anual[df_anual['comunidad_autonoma'].isin(selected_comunidades)]

        prediction_dfs = []

        # Iterar sobre cada comunidad autónoma seleccionada
        for comunidad_autonoma in selected_comunidades:
            df_comunidad = df_filtered[df_filtered['comunidad_autonoma'] == comunidad_autonoma]

            X = df_comunidad['año'].values.reshape(-1, 1)
            y = df_comunidad['total_coches'].values.reshape(-1, 1)

            regression_model = LinearRegression()

            regression_model.fit(X, y)
            
            future_dates = np.arange(selected_years_comunidad[0], selected_years_comunidad[1] + 1).reshape(-1, 1)

            future_predictions = regression_model.predict(future_dates)

            df_pred = pd.DataFrame({'año': future_dates.flatten(), 'Predicciones': future_predictions.flatten()})

            df_pred['Predicciones'] = df_pred['Predicciones'].astype(int)

            df_pred['comunidad_autonoma'] = comunidad_autonoma

            prediction_dfs.append(df_pred)

            # Concatenar todos los DataFrames de predicciones por comunidad autónoma
            df_pred_combined = pd.concat(prediction_dfs)

            df_filtered['total_coches'] = df_filtered['total_coches'].astype(int)

            # Combinar datos históricos y predicciones por comunidad autónoma
            df_combined = pd.concat([df_filtered, df_pred_combined])

            fig = px.line(df_combined, x='año', y='total_coches', color='comunidad_autonoma', title='Predicción de ventas de coches eléctricos por Comunidad Autónoma')

            for comunidad_autonoma in selected_comunidades:
                df_pred_comunidad = df_pred_combined[df_pred_combined['comunidad_autonoma'] == comunidad_autonoma]
                fig.add_trace(go.Scatter(x=df_pred_comunidad['año'], y=df_pred_comunidad['Predicciones'], mode='lines', name=f'Predicciones - {comunidad_autonoma}'))

            fig.update_layout(
                xaxis=dict(title='Año'),
                yaxis=dict(title='Ventas de Coches Eléctricos')
            )
        return fig

    st.markdown('---')

    col1, col2 = st.columns((5,5))

    with col1:
        st.header("Predicción de ventas anuales de coches eléctricos en España")
        selected_years = st.slider('Selecciona los años', df['año'].min(), df['año'].max() + 11, (df['año'].min(), df['año'].max()),key='coches_electricos')
        predecir_ventas_coches = predecir_ventas_coches_electricos(df,selected_years)
        st.plotly_chart(predecir_ventas_coches, use_container_width=True)
    with col2:
        st.header("Predicción de ventas anuales de coches eléctricos por Comunidad Autónoma")
        selected_years_comunidad = st.slider('Selecciona los años', df['año'].min(), df['año'].max() + 11, (df['año'].min(), df['año'].max()),key='coches_electricos_comunidad')
        predecir_ventas_coches_comunidad = predecir_ventas_coches_por_comunidad(df, selected_years_comunidad)
        st.plotly_chart(predecir_ventas_coches_comunidad, use_container_width=True)


    st.markdown('---')

    
    