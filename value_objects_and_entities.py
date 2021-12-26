
from dataclasses import dataclass
import pytest

@dataclass
class Name:
    first: str
    surname: str


class Person:
    def __init__(self, name: Name) -> None:
        self.name = name



def test_names_are_differents():
    abu = Name("abu", "abdal")
    boo = Name("boo", "ming")

    assert abu is not boo

def test_both_are_the_same_person():
    abu = Person(Name("abu", "abdal"))

    boo = abu

    boo.name = Name("boo", "ming")

    assert boo is abu and abu is boo


