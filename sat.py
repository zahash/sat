from pystream import Stream
from typing import Iterable, NamedTuple


class Var:
    negation_symbol = "~"

    def __init__(self, name: str, negated: bool) -> None:
        self.name = name.lstrip("~")
        self.negated = negated

    def negate(self) -> "Var":
        nvar = Var(self.name, self.negated)
        nvar.negated = not self.negated
        return nvar

    def normal_form(self) -> "Var":
        return Var(self.name, True)

    def inverted_form(self) -> "Var":
        return Var(self.name, False)

    @staticmethod
    def new(name):
        return Var(name, True), Var(name, False)

    def __eq__(self, __o: object) -> bool:
        return __o and type(self) == type(__o) and self.name == __o.name and self.negated == __o.negated

    def __hash__(self) -> int:
        return hash((self.name, self.negated))

    def __repr__(self) -> str:
        return self.name if not self.negated else self.__class__.negation_symbol + self.name


Clause = list[Var]
Expression = list[Clause]


def condition(variable: Var, expr: Expression) -> Expression:
    return expr + [[variable]]


UnitPropResult = NamedTuple(
    'UnitPropResult',
    [
        ('resolved_vars', list[Var]),
        ('expr', Expression)
    ]
)


def unit_propagate(expr: Expression) -> UnitPropResult | None:
    resolved_vars: list[Var] = []

    while True:
        unit_vars = Stream(expr) \
            .filter(lambda clause: len(clause) == 1) \
            .flatten() \
            .collect(set)

        for uvar in unit_vars:
            if uvar.negate() in unit_vars:
                return None

        unit_var = Stream(unit_vars).first()

        if not unit_var:
            return UnitPropResult(resolved_vars, expr)

        resolved_vars.append(unit_var)

        expr = Stream(expr) \
            .filter(lambda clause: unit_var not in clause) \
            .map(lambda clause: Stream(clause).filter(lambda var: var != unit_var.negate()).collect(list)) \
            .collect(list)


def condition_and_unit_propagate(variable: Var, expr: Expression) -> UnitPropResult | None:
    expr = condition(variable, expr)
    return unit_propagate(expr)


def solve(expr: Expression) -> Iterable[list[Var]] | None:
    normal_variables = Stream(expr) \
        .flatten() \
        .map(lambda v: v.normal_form()) \
        .distinct() \
        .collect(list)

    inverted_variables = Stream(expr) \
        .flatten() \
        .map(lambda v: v.inverted_form()) \
        .distinct() \
        .collect(list)

    return _solve(expr, [], list(zip(normal_variables, inverted_variables)))


def _solve(expr: Expression, conditioned_vars: list[Var], var_choices: list[tuple[Var, Var]]) -> Iterable[list[Var]] | None:
    if not expr:
        return conditioned_vars

    if not var_choices:
        return conditioned_vars

    (v, _v) = var_choices[0]

    result = condition_and_unit_propagate(v, expr)
    _result = condition_and_unit_propagate(_v, expr)

    if result:
        resolved_vars, new_expr = result
        return _solve(new_expr, list(set(conditioned_vars + [v] + resolved_vars)), var_choices[1:])

    if _result:
        resolved_vars, new_expr = result
        return _solve(new_expr, list(set(conditioned_vars + [_v] + resolved_vars)), var_choices[1:])

    return None


def main():
    x1, _x1 = Var.new("1")
    x2, _x2 = Var.new("2")
    x3, _x3 = Var.new("3")
    x4, _x4 = Var.new("4")

    expr = [
        [x1, x2],
        [x1, _x2, _x3, x4],
        [x1, _x3, _x4],
        [_x1, x2, _x3],
        [_x1, x2, _x4],
        [_x1, x3, x4],
        [_x2, x3]
    ]

    res = solve(expr)

    print(expr)
    print(res)


if __name__ == "__main__":
    main()
