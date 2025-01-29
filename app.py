import streamlit as st
from moodle_api import MoodleAPI
import os
import json
import logging
from datetime import datetime

# Configuración del sistema de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('moodle_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

MOODLE_TOKEN = "a6b62135f99e445ac5b38b6c9187f6cb"
MOODLE_API_URL = "https://formacion.ghips.co/moodle/webservice/rest/server.php"


# Configuración de la página
st.set_page_config(
    page_title="Calificaciones Moodle",
    page_icon="📚",
    layout="centered"
)

# Inicialización de la API de Moodle
@st.cache_resource
def get_moodle_api():
    try:
        logger.info("Iniciando conexión con Moodle API")
        try:
            api_url = MOODLE_API_URL
            token = MOODLE_TOKEN
            logger.info(f"Usando API URL: {api_url}")
        except FileNotFoundError:
            logger.warning("No se encontró archivo de configuración, usando variables de entorno")
            api_url = os.environ.get('MOODLE_API_URL')
            token = os.environ.get('MOODLE_TOKEN')
        
        if not api_url or not token:
            logger.error("Credenciales de Moodle no encontradas")
            st.error("⚠️ No se encontraron las credenciales de Moodle. La aplicación funcionará en modo limitado.")
            return None
            
        logger.info("Conexión con Moodle API establecida exitosamente")
        return MoodleAPI(api_url, token)
    except Exception as e:
        logger.error(f"Error al inicializar Moodle API: {str(e)}", exc_info=True)
        st.error(f"⚠️ Error de configuración: {str(e)}")
        return None

def main():
    logger.info("Iniciando aplicación")
    st.title("Sistema de Calificaciones Moodle")
    
    moodle = get_moodle_api()
    
    if moodle is None:
        logger.error("No se pudo inicializar la API de Moodle")
        st.warning("🔧 Sistema en mantenimiento")
        st.info("""
        Por favor verifica:
        1. Que el archivo `.streamlit/secrets.toml` existe y tiene los permisos correctos
        2. Que las credenciales de Moodle son correctas
        3. Que tienes conexión al servidor de Moodle
        """)
        st.stop()

    # Formulario de búsqueda de estudiante
    with st.form("search_student"):
        student_id = st.text_input("ID del Estudiante")
        search = st.form_submit_button("Buscar")

        if search and student_id:
            logger.info(f"Buscando estudiante con ID: {student_id}")
            try:
                result = moodle.get_user_by_field('id', student_id)
                if not result["error"]:
                    if result["data"]:
                        st.session_state['student'] = result["data"][0]
                        logger.info(f"Estudiante encontrado: {result['data'][0].get('fullname', 'N/A')}")
                    else:
                        logger.warning(f"No se encontró estudiante con ID: {student_id}")
                        st.warning("⚠️ No se encontró ningún estudiante con ese ID")
                else:
                    logger.error(f"Error al buscar estudiante: {result.get('message')}")
                    st.error(f"❌ Error al buscar estudiante: {result.get('message', 'Error desconocido')}")
            except Exception as e:
                logger.error(f"Error inesperado al buscar estudiante: {str(e)}", exc_info=True)
                st.error(f"❌ Error inesperado: {str(e)}")

    # Formulario de calificación
    if 'student' in st.session_state:
        student = st.session_state['student']
        logger.info(f"Preparando formulario de calificación para: {student['fullname']}")
        
        with st.form("grade_form"):
            course_id = st.number_input("ID del Curso", min_value=1)
            activity_id = st.number_input("ID de la Actividad", min_value=1)
            grade = st.slider("Calificación", 0.0, 5.0, 3.0, 0.1)
            feedback = st.text_area("Retroalimentación")
            submit = st.form_submit_button("Enviar Calificación")

            if submit:
                logger.info(f"Intentando calificar estudiante {student['id']} en curso {course_id}")
                try:
                    result = moodle.update_grade(
                        course_id=course_id,
                        component="mod_quiz",
                        activity_id=activity_id,
                        student_id=student['id'],
                        grade=grade,
                        feedback=feedback
                    )
                    
                    if not result["error"]:
                        logger.info(f"Calificación actualizada exitosamente para estudiante {student['id']}")
                        st.success("✅ Calificación actualizada exitosamente")
                    else:
                        logger.error(f"Error al actualizar calificación: {result.get('message')}")
                        st.error(f"❌ Error al actualizar la calificación: {result.get('message', 'Error desconocido')}")
                except Exception as e:
                    logger.error(f"Error inesperado al calificar: {str(e)}", exc_info=True)
                    st.error(f"❌ Error inesperado al calificar: {str(e)}")

if __name__ == "__main__":
    logger.info("=== Iniciando nueva sesión de la aplicación ===")
    main()
