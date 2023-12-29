import streamlit as st
from streamlit_option_menu import option_menu
import coches_electricos, tendencias

st.set_page_config(page_title='VE Price Prediction App', layout='wide')

def image(url, width=None, height=None):
    return f'<img src="{url}" {"width="+str(width) if width else ""} {"height="+str(height) if height else ""}>'

def link(url, text):
    return f'<a href="{url}">{text}</a>'


footer = """
   <div style="padding: 10px; position: fixed; bottom: 0; width: 100%; text-align: center;">
        Made in {0} with ❤️ by {1} 
    </div>
    """.format(image('https://avatars3.githubusercontent.com/u/45109972?s=400&v=4', width=25, height=25),
            link("https://www.cintiagarciagarces.com/", "@CintiaGarciaGarces"),
        )  


def do_presentation():
        st.markdown("<style>h1 { font-family: 'Arial', sans-serif; }</style>", unsafe_allow_html=True)

        st.markdown('### Bienvenidos al Trabajo Fin de Grado')
        
        st.write('Estás visitando el sitio web dedicado a mi trabajo fin de grado. Aquí encontrarás información detallada sobre mi investigación, los objetivos alcanzados, y los resultados obtenidos a lo largo de este proyecto académico.')
        
        st.write('Este proyecto de fin de grado se basa en el análisis de datos públicos proporcionados por la DGT y el gobierno de España acerca de la actualidad de los vehículos eléctricos en el país. Estos datos han sido cuidadosamente procesados para ofrecer una perspectiva futura del mercado en cuestión')

        st.write('Este trabajo lo estoy realizando para la Universidad a Distancia de Madrid, donde estoy llevando a cabo mi proyecto de fin de grado.')
    
        st.write('Agradezco tu interés y espero que encuentres esta presentación informativa y esclarecedora. Si tienes alguna pregunta o comentario, no dudes en ponerte en contacto conmigo.')

        st.write('Gracias por visitar mi trabajo fin de grado. ¡Espero que disfrutes explorando los detalles de mi investigación!')

        st.markdown('___')

        # logo_path = "streamlit/logo-udima.png"
        # st.image(logo_path, caption='Universidad a Distancia de Madrid', width=200)


def do_coches_electricos():
    coches_electricos.app()   

def do_tendencias():
    tendencias.app()

def display_linkedin_icon():
    linkedin_icon = "https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg"
    linkedin_url = "https://www.linkedin.com/in/cintia-garcia-garces/"

    image_html = f'<a href="{linkedin_url}" target="_blank"><img src="{linkedin_icon}" alt="Imagen" style="width: 24px;"></a>'
    st.markdown(image_html, unsafe_allow_html=True)

def display_github_icon():
    github_icon = "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png"
    github_url = "https://github.com/cintiagarcia"

    image_html = f'<a href="{github_url}" target="_blank"><img src="{github_icon}" alt="Imagen" style="width: 24px;"></a>'
    st.markdown(image_html, unsafe_allow_html=True)

def display_my_website_link():
    web_url = "https://www.cintiagarciagarces.com/"

    st.sidebar.write(f"Visita mi página web [🌐]({web_url})")

styles = {
    "container": {"margin": "0px !important", "padding": "0!important", "align-items": "stretch", "font-family": "Futura, Sans-serif"},
    "icon": {"font-family": "Futura, sans-serif"}, 
    "nav-link": {"text-align": "left", "margin":"0px", "font-family": "Futura, sans-serif"},
    "nav-link-selected": {"background-color": "lightblue", "font-weight": "normal", "color": "black", "font-family": "Futura, sans-serif"},
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

            st.markdown('&nbsp;' * 5)
            st.markdown('___')
            display_my_website_link()

            display_linkedin_icon()
            st.empty()
            display_github_icon()

    elif with_view_panel == 'main':
        menu_selection = option_menu(**kwargs)
    else:
        raise ValueError(f"Unknown view panel value: {with_view_panel}. Must be 'sidebar' or 'main'.")

    if menu['items'][menu_selection]['submenu']:
        show_menu(menu['items'][menu_selection]['submenu'])

    if menu['items'][menu_selection]['action']:
        menu['items'][menu_selection]['action']()

    st.markdown(footer, unsafe_allow_html=True)


show_menu(menu)

