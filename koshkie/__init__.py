#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 17:27
import math
from abc import ABC

from django.db.models import Func, F


class Sin(Func, ABC):
    function = 'SIN'


class Cos(Func, ABC):
    function = 'COS'


class Asin(Func, ABC):
    function = 'ASIN'


class Sqrt(Func, ABC):
    function = 'SQRT'


# for more info https://en.wikipedia.org/wiki/Haversine_formula

def haversine(lat1, lon1, lat2, lon2):
    """uses haversine formula to calculate distance
    between two locations"""
    dlat = (lat2 - lat1) * math.pi / 180.0
    dlon = (lon2 - lon1) * math.pi / 180.0

    lat1 = lat1 * math.pi / 180.0
    lat2 = lat2 * math.pi / 180.0

    if type(lat1) == F or type(lon1) == F or type(lat2) == F or type(lon2) == F:
        # if it is an expression for sql query use combine functions above
        a = (pow(Sin(dlat / 2), 2) +
             pow(Sin(dlon / 2), 2) *
             Cos(lat1) * Cos(lat2))
        rad = 6371
        c = 2 * Asin(Sqrt(a))
    else:
        # if all args are real numbers not expressions do regular math operations
        a = (pow(math.sin(dlat / 2), 2) +
             pow(math.sin(dlon / 2), 2) *
             math.cos(lat1) * math.cos(lat2))
        rad = 6371
        c = 2 * math.asin(math.sqrt(a))

    return rad * c
