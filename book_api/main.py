# main.py
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List

# ----------------------------
# ШАГ 1: Настройка базы данных
# ----------------------------

# Создаем подключение к SQLite базе данных (файл database.db)
# echo=True позволяет видеть SQL-запросы в консоли (удобно для отладки)
engine = create_engine("sqlite:///./database.db", echo=True)

# Создаем базовый класс для моделей
Base = declarative_base()

# ----------------------------
# ШАГ 2: Определяем модель Book
# ----------------------------

class BookDB(Base):
    __tablename__ = "books"  # Название таблицы в БД
    
    # Колонки таблицы:
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    title = Column(String, nullable=False)  # Название (обязательное)
    author = Column(String, nullable=False)  # Автор (обязательное)
    year = Column(Integer, nullable=True)    # Год издания (необязательное)

# Создаем таблицу в базе данных (если ее еще нет)
Base.metadata.create_all(bind=engine)

# ----------------------------
# ШАГ 3: Создаем сессии для работы с БД
# ----------------------------

# SessionLocal - фабрика для создания сессий БД
# autocommit=False - изменения не сохраняются автоматически
# autoflush=False - не сбрасываем сессию после каждого запроса
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция-зависимость для получения сессии БД
def get_db():
    db = SessionLocal()  # Создаем новую сессию
    try:
        yield db  # Отдаем сессию в обработчик запроса
    finally:
        db.close()  # Закрываем сессию после обработки

# ----------------------------
# ШАГ 4: Создаем Pydantic-схемы для валидации данных
# ----------------------------

# Схема для создания книги (без id)
class BookCreate(BaseModel):
    title: str
    author: str
    year: Optional[int] = None

# Схема для обновления книги (все поля необязательные)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None

# Схема для отображения книги (с id)
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: Optional[int]
    
    # Эта настройка позволяет работать с SQLAlchemy объектами
    class Config:
        orm_mode = True

# ----------------------------
# ШАГ 5: Создаем FastAPI приложение
# ----------------------------

app = FastAPI(title="Book Collection API")

# ----------------------------
# ШАГ 6: Создаем эндпоинты
# ----------------------------

# 1. Добавление новой книги
@app.post("/books/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Добавляет новую книгу в коллекцию
    
    Параметры:
    - title (обязательно): название книги
    - author (обязательно): автор книги
    - year (опционально): год издания
    
    Пример JSON тела запроса:
    {
        "title": "Преступление и наказание",
        "author": "Федор Достоевский",
        "year": 1866
    }
    """
    # Создаем объект книги для БД
    db_book = BookDB(**book.dict())
    
    # Добавляем в сессию
    db.add(db_book)
    
    # Сохраняем изменения в БД
    db.commit()
    
    # Обновляем объект, чтобы получить его id
    db.refresh(db_book)
    
    return db_book


# 2. Получение всех книг
@app.get("/books/", response_model=List[BookResponse])
def get_all_books(
    skip: int = Query(0, description="Пропустить N первых книг"),
    limit: int = Query(100, description="Ограничить количество книг"),
    db: Session = Depends(get_db)
):
    """
    Получает список всех книг с поддержкой пагинации
    
    Query-параметры:
    - skip: сколько книг пропустить (для пагинации)
    - limit: сколько книг вернуть (максимум)
    
    Пример запроса:
    GET /books/?skip=0&limit=10
    """
    # Получаем книги с учетом пагинации
    books = db.query(BookDB).offset(skip).limit(limit).all()
    return books


# 3. Удаление книги по ID
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Удаляет книгу по её ID
    
    Параметры пути:
    - book_id: идентификатор книги для удаления
    
    Пример запроса:
    DELETE /books/1
    """
    # Ищем книгу в БД
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    
    # Если книга не найдена - возвращаем ошибку 404
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    # Удаляем книгу
    db.delete(book)
    db.commit()
    
    # 204 - No Content (успешное удаление без возврата данных)
    return


# 4. Обновление книги по ID
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int, 
    book_update: BookUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновляет информацию о книге
    
    Параметры пути:
    - book_id: идентификатор книги
    
    Тело запроса (только поля которые нужно изменить):
    {
        "title": "Новое название",
        "author": "Новый автор",
        "year": 2024
    }
    """
    # Ищем книгу в БД
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()
    
    if not db_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    # Получаем только переданные поля (исключаем None)
    update_data = book_update.dict(exclude_unset=True)
    
    # Обновляем каждое поле
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    # Сохраняем изменения
    db.commit()
    db.refresh(db_book)
    
    return db_book


# 5. Поиск книг
@app.get("/books/search/", response_model=List[BookResponse])
def search_books(
    title: Optional[str] = Query(None, description="Поиск по названию"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    year: Optional[int] = Query(None, description="Поиск по году"),
    db: Session = Depends(get_db)
):
    """
    Ищет книги по различным критериям
    
    Можно искать по одному или нескольким полям одновременно
    Поиск регистронезависимый и частичный (LIKE %...%)
    
    Примеры запросов:
    GET /books/search/?title=война
    GET /books/search/?author=толстой&year=1869
    """
    # Начинаем с базового запроса
    query = db.query(BookDB)
    
    # Добавляем условия поиска, если они переданы
    if title:
        query = query.filter(BookDB.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(BookDB.author.ilike(f"%{author}%"))
    if year:
        query = query.filter(BookDB.year == year)
    
    # Выполняем запрос
    books = query.all()
    
    if not books:
        raise HTTPException(status_code=404, detail="Книги не найдены")
    
    return books


# Корневой эндпоинт для проверки работы
@app.get("/")
def read_root():
    """
    Основная страница API
    
    Возвращает информацию о доступных эндпоинтах
    """
    return {
        "message": "Добро пожаловать в Book Collection API!",
        "endpoints": {
            "POST /books/": "Добавить книгу",
            "GET /books/": "Получить все книги",
            "DELETE /books/{id}": "Удалить книгу",
            "PUT /books/{id}": "Обновить книгу",
            "GET /books/search/": "Поиск книг"
        },
        "docs": "http://127.0.0.1:8000/docs",
        "redoc": "http://127.0.0.1:8000/redoc"
    }