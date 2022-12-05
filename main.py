import streamlit as st
import pandas as pd
import pyqrcode
from firebase_admin import firestore

# Initialize Firestore

# Get the Firestore credentials from Streamlit secrets
creds = st.secrets.get("firebase_credentials")

# Create a Firestore client using the credentials
db = firestore.client(credentials=creds)



# Function to upload a database in xlsx format with the list of students name, e-mail, and id
def upload_database():
  data = st.file_uploader("Upload a database in xlsx format", type="xlsx")
  if data is not None:
    df = pd.read_excel(data)
    return df

# Function to generate a QR code for each student
def generate_qr_codes(df):
  for i, row in df.iterrows():
    url = f"https://my-calification-page.com?student_id={row['id']}"
    qr = pyqrcode.create(url)
    # Save the QR code as an image file
    qr.png(f"qr_codes/{row['id']}.png", scale=6)

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
    student_ref = db.collection("students").document(row['id'])
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
  student_id = st.text_input("Enter student id:")
  if student_id:
    calification_page(student_id)

# Run the app
if __name__ == "__main__":
  main()

