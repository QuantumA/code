from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set
from . import commands, events
from typing import NewType


class Product:
    """
    Representa un producto que puede ser comprado.
    """
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        """

        Args:
            sku (str): Se utiliza para identificar un producto (stock-keeping unit)
            batches (List[Batch]): [description]
            version_number (int, optional): [description]. Defaults to 0.
        """
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events = []  # type: List[events.Event]

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            self.events.append(
                events.Allocated(
                    orderid=line.orderid,
                    sku=line.sku,
                    qty=line.qty,
                    batchref=batch.reference,
                )
            )
            return batch.reference
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return None

    def change_batch_quantity(self, ref: str, qty: int):
        batch = next(b for b in self.batches if b.reference == ref)
        batch._purchased_quantity = qty
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(events.Deallocated(line.orderid, line.sku, line.qty))


@dataclass(unsafe_hash=True)
class OrderLine:
    """Reprsenta los pedidos que pueden hacer los clientes.
    Esta tiene un sku y una cantidad (qty)
    """
    orderid: str
    sku: str
    qty: int

Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)
class Batch:
    """El departamento de compras pide pequeños lotes de stock.
       Un lote de stock tiene un ID único llamado referencia, una SKU y una cantidad.

       Tenemos que asignar líneas de pedido a los lotes.
       Cuando hayamos asignado una línea de pedido a un lote, enviaremos las existencias 
       de ese lote específico a la dirección de entrega del cliente.
       Cuando asignamos x unidades de stock a un lote, la cantidad disponible se reduce en x.

       Ej:
        - Tenemos un lote de 20 SMALL-TABLE, y asignamos una línea de pedido para 2 SMALL-TABLE
        - El lote quedará con 18 SMALL-TABLE restantes.

        No podemos asignar a un lote si la cantidad disponible es menor que la cantidad de la línea de pedido.
        - Tenemos un lote de 1 CEBOLLA AZUL, y una línea de pedido de 2 CEBOLLA AZUL.
        - No deberíamos poder asignar la línea al lote.

    """



    def __init__(self, ref: Reference, sku: Sku, qty: Quantity, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate_one(self) -> OrderLine:
        return self._allocations.pop()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
