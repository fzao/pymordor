# -*- coding: utf-8 -*-
"""
    Handling with model hm

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys, os
from ctypes import *
import numpy as np
from pymordor.modelehydro import getdimmodele, getetatmodele, creermodele, detruiremodele

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

def runintercept(hm, temps, idmaille, idinter):
    """
    Run the model and info on the states
    :param hm: id number of the hydrological model
    :param temps: dictionary with info on the computational times
    :param idmaille: list of cells for the interceptions
    :param idinter: list interception numbers
    :return: a dictionary of interceptions
    """
    # get model sizes
    dim_mod = getdimmodele(hm)
    nmailinter_c = c_int(len(idmaille))
    nintercept_c = c_int(len(idinter))
    idmaille_c = (c_int * len(idmaille))(*idmaille)
    idinter_c = (c_int * len(idinter))(*idinter)
    hm_c = c_int(hm)
    # get time info
    tfin = temps['date2']
    tm = np.zeros((9, 1))
    tm[0] = tfin.timetuple().tm_sec
    tm[1] = tfin.timetuple().tm_min
    tm[2] = tfin.timetuple().tm_hour
    tm[3] = tfin.timetuple().tm_mday
    tm[4] = tfin.timetuple().tm_mon - 1
    tm[5] = tfin.timetuple().tm_year - 1850
    tm[6] = tfin.timetuple().tm_wday + 1
    tm[7] = tfin.timetuple().tm_yday - 1
    tm[8] = tfin.timetuple().tm_isdst
    if temps['dt'] == 86400:
        tm[2] = 23
    elif temps['dt'] == 3600:
        tm[1] = 59
    tm_c = (c_double * 9)(*tm)
    # discharges
    sizetab = dim_mod['nsortietransfert'] * (temps['ndates'] - 1)
    qsim_c = (c_double * sizetab)(0.0)
    # interceptions
    sizetab = len(idmaille) * len(idinter) * (temps['ndates'] - 1)
    #intercept = np.zeros((len(idmaille) * len(idinter) * (temps['ndates'] - 1), 1))
    intercept_c = (c_double * sizetab)(0.0)
    # calling the library
    valeur = MY_LIBRARY.hmRunMordorIntercept(hm_c, byref(tm_c), nmailinter_c, \
        byref(idmaille_c), nintercept_c, byref(idinter_c), \
        byref(qsim_c), byref(intercept_c))
    if valeur != 0:
        return None
    # --> state
    etat = getetatmodele(hm)
    state = {}
    state['etatproduction'] = etat['etatproduction'][0:dim_mod['nmailles']*8*10]
    state['etatproduction'] = np.asarray(state['etatproduction'])
    state['etatproduction'] = state['etatproduction'].reshape(10, dim_mod['nmailles'] * 8).transpose()
    state['etattransfert'] = etat['etattransfert'][0:dim_mod['nmailles']*dim_mod['nsortietransfert']]
    state['etattransfert'] = np.asarray(state['etattransfert'])
    state['etattransfert'] = state['etattransfert'].reshape(dim_mod['nsortietransfert'], dim_mod['nmailles']).transpose() 
    state['bufferproduction'] = etat['bufferproduction'][0:dim_mod['nbuffer']*dim_mod['nmailles']]
    state['bufferproduction'] = np.asarray(state['bufferproduction'])
    state['bufferproduction'] = state['bufferproduction'].reshape(dim_mod['nmailles'], dim_mod['nbuffer']).transpose()
    state['qmoyen'] = etat['qmoyen'][0:dim_mod['nsortietransfert']]
    state['qmoyen'] = np.asarray(state['qmoyen'])
    # --> qsim
    qsim = np.array(qsim_c)
    qsim = qsim.reshape(temps['ndates'] - 1, dim_mod['nsortietransfert'])
    # --> intercept
    inter = np.array(intercept_c)
    inter = inter.reshape(temps['ndates'] - 1, len(idmaille) * len(idinter))
    lnames = ["U","L","Z","N","sn","sns","tft","tst","Preciptot.","Tmin", \
         "Tmax","Tpn","ruiss","neige","pluie","accu","lglace","lfonte","frl", \
         "er","ep","fneige","rsurf","rvers","rbase","echNR","emax","Production"]
    intercept = {}
    for i in range(0, len(idinter)):
        intercept[lnames[i]] = inter[:, i*len(idmaille):(i+1)*len(idmaille)]
    return{'qsim':qsim, 'state':state, 'intercept':intercept}

def create(temps, maillage, forc, inflow=None):
    """
    Instantiation of a new hm model
    :param temps: dictionary with info on the computational times
    :param maillage: dictionary of the hydrological mesh
    :param forc: dictionary of associated inputs
    :return: a new id number for the instantiation
    """
    if np.sum(forc['matpmt'][:,34]==0) > 0: # null velocity detected
        return None
    ptc = np.nonzero(maillage['contraintes'])
    cnt = np.vstack((maillage['contraintes'][ptc], ptc[0]+1))
    maillessortiestransfert = ptc[0]+1
    jeumaille = np.asarray(list(range(1,maillage['nmailles']+1)))
    injectionmaille = np.zeros((maillage['nmailles'],2))
    wt = np.zeros((maillage['nmailles'], maillage['nmailles']))
    np.fill_diagonal(wt, 1)
    wt = np.vstack((wt, np.zeros((1, maillage['nmailles']))))
    wp = wt
    ndescript = 7
    nsortietransfert = cnt.shape[1]
    nparametres = 150
    dimwp = maillage['nmailles'] * (maillage['nmailles'] + 1)
    dimwt = dimwp
    hm = creermodele("modele", maillage['nmailles'], maillage['topologie'], 
        ndescript, maillage['descripteurs'], temps['dt'], nsortietransfert, maillessortiestransfert,
        nparametres, forc['matpmt'].shape[0], forc['matpmt'], jeumaille, forc['hf'],
        dimwp, dimwt, wp, wt, injectionmaille, forc['matkc'])
    return hm
    
def delete(hm):
    """
    Free the memory associated with the instance number hm
    :param hm: id number of the hydrological model
    :return: null value if success
    """
    value = detruiremodele(hm)
    if value != 0:
        return None
    return value
