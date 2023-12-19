import pandas as pd
import s3fs
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

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
    año_seleccionado = st.selectbox("Selecciona el año", años_unicos)

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
df = read_data_from_s3(bucket_name)

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

