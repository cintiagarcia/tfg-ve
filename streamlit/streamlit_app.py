import streamlit as st
from streamlit_option_menu import option_menu
import coches_electricos, tendencias


st.set_page_config(page_title='Muti-page app example', layout='wide')

def do_presentation():
        st.markdown("<style>h1 { font-family: 'Arial', sans-serif; }</style>", unsafe_allow_html=True)

        st.markdown('### Bienvenidos al Trabajo Fin de Grado')
        
        st.write('Estás visitando el sitio web dedicado a mi trabajo fin de grado. Aquí encontrarás información detallada sobre mi investigación, los objetivos alcanzados, y los resultados obtenidos a lo largo de este proyecto académico.')
        
        st.write('Mi trabajo se concentra en desarrollar un sitio web que exhiba las proyecciones de ventas de vehículos eléctricos en España. A lo largo de estas páginas, podrás explorar los diferentes aspectos del proyecto, desde la definición del problema hasta la implementación de soluciones y conclusiones alcanzadas.')

        st.write('Este trabajo se realiza en colaboración con la Universidad a Distancia de Madrid, donde estoy llevando a cabo mi investigación de fin de grado.')
    
        st.write('Agradezco tu interés y espero que encuentres esta presentación informativa y esclarecedora. Si tienes alguna pregunta o comentario, no dudes en ponerte en contacto conmigo.')

        st.write('Gracias por visitar mi trabajo fin de grado. ¡Espero que disfrutes explorando los detalles de mi investigación!')

        # logo_path = "streamlit/logo-udima.png"
        # st.image(logo_path, caption='Logo de la Universidad a Distancia de Madrid', width=200)

def do_coches_electricos():
    coches_electricos.app()   

def do_tendencias():
    tendencias.app()


styles = {
    "container": {"margin": "0px !important", "padding": "0!important", "align-items": "stretch", "font-family": "Futura, Sans-serif"},
    "icon": {"font-size": "20px", "font-family": "Futura, sans-serif"}, 
    "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "font-family": "Futura, sans-serif"},
    "nav-link-selected": {"background-color": "lightblue", "font-size": "20px", "font-weight": "normal", "color": "black", "font-family": "Futura, sans-serif"},
}

menu = {
    'title': 'VE Predicción',
    'items': { 
        'Home' : {
            'action': None, 'item_icon': 'house', 'submenu': {
                'title': None,
                'items': { 
                    'TFG' : {'action': do_presentation, 'item_icon': 'mortarboard', 'submenu': None},
                    'Datos Históricos' : {'action': do_coches_electricos, 'item_icon': 'clipboard-data', 'submenu': None},
                    'Tendencias' : {'action': do_tendencias, 'item_icon': 'bar-chart', 'submenu': None},
                },
                'menu_icon': None,
                'default_index': 0,
                'with_view_panel': 'main',
                'orientation': 'horizontal',
                'styles': styles
            }
        },
        'Datos Históricos' : {
            'action': None, 'item_icon': 'clipboard-data', 'submenu': {
                'title': None,
                'items': { 
                    'Ventas Coches Eléctricos' : {'action': do_coches_electricos, 'item_icon': 'car-front', 'submenu': None},
                },
                'menu_icon': None,
                'default_index': 0,
                'with_view_panel': 'main',
                'orientation': 'horizontal',
                'styles': styles
            }
        },
        'Tendencias' : {
            'action': None, 'item_icon': 'bar-chart', 'submenu': {
                'title': None,
                'items': { 
                    'Predicciones Ventas Coches Eléctricos' : {'action': do_tendencias, 'item_icon': 'graph-up', 'submenu': None},
                },
                'menu_icon': None,
                'default_index': 0,
                'with_view_panel': 'main',
                'orientation': 'horizontal',
                'styles': styles
            }
        }
    },

    'menu_icon': 'plugin',
    'default_index': 0,
    'with_view_panel': 'sidebar',
    'orientation': 'vertical',
    'styles': styles
}

def show_menu(menu):
    def _get_options(menu):
        options = list(menu['items'].keys())
        return options

    def _get_icons(menu):
        icons = [v['item_icon'] for _k, v in menu['items'].items()]
        return icons

    kwargs = {
        'menu_title': menu['title'] ,
        'options': _get_options(menu),
        'icons': _get_icons(menu),
        'menu_icon': menu['menu_icon'],
        'default_index': menu['default_index'],
        'orientation': menu['orientation'],
        'styles': menu['styles']
    }

    with_view_panel = menu['with_view_panel']
    if with_view_panel == 'sidebar':
        with st.sidebar:
            menu_selection = option_menu(**kwargs)
            st.markdown('___')

    elif with_view_panel == 'main':
        menu_selection = option_menu(**kwargs)
    else:
        raise ValueError(f"Unknown view panel value: {with_view_panel}. Must be 'sidebar' or 'main'.")

    if menu['items'][menu_selection]['submenu']:
        show_menu(menu['items'][menu_selection]['submenu'])

    if menu['items'][menu_selection]['action']:
        menu['items'][menu_selection]['action']()

show_menu(menu)

