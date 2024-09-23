import pickle
from multiprocessing import Process, Semaphore
from multiprocessing.shared_memory import SharedMemory
from typing import Any, Union, Dict
from core import Register, read_csv, write_csv, to_DataTable
import flet as ft

# Ruta del archivo CSV
DATA_FILE = "./data/wildfork.csv"

# Crear memoria compartida para los productos
def create_shared_product_list() -> SharedMemory:
    data = read_csv(DATA_FILE)
    product_list = [
        {
            'id_reg': reg.id_reg, 
            'name': reg.name, 
            'category': reg.category, 
            'weight': reg.weight, 
            'price': reg.price, 
            'expiry': reg.expiry, 
            'stock': reg.stock, 
            'is_locked': False  # Bandera para indicar si está bloqueado
        } 
        for reg in data
    ]
    serialized_data = pickle.dumps(product_list)  # Serializamos la lista de diccionarios
    shm = SharedMemory(create=True, size=len(serialized_data))  # Creamos memoria compartida
    shm.buf[:len(serialized_data)] = serialized_data  # Escribimos los datos en la memoria compartida
    return shm

# Función para leer los datos de la memoria compartida
def read_shared_product_list(shm: SharedMemory) -> Any:
    serialized_data = bytes(shm.buf[:])  # Leemos los datos serializados
    return pickle.loads(serialized_data)  # Deserializamos para obtener la lista de productos

# Función para escribir los datos en la memoria compartida
def write_shared_product_list(shm: SharedMemory, products: Any) -> None:
    serialized_data = pickle.dumps(products)
    shm.buf[:len(serialized_data)] = serialized_data  # Actualizamos la memoria compartida con los nuevos datos

# Función para acceder a los detalles del producto con bloqueo
def access_product(shm: SharedMemory, sem, product_id: int) -> Union[bool, Dict]:
    with sem:
        products = read_shared_product_list(shm)
        product = products[product_id]
        if product['is_locked']:
            return False  # El producto está bloqueado por otra instancia
        else:
            product['is_locked'] = True
            products[product_id] = product
            write_shared_product_list(shm, products)  # Actualizamos la memoria compartida
            return product  # Devuelve el producto para mostrar los detalles

# Función para desbloquear un producto después de la compra o regreso
def unlock_product(shm: SharedMemory, sem, product_id: int) -> None:
    with sem:
        products = read_shared_product_list(shm)
        product = products[product_id]
        product['is_locked'] = False
        products[product_id] = product
        write_shared_product_list(shm, products)  # Actualizamos la memoria compartida

def alert(msj: str) -> ft.AlertDialog:
    return ft.AlertDialog(title=ft.Text(msj))

def main(page: ft.Page, shm: SharedMemory, sem):
    # Configuración inicial de la página
    page.title = "Tarea 4 - Jorge Juarez"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # AppBar y título
    title_appbar = ft.Text("Productos disponibles", theme_style=ft.TextThemeStyle.HEADLINE_SMALL)
    appbar = ft.AppBar(
        title=title_appbar,
        center_title=True,
        leading=ft.Image(src="images/wild-fork-logo.png"),
        leading_width=180
    )

    id_register = ft.Text("", theme_style=ft.TextThemeStyle.BODY_LARGE)
    id_search = ft.TextField(label="ID del producto", icon=ft.icons.GRID_3X3)
    data_register = ft.Text("", weight=ft.FontWeight.BOLD)

    def go_register(e):
        try:
            product_id = int(id_search.value) - 1
            product = access_product(shm, sem, product_id)
            if product:
                mostrar_detalles_producto(product, product_id)
            else:
                page.open(alert("El producto está siendo accedido por otra instancia"))
        except ValueError:
            page.open(alert("Valor ingresado incorrectamente"))
        except IndexError:
            page.open(alert(f"Producto con el ID: {id_search.value} no encontrado"))
        except Exception as ex:
            page.open(alert(f"Error inesperado: {ex}"))

    def mostrar_detalles_producto(product, product_id):
        """Muestra los detalles del producto seleccionado."""
        title_appbar.value = "Compra de producto"
        id_register.value = f"Detalles del producto: {product['id_reg']}"
        data_register.value = f"""
        Nombre: {product['name']}   
        Categoría: {product['category']}      
        Peso: {product['weight']} kg    
        Precio: {product['price']} MXN  
        Caducidad: {product['expiry']}  
        Stock: {product['stock']}   
        """
        page.bottom_appbar = register_bottombar(product_id)
        page.scroll = None
        page.controls.pop()
        page.add(register)
        page.update()

    # Barra inferior en la página de inicio
    home_bottombar = ft.BottomAppBar(
        content=ft.Row(
            controls=[
                id_search,
                ft.FilledButton(text="Detalles", icon=ft.icons.SAVED_SEARCH_ROUNDED, on_click=go_register)
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY
        )
    )

    def go_home(product_id=None):
        if product_id is not None:
            unlock_product(shm, sem, product_id)
        update_data()
        title_appbar.value = "Productos disponibles"
        page.scroll = ft.ScrollMode.AUTO
        page.bottom_appbar = home_bottombar
        page.controls.pop()
        page.add(data_table)
        page.update()

    def update_data():
        """Actualiza la tabla de productos con los datos en memoria compartida."""
        products = read_shared_product_list(shm)
        data_table.rows = to_DataTable([Register(**p) for p in products])

    def shop(product_id):
        with sem:
            products = read_shared_product_list(shm)
            if int(products[product_id]['stock']) > 0:
                product_copy = products[product_id].copy()
                product_copy['stock'] = int(product_copy['stock']) - 1
                products[product_id] = product_copy
                write_shared_product_list(shm, products)
                write_csv(DATA_FILE, [Register(**p) for p in products])
                page.open(ft.AlertDialog(title=ft.Text(f"Producto '{products[product_id]['name']}' comprado con éxito"), on_dismiss=lambda e: go_home(product_id)))
            else:
                page.open(alert("No hay suficiente stock del producto."))

    def register_bottombar(product_id):
        return ft.BottomAppBar(
            content=ft.Row(
                controls=[
                    ft.FilledButton(text="Comprar", icon=ft.icons.SHOPPING_BAG_OUTLINED, on_click=lambda e: shop(product_id)),
                    ft.FilledButton(text="Regresar", icon=ft.icons.ARROW_BACK, on_click=lambda e: go_home(product_id))
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY
            )
        )

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID"), numeric=True),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Peso (kg)"), numeric=True),
            ft.DataColumn(ft.Text("Precio (MXN)"), numeric=True),
            ft.DataColumn(ft.Text("Caducidad")),
            ft.DataColumn(ft.Text("Stock"), numeric=True)
        ]
    )

    register = ft.Container(
        content=ft.Column(
            controls=[
                id_register,
                ft.Container(
                    content=data_register,
                    padding=ft.padding.all(5),
                    border=ft.border.all(2.5, "0"),
                    border_radius=ft.border_radius.all(15)
                )
            ]
        )
    )

    update_data()
    page.appbar = appbar
    page.bottom_appbar = home_bottombar
    page.add(data_table)


def run_flet_app(shm: SharedMemory, sem) -> None:
    ft.app(target=lambda page: main(page, shm, sem), assets_dir="assets")


if __name__ == "__main__":
    shm = create_shared_product_list()
    sem = Semaphore(1)

    p1 = Process(target=run_flet_app, args=(shm, sem))
    p2 = Process(target=run_flet_app, args=(shm, sem))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    shm.close()
    shm.unlink()