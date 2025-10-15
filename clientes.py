"""
Módulo: gestión y validación de clientes (feature/001-clientes-validacion)
Principios aplicados: SRP, OCP, DIP
- SRP: cada clase tiene una responsabilidad única (validar, almacenar, orquestar).
- OCP: agregar nuevas reglas de validación o un nuevo repositorio sin modificar código existente.
- DIP: el servicio depende de una abstracción (IClienteRepo), no de un repo concreto.

Cómo probar rápido (consola):
    python clientes.py
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol, List, Dict, Optional
import re

# ========
# Dominio
# ========

@dataclass(frozen=True)
class Cliente:
    id: str
    nombre_completo: str
    email: str
    fecha_nacimiento: date

    @property
    def edad(self) -> int:
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

# ======================
# Repositorio abstracto
# ======================

class IClienteRepo(Protocol):
    def agregar(self, cliente: Cliente) -> None: ...
    def listar(self) -> List[Cliente]: ...
    def buscar_por_email(self, email: str) -> Optional[Cliente]: ...

# =====================
# Repositorio en memoria
# =====================

class ClienteRepoMemoria(IClienteRepo):
    def __init__(self):
        self._clientes: Dict[str, Cliente] = {}

    def agregar(self, cliente: Cliente) -> None:
        self._clientes[cliente.id] = cliente

    def listar(self) -> List[Cliente]:
        return list(self._clientes.values())

    def buscar_por_email(self, email: str) -> Optional[Cliente]:
        return next((c for c in self._clientes.values() if c.email == email), None)

# ====================
# Reglas de validación
# ====================

class ClienteInvalido(Exception):
    pass

class ValidadorCliente:
    @staticmethod
    def validar(cliente: Cliente) -> None:
        if not cliente.nombre_completo.strip():
            raise ClienteInvalido("El nombre completo no puede estar vacío.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", cliente.email):
            raise ClienteInvalido("El email no tiene un formato válido.")
        if cliente.edad < 18:
            raise ClienteInvalido("El cliente debe ser mayor de edad.")

# =======================
# Servicio de aplicación
# =======================

class ServicioClientes:
    def __init__(self, repo: IClienteRepo):
        self.repo = repo

    def registrar(self, cliente: Cliente) -> None:
        ValidadorCliente.validar(cliente)
        if self.repo.buscar_por_email(cliente.email):
            raise ClienteInvalido("Ya existe un cliente con ese email.")
        self.repo.agregar(cliente)

    def listar(self) -> List[Cliente]:
        return self.repo.listar()

# ====================
# Ejecución de prueba
# ====================

def _demo():
    def parse_fecha(fecha_str: str) -> date:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()

    repo = ClienteRepoMemoria()
    servicio = ServicioClientes(repo)

    c1 = Cliente(
        id="1",
        nombre_completo="Juan Pérez",
        email="juan@example.com",
        fecha_nacimiento=parse_fecha("1993-03-10"),
    )

    c2 = Cliente(
        id="2",
        nombre_completo="Ana Díaz",
        email="ana@example.com",
        fecha_nacimiento=parse_fecha("2002-07-15"),
    )

    try:
        servicio.registrar(c1)
        print("✅ Cliente 1 registrado:", c1)
    except ClienteInvalido as e:
        print("❌ Error registrando cliente 1:", e)

    try:
        servicio.registrar(c2)
        print("✅ Cliente 2 registrado:", c2)
    except ClienteInvalido as e:
        print("❌ Error registrando cliente 2:", e)

    print("\nClientes en memoria:")
    for cli in servicio.listar():
        print(f"- {cli.id} | {cli.nombre_completo} | {cli.email} | edad={cli.edad}")

if __name__ == "__main__":
    _demo()
