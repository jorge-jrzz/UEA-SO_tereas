import os 
import sqlite3
from queue import Queue
from threading import Thread


def serch_register(db_path: str, register_id: int, queue: Queue):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM registers WHERE id = {register_id}")
        res = cursor.fetchone()

    queue.put(res)
    return res

def print_tuple_table(tuple_data):
    # Definir los encabezados
    headers = ["ID", "Nombre", "Categoría", "Peso (kg)", "Cantidad", "Fecha de Caducidad"]
    # Asegurarse de que tuple_data es una tupla
    if not isinstance(tuple_data, tuple):
        raise TypeError("El argumento debe ser una tupla")
    # Verificar que la tupla tiene la longitud correcta
    if len(tuple_data) != len(headers):
        raise ValueError(f"La tupla debe tener {len(headers)} elementos")
    # Convertir todos los elementos de la tupla a strings
    data = [str(item) for item in tuple_data]
    # Encontrar el ancho máximo para cada columna
    col_widths = [max(len(header), len(item)) for header, item in zip(headers, data)]
    # Crear el formato de la línea
    line_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)
    # Imprimir los encabezados
    print(line_format.format(*headers))
    # Imprimir una línea separadora
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
    # Imprimir la fila de datos
    print(line_format.format(*data))

def user_serach(db_path: str):
    result_queue = Queue()
    option = ''
    while option != 'q':
        os.system('clear')
        while True:
            try:
                print("\n\t\t\t------------- WildFork -------------\n\n")
                id = int(input("Buscar por ID: ").strip())
                print()
                break
            except ValueError:
                print("\n\tOpcion ingresada incorrectamente, vuelva a intentarlo ...")
                input("\n\nPresione Enter para continuar.")
                os.system('clear')
        
        thread = Thread(target=serch_register, args=(db_path, id, result_queue))
        thread.start()
        thread.join()
        result = result_queue.get()
        if result is not None:
            thread = Thread(target=print_tuple_table, kwargs={'tuple_data': result})
            thread.start()
            thread.join()
        else:
            print(f"\nNo se encuentra ningun registro con el ID: {id}")

        print("\n\nRealizar otra busqueda: [s]\tSalir: [q]\n")
        option = input("Opcion: ").strip()
        if option == 'q':
            break
    

if __name__ == '__main__':
    user_serach('./data/WildFork.db')

