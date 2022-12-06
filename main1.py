
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


key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")
#---------------------------------#

#---------------------------------#

# Function to upload a database in xlsx format with the list of students name, e-mail, and id
def upload_database():
  data = st.file_uploader("Subir base de datos de estudiantes, debe tener", type="xlsx")
  if data is not None:
    df = pd.read_excel(data)
    return df

# Function to generate a QR code for each student
def generate_qr_codes(df):
  qr_png={}
  for i, row in df.iterrows():
    url = f"https://qrudeamedicina.streamlit.app/?student_id={int(row['id'])}"
    qr = pyqrcode.create(url)
    # Download png image of the QR code with student name and id caption
    qr.png(f"{row['name']}_{row['id']}.png", scale=6)
    qr_png[row['name']]=f"{row['name']}_{row['id']}.png"
    # button to download all the QR codes
  zipObj = ZipFile('todos_qr_codes.zip', 'w')
  for key in qr_png:
        zipObj.write(qr_png[key])
  zipObj.close()
  #download zip in streamlit
  b64 = base64.b64encode(open('all_qr_codes.zip', 'rb').read()).decode()
  href = f'<a href="data:file/zip;base64,{b64}" download="all_qr_codes.zip">Download zip file</a>'
  st.markdown(href, unsafe_allow_html=True)

  return qr_png

# Create a function to store all the data in Firestore
def store_data_in_firestore(df):
  for i, row in df.iterrows():
    student_ref = db.collection("students").document(str(int(row['id'])))
    student_ref.set({
      'name': row['name'],
      'email': row['email']
    }) 
  
#---------------------------------#



#---------------------------------....#


# Main function
def main():
  st.title("App de calificacion Medicina UdeA prueba hecha por Alejandro Hernández-Arango MD")

  # Upload the database
  df = upload_database()

  if df is not None:
    store_data_in_firestore(df)
    st.success("Base de datos cargada exitosamente y guardada exitosamente")

    # Generate QR codes
    if st.button("Generar códigos QR"):
      generate_qr_codes(df)
      st.success("códigos QR generados exitosamente")


# Run the app
if __name__ == "__main__":
  main()

