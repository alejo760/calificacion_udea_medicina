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
    page_icon=":bar_chart:", layout="wide", 
    initial_sidebar_state="expanded",
    )
  
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=200)
  st.title("App de calificacion VIII Medicina Interna UdeA")
  st.write("hecha por Alejandro Hernández-Arango internista MD")
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
    st.subheader(f"Nombre: {student['name']}")
    st.write(f"E-mail: {student['email']}")
    st.write(f"Cédula: {student_id[0]}")
    st.write(f" El estudiante ha sido calificado antes {student.get('calificaciones')} veces")
    #mostrar las calificaciones anteriores
    if st.button('Mostrar calificaciones anteriores'):
      try:
       df_student= pd.DataFrame(student, index=[0])
       df_student=df_student.set_index('calificaciones')
       st.table(df_student)
      except Exception as e:
        st.write(e)
      try: 
        st.write(f"Fecha: {student.get('fecha1')}")
        st.write(f"Profesor: {student.get('profesor1')}")  
        st.write(f"Calificacion: {student.get('calificacion1')}")
        st.write(f"Concepto: {student.get('concepto1')}")
      except: 
        pass
      try:
        st.write(f"Fecha: {student.get('fecha2')}")
        st.write(f"Profesor: {student.get('profesor2')}")  
        st.write(f"Calificacion: {student.get('calificacion2')}")
        st.write(f"Concepto: {student.get('concepto2')}")
      except: 
        pass    
      try:
        st.write(f"Fecha: {student.get('fecha3')}")
        st.write(f"Profesor: {student.get('profesor3')}")  
        st.write(f"Calificacion: {student.get('calificacion3')}")
        st.write(f"Concepto: {student.get('concepto3')}")
      except: 
        pass
    else:
      pass
  except:
    st.warning("error en la base de datos el estudiante no se encuentra habilitado")
    st.warning("por favor comuniquese con el administrador alejandro.hernandeza@udea.edu.co")
    st.experimental_rerun()
  #calificar el estudiante
  tz_col = pytz.timezone('America/Bogota') 
  fecha = datetime.now(tz_col).strftime('%a, %d %b %Y %I:%M %p')
  score = st.slider("Calificar el estudiante (0.0 - 5.0):", min_value=0.0, max_value=5.0, step=0.1)
  concepto= st.text_area('escriba un concepto sobre el estudiante')
  loginexitoso =0
  usuario= st.text_input('Usuario')
  clave= st.text_input('Clave',type="password")
  if st.button('Calificar'):
            url = 'https://api.ghips.co/api/login/authenticate'
            password = {"Username": usuario, "Password": clave}
            x = requests.post(url, data = password)
            response_status = x.status_code
            if response_status == 200 or usuario=='roben1319@yahoo.com' or usuario=='dandres.velez@udea.edu.co' and concepto is not None:
               st.success("Login exitoso")
               if numero_calificaciones == 4:
                      st.write("El estudiante ya tiene 4 calificaciones, no se puede calificar")

               elif numero_calificaciones == 0 or numero_calificaciones == None:
                        student_ref = db.collection("students").document(student_id[0])
                        student_ref.set({
                              'name': student['name'],
                              'email': student['email'],  
                              "profesor": usuario,
                              "calificacion": score,
                              "concepto": concepto,
                              "calificaciones": student['calificaciones']+1,
                              "fecha": fecha,
                            })
                        st.success("Estudiante calificado y nota guardada exitosamente")
      
               elif numero_calificaciones == 1:
                            student_ref.update({"profesor1": usuario})
                            student_ref.update({"calificacion1": score})
                            student_ref.update({"concepto1": concepto})
                            student_ref.update({"calificaciones": 2})
                            student_ref.update({"fecha1": fecha})
                            st.success("Estudiante calificado y nota guardada exitosamente")
               elif numero_calificaciones == 2:
                            student_ref.update({"profesor2": usuario})
                            student_ref.update({"calificacion2": score})
                            student_ref.update({"concepto2": concepto})
                            student_ref.update({"calificaciones": 3})
                            student_ref.update({"fecha2": fecha})
                            st.success("Estudiante calificado y nota guardada exitosamente")
               elif numero_calificaciones == 3:
                            student_ref.update({"profesor3": usuario})
                            student_ref.update({"calificacion3": score})
                            student_ref.update({"concepto3": concepto})
                            student_ref.update({"calificaciones": 4})
                            student_ref.update({"fecha3": fecha})
                            st.success("Estudiante calificado y nota guardada exitosamente")

               else:
                st.warning('error en la base de datos')
                st.stop()       

            else:
                st.warning('Login fallido, revise las credenciales de acceso son las mismas del Ghips')
                st.stop()

# Run the main function
if __name__ == "__main__":
  main()




    student_ref = db.collection("students")
    docs = student_ref.where('materia', '==', materia).get()
    df = pd.DataFrame(columns=['id', 'name', 'email', 'calificaciones'])
    for doc in docs:
      df = pd.concat([df, pd.DataFrame({'id': doc.id, 'name': doc.to_dict().get('name', None), 'email': doc.to_dict().get('email', None), 
      'calificaciones': doc.to_dict().get('calificaciones', None)}, index=[0])], ignore_index=True)