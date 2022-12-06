import streamlit as st
import pandas as pd
from PIL import Image
from pyqrcode import QRCode
from firebase_admin import firestore
from google.cloud.firestore import Client
from google.oauth2 import service_account


key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-reddit")

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