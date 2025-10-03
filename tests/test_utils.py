import os
import tempfile
import csv


def create_test_csv_file():
    """Создает временный CSV файл для тестирования импорта"""
    # Создаем временный файл
    fd, path = tempfile.mkstemp(suffix='.csv')

    try:
        with os.fdopen(fd, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Заголовок
            writer.writerow(['id', 'наименование', 'категория', 'цена', 'рейтинг', 'отзывы'])
            # Данные
            writer.writerow([1, 'Тестовый товар 1', 'Электроника', '1000.0', '4.5', 'Отличный товар'])
            writer.writerow([2, 'Тестовый товар 2', 'Бытовая техника', '2000.0', '4.2', 'Хорошее качество'])
            writer.writerow([3, 'Тестовый товар 3', 'Электроника', '1500.0', '4.7', ''])

        return path
    except Exception:
        os.unlink(path)
        raise