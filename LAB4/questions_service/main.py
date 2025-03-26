from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Questions Service",
    description="Мікросервіс для управління запитаннями",
    version="1.0.0"
)

class QuestionModel(BaseModel):
    id: int
    test_id: int
    text: str
    answers: List[str]
    correct_answers: List[int]

questions_db: List[QuestionModel] = []
question_id_counter = 1

@app.get("/questions", response_model=List[QuestionModel])
def get_questions():
    return questions_db

@app.get("/questions/{question_id}", response_model=QuestionModel)
def get_question(question_id: int):
    for q in questions_db:
        if q.id == question_id:
            return q
    raise HTTPException(status_code=404, detail="Запитання не знайдено")

@app.post("/questions", response_model=QuestionModel, status_code=201)
def create_question(
    test_id: int = Query(...),
    text: str = Query(...),
    answers: str = Query(...),
    correct_answers: str = Query(...)
):
    global question_id_counter
    # Можна звернутися до "tests_service", щоб перевірити, чи існує тест.
    answers_list = answers.split(",")
    try:
        correct_list = [int(x) for x in correct_answers.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Некоректний формат correct_answers.")
    new_question = QuestionModel(
        id=question_id_counter,
        test_id=test_id,
        text=text,
        answers=answers_list,
        correct_answers=correct_list
    )
    questions_db.append(new_question)
    question_id_counter += 1
    return new_question

@app.put("/questions/{question_id}", response_model=QuestionModel)
def update_question(
    question_id: int,
    text: str = Query(...),
    answers: str = Query(...),
    correct_answers: str = Query(...)
):
    for idx, q in enumerate(questions_db):
        if q.id == question_id:
            answers_list = answers.split(",")
            try:
                correct_list = [int(x) for x in correct_answers.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Некоректний формат correct_answers.")
            updated_question = QuestionModel(
                id=question_id,
                test_id=q.test_id,
                text=text,
                answers=answers_list,
                correct_answers=correct_list
            )
            questions_db[idx] = updated_question
            return updated_question
    raise HTTPException(status_code=404, detail="Запитання не знайдено")

@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int):
    for idx, q in enumerate(questions_db):
        if q.id == question_id:
            questions_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Запитання не знайдено")



