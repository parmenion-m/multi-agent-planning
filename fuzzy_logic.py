
from numbers import Number
from scipy.stats import trapz


def is_fuzzy_value(a):
    return type(a) == tuple and len(a) == 4 and all([isinstance(v, Number) for v in a]) and a[0] <= a[1] <= a[2] <= a[3]


def is_interval_value(a):
    return type(a) == tuple and len(a) == 2 and all([isinstance(v, Number) for v in a]) and a[0] <= a[1]


class Fuzzy:

    value = None    # quadruple of non-strictly increasing numbers

    def __init__(self, interval=None, slack=0.1, value=None):
        """
        create a fuzzy number object
        calc value from interval and slack or get value directly from value
        if value is given, interval and slack are ignored
        """

        if is_fuzzy_value(value):
            self.value = value
        elif is_interval_value(interval) and isinstance(slack, Number):
            self.value = interval[0] - abs(interval[0]) * slack, \
                         interval[0], \
                         interval[1], \
                         interval[1] + abs(interval[1]) * slack
        else:
            raise ValueError('Not valid parameters for building Fuzzy object - interval=%s, slack=%s, value=%s'
                             % (interval, slack, value))

    def defuzzify(self):
        return (self.value[0] + 2 * self.value[1] + 2 * self.value[2] + self.value[3]) / 6

    def get_random_value(self):
        """
        create a trapezoidal distribution based on the fuzzy number
        and get a random value from it
        """

        # trapezoidal distribution parameters
        loc = self.value[0]
        scale = self.value[3] - self.value[0]
        c = (self.value[1] - self.value[0]) / scale
        d = (self.value[2] - self.value[0]) / scale

        # random value from trapezoidal distribution
        r = trapz.rvs(c, d, loc=loc, scale=scale)
        return r

    # ----- Get Fuzzy Number / Point -----

    def __repr__(self):
        return 'Fuzzy object: ' + str(self.value)

    def __str__(self):
        return 'Fuzzy value: ' + str(self.value)

    def __getitem__(self, key):
        if key in [0, 1, 2, 3]:
            return self.value[key]
        else:
            raise IndexError('Indices for Fuzzy objects should be between 0-3, %s given' % key)

    # ----- Numeric Operations -----

    def __add__(self, other):
        if other is None:
            return None
        elif isinstance(other, Fuzzy):
            result = tuple(sum(x) for x in zip(self.value, other.value))
            return Fuzzy(value=result)
        elif isinstance(other, Number):
            result = tuple(i + other for i in self.value)
            return Fuzzy(value=result)
        else:
            raise TypeError("unsupported operand type(s) for +: 'Fuzzy' and '%s'" % type(other))

    def __sub__(self, other):
        if other is None:
            return None
        elif isinstance(other, Fuzzy):
            result = (self.value[0] - other.value[3],
                      self.value[1] - other.value[2],
                      self.value[2] - other.value[1],
                      self.value[3] - other.value[0])
            return Fuzzy(value=result)
        elif isinstance(other, Number):
            result = tuple(v - other for v in self.value)
            return Fuzzy(value=result)
        else:
            raise TypeError("unsupported operand type(s) for -: 'Fuzzy' and '%s'" % type(other))

    def __mul__(self, other):
        if isinstance(other, Number):
            result = tuple(v * other for v in self.value)
            return Fuzzy(value=result)
        else:
            raise TypeError("unsupported operand type(s) for *: 'Fuzzy' and '%s'" % type(other))

    def __truediv__(self, other):
        if isinstance(other, Number):
            result = tuple(v / other for v in self.value)
            return Fuzzy(value=result)
        else:
            raise TypeError("unsupported operand type(s) for /: 'Fuzzy' and '%s'" % type(other))

    def roll_left(self, other):
        if isinstance(other, Number):
            result = tuple(max(v - other, 0.0) for v in self.value)
            return Fuzzy(value=result)
        else:
            raise TypeError("unsupported operand type(s) for -: 'Fuzzy' and '%s'" % type(other))

    # ----- Comparison Operations -----
    """
    compare defuzzified vales 
    """

    def __eq__(self, other):
        if isinstance(other, Fuzzy):
            return self.defuzzify() == other.defuzzify()
        else:
            raise TypeError("'==' not supported between instances of 'Fuzzy' and '%s'" % type(other))

    def __gt__(self, other):
        if isinstance(other, Fuzzy):
            return self.defuzzify() > other.defuzzify()
        else:
            raise TypeError("'>' not supported between instances of 'Fuzzy' and '%s'" % type(other))

    def __ge__(self, other):
        if isinstance(other, Fuzzy):
            return self.defuzzify() >= other.defuzzify()
        else:
            raise TypeError("'>=' not supported between instances of 'Fuzzy' and '%s'" % type(other))

    def __lt__(self, other):
        if isinstance(other, Fuzzy):
            return self.defuzzify() < other.defuzzify()
        else:
            raise TypeError("'<' not supported between instances of 'Fuzzy' and '%s'" % type(other))

    def __le__(self, other):
        if isinstance(other, Fuzzy):
            return self.defuzzify() <= other.defuzzify()
        else:
            raise TypeError("'<=' not supported between instances of 'Fuzzy' and '%s'" % type(other))
