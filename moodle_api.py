import requests
import logging

logger = logging.getLogger(__name__)

class MoodleAPI:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.token = token
        logger.info(f"MoodleAPI inicializada con URL: {api_url}")

    def update_grade(self, course_id, component, activity_id, student_id, grade, feedback):
        logger.info(f"Actualizando calificación - Estudiante: {student_id}, Curso: {course_id}, Actividad: {activity_id}")
        function_name = 'core_grades_update_grades'
        params = {
            "wstoken": self.token,
            "wsfunction": function_name,
            "moodlewsrestformat": "json",
            "source": "custom_source",
            "courseid": course_id,
            "component": component,
            "activityid": activity_id,
            "itemnumber": 0,
            "grades[0][studentid]": student_id,
            "grades[0][grade]": grade,
            "grades[0][str_feedback]": feedback
        }

        logger.debug(f"Enviando solicitud POST a Moodle con parámetros: {params}")
        response = requests.post(self.api_url, data=params, verify=False)
        return self._handle_response(response)

    def get_user_by_field(self, field, value):
        if field not in ["id", "username"]:
            logger.error(f"Campo no válido: {field}. Solo se permiten 'id' o 'username'.")
            return {
                "error": True,
                "message": "Campo no válido. Solo se permite 'id' o 'username'."
            }

        logger.info(f"Buscando usuario por {field}: {value}")
        function_name = 'core_user_get_users_by_field'
        params = {
            'wstoken': self.token,
            'wsfunction': function_name,
            'moodlewsrestformat': 'json',
            'field': field,
            'values[0]': value
        }

        logger.debug(f"Enviando solicitud GET a Moodle con parámetros: {params}")
        response = requests.get(self.api_url, params=params, verify=False)
        return self._handle_response(response)

    def _handle_response(self, response):
        if response.status_code == 200:
            logger.info("Respuesta exitosa del servidor Moodle")
            data = response.json()
            logger.info(f"Respuesta: {data}")

            if isinstance(data, list) and not data:  # Si la respuesta es una lista y está vacía
                return {
                    "error": False,
                    "data": None
                }
            elif isinstance(data, list):  # Si la respuesta es una lista con datos
                return {
                    "error": False,
                    "data": data
                }
            elif isinstance(data, dict) and data.get('exception'):  # Si la respuesta es un diccionario (posiblemente un error)
                return {
                    "error": True,
                    "message": data.get('message', 'Error desconocido')
                }

            return {
                "error": False,
                "data": data
            }

        logger.error(f"Error en respuesta del servidor: {response.status_code} - {response.text}")
        return {
            "error": True,
            "status_code": response.status_code,
            "message": response.text
        }
