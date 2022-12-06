import streamlit as st
import pandas as pd
from zipfile import ZipFile
from pyqrcode import QRCode
from firebase_admin import firestore
from google.cloud.firestore import Client
from google.oauth2 import service_account


key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")
#---------------------------------#



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

# Create a calification page that opens with tge qr code that shows the student info and a form that allows the teacher to calificate the student from 0.0 to 5.0


#---------------------------------#



#---------------------------------#









students = st.file_uploader("Upload student database (Excel)", type="xlsx")

if students:
    df = pd.read_excel(students)
    for index, row in df.iterrows():
        student_id = row['id']
        student_name = row['name']
            # create a QR code for each student
        url = f"https://qrudeamedicina.streamlit.app/student/{student_id}"
        qr = QRCode(url)
        img = qr.png_as_base64_str(scale=6)
        st.image(Image.open(img), width=300)

    # calificate the student from 0.0 to 5.0
    calification = st.slider(f"Calification for {student_name}", 0.0, 5.0)
    st.button("Submit calification")
    st.write(f"Calification for student {student_id}: {calification}")