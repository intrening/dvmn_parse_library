import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell

BOOK_LIST_FILENAME = os.getenv("BOOK_LIST_FILENAME", "book_list.json")

def on_reload(books_on_page=10):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open (BOOK_LIST_FILENAME, 'r') as f:
        books_json = f.read()
    books = json.loads(books_json)
    
    books_chunks = [books[x:x+books_on_page] for x in range(0, len(books), books_on_page)]
    pages_len = len(books_chunks)

    for num, books in enumerate(books_chunks, start=1):
        rendered_page = template.render(
            books=books,
            pages=range(1, pages_len+1),
            current_page=num,
        )
        filename = f'static/index{num}.html'
        with open(filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)

def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')

if __name__ == '__main__':
    main()
