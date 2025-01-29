import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import requests
import pyqrcode
import os
from io import BytesIO
from zipfile import ZipFile
from fastapi.responses import StreamingResponse

app = FastAPI()

MOODLE_API_URL = os.getenv("MOODLE_API_URL")
MOODLE_TOKEN   = os.getenv("MOODLE_TOKEN")

class GradeRequest(BaseModel):
    student_id: int
    course_id: int
    grade: float

@app.get("/")
def index():
    return {"message": "Python backend for Moodle services up and running."}

@app.post("/moodle/enroll")
async def enroll_students_in_moodle(
    studentsFile: UploadFile = File(...),
    course_id: str = Form(...),
    role_id: str = Form(...),
    generate_qr: str = Form(None)
):
    """
    1) Parse the uploaded Excel
    2) Check or create Moodle user
    3) Enroll each student
    4) [Optional] Generate QRs and return them in a ZIP
    """
    # 1) Read the Excel file into a DataFrame
    df = pd.read_excel(studentsFile.file)
    
    # This list will store any info to return
    results = []

    # 2) For each row, attempt to create or find user, then enroll in course
    for index, row in df.iterrows():
        email = row['email']
        first_name = row['name'].split()[0] if len(row['name'].split()) > 0 else row['name']
        last_name  = ' '.join(row['name'].split()[1:]) if len(row['name'].split()) > 1 else "NoLastName"
        idnumber   = str(row['id'])

        # Check if user exists by email
        user_id = find_moodle_user_by_email(email)
        if not user_id:
            # Create user
            user_id = create_moodle_user(email, first_name, last_name, idnumber)
        
        if not user_id:
            results.append({"email": email, "status": "failed to create/find user"})
            continue

        # Enroll user
        success = enroll_user_in_course(user_id, course_id, role_id)
        if success:
            results.append({"email": email, "status": "enrolled", "userid": user_id})
        else:
            results.append({"email": email, "status": "failed to enroll"})

    # 3) If generate_qr is "true", build a zip with all QRs
    if generate_qr == "true":
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "a") as zf:
            # generate a QR for each student in the df
            for index, row in df.iterrows():
                # For demonstration, let's assume the link is a simple GET param
                student_url = f"http://localhost:8000/?student_id={int(row['id'])}"
                qr = pyqrcode.create(student_url)
                # create PNG in memory
                png_io = BytesIO()
                qr.png(png_io, scale=6)
                # add to zip
                zf.writestr(f"{row['name']}_{row['id']}.png", png_io.getvalue())

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": "attachment;filename=qr_codes.zip"
            }
        )

    # 4) Otherwise, just return JSON of results
    return JSONResponse(content={"results": results})


@app.post("/moodle/grade")
def grade_student_in_moodle(req: GradeRequest):
    """
    Update student's grade in Moodle
    """
    updated = update_grade_in_moodle(req.student_id, req.course_id, req.grade)
    if updated:
        return {"status": "ok", "detail": "Grade updated"}
    else:
        return {"status": "error", "detail": "Failed to update grade"}


### Moodle Utility Functions ###

def find_moodle_user_by_email(email: str):
    """
    Use Moodle function: core_user_get_users
    with criteria= email
    """
    function_name = "core_user_get_users"
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "criteria[0][key]": "email",
        "criteria[0][value]": email
    }
    r = requests.post(MOODLE_API_URL, data=params)
    data = r.json()
    if "users" in data and len(data["users"]) > 0:
        return data["users"][0]["id"]
    return None

def create_moodle_user(email, firstname, lastname, idnumber):
    """
    Use Moodle function: core_user_create_users
    """
    function_name = "core_user_create_users"
    password = "DefaultPass123!"
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "users[0][username]": email,
        "users[0][email]": email,
        "users[0][firstname]": firstname,
        "users[0][lastname]": lastname,
        "users[0][idnumber]": idnumber,
        "users[0][password]": password,
        "users[0][auth]": "manual"
    }
    r = requests.post(MOODLE_API_URL, data=params)
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]["id"]  # created user ID
    return None

def enroll_user_in_course(userid, courseid, roleid):
    """
    Use Moodle function: enrol_manual_enrol_users
    """
    function_name = "enrol_manual_enrol_users"
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "enrolments[0][roleid]": roleid,
        "enrolments[0][userid]": userid,
        "enrolments[0][courseid]": courseid
    }
    r = requests.post(MOODLE_API_URL, data=params)
    # If no exception, it usually means success
    if r.status_code == 200:
        # If Moodle returns empty JSON or success, good
        # For actual error-check, parse r.json()
        return True
    return False

def update_grade_in_moodle(student_id, course_id, grade):
    """
    Use Moodle function: core_grades_update_grades
    The specific parameters depend on your Moodle setup (component, itemnumber, etc.)
    """
    function_name = "core_grades_update_grades"
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "source": "custom_api",
        "courseid": course_id,
        "component": "mod_assign",     # or mod_quiz, etc. depends on your Moodle item
        "activityid": 1234,           # the assignment or quiz ID in Moodle
        "itemnumber": 0,
        "grades[0][studentid]": student_id,
        "grades[0][grade]": grade,
        "grades[0][str_feedback]": "Via custom API"
    }
    r = requests.post(MOODLE_API_URL, data=params)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict) and data.get("exception"):
            # Moodle returned an error
            return False
        return True
    return False

@app.get("/moodle/courses")
def get_all_courses_endpoint():
    """
    Retrieve all courses from Moodle platform
    Returns list of courses with ID and name
    """
    courses = get_all_courses()
    if courses is None:
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to fetch courses from Moodle"}
        )
    
    # Simplify response to only include ID and name
    simplified_courses = [
        {"course_id": course["id"], "course_name": course["fullname"]}
        for course in courses
        if course.get("id") and course.get("fullname")  # Ensure fields exist
    ]
    return {"courses": simplified_courses}

### Moodle Utility Functions ###

def get_all_courses():
    """
    Use Moodle function: core_course_get_courses
    Returns list of all courses in Moodle
    """
    function_name = "core_course_get_courses"
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": function_name,
        "moodlewsrestformat": "json"
    }
    
    try:
        r = requests.post(MOODLE_API_URL, data=params)
        data = r.json()
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and data.get("exception"):
            print(f"Moodle API error: {data}")
            return None
    except Exception as e:
        print(f"Error fetching courses: {str(e)}")
        return None
    return None



if __name__ == "__main__":
    # Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
