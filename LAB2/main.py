from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Міні-бібліотека",
    description="Простий приклад REST-сервісу на FastAPI для 3 ресурсів: Автори, Книги, Читачі",
    version="1.0.0"
)

# ===== Pydantic-моделі =====
class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int

class BookBase(BaseModel):
    title: str
    author_id: int
    price: float

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

class CustomerBase(BaseModel):
    name: str
    email: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

# ===== "База даних" у пам'яті =====
authors_db: List[Author] = []
books_db: List[Book] = []
customers_db: List[Customer] = []

# Лічильники для ID
author_id_counter = 1
book_id_counter = 1
customer_id_counter = 1

# =======================
#         AUTHORS
# =======================
@app.get("/authors", response_model=List[Author])
def get_authors():
    return authors_db

@app.get("/authors/{author_id}", response_model=Author)
def get_author(author_id: int):
    for author in authors_db:
        if author.id == author_id:
            return author
    raise HTTPException(status_code=404, detail="Автор не знайдений")

@app.post("/authors", response_model=Author, status_code=201)
def create_author(author_data: AuthorCreate):
    global author_id_counter
    new_author = Author(id=author_id_counter, **author_data.dict())
    authors_db.append(new_author)
    author_id_counter += 1
    return new_author

@app.put("/authors/{author_id}", response_model=Author)
def update_author(author_id: int, author_data: AuthorCreate):
    for idx, author in enumerate(authors_db):
        if author.id == author_id:
            updated_author = Author(id=author_id, **author_data.dict())
            authors_db[idx] = updated_author
            return updated_author
    raise HTTPException(status_code=404, detail="Автор не знайдений")

@app.delete("/authors/{author_id}", status_code=204)
def delete_author(author_id: int):
    for idx, author in enumerate(authors_db):
        if author.id == author_id:
            authors_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Автор не знайдений")

# =======================
#          BOOKS
# =======================
@app.get("/books", response_model=List[Book])
def get_books():
    return books_db

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книгу не знайдено")

@app.post("/books", response_model=Book, status_code=201)
def create_book(book_data: BookCreate):
    global book_id_counter
    # Перевіряємо, чи існує автор, вказаний у book_data.author_id
    author_exists = any(author.id == book_data.author_id for author in authors_db)
    if not author_exists:
        raise HTTPException(status_code=400, detail="Автор з таким ID не існує")

    new_book = Book(id=book_id_counter, **book_data.dict())
    books_db.append(new_book)
    book_id_counter += 1
    return new_book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_data: BookCreate):
    for idx, book in enumerate(books_db):
        if book.id == book_id:
            # Перевіряємо, чи існує автор, вказаний у book_data.author_id
            author_exists = any(author.id == book_data.author_id for author in authors_db)
            if not author_exists:
                raise HTTPException(status_code=400, detail="Автор з таким ID не існує")

            updated_book = Book(id=book_id, **book_data.dict())
            books_db[idx] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Книгу не знайдено")

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for idx, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Книгу не знайдено")

# =======================
#        CUSTOMERS
# =======================
@app.get("/customers", response_model=List[Customer])
def get_customers():
    return customers_db

@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    for customer in customers_db:
        if customer.id == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Читача не знайдено")

@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(customer_data: CustomerCreate):
    global customer_id_counter
    new_customer = Customer(id=customer_id_counter, **customer_data.dict())
    customers_db.append(new_customer)
    customer_id_counter += 1
    return new_customer

@app.put("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, customer_data: CustomerCreate):
    for idx, customer in enumerate(customers_db):
        if customer.id == customer_id:
            updated_customer = Customer(id=customer_id, **customer_data.dict())
            customers_db[idx] = updated_customer
            return updated_customer
    raise HTTPException(status_code=404, detail="Читача не знайдено")

@app.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    for idx, customer in enumerate(customers_db):
        if customer.id == customer_id:
            customers_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Читача не знайдено")
