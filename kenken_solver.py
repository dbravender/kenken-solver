# A solver for KenKen puzzles

from collections import defaultdict
from itertools import chain, product

from constraint import AllDifferentConstraint, FunctionConstraint, Problem


def AddsTo(total):
    return lambda *args: sum(args) == total


def MultipliesTo(total):
    return lambda *args: reduce(lambda x, y: x * y, args) == total


def DividesTo(total):
    def fun(*args):
        args = list(args[:])
        args.sort(reverse=True)
        result = args.pop(0)
        for arg in args:
            result /= arg
        return result == total
    return fun


def SubtractsTo(total):
    return lambda *args: (
        reduce(lambda x, y: max(x, y) - min(x, y), args) == total)


def solve_board(board, cages):
    problem = Problem()
    height = len(board)
    width = len(board[0])
    assert width == height, 'Grid must be a square'

    cage_name_to_locations = defaultdict(list)

    for x in range(height):
        row_variables = [(x, ry) for ry in range(width)]
        column_variables = [(cx, x) for cx in range(height)]
        problem.addConstraint(AllDifferentConstraint(), row_variables)
        problem.addConstraint(AllDifferentConstraint(), column_variables)
        for y in range(width):
            if isinstance(board[x][y], basestring):
                # we are dealing with a function
                cage_name_to_locations[board[x][y]].append((x, y))
            else:
                # we are dealing with a pre-assigned number
                problem.addVariable((x, y), [board[x][y]])

    for cage_name, cage_locations in cage_name_to_locations.iteritems():
        cage_function = cages[cage_name]
        all_values = product(range(1, width + 1),
                             repeat=len(cage_locations))
        possible_values = set(chain(*[values for values in all_values
                                      if cage_function(*values)]))
        for location in cage_locations:
            problem.addVariable(location, list(possible_values))
        problem.addConstraint(FunctionConstraint(cage_function),
                              cage_locations)

    solution = problem.getSolution()

    answer = [row[:] for row in board]
    for x in range(height):
        for y in range(width):
            answer[x][y] = solution[(x, y)]

    return answer


board = [['a', 'a', 2],
         ['b', 'c', 'c'],
         ['b', 'd', 'd']]

cages = {
    'a': SubtractsTo(2),
    'b': DividesTo(2),
    'c': DividesTo(3),
    'd': SubtractsTo(1)
}

answer = solve_board(board, cages)

assert answer == [[3, 1, 2],
                  [2, 3, 1],
                  [1, 2, 3]]

board = [['a', 'b', 'b', 'c', 'd', 'd'],
         ['a', 'e', 'e', 'c', 'f', 'd'],
         ['g', 'g', 'h', 'h', 'f', 'd'],
         ['g', 'g', 'i', 'j', 'k', 'k'],
         ['l', 'l', 'i', 'j', 'j', 'm'],
         ['n', 'n', 'n', 'o', 'o', 'm']]

cages = {
    'a': AddsTo(11),
    'b': DividesTo(2),
    'c': MultipliesTo(20),
    'd': MultipliesTo(6),
    'e': SubtractsTo(3),
    'f': DividesTo(3),
    'g': MultipliesTo(240),
    'h': MultipliesTo(6),
    'i': MultipliesTo(6),
    'j': AddsTo(7),
    'k': MultipliesTo(30),
    'l': MultipliesTo(6),
    'm': AddsTo(9),
    'n': AddsTo(8),
    'o': DividesTo(2),
}

answer = solve_board(board, cages)

assert answer == [[5, 6, 3, 4, 1, 2],
                  [6, 1, 4, 5, 2, 3],
                  [4, 5, 2, 3, 6, 1],
                  [3, 4, 1, 2, 5, 6],
                  [2, 3, 6, 1, 4, 5],
                  [1, 2, 5, 6, 3, 4]]
