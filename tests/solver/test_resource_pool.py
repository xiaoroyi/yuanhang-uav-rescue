import pytest
from ortools.sat.python import cp_model as cp

from solver.resource_pool import InterchangeablePool


def test_pool_preserves_initial_availability_and_assigns_real_entities():
    model = cp.CpModel()
    pool = InterchangeablePool(
        model,
        [{"id": "R01", "available_after_s": 0}, {"id": "R02", "available_after_s": 5}],
        "id",
        "test",
        1000,
        10,
    )
    windows = [(0, 4), (4, 8), (5, 9)]
    for i, (start, end) in enumerate(windows):
        present = model.new_bool_var(f"p{i}")
        model.add(present == 1)
        pool.add(start * 10, end * 10, present, str(i))
    pool.constrain()
    solver = cp.CpSolver()
    assert solver.solve(model) in (cp.FEASIBLE, cp.OPTIMAL)
    assert [pool.assign(a, b) for a, b in windows] == ["R01", "R01", "R02"]


def test_unavailable_prefix_is_not_free_capacity():
    model = cp.CpModel()
    pool = InterchangeablePool(
        model,
        [{"id": "R01", "available_after_s": 0}, {"id": "R02", "available_after_s": 5}],
        "id",
        "test",
        1000,
        10,
    )
    for i, (start, end) in enumerate([(0, 6), (4, 8)]):
        present = model.new_bool_var(f"p{i}")
        model.add(present == 1)
        pool.add(start * 10, end * 10, present, str(i))
    pool.constrain()
    assert cp.CpSolver().solve(model) == cp.INFEASIBLE


def test_coloring_uses_half_open_intervals_and_refuses_unordered_input():
    model = cp.CpModel()
    pool = InterchangeablePool(
        model, [{"id": "R01", "available_after_s": 2}], "id", "test", 100, 10
    )
    assert pool.assign(2, 3) == "R01"
    assert pool.assign(3, 4) == "R01"
    with pytest.raises(ValueError, match="nondecreasing"):
        pool.assign(1, 2)
