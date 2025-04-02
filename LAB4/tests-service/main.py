from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Tests Service",
    description="Мікросервіс для управління тестами",
    version="1.0.0"
)

class TestModel(BaseModel):
    id: int
    subject_id: int
    name: str

tests_db: List[TestModel] = []
test_id_counter = 1

@app.get("/tests", response_model=List[TestModel])
def get_tests():
    return tests_db

@app.get("/tests/{test_id}", response_model=TestModel)
def get_test(test_id: int):
    for t in tests_db:
        if t.id == test_id:
            return t
    raise HTTPException(status_code=404, detail="Тест не знайдено")

@app.post("/tests", response_model=TestModel, status_code=201)
def create_test(subject_id: int = Query(...), name: str = Query(...)):
    global test_id_counter
    # Тут можна (опціонально) звертатися до мікросервісу "subjects" через HTTP,
    # щоб перевірити, чи існує предмет із таким subject_id.
    new_test = TestModel(id=test_id_counter, subject_id=subject_id, name=name)
    tests_db.append(new_test)
    test_id_counter += 1
    return new_test

@app.put("/tests/{test_id}", response_model=TestModel)
def update_test(test_id: int, subject_id: int = Query(...), name: str = Query(...)):
    for idx, t in enumerate(tests_db):
        if t.id == test_id:
            updated_test = TestModel(id=test_id, subject_id=subject_id, name=name)
            tests_db[idx] = updated_test
            return updated_test
    raise HTTPException(status_code=404, detail="Тест не знайдено")

@app.delete("/tests/{test_id}", status_code=204)
def delete_test(test_id: int):
    for idx, t in enumerate(tests_db):
        if t.id == test_id:
            tests_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Тест не знайдено")
