"""
Versión v7.1 - Enterprise Multi-Estudiante (Persistencia de Perfil Corregida)
Características:
1. Multi-Estudiante Real: Administra múltiples estudiantes de forma independiente.
2. Persistencia de Perfil Perfecta: Guarda los datos completos del estudiante (Nombres, 
   Apellidos, Grado, Grupo, Jornada) dentro del mismo archivo CSV sin perder información.
3. Colores Condicionales en PDF: El nombre del curso aparece Verde si está aprobado o Rojo si está reprobado.
4. Gráfica Fiel a v5: Incluye línea de promedio general, texto sobre cada barra y rotación a 45°.
5. Menú Completo: Opción de Borrar Cursos (Opción 6) y Panel Estadístico (Opción 7).
"""

import os
import random
import ast
import matplotlib.pyplot as plt
import pandas as pd
import termplotlib as tpl
from text_unidecode import unidecode

# Módulos avanzados para crear PDFs con Tablas estilizadas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle


class GestorAcademico:

    def __init__(self):
        """Inicializa los componentes del sistema y la carpeta de almacenamiento"""
        self.carpeta_datos = "datos_estudiantes"
        self.archivo_datos = ""
        self.registros = []
        self.escala = 5.0
        self.estudiante = {}
        self.df_cursos = pd.DataFrame(columns=['Nombre', 'Periodos', 'Nota Periodos', 'Escala', 'Promedio', 'Aprobación', 'Nivel'])
        
        # Crear la carpeta de datos si no existe
        if not os.path.exists(self.carpeta_datos):
            os.makedirs(self.carpeta_datos)

    def limpiar_pantalla(self) -> None:
        """Limpia la consola según el sistema operativo"""
        os.system('cls' if os.name == 'nt' else 'clear')

    # -----------------------------------------------------------------------------
    # Gestión de Múltiples Estudiantes (Persistencia de Datos Corregida)
    # -----------------------------------------------------------------------------
    def menu_seleccion_estudiante(self) -> bool:
        """Menú inicial para gestionar a qué estudiante se desea ingresar"""
        while True:
            print("\n" + "="*30 + "\n   SISTEMA MULTI-ESTUDIANTE\n" + "="*30)
            print("1. Seleccionar Estudiante Existente")
            print("2. Registrar Nuevo Estudiante")
            print("3. Salir del Programa")
            print("="*30)
            
            opcion = input("Opción: ").strip()
            if opcion == "1":
                if self.listar_y_cargar_estudiante():
                    return True
            elif opcion == "2":
                self.pedir_datos_estudiante(es_nuevo=True)
                return True
            elif opcion == "3":
                print("\n¡Cierre de sistema exitoso!\n")
                return False
            else:
                self.limpiar_pantalla()

    def pedir_datos_estudiante(self, es_nuevo=False) -> None:
        """Solicita los datos completos de identificación y académicos del estudiante"""
        print('\n=== Datos de Identificación del Estudiante ===\n')
        jornadas = ["M", "T", "N"]
        
        if es_nuevo:
            id_estudiante = input("Número de Documento / ID Único: ").strip()
            while not id_estudiante:
                id_estudiante = input("El ID es obligatorio: ").strip()
        else:
            id_estudiante = self.estudiante.get("ID", "anonimo")

        nombres = input("Nombres: ").strip()
        apellidos = input("Apellidos: ").strip()
        grado = self.pedir_numero("Grado (0-11): ", 0, 11)
        grupo = self.pedir_numero("Grupo (1-10): ", 1, 10)
        jornada = jornadas[self.pedir_numero("Jornada (1.Mañana, 2.Tarde, 3.Noct): ", 1, 3) - 1]
        
        self.estudiante = {
            "ID": id_estudiante, "Nombres": nombres, "Apellidos": apellidos,
            "Grado": grado, "Grupo": grupo, "Jornada": jornada
        }
        
        # Definir la ruta única del archivo CSV
        nombre_archivo = f"{id_estudiante}_{unidecode(nombres.lower()).replace(' ', '_')}.csv"
        self.archivo_datos = os.path.join(self.carpeta_datos, nombre_archivo)
        
        if es_nuevo:
            self.registros = []
            self.escala = 5.0
            self.df_cursos = pd.DataFrame(columns=['Nombre', 'Periodos', 'Nota Periodos', 'Escala', 'Promedio', 'Aprobación', 'Nivel'])
            self.guardar_datos_csv()
            print(f"\n✅ Estudiante {nombres.title()} registrado y asignado correctamente.")
            input('Presiona Enter para ir al panel principal...')
        else:
            # Si modificamos los datos de un estudiante existente, guardamos de inmediato para actualizar el CSV
            self.guardar_datos_csv()
        
        self.limpiar_pantalla()

    def listar_y_cargar_estudiante(self) -> bool:
        """Busca los archivos CSV en la carpeta y permite seleccionar uno"""
        archivos = [f for f in os.listdir(self.carpeta_datos) if f.endswith('.csv')]
        
        if not archivos:
            print("\n❌ No hay estudiantes registrados en el sistema todavía.")
            input('\nPulsa Enter para volver...')
            self.limpiar_pantalla()
            return False
        
        print('\n=== Lista de Estudiantes Registrados ===\n')
        # Para mostrar la lista inicial de forma estética, leemos rápidamente el interior de cada CSV
        for idx, archivo in enumerate(archivos, 1):
            try:
                df_temp = pd.read_csv(os.path.join(self.carpeta_datos, archivo))
                if not df_temp.empty and '_Estudiante_Nombres' in df_temp.columns:
                    nom = str(df_temp.iloc[0]['_Estudiante_Nombres']).title()
                    ape = str(df_temp.iloc[0]['_Estudiante_Apellidos']).title()
                    ident = str(df_temp.iloc[0]['_Estudiante_ID'])
                    print(f"{idx}. [{ident}] {nom} {ape}")
                else:
                    nombre_legible = archivo.replace('.csv', '').replace('_', ' ').title()
                    print(f"{idx}. {nombre_legible} (Archivo vacío)")
            except:
                nombre_legible = archivo.replace('.csv', '').replace('_', ' ').title()
                print(f"{idx}. {nombre_legible}")
            
        print(f"{len(archivos) + 1}. Volver atrás")
        
        opcion = self.pedir_numero("\nSeleccione el estudiante: ", 1, len(archivos) + 1)
        if opcion == len(archivos) + 1:
            self.limpiar_pantalla()
            return False
            
        self.archivo_datos = os.path.join(self.carpeta_datos, archivos[opcion - 1])
        self.cargar_datos_csv(archivos[opcion - 1])
        return True

    def guardar_datos_csv(self) -> None:
        """Guarda de forma persistente las notas junto con TODO el perfil del estudiante en el CSV"""
        if self.archivo_datos:
            try:
                # Si el DataFrame de cursos está vacío, creamos una fila temporal vacía para que no se pierda el perfil
                df_guardar = self.df_cursos.copy()
                if df_guardar.empty:
                    df_guardar = pd.DataFrame([{
                        'Nombre': '---', 'Periodos': 0, 'Nota Periodos': '[]', 
                        'Escala': self.escala, 'Promedio': 0.0, 'Aprobación': '---', 'Nivel': '---'
                    }])

                # Inyectamos de forma segura los metadatos completos en columnas dedicadas
                df_guardar['_Estudiante_ID'] = self.estudiante.get('ID', '')
                df_guardar['_Estudiante_Nombres'] = self.estudiante.get('Nombres', '')
                df_guardar['_Estudiante_Apellidos'] = self.estudiante.get('Apellidos', '')
                df_guardar['_Estudiante_Grado'] = self.estudiante.get('Grado', 0)
                df_guardar['_Estudiante_Grupo'] = self.estudiante.get('Grupo', 1)
                df_guardar['_Estudiante_Jornada'] = self.estudiante.get('Jornada', 'M')
                
                df_guardar.to_csv(self.archivo_datos, index=False)
                print(f"💾 ¡Expediente completo guardado para {self.estudiante['Nombres'].title()}!")
            except Exception as e:
                print(f"❌ Error al guardar los datos: {e}")

    def cargar_datos_csv(self, nombre_archivo: str) -> None:
        """Reconstruye con precisión el perfil completo del estudiante desde las columnas ocultas del CSV"""
        ruta_completa = os.path.join(self.carpeta_datos, nombre_archivo)
        if os.path.exists(ruta_completa):
            try:
                df_temporal = pd.read_csv(ruta_completa)
                
                if not df_temporal.empty and '_Estudiante_ID' in df_temporal.columns:
                    # 1. Extraemos toda la información original del estudiante de la primera fila
                    self.estudiante = {
                        "ID": str(df_temporal.iloc[0]['_Estudiante_ID']),
                        "Nombres": str(df_temporal.iloc[0]['_Estudiante_Nombres']),
                        "Apellidos": str(df_temporal.iloc[0]['_Estudiante_Apellidos']),
                        "Grado": int(df_temporal.iloc[0]['_Estudiante_Grado']),
                        "Grupo": int(df_temporal.iloc[0]['_Estudiante_Grupo']),
                        "Jornada": str(df_temporal.iloc[0]['_Estudiante_Jornada'])
                    }
                    
                    # 2. Separamos las columnas del estudiante de las de los cursos
                    columnas_estudiante = [
                        '_Estudiante_ID', '_Estudiante_Nombres', '_Estudiante_Apellidos', 
                        '_Estudiante_Grado', '_Estudiante_Grupo', '_Estudiante_Jornada'
                    ]
                    self.df_cursos = df_temporal.drop(columns=columnas_estudiante, errors='ignore')
                    
                    # 3. Si existía la fila temporal vacía del archivo inicial, la eliminamos
                    if len(self.df_cursos) == 1 and self.df_cursos.iloc[0]['Nombre'] == '---':
                        self.df_cursos = self.df_cursos.iloc[0:0]
                    
                    # Convertimos las cadenas de las notas de vuelta a listas reales de Python
                    if not self.df_cursos.empty:
                        self.df_cursos['Nota Periodos'] = self.df_cursos['Nota Periodos'].apply(ast.literal_eval)
                        self.registros = self.df_cursos.to_dict(orient='records')
                        self.escala = float(self.registros[0]['Escala'])
                    else:
                        self.registros = []
                        self.escala = 5.0
                else:
                    # Control de contingencia en caso de archivos dañados externamente
                    self.estudiante = {"ID": "error", "Nombres": "Carga", "Apellidos": "Fallida", "Grado": 0, "Grupo": 1, "Jornada": "M"}
                    self.df_cursos = pd.DataFrame(columns=['Nombre', 'Periodos', 'Nota Periodos', 'Escala', 'Promedio', 'Aprobación', 'Nivel'])
                    self.registros = []
                    self.escala = 5.0
                
                print(f"📂 ¡Expediente de {self.estudiante['Nombres'].title()} {self.estudiante['Apellidos'].title()} cargado exitosamente!")
                input('Presiona Enter para ir al panel principal...')
                self.limpiar_pantalla()
            except Exception as e:
                print(f"⚠️ Error al abrir el expediente: {e}")
                input('Pulsa Enter...')
                self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Agregar Cursos
    # -----------------------------------------------------------------------------
    def configurar_escala(self) -> None:
        if len(self.registros) == 0:
            print('\n=== Configurar Escala ===\n')
            self.escala = self.pedir_numero('Valor máximo de notas (ej: 5 ó 10): ', 1, 100)

    def agregar_curso(self) -> None:
        print('\n=== Ingresar Curso ===\n')
        notes = []
        nombre_curso = input('Ingrese nombre del curso: ').strip().lower()
        numero_periodos = self.pedir_numero('Número Periodos (máx 10): ', 1, 10)

        print('\nDigitar Notas...')
        for n in range(1, numero_periodos + 1):
            nota = self.pedir_numero(f'Digita la nota del Periodo {n} (1-{self.escala}): ', 1, self.escala, permitir_float=True)
            notes.append(nota)

        promedio_curso = round(sum(notes) / len(notes), 1)
        nivel_curso = self.nivel_desempeno(promedio_curso, self.escala)
        aprobacion = self.ver_aprobacion(promedio_curso, self.escala * 0.6)

        nuevo_registro = {
            'Nombre': nombre_curso, 'Periodos': numero_periodos, 'Nota Periodos': notes,
            'Escala': self.escala, 'Promedio': promedio_curso, 'Aprobación': aprobacion, 'Nivel': nivel_curso
        }
        self.registros.append(nuevo_registro)

        print('\n=== Datos Registrados ===\n')
        print(f'Nombre Curso: {nombre_curso.title()}')
        print(f'- Promedio Curso: {promedio_curso}')
        print(f'- Nivel Desempeño: {nivel_curso.title()}')

        df_curso_nuevo = pd.DataFrame([nuevo_registro])
        self.df_cursos = pd.concat([self.df_cursos, df_curso_nuevo], ignore_index=True)

        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Panel Estadístico Avanzado (Pandas)
    # -----------------------------------------------------------------------------
    def mostrar_estadisticas(self) -> None:
        print('\n=== Panel de Estadísticas Generales ===\n')
        if len(self.df_cursos) == 0:
            print("Sin datos suficientes para calcular estadísticas.")
        else:
            promedio_global = self.df_cursos['Promedio'].mean()
            idx_max = self.df_cursos['Promedio'].idxmax()
            idx_min = self.df_cursos['Promedio'].idxmin()
            aprobados = len(self.df_cursos[self.df_cursos['Aprobación'] == 'aprobado'])
            reprobados = len(self.df_cursos[self.df_cursos['Aprobación'] == 'reprobado'])

            print(f"📈 Promedio General Acumulado: {promedio_global:.2f} / {self.escala}")
            print(f"🥇 Materia con Mayor Rendimiento: {self.df_cursos.loc[idx_max, 'Nombre'].title()} ({self.df_cursos.loc[idx_max, 'Promedio']})")
            print(f"🥈 Materia con Menor Rendimiento: {self.df_cursos.loc[idx_min, 'Nombre'].title()} ({self.df_cursos.loc[idx_min, 'Promedio']})")
            print(f"✅ Cursos Aprobados: {aprobados}")
            print(f"❌ Cursos Reprobados: {reprobados}")
            
        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Borrar Cursos
    # -----------------------------------------------------------------------------
    def borrar_cursos(self) -> None:
        print('\n=== Borrar Cursos ===\n')
        if len(self.registros) == 0:
            print("Sin cursos para borrar.")
        else:
            print("1. Borrar un Curso específico.\n2. Borrar Todos los Cursos.\n3. Salir.")
            opcion_borrar = self.pedir_numero('Opción: ', 1, 3)

            if opcion_borrar == 1:
                posicion_curso = self.pedir_numero('Número de curso a borrar (0 -> salir): ', 0, len(self.registros))
                if posicion_curso != 0:
                    indice_curso = posicion_curso - 1
                    print(f"\nCurso a borrar: {self.registros[indice_curso]['Nombre'].title()}")
                    del self.registros[indice_curso]
                    self.df_cursos.drop(indice_curso, inplace=True)
                    self.df_cursos.reset_index(drop=True, inplace=True)
                    print("Curso borrado con éxito.")
            elif opcion_borrar == 2:
                self.registros.clear()
                self.df_cursos = self.df_cursos.iloc[0:0]
                print("Todos los cursos se han borrado.")

        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Ordenar y Ver Datos
    # -----------------------------------------------------------------------------
    def ordenar_datos(self) -> None:
        if not self.registros:
            return
        self.registros.sort(key=lambda x: unidecode(x['Nombre']))
        if not self.df_cursos.empty:
            self.df_cursos['temp'] = self.df_cursos['Nombre'].apply(lambda x: unidecode(x))
            self.df_cursos = self.df_values = self.df_cursos.sort_values(by='temp').drop(columns=['temp']).reset_index(drop=True)

    def ver_registros(self) -> None:
        print(f'\nCursos registrados: {len(self.registros)}')
        print('----------------------')
        for n, registro in enumerate(self.registros, 1):
            print(f"{n}. {registro['Nombre'].title()}: {registro['Promedio']}, {registro['Nivel'].title()}, {registro['Aprobación'].title()}")

    def ver_dataframe(self) -> None:
        print('\n=== Vista de Datos (Pandas) ===\n')
        if len(self.registros) == 0:
            print("Sin cursos registrados.")
        else:
            print(self.df_cursos[['Nombre', 'Periodos', 'Promedio', 'Aprobación', 'Nivel']])
        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    def nivel_desempeno(self, promedio: float, nota_max: float) -> str:
        p = promedio / nota_max
        if p >= 0.9: return "superior"
        elif p >= 0.8: return "alto"
        elif p >= 0.6: return "básico"
        else: return "bajo"

    def ver_aprobacion(self, promedio: float, nota_min: float) -> str:
        return "aprobado" if promedio >= nota_min else "reprobado"

    # -----------------------------------------------------------------------------
    # Gráficos (Fieles a v5 original)
    # -----------------------------------------------------------------------------
    def menu_graficar(self) -> None:
        print('\n=== Gráfica Promedios ===\n')
        if len(self.registros) == 0:
            print("Sin datos para graficar")
        else:
            nombres = [r['Nombre'].title() for r in self.registros]
            promedios = [r['Promedio'] for r in self.registros]
            niveles = [r['Nivel'] for r in self.registros]

            fig = tpl.figure()
            fig.barh(promedios, labels=nombres, force_ascii=False)
            fig.show()

            self.grafica_cursos(nombres, promedios, niveles, guardar=False)
        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    def grafica_cursos(self, nombres: list, promedios: list, niveles: list, guardar=True) -> str:
        promedio_general = sum(promedios) / len(promedios)
        colores_barras = ['#E1060D' if n=='bajo' else '#FF6600' if n=='básico' else '#FFDD00' if n=='alto' else '#008860' for n in niveles]

        plt.figure(figsize=(6.5, 4.0), dpi=300)
        barras = plt.bar(nombres, promedios, color=colores_barras, zorder=2)
        
        plt.axhline(y=promedio_general, color="red", linestyle="--", linewidth=1.5, label=f"Promedio General ({promedio_general:.1f})", zorder=3)

        plt.axhspan(0, self.escala * 0.6, facecolor="#E1060D", alpha=0.1)
        plt.axhspan(self.escala * 0.6, self.escala * 0.8, facecolor="#FF6600", alpha=0.1)
        plt.axhspan(self.escala * 0.8, self.escala * 0.9, facecolor="#FFDD00", alpha=0.1)
        plt.axhspan(self.escala * 0.9, self.escala, facecolor="#008860", alpha=0.1)

        plt.title(f"Promedio de Cursos: {self.mostrar_estudiante()[1]}", fontsize=11)
        plt.xlabel("Cursos", fontsize=11)
        plt.ylabel("Promedio", fontsize=11)
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, self.escala + 1)

        for bar in barras:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, round(yval, 2), ha="center", va="bottom", fontsize=8)

        plt.tight_layout()

        if guardar:
            id_corto = self.estudiante.get("ID", "anonimo")
            ruta = f"grafica_notas_{id_corto}.png"
            plt.savefig(ruta, bbox_inches="tight", dpi=300)
            plt.close()
            return ruta
        else:
            plt.show()
        plt.close()

    # -----------------------------------------------------------------------------
    # Estudiantes
    # -----------------------------------------------------------------------------
    def menu_estudiantes(self) -> None:
        print('\n=== Datos Estudiante Actual ===\n')
        print(self.mostrar_estudiante()[0])
        print("\n1. Editar Datos Actuales\n2. Salir")
        if self.pedir_numero('Opción: ', 1, 2) == 1:
            self.pedir_datos_estudiante(es_nuevo=False)
        self.limpiar_pantalla()

    def mostrar_estudiante(self) -> tuple:
        if len(self.estudiante) > 0:
            info = f"[{self.estudiante['ID']}] {self.estudiante['Nombres'].title()} {self.estudiante['Apellidos'].title()} {self.estudiante['Grado']}-{self.estudiante['Grupo']} J-{self.estudiante['Jornada']}"
            corto = f"{self.estudiante['Nombres'].split()[0].title()} {self.estudiante['Apellidos'].split()[0].title()}"
        else:
            info, corto = "Sin datos Estudiante", ""
        return info, corto

    # -----------------------------------------------------------------------------
    # Generar Informe PDF Dinámico por Estudiante
    # -----------------------------------------------------------------------------
    def generar_informe(self) -> None:
        if len(self.registros) == 0:
            print("\nSin cursos registrados")
            input('\nPulsa Enter...')
            return

        id_estudiante = self.estudiante.get("ID", "anonimo")
        pdf_path = f"informe_notas_{id_estudiante}.pdf"
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        estilos = getSampleStyleSheet()
        
        estilo_aprobado = ParagraphStyle('AprobadoStyle', parent=estilos['Normal'], fontSize=10, textColor=colors.HexColor('#008860'), alignment=1)
        estilo_reprobado = ParagraphStyle('ReprobadoStyle', parent=estilos['Normal'], fontSize=10, textColor=colors.HexColor('#E1060D'), alignment=1)
        
        elementos = []
        elementos.append(Paragraph("Informe Ejecutivo de Rendimiento Académico", ParagraphStyle('T1', parent=estilos['Heading1'], fontSize=20, spaceAfter=10)))
        elementos.append(Paragraph(f"<b>Estudiante:</b> {self.mostrar_estudiante()[0]}", ParagraphStyle('T2', parent=estilos['Normal'], fontSize=12, spaceAfter=15)))
        
        datos_tabla = [['Curso', 'Periodos', 'Calificaciones', 'Promedio', 'Desempeño']]
        for r in self.registros:
            estilo_celda = estilo_aprobado if r['Aprobación'] == 'aprobado' else estilo_reprobado
            datos_tabla.append([
                Paragraph(r['Nombre'].title(), estilo_celda), 
                str(r['Periodos']), str(r['Nota Periodos']), str(r['Promedio']), r['Nivel'].title()
            ])
            
        tabla_reporte = Table(datos_tabla, colWidths=[110, 60, 160, 70, 90])
        estilo_tabla = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ])
        
        for i in range(1, len(datos_tabla)):
            if i % 2 == 0:
                estilo_tabla.add('BACKGROUND', (0,i), (-1,i), colors.HexColor('#F7FAFC'))
        
        tabla_reporte.setStyle(estilo_tabla)
        elementos.append(tabla_reporte)
        elementos.append(Spacer(1, 20))

        nombres = [r['Nombre'].title() for r in self.registros]
        promedios = [r['Promedio'] for r in self.registros]
        niveles = [r['Nivel'] for r in self.registros]
        ruta_grafica = self.grafica_cursos(nombres, promedios, niveles, guardar=True)
        
        elementos.append(Image(ruta_grafica, width=480, height=295))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("<i>Sistema de Control de Notas - Creado por Sebas PuenteR, 2026</i>", ParagraphStyle('C', parent=estilos['Normal'], fontSize=8, alignment=1)))

        doc.build(elementos)
        if os.path.exists(ruta_grafica): os.remove(ruta_grafica)
        print(f"🎉 ¡PDF Ejecutivo '{pdf_path}' generado con éxito!")
        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Utilidades y Menú de Control Principal
    # -----------------------------------------------------------------------------
    def pedir_numero(self, mensaje: str, num_min, num_max, permitir_float=False):
        while True:
            try:
                numero = float(input(mensaje)) if permitir_float else int(input(mensaje))
                if num_min <= numero <= num_max: return numero
                print(f"❌ Rango inválido ({num_min} - {num_max}).")
            except ValueError:
                print("❌ Entrada no válida.")

    def degly(self) -> None:
        self.registros.clear()
        self.escala = 5.0
        for c in ["tecnología", "física", "química", "ética", "ciencias"]:
            notes = [round(random.uniform(1.5, 5.0), 1) for _ in range(3)]
            prom = round(sum(notes)/3, 1)
            self.registros.append({
                'Nombre': c, 'Periodos': 3, 'Nota Periodos': notes, 'Escala': 5.0,
                'Promedio': prom, 'Aprobación': self.ver_aprobacion(prom, 3.0), 'Nivel': self.nivel_desempeno(prom, 5.0)
            })
        self.df_cursos = pd.DataFrame(self.registros)
        self.limpiar_pantalla()

    def inicio(self) -> None:
        if not self.menu_seleccion_estudiante():
            return

        while True:
            print("\n" + "="*30 + f"\n     GESTOR ACADÉMICO v7.1\n" + "="*30)
            print(f"Estudiante Activo: {self.mostrar_estudiante()[0]}")
            self.ordenar_datos()
            self.ver_registros()
            print("\n1. Configurar/Ingresar Curso\n2. Ver Tabla Completa\n3. Datos Estudiante Activo\n4. Ver Gráficas\n5. Exportar PDF Ejecutivo\n6. Borrar Cursos\n7. Panel Estadístico (Pandas)\n8. Cambiar de Estudiante / Salir\n" + "="*30)
            
            opcion = input("Opción: ").strip()
            if opcion == "1": 
                self.configurar_escala()
                self.agregar_curso()
            elif opcion == "2": self.ver_dataframe()
            elif opcion == "3": self.menu_estudiantes()
            elif opcion == "4": self.menu_graficar()
            elif opcion == "5": self.generar_informe()
            elif opcion == "6": self.borrar_cursos()
            elif opcion == "7": self.mostrar_estadisticas()
            elif opcion == "8": 
                self.guardar_datos_csv()
                print("\n🔄 Volviendo al menú de selección...")
                if not self.menu_seleccion_estudiante():
                    print("\n¡Hasta pronto Sebas!\n")
                    break
            elif opcion == "degly": self.degly()
            else: self.limpiar_pantalla()


if __name__ == "__main__":
    app = GestorAcademico()
    app.limpiar_pantalla()
    app.inicio()
