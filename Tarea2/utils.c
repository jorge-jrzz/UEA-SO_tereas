#include "utils.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LENGTH 1024
#define NUM_PRODUCTOS 10

void order_by_codigo(char arr[][MAX_LINE_LENGTH], int num_productos) {
    char temp[MAX_LINE_LENGTH];

    for (int i = 1; i < num_productos - 1; i++) {
        for (int j = i + 1; j < num_productos; j++) {
            // Comparar los códigos de producto (los primeros campos de cada cadena)
            if (strcmp(arr[i], arr[j]) > 0) {
                // Intercambiar las filas si están en el orden incorrecto
                strcpy(temp, arr[i]);
                strcpy(arr[i], arr[j]);
                strcpy(arr[j], temp);
            }
        }
    }
}

int csv_to_array(char *file_path, char arr[][MAX_LINE_LENGTH]) {
    FILE *fp;
    char buffer[MAX_LINE_LENGTH];
    char *field;
    int i = 0;

    // Abrir el archivo en modo lectura
    fp = fopen(file_path, "r");
    if (fp == NULL) {
        perror("Error al abrir el archivo\n");
        return 1;
    }
    
    // Leer el archivo línea por línea
    while (fgets(buffer, MAX_LINE_LENGTH, fp) != NULL) {
        // Eliminar el salto de línea al final de la línea
        buffer[strcspn(buffer, "\n")] = 0;
        // agregar los datos al arreglo
        strcpy(arr[i], buffer);
        i++;
    }
    // Cerrar el archivo
    fclose(fp);
    return 0;
}

int search_by_clave(char arr[][MAX_LINE_LENGTH], int num_productos, char *clave) {
    int izquierda = 0;
    int derecha = num_productos - 1;

    // Crear una copia del arreglo para no modificar el original
    char arr_copy[num_productos][MAX_LINE_LENGTH];
    memcpy(arr_copy, arr, num_productos * MAX_LINE_LENGTH);

    while (izquierda <= derecha) {
        int medio = izquierda + (derecha - izquierda) / 2;

        int comparacion = strcmp(clave, strtok(arr_copy[medio], ","));

        if (comparacion == 0) {
            return medio;
        } else if (comparacion < 0) {
            derecha = medio - 1;
        } else {
            izquierda = medio + 1;
        }
    }

    return -1; // Clave no encontrada
}
