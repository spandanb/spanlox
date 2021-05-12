"""
Visitor abstract class
"""


from utils import camel_to_snake


class HandlerNotFoundException(Exception):
    """
    A specific handler (method) is not found;
    defined by me
    """
    pass


class Visitor:
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

    def visit(self, expr: 'Expr'):
        """
        this will determine which specific handler to invoke; dispatch

        NOTE: The tutorial defines separate methods for each
        expr type. But that's partly because of java, where reflection
        is awkward at best. In python, defining each method seems
        very manual, with no real gain in type safety, unlike java.
        More broadly, I'll use python dynamism, unless some substantial
        gain in readability or expressability is needed
        """
        suffix = camel_to_snake(expr.__class__.__name__)
        # determine the name of the handler method from class of expr
        # NB: this requires the class and handler have the
        # same name in PascalCase and snake_case, respectively
        handler = f'visit_{suffix}'
        if hasattr(self, handler):
            return getattr(self, handler)(expr)
        else:
            print(f"Visitor does not have {handler}")
            raise HandlerNotFoundException()
