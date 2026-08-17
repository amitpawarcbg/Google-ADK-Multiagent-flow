import uuid
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="Student Registration Web App",
    description="Simple Python Student Registration application for CI/CD Cloud Run deployment demonstration.",
    version="4.7.0"
)

# In-memory student storage
db: Dict[str, Dict[str, str]] = {}

class StudentCreate(BaseModel):
    name: str
    email: str
    course: str
    city: str
    gender: str
    country: str
    roll_no: str
    pincode: str
    landmark: str
    contact_no: str

class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    course: str
    city: str
    gender: str
    country: str
    roll_no: str
    pincode: str
    landmark: str
    contact_no: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "student-registration-app"}

@app.post("/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def register_student(student: StudentCreate):
    student_id = str(uuid.uuid4())[:8]
    record = {
        "id": student_id,
        "name": student.name,
        "email": student.email,
        "course": student.course,
        "city": student.city,
        "gender": student.gender,
        "country": student.country,
        "roll_no": student.roll_no,
        "pincode": student.pincode,
        "landmark": student.landmark,
        "contact_no": student.contact_no
    }
    db[student_id] = record
    return record

@app.get("/students", response_model=List[StudentResponse])
def list_students():
    return list(db.values())

@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: str):
    if student_id not in db:
        raise HTTPException(status_code=404, detail="Student not found")
    return db[student_id]

@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    if student_id not in db:
        raise HTTPException(status_code=404, detail="Student not found")
    deleted = db.pop(student_id)
    return {"message": f"Student {deleted['name']} removed successfully"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cybage DevOps - Student Registration Portal</title>
        <style>
            :root {
                --primary: #1d4ed8;
                --primary-hover: #1e40af;
                --bg: #eff6ff;
                --card-bg: #ffffff;
                --text: #1e3a5f;
                --text-muted: #1e40af;
                --accent: #1d4ed8;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 40px 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .container {
                max-width: 600px;
                width: 100%;
                background: var(--card-bg);
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(180,83,9,0.15);
                border: 1px solid #fde68a;
            }
            h1 { color: var(--accent); font-size: 1.8rem; margin-top: 0; }
            p { color: var(--text-muted); }
            label { display: block; margin: 12px 0 6px; font-weight: 600; color: #78350f; }
            input, select {
                width: 100%;
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #fcd34d;
                background: #fffbeb;
                color: #451a03;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                margin-top: 20px;
                padding: 12px;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 1rem;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover { background: var(--primary-hover); }
            .student-list { margin-top: 30px; }
            .student-item {
                background: #fffbeb;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-left: 4px solid var(--accent);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Student Registration Portal</h1>
            <p>Cybage DevOps Multi-Agent Cloud Run Demo</p>
            <form id="regForm">
                <label for="roll_no">Roll Number</label>
                <input type="text" id="roll_no" required placeholder="ROLL-101">

                <label for="name">Full Name</label>
                <input type="text" id="name" required placeholder="John Doe">

                <label for="email">Email Address</label>
                <input type="email" id="email" required placeholder="john@example.com">

                <label for="contact_no">Contact Number</label>
                <input type="text" id="contact_no" required placeholder="+1 555-0199 / +91 9876543210">

                <label for="gender">Gender</label>
                <select id="gender">
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                    <option value="Non-Binary / Other">Non-Binary / Other</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                </select>

                <label for="city">City</label>
                <input type="text" id="city" required placeholder="Pune / San Francisco">

                <label for="country">Country</label>
                <input type="text" id="country" required placeholder="India / USA">

                <label for="pincode">Pin Code</label>
                <input type="text" id="pincode" required placeholder="411014 / 94105">

                <label for="landmark">Landmark</label>
                <input type="text" id="landmark" required placeholder="Near IT Park / Central Mall">

                <label for="course">Course</label>
                <select id="course">
                    <option value="Cloud Native Architecture">Cloud Native Architecture</option>
                    <option value="Multi-Agent Systems & GenAI">Multi-Agent Systems & GenAI</option>
                    <option value="DevOps & GitOps Masterclass">DevOps & GitOps Masterclass</option>
                </select>

                <button type="submit">Register Student</button>
            </form>

            <div class="student-list">
                <h3>Registered Students</h3>
                <div id="list">Loading...</div>
            </div>
        </div>

        <script>
            async function fetchStudents() {
                const res = await fetch('/students');
                const data = await res.json();
                const listEl = document.getElementById('list');
                if(data.length === 0) {
                    listEl.innerHTML = '<p style="color: #78350f;">No students registered yet.</p>';
                    return;
                }
                listEl.innerHTML = data.map(s => `
                    <div class="student-item">
                        <div>
                            <strong>${s.name}</strong> (${s.course})<br>
                            <small style="color:#78350f;">Roll No: ${s.roll_no} | Phone: ${s.contact_no} | Gender: ${s.gender} | City: ${s.city}, ${s.country} | Landmark: ${s.landmark} | Pin: ${s.pincode} | Email: ${s.email} | ID: ${s.id}</small>
                        </div>
                    </div>
                `).join('');
            }

            document.getElementById('regForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const roll_no = document.getElementById('roll_no').value;
                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const contact_no = document.getElementById('contact_no').value;
                const gender = document.getElementById('gender').value;
                const city = document.getElementById('city').value;
                const country = document.getElementById('country').value;
                const pincode = document.getElementById('pincode').value;
                const landmark = document.getElementById('landmark').value;
                const course = document.getElementById('course').value;
                
                await fetch('/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({roll_no, name, email, contact_no, gender, city, country, pincode, landmark, course})
                });
                e.target.reset();
                fetchStudents();
            });

            fetchStudents();
        </script>
    </body>
    </html>
    """
