
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
  


# Function to generate a QR code for the student
def generate_qr_codes(materia,student_id):
  url = f"https://qrudeamedicina.streamlit.app/?student_id={student_id}&materia={materia}"
  qr = pyqrcode.create(url)
  # Download png image of the QR code with student name and id caption
  qr.png(f"{student_id}.png", scale=6)
  qr_png=f"{student_id}.png"
  return qr_png


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
if st.button("Buscar"):
    student = search_student(student_id)
    if student is not None:
      st.success(f"Estudiante encontrado: {student['name']}")
      st.write(student)
      # Generate QR codes
      if st.button("Generar códigos QR"):
        qr_png = generate_qr_codes(materia,student_id)
        st.image(qr_png)
    else:
      st.error("Estudiante no encontrado")
      if st.button("Guardar estudiante"):
          store_data_in_firestore(student_id,email,name, materia)
          st.success("Estudiante guardado")
          st.balloons()
          qr_png = generate_qr_codes(materia,student_id)
          st.image(qr_png)
          st.write("Código QR generado")


