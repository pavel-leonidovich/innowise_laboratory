-- 1. Создание таблиц
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_year INTEGER NOT NULL
);

CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 100),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE INDEX idx_student_id ON grades(student_id);


-- 2. Все оценки Alice Johnson
SELECT subject, grade
FROM grades
JOIN students ON grades.student_id = students.id
WHERE full_name = 'Alice Johnson';

-- 3. Средний балл каждого студента
SELECT 
    full_name,
    ROUND(AVG(grade), 2) AS average_grade
FROM students
JOIN grades ON students.id = grades.student_id
GROUP BY students.id, full_name
ORDER BY average_grade DESC;

-- 4. Студенты, родившиеся после 2004 года
SELECT full_name, birth_year
FROM students
WHERE birth_year > 2004
ORDER BY birth_year DESC, full_name;

-- 5. Средний балл по каждому предмету
SELECT 
    subject,
    ROUND(AVG(grade), 2) AS average_grade,
    COUNT(*) AS students_count
FROM grades
GROUP BY subject
ORDER BY average_grade DESC;

-- 6. Топ-3 студентов с наивысшим средним баллом
SELECT 
    full_name,
    ROUND(AVG(grade), 2) AS average_grade
FROM students
JOIN grades ON students.id = grades.student_id
GROUP BY students.id, full_name
ORDER BY average_grade DESC
LIMIT 3;

-- 7. Студенты, у которых есть хотя бы одна оценка ниже 80
SELECT DISTINCT
    full_name,
    subject,
    grade
FROM students
JOIN grades ON students.id = grades.student_id
WHERE grade < 80
ORDER BY full_name, grade;