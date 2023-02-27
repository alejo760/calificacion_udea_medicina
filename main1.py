
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
def upload_database_json():
  data = st.file_uploader("Subir base de datos de estudiantes en json", type="json")
  if data is not None:
    df = pd.read_json(data)
    return df
  
# Function to generate a QR code for each student
def generate_qr_codes(df, materia):
  fecha=set_time()
  qr_png={}
  for i, row in df.iterrows():
    url = f"https://qrudeamedicina.streamlit.app/?student_id={int(row['id'])}&materia={materia}"
    qr = pyqrcode.create(url)
    # Download png image of the QR code with student name and id caption
    qr.png(f"{row['name']}_{row['id']}.png", scale=6)
    qr_png[row['name']]=f"{row['name']}_{row['id']}.png"
    # button to download all the QR codes
  zipObj = ZipFile(f'todos_qr_codes.zip', 'w')
  for key in qr_png:
        zipObj.write(qr_png[key])
  zipObj.close()
  #download zip in streamlit
  b64 = base64.b64encode(open(f'todos_qr_codes.zip', 'rb').read()).decode()
  href = f'<a href="data:file/zip;base64,{b64}" download="todos_qr_codes.zip">Download zip file</a>'
  st.markdown(href, unsafe_allow_html=True)

  return qr_png

# Create a function to store all the data in Firestore and check if the student exists and if exists dont update
def store_data_in_firestore(df,collection, materia):
  for i, row in df.iterrows():
    student_ref = db.collection(collection).document(str(int(row['id'])))
    student = student_ref.get()
    if student.exists:
      st.warning(f"El estudiante {row['name']} ya existe en la base de datos")
    else:
      student_ref.set({
        'name': row['name'],
        'email': row['email'],
        'calificaciones': 0,
        'materia':materia
      })
      st.success(f"El estudiante {row['name']} fue agregado exitosamente a la base de datos")

#create new collection in firestore from a json file
def create_collection_from_json():
  df=upload_database_json()
  if df is not None:
    fecha=set_time()
    for i, row in df.iterrows():
      student_ref = db.collection('students').document(str(int(row['id'])))
      student = student_ref.get()
      if student.exists:
        st.warning(f"El estudiante {row['name']} ya existe en la base de datos")
      else:
        student_ref.set(student)
        st.success(f"El estudiante {row['name']} fue agregado exitosamente a la base de datos")


# Main function
def main():
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
  st.title("App Crear codigos QR y abrir base de datos de estudiantes")
  st.subheader("-Medicina Interna UdeA-")
  st.caption ("hecha por Alejandro Hernández-Arango MD")
  materias=['vejez', 'internado', 'adultez_I']
  collection=st.selectbox("Seleccione la colección", ['students', '2023-1'])
  materia=st.selectbox("Seleccione la materia", materias)
  # Upload the database
  with st.expander("Crear colección desde json"):
   if st.button("Crear colección desde json"):


      create_collection_from_json()
      st.success("Colección creada exitosamente")
  with st.expander("Crear base de datos desde excel"):
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
# generate a xlsx from firestore database
  if st.button(f"Descargar base de datos {materia} del periodo {collection}"):
    #select documents from firestore materia 
    fecha=set_time()
    docs = db.collection(collection).where("materia", "==", materia).stream()
    df = pd.DataFrame(columns=['id', 'name', 'email', 'calificaciones', 'materia'])
    for doc in docs:
      df = df.append(doc.to_dict(), ignore_index=True)
    df.to_json(f'notas_de_{materia}_{fecha}.json', orient="records")
    pd.json_normalize(df)
    b64 = base64.b64encode(open(f'notas_de_{materia}_{fecha}.json', 'rb').read()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="notas_de_{materia}_{fecha}.json">Download json file</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.success("Base de datos descargada exitosamente")




    
 






















#---------------------------------
  

# Run the app
if __name__ == "__main__":
  main()

