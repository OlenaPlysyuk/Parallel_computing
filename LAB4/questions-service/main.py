import json
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Questions Service",
    description="Мікросервіс для управління запитаннями з кешуванням у Redis",
    version="1.0.0"
)

# Модель запитання
class QuestionModel(BaseModel):
    id: int
    test_id: int
    text: str
    answers: List[str]
    correct_answers: List[int]

# "База даних" у пам'яті — список запитань
questions_db: List[QuestionModel] = []
question_id_counter = 1

# Підключення до Redis (ім'я хоста 'redis' відповідає сервісу Redis у docker-compose)
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Ключ для кешу всього списку запитань
CACHE_KEY_ALL = "questions:all"

# Ендпоїнт для отримання всього списку запитань з кешуванням у Redis
@app.get("/questions", response_model=List[QuestionModel])
def get_questions():
    cached_data = r.get(CACHE_KEY_ALL)
    if cached_data:
        return json.loads(cached_data)
    data = [q.dict() for q in questions_db]
    r.setex(CACHE_KEY_ALL, 60, json.dumps(data))
    return data

# Новий ендпоїнт для отримання конкретного запитання за ID (без кешування)
@app.get("/questions/{question_id}", response_model=QuestionModel)
def get_question_by_id(question_id: int):
    for q in questions_db:
        if q.id == question_id:
            return q
    raise HTTPException(status_code=404, detail="Запитання не знайдено")

# Створення нового запитання
@app.post("/questions", response_model=QuestionModel, status_code=201)
def create_question(test_id: int, text: str, answers: str, correct_answers: str):
    global question_id_counter
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
    r.delete(CACHE_KEY_ALL)  # Інвалідуємо кеш списку
    return new_question

# Оновлення існуючого запитання
@app.put("/questions/{question_id}", response_model=QuestionModel)
def update_question(question_id: int, text: str, answers: str, correct_answers: str):
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
            r.delete(CACHE_KEY_ALL)  # Інвалідуємо кеш, адже дані змінилися
            return updated_question
    raise HTTPException(status_code=404, detail="Запитання не знайдено")

# Видалення запитання
@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int):
    for idx, q in enumerate(questions_db):
        if q.id == question_id:
            questions_db.pop(idx)
            r.delete(CACHE_KEY_ALL)
            return
    raise HTTPException(status_code=404, detail="Запитання не знайдено")
