from pystream import Stream
from typing import Iterable, NamedTuple

Var = int
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
            if -uvar in unit_vars:
                return None

        unit_var = Stream(unit_vars).first()

        if not unit_var:
            return UnitPropResult(resolved_vars, expr)

        resolved_vars.append(unit_var)

        expr = Stream(expr) \
            .filter(lambda clause: unit_var not in clause) \
            .map(lambda clause: Stream(clause).filter(lambda var: var != -unit_var).collect(list)) \
            .collect(list)


def condition_and_unit_propagate(variable: Var, expr: Expression) -> UnitPropResult | None:
    expr = condition(variable, expr)
    return unit_propagate(expr)


def solve(expr: Expression) -> list[Var] | None:
    normal_variables = Stream(expr) \
        .flatten() \
        .map(lambda v: abs(v)) \
        .distinct() \
        .collect(list)

    inverted_variables = Stream(expr) \
        .flatten() \
        .map(lambda v: -abs(v)) \
        .distinct() \
        .collect(list)

    return _solve(expr, [], list(zip(normal_variables, inverted_variables)))


def _solve(expr: Expression, conditioned_vars: list[Var], var_choices: list[tuple[Var, Var]]) -> list[Var] | None:
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
        resolved_vars, new_expr = _result
        return _solve(new_expr, list(set(conditioned_vars + [_v] + resolved_vars)), var_choices[1:])

    return None


def main():
    expr = [
        [1, 2],
        [1, -2, -3, 4],
        [1, -3, -4],
        [-1, 2, -3],
        [-1, 2, -4],
        [-1, 3, 4],
        [-2, 3]
    ]

    res = solve(expr)

    print(expr)
    print(res)


if __name__ == "__main__":
    main()
