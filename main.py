import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json


def download_txt(url, filename, folder='books/'):
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
    with open(fpath,'w') as f:
        f.write(response.text)
    return fpath


def download_image(url, filename, folder='images/'):
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
    with open(fpath,'wb') as f:
        f.write(response.content)
    return fpath

book_ids = []
for page in (1,1):
    url = f'http://tululu.org/l55/{page}/'
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code in [301, 302]:
        break

    soup = BeautifulSoup(response.text, 'lxml')

    book_tables = soup.find_all('table', class_='d_book')
    book_ids += [book.find('a')['href'][2:-1] for book in book_tables]
    

book_list = []

for book_id in book_ids:
    book_link = f'http://tululu.org/b{book_id}/'
    response = requests.get(book_link, allow_redirects=False)
    response.raise_for_status()
    if response.status_code in [301, 302]:
        continue
    soup = BeautifulSoup(response.text, 'lxml')
    header = soup.find('h1').text
    title, author = header.split('::')
    title = title.strip()
    author = author.strip()
    file_url = f'http://tululu.org/txt.php?id={book_id}'
    book_path = download_txt(url=file_url, filename=f'{title}.txt')

    image_link = soup.find('div', class_='bookimage').find('img')['src']
    image_full_link = urljoin(url, image_link)
    image_file_name = image_full_link.split('/')[-1]
    img_src = download_image(url=image_full_link, filename=image_file_name, )

    comments = soup.find_all('div', class_='texts')
    comments = [comment.find('span', class_='black').text for comment in comments]

    genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres]

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
