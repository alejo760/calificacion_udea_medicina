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


key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")



# Function to upload a database in xlsx format with the list of students name, e-mail, and id
def upload_database():
  data = st.file_uploader("Upload a database in xlsx format", type="xlsx")
  if data is not None:
    df = pd.read_excel(data)
    return df

# Function to generate a QR code for each student
def generate_qr_codes(df):
  qr_png={}
  for i, row in df.iterrows():
    url = f"https://qrudeamedicina.streamlit.app/?student_id={row['id']}"
    qr = pyqrcode.create(url)
    # Download png image of the QR code with student name and id caption
    qr.png(f"{row['name']}_{row['id']}.png", scale=6)
    qr_png[row['name']]=f"{row['name']}_{row['id']}.png"
    # button to download all the QR codes
  zipObj = ZipFile('all_qr_codes.zip', 'w')
  for key in qr_png:
        zipObj.write(qr_png[key])
  zipObj.close()
  #download zip in streamlit
  b64 = base64.b64encode(open('all_qr_codes.zip', 'rb').read()).decode()
  href = f'<a href="data:file/zip;base64,{b64}" download="all_qr_codes.zip">Download zip file</a>'
  st.markdown(href, unsafe_allow_html=True)

  return qr_png
    

# create a streamlit page for each student f"https://qrudeamedicina.streamlit.app/?student_id={row['id']}" to calificate the student

    

    
# Create a calification page that shows the student info and a form that allows the teacher to calificate the student from 0.0 to 5.0
def calification_page(student_id):
  student_ref = db.collection("students").document(student_id)
  student = student_ref.get().to_dict()
  st.write(f"Name: {student['name']}")
  st.write(f"E-mail: {student['email']}")
  score = st.number_input("Enter calification (0.0-5.0):", min_value=0.0, max_value=5.0)
  # Store the calification in Firestore
  student_ref.update({'calification': score})

# Create a function to store all the data in Firestore
def store_data_in_firestore(df):
  for i, row in df.iterrows():
    student_ref = db.collection("students").document(str(int(row['id'])))
    student_ref.set({
      'name': row['name'],
      'email': row['email']
    })


  
  
  
  


# Main function
def main():
  st.title("Calification App")

  # Upload the database
  df = upload_database()
  if df is not None:
    st.success("Database uploaded successfully")

    # Generate QR codes
    if st.button("Generate QR codes"):
      generate_qr_codes(df)
      st.success("QR codes generated successfully")

    # Store the data in Firestore
    if st.button("Store data in Firestore"):
      store_data_in_firestore(df)
      st.success("Data stored successfully in Firestore")

  # Calification page
 #st.text_input("Enter student id:")
    
    student_id = st.experimental_get_query_params().get("student_id")
    st.header(student_id)

    if student_id is None:
      student_id = st.text_input("Enter student id:")
      calification_page(student_id)
    else:
      calification_page(student_id)


# Run the app
if __name__ == "__main__":
  main()

