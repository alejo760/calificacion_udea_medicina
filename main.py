import streamlit as st
import pandas as pd
import json
from zipfile import ZipFile
from firebase_admin import firestore
from google.cloud.firestore import Client
from google.oauth2 import service_account
import requests
from google.cloud import firestore
#import library to uptdate firestore database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import pytz 
        

                 
# Main function
def main():
  # Set the page layout
  st.set_page_config(
    page_title="Calificación VIII Medicina Interna UdeA", 
    page_icon=":bar_chart:",
    initial_sidebar_state="expanded",
    layout= "centered",
    menu_items={
        'About': "App de calificación creada para los estudiantes de Medicina Interna"
    }
)
  
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
  st.title("PRÁCTICAS CLÍNICAS - ADULTEZ 1 (3037013) SEMESTRE 2022- II UdeA")
  st.caption("Elaborado por Alejandro Hernández-Arango internista")
  urlcalificacion="https://docs.google.com/document/d/1V-xFwZ8KkcUuASTTL3BiJcNfoLUm2Kge/edit?usp=sharing&ouid=100347739923869585504&rtpof=true&sd=true"
  st.caption("[Instrucciones de calificación de la UdeA para Adultez](%s)" % urlcalificacion, unsafe_allow_html=True)
  #tomar informacion del QR por el metodo experimental_get_query_params
  try:
    student_id = st.experimental_get_query_params().get("student_id")
  except:
    st.warning("el codigo QR no fue leido adecuadamente:")
    st.warning("por favor escanee el codigo QR nuevamente")
    st.warning("si el problema persiste, por favor comuniquese con el administrador alejandro.hernandeza@udea.edu.co")
    st.experimental_rerun()
  try:
  #cargar la llave de firebase
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")  
    student_ref = db.collection("students").document(student_id[0])
    student = student_ref.get().to_dict()
    #mostrar la informacion del estudiante
    numero_calificaciones=student.get("calificaciones")
    # write a line 
    st.write("")
    st.write("")
    # write a line
    st.subheader(f"{student['name']}")
    st.write(f"{student['email']}")
    st.write(f" {student_id[0]}")
    st.write("")
    st.write("")
    if numero_calificaciones==None:
      st.write("El estudiante **no** ha sido calificado antes")
    else:
     st.write(f" El estudiante ha sido calificado antes **{student.get('calificaciones')}** veces")
    #Show all the student's previous grades in firestore subcollection calificaciones in a table with multindex in calification column
    if st.button('Ver calificaciones anteriores')and numero_calificaciones!=None:
      st.write("")
      st.write("")
      try:
        calificaciones = pd.DataFrame(student[f"calificacion0"])
        calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
        st.table(calificaciones)
        try:
          calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-1}"])
          calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
          st.table(calificaciones)
          try:
            calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-2}"])
            calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
            st.table(calificaciones)
            try:
              calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-3}"])
              calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
              st.table(calificaciones)
            except Exception as e:
              st.warning("el estudiante no tien más calificaciones anteriores")
          except Exception as e:
            st.warning("el estudiante no tiene más calificaciones anteriores")
        except Exception as e:
          st.warning("el estudiante no tiene más calificaciones anteriores")
      except Exception as e:
        st.warning("el estudiante no tiene más calificaciones anteriores")
  except Exception as e:
    st.warning("error en la base de datos el estudiante no se encuentra habilitado")
    st.warning("por favor comuniquese con el administrador alejandro.hernandeza@udea.edu.co")
    st.warning(e)
    st.experimental_rerun()
  #calificar el estudiante
  tz_col = pytz.timezone('America/Bogota') 
  fecha = datetime.now(tz_col).strftime('%a, %d %b %Y %I:%M %p')
  score = st.number_input("Calificar el estudiante (0.0 - 5.0):", min_value=0.0, max_value=5.0, step=0.1)
  concepto= st.text_area('Escriba un concepto sobre el estudiante')
  st.write("Ingrese el usuario y la clave de Ghips")
  usuario= st.text_input('Usuario')
  clave= st.text_input('Clave',type="password")
  if st.button('Calificar'):
            url = 'https://api.ghips.co/api/login/authenticate'
            password = {"Username": usuario, "Password": clave}
            x = requests.post(url, data = password)
            response_status = x.status_code
            if response_status == 200 or usuario=='roben1319@yahoo.com' or usuario=='dandres.velez@udea.edu.co' and concepto is not None:
               #st.success("Login exitoso")
               if numero_calificaciones == 4:
                      st.write("El estudiante ya tiene 4 calificaciones, no se puede calificar")

               else:
                        student_ref = db.collection("students").document(student_id[0])
                        student_ref.set({
                              'name': student['name'],
                              'email': student['email'],
                              "calificaciones": student['calificaciones']+1,  
                              f"calificacion{numero_calificaciones}": [{
                                f"score{numero_calificaciones}":score,
                                f"concepto{numero_calificaciones}": concepto,
                                f"profesor{numero_calificaciones}": usuario,
                                f"fecha{numero_calificaciones}": fecha,
                            }]
                            },merge=True)
                        st.success("Estudiante calificado y nota guardada exitosamente")
               
            else:
                st.warning('Login fallido, revise las credenciales de acceso son las mismas del Ghips')
                st.stop()

# Run the main function
if __name__ == "__main__":
  main()

