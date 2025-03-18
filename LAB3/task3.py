from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Система Тестування",
    description=(
        "Викладач створює Тести з кількома Запитаннями закритого типу "
        "(одна/кілька правильних відповідей з N варіантів) у межах Предмету. "
        "Студент переглядає список Тестів, відповідає на Запитання."
    ),
    version="1.0.0"
)



# Pydantic-моделі для вихідних даних (response_model).
class SubjectModel(BaseModel):
    id: int
    name: str


class TestModel(BaseModel):
    id: int
    subject_id: int
    name: str


class QuestionModel(BaseModel):
    id: int
    test_id: int
    text: str
    # Варіанти відповідей (список текстових рядків)
    answers: List[str]
    # Індекси правильних відповідей (може бути один або кілька)
    correct_answers: List[int]


class StudentModel(BaseModel):
    id: int
    name: str



# "База даних" у пам'яті
subjects_db: List[SubjectModel] = []
tests_db: List[TestModel] = []
questions_db: List[QuestionModel] = []
students_db: List[StudentModel] = []

subject_id_counter = 1
test_id_counter = 1
question_id_counter = 1
student_id_counter = 1



#                           П Р Е Д М Е Т И
@app.get("/subjects", response_model=List[SubjectModel])
def get_subjects():
    """Повертає список усіх предметів."""
    return subjects_db


@app.get("/subjects/{subject_id}", response_model=SubjectModel)
def get_subject(subject_id: int):
    """Повертає предмет за ID."""
    for subj in subjects_db:
        if subj.id == subject_id:
            return subj
    raise HTTPException(status_code=404, detail="Предмет не знайдено")


@app.post("/subjects", response_model=SubjectModel, status_code=201)
def create_subject(name: str = Query(..., description="Назва предмета")):
    """
    Створити новий предмет.

    Приклад виклику:
      POST /subjects?name=Математика
    """
    global subject_id_counter
    new_subject = SubjectModel(id=subject_id_counter, name=name)
    subjects_db.append(new_subject)
    subject_id_counter += 1
    return new_subject


@app.put("/subjects/{subject_id}", response_model=SubjectModel)
def update_subject(subject_id: int, name: str = Query(..., description="Нова назва предмета")):
    """Оновити назву предмета за ID."""
    for idx, subj in enumerate(subjects_db):
        if subj.id == subject_id:
            updated_subject = SubjectModel(id=subject_id, name=name)
            subjects_db[idx] = updated_subject
            return updated_subject
    raise HTTPException(status_code=404, detail="Предмет не знайдено")


@app.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int):
    """Видалити предмет за ID."""
    for idx, subj in enumerate(subjects_db):
        if subj.id == subject_id:
            subjects_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Предмет не знайдено")



#                                Т Е С Т И
@app.get("/tests", response_model=List[TestModel])
def get_tests():
    """Повертає список усіх тестів."""
    return tests_db


@app.get("/tests/{test_id}", response_model=TestModel)
def get_test(test_id: int):
    """Повертає тест за ID."""
    for t in tests_db:
        if t.id == test_id:
            return t
    raise HTTPException(status_code=404, detail="Тест не знайдено")


@app.post("/tests", response_model=TestModel, status_code=201)
def create_test(
        subject_id: int = Query(..., description="ID предмета"),
        name: str = Query(..., description="Назва тесту")
):
    """
    Створити новий тест для певного предмета.

    Приклад:
      POST /tests?subject_id=1&name=Контрольна%20робота
    """
    global test_id_counter
    # Перевірка, чи існує предмет
    subj_exists = any(s.id == subject_id for s in subjects_db)
    if not subj_exists:
        raise HTTPException(status_code=400, detail="Предмет із таким ID не існує")

    new_test = TestModel(id=test_id_counter, subject_id=subject_id, name=name)
    tests_db.append(new_test)
    test_id_counter += 1
    return new_test


@app.put("/tests/{test_id}", response_model=TestModel)
def update_test(
        test_id: int,
        subject_id: int = Query(..., description="Новий ID предмета"),
        name: str = Query(..., description="Нова назва тесту")
):
    """Оновити тест (ID предмета, назву)."""
    for idx, t in enumerate(tests_db):
        if t.id == test_id:
            # Перевірка, чи існує предмет
            subj_exists = any(s.id == subject_id for s in subjects_db)
            if not subj_exists:
                raise HTTPException(status_code=400, detail="Предмет із таким ID не існує")

            updated_test = TestModel(id=test_id, subject_id=subject_id, name=name)
            tests_db[idx] = updated_test
            return updated_test
    raise HTTPException(status_code=404, detail="Тест не знайдено")


@app.delete("/tests/{test_id}", status_code=204)
def delete_test(test_id: int):
    """Видалити тест за ID."""
    for idx, t in enumerate(tests_db):
        if t.id == test_id:
            tests_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Тест не знайдено")


# ----------------------------------------------------------------------------------
#                            З А П И Т А Н Н Я
# ----------------------------------------------------------------------------------
@app.get("/questions", response_model=List[QuestionModel])
def get_questions():
    """Повертає список усіх запитань."""
    return questions_db


@app.get("/questions/{question_id}", response_model=QuestionModel)
def get_question(question_id: int):
    """Повертає запитання за ID."""
    for q in questions_db:
        if q.id == question_id:
            return q
    raise HTTPException(status_code=404, detail="Запитання не знайдено")


@app.post("/questions", response_model=QuestionModel, status_code=201)
def create_question(
        test_id: int = Query(..., description="ID тесту"),
        text: str = Query(..., description="Текст запитання"),
        answers: str = Query(..., description="Варіанти відповідей, через кому (наприклад: 'Київ,Львів,Одеса')"),
        correct_answers: str = Query(..., description="Індекси правильних відповідей, через кому (наприклад: '0,2')")
):
    """
    Створити нове запитання закритого типу для певного тесту.
    - `answers` передається одним рядком, розділеним комами.
    - `correct_answers` також передається комами (може бути один або кілька індексів).

    Приклад:
      POST /questions?test_id=1&text=2+2%3D%3F&answers=4,5,22&correct_answers=0
    """
    global question_id_counter
    # Перевірка, чи існує тест
    test_exists = any(t.id == test_id for t in tests_db)
    if not test_exists:
        raise HTTPException(status_code=400, detail="Тест із таким ID не існує")

    answers_list = answers.split(",")  # Розділяємо варіанти відповіді
    # Розділяємо індекси правильних відповідей і перетворюємо в int
    try:
        correct_list = [int(x) for x in correct_answers.split(",")]
    except ValueError:
        raise HTTPException(status_code=400,
                            detail="Некоректний формат correct_answers (очікується комами розділені числа).")

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
        text: str = Query(..., description="Новий текст запитання"),
        answers: str = Query(..., description="Нові варіанти відповіді (через кому)"),
        correct_answers: str = Query(..., description="Нові індекси правильних відповідей (через кому)")
):
    """Оновити запитання (текст, варіанти, правильні відповіді) за ID."""
    for idx, q in enumerate(questions_db):
        if q.id == question_id:
            answers_list = answers.split(",")
            try:
                correct_list = [int(x) for x in correct_answers.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Некоректний формат correct_answers.")

            updated_question = QuestionModel(
                id=question_id,
                test_id=q.test_id,  # test_id не змінюємо
                text=text,
                answers=answers_list,
                correct_answers=correct_list
            )
            questions_db[idx] = updated_question
            return updated_question
    raise HTTPException(status_code=404, detail="Запитання не знайдено")


@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int):
    """Видалити запитання за ID."""
    for idx, q in enumerate(questions_db):
        if q.id == question_id:
            questions_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Запитання не знайдено")


# ----------------------------------------------------------------------------------
#                             С Т У Д Е Н Т И
# ----------------------------------------------------------------------------------
@app.get("/students", response_model=List[StudentModel])
def get_students():
    """Повертає список усіх студентів."""
    return students_db


@app.get("/students/{student_id}", response_model=StudentModel)
def get_student(student_id: int):
    """Повертає студента за ID."""
    for st in students_db:
        if st.id == student_id:
            return st
    raise HTTPException(status_code=404, detail="Студента не знайдено")


@app.post("/students", response_model=StudentModel, status_code=201)
def create_student(
        name: str = Query(..., description="Ім'я студента")
):
    """
    Створити нового студента (лише ім'я, для прикладу).

    Приклад:
      POST /students?name=Petro
    """
    global student_id_counter
    new_st = StudentModel(id=student_id_counter, name=name)
    students_db.append(new_st)
    student_id_counter += 1
    return new_st


@app.put("/students/{student_id}", response_model=StudentModel)
def update_student(
        student_id: int,
        name: str = Query(..., description="Нове ім'я студента")
):
    """Оновити ім'я студента за ID."""
    for idx, st in enumerate(students_db):
        if st.id == student_id:
            updated_st = StudentModel(id=student_id, name=name)
            students_db[idx] = updated_st
            return updated_st
    raise HTTPException(status_code=404, detail="Студента не знайдено")


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    """Видалити студента за ID."""
    for idx, st in enumerate(students_db):
        if st.id == student_id:
            students_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Студента не знайдено")


# ----------------------------------------------------------------------------------
#       ВІДПОВІДЬ НА ЗАПИТАННЯ (перевірка правильності) - приклад
# ----------------------------------------------------------------------------------
@app.post("/questions/{question_id}/answer")
def answer_question(
        question_id: int,
        student_id: int = Query(..., description="ID студента"),
        chosen_answers: str = Query(..., description="Індекси вибраних відповідей, через кому")
):
    """
    Студент надсилає відповідь на запитання.
    Приклад:
      POST /questions/5/answer?student_id=1&chosen_answers=0,2

    Повертає, чи правильна відповідь.
    """
    # Перевіримо, чи існує студент
    st_exists = any(st.id == student_id for st in students_db)
    if not st_exists:
        raise HTTPException(status_code=400, detail="Студента з таким ID не існує")

    # Шукаємо запитання
    question = None
    for q in questions_db:
        if q.id == question_id:
            question = q
            break
    if not question:
        raise HTTPException(status_code=404, detail="Запитання не знайдено")

    # Парсимо обрані індекси
    try:
        chosen_list = [int(x) for x in chosen_answers.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Некоректний формат chosen_answers.")

    # Порівнюємо множини
    is_correct = (set(chosen_list) == set(question.correct_answers))
    return {
        "question_id": question_id,
        "student_id": student_id,
        "chosen_answers": chosen_list,
        "correct_answers": question.correct_answers,
        "result": "correct" if is_correct else "wrong"
    }

# ----------------------------------------------------------------------------------
#   uvicorn task3:app --reload
# АБО
#   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# ----------------------------------------------------------------------------------
