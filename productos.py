"""
Módulo: gestión de productos e inventario (feature/003-productos-inventario)
Principios: SRP, OCP, DIP

Prueba rápida:
  python productos.py
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, List, Optional


# ===== Dominio =====

@dataclass(frozen=True)
class Producto:
    sku: str
    nombre: str
    stock: int
    precio: float

    @property
    def valor_en_inventario(self) -> float:
        return round(self.stock * self.precio, 2)


# ===== Puertos (DIP) =====

class IProductoRepo(Protocol):
    def guardar(self, p: Producto) -> None: ...
    def obtener(self, sku: str) -> Optional[Producto]: ...
    def listar(self) -> List[Producto]: ...
    def actualizar(self, p: Producto) -> None: ...


# ===== Infra: repo en memoria =====

class ProductoRepoMem(IProductoRepo):
    def __init__(self) -> None:
        self._data: Dict[str, Producto] = {}

    def guardar(self, p: Producto) -> None:
        if p.sku in self._data:
            raise ValueError(f"SKU duplicado: {p.sku}")
        self._data[p.sku] = p

    def obtener(self, sku: str) -> Optional[Producto]:
        return self._data.get(sku)

    def listar(self) -> List[Producto]:
        return list(self._data.values())

    def actualizar(self, p: Producto) -> None:
        if p.sku not in self._data:
            raise KeyError(f"SKU no existe: {p.sku}")
        self._data[p.sku] = p


# ===== Servicio de aplicación =====

class ProductoInvalido(Exception): ...

class ProductoService:
    def __init__(self, repo: IProductoRepo) -> None:
        self._repo = repo

    def registrar(self, sku: str, nombre: str, stock: int, precio: float) -> Producto:
        self._validar(sku, nombre, stock, precio)
        p = Producto(sku=sku, nombre=nombre, stock=stock, precio=precio)
        self._repo.guardar(p)
        return p

    def ajustar_stock(self, sku: str, delta: int) -> Producto:
        p = self._repo.obtener(sku)
        if not p:
            raise ProductoInvalido(f"No existe SKU {sku}")
        nuevo = Producto(sku=p.sku, nombre=p.nombre, stock=p.stock + delta, precio=p.precio)
        if nuevo.stock < 0:
            raise ProductoInvalido("El stock no puede ser negativo")
        self._repo.actualizar(nuevo)
        return nuevo

    def listar(self) -> List[Producto]:
        return self._repo.listar()

    def _validar(self, sku: str, nombre: str, stock: int, precio: float) -> None:
        if not sku or len(sku) < 3:
            raise ProductoInvalido("SKU inválido")
        if not nombre or len(nombre) < 3:
            raise ProductoInvalido("Nombre inválido")
        if stock < 0:
            raise ProductoInvalido("Stock no puede ser negativo")
        if precio <= 0:
            raise ProductoInvalido("Precio debe ser mayor a 0")


# ===== Demo rápida =====

def _demo() -> None:
    repo = ProductoRepoMem()
    svc = ProductoService(repo)

    print("== Registro de productos ==")
    p1 = svc.registrar("P-001", "Teclado", 10, 25.5)
    p2 = svc.registrar("P-002", "Mouse", 15, 12.0)
    print("✔️ Registrados:", p1, "|", p2)

    print("\n== Ajuste de stock (entrada +5 a P-001) ==")
    p1 = svc.ajustar_stock("P-001", +5)
    print("Nuevo:", p1)

    print("\n== Inventario ==")
    for p in svc.listar():
        print(f"- {p.sku} | {p.nombre} | stock={p.stock} | precio={p.precio} | valor={p.valor_en_inventario}")

if __name__ == "__main__":
    _demo()
