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


# Create a calification page that shows the student info and a form that allows the teacher to calificate the student from 0.0 to 5.0
def calification_page(student_id):
  student_ref = db.collection("students").document(student_id)
  student = student_ref.get().to_dict()
  st.write(f"Name: {student['name']}")
  st.write(f"E-mail: {student['email']}")
  score = st.slider("Enter calification (0.0-5.0):", min_value=0.0, max_value=5.0, step=0.1)
  # Store the calification in Firestore
  student_ref.update({'calification': score})


# Main function
def main():
  st.title("Calification App")
  # Calification page
  student_id = st.experimental_get_query_params().get("student_id")
  if student_id is None:
      student_id = st.text_input("Enter student id:")
      calification_page(student_id)
  else:
      calification_page(student_id[0])


# Run the app
if __name__ == "__main__":
  main()

