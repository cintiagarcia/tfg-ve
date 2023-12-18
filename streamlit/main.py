import streamlit as st
from streamlit_option_menu import option_menu
import coches_electricos, tendencias

st.set_page_config(
    page_title='TFG',
    layout='wide', 
    initial_sidebar_state='expanded',
)

class Multiapp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            'title': title,
            'function': func
        })    

    def run():
        with st.sidebar:
            app = option_menu(
                menu_title='Main Menu',
                options=['Home', 'Datos Históricos', 'Tendencias'],
                icons=['house', 'clipboard-data', 'bar-chart'],
                menu_icon='cast',
            )

        if app == "Datos Históricos":
            coches_electricos.app()   
        if app == 'Tendencias':
            tendencias.app()        

    run()
