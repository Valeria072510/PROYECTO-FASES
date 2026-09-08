# -*- coding: utf-8 -*-
"""
============================================================
TDA: MemoryAuditor
============================================================
Responsabilidad única: medir el tamaño de la pila de llamadas
(Call Stack) y el consumo de memoria del programa, SIN conocer
qué se está calculando. Este archivo es el "contrato" del TDA:
si otro equipo lo lee, sabe exactamente qué puede esperar de él
sin ver una sola línea de FractalEngine (barrera de abstracción).

------------------------------------------------------------
ESTADO INTERNO (privado, no accesible desde fuera de la clase)
------------------------------------------------------------
    _profundidad_actual : int   -> llamadas activas en este instante
    _profundidad_maxima : int   -> máxima profundidad alcanzada
    _total_llamadas      : int   -> llamadas recursivas acumuladas
    _memoria_pico_bytes   : int   -> pico de memoria real (tracemalloc)
    _colapsado            : bool  -> True si se detectó un fallo
    _motivo_colapso        : str|None

------------------------------------------------------------
INVARIANTE DE REPRESENTACIÓN
------------------------------------------------------------
    1) _profundidad_actual >= 0
    2) _profundidad_maxima >= _profundidad_actual
    3) _total_llamadas >= _profundidad_maxima

------------------------------------------------------------
OPERACIONES (firma, precondición, postcondición)
------------------------------------------------------------
iniciar_medicion() -> None
    pre:  ninguna
    post: contadores en 0, tracemalloc activo.

registrar_llamada() -> None
    pre:  ninguna (se llama al ENTRAR a cada función recursiva)
    post: _profundidad_actual += 1
          _total_llamadas += 1
          _profundidad_maxima = max(_profundidad_maxima, _profundidad_actual)

registrar_retorno() -> None
    pre:  _profundidad_actual > 0
    post: _profundidad_actual -= 1

marcar_colapso(motivo: str) -> None
    pre:  ninguna
    post: _colapsado = True; guarda el motivo y la profundidad exacta
          en la que ocurrió.

detener_medicion() -> dict
    pre:  iniciar_medicion() fue llamado antes
    post: congela la medición de tracemalloc y devuelve reporte()

reporte() -> dict
    post: devuelve {profundidad_maxima, total_llamadas, memoria_pico_kb,
                     colapsado, motivo_colapso} sin modificar el estado.
============================================================
"""

import tracemalloc


class MemoryAuditor:

    def __init__(self):
        self._profundidad_actual = 0
        self._profundidad_maxima = 0
        self._total_llamadas = 0
        self._memoria_pico_bytes = 0
        self._colapsado = False
        self._motivo_colapso = None
        self._midiendo = False

    # ---------------- ciclo de vida ----------------
    def iniciar_medicion(self) -> None:
        self._profundidad_actual = 0
        self._profundidad_maxima = 0
        self._total_llamadas = 0
        self._memoria_pico_bytes = 0
        self._colapsado = False
        self._motivo_colapso = None
        tracemalloc.start()
        self._midiendo = True

    def detener_medicion(self) -> dict:
        if self._midiendo:
            _, pico = tracemalloc.get_traced_memory()
            self._memoria_pico_bytes = pico
            tracemalloc.stop()
            self._midiendo = False
        return self.reporte()

    # ---------------- instrumentación de la pila ----------------
    def registrar_llamada(self) -> None:
        self._profundidad_actual += 1
        self._total_llamadas += 1
        if self._profundidad_actual > self._profundidad_maxima:
            self._profundidad_maxima = self._profundidad_actual

    def registrar_retorno(self) -> None:
        assert self._profundidad_actual > 0, "registrar_retorno() sin llamada previa"
        self._profundidad_actual -= 1

    def marcar_colapso(self, motivo: str) -> None:
        self._colapsado = True
        self._motivo_colapso = f"{motivo} (profundidad máxima alcanzada: {self._profundidad_maxima})"

    # ---------------- salida ----------------
    def reporte(self) -> dict:
        return {
            "profundidad_maxima": self._profundidad_maxima,
            "total_llamadas": self._total_llamadas,
            "memoria_pico_kb": round(self._memoria_pico_bytes / 1024, 2),
            "colapsado": self._colapsado,
            "motivo_colapso": self._motivo_colapso,
        }
