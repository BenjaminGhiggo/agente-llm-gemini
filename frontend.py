# frontend.py

import backend
import streamlit as st
from streamlit_chat import message

st.title("Asistente de Consultas SQL")
st.write("Haz preguntas sobre la base de datos y obtén respuestas al instante.")

if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = []

def click():
    if st.session_state.user != '':
        pregunta = st.session_state.user
        respuesta = backend.consulta(pregunta)

        st.session_state.preguntas.append(pregunta)
        st.session_state.respuestas.append(respuesta)

        st.session_state.user = ''

with st.form('my-form'):
    query = st.text_input('¿En qué te puedo ayudar?', key='user', help='Escribe tu pregunta y presiona Enviar')
    submit_button = st.form_submit_button('Enviar', on_click=click)

if st.session_state.preguntas:
    for i in range(len(st.session_state.respuestas)-1, -1, -1):
        message(f"**Pregunta:** {st.session_state.preguntas[i]}", is_user=True, key=f"pregunta_{i}")
        message(f"**Respuesta:** {st.session_state.respuestas[i]}", key=f"respuesta_{i}")

    continuar_conversacion = st.checkbox('¿Quieres hacer otra pregunta?')
    if not continuar_conversacion:
        st.session_state.preguntas = []
        st.session_state.respuestas = []
