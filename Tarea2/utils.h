// mi_biblioteca.h
#ifndef UTILS_H
#define UTILS_H

#define MAX_LINE_LENGTH 1024

void order_by_codigo(char arr[][MAX_LINE_LENGTH], int num_productos);
int csv_to_array(char *file_path, char arr[][MAX_LINE_LENGTH]);
int search_by_clave(char arr[][MAX_LINE_LENGTH], int num_productos, char *clave);

#endif
