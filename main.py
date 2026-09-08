# -*- coding: utf-8 -*-
"""
Programa principal.
El main NO conoce cómo FractalEngine dibuja ni cómo MemoryAuditor mide:
solo llama a sus contratos públicos (barrera de abstracción total).
"""

import sys
import time

from memory_auditor import MemoryAuditor
from fractal_engine import ArbolFractal
from prueba_colapso import encontrar_n_maximo


def demo(nivel=6):
    print(f"\n=== DEMO: árbol fractal a profundidad n={nivel} ===\n")
    auditor = MemoryAuditor()
    auditor.iniciar_medicion()

    motor = ArbolFractal(alto=nivel + 2, ancho=(nivel + 2) * 2, auditor=auditor)
    motor.generar(nivel)

    reporte = auditor.detener_medicion()
    print(motor.render())
    print("\n--- Reporte de auditoría ---")
    for k, v in reporte.items():
        print(f"  {k}: {v}")


def prueba_estres_fractal(nivel_max=22, limite_segundos=2.0):
    """
    Incrementa la profundidad del árbol y mide tiempo / llamadas / memoria.
    'Colapso práctico' = el tiempo de una sola ejecución supera el límite,
    evidenciando la explosión combinatoria O(2^n).
    """
    print("\n=== PRUEBA DE ESTRÉS: FractalEngine (crecimiento exponencial) ===")
    print(f"{'n':>3} | {'llamadas totales':>17} | {'prof. pila':>10} | {'tiempo (s)':>10} | {'memoria (KB)':>12}")
    print("-" * 68)

    n_colapso = None
    for n in range(1, nivel_max + 1):
        auditor = MemoryAuditor()
        auditor.iniciar_medicion()
        motor = ArbolFractal(alto=n + 2, ancho=(n + 2) * 2, auditor=auditor)

        inicio = time.perf_counter()
        motor.generar(n)
        duracion = time.perf_counter() - inicio

        reporte = auditor.detener_medicion()
        print(f"{n:>3} | {reporte['total_llamadas']:>17} | {reporte['profundidad_maxima']:>10} | "
              f"{duracion:>10.4f} | {reporte['memoria_pico_kb']:>12}")

        if duracion > limite_segundos and n_colapso is None:
            n_colapso = n
            print(f"\n>>> COLAPSO PRÁCTICO en n={n}: el tiempo de ejecución superó "
                  f"{limite_segundos}s por la explosión combinatoria O(2^n).")
            break

    return n_colapso


def prueba_estres_pila():
    """
    Encuentra el n_max real que soporta la pila de Python (RecursionError),
    usando la recursión lineal auxiliar de prueba_colapso.py.
    """
    print("\n=== PRUEBA DE ESTRÉS: Stack Overflow real (recursión lineal) ===")
    print(f"Límite de recursión configurado por Python: {sys.getrecursionlimit()}")

    auditor = MemoryAuditor()
    n_max, reporte = encontrar_n_maximo(auditor)

    print(f"\nn máximo soportado sin colapso: {n_max}")
    print("--- Reporte de auditoría en el punto de colapso ---")
    for k, v in reporte.items():
        print(f"  {k}: {v}")
    return n_max, reporte


if __name__ == "__main__":
    demo(nivel=6)
    prueba_estres_fractal(nivel_max=22, limite_segundos=2.0)
    prueba_estres_pila()
