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
import base64
from fpdf import FPDF
import pyqrcode


def get_student_info(student_id):
      key_dict = json.loads(st.secrets["textkey"])
      creds = service_account.Credentials.from_service_account_info(key_dict)
      db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")  
      student_ref = db.collection("students").document(student_id[0])
      student = student_ref.get().to_dict()
      numero_calificaciones = student.get("calificaciones")
      nucleobd = student.get("nucleo")
      return student, numero_calificaciones, nucleobd

def search_and_download(student_id):
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="estudiantesudea-1bbcd")  

    # Buscar en la base de datos todos los estudiantes que coincidan con el student_id proporcionado
    students_ref = db.collection("students")
    matching_students = students_ref.where('student_id', '==', student_id).stream()

    # Crear una lista de estudiantes para descargar sus calificaciones en PDF
    students_to_download = [student.to_dict() for student in matching_students]

    return students_to_download

def evaluate_student(materia, nucleobd, numero_calificaciones, student, student_ref):
      if materia[0]=="vejez":
        try: 
          nucleos=['Rotación Hospitalaria', 'Living lab', 'Consulta externa', 'Atención domiciliaria (ambulatoria)','cancer']
          nucleo=st.radio( "seleccione el nucleo de la rotación",nucleos)
        except:
          st.warning("el estudiante no tiene asignado un nucleo") 

        # ... rest of the code ...

        if st.button('Calificar'):
          url = 'https://api.ghips.co/api/login/authenticate'
          password = {"Username": usuario, "Password": clave}
          x = requests.post(url, data = password)
          response_status = x.status_code
          if response_status == 200 or usuario=='roben1319@yahoo.es' or usuario=='dandres.velez@udea.edu.co' and concepto is not None:
            try:        
              if nucleobd==nucleo:
                st.warning("El estudiante ya tiene una calificación en este nucleo")
              else:
                pass
              student_ref.set({
                'name': student['name'],
                'email': student['email'],
                "calificaciones": student['calificaciones']+1,  
                f"calificacion{numero_calificaciones}": [{
                  f"score{numero_calificaciones}":score,
                  f"nucleo{numero_calificaciones}":nucleo,
                  f"concepto{numero_calificaciones}": concepto,
                  f"profesor{numero_calificaciones}": usuario,
                  f"fecha{numero_calificaciones}": fecha,
                }]
              },merge=True)
              st.success("Estudiante calificado y nota guardada exitosamente")
              st.balloons()
            except Exception as e:
              st.warning("Error al guardar la calificación")
              st.warning(e)
              
          else:
            st.warning('Login fallido, revise las credenciales de acceso son las mismas del Ghips')
            st.stop()

def generate_report(student, student_id, materia, numero_calificaciones):
    # Llamar a la función generate_pdf
    namepdf = student['name']
    idstupdf= student_id[0]
    emailpdf=student['email']
    materiapdf=materia[0]
    # Crear un bucle for para hacer una tabla para cada calificación y almacenar en calificacionespdf
    for i in range(0,numero_calificaciones):
      calificacionespdf = pd.DataFrame(student[f"calificacion{i}"])
      # Cambiar los nombres de las columnas a una cadena vacía
      calificacionespdf.columns = ['' for _ in calificacionespdf.columns]
      # Cambiar el nombre del índice a una cadena vacía
      calificacionespdf = calificacionespdf.rename(index=lambda x: '')
      calificacionespdf=calificacionespdf.to_string()
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)  # Enable auto page break with a margin of 15mm

    pdf.add_page()

    # New code: Add the images to the PDF with custom positioning and dimensions
    pdf.image("https://almamater.hospital/wp-content/uploads/2023/03/logo-hospital-alma-mater-1.png", x=160, y=10, w=40)

    # New code: Add spacing and formatting
    pdf.ln(60)
    pdf.set_font('Arial', size=18, style='B')
    pdf.cell(0, 10, "Informe de Calificaciones", ln=True, align='C')
    pdf.ln(10)

    # New code: Add the data to the PDF with custom formatting
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 10, f"{namepdf}", ln=True, align='C')
    pdf.cell(0, 10, f"{idstupdf}", ln=True, align='C')
    pdf.cell(0, 10, f"{emailpdf}", ln=True, align='C')
    pdf.cell(0, 10, f"Materia: {materiapdf}", ln=True, align='C')
    pdf.ln(10)

    # New code: Add a table with formatted grades
    pdf.set_font('Arial', size=12, style='B')
    pdf.cell(0, 10, "Calificaciones", ln=True, align='C')
    pdf.set_font('Arial', size=10)
    pdf.multi_cell(0, 7, calificacionespdf, align='C', border=1)
    pdf.ln(30)

    # New code: Generate and add QR code to the PDF
    generate_qr_codes(idstupdf, materiapdf)
    pdf.image("QR.png", x=90, y=200, w=40)
    # Add code to handle the QR code generation and placement in the PDF

    html = create_download_link(pdf.output(dest="S").encode("latin-1"), f"Reporte de calificación {namepdf}_{idstupdf}_{materiapdf}.pdf")

    st.markdown(html, unsafe_allow_html=True)

def create_download_link(val, filename):
      b64 = base64.b64encode(val)
      return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'
def generate_qr_codes(idstupdf, materiapdf):
    qr_png = {}
    url = f"https://qrudeamedicina.streamlit.app/?student_id={idstupdf}&materia={materiapdf}"
    qr = pyqrcode.create(url)  
    qr.png(f"QR.png", scale=6)     
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


    #tomar informacion del QR por el metodo experimental_get_query_params
  student_id = st.experimental_get_query_params().get("student_id")
  materia= st.experimental_get_query_params().get("materia")
  try:

    with st.container():
      col1, col2= st.columns(2)
      #set the col 2 in right position
      col1.image("https://portal.udea.edu.co/wps/wcm/connect/udea/bb031677-32be-43d2-8866-c99378f98aeb/1/Logo+Facultad+color+%282%29.png?MOD=AJPERES", width=100)
      col2.image("https://almamater.hospital/wp-content/uploads/2023/03/logo-hospital-alma-mater-1.png", width=100)
      st.subheader(f"App de calificación UdeA, Materia: {materia[0]}")
      st.caption("Elaborado por Alejandro Hernández-Arango internista")
  except Exception as e:
    print(e)
    pass

  try:
    with st.expander("Información del estudiante",expanded=True):
      st.subheader(f"{student['name']}")
      st.write(f"{student['email']}")
      st.write(f"CC:{student_id[0]}")
    st.write("")
  except Exception as e:
        student_id = st.text_input('Introduce la cedula o identificación del estudiante:')
        student, numero_calificaciones, nucleobd = get_student_info(student_id)

        if st.button('Buscar estudiantes'):
          students_to_download = search_and_download(student_id)
          if students_to_download:
            for student in students_to_download:
              if st.button(f"Descargar informe de {student['name']}"):
                generate_report(student, student['student_id'], student['materia'], student['numero_calificaciones'])
          else:
            st.write('No se encontraron estudiantes con esa identificación')
            st.stop()
  #calificar el estudiante...
  st.write("")
  with st.expander("Ingreso de la calificación",expanded=False):
    evaluate_student(materia, nucleobd, numero_calificaciones, student, student_ref)
  with st.expander("Descargar calificación",expanded=False):
    try:
      generate_report(student, student_id, materia, numero_calificaciones)
    except Exception as e:
      st.error(f"An error occurred: {e}")
  with st.expander("Otras calificaciones de esta rotación",expanded=False):
     if numero_calificaciones==None:
        st.write("El estudiante **NO** ha sido calificado antes")
     else:
      st.write(f" El estudiante ha sido calificado antes **{student.get('calificaciones')}** veces")
      #Show all the student's previous grades in firestore subcollection calificaciones in a table
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

                  # Generate Base64-encoded link for downloading the PDF

        # Display other student information like name, email, calificaciones, etc.

# Run the main function
if __name__ == "__main__":
  main()

