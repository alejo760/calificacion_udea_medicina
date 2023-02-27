
import streamlit as st
import pandas as pd
import pyqrcode
import png
import base64
import io
import xlsxwriter
import json
from zipfile import ZipFile
from firebase_admin import firestore
from google.cloud.firestore import Client
from google.oauth2 import service_account
import firebase_admin
from datetime import datetime
import pytz 
from firebase_admin import credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText







# function to search student in the database by id
def search_student(student_id):
  doc_ref = db.collection(u'Estudiantes').document(f'{student_id}')
  doc = doc_ref.get()
  if doc.exists:
    return doc.to_dict()
  else:
    return None
  
# function to generate a QR code
def generate_qr_code(student_id, materia):
  url = f"https://qrudeamedicina.streamlit.app/?student_id={student_id}&materia={materia}"
  qr = pyqrcode.create(url)
  # Download png image of the QR code with student name and id caption
  qr.png(f"{student_id}.png", scale=6)
  # button to download QR code
  b64 = base64.b64encode(open(f'{student_id}.png', 'rb').read()).decode()
  href = f'<a href="data:file/png;base64,{b64}" download="{student_id}.png">Download QR code</a>'
  st.markdown(href, unsafe_allow_html=True)
  return href



  


def store_data_in_firestore(student_id,email,name, materia):
  doc_ref = db.collection(u'estudiantes').document(f'{student_id}')
  doc_ref.set({
    u'nombre': f'{name}',
    u'email': f'{email}',
    u'materia': f'{materia}'
  })






def set_time():
  tz_NY = pytz.timezone('America/Bogota') 
  datetime_NY = datetime.now(tz_NY)
  fecha=datetime_NY.strftime("%d/%m/%Y %H:%M:%S")
  return fecha




key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")
st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
st.title("App buscar y crear códigos QR de estudiantes")
st.subheader("-Medicina Interna UdeA-")
st.caption ("hecha por Alejandro Hernández-Arango MD")
materias=['vejez', 'internado', 'adultez_I']
materia=st.selectbox("Seleccione la materia", materias)
student_id=st.text_input("Ingrese el id del estudiante")
name = st.text_input("Ingrese el nombre del estudiante")
email = st.text_input("Ingrese el email del estudiante")
if st.button("Buscar estudiante"):
  student = search_student(student_id)
  if student is not None:
    st.success("Estudiante encontrado")
    st.write(student)
  else:
    st.error("Estudiante no encontrado")
if st.button("Crear código QR"):
  fecha = set_time()
  store_data_in_firestore(student_id,email,name, materia)
  st.success("Estudiante creado exitosamente")
  # Generate QR code
  if st.button("Generar códigos QR"):
    generate_qr_code(student_id, materia)
    st.success("código QR generado exitosamente")
    st.write(fecha)
    st.write("El código QR se descargará automáticamente")
    st.write("Si no se descarga, haga click en el botón de abajo")




