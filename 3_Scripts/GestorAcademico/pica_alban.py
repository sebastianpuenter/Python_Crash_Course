import pandas as pd
import unicodedata
import os

def eliminar_acentos_y_mayusculas(texto):
    """Función para quitar acentos y pasar a minúsculas para ordenar correctamente."""
    if not isinstance(texto, str):
        return ""
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    texto_sin_acentos = texto_normalizado.encode('ASCII', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower()

def consolidar_notas_en_un_archivo(lista_nombres_archivos, archivo_salida):
    # Definimos los nombres de las columnas tal como aparecen en la fila 7
    columna_alumnos = 'Nombre' 
    columna_nota = 'TECNOLOGÍA'
    
    # Creamos el escritor de Excel (ExcelWriter) para meter múltiples hojas
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        
        for nombre_base in lista_nombres_archivos:
            # Reconstruimos el nombre del archivo con su extensión
            archivo_entrada = f"{nombre_base}.xlsx"
            
            # Verificamos si el archivo realmente existe para que no se caiga el programa
            if not os.path.exists(archivo_entrada):
                print(f"⚠️ Advertencia: No se encontró el archivo '{archivo_entrada}'. Se saltará.")
                continue
            
            try:
                # 1. Leer el archivo (Fila 7 de Excel es el índice 6 en Python)
                df = pd.read_excel(archivo_entrada, header=6)
                
                # Validar que existan las columnas en este archivo específico
                if columna_alumnos not in df.columns or columna_nota not in df.columns:
                    print(f"❌ Error en '{archivo_entrada}': No se encontraron las columnas necesarias en la fila 7.")
                    continue
                
                # 2. Multiplicar la nota de tecnología por 2
                df[columna_nota] = df[columna_nota] * 2
                
                # 3. Crear columna temporal para ordenación ciega a acentos/mayúsculas
                df['nombre_busqueda'] = df[columna_alumnos].apply(eliminar_acentos_y_mayusculas)
                
                # 4. Ordenar alfabéticamente
                df_ordenado = df.sort_values(by='nombre_busqueda')
                
                # 5. Filtrar para dejar solo la columna del estudiante y tecnología
                df_final = df_ordenado[[columna_alumnos, columna_nota]]
                
                # 6. Guardar en el archivo consolidado. El nombre de la hoja será el nombre del archivo.
                # (Excel acepta un máximo de 31 caracteres para el nombre de las hojas; tus nombres miden ~14, así que perfecto)
                df_final.to_excel(writer, sheet_name=nombre_base, index=False)
                print(f"✅ Procesado con éxito: Hoja '{nombre_base}' añadida.")
                
            except Exception as e:
                print(f"❌ Ocurrió un error inesperado al procesar '{archivo_entrada}': {e}")

# --- CONFIGURACIÓN DE RUTAS Y EJECUCIÓN ---

# Lista exacta con los 11 nombres de tus archivos (sin el .xlsx)
archivos_colegio = [
    "PICA Per. 2 6-1", "PICA Per. 2 6-2", "PICA Per. 2 6-3", "PICA Per. 2 6-4",
    "PICA Per. 2 8-1", "PICA Per. 2 8-2",
    "PICA Per. 2 9-1", "PICA Per. 2 9-2",
    "PICA Per. 2 10-1", "PICA Per. 2 10-2",
    "PICA Per. 2 11-1"
]

archivo_consolidado_final = 'Consolidado_Tecnologia_Periodo2.xlsx'

print("Iniciando el procesamiento de los 11 archivos...\n")
consolidar_notas_en_un_archivo(archivos_colegio, archivo_consolidado_final)
print(f"\n¡Todo listo! Se ha creado el archivo único: '{archivo_consolidado_final}'")