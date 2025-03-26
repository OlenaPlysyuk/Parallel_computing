import requests
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Answers Service",
    description="Мікросервіс для перевірки відповідей на запитання",
    version="1.0.0"
)

@app.post("/questions/{question_id}/answer")
def answer_question(
    question_id: int,
    student_id: int = Query(..., description="ID студента"),
    chosen_answers: str = Query(..., description="Індекси вибраних відповідей, через кому")
):
    # Перевірка існування студента (звертаємося до students_service)
    student_url = f"http://students_service:8004/students/{student_id}"
    student_response = requests.get(student_url)
    if student_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Студента з таким ID не існує")

    # Отримання даних запитання (з questions_service)
    question_url = f"http://questions_service:8003/questions/{question_id}"
    question_response = requests.get(question_url)
    if question_response.status_code != 200:
        raise HTTPException(status_code=404, detail="Запитання не знайдено")
    question = question_response.json()

    # Парсинг вибраних відповідей
    try:
        chosen_list = [int(x) for x in chosen_answers.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Некоректний формат chosen_answers.")

    correct_answers = question.get("correct_answers")
    if correct_answers is None:
        raise HTTPException(status_code=500, detail="Помилка у даних запитання")

    is_correct = set(chosen_list) == set(correct_answers)
    return {
        "question_id": question_id,
        "student_id": student_id,
        "chosen_answers": chosen_list,
        "correct_answers": correct_answers,
        "result": "correct" if is_correct else "wrong"
    }
