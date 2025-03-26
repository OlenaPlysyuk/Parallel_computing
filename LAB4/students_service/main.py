from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Students Service",
    description="Мікросервіс для управління студентами",
    version="1.0.0"
)

class StudentModel(BaseModel):
    id: int
    name: str

students_db: List[StudentModel] = []
student_id_counter = 1

@app.get("/students", response_model=List[StudentModel])
def get_students():
    return students_db

@app.get("/students/{student_id}", response_model=StudentModel)
def get_student(student_id: int):
    for st in students_db:
        if st.id == student_id:
            return st
    raise HTTPException(status_code=404, detail="Студента не знайдено")

@app.post("/students", response_model=StudentModel, status_code=201)
def create_student(name: str = Query(...)):
    global student_id_counter
    new_st = StudentModel(id=student_id_counter, name=name)
    students_db.append(new_st)
    student_id_counter += 1
    return new_st

@app.put("/students/{student_id}", response_model=StudentModel)
def update_student(student_id: int, name: str = Query(...)):
    for idx, st in enumerate(students_db):
        if st.id == student_id:
            updated_st = StudentModel(id=student_id, name=name)
            students_db[idx] = updated_st
            return updated_st
    raise HTTPException(status_code=404, detail="Студента не знайдено")

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    for idx, st in enumerate(students_db):
        if st.id == student_id:
            students_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Студента не знайдено")
