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

def consolidar_todas_las_notas(lista_nombres_archivos, archivo_salida):
    columna_alumnos = 'Nombre' 
    
    # Creamos el escritor de Excel para consolidar las pestañas
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        
        for nombre_base in lista_nombres_archivos:
            archivo_entrada = f"{nombre_base}.xlsx"
            
            if not os.path.exists(archivo_entrada):
                print(f"⚠️ Advertencia: No se encontró el archivo '{archivo_entrada}'. Se saltará.")
                continue
            
            try:
                # 1. Leer el archivo desde la fila 7 (índice 6 en Python)
                df = pd.read_excel(archivo_entrada, header=6)
                
                # Validar que al menos exista la columna del estudiante para poder ordenar
                if columna_alumnos not in df.columns:
                    print(f"❌ Error en '{archivo_entrada}': No se encontró la columna '{columna_alumnos}' en la fila 7.")
                    continue
                
                # 2. Crear columna temporal para ordenación
                df['nombre_busqueda'] = df[columna_alumnos].apply(eliminar_acentos_y_mayusculas)
                
                # 3. Ordenar alfabéticamente
                df_ordenado = df.sort_values(by='nombre_busqueda')
                
                # 4. Eliminar la columna temporal de búsqueda
                df_final = df_ordenado.drop(columns=['nombre_busqueda'])
                
                # 5. Multiplicar por 2 TODAS las columnas que sean numéricas (excepto si hay un ID numérico)
                # Esto procesará Tecnología, Matemáticas, Ciencias, etc., de forma automática.
                for columna in df_final.columns:
                    if columna != columna_alumnos and pd.api.types.is_numeric_dtype(df_final[columna]):
                        df_final[columna] = df_final[columna] * 2
                
                # 6. Guardar la información completa en su respectiva pestaña
                df_final.to_excel(writer, sheet_name=nombre_base, index=False)
                print(f"✅ Procesado con éxito: Hoja '{nombre_base}' creada con todas sus columnas.")
                
            except Exception as e:
                print(f"❌ Ocurrió un error inesperado al procesar '{archivo_entrada}': {e}")

# --- CONFIGURACIÓN DE RUTAS Y EJECUCIÓN ---

archivos_colegio = [
    "PICA Per. 2 6-1", "PICA Per. 2 6-2", "PICA Per. 2 6-3", "PICA Per. 2 6-4",
    "PICA Per. 2 7-1", "PICA Per. 2 7-2", "PICA Per. 2 7-3", 
    "PICA Per. 2 8-1", "PICA Per. 2 8-2",
    "PICA Per. 2 9-1", "PICA Per. 2 9-2",
    "PICA Per. 2 10-1", "PICA Per. 2 10-2",
    "PICA Per. 2 11-1"
]

archivo_consolidado_final = 'Consolidado_Notas_Multiplicadas.xlsx'

print("Iniciando el procesamiento de los 11 archivos (Modo: Todas las columnas)...\n")
consolidar_todas_las_notas(archivos_colegio, archivo_consolidado_final)
print(f"\n¡Todo listo! Archivo completo generado en: '{archivo_consolidado_final}'")