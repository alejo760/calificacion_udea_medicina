import streamlit as st
import pandas as pd
import pyqrcode
import png
import base64
import io
import xlsxwriter
import json



from google.cloud import firestore
from google.cloud.firestore import Client
from google.oauth2 import service_account

@st.experimental_singleton
def get_db():
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")

    return db


# Function to upload a database in xlsx format with the list of students name, e-mail, and id
def upload_database():
  data = st.file_uploader("Upload a database in xlsx format", type="xlsx")
  if data is not None:
    df = pd.read_excel(data)
    return df

# Function to generate a QR code for each student in a pdf file and download the pdf file
def generate_qr_codes(df):
  for i, row in df.iterrows():
    # Generate the QR code
    url = pyqrcode.create(row['id'])
    url.png(f"{row['id']} {row['name']}.png", scale=10)

    # Download the QR code
    image = open(f"{row['id']}.png", "rb")
    image_read = image.read()
    b64 = base64.b64encode(image_read).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="{row["id"]}.png">Download {row["id"]}.png</a>'
    st.markdown(href, unsafe_allow_html=True)



    

    
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
  get_db()
  for i, row in df.iterrows():
    student_ref = db.collection("students").document(row['id'])
    student_ref.set({
      'name': row['name'],
      'email': row['email']
    })

def download_df_in_excel(df):
  output = io.BytesIO()
  writer = pd.ExcelWriter(output, engine='xlsxwriter')
  df.to_excel(writer, sheet_name='Sheet1')
  writer.save()
  processed_data = output.getvalue()
  return processed_data

  
  
  
  


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
    #download xlsx in streamlit
    if st.button("Download xlsx"):
      b64 = base64.b64encode(download_df_in_excel(df)).decode()
      href = f'<a href="data:file/xlsx;base64,{b64}" download="myfilename.xlsx">Download xlsx file</a>'
      st.markdown(href, unsafe_allow_html=True)

  # Calification page
  student_id = st.text_input("Enter student id:")
  if student_id:
    calification_page(student_id)

# Run the app
if __name__ == "__main__":
  main()

