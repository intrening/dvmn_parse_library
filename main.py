import argparse
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json


def download_txt(url, filename, folder='books'):
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
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    fpath = os.path.join(folder, filename)
    with open(fpath, 'w') as f:
        f.write(response.text)
    return fpath


def download_image(url, filename, folder='images'):
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
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    fpath = os.path.join(folder, filename)
    with open(fpath, 'wb') as f:
        f.write(response.content)
    return fpath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_page", help="Первая страница для скачивания", default=1, type=int,
    )
    parser.add_argument(
        "--end_page", help="Последняя страница для скачивания", default=None, type=int,
    )
    args = parser.parse_args()
    start_page, end_page = args.start_page, args.end_page

    base_url = 'http://tululu.org'
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
        book_path = download_txt(url=file_url, filename=f'{title}.txt')

        image_link = soup.select_one('.bookimage img')['src']
        image_full_link = urljoin(base_url, image_link)
        image_file_name = image_full_link.split('/')[-1]
        img_src = download_image(url=image_full_link, filename=image_file_name)

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

    with open('book_list.json', 'w') as book_file:
        json.dump(book_list, book_file, ensure_ascii=True)


if __name__ == "__main__":
    main()
