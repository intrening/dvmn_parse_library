from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell


def on_reload():
    BOOKS_ON_PAGE = 10
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open ('book_list.json', 'r') as f:
        books_json = f.read()
    books = json.loads(books_json)
    
    books_chunks = [books[x:x+BOOKS_ON_PAGE] for x in range(0, len(books), BOOKS_ON_PAGE)]
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

on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')