"""
Módulo: facturación y descuentos (feature/002-facturacion-descuentos)
Principios aplicados: SRP, OCP, DIP

- SRP: cada clase tiene su responsabilidad (item, estrategia de descuento, cálculo).
- OCP: puedes agregar nuevas estrategias de descuento sin tocar el servicio.
- DIP: el servicio depende de una abstracción (IDiscountStrategy), no de una concreta.

Prueba rápida:
    python facturacion.py
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List
from datetime import date


# ==========
# Dominio
# ==========

@dataclass(frozen=True)
class Item:
    sku: str
    nombre: str
    cantidad: int
    precio_unitario: float

    @property
    def subtotal(self) -> float:
        return round(self.cantidad * self.precio_unitario, 2)


# ===========================
# Estrategias de Descuento
# ===========================

class IDiscountStrategy(Protocol):
    def aplicar(self, monto: float) -> float:
        """Devuelve el monto con descuento aplicado."""


@dataclass(frozen=True)
class DescuentoNulo(IDiscountStrategy):
    def aplicar(self, monto: float) -> float:
        return round(monto, 2)


@dataclass(frozen=True)
class DescuentoPorcentaje(IDiscountStrategy):
    porcentaje: float  # 0..100

    def aplicar(self, monto: float) -> float:
        if self.porcentaje < 0 or self.porcentaje > 100:
            raise ValueError("Porcentaje de descuento inválido (0..100).")
        return round(monto * (1 - self.porcentaje / 100.0), 2)


@dataclass(frozen=True)
class DescuentoFijo(IDiscountStrategy):
    monto_fijo: float  # >= 0

    def aplicar(self, monto: float) -> float:
        if self.monto_fijo < 0:
            raise ValueError("El descuento fijo no puede ser negativo.")
        return round(max(0.0, monto - self.monto_fijo), 2)


# ===========================
# Servicio de Facturación
# ===========================

@dataclass
class Factura:
    numero: str
    fecha: date
    items: List[Item]
    subtotal: float
    total_con_descuento: float
    estrategia_descuento: IDiscountStrategy


class FacturacionService:
    def __init__(self, estrategia: IDiscountStrategy) -> None:
        self._estrategia = estrategia

    def calcular(self, numero: str, items: List[Item]) -> Factura:
        if not items:
            raise ValueError("La factura debe contener al menos un item.")
        subtotal = round(sum(i.subtotal for i in items), 2)
        total = self._estrategia.aplicar(subtotal)
        return Factura(
            numero=numero,
            fecha=date.today(),
            items=items,
            subtotal=subtotal,
            total_con_descuento=total,
            estrategia_descuento=self._estrategia,
        )


# ==========
# Demo
# ==========

def _demo() -> None:
    items = [
        Item(sku="A100", nombre="Teclado", cantidad=2, precio_unitario=25.0),
        Item(sku="B200", nombre="Mouse",   cantidad=1, precio_unitario=18.5),
        Item(sku="C300", nombre="Pad",     cantidad=3, precio_unitario=5.75),
    ]

    print("== Sin descuento ==")
    s1 = FacturacionService(DescuentoNulo())
    f1 = s1.calcular("F-0001", items)
    print(f"Subtotal: {f1.subtotal} | Total: {f1.total_con_descuento}")

    print("\n== Descuento 10% ==")
    s2 = FacturacionService(DescuentoPorcentaje(10))
    f2 = s2.calcular("F-0002", items)
    print(f"Subtotal: {f2.subtotal} | Total: {f2.total_con_descuento}")

    print("\n== Descuento fijo 8.00 ==")
    s3 = FacturacionService(DescuentoFijo(8.0))
    f3 = s3.calcular("F-0003", items)
    print(f"Subtotal: {f3.subtotal} | Total: {f3.total_con_descuento}")


if __name__ == "__main__":
    _demo()
