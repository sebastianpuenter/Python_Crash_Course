""""
Cambios:
1. Se mejora el gráfico con colores en las barras y en el fondo de acuerdo a los niveles.
2. Se agrega la opción de borrar todos los cursos.
3. Se ordenan los cursos ingresados en orden alfabético.
4. Se agrega la opción de datos del estudiante (nombre, grado, jornada)
5. Se agrega la opción de generar informe en pdf

Futuro:
"""

""""
@author Sebastián PuenteR, jun 2026
"""
import os
import pandas as pd
import random
import matplotlib.pyplot as plt
import termplotlib as tpl
# para quitar tildes y poder ordenar alfabeticamente una lista
from text_unidecode import unidecode

# Módulos para crear pdfs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


# Lista vacia para acumular los registros
registros = []


# -----------------------------------------------------------------------------
# Agregar Cursos
# -----------------------------------------------------------------------------
def agregar_curso() -> None:
    """Se crea un curso con notas por periodo, cáculo del promedio,
    nivel de desempeño, resultado de aprobación. Posteriormente se
    guarda en una lista y un dataframe
    """

    global escala

    print('\n=== Ingresar Curso ===\n')
    notas = []
    nombre_curso = input('Ingrese nombre del curso: ').strip().lower()
    #NumPeriodos = int(input('Número Periodos: '))
    numero_periodos = pedir_numero('Número Periodos (máx 10): ', 1, 10)

    # Se capturan las notas para cada periodo y se guardan en la lista notas
    print('\nDigitar Notas...')
    for n in range(1, numero_periodos+1):
        nota = pedir_numero(f'Digita la nota del Periodo {n} (1-{escala}): ', 1, escala, permitir_float=True)
        notas.append(nota)
    
    # Cálculos
    promedio_curso = round(sum(notas) / len(notas), 1)
    # Niveles: Superior, Alto, Básico, Bajo
    nivel_curso = nivel_desempeño(promedio_curso, escala)
    # Se maneja un mínimo de aprobación del 60%
    aprobacion = ver_aprobacion(promedio_curso, escala*0.6)

    # Se agrega el registro como un diccionario dentro de la lista Registros
    nuevo_registro = {
        'Nombre': nombre_curso,
        'Periodos': numero_periodos,
        'Nota Periodos': notas,
        'Escala': escala,
        'Promedio': promedio_curso,
        'Aprobación': aprobacion,
        'Nivel': nivel_curso
    }
    registros.append(nuevo_registro)

    # Mostrar datos registrados
    print('\n=== Datos Registrados ===\n')
    print(f'Nombre Curso: {nombre_curso.title()}')
    print(f'Número Periodos: {numero_periodos}')
    print(f'Notas Registradas: {notas}')
    print(f'Escala: 1 - {escala}\n')
    print(f'- Promedio Curso: {promedio_curso}')
    print(f'- Aprobación: {aprobacion.title()}')
    print(f'- Nivel Desempeño: {nivel_curso.title()}')

    # Guardar info en Dataframe
    global df_cursos
    df_curso_nuevo = pd.DataFrame([nuevo_registro])
    df_cursos = pd.concat([df_cursos, df_curso_nuevo], ignore_index=True)

    input('\nPulsa Enter para continuar...')
    os.system('clear')


# -----------------------------------------------------------------------------
# Borrar Cursos
# -----------------------------------------------------------------------------
def borrar_cursos() -> None:
    """Borra curso tanto en la lista Registro como en el Dataframe"""

    global df_cursos

    print('\n=== Borrar Cursos ===\n')

    if len(registros) == 0:
        print('Sin cursos para borrar')

    else:
        print('1. Borrar un Curso (recomendado).')
        print('2. Borrar Todos los Cursos.')
        print('3. Salir.')
        opcion_borrar = pedir_numero('Opción: ',1,3)
        
        # Borrar un Curso
        if opcion_borrar == 1:
            posicion_curso = pedir_numero('Número de curso a borrar (0 -> salir): ', 0, len(registros))

            # Si no se elige 0 que es salir del menú borrar curso
            if posicion_curso != 0:
                indice_curso = posicion_curso - 1
                print(f'\nCurso a borrar: {posicion_curso}. {registros[indice_curso]['Nombre'].title()}')
                # Borrar curso en la lista Registros
                del registros[indice_curso]
                # Borrar curso en el Dataframe
                df_cursos.drop(indice_curso, inplace=True)
                df_cursos.reset_index(drop=True, inplace=True)
                print('Curso borrado.')
            else:
                os.system('clear')
                return
        
        # Borrar todos los cursos
        elif opcion_borrar == 2:
            # Borramos todos los registros en la listab de registros
            registros.clear()
            # Borramos todo el contenido del Dataframe
            df_cursos = df_cursos.iloc[0:0]
            print('Todos los cursos se han borrado.')

        elif opcion_borrar == 3:
            os.system('clear')
            return
    
    input('\nPulsa Enter para continuar...')
    os.system('clear')


# -----------------------------------------------------------------------------
# Ordenar Datos Cursos
# -----------------------------------------------------------------------------
def ordenar_datos():
    """
    Ordenar alfabéticamente registro y dataframe con los cursos ingresados
    """

    # Ordenar el registro alfabéticamente
    registros.sort(key=lambda x: unidecode(x['Nombre']))

    # Ordenar cursos, en el dataframe, por orden alafabético
    global df_cursos    
    df_cursos['temp'] = df_cursos['Nombre'].apply(lambda x: unidecode(x))
    df_cursos = (
        df_cursos.sort_values(by='temp')
        .drop(columns=['temp'])
        .reset_index(drop=True)
    )


# -----------------------------------------------------------------------------
# Ver Cursos Registrados
# -----------------------------------------------------------------------------
def ver_registros() -> None:
    """Imprime un listado de los cursos que se han registrado"""

    print(f'\nCursos registrados: {len(registros)}')
    print('----------------------')
    
    # Imprimir cursos
    n = 1
    for registro in registros:
        print(f'{n}. {registro['Nombre'].title()}: {registro['Promedio']}, {registro['Nivel'].title()}, {registro['Aprobación'].title()}')
        n+=1


# -----------------------------------------------------------------------------
# Ver Dataframe
# -----------------------------------------------------------------------------
def ver_dataframe() -> None:
    """Imprime los cursos registrados guardados en un Dataframe"""

    # Imprimir dataframe con los cursos
    print('\n=== Cursos Registrados ===\n')
    if len(registros) == 0:
        print('Sin cursos registrados.')
    else:
        print(df_cursos)
        print(f'\nTotal Cursos Registrados: {len(df_cursos)}')


    input('\nPulsa Enter para continuar...')
    os.system('clear')


# -----------------------------------------------------------------------------
# Nivel de Desempeño
# -----------------------------------------------------------------------------
def nivel_desempeño(promedio: float, nota_max: int):
    """Devuelve el nivel de desempeño en una escala de 1 a max"""

    promedio_normalizado = promedio/nota_max

    if promedio_normalizado >=  9/10:
        return 'superior'
    elif promedio_normalizado >= 8/10:
        return 'alto'
    elif promedio_normalizado >= 6/10:
        return 'básico'
    else:
        return 'bajo'


# -----------------------------------------------------------------------------
# Revisar Aprobación
# -----------------------------------------------------------------------------
def ver_aprobacion(promedio: float, nota_min_aprobacion: float):
    """Devuelve si el curso es aprobado o reprobado de acuerdo a la notamin de aprobación"""

    if promedio >= nota_min_aprobacion:
        return 'aprobado'
    else:
        return 'reprobado'


# -----------------------------------------------------------------------------
# Inicializar Dataframe
# -----------------------------------------------------------------------------
def iniciar_dataframe():
    """Función que crea el DataFrame inicial vacio donde se iran guardando los cursos"""
    
    global df_cursos
    df_cursos = pd.DataFrame(columns=["Nombre", "Periodos", "Nota Periodos", "Escala", "Promedio", "Aprobación", "Nivel"])


# -----------------------------------------------------------------------------
# Graficar Cursos
# -----------------------------------------------------------------------------
def menu_graficar():
    """"Se grafica el promedio de los cursos registrado tanto en la terminal
    como en una figura con formato.
    """

    global escala

    print('\n=== Gráfica Promedios ===\n')

    if len(registros) == 0:
        print('Sin datos para graficar')
    
    else:
        nombre_cursos: list = []; promedio_cursos: list = []; niveles_cursos = []
        # se obtiene lista de nombres de cursos, promedios y nivel de desempeño
        for registro in registros:
            nombre_cursos.append(registro['Nombre'].title())
            promedio_cursos.append(registro['Promedio'])
            niveles_cursos.append(registro['Nivel'])
    
        # === Crear la figura para la terminal ===
        fig = tpl.figure()
        # Dibujar el gráfico de barras horizontales
        fig.barh(promedio_cursos, labels=nombre_cursos, force_ascii=False)
        # Mostrar el gráfico en la consola
        fig.show()

        # === Graficar con Matplotlib ===
        grafica_cursos(nombre_cursos, promedio_cursos, niveles_cursos, guardar=False)

    input('\nPulsa Enter para continuar...')
    os.system('clear')


# -----------------------------------------------------------------------------
# Gráfica de los Cursos
# -----------------------------------------------------------------------------
def grafica_cursos(nombres, promedios, niveles, guardar=True):
    """Se genera la grafica de los cursos en barras
    y se retorna la ruta de la gráfica si guardar=True
    """
        
    promedio_general = sum(promedios) / len(promedios)
        
    # Clasificar por 4 niveles con la paleta oficial de UNITED COLORS OF BENETTON
    colores_barras = []
    for nivel in niveles:
        if nivel == 'bajo':
            colores_barras.append('#E1060D')      # Bajo (Rojo Benetton)
        elif nivel == 'básico':
            colores_barras.append('#FF6600')      # Básico (Naranja)
        elif nivel == 'alto':
            colores_barras.append('#FFDD00')      # Alto (Amarillo Cítrico)
        else:
            colores_barras.append('#008860')      # Superior (Verde Benetton Oficial)

    # Crear gráfico de barras
    plt.figure(figsize=(6.5, 4.0), dpi=300)
    barras = plt.bar(nombres, promedios, color=colores_barras, zorder=2)

    # Agregar el promedio general como línea horizontal
    plt.axhline(y=promedio_general, color='red', linestyle='--', linewidth=1.5,
                label=f'Promedio General ({promedio_general:.1f})', zorder=3)
        
    # PINTAR EL FONDO CON TONOS PASTEL EXTRAÍDOS DE LA PALETA (Transparencia suave)
    plt.axhspan(0, escala*0.6, facecolor='#E1060D', alpha=0.1, label=f'Bajo (0.0 - {escala*0.6-0.1})')
    plt.axhspan(escala*0.6, escala*0.8, facecolor='#FF6600', alpha=0.1, label=f'Básico ({escala*0.6} - {escala*0.8-0.1})')
    plt.axhspan(escala*0.8, escala*0.9, facecolor='#FFDD00', alpha=0.1, label=f'Alto ({escala*0.8} - {escala*0.9-0.1})')
    plt.axhspan(escala*0.9, escala, facecolor='#008860', alpha=0.1, label=f'Superior ({escala*0.9} - {escala})')

    # Personalizar el gráfico
    titulo_grafico = f'Promedio de Cursos: {mostrar_estudiante()[1]}'
    #plt.title(titulo_grafico, fontsize=14, fontweight='bold')
    plt.title(titulo_grafico, fontsize=11)
    plt.xlabel('Cursos', fontsize=11)
    plt.ylabel('Promedio', fontsize=11)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, escala+1) # Ajusta este límite según la escala de tus notas (ej. 100 o 5)
    plt.legend()

    # Mostrar valores encima de cada barra
    for bar in barras:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2, yval + 0.2, round(yval, 2),
            ha='center', va='bottom', fontsize=8
        )
        
    # Ajustar diseño y mostrar
    plt.tight_layout()
    #plt.grid()

    # Guardar imagen en archivo
    if guardar:
        nombre_sin_espacios = mostrar_estudiante()[1].replace(' ', '_')
        ruta_grafica = f'grafica_notas_{nombre_sin_espacios}.png'
        plt.savefig(ruta_grafica, bbox_inches='tight', dpi=300)
        plt.close()
        return ruta_grafica
    else:
        plt.show()
        
    plt.close()


# -----------------------------------------------------------------------------
# Establecer Escala de las Notas
# -----------------------------------------------------------------------------
def configurar_escala():
    """se establece la escala en la que se ingresa las notas"""

    global escala

    if len(registros) == 0:
        print('\n=== Configurar Escala ===\n')
        escala = pedir_numero('Valor máximo de notas (ej: 5 ó 10): ', 1, 100)
        #os.system('clear')
        #mostrarMenu()


# -----------------------------------------------------------------------------
# Menú Datos Estudiante
# -----------------------------------------------------------------------------
def menu_estudiantes():

    print('\n=== Datos Estudiante ===\n')
    print(mostrar_estudiante()[0])
    print('\n1. Editar')
    print('2. Salir')
    opcion_estudiante = pedir_numero('Opción: ',1,2)

    if opcion_estudiante == 1:
        pedir_datos_estudiante()
    elif opcion_estudiante == 2:
        os.system('clear')
        return

    #input('\nPulsa Enter para continuar...')
    os.system('clear')


# -----------------------------------------------------------------------------
# Pedir Datos Estudiante
# -----------------------------------------------------------------------------
def pedir_datos_estudiante():

    global estudiante
    jornadas = ['M', 'T', 'N']
    estudiante_nombres = input('\nNombre: ').strip()
    estudiante_apellidos = input('Apellidos: ').strip()
    estudiante_grado = pedir_numero('Grado: ',0,11)
    estudiante_grupo = pedir_numero('Grupo: ',1,10)
    num_jornada = pedir_numero('Jornada (1.Mañana, 2.Tarde, 3.Noct): ',1,3)
    estudiante_jornada = jornadas[num_jornada-1]

    # Diccionario con datos del estudiante
    estudiante = {
        'Nombres': estudiante_nombres,
        'Apellidos': estudiante_apellidos,
        'Grado': estudiante_grado,
        'Grupo': estudiante_grupo,
        'Jornada': estudiante_jornada
    }


# -----------------------------------------------------------------------------
# Hay Estudiante?
# -----------------------------------------------------------------------------
def hay_estudiante() -> bool:

    global estudiante
    if len(estudiante) == 0:
        return False
    else:
        return True


# -----------------------------------------------------------------------------
# Mostrar Datos Estudiantes
# -----------------------------------------------------------------------------
def mostrar_estudiante() -> str:

    global estudiante

    if hay_estudiante():
        info_estudiante = (
            f'{estudiante['Nombres'].title()} {estudiante['Apellidos'].title()} '
            f'{estudiante["Grado"]}-{estudiante["Grupo"]} '
            f'J{estudiante["Jornada"].title()}'
        )
        nombre_corto = (
            f'{estudiante["Nombres"].split()[0].title()} '
            f'{estudiante["Apellidos"].split()[0].title()} '
            f'{estudiante["Grado"]}-{estudiante["Grupo"]} '
            f'J{estudiante["Jornada"].title()}'
        )

    else:
        info_estudiante = 'Sin datos Estudiante'
        nombre_corto = ''
    
    #print(f'Estudiante: {info_estudiante}')
    return info_estudiante, nombre_corto


# -----------------------------------------------------------------------------
# Pedir Número
# -----------------------------------------------------------------------------
def pedir_numero(mensaje: str, num_min: int | float, num_max: int | float, permitir_float: bool=False):
    """Función que captura un número del teclado en un rango fijo (min - max),
    ya sea entero o float de acuerdo al respectivo parámetro
    """

    while True:

        entrada = input(mensaje)
        try:
            # Conversión según parámetro
            if permitir_float:
                numero = float(entrada)
            else:
                numero = int(entrada)

            # Validar rango
            if num_min <= numero <= num_max:
                return numero  # Retorna el número y termina la función
            else:
                print(f'❌ Error: El número debe estar entre {num_min} y {num_max}.\n')

        except ValueError:
            if permitir_float:
                print('❌ Error: Ingresa un número válido (entero o decimal).\n')
            else:
                print('❌ Error: Por favor, ingresa solo números enteros.\n')


# -----------------------------------------------------------------------------
# Mostrar Menú Principal
# -----------------------------------------------------------------------------
def mostrar_menu():
    """Imprime las opciones disponibles en la pantalla y muestra los cursos registrados"""
    
    print("\n" + "="*25)
    print("      MENÚ PRINCIPAL      ")
    print("="*25)
    print("1. Ingresar Curso")
    print("2. Ver Registros")
    print("3. Datos Estudiantes")
    print("4. Graficar")
    print("5. Generar Informe")
    print("6. Borrar Cursos")
    print("7. Salir")
    print("="*25)


# -----------------------------------------------------------------------------
# Generar Informe
# -----------------------------------------------------------------------------
def generar_informe():

    if len(registros) == 0:
        print('\nSin cursos registrados')
        input('\nPulsa Enter para continuar...')
        os.system('clear')
        return
    
    # Información necesaria para el informe
    # se obtiene lista de nombres de cursos, promedios y nivel de desempeño
    nombre_cursos: list = []; promedio_cursos: list = []
    nivel_cursos: list = []; aprobacion_cursos : list = []
    notas_cursos: list = []
    for registro in registros:
        nombre_cursos.append(registro['Nombre'].title())
        promedio_cursos.append(registro['Promedio'])
        notas_cursos.append(registro['Nota Periodos'])
        nivel_cursos.append(registro['Nivel'])
        aprobacion_cursos.append(registro['Aprobación'])
    total_cursos = len(registros)
    total_cursos_aprobados = aprobacion_cursos.count('aprobado')
    total_cursos_reprobados = aprobacion_cursos.count('reprobado')
    
    # Crear el documento PDF
    pdf_path = 'informe_notas.pdf'
    doc = SimpleDocTemplate(
        pdf_path, pagesize=letter,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )

    # Estilos
    estilos = getSampleStyleSheet()
    titulo_estilo = ParagraphStyle('Title', parent=estilos['Heading1'])
    subtitulo_estilo = ParagraphStyle('Subtitle', parent=estilos['Heading2'], spaceBefore=4)
    texto_estilo = ParagraphStyle('Normal', parent=estilos['Normal'], fontSize=12, spaceAfter=8)
    infocurso_estilo = ParagraphStyle('curso', parent=estilos['Normal'], fontSize=11, spaceAfter=6)
    creditos_estilo = ParagraphStyle('creditos', parent=estilos['Normal'], fontSize=8)
    
    # Elementos del PDF
    elementos = []
    
    # Título
    elementos.append(Paragraph("Informe de Rendimiento Académico", titulo_estilo))

    # Datos Esudiante
    elementos.append(Paragraph(f'Estudiante: {mostrar_estudiante()[0]}', subtitulo_estilo))
    elementos.append(Spacer(1, 10))

    # Texto con información de todos los cursos
    elementos.append(Paragraph("A continuación, se presenta el detalle de las calificaciones por curso:", texto_estilo))
    elementos.append(Spacer(1, 10))
    
    for n in range(0, total_cursos):
        if aprobacion_cursos[n] == 'aprobado':
            color = 'green'
        else:
            color = 'red'
        info_curso = (
            f'<b>{n+1}. <font color={color}>{nombre_cursos[n].title()}</font>: </b>'
            f'Promedio: {promedio_cursos[n]}, '
            f'{aprobacion_cursos[n].title()}-'
            f'{nivel_cursos[n].title()}. '
            f'Nota Periodos: {notas_cursos[n]}' 
        )
        elementos.append(Paragraph(info_curso, infocurso_estilo))
    
    linea_totales = (
        f'<font color=gray><i>Total Cursos: {total_cursos}, '
        f'Total Cursos Aprobados: {total_cursos_aprobados}, '
        f'Total Cursos Reprobados: {total_cursos_reprobados}</i></font>'
    )
    elementos.append(Spacer(1,8))
    elementos.append(Paragraph(linea_totales, infocurso_estilo))

    # Insertar gráfica
    elementos.append(Spacer(1, 20))
    ruta_grafica = grafica_cursos(nombre_cursos, promedio_cursos, nivel_cursos)
    elementos.append(Image(ruta_grafica, width=500, height=300))

    # Créditos
    elementos.append(Spacer(1,10))
    creditos = 'Creado por: Sebas PuenteR, 2026 :)'
    elementos.append(Paragraph(creditos, creditos_estilo))

    # Construir PDF
    doc.build(elementos)
    print("¡PDF generado con éxito!")

    # Eliminar la imagen guardada
    if os.path.exists(ruta_grafica):
        os.remove(ruta_grafica)

    input('\nPulsa Enter para continuar...')
    os.system('clear')


# ======================================
def degly():
    """Función para pruebas del programa"""

    global escala
    registros.clear()

    print('\nCrear Cursos de Prueba')
    escala = int(input('Define escala: '))

    cursos_prueba = ['tecnología', 'física', 'química', 'ética', 'ciencias', 'ártes', 'español']

    for n in range(0, len(cursos_prueba)):
        
        notas_curso_prueba = []
        for i in range(4): # 4 notas (4 periodos)
            nota_aleatoria = random.uniform(2.0, escala)
            nota_redondeada = round(nota_aleatoria, 1)  # Deja un solo decimal
            notas_curso_prueba.append(nota_redondeada)
        
        promedio_prueba = sum(notas_curso_prueba) / len(notas_curso_prueba)

        reg_aux = {
            'Nombre': cursos_prueba[n],
            'Periodos': 4,
            'Nota Periodos': notas_curso_prueba,
            'Escala': escala,
            'Promedio': round(promedio_prueba,1),
            'Aprobación': ver_aprobacion(promedio_prueba, escala*0.6),
            'Nivel': nivel_desempeño(promedio_prueba, escala)
        }
        registros.append(reg_aux)

    # Ordenar el registro alfabéticamente
    registros.sort(key=lambda x: unidecode(x['Nombre']))
    global df_cursos
    df_cursos = pd.DataFrame(registros)
    
    os.system('clear')
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Inicio Programa
# -----------------------------------------------------------------------------
def inicio():

    iniciar_dataframe()
    global estudiante
    estudiante = {}

    while True:

        mostrar_menu()
        print('Estudiante:', mostrar_estudiante()[0])
        ordenar_datos()
        ver_registros()
        
        opcion_menu = input('\nDigite su opción del menú: ').strip()

        match opcion_menu:
            case '1':
                configurar_escala()
                agregar_curso()
            case '2':
                ver_dataframe()
            case '3':
                menu_estudiantes()
            case '4':
                menu_graficar()
            case '5':
                generar_informe()
            case '6':
                borrar_cursos()
            case '7':
                print('\nHasta Pronto!...')
                print('= Sebas PuenteR =\n')
                break
            case 'degly':
                degly()
            case _:
                print("Opción no válida")  # The '_' acts as a default 'else' case
                os.system('clear')

# Punto de entrada del script
if __name__ == "__main__":
    os.system('clear')
    inicio()