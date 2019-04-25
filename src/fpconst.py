PosInf = 1e300000
NegInf = -PosInf
NaN = PosInf/PosInf

def isPosInf(value):
    return PosInf == value

def isNegInf(value):
    return NegInf == value

def isInf(value):
    return PosInf == value or NegInf == value

def isFinite(value):
    return PosInf > value > NegInf

def isNaN(value):
    return isinstance(value, float) and value != value