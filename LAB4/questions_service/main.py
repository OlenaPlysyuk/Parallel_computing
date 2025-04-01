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


@app.get("/questions", response_model=List[QuestionModel])
def get_questions():
    # Перевірка наявності кешованих даних
    cached_data = r.get(CACHE_KEY_ALL)
    if cached_data:
        # Якщо є — повертаємо дані з Redis (розпаковуємо з JSON)
        return json.loads(cached_data)

    # Якщо кеш порожній, беремо дані з "бази даних"
    data = [q.dict() for q in questions_db]
    # Записуємо дані у Redis із TTL (60 секунд)
    r.setex(CACHE_KEY_ALL, 60, json.dumps(data))
    return data


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

    # Інвалідація кешу, адже список запитань змінився
    r.delete(CACHE_KEY_ALL)
    return new_question


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
            # Інвалідуємо кеш, щоб наступні запити повернули оновлені дані
            r.delete(CACHE_KEY_ALL)
            return updated_question
    raise HTTPException(status_code=404, detail="Запитання не знайдено")


@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int):
    for idx, q in enumerate(questions_db):
        if q.id == question_id:
            questions_db.pop(idx)
            # Інвалідуємо кеш, адже дані змінилися
            r.delete(CACHE_KEY_ALL)
            return
    raise HTTPException(status_code=404, detail="Запитання не знайдено")
