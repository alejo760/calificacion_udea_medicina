import streamlit as st
import pandas as pd
import pyqrcode
import base64
import json
from zipfile import ZipFile
import requests
import pytz
from datetime import datetime

# Moodle Configuration (Add these keys to your Streamlit secrets or environment variables)
MOODLE_API_URL = st.secrets["MOODLE_API_URL"]
MOODLE_API_TOKEN = st.secrets["MOODLE_API_TOKEN"]
STUDENT_ROLE_ID = 5  # Role ID for student enrollment

def set_time():
    tz_col = pytz.timezone('America/Bogota')
    fecha = datetime.now(tz_col).strftime('%a, %d %b %Y %I:%M %p')
    return fecha

# Function to upload a database in xlsx format with the list of students name, e-mail, and id
def upload_database():
    data = st.file_uploader("Subir base de datos de estudiantes, debe tener id, nombre, email", type="xlsx")
    if data is not None:
        df = pd.read_excel(data)
        return df

# Function to generate a QR code for each student
def generate_qr_codes(df, materia):
    fecha = set_time()
    qr_png = {}
    for i, row in df.iterrows():
        url = f"https://qrudeamedicina.streamlit.app/?student_id={int(row['id'])}&materia={materia}"
        qr = pyqrcode.create(url)
        qr_filename = f"{row['name']}_{row['id']}.png"
        qr.png(qr_filename, scale=6)
        qr_png[row['name']] = qr_filename

    # Create a ZIP file with all QR codes
    zipObj = ZipFile(f'todos_qr_codes.zip', 'w')
    for key in qr_png:
        zipObj.write(qr_png[key])
    zipObj.close()

    # Provide download link for ZIP file
    b64 = base64.b64encode(open(f'todos_qr_codes.zip', 'rb').read()).decode()
    href = f'<a href="data:file/zip;base64,{b64}" download="todos_qr_codes.zip">Download zip file</a>'
    st.markdown(href, unsafe_allow_html=True)

    return qr_png

# Function to create users in Moodle
def create_users_in_moodle(df):
    for i, row in df.iterrows():
        email = row['email']
        firstname = row['name']
        lastname = "Default"  # You can modify this if you have last names in the data
        user_id = row['id']
        password = "DefaultPassword123!"

        params = {
            "wstoken": MOODLE_API_TOKEN,
            "wsfunction": "core_user_create_users",
            "moodlewsrestformat": "json",
            "users[0][username]": email,
            "users[0][email]": email,
            "users[0][firstname]": firstname,
            "users[0][lastname]": lastname,
            "users[0][idnumber]": user_id,
            "users[0][auth]": "manual",
            "users[0][lang]": "es",
            "users[0][password]": password
        }

        response = requests.post(MOODLE_API_URL, data=params)
        if response.status_code == 200:
            try:
                result = response.json()
                if "error" in result:
                    st.error(f"Error creando usuario {email}: {result['message']}")
                else:
                    st.success(f"Usuario {email} creado exitosamente.")
                    user_moodle_id = result[0]['id']  # Get the created user ID for enrollment
                    enroll_user_in_course(user_moodle_id, STUDENT_ROLE_ID, course_id=2)  # Modify course_id as needed
            except ValueError:
                st.error(f"Respuesta inválida al crear usuario {email}: {response.text}")
        else:
            st.error(f"Error creando usuario {email}: {response.status_code} {response.text}")

# Function to enroll user in Moodle course
def enroll_user_in_course(userid, roleid, course_id):
    params = {
        "wstoken": MOODLE_API_TOKEN,
        "wsfunction": "enrol_manual_enrol_users",
        "moodlewsrestformat": "json",
        "enrolments[0][roleid]": roleid,
        "enrolments[0][userid]": userid,
        "enrolments[0][courseid]": course_id
    }

    response = requests.post(MOODLE_API_URL, data=params)
    if response.status_code == 200:
        try:
            # Success message for enrollment
            st.success(f"Usuario con ID {userid} matriculado exitosamente en el curso con ID {course_id}.")
        except ValueError:
            st.error(f"Respuesta inválida al matricular usuario {userid}: {response.text}")
    else:
        st.error(f"Error matriculando usuario {userid}: {response.status_code} {response.text}")

# Main function
def main():
    st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
    st.title("App Crear codigos QR y subir estudiantes a Moodle")
    st.subheader("-Medicina Interna UdeA-")
    st.caption("hecha por Alejandro Hernández-Arango MD")
    materias = ['Medicina Interna Internado']
    materia = st.selectbox("Seleccione la materia", materias)
    # Upload the database
    with st.expander("Crear base de datos desde excel"):
        df = upload_database()
        if df is not None:
            # Generate QR codes
            if st.button("Generar códigos QR"):
                generate_qr_codes(df, materia)
                st.success("Códigos QR generados exitosamente")

            # Create users in Moodle
            if st.button("Crear usuarios en Moodle y matricular"):
                create_users_in_moodle(df)
                st.success("Usuarios creados y matriculados exitosamente en Moodle")

# Run the app
if __name__ == "__main__":
    main()
