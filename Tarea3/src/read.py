import threading
import sqlite3
from queue import Queue
from typing import List
import os

def get_50_registers(db_path: str, page: int, queue: Queue):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM registers LIMIT 50 OFFSET {(page - 1) * 50}")
        res = cursor.fetchall()

    queue.put(res)

    return res

def print_tuple_table(tuples: List):
    # Definir los encabezados
    headers = ["ID", "Nombre", "Categoría", "Peso (kg)", "Cantidad", "Fecha de Caducidad"]
    # Convertir tuples a una lista de listas para facilitar el manejo
    data = [list(t) for t in tuples]
    # Encontrar el ancho máximo para cada columna
    col_widths = [max(len(str(item)) for item in column) for column in zip(headers, *data)]
    # Crear el formato de la línea
    line_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)
    # Imprimir los encabezados
    print(line_format.format(*headers))
    # Imprimir una línea separadora
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
    # Imprimir cada fila de datos
    for row in data:
        print(line_format.format(*(str(item) for item in row)))


def show_db(db_path: str, page: int):
    result_queue = Queue()
    thread = threading.Thread(target=get_50_registers, args=(db_path, page, result_queue))
    thread.start()
    print("\n\t\t\t------------- WildFork -------------\n\n")
    thread.join()
    result = result_queue.get()
    print_tuple_table(result)


def view_all(db_path: str):
    page = 1
    option = ''
    while option != 'q':
        thread = threading.Thread(target=show_db, args=(db_path, page))
        os.system('clear')
        thread.start()
        thread.join()
        print("\n\n-----------------------------------------------------------------------------------------------")
        print("Anteriores 50 registros: [b]\tSiguientes 50 registros: [n]\tSalir: [q]\n")
        option = input("Opcion: ").strip()
        if option == 'n':
            page += 1
        elif option == 'b':
            if page > 1:
                page -= 1


if __name__ == '__main__':
    view_all('./data/WildFork.db')