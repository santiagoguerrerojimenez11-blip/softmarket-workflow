"""
Módulo: Reportes de Ventas
(feature/004-reportes-ventas)

Principios aplicados:
- SRP: cada clase tiene su responsabilidad.
- OCP: se pueden agregar nuevos tipos de reportes sin modificar el servicio.
- DIP: el servicio depende de una abstracción, no de una implementación concreta.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List
from datetime import date

# ============
# Dominio
# ============

@dataclass(frozen=True)
class Venta:
    id_venta: str
    cliente: str
    producto: str
    cantidad: int
    precio_unitario: float
    fecha: date

    @property
    def total(self) -> float:
        return self.cantidad * self.precio_unitario


# ============
# Repositorio
# ============

class IVentaRepo(Protocol):
    def registrar(self, venta: Venta) -> None: ...
    def listar(self) -> List[Venta]: ...


class VentaRepoMem:
    def __init__(self):
        self._ventas: List[Venta] = []

    def registrar(self, venta: Venta) -> None:
        self._ventas.append(venta)

    def listar(self) -> List[Venta]:
        return list(self._ventas)


# ============
# Servicio
# ============

class ReporteVentasService:
    def __init__(self, repo: IVentaRepo):
        self._repo = repo

    def total_general(self) -> float:
        return sum(v.total for v in self._repo.listar())

    def total_por_cliente(self, cliente: str) -> float:
        return sum(v.total for v in self._repo.listar() if v.cliente == cliente)

    def total_por_producto(self, producto: str) -> float:
        return sum(v.total for v in self._repo.listar() if v.producto == producto)


# ============
# Demo rápida
# ============

def _demo() -> None:
    repo = VentaRepoMem()
    svc = ReporteVentasService(repo)

    v1 = Venta("V-001", "Carlos", "Teclado", 2, 25.5, date(2025, 10, 14))
    v2 = Venta("V-002", "Santiago", "Mouse", 3, 12.0, date(2025, 10, 14))
    v3 = Venta("V-003", "Carlos", "Monitor", 1, 80.0, date(2025, 10, 14))

    repo.registrar(v1)
    repo.registrar(v2)
    repo.registrar(v3)

    print("\n== Ventas registradas ==")
    for v in repo.listar():
        print(f"{v.id_venta}: {v.cliente} compró {v.cantidad}x {v.producto} por ${v.total}")

    print("\n== Totales ==")
    print(f"Total general: ${svc.total_general()}")
    print(f"Total Carlos: ${svc.total_por_cliente('Carlos')}")
    print(f"Total Mouse: ${svc.total_por_producto('Mouse')}")


if __name__ == "__main__":
    _demo()
