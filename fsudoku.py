#!/usr/bin/python3
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   (c) 2008 Joseph Coffland

import copy
import sys
import fileinput


class Set:
    def __init__(self, cells, indicies):
        self.cells = cells
        self.indicies = indicies


    def unique(self):
        values = []
        for value in self.cells:
            if value in values: return False
            if value != None: values += [value]
        return True



class Grid:
    def __init__(self, cells, size):
        self.size = size
        self.cells = list(cells)


    def get(self, row, col):
        return self.cells[row + col * self.size]


    def set(self, row, col, value):
        self.cells[row + col * self.size] = value


    def getRow(self, row):
        return Set(list(map(lambda col: self.get(row, col), range(self.size))),
                   list(map(lambda col: row + col * self.size, range(self.size))))


    def getCol(self, col):
        return Set(list(map(lambda row: self.get(row, col), range(self.size))),
                   list(map(lambda row: row + col * self.size, range(self.size))))


    def getBlock(self, blk):
        rowOffset = (blk // 3) * 3
        colOffset = (blk % 3) * 3
        values = []
        indicies = []
        for row in range(3):
            for col in range(3):
                r = row + rowOffset
                c = col + colOffset
                values += [self.get(r, c)]
                indicies += [r + c * self.size]

        return Set(values, indicies)


    def iterateSets(self):
        sets = []
        for i in range(self.size):
            sets += [self.getRow(i), self.getCol(i), self.getBlock(i)]
        return sets


    def showRow(self, row):
        for col in range(self.size):
            if col and col % 3 == 0: sys.stdout.write(' ')
            value = self.get(row, col)
            if value == None: sys.stdout.write('?')
            else: sys.stdout.write(str(value))
            sys.stdout.write(' ')


    def show(self):
        for row in range(self.size):
            self.showRow(row)
            sys.stdout.write('\n')

            if row and row != self.size - 1 and row % 3 == 2:
                sys.stdout.write('\n')



class Puzzle:
    def __init__(self):
        size = 9
        self.grid = Grid(map(lambda x: None, range(size * size)), size)


    def isValid(self):
        for set in self.grid.iterateSets():
            if not set.unique():
                return False

        return True


    def assertValid(self):
        if not self.isValid():
            print("Puzzle invalid")
            sys.exit(1)


    def isSolved(self):
        if not self.isValid(): return False
        for cell in self.grid.cells:
            if cell == None: return False

        return True


    def show(self):
        self.grid.show()


    def read(self):
        row = 0
        for line in fileinput.input():
            nums = line.split()
            if len(nums) == 0: continue
            if len(nums) != self.grid.size:
                print("Invalid input at line ", row)

            for col in range(self.grid.size):
                if nums[col] == '?': self.grid.set(row, col, None)
                else: self.grid.set(row, col, int(nums[col]))

            row = row + 1
            if row == self.grid.size: break

    def read_file(self, file_name):
        with open(file_name) as f:
            row = 0
            for line in f:
                nums = line.split()
                if len(nums) == 0: continue
                if len(nums) != self.grid.size:
                    print("Invalid input at line ", row)

                for col in range(self.grid.size):
                    if nums[col] == '?': self.grid.set(row, col, None)
                    else: self.grid.set(row, col, int(nums[col]))

                row = row + 1
                if row == self.grid.size: break



class Possible:
    def __init__(self, value = None):
        self.set(value)


    def set(self, value):
        if value == None: self.possible = list(range(1, 10))
        else: self.possible = [value]


    def count(self):
        return len(self.possible)


    def has(self, value):
        return value in self.possible


    def remove(self, value):
        if value in self.possible:
            self.possible = list(filter(lambda x: x != value, self.possible))
            return True
        return False

combination_counter = 0

class PossibleGrid:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.grid = Grid(map(lambda cell: Possible(cell), puzzle.grid.cells),
                         puzzle.grid.size)


    def removeImpossible(self, set):
        result = False
        values = []
        unset = []
        for cell in set.cells:
            if cell.count() == 1: values += [cell.possible[0]]
            else: unset += [cell]

        for cell in unset:
            for value in values:
                if cell.remove(value): result = True

        return result


    def findExclusives(self, set):
        exclusives = []
        values = list(map(lambda x: [], range(self.grid.size)))

        for cell in set.cells:
            if cell.count() != 1:
                for value in cell.possible:
                    values[value - 1] += [cell]

        for i in range(self.grid.size):
            if len(values[i]) == 1:
                exclusives += (values[i][0], i + 1)

        if exclusives: return exclusives
        else: return None


    def solve(self):
        global combination_counter
        combination_counter = combination_counter + 1
        while True:
            while len(list(filter(lambda set: self.removeImpossible(set),
                             self.grid.iterateSets()))):
                continue

            exclusives = list(map(self.findExclusives, self.grid.iterateSets()))
            exclusives = list(filter(lambda x: x, exclusives))
            if not exclusives: break
            for pair in exclusives:
                pair[0].set(pair[1])

        self.fill()


    def fill(self):
        for i in range(len(self.grid.cells)):
            if self.grid.cells[i].count() == 1:
                self.puzzle.grid.cells[i] = self.grid.cells[i].possible[0]


    def iterateCombinations(self, set, values = []):
        results = []

        if len(values) == len(set.cells):
            return [copy.deepcopy(values)]

        cell = set.cells[len(values)]
        for value in cell.possible:
            if value not in values:
                results += self.iterateCombinations(set, values + [value])

        return results


    def tryCombinations(self, puzzle, sets, index = 0):
        if index == len(sets):
            self.puzzle.grid = puzzle.grid
            return

        set = sets[index]
        cpuzzle = copy.deepcopy(puzzle)

        for comb in self.iterateCombinations(set):
            valid = True

            for i in range(len(comb)):
                cindex = set.indicies[i]
                value = puzzle.grid.cells[cindex]

                if value == None:
                    cpuzzle.grid.cells[cindex] = comb[i]
                elif value != comb[i]:
                    valid = False
                    break

            if valid and cpuzzle.isValid():
                ppuzzle = copy.deepcopy(cpuzzle)
                possible = PossibleGrid(ppuzzle)
                possible.solve()

                if ppuzzle.isSolved():
                    self.puzzle.grid = ppuzzle.grid
                    return

                elif ppuzzle.isValid():
                    self.tryCombinations(ppuzzle, sets, index + 1)


    def tryAllCombinations(self):
        sets = self.grid.iterateSets()
        self.tryCombinations(copy.deepcopy(self.puzzle), sets)


def solve(puzzle):
    print("Solving . . .")
    sys.stdout.flush()
    possible = PossibleGrid(puzzle)
    possible.solve()

    if not puzzle.isSolved():
        print ("hard . . .")
        sys.stdout.flush()
        possible.tryAllCombinations()

    print("done")


puzzle = Puzzle()

## puzzle.read()
if len(sys.argv) > 1:
    puzzle.read_file(sys.argv[1])
else:
    sys.exit(1)

puzzle.show()
puzzle.assertValid()
print('-------------------')
solve(puzzle)

puzzle.show()

print('Combinations:', combination_counter)

puzzle.assertValid()
