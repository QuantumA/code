from datetime import date
from src.allocation.domain.model import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    """
        Probamos que al crear un batch con una cantidad, al realizar un pedido de n unidades
        estas se restan del batch.

    """


    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    """Helper function que devuelve un batch y un OrderLine de un determinado tamaño"""
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )


def test_can_allocate_if_available_greater_than_required():
    """ Probamos que la función can_allocate permita realizar pedidos
        de menor cantidad que el lote.
    """
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    """ Probamos que la función can_allocate impida realizar pedidos
        de mayor cantidad que el lote.
    """
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    """ Probamos que la función can_allocate permita realizar pedidos
        de igual cantidad que el lote.
    """
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    """ Probamos que la función can_allocate impide realizar pedidos
        a un lote que tiene distinto sku.
    """

    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_allocation_is_idempotent():
    """Probar que si metemos el mismo orderLine no se resta el stock.
    """
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2) 
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
