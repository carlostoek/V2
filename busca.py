import os
import sys
import argparse
from collections import defaultdict
import re

def buscar_palabra_en_archivos(palabra, ruta, ignorar_mayusculas=True):
    """
    Busca una palabra en todos los archivos de texto en una ruta y sus subcarpetas
    
    Args:
        palabra (str): Palabra a buscar
        ruta (str): Ruta del directorio donde buscar
        ignorar_mayusculas (bool): Si True, no distingue mayúsculas y minúsculas
        
    Returns:
        dict: Resultados organizados por archivo con líneas y conteos
    """
    resultados = defaultdict(lambda: {'conteo': 0, 'lineas': []})
    total_coincidencias = 0
    archivos_procesados = 0
    
    # Patrón de búsqueda (con o sin distinción de mayúsculas)
    patron = re.compile(re.escape(palabra), re.IGNORECASE) if ignorar_mayusculas else re.compile(re.escape(palabra))
    
    # Recorrer todos los archivos en la ruta y subcarpetas
    for raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            
            try:
                # Intentar leer el archivo como texto
                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                    archivos_procesados += 1
                    for num_linea, linea in enumerate(f, 1):
                        coincidencias = patron.findall(linea)
                        if coincidencias:
                            resultados[ruta_completa]['conteo'] += len(coincidencias)
                            resultados[ruta_completa]['lineas'].append(num_linea)
                            total_coincidencias += len(coincidencias)
            except Exception as e:
                # Saltar archivos binarios o con problemas de acceso
                continue
    
    return dict(resultados), total_coincidencias, archivos_procesados

def mostrar_resultados(resultados, total_coincidencias, archivos_procesados):
    """Muestra los resultados de la búsqueda de forma organizada"""
    if not resultados:
        print("\n🔍 No se encontraron coincidencias.")
        return
    
    print(f"\n📊 RESULTADOS DE BÚSQUEDA:")
    print(f"• Archivos con coincidencias: {len(resultados)}")
    print(f"• Coincidencias totales: {total_coincidencias}")
    print(f"• Archivos procesados: {archivos_procesados}\n")
    
    for archivo, datos in resultados.items():
        print(f"📂 Archivo: {archivo}")
        print(f"   → Coincidencias encontradas: {datos['conteo']}")
        
        # Mostrar primeras 5 líneas con coincidencias
        if datos['lineas']:
            lineas_str = ", ".join(map(str, datos['lineas'][:5]))
            if len(datos['lineas']) > 5:
                lineas_str += f", ... (+{len(datos['lineas'])-5} más)"
            print(f"   → Líneas con coincidencias: {lineas_str}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Buscador Avanzado de Palabras en Archivos')
    parser.add_argument('palabra', type=str, help='Palabra a buscar')
    parser.add_argument('-r', '--ruta', type=str, default='.', 
                        help='Ruta donde buscar (por defecto: directorio actual)')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Búsqueda sensible a mayúsculas/minúsculas')
    parser.add_argument('-v', '--version', action='version', version='Buscador 1.0')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.ruta):
        print(f"❌ Error: La ruta '{args.ruta}' no existe.")
        sys.exit(1)
    
    print(f"🔍 Buscando '{args.palabra}' en '{args.ruta}'...")
    resultados, total_coincidencias, archivos_procesados = buscar_palabra_en_archivos(
        args.palabra, 
        args.ruta, 
        not args.case_sensitive
    )
    
    mostrar_resultados(resultados, total_coincidencias, archivos_procesados)

if __name__ == "__main__":
    main()
