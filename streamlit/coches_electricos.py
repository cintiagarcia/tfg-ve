import pandas as pd
import s3fs
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from st_files_connection import FilesConnection


def app():
    # List all objects in the bucket
    bucket_name = "clean-data-ve-eu-central-1"

    def read_data_from_s3(bucket_name):
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

    conn = st.connection('s3', type=FilesConnection)

    def generate_yearly_sales_chart(df):

        # Calcular el sumatorio de la columna "diferencia_mes_anterior" por año
        grouped_data = df.groupby('año')['total_coches'].sum().reset_index()

        # Crear un gráfico de barras con Plotly
        barra = px.bar(grouped_data, x='año', y='total_coches')

        # Crear un gráfico de línea con Plotly
        linea = px.line(grouped_data, x='año', y='total_coches')

        fig = go.Figure()

        # Agregar la subtrama del gráfico de barras
        fig.add_trace(go.Bar(x=barra.data[0].x, y=barra.data[0].y, name="Gráfico Barra"))

        # Agregar la subtrama del gráfico de línea
        fig.add_trace(go.Scatter(x=linea.data[0].x, y=linea.data[0].y, name="Gráfico Línea"))

        fig.update_layout(title='Venta anual de coches eléctricos en España')

        return fig


    def generate_sales_by_region_chart(df):
        #Obtener los años únicos en los datos
        años_unicos = df["año"].unique()

        # Interfaz para seleccionar el año
        año_seleccionado = st.selectbox("Selecciona el año", años_unicos, key="sales_by_region_year")

        # Filtrar los datos para el año seleccionado
        filtrado = df[df["año"] == año_seleccionado]  

        # Calcular el acumulado de la columna "total_coches" por comunidad autónoma
        acumulado_por_comunidad = filtrado.groupby('comunidad_autonoma')['total_coches'].sum().reset_index()

        # Crear el gráfico de barras del acumulado por comunidad autónoma
        fig = px.bar(acumulado_por_comunidad, x='comunidad_autonoma', y='total_coches', title='Venta anual de Coches por Comunidad Autónoma')
        fig.update_xaxes(title='Comunidad Autónoma')
        fig.update_yaxes(title='Total de Coches')

        return fig


    # Leer los datos desde S3
    df = read_data_from_s3(bucket_name, conn)

    st.markdown('---')

    # Crear las columnas
    col1, col2 = st.columns((5,5))

    # Mostrar el gráfico de ventas anuales en la columna 1
    with col1:
        st.header("Ventas Anuales")
        yearly_sales_chart = generate_yearly_sales_chart(df)
        st.plotly_chart(yearly_sales_chart, use_container_width=True)

    # Mostrar el gráfico de ventas por región en la columna 2
    with col2:
        st.header("Ventas por Comunidad Autónoma")
        sales_by_region_chart = generate_sales_by_region_chart(df)
        st.plotly_chart(sales_by_region_chart, use_container_width=True)

    st.markdown('---')


    def generate_yearly_sales_cum_chart(df):
        # Crear una columna de fecha combinando las columnas "año" y "mes"
        df['fecha'] = pd.to_datetime(df['año'].astype(str) + '-' + df['mes'].astype(str))

        # Ordenar los datos por fecha
        df = df.sort_values('fecha')

        # Calcular el acumulado de ventas por mes
        df['acumulado'] = df['total_coches'].cumsum()

        # Crear un gráfico de líneas
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['fecha'], y=df['acumulado'], mode='lines', name='Acumulado de Ventas', line_shape='spline'))

        fig.update_layout(title='Número de coches eléctricos en circulación en España por Mes',
                        xaxis_title='Fecha',
                        yaxis_title='Número de Coches Eléctricos')

        return fig

    sales_by_region_chart = generate_yearly_sales_cum_chart(df)
    st.plotly_chart(sales_by_region_chart, use_container_width=True)

    def generate_sales_by_region_cum_chart(df):
        # Ordenar el DataFrame por año y comunidad autónoma
        df_sorted = df.sort_values(['año', 'comunidad_autonoma'])

        # Calcular el total acumulado por año y comunidad autónoma
        df_sorted['acumulado'] = df_sorted.groupby(['comunidad_autonoma'])['total_coches'].cumsum()

        # Obtener los años únicos en los datos
        años_unicos = df_sorted['año'].unique()

        # Interfaz para seleccionar el año
        año_seleccionado = st.selectbox("Selecciona el año", años_unicos)

        # Filtrar los datos para el año seleccionado y años anteriores
        filtrado = df_sorted[df_sorted['año'] <= año_seleccionado].copy()

        # Crear columnas para el valor acumulado en el año seleccionado y el valor acumulado hasta el año anterior
        filtrado['acumulado_seleccionado'] = filtrado.groupby('comunidad_autonoma')['acumulado'].transform('last')
        filtrado['acumulado_anterior'] = filtrado.groupby('comunidad_autonoma')['acumulado'].shift().fillna(0)

        # Filtrar los datos para el año seleccionado
        filtrado_seleccionado = filtrado[filtrado['año'] == año_seleccionado]

        # Crear el gráfico de barras del acumulado por comunidad autónoma
        fig = go.Figure()
        fig.add_trace(go.Bar(x=filtrado_seleccionado['comunidad_autonoma'], y=filtrado_seleccionado['acumulado_seleccionado'],
                            name='Acumulado Seleccionado'))

        fig.update_layout(title='Venta anual de Coches por Comunidad Autónoma',
                        xaxis_title='Comunidad Autónoma',
                        yaxis_title='Total de Coches')

        return fig


    # # Ejemplo de uso
    # dataframe = pd.DataFrame({
    #     'comunidad_autonoma': ['A', 'A', 'B', 'B', 'C', 'C'],
    #     'total_coches': [10, 20, 30, 40, 50, 60],
    #     'año': [2020, 2021, 2020, 2021, 2020, 2021]
    # })

    sales_by_region_chart = generate_sales_by_region_cum_chart(df)
    st.plotly_chart(sales_by_region_chart, use_container_width=True)
