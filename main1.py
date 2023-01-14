
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



key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")

def set_time():
  tz_col = pytz.timezone('America/Bogota') 
  fecha = datetime.now(tz_col).strftime('%a, %d %b %Y %I:%M %p')
  return fecha

#---------------------------------#

#---------------------------------#

# Function to upload a database in xlsx format with the list of students name, e-mail, and id
def upload_database():
  data = st.file_uploader("Subir base de datos de estudiantes, debe tener id, nombre, email", type="xlsx")
  if data is not None:
    df = pd.read_excel(data)
    return df

# Function to generate a QR code for each student
def generate_qr_codes(df, materia,fecha):
  qr_png={}
  for i, row in df.iterrows():
    url = f"https://qrudeamedicina.streamlit.app/?student_id={int(row['id'])}&materia={materia}"
    qr = pyqrcode.create(url)
    # Download png image of the QR code with student name and id caption
    qr.png(f"{row['name']}_{row['id']}.png", scale=6)
    qr_png[row['name']]=f"{row['name']}_{row['id']}.png"
    # button to download all the QR codes
  zipObj = ZipFile(f'todos_qr_codes_{materia}_{fecha}.zip', 'w')
  for key in qr_png:
        zipObj.write(qr_png[key])
  zipObj.close()
  #download zip in streamlit
  b64 = base64.b64encode(open(f'todos_qr_codes_{materia}_{fecha}.zip', 'rb').read()).decode()
  href = f'<a href="data:file/zip;base64,{b64}" download=f"todos_qr_codes_{materia}_{fecha}.zip">Download zip file</a>'
  st.markdown(href, unsafe_allow_html=True)

  return qr_png

# Create a function to store all the data in Firestore
def store_data_in_firestore(df,fecha, materia):
  for i, row in df.iterrows():
    student_ref = db.collection("students").document(str(int(row['id'])))
    student_ref.set({
      'name': row['name'],
      'email': row['email'],
      'calificaciones': 0,
      'materia':materia
    })

#---------------------------------#



#---------------------------------....#


# Main function
def main():
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
  st.title("App Crear codigos QR y abrir base de datos de estudiantes")
  st.subheader("-Medicina Interna UdeA-")
  st.caption ("hecha por Alejandro Hernández-Arango MD")
  materias=['vejez', 'internado', 'adultez_I', 'cancer']
  materia=st.selectbox("Seleccione la materia", materias)
  # Upload the database
  df = upload_database()

  if df is not None:
    #set_time()
    fecha = set_time()
    store_data_in_firestore(df, fecha, materia)
    st.success("Base de datos cargada exitosamente y guardada exitosamente")
    # Generate QR codes
    if st.button("Generar códigos QR"):
      generate_qr_codes(df, materia)
      st.success("códigos QR generados exitosamente")
  if st.button("bajar todas las notas calificaciones de una materia en xlsx"):
    student_ref = db.collection("students")
    docs = student_ref.where('materia', '==', materia).where("calificacion0", "array_contains", "0").where("calificacion1", "array_contains", "0").where("calificacion2", "array_contains", "0").where("calificacion3", "array_contains", "0").where("calificacion4", "array_contains", "0").get()
    df = pd.DataFrame(columns=['id', 'name', 'email', 'calificaciones'])
    for doc in docs:
        df = pd.concat([df, pd.DataFrame({'id': doc.id, 'name': doc.to_dict().get('name', None), 'email': doc.to_dict().get('email', None), 'calificaciones': doc.to_dict().get('calificaciones', None)}, index=[0])], ignore_index=True)
    df.to_excel(f"notas_{materia}.xlsx", index=False)
    b64 = base64.b64encode(open(f"notas_{materia}.xlsx", 'rb').read()).decode()
    href = f'<a href="data:file/xlsx;base64,{b64}" download="notas_{materia}.xlsx">Download xlsx file</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.success("notas descargadas exitosamente")



  #if st.button("asignar la materia adultez_I a los estudiantes existentes en la base de datos"):
    #student_ref = db.collection("students")
    #docs = student_ref.get()
    #for doc in docs:
      #doc_ref = db.collection("students").document(doc.id)
      #doc_ref.update({
      #'materia': 'adultez_I'
    #})
    #st.success("materia asignada exitosamente")


# Run the app
if __name__ == "__main__":
  main()

