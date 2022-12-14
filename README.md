# calificacion_udea_medicina

## Problema que pretende resolver: 
En el documental con Radicado: 2021‐064410 se evidencia desde 2021 acotando las nuevas necesidades que requiere Minsalud con los estudiantes Mediante el Acuerdo 00273 del 5 de octubre de 2021,  en el cual el Ministerio de Salud y Protección Social cambia el modelo de evaluación de calidad que se realizaba en los escenarios de prácticas formativas de educación superior en salud; sustituyendo así el Acuerdo 003 de 2003.
En el anexo técnico del acuerdo que adjunto numeral III opción a del plan de delegación progresiva de actividades, hay un ítem sobre actividades para promover el logro de los resultados de aprendizaje definidos para cada práctica formativa o rotación. Para las especialidades clínicas es muy importante evaluar el razonamiento clínico de los estudiantes de pregrado y posgrado sobre la construcción de las historias clínicas al momento de avalar las notas de ronda interconsulta o notas adicionales con un calificativo de 0.0 a 5.0, dado que la evaluación es subjetiva en este momento en un formato de hoja física que por protocolo debe llevar el sello del especialista(que ya no usamos por a firma electrónica).
Para los estudiantes de pregrado rotando en áreas quirúrgicas, el desempeño podría ser evaluado en las mismas notas de ronda quirúrgica de acuerdo a sus objetivos de rotación, con un calificativo de 0.0 a 5.0, para los estudiantes de posgrado quirúrgicos podría ser en las notas de Cirugía al momento de avalarlas.

Esta nota de seguimiento hace parte del conjunto de calificación de los estudiantes según el formato de calificación definido por el comité programa que se hace al final por cada docente



## Historia de Usuario

Como Personal asistencial- docente (Médico) quiero tener la posibilidad de calificar cada nota que avale de los estudiantes para disminuir la subjetividad de la calificación de la rotación y tener constancia de evaluación en el sistema para ser consultada posteriormente para los formatos de calificación definidos por cada universidad o por talento humano para obtener información objetiva de desempeño técnico al momento de contratar los profesionales que fueron estudiantes. Disminuir el impacto ambiental de la calificación con hojas impresas y digitalizar el proceso

Objetivo del desarrollo 
Crear una app de calificación con códigos QR que permita consumir una API de Ghips (API aun sin desarrollo) que obtenga los datos de calificación guardados en la base de datos de ghips de los estudiantes en un periodo determinado de tiempo que permita de forma externa al ghips modificarse según los parámetros de evaluación de cada rotación que permita la posibilidad de extender el desarrollo a otras areas de forma futura.





## Códigos y versión preliminar de app.

En el momento se hará una prueba piloto para evaluar UX (experiencia de usuario) con una cohorte de estudiantes de VIII semestre con una app desplegada en la nube pública, la autenticación es con ghips, pero por medio de la API devuelve si fue correcta la autenticación no guarda contraseñas por lo que no compromete la seguridad.
