# -*- coding: utf-8 -*-
"""
    Wrapper for the library 'libMordorGlobal' of MORDOR-TS

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys, os
from ctypes import *
import numpy as np

NPMT = 150
TMAX = 100000
NSTOCK = 10
LIBMORDOR = os.environ.get('LIBMORDOR')

if sys.platform.startswith('linux'):
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'/libMordorGlobal.so')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libMordorGlobal.so. Check the environmental variable LIBMORDOR.')
elif sys.platform.startswith('win'):
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'\libMordorGlobal.dll')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libMordorGlobal.dll. Check the environmental variable LIBMORDOR.')
else:
    raise Exception(u'unsupported OS')

def prepparam(pmt, etagement, nstock, don, npas, cond):
    """ Data preparation of global Mordor """
    # ctype format
    pmt_c = (c_double*49)(*pmt)
    sizetab = 3*nstock
    etagement_c = (c_double*sizetab)(*etagement.reshape(sizetab, 1))
    sizetab = 5*npas
    don_c = (c_double*sizetab)(*don.reshape(sizetab, 1))
    cond_c = (c_double*11)(*cond)
    flag_c = c_int()
    pmt2_c = (c_double*NPMT)(0.0)
    sizetab = 10*TMAX
    don2_c = (c_double*sizetab)(0.0)
    cond2_c = (c_double*NPMT)(0.0)

    # calling the librairie
    MY_LIBRARY.mordor_prep_param(byref(pmt_c), byref(etagement_c), \
         byref(don_c), byref(cond_c), byref(flag_c), byref(pmt2_c), \
         byref(don2_c), byref(cond2_c))

    # return values in standard types
    flag = flag_c.value
    pmt2 = np.array(pmt2_c)
    don2 = np.array(don2_c)
    don2_ = don2.reshape(10, TMAX).transpose()
    cond2 = np.array(cond2_c)

    return flag, pmt2, don2_, cond2

def initialisation(pmt, tnn, txn, cond):
    """ Data initialization of global Mordor """
    # ctype format
    pmt_c = (c_double*NPMT)(*pmt)
    tnn_c = (c_double*TMAX)(*tnn)
    txn_c = (c_double*TMAX)(*txn)
    cond_c = (c_double*NPMT)(*cond)
    flag_c = (c_int*10)()
    tpn_c = (c_double*TMAX)(0.0)
    prep_kc_c = (c_double*366)(0.0)
    sizetab = NSTOCK*8
    etat_ini_c = (c_double*sizetab)(0.0)

    # calling the library
    MY_LIBRARY.mordor_initialisation(byref(pmt_c), byref(tnn_c), byref(txn_c), \
            byref(cond_c), byref(flag_c), byref(tpn_c), byref(prep_kc_c), \
            byref(etat_ini_c))

    # return values in standard types
    flag = np.array(flag_c)
    tpn = np.array(tpn_c)
    prep_kc = np.array(prep_kc_c)
    etat_i = np.array(etat_ini_c)
    etat_ini = etat_i.reshape(NSTOCK, 8).transpose()

    return flag, tpn, prep_kc, etat_ini

