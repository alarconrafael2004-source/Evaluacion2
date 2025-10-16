import requests
import sys

class NavegadorBiblioteca:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url_base = "https://graphhopper.com/api/1/route"
        
        self.biblioteca = {
            "lat": -33.4419,
            "lng": -70.6453,
            "nombre": "Biblioteca Nacional de Chile, Av. Libertador Bernardo O'Higgins 651, Santiago"
        }
    
    def obtener_ubicacion_usuario(self, mensaje):
        while True:
            try:
                entrada = input(mensaje).strip()
                
                if entrada.lower() in ['s', 'salir']:
                    return None
                if entrada.lower() in ['m', 'menu']:
                    return 'menu'
                
                # Verificar si son coordenadas
                if ',' in entrada:
                    partes = entrada.split(',')
                    if len(partes) == 2:
                        try:
                            latitud = float(partes[0].strip())
                            longitud = float(partes[1].strip())
                            if -90 <= latitud <= 90 and -180 <= longitud <= 180:
                                return {
                                    "lat": latitud,
                                    "lng": longitud,
                                    "nombre": f"Ubicación en ({latitud:.4f}, {longitud:.4f})"
                                }
                        except ValueError:
                            print("Error: Formato de coordenadas incorrecto")
                
                # Buscar como dirección
                print("Buscando dirección...")
                return self.buscar_por_direccion(entrada)
                
            except KeyboardInterrupt:
                print("\nPrograma interrumpido por el usuario.")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
    
    def buscar_por_direccion(self, direccion):
        """Busca coordenadas usando una dirección"""
        try:
            url = "https://graphhopper.com/api/1/geocode"
            parametros = {
                'q': direccion + ", Chile",
                'key': self.api_key,
                'limit': 1,
                'locale': 'es'
            }
            
            respuesta = requests.get(url, params=parametros, timeout=10)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if datos.get('hits'):
                    lugar = datos['hits'][0]
                    nombre_lugar = lugar.get('name', direccion)
                    ciudad = lugar.get('city', '')
                    
                    direccion_completa = nombre_lugar
                    if ciudad:
                        direccion_completa += f", {ciudad}"
                    
                    return {
                        "lat": lugar['point']['lat'],
                        "lng": lugar['point']['lng'],
                        "nombre": direccion_completa
                    }
                else:
                    print("No se encontró la dirección. Intente con otra ubicación.")
                    return None
            else:
                print("Error en la búsqueda de dirección")
                return None
                
        except Exception as e:
            print(f"Error al buscar dirección: {e}")
            return None
    
    def calcular_ruta_biblioteca(self, origen, medio_transporte='car'):
        """Calcula la ruta desde el origen hasta la biblioteca"""
        try:
            punto_origen = f"{origen['lat']},{origen['lng']}"
            punto_biblioteca = f"{self.biblioteca['lat']},{self.biblioteca['lng']}"
            
            parametros = {
                'point': [punto_origen, punto_biblioteca],
                'vehicle': medio_transporte,
                'key': self.api_key,
                'instructions': True,
                'locale': 'es',
                'points_encoded': False
            }
            
            print("Calculando ruta a la Biblioteca Nacional...")
            respuesta = requests.get(self.url_base, params=parametros, timeout=30)
            
            if respuesta.status_code == 200:
                return respuesta.json()
            else:
                print("Error en el cálculo de la ruta")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def formatear_tiempo(self, segundos):
        """Convierte segundos a formato legible"""
        try:
            segundos = int(segundos)
            minutos = segundos // 60
            
            if minutos < 60:
                return f"{minutos} minutos"
            
            horas = minutos // 60
            minutos_restantes = minutos % 60
            
            if minutos_restantes == 0:
                return f"{horas} horas"
            else:
                return f"{horas} horas y {minutos_restantes} minutos"
        except:
            return "tiempo no disponible"
    
    def formatear_distancia(self, metros):
        """Convierte metros a formato legible"""
        try:
            metros = float(metros)
            if metros < 1000:
                return f"{metros:.0f} metros"
            else:
                return f"{metros/1000:.2f} kilómetros"
        except:
            return "distancia no disponible"
    
    def mostrar_comparacion_transportes(self, origen):
        """Muestra comparación entre todos los medios de transporte disponibles"""
        print("\n--- COMPARACIÓN DE MEDIOS DE TRANSPORTE ---")
        
        medios_transporte = [
            ('car', 'Auto'),
            ('bike', 'Bicicleta'),
            ('foot', 'Caminando')
        ]
        
        resultados = []
        
        for medio, nombre in medios_transporte:
            ruta = self.calcular_ruta_biblioteca(origen, medio)
            if ruta and ruta.get('paths'):
                datos_ruta = ruta['paths'][0]
                distancia = datos_ruta.get('distance', 0)
                tiempo = datos_ruta.get('time', 0)
                
                resultados.append({
                    'medio': nombre,
                    'distancia': distancia,
                    'tiempo': tiempo,
                    'datos_ruta': ruta
                })
                
                print(f"\n{nombre.upper()}:")
                print(f"  • Distancia: {self.formatear_distancia(distancia)}")
                print(f"  • Tiempo estimado: {self.formatear_tiempo(tiempo//1000)}")
                
                # Recomendaciones específicas por medio de transporte
                if medio == 'car':
                    print(f"  • Recomendación: Ideal para distancias largas")
                    print(f"  • Consideración: Tráfico y estacionamiento")
                elif medio == 'bike':
                    print(f"  • Recomendación: Excelente para distancias medias")
                    print(f"  • Consideración: Vías ciclistas disponibles")
                elif medio == 'foot':
                    if distancia < 2000:
                        print(f"  • Recomendación: Perfecto para esta distancia")
                    else:
                        print(f"  • Recomendación: Considerar transporte público")
        
        return resultados
    
    def mostrar_instrucciones_detalladas(self, datos_ruta, origen, medio_transporte):
        """Muestra instrucciones paso a paso para llegar a la biblioteca"""
        if not datos_ruta or 'paths' not in datos_ruta:
            print("No se pudieron obtener las instrucciones de la ruta")
            return
        
        ruta = datos_ruta['paths'][0]
        instrucciones = ruta.get('instructions', [])
        
        print("\n" + "="*60)
        print("INSTRUCCIONES DETALLADAS PARA LLEGAR A LA BIBLIOTECA")
        print("="*60)
        
        # Información general
        distancia = ruta.get('distance', 0)
        tiempo = ruta.get('time', 0)
        
        print(f"Desde: {origen['nombre']}")
        print(f"Hasta: {self.biblioteca['nombre']}")
        print(f"Medio de transporte: {medio_transporte}")
        print(f"Distancia total: {self.formatear_distancia(distancia)}")
        print(f"Tiempo estimado: {self.formatear_tiempo(tiempo//1000)}")
        print("-" * 60)
        
        if instrucciones:
            print("\nINSTRUCCIONES DE NAVEGACIÓN:")
            print("-" * 40)
            
            for numero, instruccion in enumerate(instrucciones, 1):
                texto = instruccion.get('text', 'Continuar')
                distancia_tramo = instruccion.get('distance', 0)
                tiempo_tramo = instruccion.get('time', 0) // 1000
                
                print(f"\nPaso {numero}: {texto}")
                print(f"   - Avance: {self.formatear_distancia(distancia_tramo)}")
                print(f"   - Tiempo: {self.formatear_tiempo(tiempo_tramo)}")
        
        # Información adicional según el medio de transporte
        print("\n" + "="*60)
        print("INFORMACIÓN ADICIONAL:")
        
        if medio_transporte == "Auto":
            print("• Estacionamiento: Disponible en calles aledañas")
            print("• Tráfico: Considere horas punta (7:00-9:30 / 17:30-20:00)")
            print("• Peajes: No hay peajes en esta ruta")
            
        elif medio_transporte == "Bicicleta":
            print("• Ciclovías: Ruta utiliza ciclovías disponibles")
            print("• Seguridad: Use casco y luces reflectantes")
            print("• Estacionamiento: Bicicletero disponible en biblioteca")
            
        elif medio_transporte == "Caminando":
            print("• Accesibilidad: Ruta accesible para peatones")
            print("• Cruces: Utilice pasos peatonales señalizados")
            print("• Tiempo: Lleve agua en días calurosos")
        
        print("="*60)
    
    def mostrar_informacion_transporte_publico(self, origen):
        """Proporciona información sobre transporte público"""
        print("\n--- INFORMACIÓN DE TRANSPORTE PÚBLICO ---")
        print("Para llegar a la Biblioteca Nacional en transporte público:")
        print("\nLíneas de Metro cercanas:")
        print("• Estación Santa Lucía (Línea 1) - 5 minutos caminando")
        print("• Estación Universidad de Chile (Línea 1) - 8 minutos caminando")
        print("• Estación La Moneda (Línea 1) - 10 minutos caminando")
        
        print("\nMicrobuses (Buses):")
        print("• Líneas que pasan por Alameda: 210, 213, 301, 345, 385")
        print("• Líneas que pasan por Miraflores: 201, 226, 401")
        
        print("\nRecomendaciones:")
        print("• Use la aplicación 'Moovit' para rutas actualizadas")
        print("• Considere tarjeta BIP! para todos los transportes")
        print("• Horario biblioteca: Lunes a Viernes 9:00-19:00")
    
    def calcular_ruta_completa(self):
        """Flujo completo para calcular ruta a la biblioteca"""
        print("\n--- RUTA A LA BIBLIOTECA NACIONAL ---")
        print("Destino: Biblioteca Nacional de Chile")
        print("Ubicación: Av. Libertador Bernardo O'Higgins 651, Santiago")
        print("-" * 50)
        
        # Obtener ubicación del usuario
        origen = self.obtener_ubicacion_usuario("\n¿Desde dónde parte? (dirección o coordenadas): ")
        if origen is None or origen == 'menu':
            return
        
        print(f"\nUbicación de partida: {origen['nombre']}")
        
        # Mostrar comparación de todos los transportes
        resultados = self.mostrar_comparacion_transportes(origen)
        
        if not resultados:
            print("No se pudieron calcular rutas. Intente con otra ubicación.")
            return
        
        # Seleccionar medio de transporte
        print("\n--- SELECCIÓN DE MEDIO DE TRANSPORTE ---")
        print("1. En auto (más rápido para distancias largas)")
        print("2. En bicicleta (ecológico y saludable)")
        print("3. Caminando (ideal para distancias cortas)")
        print("4. Información de transporte público")
        
        while True:
            opcion = input("\nSeleccione cómo quiere viajar (1-4): ").strip()
            
            if opcion == '1' and any(r['medio'] == 'Auto' for r in resultados):
                transporte = 'Auto'
                datos_ruta = next(r['datos_ruta'] for r in resultados if r['medio'] == 'Auto')
                break
            elif opcion == '2' and any(r['medio'] == 'Bicicleta' for r in resultados):
                transporte = 'Bicicleta'
                datos_ruta = next(r['datos_ruta'] for r in resultados if r['medio'] == 'Bicicleta')
                break
            elif opcion == '3' and any(r['medio'] == 'Caminando' for r in resultados):
                transporte = 'Caminando'
                datos_ruta = next(r['datos_ruta'] for r in resultados if r['medio'] == 'Caminando')
                break
            elif opcion == '4':
                self.mostrar_informacion_transporte_publico(origen)
                return
            else:
                print("Opción inválida o no disponible. Seleccione 1, 2, 3 o 4")
        
        # Mostrar instrucciones detalladas
        self.mostrar_instrucciones_detalladas(datos_ruta, origen, transporte)
    
    def mostrar_informacion_biblioteca(self):
        """Muestra información sobre la Biblioteca Nacional"""
        print("\n--- INFORMACIÓN DE LA BIBLIOTECA NACIONAL ---")
        print("• Nombre: Biblioteca Nacional de Chile")
        print("• Dirección: Av. Libertador Bernardo O'Higgins 651, Santiago")
        print("• Horario atención: Lunes a Viernes 9:00 - 19:00 horas")
        print("• Servicios disponibles:")
        print("  - Sala de lectura y estudio")
        print("  - Préstamo de libros")
        print("  - Archivos históricos y documentos")
        print("  - Acceso a bases de datos")
        print("  - Visitas guiadas")
        print("• Acceso: Público general, entrada gratuita")
        print("• Contacto: +56 2 2360 5600")
        print("-" * 50)
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema"""
        print("\n=== SISTEMA DE NAVEGACIÓN ===")
        print("Bienvenido al sistema de rutas a la Biblioteca Nacional")
        print("\nOpciones disponibles:")
        print("1. Calcular ruta a la Biblioteca Nacional")
        print("2. Información sobre la Biblioteca")
        print("3. Salir del sistema")
        
        while True:
            opcion = input("\nSeleccione una opción (1-3): ").strip()
            if opcion in ['1', '2', '3']:
                return opcion
            else:
                print("Opción inválida. Por favor seleccione 1, 2 o 3")
    
    def ejecutar(self):
        """Función principal que ejecuta el sistema"""
        print("Sistema de Navegación a la Biblioteca Nacional")
        print("Conectado al servicio de mapas...")
        
        while True:
            try:
                opcion = self.mostrar_menu_principal()
                
                if opcion == '1':
                    self.calcular_ruta_completa()
                elif opcion == '2':
                    self.mostrar_informacion_biblioteca()
                elif opcion == '3':
                    print("\nGracias por usar el sistema de navegación")
                    print("¡Esperamos verlo en la Biblioteca Nacional!")
                    break
                
                # Pausa antes de mostrar el menú nuevamente
                if opcion != '3':
                    input("\nPresione Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\nPrograma finalizado por el usuario")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")

def main():
    """Función principal del programa"""
    LLAVE_API = "f51d1500-474c-4a21-8275-eb882e0ecc33"
    
    try:
        navegador = NavegadorBiblioteca(LLAVE_API)
        navegador.ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma finalizado")
    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    main()

