"""
Versión v6 - Premium (Escala Manual y Gráfica Original Restauradas)
Características:
1. Configuración de Escala Libre: Al presionar la opción 1 con el programa vacío, te vuelve a pedir la escala a manejar tal como en tu v5.
2. Gráfica Fiel a v5: Incluye línea de promedio general, texto sobre cada barra y rotación a 45°.
3. Menú Completo: Opción de Borrar Cursos (Opción 6) y Panel Estadístico (Opción 7).
4. Persistencia: Carga automática al iniciar y guardado automático en CSV al salir (Opción 8).
5. ReportLab Avanzado: El PDF genera una tabla ejecutiva con estilos y celdas alineadas.
6. Compatibilidad para limpiar pantalla (Windows/Linux/Mac).
"""

import os
import random
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
        """Inicializa los componentes del sistema y carga datos existentes"""
        self.archivo_datos = "3_Scripts/GestorAcademico/datos_estudiantes/mis_notas.csv"
        self.registros = []
        self.escala = 5.0  # Valor por defecto inicial
        self.estudiante = {}
        
        # Inicializamos un DataFrame con la estructura correcta
        self.df_cursos = pd.DataFrame(columns=[
            'Nombre', 'Periodos', 'Nota Periodos', 'Escala', 'Promedio', 'Aprobación', 'Nivel'
        ])
        
        # Intentar cargar datos guardados de sesiones anteriores
        self.cargar_datos_csv()

    def limpiar_pantalla(self) -> None:
        """Limpia la consola según el sistema operativo"""
        os.system('cls' if os.name == 'nt' else 'clear')

    # -----------------------------------------------------------------------------
    # Persistencia de Datos (CSV)
    # -----------------------------------------------------------------------------
    def guardar_datos_csv(self) -> None:
        """Guarda de forma persistente el DataFrame en un archivo CSV"""
        try:
            self.df_cursos.to_csv(self.archivo_datos, index=False)
            print("💾 ¡Datos guardados correctamente en 'mis_notas.csv'!")
        except Exception as e:
            print(f"❌ Error al guardar los datos: {e}")

    def cargar_datos_csv(self) -> None:
        """Carga los datos del archivo CSV si existe al iniciar el programa"""
        if os.path.exists(self.archivo_datos):
            try:
                self.df_cursos = pd.read_csv(self.archivo_datos)
                # Convertimos las cadenas de las notas de vuelta a listas reales de Python
                import ast
                self.df_cursos['Nota Periodos'] = self.df_cursos['Nota Periodos'].apply(ast.literal_eval)
                
                # Sincronizamos la lista de registros con lo que leímos del DataFrame
                self.registros = self.df_cursos.to_dict(orient='records')
                
                if len(self.registros) > 0:
                    self.escala = float(self.registros[0]['Escala'])
                print("📂 ¡Se han cargado tus cursos guardados automáticamente!")
            except Exception as e:
                print(f"⚠️ Nota: Se encontró un archivo de datos pero no se pudo leer ({e}).")

    # -----------------------------------------------------------------------------
    # Agregar Cursos
    # -----------------------------------------------------------------------------
    def configurar_escala(self) -> None:
        """Permite al usuario definir la escala si no hay cursos registrados"""
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
        """Muestra un resumen analítico del rendimiento actual usando Pandas"""
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
            self.df_cursos = self.df_cursos.sort_values(by='temp').drop(columns=['temp']).reset_index(drop=True)

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
            print(self.df_cursos)
            #print(self.df_cursos[['Nombre', 'Periodos', 'Promedio', 'Aprobación', 'Nivel']])
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
    # Gráficos (RESTAURADA CON TODAS LAS CARACTERÍSTICAS ORIGINALES)
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
        
        # Línea con el promedio general original
        plt.axhline(y=promedio_general, color="red", linestyle="--", linewidth=1.5, label=f"Promedio General ({promedio_general:.1f})", zorder=3)

        # Capas de fondo originales (alpha=0.1)
        plt.axhspan(0, self.escala * 0.6, facecolor="#E1060D", alpha=0.1)
        plt.axhspan(self.escala * 0.6, self.escala * 0.8, facecolor="#FF6600", alpha=0.1)
        plt.axhspan(self.escala * 0.8, self.escala * 0.9, facecolor="#FFDD00", alpha=0.1)
        plt.axhspan(self.escala * 0.9, self.escala, facecolor="#008860", alpha=0.1)

        plt.title(f"Promedio de Cursos: {self.mostrar_estudiante()[1]}", fontsize=11)
        plt.xlabel("Cursos", fontsize=11)
        plt.ylabel("Promedio", fontsize=11)
        plt.xticks(rotation=45, ha="right") # Rotación original a 45 grados
        plt.ylim(0, self.escala + 1)
        #plt.legend()

        # Texto/Promedio encima de cada barra original
        for bar in barras:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, round(yval, 2), ha="center", va="bottom", fontsize=8)

        plt.tight_layout()

        if guardar:
            nombre_sin_espacios = self.mostrar_estudiante()[1].replace(" ", "_")
            ruta = f"grafica_notas_{nombre_sin_espacios}.png"
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
        print('\n=== Datos Estudiante ===\n')
        print(self.mostrar_estudiante()[0])
        print("\n1. Editar\n2. Salir")
        if self.pedir_numero('Opción: ', 1, 2) == 1:
            self.pedir_datos_estudiante()
        self.limpiar_pantalla()

    def pedir_datos_estudiante(self) -> None:
        jornadas = ["M", "T", "N"]
        self.estudiante = {
            "Nombres": input("\nNombre: ").strip(), "Apellidos": input("Apellidos: ").strip(),
            "Grado": self.pedir_numero("Grado: ", 0, 11), "Grupo": self.pedir_numero("Grupo: ", 1, 10),
            "Jornada": jornadas[self.pedir_numero("Jornada (1.Mañana, 2.Tarde, 3.Noct): ", 1, 3) - 1]
        }

    def mostrar_estudiante(self) -> tuple:
        if len(self.estudiante) > 0:
            info = f"{self.estudiante['Nombres'].title()} {self.estudiante['Apellidos'].title()} {self.estudiante['Grado']}-{self.estudiante['Grupo']} J-{self.estudiante['Jornada']}"
            corto = f"{self.estudiante['Nombres'].split()[0].title()} {self.estudiante['Apellidos'].split()[0].title()} {self.estudiante['Grado']}-{self.estudiante['Grupo']} J{self.estudiante['Jornada'].title()}"
        else:
            info, corto = "Sin datos Estudiante", ""
        return info, corto

    # -----------------------------------------------------------------------------
    # Generar Informe PDF Avanzado con Tablas Estilizadas
    # -----------------------------------------------------------------------------
    def generar_informe(self) -> None:
        if len(self.registros) == 0:
            print("\nSin cursos registrados")
            input('\nPulsa Enter...')
            return

        pdf_path = "informe_notas_ejecutivo.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        estilos = getSampleStyleSheet()
        
        # Estilos
        estilo_aprobado = ParagraphStyle('AprobadoStyle', parent=estilos['Normal'], fontSize=10, textColor=colors.black, alignment=1)
        estilo_reprobado = ParagraphStyle('ReprobadoStyle', parent=estilos['Normal'], fontSize=10, textColor=colors.HexColor('#E1060D'), alignment=1)

        elementos = []
        elementos.append(Paragraph("Informe Ejecutivo de Rendimiento Académico", ParagraphStyle('T1', parent=estilos['Heading1'], fontSize=20, spaceAfter=10)))
        elementos.append(Paragraph(f"<b>Estudiante:</b> {self.mostrar_estudiante()[0]}", ParagraphStyle('T2', parent=estilos['Normal'], fontSize=14, spaceAfter=20)))
        elementos.append(Spacer(1, 10))

        # --- TABLA EJECUTIVA ---
        datos_tabla = [['Curso', 'Periodos', 'Calificaciones', 'Promedio', 'Aprobación', 'Desempeño']]
        for r in self.registros:
            # Seleccionamos dinámicamente el estilo según el estado de aprobación
            if r['Aprobación'] == 'aprobado':
                estilo_celda = estilo_aprobado
            else:
                estilo_celda = estilo_reprobado

            # Agregamos la fila envolviendo el nombre del curso en el Paragraph seleccionado
            datos_tabla.append([
                Paragraph(r['Nombre'].title(), estilo_celda),
                str(r['Periodos']),
                str(r['Nota Periodos']),
                str(r['Promedio']),
                Paragraph(r['Aprobación'].title(), estilo_celda),
                #r['Aprobación'].title(),
                r['Nivel'].title()
            ])
            
        tabla_reporte = Table(datos_tabla, colWidths=[110, 60, 120, 70, 70, 80])
        estilo_tabla = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
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
        elementos.append(Spacer(1, 10))

        # Totales
        aprobaciones = [r['Aprobación'] for r in self.registros]
        total_cursos_aprobados = aprobaciones.count('aprobado')
        total_cursos_reprobados = aprobaciones.count('reprobado')
        linea_totales = (
            f"<font color=gray><i>Total Cursos: {len(self.registros)}, "
            f"Total Cursos Aprobados: {total_cursos_aprobados}, "
            f"Total Cursos Reprobados: {total_cursos_reprobados}</i></font>"
        )
        totales_estilo = ParagraphStyle('infototal', parent=estilos['Normal'], fontSize=11, spaceAfter=6, alignment=1)
        elementos.append(Paragraph(linea_totales, totales_estilo))
        elementos.append(Spacer(1, 14))

        # Añadir Gráfica Completa
        nombres = [r['Nombre'].title() for r in self.registros]
        promedios = [r['Promedio'] for r in self.registros]
        niveles = [r['Nivel'] for r in self.registros]
        ruta_grafica = self.grafica_cursos(nombres, promedios, niveles, guardar=True)
        
        elementos.append(Image(ruta_grafica, width=500, height=300))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("<i>Sistema de Control de Notas - Creado por Sebas PuenteR, 2026</i>", ParagraphStyle('C', parent=estilos['Normal'], fontSize=8, alignment=1)))

        doc.build(elementos)
        if os.path.exists(ruta_grafica): os.remove(ruta_grafica)
        print("🎉 ¡PDF Ejecutivo con Tablas y Gráfica original generado con éxito!")
        input('\nPulsa Enter para continuar...')
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Utilidades y Menú Principal
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
        self.escala = float(input('Define escala: '))
        for c in ["tecnología", "física", "química", "ética", "ciencias"]:
            notes = [round(random.uniform(2.0, self.escala), 1) for _ in range(3)]
            prom = round(sum(notes)/3, 1)
            self.registros.append({
                'Nombre': c, 'Periodos': 3, 'Nota Periodos': notes, 'Escala': self.escala,
                'Promedio': prom, 'Aprobación': self.ver_aprobacion(prom, self.escala*0.6), 'Nivel': self.nivel_desempeno(prom, self.escala)
            })
        self.df_cursos = pd.DataFrame(self.registros)
        self.limpiar_pantalla()

    def inicio(self) -> None:
        while True:
            print("\n" + "="*30 + "\n     GESTOR ACADÉMICO v6\n" + "="*30)
            print(f"Estudiante: {self.mostrar_estudiante()[0]}")
            self.ordenar_datos()
            self.ver_registros()
            print("\nMenú Principal:")
            print("\n1. Configurar/Ingresar Curso\n2. Ver Tabla Completa\n3. Datos Estudiante\n4. Ver Gráficas\n5. Exportar PDF Ejecutivo\n6. Borrar Cursos\n7. Panel Estadístico (Pandas)\n8. Guardar y Salir\n" + "="*30)
            
            opcion = input("Opción: ").strip()
            if opcion == "1": 
                self.configurar_escala()  # <- ¡Restaurada la llamada aquí!
                self.agregar_curso()
            elif opcion == "2": self.ver_dataframe()
            elif opcion == "3": self.menu_estudiantes()
            elif opcion == "4": self.menu_graficar()
            elif opcion == "5": self.generar_informe()
            elif opcion == "6": self.borrar_cursos()
            elif opcion == "7": self.mostrar_estadisticas()
            elif opcion == "8": 
                self.guardar_datos_csv()
                print("\n¡Hasta pronto Sebas!\n")
                break
            elif opcion == "degly": self.degly()
            else: self.limpiar_pantalla()


if __name__ == "__main__":
    app = GestorAcademico()
    app.limpiar_pantalla()
    app.inicio()
