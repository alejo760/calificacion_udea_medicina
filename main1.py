import streamlit as st
import pandas as pd
import pyqrcode
import base64
import json
from zipfile import ZipFile
import requests
from datetime import datetime, timedelta

# Function to check if a user exists in Moodle by email
def user_email_exists(api_url, token, email):
    function_name = "core_user_get_users"
    params = {
        "wstoken": token,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "criteria[0][key]": "email",
        "criteria[0][value]": email,
    }

    response = requests.post(api_url, data=params)
    if response.status_code == 200:
        try:
            users = response.json().get('users', [])
            if len(users) > 0:
                return users[0]['id']  # Return the user ID
            else:
                return None
        except ValueError:
            st.error(f"Error: Respuesta no válida al verificar email {email}: {response.text}")
            return None
    else:
        st.error(f"Error verificando email {email}: {response.status_code} {response.text}")
        return None

# Function to create a user in Moodle
def create_user(api_url, token, email, firstname, lastname, idnumber):
    function_name = "core_user_create_users"
    password = "DefaultPassword123!"  # You can generate a random password if needed
    params = {
        "wstoken": token,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "users[0][username]": email,
        "users[0][email]": email,
        "users[0][firstname]": firstname,
        "users[0][lastname]": lastname,
        "users[0][idnumber]": idnumber,
        "users[0][auth]": "manual",
        "users[0][lang]": "es",
        "users[0][password]": password,
        "users[0][createpassword]": 0,
    }

    response = requests.post(api_url, data=params)
    if response.status_code == 200:
        try:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']  # Return the created user ID
            else:
                st.error(f"Error creando usuario {email}: {response.text}")
                return None
        except ValueError:
            st.error(f"Error: Respuesta no válida al crear usuario {email}: {response.text}")
            return None
    else:
        st.error(f"Error creando usuario {email}: {response.status_code} {response.text}")
        return None

# Function to enroll a user in a Moodle course
def enrol_user_in_course(api_url, token, roleid, userid, courseid, timestart=None, timeend=None, suspend=0):
    function_name = "enrol_manual_enrol_users"
    params = {
        "wstoken": token,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "enrolments[0][roleid]": roleid,
        "enrolments[0][userid]": userid,
        "enrolments[0][courseid]": courseid,
        "enrolments[0][suspend]": suspend,
    }
    if timestart:
        params["enrolments[0][timestart]"] = timestart
    if timeend:
        params["enrolments[0][timeend]"] = timeend

    response = requests.post(api_url, data=params)
    if response.status_code == 200:
        return True  # Enrollment successful
    else:
        st.error(f"Error matriculando usuario {userid} en el curso {courseid}: {response.status_code} {response.text}")
        return False

# Function to generate QR codes
def generate_qr_codes(df, materia):
    fecha = datetime.now().strftime('%Y%m%d%H%M%S')
    qr_png = {}
    for i, row in df.iterrows():
        url = f"https://qrudeamedicina.streamlit.app/?student_id={int(row['id'])}&materia={materia}"
        qr = pyqrcode.create(url)
        qr_filename = f"{row['name']}_{row['id']}.png"
        qr.png(qr_filename, scale=6)
        qr_png[row['name']] = qr_filename

    # Create zip file
    zip_filename = f'qr_codes_{fecha}.zip'
    with ZipFile(zip_filename, 'w') as zipObj:
        for key in qr_png:
            zipObj.write(qr_png[key])

    # Provide download link
    b64 = base64.b64encode(open(zip_filename, 'rb').read()).decode()
    href = f'<a href="data:file/zip;base64,{b64}" download="{zip_filename}">Descargar archivo ZIP con códigos QR</a>'
    st.markdown(href, unsafe_allow_html=True)

    return qr_png

# Main function
def main():
    st.image(
        "https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES",
        width=200,
    )
    st.title("App Crear códigos QR y crear usuarios en Moodle")
    st.subheader("-Medicina Interna UdeA-")
    st.caption("Hecha por Alejandro Hernández-Arango MD")

    # Moodle API configuration
    api_url = st.secrets["API_MOODLE_URL"]
    token = st.secrets["API_MOODLE"]

    # Define course ID and role ID
    courseid = 5  # "medicina interna interna internado"
    roleid = 5    # Student role ID in Moodle

    materia = st.selectbox("Seleccione la materia", ["Medicina Interna Internado"])

    # Date pickers for enrollment start and end dates
    st.write("Seleccione la fecha de inicio y fin de la matriculación")
    col1, col2 = st.columns(2)
    with col1:
        timestart = st.date_input("Fecha de inicio", value=datetime.now().date())
    with col2:
        timeend = st.date_input("Fecha de fin", value=(datetime.now() + timedelta(days=30)).date())

    # Convert dates to timestamps
    timestart_timestamp = int(datetime.combine(timestart, datetime.min.time()).timestamp())
    timeend_timestamp = int(datetime.combine(timeend, datetime.min.time()).timestamp())

    # Upload the database
    data_file = st.file_uploader(
        "Subir base de datos de estudiantes (debe tener columnas: id, name, email)", type="xlsx"
    )
    if data_file is not None:
        df = pd.read_excel(data_file)
        st.success("Base de datos cargada exitosamente")
        if st.button("Crear usuarios y matricular en Moodle"):
            for i, row in df.iterrows():
                email = row['email']
                fullname = row['nombre'].split()
                firstname = fullname[0] if len(fullname) > 0 else ''
                lastname = ' '.join(fullname[1:]) if len(fullname) > 1 else ''
                idnumber = str(row['id'])

                # Check if user exists
                userid = user_email_exists(api_url, token, email)
                if userid:
                    st.info(f"El usuario con email {email} ya existe. ID: {userid}")
                else:
                    # Create user
                    userid = create_user(api_url, token, email, firstname, lastname, idnumber)
                    if userid:
                        st.success(f"Usuario {email} creado con ID {userid}")
                    else:
                        st.error(f"Error creando usuario {email}")
                        continue  # Skip to next user

                # Enroll user in course
                enrolment_success = enrol_user_in_course(
                    api_url, token, roleid, userid, courseid, timestart_timestamp, timeend_timestamp
                )
                if enrolment_success:
                    st.success(f"Usuario {email} matriculado en el curso {courseid}")
                else:
                    st.error(f"Error matriculando usuario {email} en el curso")

            # Generate QR codes
            if st.button("Generar códigos QR"):
                generate_qr_codes(df, materia)
                st.success("Códigos QR generados exitosamente")

# Run the app
if __name__ == "__main__":
    main()
