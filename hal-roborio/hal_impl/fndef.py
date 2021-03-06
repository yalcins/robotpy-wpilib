import ctypes as C
import os
import sys
import time

__all__ = ["_dll", "_RETFUNC", "_VAR", "sleep"]

_dll = C.CDLL(os.path.join(os.path.dirname(sys.modules['hal_impl'].__file__), "libHALAthena.so"), use_errno=True)
sleep = time.sleep

def _RETFUNC(name, restype, *params, out=None, library=_dll,
             errcheck=None, handle_missing=False, c_name=None):
    prototype = C.CFUNCTYPE(restype, *tuple(param[1] for param in params))
    paramflags = []
    for param in params:
        if out is not None and param[0] in out:
            dir = 2
        else:
            dir = 1
        if len(param) == 3:
            paramflags.append((dir, param[0], param[2]))
        else:
            paramflags.append((dir, param[0]))
        
    # Note: keep in sync with hal-sim implementation
    if c_name is None:
        c_name = 'HAL_%s%s' % (name[0].upper(), name[1:])
            
    try:
        func = prototype((name, library), tuple(paramflags))
        if errcheck is not None:
            func.errcheck = errcheck
    except AttributeError:
        if not handle_missing:
            raise
        def func(*args, **kwargs):
            raise NotImplementedError
    return func

# Thunkfunc is specialized in simulation, but the same as _RETFUNC
# outside of simulation
_THUNKFUNC = _RETFUNC

def _VAR(name, type, library=_dll):
    return type.in_dll(library, name)
