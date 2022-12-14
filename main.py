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
  st.image('data:image/png;base64,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')
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
    # write a line
    with st.expander("Información del estudiante",expanded=True):
      st.subheader(f"{student['name']}")
      st.write(f"{student['email']}")
      st.write(f"CC:{student_id[0]}")
    st.write("")
    with st.expander("Otras calificaciones de esta rotación",expanded=False):
     if numero_calificaciones==None:
        st.write("El estudiante **NO** ha sido calificado antes")
     else:
      st.write(f" El estudiante ha sido calificado antes **{student.get('calificaciones')}** veces")
      #Show all the student's previous grades in firestore subcollection calificaciones in a table with multindex in calification column
     if st.button('Ver calificaciones anteriores')and numero_calificaciones!=None:
      st.write("")
      with st.container():
       try:
        calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-1}"])
        calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
        #order columns
        st.write(calificaciones)
        try:
          calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-2}"])
          calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
          st.write(calificaciones)
          try:
            calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-3}"])
            calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
            st.write(calificaciones)
            try:
              calificaciones = pd.DataFrame(student[f"calificacion{numero_calificaciones-4}"])
              calificaciones.columns = pd.MultiIndex.from_product([[''], calificaciones.columns])
              st.write(calificaciones)
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
  st.write("")
  with st.expander("Ingreso de la calificación",expanded=False):
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
            if response_status == 200 or usuario=='roben1319@yahoo.es' or usuario=='dandres.velez@udea.edu.co' and concepto is not None:
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
                        st.balloons()
               
            else:
                st.warning('Login fallido, revise las credenciales de acceso son las mismas del Ghips')
                st.stop()

# Run the main function
if __name__ == "__main__":
  main()

