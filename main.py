import requests
import os

os.makedirs('books', exist_ok=True)

for id in range(1,11):
    url = f'http://tululu.org/txt.php?id={id}'
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code not in [301, 302]:
        with open(f'books/book{id}.txt','w') as f:
            f.write(response.text)
