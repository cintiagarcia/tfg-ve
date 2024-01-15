import streamlit as st
from openai import OpenAI
import uuid
import time

client = OpenAI()

# Definir la clave de API de OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "run" not in st.session_state:
    st.session_state.run = {"status": None}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retry_error" not in st.session_state:
    st.session_state.retry_error = 0

def app():
    # Función para generar una respuesta del modelo ChatGPT
    def run_chat_app():
        st.title("VE Asistente")
        # Inicializar el asistente de openAI
        if "assistant" not in st.session_state:
            client.api_key = st.secrets["OPENAI_API_KEY"]
            st.session_state.assistant = client.beta.assistants.retrieve(st.secrets["OPENAI_ASSISTANT"])
            st.session_state.thread = client.beta.threads.create(
                metadata={'session_id': st.session_state.session_id}
            )

        elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == "completed":
            st.session_state.messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )
            for message in reversed(st.session_state.messages.data):
                if message.role in ["user", "assistant"]:
                    with st.chat_message(message.role):
                        for content_part in message.content:
                            message_text = content_part.text.value
                            st.markdown(message_text)

        # Chat input
        if prompt := st.chat_input("¿Cómo puedo ayudarte?"):
            with st.chat_message('user'):
                st.write(prompt)

            message_data = {
                "thread_id": st.session_state.thread.id,
                "role": "user",
                "content": prompt
            }

            if "file_id" in st.session_state:
                message_data["file_ids"] = [st.session_state.file_id]

            st.session_state.messages = client.beta.threads.messages.create(**message_data)

            st.session_state.run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread.id,
                assistant_id=st.session_state.assistant.id,
            )
            if st.session_state.retry_error < 3:
                time.sleep(1)
                st.rerun()

        # Manejar el estado
        if hasattr(st.session_state.run, 'status'):
            if st.session_state.run.status == "running":
                with st.chat_message('assistant'):
                    st.write("Pensando ......")
                if st.session_state.retry_error < 3:
                    time.sleep(1)
                    st.rerun()

            elif st.session_state.run.status == "failed":
                st.session_state.retry_error += 1
                with st.chat_message('assistant'):
                    if st.session_state.retry_error < 3:
                        st.write("Fallo en la ejecución, reintentando...")
                        time.sleep(3)
                        st.rerun()
                    else:
                        st.error("Error: OpenAI API esta procesando demasiadas solicitudes. Por favor, intentalo despues ......")

            elif st.session_state.run.status != "completed":
                st.session_state.run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread.id,
                    run_id=st.session_state.run.id,
                )
                if st.session_state.retry_error < 3:
                    time.sleep(3)
                    st.rerun()
    run_chat_app()

