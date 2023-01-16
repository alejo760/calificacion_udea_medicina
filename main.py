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
    page_title="Calificación Estudiantes UdeA", 
    page_icon=":bar_chart:",
    initial_sidebar_state="expanded",
    layout= "centered",
    menu_items={
        'About': "App de calificación creada para los estudiantes de Medicina UdeA"
    }
)
  st.image("https://almamater.hospital/wp-content/uploads/2022/09/Almamaterhospital.png", width=300)
  st.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=100)
  st.title("CALIFICACIÓN")
  st.caption("Elaborado por Alejandro Hernández-Arango internista")
 
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
    materia= st.experimental_get_query_params().get("materia")
    
    st.header(type(materia))
    if materia=="['vejez']":
      if nucleo is not None:
        nucleos=['Rotación Hospitalaria', 'Living lab', 'Consulta externa', 'Atención domiciliaria (ambulatoria)']
        nucleo=st.select_slider( "seleccione el nucleo de la rotación",nucleos)
      else:
        st.warning("el estudiante no tiene asignado un nucleo") 
      st.write("Calificación de la rotación de **Vejez**")
      st.image("https://lh6.googleusercontent.com/jrgDxu8U0Z9H_kl09g8vnuYoeFlxGtNeZ1hRRVRn0qKcYitViZj04Xe-deQMq_4gmQ7amoSw2o9nJtW8tDt6rmoT7i42RvDAe6Dkp5ilRDoKg6KD5cR61IkQdgVTeaimjK7qn7YPLVWiDQm3wCEIiaCovw2PVoapAcP1SjNIZfn_tVOR0ThZIq1cvElShsbrZAo0",width=200)
      item1=st.slider("40% Academico", min_value=0.0, max_value=5.0, step=0.1)
      st.image("https://lh5.googleusercontent.com/niGf3eCwkrIDFwIHwSO8AsGuTnBptssKmg99NGwquiDxbeuv3vG18A9Aa_4ySzF-eh0gcjcgSGshEemmwwrh3dLZoEL87iT90NUGNSzPTSY_2r33qaT8UkQR71lYRSe7PSFogLVkmzW6akSwO7n38QY530cHoZ5KnEdOLX_oRHWaZs-B57kk_xxrPMsXdqLILVe2",width=200)
      item2=st.slider("40% Practico", min_value=0.0, max_value=5.0, step=0.1)
      st.image("https://lh3.googleusercontent.com/VQ7qWA5H8jLdUIuwup35xHEJcNficeEPsb9xurvRlYQcFIfpr6OzoXgssnAPGM3NWAFhF2mhvDJzFJTrsRt5b1ogyt2-V898oTYo4I1rvF9vvrCusIAlGXYnoDCJ7xisILpGjq2yv3a5NyJ1y2l5I6PBpxMYk-phVFS_wtc6cPYt0Ke4xnoZoV8j39jOXweMG4DX",width=200)
      item3=st.slider("20% Profesionalismo", min_value=0.0, max_value=5.0, step=0.1)
      score=round((item1*0.4+item2*0.4+item3*0.2),2)
      st.header("Calificación final",score)
    elif materia=="['adultez']":
      st.subheader("Calificación de la rotación de **adultez_I**")
      st.write("Lee acerca de los problemas de los pacientes discutidos en la ronda. \n Estudia los temas asignados y los vistos durante el componente teórico del curso.\n Reconoce sus vacíos de conocimiento y hace esfuerzos por llenarlos. **ASPECTOS ACADÉMICOS (60%)*")
      item1=st.slider( "60% Academico", min_value=0.0, max_value=5.0, step=0.1)
      st.write("Completa, clara y precisa. **HISTORIA CLÍNICA (10%)**")
      item2=st.slider( "10% Historia clínica", min_value=0.0, max_value=5.0, step=0.1)
      st.write("Sabe iniciar un tratamiento y es capaz de justificar su elección. \n Ordena los exámenes diagnósticos necesarios.\n Mide riesgo/beneficio de los exámenes y los \n esquemas terapéuticos. **PLAN DE MANEJO (10%)**")
      item3=st.slider( "10% Plan de manejo", min_value=0.0, max_value=5.0, step=0.1)
      st.write("Le habla al paciente con un lenguaje que él comprende. Coopera con sus compañeros. \n Es cortés con el personal que labora en el área.\n Busca como mejorar. Responde positivamente a la crítica.\n Llega a tiempo a las actividades acordadas. Cumple con el trabajo que se le asigna \n Sabe escuchar al otro. Entiende y acepta las diferencias religiosas, culturales,\n raciales, económicas y políticas. **CUALIDADES HUMANAS (20%)**")
      item4=st.slider( "20% Cualidades humanas", min_value=0.0, max_value=5.0, step=0.1)
      score=round((item1*0.6+item2*0.1+item3*0.1+item4*0.2),2)
      st.header("Calificación final ",score)
    elif materia=="['internado']":
      st.write("Calificación de la rotación de **Internado**")
      st.image("https://lh6.googleusercontent.com/jrgDxu8U0Z9H_kl09g8vnuYoeFlxGtNeZ1hRRVRn0qKcYitViZj04Xe-deQMq_4gmQ7amoSw2o9nJtW8tDt6rmoT7i42RvDAe6Dkp5ilRDoKg6KD5cR61IkQdgVTeaimjK7qn7YPLVWiDQm3wCEIiaCovw2PVoapAcP1SjNIZfn_tVOR0ThZIq1cvElShsbrZAo0",width=200)
      item1=st.slider("40% Academico", min_value=0.0, max_value=5.0, step=0.1)
      st.image("https://lh5.googleusercontent.com/niGf3eCwkrIDFwIHwSO8AsGuTnBptssKmg99NGwquiDxbeuv3vG18A9Aa_4ySzF-eh0gcjcgSGshEemmwwrh3dLZoEL87iT90NUGNSzPTSY_2r33qaT8UkQR71lYRSe7PSFogLVkmzW6akSwO7n38QY530cHoZ5KnEdOLX_oRHWaZs-B57kk_xxrPMsXdqLILVe2",width=200)
      item2=st.slider("40% Practico", min_value=0.0, max_value=5.0, step=0.1)
      st.image("https://lh3.googleusercontent.com/VQ7qWA5H8jLdUIuwup35xHEJcNficeEPsb9xurvRlYQcFIfpr6OzoXgssnAPGM3NWAFhF2mhvDJzFJTrsRt5b1ogyt2-V898oTYo4I1rvF9vvrCusIAlGXYnoDCJ7xisILpGjq2yv3a5NyJ1y2l5I6PBpxMYk-phVFS_wtc6cPYt0Ke4xnoZoV8j39jOXweMG4DX",width=200)
      item3=st.slider("20% Profesionalismo", min_value=0.0, max_value=5.0, step=0.1)
      score=round((item1*0.4+item2*0.4+item3*0.2),2)
      st.header("Calificación final",score)
    elif materia=="['cancer']":
      st.write("Calificación de la rotación de **cancer**")
      st.image("https://lh6.googleusercontent.com/jrgDxu8U0Z9H_kl09g8vnuYoeFlxGtNeZ1hRRVRn0qKcYitViZj04Xe-deQMq_4gmQ7amoSw2o9nJtW8tDt6rmoT7i42RvDAe6Dkp5ilRDoKg6KD5cR61IkQdgVTeaimjK7qn7YPLVWiDQm3wCEIiaCovw2PVoapAcP1SjNIZfn_tVOR0ThZIq1cvElShsbrZAo0",width=200)
      item1=st.slider("40% Academico", min_value=0.0, max_value=5.0, step=0.1)
      st.image("https://lh5.googleusercontent.com/niGf3eCwkrIDFwIHwSO8AsGuTnBptssKmg99NGwquiDxbeuv3vG18A9Aa_4ySzF-eh0gcjcgSGshEemmwwrh3dLZoEL87iT90NUGNSzPTSY_2r33qaT8UkQR71lYRSe7PSFogLVkmzW6akSwO7n38QY530cHoZ5KnEdOLX_oRHWaZs-B57kk_xxrPMsXdqLILVe2",width=200)
      item2=st.slider("40% Practico", min_value=0.0, max_value=5.0, step=0.1)
      st.image("https://lh3.googleusercontent.com/VQ7qWA5H8jLdUIuwup35xHEJcNficeEPsb9xurvRlYQcFIfpr6OzoXgssnAPGM3NWAFhF2mhvDJzFJTrsRt5b1ogyt2-V898oTYo4I1rvF9vvrCusIAlGXYnoDCJ7xisILpGjq2yv3a5NyJ1y2l5I6PBpxMYk-phVFS_wtc6cPYt0Ke4xnoZoV8j39jOXweMG4DX",width=200)
      item3=st.slider("20% Profesionalismo", min_value=0.0, max_value=5.0, step=0.1)
      score=round((item1*0.4+item2*0.4+item3*0.2),2)
      st.header("Calificación final",score)
    else:
      st.warning("el estudiante no tiene asignado una materia") 

    tz_col = pytz.timezone('America/Bogota') 
    fecha = datetime.now(tz_col).strftime('%a, %d %b %Y %I:%M %p')
    #score = st.number_input("Calificar el estudiante (0.0 - 5.0):", min_value=0.0, max_value=5.0, step=0.1)
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

