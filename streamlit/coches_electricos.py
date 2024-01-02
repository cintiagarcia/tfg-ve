import pandas as pd
import s3fs
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from st_files_connection import FilesConnection


def app():
    # List all objects in the bucket
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

    def generate_yearly_sales_chart(df):

        # Calcular el sumatorio de la columna "diferencia_mes_anterior" por año
        grouped_data = df.groupby('año')['total_coches'].sum().reset_index()

        barra = px.bar(grouped_data, x='año', y='total_coches')
        linea = px.line(grouped_data, x='año', y='total_coches')

        fig = go.Figure()

        fig.add_trace(go.Bar(x=barra.data[0].x, y=barra.data[0].y, name="Gráfico Barra"))
        fig.add_trace(go.Scatter(x=linea.data[0].x, y=linea.data[0].y, name="Gráfico Línea"))

        fig.update_layout(title='Venta anual de coches eléctricos en España')

        return fig
    
    
    def show_sales_kpi(df):
        total_ventas = df.groupby('año')['total_coches'].sum().reset_index()

        fig = px.pie(total_ventas, values='total_coches', names='año', title='Distribución de ventas de coches eléctricos por año')
        fig.update_traces(textinfo='percent+label', pull=[0.1] * len(total_ventas))

        return fig

    def generate_sales_by_region_chart(df):
        años_unicos = df["año"].unique()

        año_seleccionado = st.selectbox("Selecciona el año", años_unicos, key="sales_by_region_year")

        filtrado = df[df["año"] == año_seleccionado]  

        acumulado_por_comunidad = filtrado.groupby('comunidad_autonoma')['total_coches'].sum().reset_index()

        fig = px.bar(acumulado_por_comunidad, x='comunidad_autonoma', y='total_coches', title='Venta anual de coches por Comunidad Autónoma')
        fig.update_xaxes(title='Comunidad Autónoma')
        fig.update_yaxes(title='Total de Coches')

        return fig
    
    def show_sales_by_region_kpi(df):
        años_unicos = df["año"].unique()

        año_seleccionado = st.selectbox("Selecciona el año", años_unicos, key="sales_by_region_year_kpi")

        filtrado = df[df["año"] == año_seleccionado]  

        acumulado_por_comunidad = filtrado.groupby('comunidad_autonoma')['total_coches'].sum().reset_index()

        fig = px.pie(
            acumulado_por_comunidad,
            values='total_coches',
            names='comunidad_autonoma',
            title='Venta anual de coches por Comunidad Autónoma'
        )
        fig.update_traces(textinfo='percent+label', pull=[0.1] * len(acumulado_por_comunidad))

        return fig

    conn = st.connection('s3', type=FilesConnection)

    df = read_data_from_s3(bucket_name, conn)

    st.markdown('---')

    
    col1, col2 = st.columns((5,5))
    with col1:
        st.header("Ventas Anuales")
        total_sales_kpi = show_sales_kpi(df)
        st.plotly_chart(total_sales_kpi, use_container_width=True)
    with col2:
        st.header("Ventas Anuales")
        yearly_sales_chart = generate_yearly_sales_chart(df)
        st.plotly_chart(yearly_sales_chart, use_container_width=True)

    st.markdown('---')

    col1, col2 = st.columns((5,5))
    with col1:
        st.header("Ventas Anuales")
        yearly_sales_kpi = show_sales_by_region_kpi(df)
        st.plotly_chart(yearly_sales_kpi, use_container_width=True)
    with col2:
        st.header("Ventas por Comunidad Autónoma")
        sales_by_region_chart = generate_sales_by_region_chart(df)
        st.plotly_chart(sales_by_region_chart, use_container_width=True)

    st.markdown('---')

    def generate_yearly_sales_cum_chart(df):
        df['fecha'] = pd.to_datetime(df['año'].astype(str) + '-' + df['mes'].astype(str))

        df = df.sort_values('fecha')

        df['acumulado'] = df['total_coches'].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['fecha'], y=df['acumulado'], mode='lines', name='Acumulado de Ventas', line_shape='spline'))

        fig.update_layout(title='Número de coches eléctricos en circulación en España por Mes',
                        xaxis_title='Fecha',
                        yaxis_title='Número de Coches Eléctricos')

        return fig

    sales_by_region_chart = generate_yearly_sales_cum_chart(df)
    st.plotly_chart(sales_by_region_chart, use_container_width=True)

    st.markdown('---')
