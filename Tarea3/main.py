import os
from pathlib import Path
import subprocess
from threading import Thread

def menu() -> int:
    os.system('clear')
    print("\n\t--------------- WildFork ---------------\n")
    print("1. Mostrar carpeta donde se encuentra el archivo a leer")
    print("2. Leer el archivo del negocio WildFork")
    print("3. Buscar por clave en el archivo del negocio WildFork")
    print("4. Salir")
    try: 
        option = int(input("\nIngrese una opcion: "))
        return option
    except ValueError:
        print("\n\tOpcion ingresada incorrectamente, vuelva a intentarlo ...")
        input("\n\nPresione Enter para continuar.")
        os.system('clear')
        menu()


def main():
    while True:
        option = menu()
        match option:
            case 1:
                # Ejecutar un proceso hijo con la ejecucion del comando `ls`
                result = subprocess.run(["ls", "-l"])

                # Verificar si se ejecutó correctamente
                if result.returncode == 0:
                    print("\n\n\tEl comando se ejecutó con éxito")
                else:
                    print("\n\n\tHubo un error al ejecutar el comando")
                
                input("\n\nPresione Enter para continuar.")
                
            case 2:
                script = Path("./src/read.py")
                # Ejecutar un proceso hijo con la ejecucion del programa de mostrar los registros
                result = subprocess.run(["python", script.absolute()])

                # Verificar si se ejecutó correctamente
                if result.returncode != 0:
                    print("\n\n\tHubo un error al ejecutar el comando")
                    input("\n\nPresione Enter para continuar.")

            case 3:
                script = Path("./src/search.py")
                # Ejecutar un proceso hijo con la ejecucion del programa de mostrar los registros
                result = subprocess.run(["python", script.absolute()])

                # Verificar si se ejecutó correctamente
                if result.returncode != 0:
                    print("\n\n\tHubo un error al ejecutar el comando")
                    input("\n\nPresione Enter para continuar.")

            case 4:
                os.system("clear")
                print("\n\tVuleva pronto <3\n")
                break
            case _:
                print("Esa opcion no se encuentra en el menu :(")
                input("\n\nPresione Enter para continuar.")
        

if __name__ == '__main__':
    main()
