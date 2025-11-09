import time
import requests
import schedule
import sys
import pytest
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_book_data(url: str) -> dict:
    """
    Функция парсит HTML-страницу и извлекает информацию по книге:
        - название;
        - описание;
        - цена;
        - рейтинг;
        - количество в наличии;
        - характеристики из таблицы Product Information.

    Аргумент: url (str): URL web-страницы.

    Возвращает словарь с ключами:
            - "title" (str): Название книги.
            - "description" (str | None): Описание книги (если присутствует).
            - "price" (str): Цена книги.
            - "availability" (str): Наличие и количество на складе.
            - "rating" (str): Рейтинг книги.
            - "product_information" (dict): Характеристики из таблицы Product Information.
    """
    response = requests.get(url)
    response.raise_for_status()

    response.encoding = 'utf-8'  # Декодирование в UTF-8

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1').get_text(strip=True)  # Название книги

    # Описание книги
    description = None
    desc_header = soup.find('div', id='product_description')
    if desc_header and desc_header.find_next_sibling('p'):
        description = desc_header.find_next_sibling('p').get_text(strip=True)

    price = soup.find('p', class_='price_color').get_text(strip=True)  # Цена книги
    availability = soup.find('p', class_='instock availability').get_text(strip=True)  # Наличие книги

    # Рейтинг книги
    rating_element = soup.find('p', class_='star-rating')
    rating = rating_element['class'][1] if rating_element and len(rating_element['class']) > 1 else None

    # Дополнительные характеристики из таблицы Product Information
    product_info = {}
    table = soup.find('table', class_='table table-striped')
    if table:
        for row in table.find_all('tr'):
            key = row.find('th').get_text(strip=True)
            value = row.find('td').get_text(strip=True)
            product_info[key] = value

    return {
        'title': title,
        'price': price,
        'availability': availability,
        'rating': rating,
        'description': description,
        'product_information': product_info,
    }


def print_book_data(data: dict) -> None:
    """
    Функция оформляет вывод данных о книге.

    Аргумент: data (dict): Словарь, возвращённый функцией get_book_data().
    """
    sys.stdout.reconfigure(encoding='utf-8')  # Вывод в UTF-8

    print("\n" + "-" * 50)
    print(f"  {data['title']}")
    print("-" * 50)
    print(f" Цена: {data['price']}")
    print(f" Рейтинг: {data['rating']}")
    print(f" Наличие: {data['availability']}\n")

    if data['description']:
        print(" Описание:")
        print(f"{data['description']}\n")

    print(" Характеристики (Product Information):")
    for key, value in data['product_information'].items():
        print(f"  • {key}: {value}")
    print("-" * 50 + "\n")

def scrape_books(url: str, is_save: bool = False) -> list:
    """
    Функция проходиться по всем страницам из каталога и собирает данные о книгах.

    Аргументы:
        url (str): Базовый URL каталога, где {N} номер страницы.
        is_save (bool): Если True, сохраняет данные в файл 'books_data.txt'.
                        Если False, просто возвращает результат.

    Возвращает:
        list: Список словарей с данными о книгах.
    """

    all_books = []
    page_num = 1

    print("Начинаем парсинг каталога: \n")

    while True:
        page_url = url.format(page_num)
        response = requests.get(page_url)
        base_page_url = page_url.rsplit('/', 1)[0] + '/'

        if response.status_code == 404:
            print(f" Парсинг завершён. Всего страниц: {page_num - 1}")
            break

        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        book_links = [
            urljoin(base_page_url, a['href'])
            for a in soup.select('h3 a')
        ]

        print(f" Обрабатываем страницу {page_num} ({len(book_links)} книг)...")

        for link in book_links:
            try:
                book_data = get_book_data(link)
                all_books.append(book_data)
            except Exception as e:
                print(f" Ошибка при обработке {link}: {e}")

        page_num += 1

    if is_save:
        with open("books_data.txt", "w", encoding="utf-8") as file:
            for i, book in enumerate(all_books, start=1):
                file.write(f"{i}. {book['title']} — {book['price']} — {book['availability']}\n")
                file.write(f"   Рейтинг: {book['rating']}\n")
                if book['description']:
                    file.write(f"   Описание: {book['description'][:200]}...\n")
                file.write(f"   Характеристики: {book['product_information']}\n")
                file.write("-" * 80 + "\n")
        print("\n Данные успешно сохранены в файл books_data.txt")

    return all_books

def scheduler (url: str, time_str: str = "19:00"):
    """
    Настраивает ежедневный запуск парсера в указанное время и выполняет сбор данных с указанного URL.

    Аргументы:
        url (str): Базовый URL каталога.
        time_str (str): Время запуска в 19:00.
    """
    def time():
        scrape_books(url, is_save=True)

    schedule.every().day.at(time_str).do(time)
    print(f" Планировщик запущен. \n")

    while True:
        schedule.run_pending()
        time.sleep(60)  # проверяем расписание раз в минуту
