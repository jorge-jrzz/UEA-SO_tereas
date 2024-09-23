import flet as ft
from core import read_csv, write_csv, to_DataTable, search_register

# Ruta del archivo CSV
DATA_FILE = "./data/wildfork.csv"

# Leer los datos iniciales
data = read_csv(DATA_FILE)
rows = to_DataTable(data)


def alert(error: str) -> ft.AlertDialog:
    """Mostrar un diálogo de alerta con un mensaje de error."""
    return ft.AlertDialog(title=ft.Text(error))


def main(page: ft.Page):
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
            product_id = int(id_search.value)
            reg_info = search_register(data, product_id)
            if reg_info:
                mostrar_detalles_producto(reg_info)
            else:
                page.open(alert("No se encuentra un producto con el ID ingresado o el producto está agotado"))
        except ValueError:
            page.open(alert("Valor ingresado incorrectamente"))
        except Exception as ex:
            print(f"Error inesperado: {ex}")

    def mostrar_detalles_producto(reg_info):
        """Muestra los detalles del producto seleccionado."""
        title_appbar.value = "Compra de producto"
        id_register.value = f"Detalles del producto: {id_search.value}"
        data_register.value = str(reg_info)
        page.bottom_appbar = register_bottombar
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
    def go_home(e):
        actualizar_datos()
        title_appbar.value = "Productos disponibles"
        page.scroll = ft.ScrollMode.AUTO
        page.bottom_appbar = home_bottombar
        page.controls.pop()
        page.add(data_table)
        page.update()

    # Función para actualizar los datos de la tabla
    def actualizar_datos():
        global data, rows
        data = read_csv(DATA_FILE)
        rows = to_DataTable(data)
        data_table.rows = rows

    # Función para procesar la compra de un producto
    def shop(e):
        try:
            product_id = int(id_search.value) - 1
            if int(data[product_id].stock) > 0:
                data[product_id].stock = int(data[product_id].stock) - 1
                write_csv(DATA_FILE, data)
                page.open(ft.AlertDialog(title=ft.Text(f"Producto '{data[product_id].name}' comprado con éxito"), on_dismiss=go_home))
            else:
                page.open(alert("No hay suficiente stock del producto."))
        except Exception as ex:
            page.open(alert(f"Error en la compra: {ex}"))

    # Barra inferior en la página de detalles
    register_bottombar = ft.BottomAppBar(
        content=ft.Row(
            controls=[
                ft.FilledButton(text="Comprar", icon=ft.icons.SHOPPING_BAG_OUTLINED, on_click=shop),
                ft.FilledButton(text="Regresar", icon=ft.icons.ARROW_BACK, on_click=go_home)
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
            ft.DataColumn(ft.Text("Categoria")),
            ft.DataColumn(ft.Text("Peso (kg)"), numeric=True),
            ft.DataColumn(ft.Text("Precio (MXN)"), numeric=True),
            ft.DataColumn(ft.Text("Caducidad")),
            ft.DataColumn(ft.Text("Stock"), numeric=True),
        ],
        rows=rows
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
    page.appbar = appbar
    page.bottom_appbar = home_bottombar
    page.add(data_table)


ft.app(
    main,
    assets_dir="assets"
)