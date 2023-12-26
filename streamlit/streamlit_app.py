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

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title='Main Menu',
                options=['Home', 'Datos Históricos', 'Tendencias'],
                icons=['house', 'clipboard-data', 'bar-chart'],
                menu_icon='cast',
            )

        if app == "Home":
            self.show_home()
        elif app == "Datos Históricos":
            coches_electricos.app()   
        elif app == 'Tendencias':
            tendencias.app()       

    def show_home(self):
        # Puedes personalizar el contenido de la aplicación "Home"
        st.title('Bienvenido al Home')
        st.write('Este es el contenido de la aplicación Home.')

# Crear una instancia de Multiapp
multiapp = Multiapp()

# Añadir las aplicaciones
multiapp.add_app('Datos Históricos', coches_electricos.app)
multiapp.add_app('Tendencias', tendencias.app)

# Ejecutar la aplicación seleccionada
multiapp.run()
