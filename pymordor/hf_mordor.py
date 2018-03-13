# -*- coding: utf-8 -*-
"""
    Handling with model hm

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys, os
from ctypes import *
import numpy as np
from pymordor.modelehydro import creerbaseforcage, detruireforcage, remplirsiteforcage
from pymordor.mordorglobal import prepparam, initialisation
from pymordor.utils import calcidjour

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

def create(temps, maillage, meteo, etat0, param, tabinj=None):
    """
    Instantiation of new inputs
    :param temps: dictionary with info on the computational times
    :param maillage: dictionary of the hydrological mesh
    :param meteo: array for rain and temperature values
    :param etat0: array of the initial state
    :param param: array of hydrological parameters
    """
    carameteo = np.zeros((maillage['nmailles'],4))
    carameteo[:,0:3] = maillage['descripteurs'][:,0:3]
    hf = creerbaseforcage('forcage', maillage['nmailles'], carameteo, maillage['nmailles'], carameteo, maillage['nqinj'], temps['ndates'], temps['date1'], temps['dt'])
    if hf < 0:
        return None
    nech = etat0[0]
    id_jour = calcidjour(temps['date1'], temps['date2'])
    matini = np.zeros((8, maillage['nbandes']*10))
    i = 0
    p = meteo['rain'][0:temps['ndates'],i].reshape(temps['ndates'],1)
    tmin = meteo['tmin'][0:temps['ndates'],i].reshape(temps['ndates'],1)
    tmax = meteo['tmax'][0:temps['ndates'],i].reshape(temps['ndates'],1)
    tmoy = (tmin+tmax) * 0.5
    idj = np.asarray(id_jour['id_days'])
    don = np.hstack((idj, np.zeros((temps['ndates'],1)), p, tmoy,np.zeros((temps['ndates'],1))))
    etage = np.zeros((3, maillage['nbandes']))
    etage[0,:] = 1./maillage['nbandes']
    etage[1,:] = maillage['altitudes'][0]

    # Preparation des parametres Mordor global
    param[3] = maillage['descripteurs'][i, 3]
    param[5] = maillage['descripteurs'][i, 2]
    param[6] = maillage['descripteurs'][i, 4]
    prep = prepparam(param, etage.transpose(), maillage['nbandes'],don,temps['ndates'],np.hstack((temps['ndates']+nech,etat0[0:9])))

    # Initialisation Mordor global
    matpmt = prep['pmt2']
    iniglob = initialisation(prep['pmt2'], tmin, tmax, prep['cond2'])

    matkc = iniglob['prep_kc'].reshape(366,1)
    matini = iniglob['etat_ini']
    iniglob['tpn'] = iniglob['tpn'][0:temps['ndates'],]

    # remplissage de la base de forcage hf
    val = remplirsiteforcage(hf, 1, i+1, temps['ndates'], p)
    val = remplirsiteforcage(hf, 3, i+1, temps['ndates'], tmin)
    val = remplirsiteforcage(hf, 4, i+1, temps['ndates'], tmax)
    val = remplirsiteforcage(hf, 6, i+1, temps['ndates'], iniglob['tpn'])

    if maillage['nmailles'] > 1:
        for i in range(1, maillage['nmailles']):
            p = meteo['rain'][0:temps['ndates'],i].reshape(temps['ndates'],1)
            tmin = meteo['tmin'][0:temps['ndates'],i].reshape(temps['ndates'],1)
            tmax = meteo['tmax'][0:temps['ndates'],i].reshape(temps['ndates'],1)
            tmoy = (tmin+tmax) * 0.5
            don = np.hstack((idj, np.zeros((temps['ndates'],1)), p, tmoy,np.zeros((temps['ndates'],1))))
            etage[1,:] = maillage['altitudes'][i]
            param[3] = maillage['descripteurs'][i, 3]
            param[5] = maillage['descripteurs'][i, 2]
            param[6] = maillage['descripteurs'][i, 4]
            prep = prepparam(param, etage.transpose(), maillage['nbandes'],don,temps['ndates'],np.hstack((temps['ndates']+nech,etat0[0:9])))
            matpmt = np.vstack((matpmt, prep['pmt2']))
            iniglob = initialisation(prep['pmt2'], tmin, tmax, prep['cond2'])
            iniglob['tpn'] = iniglob['tpn'][0:temps['ndates'],]
            matkc = np.hstack((matkc, iniglob['prep_kc'].reshape(366,1)))
            matini = np.vstack((matini, iniglob['etat_ini']))
            val = remplirsiteforcage(hf, 1, i+1, temps['ndates'], p)
            val = remplirsiteforcage(hf, 3, i+1, temps['ndates'], tmin)
            val = remplirsiteforcage(hf, 4, i+1, temps['ndates'], tmax)
            val = remplirsiteforcage(hf, 6, i+1, temps['ndates'], iniglob['tpn'])

    if maillage['nqinj'] > 0:
        for i in range(0, maillage['nqinj']):
            val = remplirsiteforcage(hf, 5, i+1, temps['ndates'], tabinj)
            
    forc = {'hf':hf, 'prep':prep, 'matpmt':matpmt, 'matkc':matkc, 'matini':matini}
    return forc
    
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
