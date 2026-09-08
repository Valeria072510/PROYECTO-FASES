# -*- coding: utf-8 -*-
"""
============================================================
Prueba de colapso real de la pila (Stack Overflow)
============================================================
IMPORTANTE (hallazgo que debe ir en el reporte técnico):

ArbolFractal.generar(n) tiene una pila (stack) de profundidad O(n),
pero un número de LLAMADAS TOTALES de O(2^n). Esto significa que,
para forzar un Stack Overflow real vía el árbol, habría que llegar
a nivel ~ límite de recursión de Python (~1000), lo que exigiría
completar más de 2^1000 llamadas totales: computacionalmente
imposible en cualquier tiempo de vida útil.

En la práctica, el árbol NUNCA colapsa por profundidad de pila:
colapsa por EXPLOSIÓN COMBINATORIA (tiempo/memoria), mucho antes.
Esa es justamente la conclusión de la Parte 3 (Time-Space Tradeoff).

Para exhibir un Stack Overflow real y medir el n_max exacto que
soporta el intérprete, se usa una recursión lineal auxiliar (1 sola
llamada hija por nivel, como pide el profesor: "hasta forzar el
colapso"). Aquí sí la profundidad de pila crece 1:1 con n, así que
el límite se alcanza en segundos.
"""

import sys


def caida_libre(auditor, nivel_objetivo, nivel_actual=1):
    """
    Recursión lineal: cada llamada genera exactamente 1 llamada hija.
    Caso base: nivel_actual >= nivel_objetivo.
    Paso recursivo: nivel_actual + 1.
    """
    auditor.registrar_llamada()
    try:
        if nivel_actual >= nivel_objetivo:
            return nivel_actual
        return caida_libre(auditor, nivel_objetivo, nivel_actual + 1)
    finally:
        auditor.registrar_retorno()


def encontrar_n_maximo(auditor, limite_busqueda=None):
    """
    Incrementa nivel_objetivo hasta que Python lance RecursionError.
    Devuelve (n_maximo_exitoso, reporte_del_auditor_en_el_colapso).
    """
    if limite_busqueda is None:
        limite_busqueda = sys.getrecursionlimit() + 50

    n_maximo_exitoso = 0
    for n in range(1, limite_busqueda):
        auditor.iniciar_medicion()
        try:
            caida_libre(auditor, n)
            n_maximo_exitoso = n
        except RecursionError:
            auditor.marcar_colapso("RecursionError de Python (Stack Overflow real)")
            reporte = auditor.detener_medicion()
            return n_maximo_exitoso, reporte
        finally:
            if auditor._midiendo:
                auditor.detener_medicion()
    return n_maximo_exitoso, auditor.reporte()
