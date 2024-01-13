import functools
import pandas as pd
import s3fs
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from st_files_connection import FilesConnection
import numpy as np


def app():
    # List all objects in the bucket
    bucket_name = "clean-data-ve-eu-central-1"

    @functools.lru_cache(maxsize=None)
    def read_data_from_s3(bucket_name, conn):
        # Crear un objeto de sistema de archivos S3
        fs = s3fs.S3FileSystem()
        file_paths = fs.glob(f"{bucket_name}/*")
        

        # Leer los objetos y procesar los datos
        data_frames = []
        for file_path in file_paths:
            with fs.open(file_path, "rb") as file:
                # Read the object content, a csv file
                df = pd.read_csv(file)
                data_frames.append(df)

        # Concatenar todos los marcos de datos
        df = pd.concat(data_frames)

        return df

    @st.cache_data
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
    
    @st.cache_data
    def show_sales_kpi(df):
        total_sales = df.groupby('año')['total_coches'].sum().reset_index()

        fig = px.pie(total_sales, values='total_coches', names='año', title='Distribución de ventas de coches eléctricos por año en España')
        fig.update_traces(textinfo='percent+label', pull=[0.1] * len(total_sales))

        return fig

    @st.cache_data(experimental_allow_widgets=True)
    def generate_sales_by_region_chart(df):
        unique_years = df["año"].unique()

        selected_year = st.selectbox("Selecciona el año", unique_years, key="sales_by_region_year")

        filter = df[df["año"] == selected_year]  

        accumulated_per_region = filter.groupby('comunidad_autonoma')['total_coches'].sum().reset_index()

        fig = px.bar(accumulated_per_region, x='comunidad_autonoma', y='total_coches', title='Venta anual de coches por Comunidad Autónoma')
        fig.update_xaxes(title='Comunidad Autónoma')
        fig.update_yaxes(title='Total de Coches')

        return fig
    
    @st.cache_data(experimental_allow_widgets=True)
    def show_sales_by_region_kpi(df):
        unique_years = df["año"].unique()

        selected_year = st.selectbox("Selecciona el año", unique_years, key="sales_by_region_year_kpi")

        filtrado = df[df["año"] == selected_year]  

        accumulated_per_region = filtrado.groupby('comunidad_autonoma')['total_coches'].sum().reset_index()

        fig = px.pie(
            accumulated_per_region,
            values='total_coches',
            names='comunidad_autonoma',
            title='Distribución de ventas de coches eléctricos por Comunidad Autónoma'
        )
        fig.update_traces(textinfo='percent+label', pull=[0.1] * len(accumulated_per_region))

        return fig
    
    @st.cache_data
    def show_kpis(df):
        total_sales = int(df['total_coches'].sum())
        total_sales_by_year = df.groupby('año')['total_coches'].sum()

        annual_variation = total_sales_by_year.pct_change() * 100
        annual_variation = annual_variation.replace([np.inf, -np.inf, np.nan], 0)

        with st.container():
            col1, col2 = st.columns((2, 6))
            with col1:
                st.markdown('''
                <div style="border: 2px solid #45a7c8; padding: 10px">
                    <h3 style="text-align: center">Total de ventas</h3>
                    <p style="text-align: center; font-size: 24px"><strong>{}</strong> <i class="bi bi-ev-front"></i></p>
                    <br>
                </div>
                '''.format('{:,}'.format(total_sales)), unsafe_allow_html=True)

            with col2:
                st.markdown('''
                <div style="border: 2px solid #45a7c8; padding: 10px">
                    <h3 style="text-align: center">Porcentaje de Variación Anual</h3>
                    <div style="overflow-x: auto;">
                        <table style="margin-left: auto; margin-right: auto;">
                            <thead>
                                <tr>
                                    <th></th>
                                    {}
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td style="text-align: center">Porcentaje de Variación</td>
                                    {}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                '''.format(
                    ''.join('<th>{}</th>'.format(año) for año in total_sales_by_year.index),
                    ''.join('<td style="text-align: center">{:.2f}%</td>'.format(variación) for variación in annual_variation),
                ), unsafe_allow_html=True)

    @st.cache_data(experimental_allow_widgets=True)
    def generate_yearly_sales_cum_chart(df):
        df['fecha'] = pd.to_datetime(df['año'].astype(str) + '-' + df['mes'].astype(str))

        df = df.sort_values('fecha')

        df['acumulado'] = df['total_coches'].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['fecha'], y=df['acumulado'], mode='lines', name='Acumulado de Ventas', line_shape='spline'))

        st.header("Número Total de Coches Eléctricos")

        fig.update_layout(title='Número de coches eléctricos en circulación en España por Mes',
                        xaxis_title='Fecha',
                        yaxis_title='Número de Coches Eléctricos')

        return fig
    
    conn = st.connection('s3', type=FilesConnection)

    df = read_data_from_s3(bucket_name, conn)

    st.markdown('---')

    st.write("")

    show_kpis(df)

    st.write("")

    st.markdown('---')

    st.markdown('<h1 style="text-align: center;">Ventas Anuales</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns((5,5))
    with col1:
        total_sales_kpi = show_sales_kpi(df)
        st.plotly_chart(total_sales_kpi, use_container_width=True)
    with col2:
        yearly_sales_chart = generate_yearly_sales_chart(df)
        st.plotly_chart(yearly_sales_chart, use_container_width=True)

    st.markdown('---')

    st.markdown('<h1 style="text-align: center;">Ventas Anuales por Comunidad Autónoma</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns((5,5))
    with col1:
        yearly_sales_kpi = show_sales_by_region_kpi(df)
        st.plotly_chart(yearly_sales_kpi, use_container_width=True)
    with col2:
        sales_by_region_chart = generate_sales_by_region_chart(df)
        st.plotly_chart(sales_by_region_chart, use_container_width=True)
    
    st.write("")

    st.markdown('---')

    sales_by_region_chart = generate_yearly_sales_cum_chart(df)
    st.plotly_chart(sales_by_region_chart, use_container_width=True)

    st.markdown('---')
