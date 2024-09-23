from typing import List, Dict, Union, Optional
from csv import DictReader, DictWriter
import flet as ft


class Register:
    def __init__(self, id_reg: int, name: str, category: str, weight: int, price: float, expiry: str, stock: int, is_locked: Optional[bool] = None) -> None:
        self.id_reg = id_reg
        self.name = name
        self.category = category
        self.weight = weight
        self.price = price
        self.expiry = expiry
        self.stock = stock
        self.is_locked = is_locked

    def getattribs_dict(self) -> Dict:
        return {
            "id_reg": self.id_reg, "name": self.name, "category": self.category,
            "weight": self.weight, "price": self.price, "expiry": self.expiry, "stock": self.stock
        }

    def __str__(self) -> str:
        return f'Nombre: {self.name}\nCategoria: {self.category}\nPeso (kg): {self.weight}\nPrecio (MXN): $ {self.price}\nCaducidad: {self.expiry}\nStock: {self.stock}'


def read_csv(file_path: str) -> List[Register]:
    """Leer datos desde un archivo CSV y devolver una lista de registros."""
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = DictReader(file)
            return [Register(**row) for row in csv_reader]
    except FileNotFoundError:
        print(f"El archivo {file_path} no se encuentra.")
        return []


def write_csv(file_path: str, registers: List[Register]) -> None:
    """Escribir los registros actualizados en un archivo CSV."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id_reg', 'name', 'category', 'weight', 'price', 'expiry', 'stock']
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in registers:
            writer.writerow(r.getattribs_dict())


def to_DataTable(registers: List[Register]) -> List[ft.DataRow]:
    """Convertir los registros en filas para la tabla de datos en Flet."""
    return [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(rr.id_reg))),
                ft.DataCell(ft.Text(rr.name)),
                ft.DataCell(ft.Text(rr.category)),
                ft.DataCell(ft.Text(str(rr.weight))),
                ft.DataCell(ft.Text(f"${rr.price}")),
                ft.DataCell(ft.Text(rr.expiry)),
                ft.DataCell(ft.Text(str(rr.stock)))
            ]
        ) for rr in registers
    ]


def search_register(registers: List[Register], id_reg: int) -> Union[Register, bool]:
    """Buscar un registro por su ID. Devolver el registro o False si no existe."""
    return False if id_reg > len(registers) or id_reg <= 0 else registers[id_reg - 1]