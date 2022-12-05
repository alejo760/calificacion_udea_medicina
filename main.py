import streamlit as st
import pandas as pd
import pyqrcode
import png
import base64


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

# Function to generate a QR code for each student
def generate_qr_codes(df):
  qrdict={}
  for i, row in df.iterrows():
    url = f"https://qrudeamedicina.streamlit.app/?student_id={row['id']}"
    qr = pyqrcode.create(url)
    # Save the QR code as an image file
    #append to qrdict
    qrdict[row['id']]=qr.png_as_base64_str(scale=8)
  df['QR']=qrdict
    

    
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

def get_table_download_link(df):
  """Generates a link allowing the data in a given panda dataframe to be downloaded
  in:  dataframe
  out: href string
  """
  csv = df.to_excel(index=False)
  b64 = base64.b64encode(
      csv.encode()
  ).decode()  # some strings <-> bytes conversions necessary here
  return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


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

    if st.button("Download QR codes"):
      st.markdown(get_table_download_link(df), unsafe_allow_html=True)

  # Calification page
  student_id = st.text_input("Enter student id:")
  if student_id:
    calification_page(student_id)

# Run the app
if __name__ == "__main__":
  main()

