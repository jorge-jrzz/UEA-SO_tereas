#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/wait.h>

int print_menu() {
    int option;
    system("clear");
    printf("\n\t\t\t--------------- WildFork ---------------\n\n");
    printf("1. Mostrar carpeta donde se encuentra el archivo a leer\n");
    printf("2. Leer el archivo del negocio WildFork\n");
    printf("3. Buscar por clave en el archivo del negocio WildFork\n");
    printf("4. Salir\n\n");
    printf("Ingrese una opcion: ");
    scanf("%d", &option);
    return option;
}

int main() {
    int option;
    pid_t pid1, pid2;
    option = print_menu();

    while (option != 4) {
        switch (option) {
            case 1:
                system("clear");
                pid1 = fork();
                if (pid1 < 0) {
                    // Error al crear el proceso
                    perror("Fork failed");
                    exit(1);
                } else if (pid1 == 0) {
                    // Código del proceso hijo.
                    execl("/bin/ls", "ls", "-l", NULL);
                }
                wait(NULL);
                break;
            case 2:
            // gcc utils.c leeArchivo.c -o leeArchivo -I .h && ./leeArchivo
                system("clear");
                // Crear el primer proceso para la compilación
                pid1 = fork();
                if (pid1 < 0) {
                    // Error al crear el proceso
                    perror("Fork failed");
                    exit(1);
                } else if (pid1 == 0) {
                    // Código del proceso hijo: compilar los archivos con gcc
                    execl("/usr/bin/gcc", "gcc", "utils.c", "leeArchivo.c", "-o", "leeArchivo", "-I", ".h", NULL);
                    // Si execl falla
                    perror("execl failed");
                    exit(1);
                }

                // Esperar a que la compilación termine
                wait(NULL);

                // Crear el segundo proceso para ejecutar el programa compilado
                pid2 = fork();
                if (pid2 < 0) {
                    // Error al crear el proceso
                    perror("Fork failed");
                    exit(1);
                } else if (pid2 == 0) {
                    // Código del proceso hijo: ejecutar el programa compilado
                    execl("./leeArchivo", "./leeArchivo", NULL);
                    // Si execl falla
                    perror("execl failed");
                    exit(1);
                }
                // Esperar a que el programa compilado termine
                wait(NULL);
                break;
            case 3:
                system("clear");
                // Crear el primer proceso para la compilación
                pid1 = fork();
                if (pid1 < 0) {
                    // Error al crear el proceso
                    perror("Fork failed");
                    exit(1);
                } else if (pid1 == 0) {
                    // Código del proceso hijo: compilar los archivos con gcc
                    execl("/usr/bin/gcc", "gcc", "utils.c", "buscaRegistro.c", "-o", "buscaRegistro", "-I", ".h", NULL);
                    // Si execl falla
                    perror("execl failed");
                    exit(1);
                }

                // Esperar a que la compilación termine
                wait(NULL);

                // Crear el segundo proceso para ejecutar el programa compilado
                pid2 = fork();
                if (pid2 < 0) {
                    // Error al crear el proceso
                    perror("Fork failed");
                    exit(1);
                } else if (pid2 == 0) {
                    // Código del proceso hijo: ejecutar el programa compilado
                    execl("./buscaRegistro", "./buscaRegistro", NULL);
                    // Si execl falla
                    perror("execl failed");
                    exit(1);
                }
                // Esperar a que el programa compilado termine
                wait(NULL);
                break;
            default:
                printf("Opcion no valida\n");
                break;
        }
        printf("\nPresione Enter para continuar...");
        getchar();
        getchar();
        option = print_menu();
    }
    return 0;
}