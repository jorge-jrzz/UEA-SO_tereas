from random import choice
import sqlite3
from pathlib import Path
from typing import List, Generator


def get_id():
    first_id = 2139
    for _ in range(100000):
        first_id += 1
        yield first_id
    

def make_register(path: str, id_generator: Generator) -> List[str]:
    register = []
    data_files = Path(path).glob('*.txt')

    register.append(next(id_generator))

    for current_file in data_files:
        lines = current_file.read_text(encoding='utf-8').splitlines()
        register.append(choice(lines))

    return register


if __name__ == '__main__':
    registers_db = './data/WildFork.db'
    
    id = get_id()

    with sqlite3.connect(registers_db) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registers (
                id INTEGER PRYMARY KEY,
                nombre_producto TEXT,
                categoria TEXT,
                peso_kg TEXT,
                precio TEXT,
                fecha_vencimiento TEXT
            )
        ''')

        for _ in range(100000):
            register = make_register('./data', id)
            cursor.execute('''
                INSERT INTO registers (id, nombre_producto, categoria, peso_kg, precio, fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?)''',  tuple(register)
            )