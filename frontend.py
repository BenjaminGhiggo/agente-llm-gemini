# frontend.py

import backend  # Importar el módulo backend que contiene la lógica de procesamiento de consultas
import streamlit as st  # Importar la biblioteca Streamlit para crear la interfaz de usuario
from streamlit_chat import message  # Importar la función message para mostrar mensajes de chat en Streamlit
import re  # Importar el módulo de expresiones regulares

# Establecer el título de la aplicación
st.title("Sistema 2")
# Añadir una descripción debajo del título
st.write("¡Puedes hacerme todas las preguntas sobre mercado y dejar trabajar al equipo de Data Science!")

# Inicializar el estado de la sesión para almacenar preguntas y respuestas si no existen
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = []

# Definir la función que se ejecuta al hacer clic en el botón de enviar
def click():
    # Verificar si el input del usuario no está vacío
    if st.session_state.user != '':
        # Obtener la pregunta del usuario
        pregunta = st.session_state.user
        # Obtener la respuesta llamando a la función consulta del módulo backend
        respuesta = backend.consulta(pregunta)

        # Añadir la pregunta y la respuesta al estado de la sesión
        st.session_state.preguntas.append(pregunta)
        st.session_state.respuestas.append(respuesta)

        # Mostrar la pregunta en el chat
        message(pregunta, is_user=True, key=f"pregunta_{len(st.session_state.preguntas)-1}")
        
        # Mostrar la respuesta en el chat
        if respuesta.isdigit():  # Si la respuesta es solo un número
            st.write(respuesta)
        elif re.match(r'^\|.*\|$', respuesta, re.DOTALL):  # Si es una tabla Markdown
            st.markdown(respuesta, unsafe_allow_html=True)
        else:
            message(respuesta, is_user=False, key=f"respuesta_{len(st.session_state.respuestas)-1}")

        # Limpiar el input de usuario después de enviar la pregunta
        st.session_state.user = ''

# Crear un formulario en Streamlit
with st.form('my-form'):
    # Añadir un campo de texto para que el usuario ingrese su pregunta
    query = st.text_input('¿En qué te puedo ayudar?:', key='user', help='Pulsa Enviar para hacer la pregunta')
    # Añadir un botón de submit que ejecuta la función click cuando se hace clic
    submit_button = st.form_submit_button('Enviar', on_click=click)

# Opcional: Mostrar todas las conversaciones anteriores
# Ya se manejó en la función `click`, por lo que este bloque puede ser removido o adaptado según necesidad