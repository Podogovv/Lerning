import pytest
from scraper import get_book_data, scrape_books


@pytest.fixture
def sample_book_url():
    # Пример страницы книги
    return "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"


@pytest.fixture
def sample_catalog_url():
    # Пример первой страницы каталога
    return "https://books.toscrape.com/catalogue/page-1.html"


def test_get_book_data_keys(sample_book_url):
    """
    Тест: get_book_data возвращает словарь с нужными ключами.
    """
    data = get_book_data(sample_book_url)
    assert isinstance(data, dict), "Результат должен быть словарём"
    expected_keys = {"title", "price", "availability", "rating", "description", "product_information"}
    assert expected_keys.issubset(data.keys()), "Словарь должен содержать все ключи"
    
    # Вывод результата теста
    print("\n[test_get_book_data_keys] Успешно! Полученные ключи:", data.keys())


def test_get_book_data_title(sample_book_url):
    """
    Тест: title книги корректно считывается.
    """
    data = get_book_data(sample_book_url)
    assert data["title"] == "A Light in the Attic", f"Ожидаемый title 'A Light in the Attic', получено '{data['title']}'"

    # Вывод результата теста
    print(f"\n[test_get_book_data_title] Успешно! title книги: {data['title']}")

def test_get_book_data_availability_number(sample_book_url):
    """Проверка, что в наличии указано число экземпляров"""
    data = get_book_data(sample_book_url)
    avail = data["availability"]
    assert any(char.isdigit() for char in avail), f"Ожидалось число в строке наличия, получено: {avail}"
    print(f"\n test_get_book_data_availability_number: строка наличия — '{avail}'")

