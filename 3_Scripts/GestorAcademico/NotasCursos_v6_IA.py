"""
Cambios v6:
1. Reestructuración completa a Programación Orientada a Objetos (Clase GestorAcademico).
2. Eliminación absoluta de variables globales (ahora son atributos de instancia).
3. Corrección de SyntaxError en f-strings por comillas anidadas.
4. Optimización de limpieza de pantalla (compatible con Windows, Linux y macOS).
5. Corrección de incremento redundante en el ciclo de generación de PDF.
6. Inicialización segura de la escala por defecto para evitar NameError.
"""

import os
import random
import matplotlib.pyplot as plt
import pandas as pd
import termplotlib as tpl
from text_unidecode import unidecode

# Módulos para crear pdfs
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer


class GestorAcademico:

    def __init__(self):
        """Inicializa los atributos principales del sistema evitando variables globales"""
        self.registros = []
        self.escala = 5.0  # Escala por defecto para evitar errores si no se configura al inicio
        self.estudiante = {}
        self.df_cursos = pd.DataFrame(
            columns=[
                "Nombre",
                "Periodos",
                "Nota Periodos",
                "Escala",
                "Promedio",
                "Aprobación",
                "Nivel",
            ]
        )

    def limpiar_pantalla(self) -> None:
        """Limpia la consola de forma compatible con Windows (cls) y Unix/Mac (clear)"""
        os.system("cls" if os.name == "nt" else "clear")

    # -----------------------------------------------------------------------------
    # Establecer Escala de las Notas
    # -----------------------------------------------------------------------------
    def configurar_escala(self) -> None:
        """Establece la escala en la que se ingresarán las notas"""
        if len(self.registros) == 0:
            print("\n=== Configurar Escala ===\n")
            self.escala = self.pedir_numero(
                "Valor máximo de notas (ej: 5 ó 10): ", 1, 100
            )

    # -----------------------------------------------------------------------------
    # Agregar Cursos
    # -----------------------------------------------------------------------------
    def agregar_curso(self) -> None:
        """Crea un curso con sus notas, calcula promedios y lo registra"""
        print("\n=== Ingresar Curso ===\n")
        notas = []
        nombre_curso = input("Ingrese nombre del curso: ").strip().lower()
        numero_periodos = self.pedir_numero("Número Periodos (máx 10): ", 1, 10)

        print("\nDigitar Notas...")
        for n in range(1, numero_periodos + 1):
            nota = self.pedir_numero(
                f"Digita la nota del Periodo {n} (1-{self.escala}): ",
                1,
                self.escala,
                permitir_float=True,
            )
            notas.append(nota)

        # Cálculos
        promedio_curso = round(sum(notas) / len(notas), 1)
        nivel_curso = self.nivel_desempeno(promedio_curso, self.escala)
        aprobacion = self.ver_aprobacion(promedio_curso, self.escala * 0.6)

        # Se agrega el registro como un diccionario
        nuevo_registro = {
            "Nombre": nombre_curso,
            "Periodos": numero_periodos,
            "Nota Periodos": notas,
            "Escala": self.escala,
            "Promedio": promedio_curso,
            "Aprobación": aprobacion,
            "Nivel": nivel_curso,
        }
        self.registros.append(nuevo_registro)

        # Mostrar datos registrados
        print("\n=== Datos Registrados ===\n")
        print(f"Nombre Curso: {nombre_curso.title()}")
        print(f"Número Periodos: {numero_periodos}")
        print(f"Notas Registradas: {notas}")
        print(f"Escala: 1 - {self.escala}\n")
        print(f"- Promedio Curso: {promedio_curso}")
        print(f"- Aprobación: {aprobacion.title()}")
        print(f"- Nivel Desempeño: {nivel_curso.title()}")

        # Guardar info en Dataframe
        df_curso_nuevo = pd.DataFrame([nuevo_registro])
        self.df_cursos = pd.concat(
            [self.df_cursos, df_curso_nuevo], ignore_index=True
        )

        input("\nPulsa Enter para continuar...")
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Borrar Cursos
    # -----------------------------------------------------------------------------
    def borrar_cursos(self) -> None:
        """Borra un curso específico o todos los cursos del sistema"""
        print("\n=== Borrar Cursos ===\n")

        if len(self.registros) == 0:
            print("Sin cursos para borrar")
        else:
            print("1. Borrar un Curso (recomendado).")
            print("2. Borrar Todos los Cursos.")
            print("3. Salir.")
            opcion_borrar = self.pedir_numero("Opción: ", 1, 3)

            if opcion_borrar == 1:
                posicion_curso = self.pedir_numero(
                    "Número de curso a borrar (0 -> salir): ",
                    0,
                    len(self.registros),
                )

                if posicion_curso != 0:
                    indice_curso = posicion_curso - 1
                    # CORREGIDO: Uso de comillas dobles internas para evitar SyntaxError
                    print(
                        f'\nCurso a borrar: {posicion_curso}. {self.registros[indice_curso]["Nombre"].title()}'
                    )
                    del self.registros[indice_curso]
                    self.df_cursos.drop(indice_curso, inplace=True)
                    self.df_cursos.reset_index(drop=True, inplace=True)
                    print("Curso borrado.")
                else:
                    self.limpiar_pantalla()
                    return

            elif opcion_borrar == 2:
                self.registros.clear()
                self.df_cursos = self.df_cursos.iloc[0:0]
                print("Todos los cursos se han borrado.")

            elif opcion_borrar == 3:
                self.limpiar_pantalla()
                return

        input("\nPulsa Enter para continuar...")
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Ordenar Datos Cursos
    # -----------------------------------------------------------------------------
    def ordenar_datos(self) -> None:
        """Ordena alfabéticamente el registro y el dataframe"""
        if not self.registros:
            return

        self.registros.sort(key=lambda x: unidecode(x["Nombre"]))

        self.df_cursos["temp"] = self.df_cursos["Nombre"].apply(
            lambda x: unidecode(x)
        )
        self.df_cursos = (
            self.df_cursos.sort_values(by="temp")
            .drop(columns=["temp"])
            .reset_index(drop=True)
        )

    # -----------------------------------------------------------------------------
    # Ver Cursos Registrados
    # -----------------------------------------------------------------------------
    def ver_registros(self) -> None:
        """Imprime un listado resumido de los cursos registrados"""
        print(f"\nCursos registrados: {len(self.registros)}")
        print("----------------------")

        for n, registro in enumerate(self.registros, 1):
            # CORREGIDO: Comillas internas corregidas para evitar SyntaxError
            print(
                f'{n}. {registro["Nombre"].title()}: {registro["Promedio"]}, {registro["Nivel"].title()}, {registro["Aprobación"].title()}'
            )

    # -----------------------------------------------------------------------------
    # Ver Dataframe
    # -----------------------------------------------------------------------------
    def ver_dataframe(self) -> None:
        """Imprime el DataFrame estructurado con Pandas"""
        print("\n=== Cursos Registrados ===\n")
        if len(self.registros) == 0:
            print("Sin cursos registrados.")
        else:
            print(self.df_cursos)
            print(f"\nTotal Cursos Registrados: {len(self.df_cursos)}")

        input("\nPulsa Enter para continuar...")
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Nivel de Desempeño y Aprobación
    # -----------------------------------------------------------------------------
    def nivel_desempeno(self, promedio: float, nota_max: float) -> str:
        """Devuelve el nivel de desempeño en base a un porcentaje estandarizado"""
        promedio_normalizado = promedio / nota_max
        if promedio_normalizado >= 9 / 10:
            return "superior"
        elif promedio_normalizado >= 8 / 10:
            return "alto"
        elif promedio_normalizado >= 6 / 10:
            return "básico"
        else:
            return "bajo"

    def ver_aprobacion(
        self, promedio: float, nota_min_aprobacion: float
    ) -> str:
        """Determina si un curso fue aprobado o reprobado"""
        return "aprobado" if promedio >= nota_min_aprobacion else "reprobado"

    # -----------------------------------------------------------------------------
    # Graficar Cursos
    # -----------------------------------------------------------------------------
    def menu_graficar(self) -> None:
        """Genera y muestra las gráficas de rendimiento (Consola y Matplotlib)"""
        print("\n=== Gráfica Promedios ===\n")

        if len(self.registros) == 0:
            print("Sin datos para graficar")
        else:
            nombre_cursos = [r["Nombre"].title() for r in self.registros]
            promedio_cursos = [r["Promedio"] for r in self.registros]
            niveles_cursos = [r["Nivel"] for r in self.registros]

            # Gráfico en Terminal
            fig = tpl.figure()
            fig.barh(promedio_cursos, labels=nombre_cursos, force_ascii=False)
            fig.show()

            # Gráfico en Matplotlib
            self.grafica_cursos(
                nombre_cursos, promedio_cursos, niveles_cursos, guardar=False
            )

        input("\nPulsa Enter para continuar...")
        self.limpiar_pantalla()

    def grafica_cursos(
        self, nombres: list, promedios: list, niveles: list, guardar=True
    ) -> str:
        """Genera la personalización estética del gráfico de barras"""
        promedio_general = sum(promedios) / len(promedios)

        colores_barras = []
        for nivel in niveles:
            if nivel == "bajo":
                colores_barras.append("#E1060D")
            elif nivel == "básico":
                colores_barras.append("#FF6600")
            elif nivel == "alto":
                colores_barras.append("#FFDD00")
            else:
                colores_barras.append("#008860")

        plt.figure(figsize=(6.5, 4.0), dpi=300)
        barras = plt.bar(nombres, promedios, color=colores_barras, zorder=2)

        plt.axhline(
            y=promedio_general,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=f"Promedio General ({promedio_general:.1f})",
            zorder=3,
        )

        # Fondos traslúcidos por niveles
        plt.axhspan(
            0,
            self.escala * 0.6,
            facecolor="#E1060D",
            alpha=0.1,
            label=f"Bajo (0.0 - {self.escala*0.6-0.1:.1f})",
        )
        plt.axhspan(
            self.escala * 0.6,
            self.escala * 0.8,
            facecolor="#FF6600",
            alpha=0.1,
            label=f"Básico ({self.escala*0.6:.1f} - {self.escala*0.8-0.1:.1f})",
        )
        plt.axhspan(
            self.escala * 0.8,
            self.escala * 0.9,
            facecolor="#FFDD00",
            alpha=0.1,
            label=f"Alto ({self.escala*0.8:.1f} - {self.escala*0.9-0.1:.1f})",
        )
        plt.axhspan(
            self.escala * 0.9,
            self.escala,
            facecolor="#008860",
            alpha=0.1,
            label=f"Superior ({self.escala*0.9:.1f} - {self.escala})",
        )

        titulo_grafico = f"Promedio de Cursos: {self.mostrar_estudiante()[1]}"
        plt.title(titulo_grafico, fontsize=11)
        plt.xlabel("Cursos", fontsize=11)
        plt.ylabel("Promedio", fontsize=11)
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, self.escala + 1)
        plt.legend()

        for bar in barras:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                yval + 0.2,
                round(yval, 2),
                ha="center",
                va="bottom",
                fontsize=8,
            )

        plt.tight_layout()

        if guardar:
            nombre_sin_espacios = self.mostrar_estudiante()[1].replace(
                " ", "_"
            )
            ruta_grafica = f"grafica_notas_{nombre_sin_espacios}.png"
            plt.savefig(ruta_grafica, bbox_inches="tight", dpi=300)
            plt.close()
            return ruta_grafica
        else:
            plt.show()

        plt.close()

    # -----------------------------------------------------------------------------
    # Gestión de Datos del Estudiante
    # -----------------------------------------------------------------------------
    def menu_estudiantes(self) -> None:
        """Menú para visualizar o editar la información del estudiante"""
        print("\n=== Datos Estudiante ===\n")
        print(self.mostrar_estudiante()[0])
        print("\n1. Editar")
        print("2. Salir")
        opcion_estudiante = self.pedir_numero("Opción: ", 1, 2)

        if opcion_estudiante == 1:
            self.pedir_datos_estudiante()
        elif opcion_estudiante == 2:
            self.limpiar_pantalla()
            return

        self.limpiar_pantalla()

    def pedir_datos_estudiante(self) -> None:
        """Captura por consola la información de identidad académica"""
        jornadas = ["M", "T", "N"]
        estudiante_nombres = input("\nNombre: ").strip()
        estudiante_apellidos = input("Apellidos: ").strip()
        estudiante_grado = self.pedir_numero("Grado: ", 0, 11)
        estudiante_grupo = self.pedir_numero("Grupo: ", 1, 10)
        num_jornada = self.pedir_numero(
            "Jornada (1.Mañana, 2.Tarde, 3.Noct): ", 1, 3
        )
        estudiante_jornada = jornadas[num_jornada - 1]

        self.estudiante = {
            "Nombres": estudiante_nombres,
            "Apellidos": estudiante_apellidos,
            "Grado": estudiante_grado,
            "Grupo": estudiante_grupo,
            "Jornada": estudiante_jornada,
        }

    def hay_estudiante(self) -> bool:
        """Verifica si los datos del estudiante han sido rellenados"""
        return len(self.estudiante) > 0

    def mostrar_estudiante(self) -> tuple:
        """Retorna cadenas formateadas con la información del alumno"""
        if self.hay_estudiante():
            # CORREGIDO: Uso de comillas internas dobles dentro de f-strings
            info_estudiante = (
                f"{self.estudiante['Nombres'].title()} {self.estudiante['Apellidos'].title()} "
                f"{self.estudiante['Grado']}-{self.estudiante['Grupo']} "
                f"J{self.estudiante['Jornada'].title()}"
            )
            nombre_corto = (
                f"{self.estudiante['Nombres'].split()[0].title()} "
                f"{self.estudiante['Apellidos'].split()[0].title()} "
                f"{self.estudiante['Grado']}-{self.estudiante['Grupo']} "
                f"J{self.estudiante['Jornada'].title()}"
            )
        else:
            info_estudiante = "Sin datos Estudiante"
            nombre_corto = ""

        return info_estudiante, nombre_corto

    # -----------------------------------------------------------------------------
    # Validación Robusta de Entradas Numéricas
    # -----------------------------------------------------------------------------
    def pedir_numero(
        self,
        mensaje: str,
        num_min: int | float,
        num_max: int | float,
        permitir_float: bool = False,
    ):
        """Previene caídas del programa mediante bucles de validación try-except"""
        while True:
            entrada = input(mensaje)
            try:
                numero = float(entrada) if permitir_float else int(entrada)

                if num_min <= numero <= num_max:
                    return numero
                else:
                    print(
                        f"❌ Error: El número debe estar entre {num_min} y {num_max}.\n"
                    )
            except ValueError:
                if permitir_float:
                    print(
                        "❌ Error: Ingresa un número válido (entero o decimal).\n"
                    )
                else:
                    print("❌ Error: Por favor, ingresa solo números enteros.\n")

    def mostrar_menu(self) -> None:
        """Muestra el menú principal de opciones en la interfaz de comando"""
        print("\n" + "=" * 25)
        print("      MENÚ PRINCIPAL      ")
        print("=" * 25)
        print("1. Ingresar Curso")
        print("2. Ver Registros")
        print("3. Datos Estudiantes")
        print("4. Graficar")
        print("5. Generar Informe")
        print("6. Borrar Cursos")
        print("7. Salir")
        print("=" * 25)

    # -----------------------------------------------------------------------------
    # Generar Informe PDF
    # -----------------------------------------------------------------------------
    def generar_informe(self) -> None:
        """Exporta las notas consolidadas y el gráfico a un documento PDF"""
        if len(self.registros) == 0:
            print("\nSin cursos registrados")
            input("\nPulsa Enter para continuar...")
            self.limpiar_pantalla()
            return

        nombre_cursos = [r["Nombre"].title() for r in self.registros]
        promedio_cursos = [r["Promedio"] for r in self.registros]
        notas_cursos = [r["Nota Periodos"] for r in self.registros]
        nivel_cursos = [r["Nivel"] for r in self.registros]
        aprobacion_cursos = [r["Aprobación"] for r in self.registros]

        total_cursos = len(self.registros)
        total_cursos_aprobados = aprobacion_cursos.count("aprobado")
        total_cursos_reprobados = aprobacion_cursos.count("reprobado")

        pdf_path = "informe_notas.pdf"
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        estilos = getSampleStyleSheet()
        titulo_estilo = ParagraphStyle("Title", parent=estilos["Heading1"])
        subtitulo_estilo = ParagraphStyle(
            "Subtitle", parent=estilos["Heading2"], spaceBefore=4
        )
        texto_estilo = ParagraphStyle(
            "Normal", parent=estilos["Normal"], fontSize=12, spaceAfter=8
        )
        infocurso_estilo = ParagraphStyle(
            "curso", parent=estilos["Normal"], fontSize=11, spaceAfter=6
        )
        creditos_estilo = ParagraphStyle(
            "creditos", parent=estilos["Normal"], fontSize=8
        )

        elementos = []
        elementos.append(
            Paragraph("Informe de Rendimiento Académico", titulo_estilo)
        )
        elementos.append(
            Paragraph(f"Estudiante: {self.mostrar_estudiante()[0]}", subtitulo_estilo)
        )
        elementos.append(Spacer(1, 10))
        elementos.append(
            Paragraph(
                "A continuación, se presenta el detalle de las calificaciones por curso:",
                texto_estilo,
            )
        )
        elementos.append(Spacer(1, 10))

        for n in range(total_cursos):
            color = "green" if aprobacion_cursos[n] == "aprobado" else "red"
            info_curso = (
                f"<b>{n+1}. <font color={color}>{nombre_cursos[n].title()}</font>: </b>"
                f"Promedio: {promedio_cursos[n]}, "
                f"{aprobacion_cursos[n].title()}-"
                f"{nivel_cursos[n].title()}. "
                f"Nota Periodos: {notas_cursos[n]}"
            )
            elementos.append(Paragraph(info_curso, infocurso_estilo))
            # CORREGIDO: Se removió 'n+=1' porque el ciclo for lo maneja automáticamente.

        linea_totales = (
            f"<font color=gray><i>Total Cursos: {total_cursos}, "
            f"Total Cursos Aprobados: {total_cursos_aprobados}, "
            f"Total Cursos Reprobados: {total_cursos_reprobados}</i></font>"
        )
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(linea_totales, infocurso_estilo))

        elementos.append(Spacer(1, 20))
        ruta_grafica = self.grafica_cursos(
            nombre_cursos, promedio_cursos, nivel_cursos
        )
        elementos.append(Image(ruta_grafica, width=500, height=300))

        elementos.append(Spacer(1, 10))
        creditos = "Creado por: Sebas PuenteR, 2026 :)"
        elementos.append(Paragraph(creditos, creditos_estilo))

        doc.build(elementos)
        print("¡PDF generado con éxito!")

        if os.path.exists(ruta_grafica):
            os.remove(ruta_grafica)

        input("\nPulsa Enter para continuar...")
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Función de Pruebas (Mock Data)
    # -----------------------------------------------------------------------------
    def degly(self) -> None:
        """Inyecta de forma masiva datos aleatorios con propósitos de testing rápido"""
        self.registros.clear()
        print("\nCrear Cursos de Prueba")
        self.escala = int(input("Define escala: "))

        cursos_prueba = [
            "tecnología",
            "física",
            "química",
            "ética",
            "ciencias",
            "artes",
            "español",
        ]

        for curso in cursos_prueba:
            notas_curso_prueba = [
                round(random.uniform(2.0, self.escala), 1) for _ in range(4)
            ]
            promedio_prueba = sum(notas_curso_prueba) / len(notas_curso_prueba)

            reg_aux = {
                "Nombre": curso,
                "Periodos": 4,
                "Nota Periodos": notas_curso_prueba,
                "Escala": self.escala,
                "Promedio": round(promedio_prueba, 1),
                "Aprobación": self.ver_aprobacion(
                    promedio_prueba, self.escala * 0.6
                ),
                "Nivel": self.nivel_desempeno(promedio_prueba, self.escala),
            }
            self.registros.append(reg_aux)

        self.ordenar_datos()
        self.df_cursos = pd.DataFrame(self.registros)
        self.limpiar_pantalla()

    # -----------------------------------------------------------------------------
    # Bucle Principal de Ejecución
    # -----------------------------------------------------------------------------
    def inicio(self) -> None:
        """Orquesta la ejecución persistente del menú interactivo"""
        while True:
            self.mostrar_menu()
            print("Estudiante:", self.mostrar_estudiante()[0])
            self.ordenar_datos()
            self.ver_registros()

            opcion_menu = input("\nDigite su opción del menú: ").strip()

            match opcion_menu:
                case "1":
                    self.configurar_escala()
                    self.agregar_curso()
                case "2":
                    self.ver_dataframe()
                case "3":
                    self.menu_estudiantes()
                case "4":
                    self.menu_graficar()
                case "5":
                    self.generar_informe()
                case "6":
                    self.borrar_cursos()
                case "7":
                    print("\nHasta Pronto!...")
                    print("= Sebas PuenteR =\n")
                    break
                case "degly":
                    self.degly()
                case _:
                    print("Opción no válida")
                    self.limpiar_pantalla()


if __name__ == "__main__":
    # Instanciamos el objeto y lanzamos el programa
    sistema = GestorAcademico()
    sistema.limpiar_pantalla()
    sistema.inicio()
