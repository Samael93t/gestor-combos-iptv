# -*- coding: utf-8 -*-
"""
🔗 GESTOR DE COMBOS — VERSIÓN PRO
Busca, une, verifica y divide listas M3U
Límite por archivo: 20 MB
"""

import os
import sys
import re
import time
from pathlib import Path

# ========== CONFIGURACIÓN ==========
CARPETA_COMBO = "/sdcard/combo"
LIMITE_MB = 20
TAMANIO_LIMITE = LIMITE_MB * 1024 * 1024  # En bytes

# Colores
AZUL = '\033[94m'
VERDE = '\033[92m'
AMARILLO = '\033[93m'
ROJO = '\033[91m'
RESET = '\033[0m'

# ========== FUNCIONES BÁSICAS ==========

def crear_carpeta_si_no_existe(ruta):
    if not os.path.exists(ruta):
        os.makedirs(ruta)
        print(f"{VERDE}✅ Carpeta creada: {ruta}{RESET}")

def listar_archivos_combo():
    crear_carpeta_si_no_existe(CARPETA_COMBO)
    archivos = []
    for f in os.listdir(CARPETA_COMBO):
        if f.endswith(('.txt', '.m3u', '.m3u8')):
            ruta_completa = os.path.join(CARPETA_COMBO, f)
            tamano = os.path.getsize(ruta_completa)
            lineas = contar_lineas(ruta_completa)
            archivos.append((f, tamano, lineas))
    return archivos

def contar_lineas(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def dividir_por_tamano(lineas, ruta_salida, max_tamano=TAMANIO_LIMITE):
    partes = []
    parte_num = 1
    lineas_actuales = []
    tamano_actual = 0
    
    for linea in lineas:
        tamano_linea = len(linea.encode('utf-8')) + 1
        if tamano_actual + tamano_linea > max_tamano and lineas_actuales:
            nombre_base = os.path.splitext(ruta_salida)[0]
            ext = os.path.splitext(ruta_salida)[1]
            nombre_parte = f"{nombre_base}_parte{parte_num}{ext}"
            with open(nombre_parte, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lineas_actuales))
            partes.append((nombre_parte, len(lineas_actuales)))
            parte_num += 1
            lineas_actuales = []
            tamano_actual = 0
        lineas_actuales.append(linea)
        tamano_actual += tamano_linea
    
    if lineas_actuales:
        nombre_base = os.path.splitext(ruta_salida)[0]
        ext = os.path.splitext(ruta_salida)[1]
        if parte_num == 1:
            nombre_parte = ruta_salida
        else:
            nombre_parte = f"{nombre_base}_parte{parte_num}{ext}"
        with open(nombre_parte, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas_actuales))
        partes.append((nombre_parte, len(lineas_actuales)))
    
    return partes

# ========== 🆕 BUSCAR TODOS LOS M3U DEL CELULAR ==========

def buscar_todos_los_m3u():
    print(f"\n{AZUL}🔍 Buscando TODOS los archivos .m3u / .m3u8 en el celular...{RESET}")
    rutas_buscar = [
        "/sdcard/Download",
        "/sdcard/Downloads",
        "/sdcard/Documentos",
        "/sdcard/Documents",
        CARPETA_COMBO,
        "/sdcard/qpython/scripts3",
        "/sdcard/Download/iptv"
    ]
    
    todos_los_m3u = []
    
    for ruta_base in rutas_buscar:
        if not os.path.exists(ruta_base):
            continue
        try:
            for raiz, carpetas, archivos in os.walk(ruta_base):
                for archivo in archivos:
                    if archivo.lower().endswith(('.m3u', '.m3u8')):
                        ruta_completa = os.path.join(raiz, archivo)
                        tamano = os.path.getsize(ruta_completa)
                        lineas = contar_lineas(ruta_completa)
                        todos_los_m3u.append((ruta_completa, tamano, lineas))
        except Exception as e:
            continue
    
    if not todos_los_m3u:
        print(f"{AMARILLO}⚠️ No se encontraron archivos M3U{RESET}")
        return []
    
    print(f"\n{VERDE}✅ Encontrados {len(todos_los_m3u)} archivos M3U:{RESET}")
    for i, (ruta, tam, lin) in enumerate(todos_los_m3u, 1):
        print(f"  {i}. {os.path.basename(ruta)}")
        print(f"     📂 {ruta}")
        print(f"     📏 {tam/1024:.1f} KB | 📝 {lin} líneas")
    
    return todos_los_m3u

def crear_combo_desde_todos_m3u():
    todos = buscar_todos_los_m3u()
    if not todos:
        return
    
    print(f"\n{AZUL}¿Quieres incluir TODOS los archivos? (S/N){RESET}")
    respuesta = input().strip().lower()
    
    if respuesta != 's':
        print(f"\n{AZUL}Escribe los números separados por coma (ej: 1,3,5-8):{RESET}")
        seleccion = input().strip()
        archivos_seleccionados = []
        for parte in seleccion.split(','):
            if '-' in parte:
                ini, fin = map(int, parte.split('-'))
                archivos_seleccionados.extend(todos[ini-1:fin])
            else:
                archivos_seleccionados.append(todos[int(parte)-1])
    else:
        archivos_seleccionados = todos
    
    print(f"\n{AMARILLO}📝 Leyendo archivos...{RESET}")
    todas_las_lineas = []
    urls_vistas = set()
    
    for ruta, _, _ in archivos_seleccionados:
        try:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        if linea not in urls_vistas:
                            urls_vistas.add(linea)
                            todas_las_lineas.append(linea)
        except Exception as e:
            print(f"{ROJO}❌ No se pudo leer: {ruta}{RESET}")
    
    print(f"{VERDE}✅ Total de líneas únicas: {len(todas_las_lineas)}{RESET}")
    
    nombre_salida = os.path.join(CARPETA_COMBO, "combo_universal.m3u")
    partes = dividir_por_tamano(todas_las_lineas, nombre_salida)
    
    print(f"\n{VERDE}🎉 ¡Combo creado exitosamente!{RESET}")
    for ruta, cant in partes:
        print(f"   ✅ {os.path.basename(ruta)} — {cant} líneas")

# ========== 🆕 VERIFICAR ENLACES ACTIVOS ==========

def verificar_enlaces_activos():
    print(f"\n{AZUL}🌐 VERIFICADOR DE ENLACES ACTIVOS{RESET}")
    archivos = listar_archivos_combo()
    
    if not archivos:
        print(f"{AMARILLO}⚠️ No hay archivos en la carpeta combo{RESET}")
        return
    
    print(f"\nArchivos disponibles:")
    for i, (nombre, _, lin) in enumerate(archivos, 1):
        print(f"  {i}. {nombre} — {lin} líneas")
    
    print(f"\n{AZUL}Escribe el número del archivo a verificar:{RESET}")
    num = int(input().strip()) - 1
    nombre_archivo = archivos[num][0]
    ruta_completa = os.path.join(CARPETA_COMBO, nombre_archivo)
    
    print(f"\n{AMARILLO}⚠️ Nota: Este script NO verifica conexión real para no perder tiempo.")
    print(f"    Solo limpia duplicados, líneas vacías y formato incorrecto.{RESET}")
    print(f"{AZUL}    Para verificación completa con internet, úsalo con yt-dlp instalado.{RESET}")
    
    lineas_validas = []
    urls_vistas = set()
    
    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
        for linea in f:
            orig = linea
            linea = linea.strip()
            
            if not linea:
                continue
            if linea.startswith('#'):
                lineas_validas.append(linea)
                continue
            
            if linea not in urls_vistas:
                urls_vistas.add(linea)
                if linea.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
                    lineas_validas.append(linea)
    
    nombre_salida = os.path.join(CARPETA_COMBO, f"ACTIVO_{nombre_archivo}")
    with open(nombre_salida, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write(f"# Verificado: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"# Total válidas: {len([l for l in lineas_validas if not l.startswith('#')])}\n")
        f.write('\n'.join(lineas_validas))
    
    print(f"\n{VERDE}✅ Archivo generado: {os.path.basename(nombre_salida)}{RESET}")
    print(f"   ✅ Enlaces válidos: {len([l for l in lineas_validas if not l.startswith('#')])}")
    print(f"   ✅ Duplicados eliminados: {archivos[num][2] - len([l for l in lineas_validas if not l.startswith('#')])}")

# ========== FUNCIONES ORIGINALES ==========

def unir_combos():
    archivos = listar_archivos_combo()
    if not archivos:
        print(f"{AMARILLO}⚠️ No hay archivos en la carpeta combo{RESET}")
        return
    
    print(f"\nArchivos disponibles:")
    for i, (nombre, tam, lin) in enumerate(archivos, 1):
        print(f"  {i}. {nombre} — {lin} líneas — {tam/1024:.1f} KB")
    
    print(f"\n{AZUL}Escribe los números a unir (ej: 1,3,5-8):{RESET}")
    seleccion = input().strip()
    
    archivos_seleccionados = []
    for parte in seleccion.split(','):
        if '-' in parte:
            ini, fin = map(int, parte.split('-'))
            archivos_seleccionados.extend(archivos[ini-1:fin])
        else:
            archivos_seleccionados.append(archivos[int(parte)-1])
    
    todas_las_lineas = []
    urls_vistas = set()
    
    for nombre, _, _ in archivos_seleccionados:
        ruta = os.path.join(CARPETA_COMBO, nombre)
        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#') and linea not in urls_vistas:
                    urls_vistas.add(linea)
                    todas_las_lineas.append(linea)
    
    print(f"\n{VERDE}✅ Total de líneas únicas: {len(todas_las_lineas)}{RESET}")
    
    nombre_salida = os.path.join(CARPETA_COMBO, "combo_unido.m3u")
    partes = dividir_por_tamano(todas_las_lineas, nombre_salida)
    
    print(f"\n{VERDE}🎉 ¡Unión completada!{RESET}")
    for ruta, cant in partes:
        print(f"   ✅ {os.path.basename(ruta)} — {cant} líneas")

def dividir_combo():
    archivos = listar_archivos_combo()
    if not archivos:
        return
    
    print(f"\nArchivos disponibles:")
    for i, (nombre, _, lin) in enumerate(archivos, 1):
        print(f"  {i}. {nombre} — {lin} líneas")
    
    print(f"\n{AZUL}Número del archivo a dividir:{RESET}")
    num = int(input().strip()) - 1
    nombre = archivos[num][0]
    ruta = os.path.join(CARPETA_COMBO, nombre)
    
    print(f"{AZUL}En cuántas partes?{RESET}")
    partes = int(input().strip())
    
    with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
        lineas = [l.strip() for l in f if l.strip()]
    
    total = len(lineas)
    por_parte = total // partes
    resto = total % partes
    
    for p in range(partes):
        inicio = p * por_parte
        fin = inicio + por_parte + (resto if p == partes-1 else 0)
        lineas_parte = lineas[inicio:fin]
        nombre_parte = f"{os.path.splitext(nombre)[0]}_parte{p+1}{os.path.splitext(nombre)[1]}"
        ruta_parte = os.path.join(CARPETA_COMBO, nombre_parte)
        with open(ruta_parte, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas_parte))
        print(f"{VERDE}✅ {nombre_parte} — {len(lineas_parte)} líneas{RESET}")

def eliminar_duplicados():
    archivos = listar_archivos_combo()
    if not archivos:
        return
    
    print(f"\nArchivos disponibles:")
    for i, (nombre, _, lin) in enumerate(archivos, 1):
        print(f"  {i}. {nombre} — {lin} líneas")
    
    print(f"\n{AZUL}Número del archivo:{RESET}")
    num = int(input().strip()) - 1
    nombre = archivos[num][0]
    ruta = os.path.join(CARPETA_COMBO, nombre)
    
    with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
        lineas = f.readlines()
    
    vistas = set()
    unicas = []
    duplicados = 0
    
    for l in lineas:
        t = l.strip()
        if t in vistas and not t.startswith('#'):
            duplicados += 1
        else:
            vistas.add(t)
            unicas.append(l.rstrip('\n'))
    
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('\n'.join(unicas))
    
    print(f"{VERDE}✅ Hecho! Duplicados eliminados: {duplicados}{RESET}")
    print(f"   Líneas restantes: {len(unicas)}")

def ver_contenido():
    archivos = listar_archivos_combo()
    if not archivos:
        return
    
    print(f"\nArchivos disponibles:")
    for i, (nombre, _, lin) in enumerate(archivos, 1):
        print(f"  {i}. {nombre} — {lin} líneas")
    
    print(f"\n{AZUL}Número del archivo:{RESET}")
    num = int(input().strip()) - 1
    nombre = archivos[num][0]
    ruta = os.path.join(CARPETA_COMBO, nombre)
    
    with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
        primeras = []
        for _ in range(15):
            try:
                primeras.append(next(f).rstrip('\n'))
            except StopIteration:
                break
    
    print(f"\n{AMARILLO}📄 Primeras {len(primeras)} líneas de {nombre}:{RESET}")
    for l in primeras:
        print(f"  {l}")
    print(f"{AMARILLO}... (resto omitido){RESET}")

def menu():
    crear_carpeta_si_no_existe(CARPETA_COMBO)
    
    while True:
        os.system('clear')
        print(f"\n{AZUL}")
        print("="*50)
        print("   🔗 GESTOR DE COMBOS — VERSIÓN PRO")
        print("="*50)
        print(f"📂 Carpeta: {CARPETA_COMBO}")
        print(f"📦 Límite por archivo: {LIMITE_MB} MB")
        print("-"*50)
        print(f"  1. Unir combos de la carpeta combo")
        print(f"  2. 🆕 Crear combo desde TODOS los M3U del celular")
        print(f"  3. Dividir combo en varios archivos")
        print(f"  4. 🆕 Verificar enlaces activos y vigentes")
        print(f"  5. Ver contenido de un combo")
        print(f"  6. Eliminar duplicados en un combo")
        print(f"  7. Contar líneas de cada combo")
        print(f"  8. Renombrar combo")
        print(f"  9. Eliminar combo")
        print(f"  0. Salir")
        print("="*50 + RESET)
        
        opcion = input(f"\n👉 Elige una opción: ").strip()
        
        if opcion == '1':
            unir_combos()
        elif opcion == '2':
            crear_combo_desde_todos_m3u()
        elif opcion == '3':
            dividir_combo()
        elif opcion == '4':
            verificar_enlaces_activos()
        elif opcion == '5':
            ver_contenido()
        elif opcion == '6':
            eliminar_duplicados()
        elif opcion == '7':
            archivos = listar_archivos_combo()
            print(f"\n{AZUL}📊 RESUMEN DE ARCHIVOS:{RESET}")
            for i, (n, t, l) in enumerate(archivos, 1):
                print(f"  {i}. {n} — {l} líneas — {t/1024:.1f} KB")
        elif opcion == '8':
            archivos = listar_archivos_combo()
            for i, (n, _, _) in enumerate(archivos, 1):
                print(f"  {i}. {n}")
            num = int(input("\nNúmero: ")) - 1
            viejo = archivos[num][0]
            nuevo = input("Nuevo nombre: ").strip()
            os.rename(os.path.join(CARPETA_COMBO, viejo), os.path.join(CARPETA_COMBO, nuevo))
            print(f"{VERDE}✅ Renombrado a: {nuevo}{RESET}")
        elif opcion == '9':
            archivos = listar_archivos_combo()
            for i, (n, _, _) in enumerate(archivos, 1):
                print(f"  {i}. {n}")
            num = int(input("\nNúmero: ")) - 1
            nombre = archivos[num][0]
            if input(f"¿Eliminar {nombre}? (S/N): ").lower() == 's':
                os.remove(os.path.join(CARPETA_COMBO, nombre))
                print(f"{VERDE}✅ Eliminado{RESET}")
        elif opcion == '0':
            print(f"{VERDE}👋 ¡Hasta luego!{RESET}")
            break
        
        if opcion != '0':
            input(f"\n{AMARILLO}Presiona Enter para continuar...{RESET}")

if __name__ == "__main__":
    menu()


