from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Subjects Service",
    description="Мікросервіс для управління предметами",
    version="1.0.0"
)

class SubjectModel(BaseModel):
    id: int
    name: str

subjects_db: List[SubjectModel] = []
subject_id_counter = 1

@app.get("/subjects", response_model=List[SubjectModel])
def get_subjects():
    return subjects_db

@app.get("/subjects/{subject_id}", response_model=SubjectModel)
def get_subject(subject_id: int):
    for subj in subjects_db:
        if subj.id == subject_id:
            return subj
    raise HTTPException(status_code=404, detail="Предмет не знайдено")

@app.post("/subjects", response_model=SubjectModel, status_code=201)
def create_subject(name: str = Query(..., description="Назва предмета")):
    global subject_id_counter
    new_subject = SubjectModel(id=subject_id_counter, name=name)
    subjects_db.append(new_subject)
    subject_id_counter += 1
    return new_subject

@app.put("/subjects/{subject_id}", response_model=SubjectModel)
def update_subject(subject_id: int, name: str = Query(..., description="Нова назва предмета")):
    for idx, subj in enumerate(subjects_db):
        if subj.id == subject_id:
            updated_subject = SubjectModel(id=subject_id, name=name)
            subjects_db[idx] = updated_subject
            return updated_subject
    raise HTTPException(status_code=404, detail="Предмет не знайдено")

@app.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int):
    for idx, subj in enumerate(subjects_db):
        if subj.id == subject_id:
            subjects_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Предмет не знайдено")
