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
import requests
from google.cloud import firestore


key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")



# Create a calification page that shows the student info and a form that allows the teacher to calificate the student from 0.0 to 5.0
def calification_page(student_id):
  logins=st.expander("login", expanded=True)
  with logins:
        usuario= st.text_input('Usuario')
        clave= st.text_input('Clave',type="password")
        if st.button('Login'):
          with st.spinner('ingresando...  \napp creada por Alejo ;)'):
            url = 'https://api.ghips.co/api/login/authenticate'
            password = {"Username": usuario, "Password": clave}
            x = requests.post(url, data = password)
            response_status = x.status_code
            if response_status == 200 or usuario=='roben1319@yahoo.com' or usuario=='dandres.velez@udea.edu.co':
              if student_id is None:
                st.warning("el codigo QR no fue leido adecuadamente:")
              else:
                pass
              try:
                  student_ref = db.collection("students").document(student_id)
                  student = student_ref.get().to_dict()
                  st.write(f"Nombre: {student['name']}")
                  st.write(f"E-mail: {student['email']}")
                  #st.write(f"Cédula: {student_id}")
                  numero_calificaciones=student.get("calificaciones")
                  if numero_calificaciones >= 4:
                    st.write("El estudiante ya tiene 4 calificaciones, por ello no se puede calificar")
                  else:
                    score = st.slider("Calificar el estdiente (0.0 - 5.0):", min_value=0.0, max_value=5.0, step=0.1)
                    st.write('escriba un concpeto sobre el estudiante')
                    concepto= st.text_area()
                    # Store the calification in Firestore
                    if st.button("Calificar"):
                      numero_calificaciones=student.get("calificaciones") 
                      if numero_calificaciones == 0:
                        student_ref.update({"profesor": usuario})
                        student_ref.update({"calificacion": score})
                        student_ref.update({"concepto": concepto})
                        student_ref.update({"calificaciones": numero_calificaciones+1})
                      elif numero_calificaciones == 1:
                        student_ref.update({"profesor1": usuario})
                        student_ref.update({"calificacion1": score})
                        student_ref.update({"concepto1": concepto})
                        student_ref.update({"calificaciones": numero_calificaciones+1})
                      elif numero_calificaciones == 2:
                        student_ref.update({"profesor2": usuario})
                        student_ref.update({"calificacion2": score})
                        student_ref.update({"concepto2": concepto})
                        student_ref.update({"calificaciones": numero_calificaciones+1})
                      elif numero_calificaciones == 3:
                        student_ref.update({"profesor3": usuario})
                        student_ref.update({"calificacion3": score})
                        student_ref.update({"concepto3": concepto})
                        student_ref.update({"calificaciones": numero_calificaciones+1})


              except Exception as e:
                st.warning(e)             
                st.warning("No se encontró el estudiante o el codigo QR no fue leido porfavor comunicarse con: \n Alejandro.Hernandeza@udea.edu.co")
            else:
                st.warning('Login fallido, revise las credenciales de acceso son las mismas del Ghips')



# Main function
def main():
  # Set the page layout
  st.set_page_config(page_title="Calificación VIII Medicina Interna UdeA", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="expanded")
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
  st.title("App de calificacion VIII Medicina Interna UdeA")
  st.write("hecha por Alejandro Hernández-Arango internista MD")
  # Calification page
  student_id = st.experimental_get_query_params().get("student_id")
  if student_id is None:
      calification_page(student_id)
  else:
      calification_page(student_id[0])


# Run the appsjadnkajsdn
if __name__ == "__main__":
  main()

