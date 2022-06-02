# Shop ORM Project

Учебный проект для курсовой работы во 2 семестре 3 курса РТУ МИРЭА.

### Структура:
* `sql` - SQL файлы для генерации таблиц, триггеров и заполнения
* `orm` - файлы для генерации таблицы с использованием ORM подхода
  * `extensions.py` - вспомогательные миксины
  * `tables.py` - классы таблиц 
  * `insert.py` - изначальное заполнение mock-данными
* `cli` - интерфейс командной строки
* `app` - графический интерфейс
* `requirements.txt` - зависимости проекта

### Запуск

```
pip install -r requirements.txt

python main.py
```