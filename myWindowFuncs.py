import math

windows = [
    'invendelirium1', 
    'invendelirium1dip',
]

def getWindow(num_points, window):
    if window[0] in windows:
        import myWindowFuncs
        win = getattr(myWindowFuncs, window[0])(num_points, *window[1:])
        return win
    else:
        raise KeyError(str(window) + str(window[0] == 'invendelirium1'))


def _computeWindow(num_points, f):
    import numpy as np
    data = np.zeros(num_points)
    for i in range(num_points):
        data[i] = f(i/(num_points-1))
    return data

def invendelirium1_f(x, twidth, deg):
    if abs(x - 0.0) < 1e-11 or abs(x - 1.0) < 1e-11:
        return 0.0
    return math.exp(
        -(
            twidth * twidth  /  (x * (1-x))
        ) ** deg
    )

def invendelirium1(numpoints, twidth = 0.5, deg = 1.0, sym = True):
    return _computeWindow(numpoints, lambda x : invendelirium1_f(x, twidth, deg))

def invendelirium1dip_f(x, twidth, deg, dip):
    if abs(x - 0.0) < 1e-11 or abs(x - 1.0) < 1e-11:
        return 0.0
    return math.exp(
        -(
            twidth * twidth  /  (x * (1-x))
        ) ** deg
    ) * math.cosh((x-0.5) * dip)

def invendelirium1dip(numpoints, twidth = 0.5, deg = 1.0, dip = 4.0, sym = True):
    return _computeWindow(numpoints, lambda x : invendelirium1dip_f(x, twidth, deg, dip))


# register windows into scipy
import scipy.signal.windows.windows as ww
for w in windows:
    ww._win_equiv[w] = locals()[w]
    ww._needs_param.update(w)
del(ww)