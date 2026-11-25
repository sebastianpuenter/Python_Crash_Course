"""
Versión v8.0 - POO Avanzada (Objetos por Estudiante)
Arquitectura:
1. Clase 'Estudiante': Cada alumno es un objeto independiente con sus propios atributos 
   (ID, Nombre, Grado, Cursos) y métodos (generar_pdf, graficar, agregar_curso).
2. Clase 'SistemaGestion': Controlador global que administra la carpeta de datos,
   el menú de la consola y la selección del estudiante activo.
3. Persistencia Perfecta: Toda la información del perfil y notas se guarda y recupera 
   correctamente desde su archivo CSV individual.
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


# =============================================================================
# CLASE MODELO: ESTUDIANTE (Un objeto independiente por cada alumno)
# =============================================================================
class Estudiante:
    def __init__(self, id_estudiante: str, nombres: str, apellidos: str, grado: int, grupo: int, jornada: str):
        """Inicializa los atributos únicos de este estudiante específico"""
        self.id = id_estudiante
        self.nombres = nombres
        self.apellidos = apellidos
        self.grado = grado
        self.grupo = grupo
        self.jornada = jornada
        self.escala = 5.0
        
        # El DataFrame de cursos y la lista pertenecen de forma única a este objeto estudiante
        self.df_cursos = pd.DataFrame(columns=['Nombre', 'Periodos', 'Nota Periodos', 'Escala', 'Promedio', 'Aprobación', 'Nivel'])
        self.registros = []

    def actualizar_perfil(self, nombres: str, apellidos: str, grado: int, grupo: int, jornada: str):
        """Permite modificar los datos personales del estudiante"""
        self.nombres = nombres
        self.apellidos = apellidos
        self.grado = grado
        self.grupo = grupo
        self.jornada = jornada

    def obtener_info_completa(self) -> str:
        return f"[{self.id}] {self.nombres.title()} {self.apellidos.title()} {self.grado}-{self.grupo} J-{self.jornada}"

    def obtener_nombre_corto(self) -> str:
        primer_nombre = self.nombres.split()[0].title() if self.nombres else ""
        primer_apellido = self.apellidos.split()[0].title() if self.apellidos else ""
        return f"{primer_nombre} {primer_apellido}"

    def ordenar_cursos(self) -> None:
        if not self.registros:
            return
        self.registros.sort(key=lambda x: unidecode(x['Nombre']))
        if not self.df_cursos.empty:
            self.df_cursos['temp'] = self.df_cursos['Nombre'].apply(lambda x: unidecode(x))
            self.df_cursos = self.df_cursos.sort_values(by='temp').drop(columns=['temp']).reset_index(drop=True)

    def agregar_curso_objeto(self, nombre: str, periodos: int, notas: list) -> None:
        """Calcula las métricas e ingresa el curso al expediente de este estudiante"""
        promedio = round(sum(notas) / len(notas), 1)
        
        # Determinar nivel de desempeño
        porcentaje = promedio / self.escala
        if porcentaje >= 0.9: nivel = "superior"
        elif porcentaje >= 0.8: nivel = "alto"
        elif porcentaje >= 0.6: nivel = "básico"
        else: nivel = "bajo"
        
        aprobacion = "aprobado" if promedio >= (self.escala * 0.6) else "reprobado"

        nuevo_registro = {
            'Nombre': nombre.lower(), 'Periodos': periodos, 'Nota Periodos': notas,
            'Escala': self.escala, 'Promedio': promedio, 'Aprobación': aprobacion, 'Nivel': nivel
        }
        self.registros.append(nuevo_registro)
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        self.df_cursos = pd.concat([self.df_cursos, df_nuevo], ignore_index=True)

    def mostrar_estadisticas_objeto(self) -> None:
        """Calcula métricas analíticas usando Pandas sobre el DataFrame de este estudiante"""
        print('\n=== Panel de Estadísticas Generales ===\n')
        if self.df_cursos.empty:
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

    def generar_grafica_objeto(self, guardar=True) -> str:
        """Construye la visualización gráfica de las notas de este estudiante"""
        nombres = [r['Nombre'].title() for r in self.registros]
        promedios = [r['Promedio'] for r in self.registros]
        niveles = [r['Nivel'] for r in self.registros]
        
        promedio_general = sum(promedios) / len(promedios)
        colores_barras = ['#E1060D' if n=='bajo' else '#FF6600' if n=='básico' else '#FFDD00' if n=='alto' else '#008860' for n in niveles]

        plt.figure(figsize=(6.5, 4.0), dpi=300)
        barras = plt.bar(nombres, promedios, color=colores_barras, zorder=2)
        
        plt.axhline(y=promedio_general, color="red", linestyle="--", linewidth=1.5, label=f"Promedio General ({promedio_general:.1f})", zorder=3)
        plt.axhspan(0, self.escala * 0.6, facecolor="#E1060D", alpha=0.1)
        plt.axhspan(self.escala * 0.6, self.escala * 0.8, facecolor="#FF6600", alpha=0.1)
        plt.axhspan(self.escala * 0.8, self.escala * 0.9, facecolor="#FFDD00", alpha=0.1)
        plt.axhspan(self.escala * 0.9, self.escala, facecolor="#008860", alpha=0.1)

        plt.title(f"Promedio de Cursos: {self.obtener_nombre_corto()}", fontsize=11)
        plt.xlabel("Cursos", fontsize=11)
        plt.ylabel("Promedio", fontsize=11)
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, self.escala + 1)

        for bar in barras:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, round(yval, 2), ha="center", va="bottom", fontsize=8)

        plt.tight_layout()

        if guardar:
            ruta = f"grafica_notas_{self.id}.png"
            plt.savefig(ruta, bbox_inches="tight", dpi=300)
            plt.close()
            return ruta
        else:
            plt.show()
        plt.close()

    def generar_pdf_objeto(self) -> None:
        """Exporta el reporte ejecutivo de este estudiante a PDF autónomamente"""
        if not self.registros:
            print("\nSin cursos registrados para generar el reporte.")
            return

        pdf_path = f"informe_notas_{self.id}.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        estilos = getSampleStyleSheet()
        
        estilo_aprobado = ParagraphStyle('AprobadoStyle', parent=estilos['Normal'], fontSize=10, textColor=colors.HexColor('#008860'), alignment=1)
        estilo_reprobado = ParagraphStyle('ReprobadoStyle', parent=estilos['Normal'], fontSize=10, textColor=colors.HexColor('#E1060D'), alignment=1)
        
        elementos = []
        elementos.append(Paragraph("Informe Ejecutivo de Rendimiento Académico", ParagraphStyle('T1', parent=estilos['Heading1'], fontSize=20, spaceAfter=10)))
        elementos.append(Paragraph(f"<b>Estudiante:</b> {self.obtener_info_completa()}", ParagraphStyle('T2', parent=estilos['Normal'], fontSize=12, spaceAfter=15)))
        
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

        ruta_grafica = self.generar_grafica_objeto(guardar=True)
        elementos.append(Image(ruta_grafica, width=480, height=295))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("<i>Sistema de Control de Notas - Creado por Sebas PuenteR, 2026</i>", ParagraphStyle('C', parent=estilos['Normal'], fontSize=8, alignment=1)))

        doc.build(elementos)
        if os.path.exists(ruta_grafica): 
            os.remove(ruta_grafica)
        print(f"🎉 ¡PDF Ejecutivo '{pdf_path}' generado con éxito!")


# =============================================================================
# CLASE CONTROLADORA: SISTEMA GESTIÓN (Orquestador global de la aplicación)
# =============================================================================
class SistemaGestion:
    def __init__(self):
        self.carpeta_datos = "datos_estudiantes"
        self.estudiante_activo = None  # <--- Apunta al OBJETO Estudiante actual en memoria
        
        if not os.path.exists(self.carpeta_datos):
            os.makedirs(self.carpeta_datos)

    def limpiar_pantalla(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def menu_inicial(self) -> bool:
        """Controla el flujo de entrada al programa"""
        while True:
            print("\n" + "="*30 + "\n   SISTEMA MULTI-ESTUDIANTE (POO)\n" + "="*30)
            print("1. Seleccionar Estudiante Existente")
            print("2. Registrar Nuevo Estudiante")
            print("3. Salir del Programa")
            print("="*30)
            
            opcion = input("Opción: ").strip()
            if opcion == "1":
                if self.listar_y_cargar_estudiante():
                    return True
            elif opcion == "2":
                self.crear_nuevo_estudiante()
                return True
            elif opcion == "3":
                print("\n¡Cierre de sistema exitoso!\n")
                return False
            else:
                self.limpiar_pantalla()

    def crear_nuevo_estudiante(self) -> None:
        """Instancia un nuevo objeto Estudiante y lo guarda en el disco"""
        print('\n=== Registrar Nuevo Estudiante ===\n')
        id_est = input("Número de Documento / ID Único: ").strip()
        while not id_est:
            id_est = input("El ID es obligatorio: ").strip()
            
        nombres = input("Nombres: ").strip()
        apellidos = input("Apellidos: ").strip()
        grado = self.pedir_numero_global("Grado (0-11): ", 0, 11)
        grupo = self.pedir_numero_global("Grupo (1-10): ", 1, 10)
        
        jornadas = ["M", "T", "N"]
        jornada = jornadas[self.pedir_numero_global("Jornada (1.Mañana, 2.Tarde, 3.Noct): ", 1, 3) - 1]
        
        # INSTANCIAMOS EL OBJETO DE LA CLASE ESTUDIANTE
        self.estudiante_activos = Estudiante(id_est, nombres, apellidos, grado, grupo, jornada)
        self.estudiante_activo = self.estudiante_activos
        
        self.guardar_objeto_csv()
        print(f"\n✅ Objeto Estudiante [{id_est}] creado y guardado en disco duro.")
        input('Presiona Enter para ir al panel principal...')
        self.limpiar_pantalla()

    def listar_y_cargar_estudiante(self) -> bool:
        """Muestra los archivos disponibles y carga el seleccionado convirtiéndolo en objeto"""
        archivos = [f for f in os.listdir(self.carpeta_datos) if f.endswith('.csv')]
        if not archivos:
            print("\n❌ No hay expedientes en el sistema. Registre un estudiante primero.")
            input('\nPulsa Enter...')
            self.limpiar_pantalla()
            return False
        
        print('\n=== Lista de Estudiantes Disponibles ===\n')
        for idx, archivo in enumerate(archivos, 1):
            try:
                df_temp = pd.read_csv(os.path.join(self.carpeta_datos, archivo))
                nom = str(df_temp.iloc[0]['_Estudiante_Nombres']).title()
                ape = str(df_temp.iloc[0]['_Estudiante_Apellidos']).title()
                ident = str(df_temp.iloc[0]['_Estudiante_ID'])
                print(f"{idx}. [{ident}] {nom} {ape}")
            except:
                print(f"{idx}. {archivo} (Archivo sin estructurar)")
                
        print(f"{len(archivos) + 1}. Volver atrás")
        
        opcion = self.pedir_numero_global("\nSeleccione el estudiante: ", 1, len(archivos) + 1)
        if opcion == len(archivos) + 1:
            self.limpiar_pantalla()
            return False
            
        self.cargar_objeto_csv(archivos[opcion - 1])
        return True

    def guardar_objeto_csv(self) -> None:
        """Serializa el objeto Estudiante Activo y sus cursos en un archivo CSV"""
        if self.estudiante_activo:
            nombre_archivo = f"{self.estudiante_activo.id}_{unidecode(self.estudiante_activo.nombres.lower()).replace(' ', '_')}.csv"
            ruta = os.path.join(self.carpeta_datos, nombre_archivo)
            try:
                df_guardar = self.estudiante_activo.df_cursos.copy()
                if df_guardar.empty:
                    df_guardar = pd.DataFrame([{
                        'Nombre': '---', 'Periodos': 0, 'Nota Periodos': '[]', 
                        'Escala': self.estudiante_activo.escala, 'Promedio': 0.0, 'Aprobación': '---', 'Nivel': '---'
                    }])

                # Metadatos del objeto inyectados como columnas
                df_guardar['_Estudiante_ID'] = self.estudiante_activo.id
                df_guardar['_Estudiante_Nombres'] = self.estudiante_activo.nombres
                df_guardar['_Estudiante_Apellidos'] = self.estudiante_activo.apellidos
                df_guardar['_Estudiante_Grado'] = self.estudiante_activo.grado
                df_guardar['_Estudiante_Grupo'] = self.estudiante_activo.grupo
                df_guardar['_Estudiante_Jornada'] = self.estudiante_activo.jornada
                
                df_guardar.to_csv(ruta, index=False)
                print(f"💾 Cambios guardados para el objeto '{self.estudiante_activo.obtener_nombre_corto()}'.")
            except Exception as e:
                print(f"❌ Error al guardar datos del objeto: {e}")

    def cargar_objeto_csv(self, archivo: str) -> None:
        """Lee el CSV y recrea (instancia) un objeto limpio de la clase Estudiante"""
        ruta = os.path.join(self.carpeta_datos, archivo)
        try:
            df_temp = pd.read_csv(ruta)
            # Reconstruimos el objeto invocando al constructor __init__ de Estudiante
            self.estudiante_activo = Estudiante(
                id_estudiante=str(df_temp.iloc[0]['_Estudiante_ID']),
                nombres=str(df_temp.iloc[0]['_Estudiante_Nombres']),
                apellidos=str(df_temp.iloc[0]['_Estudiante_Apellidos']),
                grado=int(df_temp.iloc[0]['_Estudiante_Grado']),
                grupo=int(df_temp.iloc[0]['_Estudiante_Grupo']),
                jornada=str(df_temp.iloc[0]['_Estudiante_Jornada'])
            )
            
            # Limpiamos columnas de control
            columnas = ['_Estudiante_ID', '_Estudiante_Nombres', '_Estudiante_Apellidos', '_Estudiante_Grado', '_Estudiante_Grupo', '_Estudiante_Jornada']
            self.estudiante_activo.df_cursos = df_temp.drop(columns=columnas, errors='ignore')
            
            if len(self.estudiante_activo.df_cursos) == 1 and self.estudiante_activo.df_cursos.iloc[0]['Nombre'] == '---':
                self.estudiante_activo.df_cursos = self.estudiante_activo.df_cursos.iloc[0:0]
                
            if not self.estudiante_activo.df_cursos.empty:
                self.estudiante_activo.df_cursos['Nota Periodos'] = self.estudiante_activo.df_cursos['Nota Periodos'].apply(ast.literal_eval)
                self.estudiante_activo.registros = self.estudiante_activo.df_cursos.to_dict(orient='records')
                self.estudiante_activo.escala = float(self.estudiante_activo.registros[0]['Escala'])
                
            print(f"📂 Objeto instanciado para: {self.estudiante_activo.obtener_info_completa()}")
            input('Presiona Enter para continuar...')
            self.limpiar_pantalla()
        except Exception as e:
            print(f"❌ Error al reconstruir el objeto Estudiante: {e}")
            input('Pulsa Enter...')
            self.limpiar_pantalla()

    def ingresar_curso_menu(self) -> None:
        print('\n=== Ingresar Curso ===\n')
        if not self.estudiante_activo.registros:
            self.estudiante_activo.escala = self.pedir_numero_global('Valor máximo de notas (ej: 5 ó 10): ', 1, 100)
            
        nombre_curso = input('Ingrese nombre del curso: ').strip().lower()
        num_periodos = self.pedir_numero_global('Número Periodos (máx 10): ', 1, 10)

        notas = []
        for n in range(1, num_periodos + 1):
            nota = self.pedir_numero_global(f'Nota Periodo {n} (1-{self.estudiante_activo.escala}): ', 1, self.estudiante_activo.escala, permitir_float=True)
            notas.append(nota)

        # LLAMAMOS AL MÉTODO PROPIO DEL OBJETO ESTUDIANTE
        self.estudiante_activo.agregar_curso_objeto(nombre_curso, num_periodos, notas)
        input('\nCurso añadido. Pulsa Enter para continuar...')
        self.limpiar_pantalla()

    def editar_perfil_menu(self) -> None:
        print('\n=== Datos Estudiante Activo ===\n')
        print(self.estudiante_activo.obtener_info_completa())
        print("\n1. Editar Datos Actuales\n2. Salir")
        if self.pedir_numero_global('Opción: ', 1, 2) == 1:
            nombres = input("\nNombres: ").strip()
            apellidos = input("Apellidos: ").strip()
            grado = self.pedir_numero_global("Grado (0-11): ", 0, 11)
            grupo = self.pedir_numero_global("Grupo (1-10): ", 1, 10)
            jornadas = ["M", "T", "N"]
            jornada = jornadas[self.pedir_numero_global("Jornada (1.Mañana, 2.Tarde, 3.Noct): ", 1, 3) - 1]
            
            # El objeto actualiza sus propios atributos internos
            self.estudiante_activo.actualizar_perfil(nombres, apellidos, grado, grupo, jornada)
            self.guardar_objeto_csv()
        self.limpiar_pantalla()

    def borrar_cursos_menu(self) -> None:
        print('\n=== Borrar Cursos ===\n')
        if not self.estudiante_activo.registros:
            print("Sin cursos para borrar.")
        else:
            print("1. Borrar un Curso específico.\n2. Borrar Todos los Cursos.\n3. Salir.")
            opcion = self.pedir_numero_global('Opción: ', 1, 3)

            if opcion == 1:
                pos = self.pedir_numero_global('Número de curso a borrar (0 -> salir): ', 0, len(self.estudiante_activo.registros))
                if pos != 0:
                    idx = pos - 1
                    del self.estudiante_activo.registros[idx]
                    self.estudiante_activo.df_cursos.drop(idx, inplace=True)
                    self.estudiante_activo.df_cursos.reset_index(drop=True, inplace=True)
                    print("Curso eliminado del objeto estudiante.")
            elif opcion == 2:
                self.estudiante_activo.registros.clear()
                self.estudiante_activo.df_cursos = self.estudiante_activo.df_cursos.iloc[0:0]
                print("Historial limpio.")
        input('\nPulsa Enter...')
        self.limpiar_pantalla()

    def pedir_numero_global(self, mensaje: str, num_min, num_max, permitir_float=False):
        while True:
            try:
                numero = float(input(mensaje)) if permitir_float else int(input(mensaje))
                if num_min <= numero <= num_max: return numero
                print(f"❌ Rango inválido ({num_min} - {num_max}).")
            except ValueError:
                print("❌ Entrada no válida.")

    def comando_degly_objeto(self) -> None:
        self.estudiante_activo.registros.clear()
        self.estudiante_activo.escala = 5.0
        for c in ["tecnología", "física", "química", "ética", "ciencias"]:
            notes = [round(random.uniform(1.5, 5.0), 1) for _ in range(3)]
            self.estudiante_activo.agregar_curso_objeto(c, 3, notes)
        self.limpiar_pantalla()

    def inicio(self) -> None:
        if not self.menu_inicial():
            return

        while True:
            print("\n" + "="*30 + f"\n     GESTOR ACADÉMICO v8.0\n" + "="*30)
            print(f"Estudiante Activo: {self.estudiante_activo.obtener_info_completa()}")
            self.estudiante_activo.ordenar_cursos()
            
            # Listar cursos del estudiante activo
            print(f'\nCursos registrados: {len(self.estudiante_activo.registros)}')
            print('----------------------')
            for n, r in enumerate(self.estudiante_activo.registros, 1):
                print(f"{n}. {r['Nombre'].title()}: {r['Promedio']}, {r['Nivel'].title()}, {r['Aprobación'].title()}")
                
            print("\n1. Configurar/Ingresar Curso\n2. Ver Tabla Completa (Pandas)\n3. Datos Estudiante Activo\n4. Ver Gráficas\n5. Exportar PDF Ejecutivo\n6. Borrar Cursos\n7. Panel Estadístico (Pandas)\n8. Cambiar de Estudiante / Salir\n" + "="*30)
            
            opcion = input("Opción: ").strip()
            if opcion == "1": 
                self.ingresar_curso_menu()
            elif opcion == "2": 
                print('\n=== Vista de Datos (Pandas) ===\n')
                if self.estudiante_activo.df_cursos.empty: print("Sin cursos.")
                else: print(self.estudiante_activo.df_cursos[['Nombre', 'Periodos', 'Promedio', 'Aprobación', 'Nivel']])
                input('\nPulsa Enter...')
                self.limpiar_pantalla()
            elif opcion == "3": self.editar_perfil_menu()
            elif opcion == "4": 
                print('\n=== Gráfica Promedios ===\n')
                if not self.estudiante_activo.registros: print("Sin datos.")
                else:
                    fig = tpl.figure()
                    fig.barh([r['Promedio'] for r in self.estudiante_activo.registros], labels=[r['Nombre'].title() for r in self.estudiante_activo.registros], force_ascii=False)
                    fig.show()
                    self.estudiante_activo.generar_grafica_objeto(guardar=False)
                input('\nPulsa Enter...')
                self.limpiar_pantalla()
            elif opcion == "5": 
                self.estudiante_activo.generar_pdf_objeto()
                input('\nPulsa Enter...')
                self.limpiar_pantalla()
            elif opcion == "6": self.borrar_cursos_menu()
            elif opcion == "7": 
                self.estudiante_activo.mostrar_estadisticas_objeto()
                input('\nPulsa Enter...')
                self.limpiar_pantalla()
            elif opcion == "8": 
                self.guardar_objeto_csv()
                print("\n🔄 Volviendo al menú de selección...")
                if not self.menu_inicial():
                    print("\n¡Hasta pronto Sebas!\n")
                    break
            elif opcion == "degly": 
                self.comando_degly_objeto()
            else: 
                self.limpiar_pantalla()


if __name__ == "__main__":
    app = SistemaGestion()
    app.limpiar_pantalla()
    app.inicio()