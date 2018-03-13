# -*- coding: utf-8 -*-
"""
    Handling with model hm

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys, os
from ctypes import *
import numpy as np
from pymordor.modelehydro import detruireforcage

LIBMORDOR = os.environ.get('LIBMORDOR')

if sys.platform.startswith('linux'):
    try:
        MY_LIBRARY0 = CDLL(LIBMORDOR+'/libRunMordorTS.so')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libRunMordorTS.so. Check the environmental variable LIBMORDOR.')
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'/libWrapperModeleHydro.so')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libWrapperModeleHydro.so. Check the environmental variable LIBMORDOR.')
elif sys.platform.startswith('win'):
    try:
        MY_LIBRARY0 = CDLL(LIBMORDOR+'\libRunMordorTS.dll')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libRunMordorTS.dll. Check the environmental variable LIBMORDOR.')
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'\libWrapperModeleHydro.dll')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libWrapperModeleHydro.dll. Check the environmental variable LIBMORDOR.')
else:
    raise Exception(u'unsupported OS')

def delete(hf):
    """
    Free the memory associated with the instance number hf
    :param hf: id number for the inputs of the hydrological model
    :return: null value if success
    """
    value = detruireforcage(hf)
    if value != 0:
        return None
    return value
