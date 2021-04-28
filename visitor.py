"""
Visitor abstract class
"""

from abc import ABC, abstractmethod


class HandlerNotFoundException(Exception):
    """
    A specific handler (method) is not found;
    defined by me
    """
    pass


class Visitor(ABC):
    """
    Conceptually, Visitor is an interface/abstract class,
    where different concrete Visitors, e.g. AstPrinter can handle
    different tasks, e.g. printing tree, evaluating tree.
    This indirection allows us to add new behaviors for the parser
    via a new concrete class; instead of either: 1) modifying
    the parser symbol classes (OOF), or 2) adding a new function
    for any new behavior (e.g. functional)

    See following for visitor design pattern in python:
     https://refactoring.guru/design-patterns/visitor/python/example
    """
    pass

    @abstractmethod
    def visit(self, expr: 'Expr'):
        """
        this will determine which specific handler to invoke

        NOTE: The tutorial defines separate methods for each
        expr type. But that's partly because of java, where reflection
        is awkward at best. In python, defining each method seems
        very manual, with no real gain in type safety, unlike java.
        More broadly, I'll use python dynamism, unless some substantial
        gain in readability or expressability is needed
        """
        pass
