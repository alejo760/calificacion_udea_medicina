
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

  fecha=set_time()
  qr_png={}
  url = f"https://qrudeamedicina.streamlit.app/?student_id={student_id}&materia={materia}"
  qr = pyqrcode.create(url)
  return qr_png



#---------------------------------#



#---------------------------------....#


# Main function
def main():
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
  st.title("App buscar y crear códigos QR de estudiantes")
  st.subheader("-Medicina Interna UdeA-")
  st.caption ("hecha por Alejandro Hernández-Arango MD")
  materias=['vejez', 'internado', 'adultez_I']
  materia=st.selectbox("Seleccione la materia", materias)
  student_id=st.text_input("Ingrese el id del estudiante")
  if st.button("Buscar"):
    student = search_student(student_id)
    if student is not None:
      st.success(f"Estudiante encontrado: {student['name']}")
      st.write(student)
      # Generate QR codes
      if st.button("Generar códigos QR"):
        qr_png = generate_qr_codes(materia)
        st.image(qr_png[student['name']])
    else:
      st.error("Estudiante no encontrado")

  # Generate a QR code for the student



if __name__ == "__main__":


  key_dict = json.loads(st.secrets["textkey"])
  creds = service_account.Credentials.from_service_account_info(key_dict)
  db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")
  main()

#---------------------------------#



    
 






















#---------------------------------
  

# Run the app
if __name__ == "__main__":
  main()

