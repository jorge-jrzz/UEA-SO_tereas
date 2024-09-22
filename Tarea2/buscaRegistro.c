#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/wait.h>

#include "utils.h"

#define MAX_LINE_LENGTH 1024
#define NUM_PRODUCTOS 10


int main() {
    // Crear una clave para la memoria compartida
    key_t key = ftok("shmfile", 65);

    // Calcular el tamaño de la memoria compartida
    int shmid = shmget(key, NUM_PRODUCTOS * MAX_LINE_LENGTH * sizeof(char), 0666|IPC_CREAT);

    // Adjuntar la memoria compartida al espacio de direcciones del proceso
    char (*arr)[MAX_LINE_LENGTH] = shmat(shmid, NULL, 0);

    // Crear un proceso hijo
    pid_t pid = fork();

    if (pid < 0) {
        // Error al crear el proceso
        perror("Fork failed");
        exit(1);

    } else if (pid == 0) {
        // Código del proceso hijo: Crear el arreglo leyencdo el archivo
        csv_to_array("wildfork.csv", arr);
        // Desapegar la memoria compartida
        shmdt(arr);

    } else {
        // Código del proceso padre
        wait(NULL);
        int i = 0;
        char *field;
        char input[5];

        // Ordenar el arreglo por el campo "codigo"
        order_by_codigo(arr, NUM_PRODUCTOS);

        // El usuario ingresa una clave
        printf("Ingrese la clave del producto (5 digitos): ");
        scanf("%s", input);
        int index = search_by_clave(arr, NUM_PRODUCTOS, input);

        if (index != -1) {
            printf("Producto encontrado:\n\n");
            // Codigo_producto, Nombre_producto, Categoria, Peso_kg, Precio, Fecha_vencimiento
            printf("%-15s\t %-15s\t%-15s\t%-15s\t%-15s\t%-15s\n", "Codigo_producto", "Nombre_producto", "Categoria", "Peso_kg", "Precio", "Fecha_vencimiento");
            // Separar los campos y formatear la salida con tabuladores
            field = strtok(arr[index], ",");
            while (field != NULL) {
                // Ajusta el ancho de los campos según sea necesario
                printf("%-15s\t", field);
                field = strtok(NULL, ",");
            }
            printf("\n");
        } else {
            printf("Producto no encontrado\n");
        }

        // Desapegar la memoria compartida
        shmdt(arr);

        // Eliminar el segmento de memoria compartida
        shmctl(shmid, IPC_RMID, NULL);
    }

    return 0;
}
