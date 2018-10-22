#!/usr/bin/env python3

__author__ = "Night Phawks"

import csv

###########################
##  Utilities Functions  ##
###########################

def _intsqrt(v):
    """Compute int squareroot floor"""
    c = 0

    while c**2 <= v:
        c += 1
    
    return c - 1

#Deprecated
def _int_to_bytes(integer, endian = 'little'):
    """Convert int to bytes object without specifing size"""
    size = 1
    while 1<<(8*size) <= integer:
        size += 1

    return integer.to_bytes(size, endian)

#Deprecated
def _2d_range(*arg):

    for x in range(*arg):
        for y in range(*arg):
            yield x, y

def _triangle_range(stop):

    for x in range(stop):
        for y in range(x, stop):
            yield x, y

def _s2bl(size):
    """Size to Bytes lenght"""
    return size**2 // 8 + 1

def _is_iterable(obj):
    return hasattr(obj, "__iter__")

##########################
## Classes Definitions  ##
##########################

class Matrix:
    """Binary square matrix, used to represent a graph

    parameters:
    -size : int : size of the matrix
    -binary : bytearray : bytearray objet representing the binary
        matrix, is maatrix is None, auto-allocate bytearray object
        with the size parameter (default : None)
    -forcesymetry : bool : force the symetry of the matrix (default :
        False)
    -selflinking : bool : allow point to be linked with themselves
        (default : True)

    See also alt-constructor:
    -from_iterable
    -from_binfile
    -from_csv"""

    def __getitem__(self, i):
        #1D index
        if isinstance(i, int):
            return self._read_bit(i)

        #2D index
        elif len(i) == 2:
            #Column
            i, j = i
            if i is Ellipsis:
                return self.read_col(j)

            #Line
            elif j is Ellipsis:
                return self.read_line(i)

            #Single Value
            else :
                return self.read

        #Error
        else:
            raise TypeError("list indices must be integers or " +
            "iterable of lenght 2")

    def __init__(self, size, binary = None, **kwarg):
        self.size = size
        self.binary = binary if binary else bytearray(_s2bl(size))
        self.forcesymetry = kwarg.get("forcesymetry", False)
        self._update()

    def _update(self):

        if self.forcesymetry and not self.is_symetric:
            self.make_symetry()

    @classmethod
    def from_iterable(cls, iterable, **kwarg):
        """Alternative Constructor : create a matrix from an iterable
        of iterable, ValueError is raised if one of the sub-iterable
        have not the same size than his parent"""
        size = len(iterable)
        self = cls(size, **kwarg)
        errmsg = "Sub-iterable have a different size from it's parent"

        for x, sub in enumerate(iterable):

            if len(sub) != size:
                raise ValueError(errmsg)

            for y, v in enumerate(sub):
                self.write(x, y, v)

        return self

    @classmethod
    def from_binfile(cls, file, **kwarg):
        """Alternative Constructor : create a matrix from a binary
        file, the file must be opened in binary mode and readable"""
        binary = file.read()
        size = _intsqrt(len(binary)*8)
        binary = bytearray(binary[:_s2bl(size)])
        return cls(size, binary, **kwarg)

    @classmethod
    def from_csv(cls, file, **kwarg):
        """Alternative Constructor : create a matrix from a CSV file,
        the file must be readable"""
        r = csv.reader(file)
        iterable = [[int(y) for y in line] for line in r ]
        return cls.from_iterable(iterable)

    def is_symetric(self):
        """Check if the matrix is symetric or not"""
        for x, y in _triangle_range(self.size):

            if self.read(x, y) != self.read(y, x):
                return False

        return True

    def make_symetry(self, axis = 0):
        """Make the matrix symetric * * * """
        for x, y in _triangle_range(self.size):

            if axis:
                self.write(x, y, self.read(y, x))
            else:
                self.write(y, x, self.read(x, y))

    def set_diagonal(self, value = 0):
        """Set all value in the diagonal of the matrix (default 0)"""
        for d in range(self.size):
            self.write(d, d, value)


    def read(self, x, y):
        """Read the value at coord x, y. Equivalent of Matrix[x, y]"""
        i = self.size * x + y
        return self._read_bit(i)

    def write(self, x, y, value):
        """Set the value at coord x, y"""
        i = self.size * x + y
        self._write_bit(i, value)

    def read_line(self, x):
        """Return a list containing all the value of the x line.
        Equivalent of Matrix[..., x]"""
        linerange = self._line_range(x)
        line = []

        for i in linerange:
            line.append(self._read_bit(i))

        return line

    def write_line(self, x, args):
        """Write the x line with args. If args is an iterable,
        write the iterable in the line (leave the rest of the line
        if the iterable is smaller than the line). Else, write args on
        all value of the line"""
        linerange = self._line_range(x)

        if _is_iterable(args):
            for i, v in zip(linerange, args):
                self._write_bit(i, v)

        else :
            for i in linerange:
                self._write_bit(i, args)

    def read_col(self, y):
        """Return a list containing all the value of the y column.
        Equivalent of Matrix[x, ...]"""
        colrange = self._col_range(y)
        col = []

        for i in colrange:
            col.append(self._read_bit(i))

        return col

    def write_col(self, y, args):
        """Write the y column with args. If args is an iterable,
        write the iterable in the column (leave the rest of the column
        if the iterable is smaller than the column). Else, write args
        on all value of the column"""
        linerange = self._line_range(x)

        if _is_iterable(args):
            for i, v in zip(linerange, args):
                self._write_bit(i, v)

        else :
            for i in linerange:
                self._write_bit(i, args)

    def _read_bit(self, i):
        byte, bit = divmod(i, 8)
        b = self.binary[byte] >> bit
        return b % 2

    def _write_bit(self, i, v):
        byte, bit = divmod(i, 8)
        b = self.binary[byte]

        if v:
            b |= 1 << bit
        else:
            b &= b ^ (1 << bit)

        self.binary[byte] = b

    def _line_range(self, x):
        start = x * self.size
        stop = start + self.size
        return range(start, stop)

    def _col_range(self, y):
        start = y
        stop = self.size**2 + y
        step = self.size
        return range(start, stop, step)

    def __str__(self):
        s = ""

        for x in range(self.size):
            s += "|"

            for y in range(self.size):
                s += str(self.read(x, y))

            s += "|\n"

        return s

class Graph(Matrix):
    """docstring for Graph"""

    _selflinking = True

    @property
    def selflinking(self):
        """Allow point to be linked on themselves"""
        return self._selflinking

    @selflinking.setter
    def selflinking(self, v):
        self._selflinking = bool(v)
        self._update()

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self._selflinking = kwarg.get("selflinking", self.selflinking)
        self.names = kwarg.get("names")

    def _update(self):
        super()._update()

        if not self.selflinking:
            self.set_diagonal()

    def get_links(self, point):
        l = []

        for i, x in enumerate(self.read_line(point)):

            if x:
                l.append(i)

        return l

    def to_list(self):
        """Actually it's a tuple of list but nevermind ;3"""
        t = ([],) * self.size
        for x in range(self.size):
            t[x].extend(self.get_links(x))

        return t1

    def is_linked(point, target = None):
        return NotImplemented

    def link(origin, target, symetric = True):
        return NotImplemented

    def unlink(origin, target, symetric = True):
        return NotImplemented