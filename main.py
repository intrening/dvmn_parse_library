import argparse
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json


def download_txt(url, filename, text_folder):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code in [301, 302]:
        return None
    os.makedirs(text_folder, exist_ok=True)
    filename = sanitize_filename(filename)
    fpath = os.path.join(text_folder, filename)
    with open(fpath, 'w') as f:
        f.write(response.text)
    return fpath


def download_image(url, filename, image_folder):
    """Функция для скачивания картинок.

    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранена картинка.
    """
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code in [301, 302]:
        return None
    os.makedirs(image_folder, exist_ok=True)
    filename = sanitize_filename(filename)
    fpath = os.path.join(image_folder, filename)
    with open(fpath, 'wb') as f:
        f.write(response.content)
    return fpath


def get_book_ids(base_url, start_page, end_page):
    """Функция собирает список id всех книг в указанных страницах.

    Args:
        base_url (str): Cсылка на сайт.
        start_page (int): Номер первой страницы для скачивания.
        end_page (int): Номер последней страницы для скачивания.
    Returns:
        list: список id скачанных книг.
    """
    book_ids = []
    page = start_page - 1
    while not end_page or page <= end_page:
        page += 1
        page_url = f'{base_url}/l55/{page}/'
        response = requests.get(page_url, allow_redirects=False)
        response.raise_for_status()
        if response.status_code in [301, 302]:
            break
        soup = BeautifulSoup(response.text, 'lxml')
        links_from_page = soup.select('.d_book .bookimage a')
        book_ids += [link['href'][2:-1] for link in links_from_page]
    return book_ids

def get_book_list(base_url, book_ids, image_folder, text_folder):
    """Функция скачивает книги и изображения в указанные папки.

    Args:
        base_url (str): Cсылка на сайт.
        book_ids (list): список id скачанных книг.
        image_folder (str): Название папки для изображений.
        text_folder (str): Название папки для текста книг.
    Returns:
        book_list: Список словарей с книгами.
    """
    book_list = []
    for book_id in book_ids:
        book_link = f'{base_url}/b{book_id}/'
        response = requests.get(book_link, allow_redirects=False)
        response.raise_for_status()
        if response.status_code in [301, 302]:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        header = soup.find('h1').text
        title, author = header.split('::')
        title, author = title.strip(), author.strip()

        file_url = f'{base_url}/txt.php?id={book_id}'
        book_path = download_txt(url=file_url, filename=f'{title}.txt', text_folder=text_folder)

        image_link = soup.select_one('.bookimage img')['src']
        image_full_link = urljoin(base_url, image_link)
        image_file_name = image_full_link.split('/')[-1]
        img_src = download_image(
            url=image_full_link, filename=image_file_name, image_folder=image_folder,
        )

        comments_soup = soup.select('div.texts span.black')
        comments = [comment.text for comment in comments_soup]

        genres_soup = soup.select('span.d_book a')
        genres = [genre.text for genre in genres_soup]

        book_list.append({
            'title': title,
            'author': author,
            'img_src': img_src,
            'book_path': book_path,
            'comments': comments,
            'genres': genres,
        })
    return book_list

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_page", default=1, type=int,
        help="Первая страница для скачивания", 
    )
    parser.add_argument(
        "--end_page", default=None, type=int,
        help="Последняя страница для скачивания", 
    )
    args = parser.parse_args()
    book_list_filename = os.getenv("BOOK_LIST_FILENAME", "book_list.json")

    base_url = 'http://tululu.org'
    book_ids = get_book_ids(
        base_url=base_url,
        start_page=args.start_page,
        end_page=args.end_page,
    )
    book_list = get_book_list(
        base_url=base_url,
        book_ids=book_ids,
        image_folder=os.getenv('BOOK_IMAGE_FOLDERNAME', 'images'),
        text_folder=os.getenv('BOOK_TEXT_FOLDERNAME', 'books'),
    )

    with open(book_list_filename, 'w') as book_file:
        json.dump(book_list, book_file, ensure_ascii=True)


if __name__ == "__main__":
    main()
