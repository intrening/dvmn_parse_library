import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


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


def download_image(url, filename, folder='books/'):
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

for id in range(1,11):
    url = f'http://tululu.org/b{id}/'
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code in [301, 302]:
        continue
    soup = BeautifulSoup(response.text, 'lxml')
    header = soup.find('h1').text
    book_name, _ = header.split('::')
    book_name = book_name.strip()
    file_url = f'http://tululu.org/txt.php?id={id}'
    download_txt(url=file_url, filename=f'{book_name}.txt')

    image_link = soup.find('div', class_='bookimage').find('img')['src']
    full_link = urljoin(url, image_link)
    image_file_name = full_link.split('/')[-1]
    download_image(url=full_link, filename=image_file_name, )

