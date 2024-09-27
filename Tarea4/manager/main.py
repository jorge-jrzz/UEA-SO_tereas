from multiprocessing import Manager, Process
from typing import List
import flet as ft
from core import Register, read_csv, write_csv, to_DataTable

# Ruta del archivo CSV
DATA_FILE = "./data/wildfork.csv"

# Crear memoria compartida para los productos con todos los atributos
def create_shared_product_list():
    data = read_csv(DATA_FILE)
    # Incluimos todos los atributos de cada registro
    return [
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

# Función para acceder a los detalles del producto con bloqueo
def access_product(products: List, lock, product_id):
    with lock:
        product = products[product_id]
        if product['is_locked']:
            return False  # El producto está bloqueado por otra instancia
        else:
            lock_state = product.copy()
            lock_state['is_locked'] = True
            products[product_id] = lock_state # Bloquea el producto
            return product  # Devuelve el producto para mostrar los detalles

# Función para desbloquear un producto después de la compra o regreso
def unlock_product(products, lock, product_id):
    with lock:
        product = products[product_id]
        lock_state = product.copy()
        lock_state['is_locked'] = False
        products[product_id] = lock_state  # Desbloquea el producto

def alert(error: str) -> ft.AlertDialog:
    """Mostrar un diálogo de alerta con un mensaje de error."""
    return ft.AlertDialog(title=ft.Text(error))

def main(page: ft.Page, products: List, lock):
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

    # Componentes de la interfaz de usuario
    id_register = ft.Text("", theme_style=ft.TextThemeStyle.BODY_LARGE)
    id_search = ft.TextField(label="ID del producto", icon=ft.icons.GRID_3X3)
    data_register = ft.Text("", weight=ft.FontWeight.BOLD)

    # Función para buscar un registro
    def go_register(e):
        try:
            product_id = int(id_search.value) - 1
            # Intentamos acceder al producto con el bloqueo
            # print("Estado del bloqueo: ", products[product_id]['is_locked'])
            product = access_product(products, lock, product_id)
            # print("Estado del bloqueo despues: ", products[product_id]['is_locked'])
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

    # Función para regresar a la página principal
    def go_home(product_id=None):
        if product_id is not None:
            unlock_product(products, lock, product_id)  # Desbloqueamos el producto
        actualizar_datos()
        title_appbar.value = "Productos disponibles"
        page.scroll = ft.ScrollMode.AUTO
        page.bottom_appbar = home_bottombar
        page.controls.pop()
        page.add(data_table)
        page.update()

    # Función para actualizar los datos de la tabla
    def actualizar_datos():
        """Actualiza la tabla de productos con los datos en memoria compartida."""
        # Convertimos cada diccionario de producto a un objeto Register
        data_table.rows = to_DataTable([Register(**p) for p in products])

    # Función para procesar la compra de un producto
    def shop(product_id):
        with lock:
            if int(products[product_id]['stock']) > 0:
                product_copy = products[product_id].copy()
                product_copy['stock'] = int(product_copy['stock']) - 1
                products[product_id] = product_copy
                # Actualizamos el archivo CSV
                write_csv(DATA_FILE, [Register(**p) for p in products])
                page.open(ft.AlertDialog(title=ft.Text(f"Producto '{products[product_id]['name']}' comprado con éxito"), on_dismiss=lambda e: go_home(product_id)))
            else:
                page.open(alert("No hay suficiente stock del producto."))

    # Barra inferior en la página de detalles
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

    # Tabla de productos
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

    # Contenedor de detalles del registro
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

    # Configuración inicial de la página
    actualizar_datos()
    page.appbar = appbar
    page.bottom_appbar = home_bottombar
    page.add(data_table)


def run_flet_app(products, lock):
    ft.app(target=lambda page: main(page, products, lock), assets_dir="assets")


if __name__ == "__main__":
    manager = Manager()
    products = manager.list(create_shared_product_list())
    lock = manager.Lock()

    # Crear dos procesos que corran la aplicación Flet
    p1 = Process(target=run_flet_app, args=(products, lock))
    p2 = Process(target=run_flet_app, args=(products, lock))

    # Iniciar ambos procesos
    p1.start()
    p2.start()

    # Esperar a que ambos procesos terminen
    p1.join()
    p2.join()