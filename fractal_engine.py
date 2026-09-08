# -*- coding: utf-8 -*-
"""
============================================================
TDA: FractalEngine (clase abstracta)
============================================================
Responsabilidad única: dibujar un patrón fractal recursivo sobre
un canvas de caracteres. NO sabe cómo se audita la memoria; solo
reporta cada entrada/salida de llamada a un colaborador que cumple
el contrato de MemoryAuditor (inyección de dependencia -> barrera
de abstracción total entre ambos TDA).

------------------------------------------------------------
ATRIBUTOS (protegidos)
------------------------------------------------------------
    _canvas   : list[list[str]]   matriz alto x ancho de caracteres
    _auditor  : MemoryAuditor     colaborador inyectado por el main

------------------------------------------------------------
OPERACIONES (firma, precondición, postcondición)
------------------------------------------------------------
generar(nivel: int) -> None      [ABSTRACTO]
    pre:  nivel >= 0
    post: _canvas contiene el patrón dibujado hasta profundidad `nivel`;
          cada llamada recursiva llamó a auditor.registrar_llamada() al
          entrar y auditor.registrar_retorno() al salir (incluso si hubo
          excepción, vía try/finally).

render() -> str
    post: retorna una representación imprimible de _canvas, sin alterarlo.
============================================================
"""

from abc import ABC, abstractmethod


class FractalEngine(ABC):

    def __init__(self, alto: int, ancho: int, auditor):
        self._canvas = [[" "] * ancho for _ in range(alto)]
        self._auditor = auditor

    @abstractmethod
    def generar(self, nivel: int) -> None:
        ...

    def render(self) -> str:
        return "\n".join("".join(fila) for fila in self._canvas)


class ArbolFractal(FractalEngine):
    """
    Implementación concreta: Opción B del anexo (árbol binario recursivo).

    Caso base:
        nivel == 0  o  longitud <= 0   -> se detiene la recursión.
    Paso recursivo:
        Se dibuja el tramo actual y se generan 2 llamadas auto-referenciadas
        (rama izquierda, rama derecha) con longitud - 1 y nivel - 1.

    Complejidad (ver reporte técnico para la justificación completa):
        Tiempo   T(n) = O(2^n)   -> cada nivel duplica las llamadas.
        Espacio  S(n) = O(n)     -> la pila (stack) solo crece con la
                                     profundidad de UNA rama a la vez
                                     (DFS), nunca con el ancho del árbol.
    """

    def __init__(self, alto: int, ancho: int, auditor):
        super().__init__(alto, ancho, auditor)

    def generar(self, nivel: int) -> None:
        assert nivel >= 0, "precondición violada: nivel debe ser >= 0"
        x0 = len(self._canvas[0]) // 2
        y0 = len(self._canvas) - 1
        longitud_inicial = min(nivel, len(self._canvas) - 1)
        self._dibujar_rama(x0, y0, longitud_inicial, angulo=0, nivel=nivel)

    def _dibujar_rama(self, x, y, longitud, angulo, nivel):
        # --- instrumentación: ENTRADA a la llamada ---
        self._auditor.registrar_llamada()
        try:
            # 1. CASO BASE
            if nivel == 0 or longitud <= 0:
                return

            # 2. RENDERIZADO del tramo actual
            char = "|" if angulo == 0 else ("/" if angulo < 0 else "\\")
            for i in range(longitud):
                ny, nx = y - i, x + i * angulo
                if 0 <= ny < len(self._canvas) and 0 <= nx < len(self._canvas[0]):
                    self._canvas[ny][nx] = char

            nuevo_x = x + longitud * angulo
            nuevo_y = y - longitud
            nueva_longitud = longitud - 1
            nuevo_nivel = nivel - 1

            # 3. PASO RECURSIVO (llamadas auto-referenciadas)
            self._dibujar_rama(nuevo_x, nuevo_y, nueva_longitud, -1, nuevo_nivel)  # izquierda
            self._dibujar_rama(nuevo_x, nuevo_y, nueva_longitud, 1, nuevo_nivel)   # derecha
        finally:
            # --- instrumentación: SALIDA de la llamada (siempre se ejecuta) ---
            self._auditor.registrar_retorno()
