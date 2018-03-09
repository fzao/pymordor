# -*- coding: utf-8 -*-
"""
    Wrapper for the library 'libWrapperModeleHydro' of MORDOR-TS

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys, os
from ctypes import *
import numpy as np

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

def creerbaseforcage(nom, npluvio, carapluvio, nmeteo, carameteo, nqinj, \
                ndates, tdeb, dt0):
    """ handle of weather inputs """
    # Data preparation in ctype format
    nom_c = c_char_p(nom.encode())
    npluvio_c = c_int(npluvio)
    sizetab = 4 * npluvio
    carapluvio = carapluvio.transpose().reshape(carapluvio.size, 1)
    carapluvio_c = (c_double * sizetab)(*carapluvio)
    nmeteo_c = c_int(nmeteo)
    sizetab = 4 * nmeteo
    carameteo = carameteo.transpose().reshape(carameteo.size, 1)
    carameteo_c = (c_double * sizetab)(*carameteo)
    nqinj_c = c_int(nqinj)
    ndates_c = c_int(ndates)
    tm = np.zeros((9, 1))
    tm[0] = tdeb.timetuple().tm_sec
    tm[1] = tdeb.timetuple().tm_min
    tm[2] = tdeb.timetuple().tm_hour
    tm[3] = tdeb.timetuple().tm_mday
    tm[4] = tdeb.timetuple().tm_mon - 1
    tm[5] = tdeb.timetuple().tm_year - 1850
    tm[6] = tdeb.timetuple().tm_wday + 1
    tm[7] = tdeb.timetuple().tm_yday - 1
    tm[8] = tdeb.timetuple().tm_isdst
    tm_c = (c_double * 9)(*tm)
    dt_c = c_double(dt0)
    # calling the library
    valeur = MY_LIBRARY.CreerBaseForcage(nom_c, npluvio_c, \
        byref(carapluvio_c), \
        nmeteo_c, byref(carameteo_c), nqinj_c, ndates_c, \
        byref(tm_c), dt_c)
    # return values in standard types
    return valeur

def remplirsiteforcage(handleforcage, numfeuille, numsite, ndates, valeurssite):
    """ Copy of the time series to the required site """
    # Data preparation in ctype format
    handleforcage_c = c_int(handleforcage)
    numfeuille_c = c_int(numfeuille)
    numsite_c = c_int(numsite)
    ndates_c = c_int(ndates)
    valeurssite_c = (c_double * ndates)(*valeurssite)
    # calling the library
    valeur = MY_LIBRARY.RemplirSiteForcage(handleforcage_c, numfeuille_c, \
        numsite_c, ndates_c, byref(valeurssite_c))
    # return values in standard types
    return valeur

def creermodele(nom, nmailles, topologiemailles, ndescript, \
    descripteursmailles, dt0, nsortietransfert, maillesortietransfert, \
    nparametres, njeux, matriceparametres, jeumaille, handleforcage, \
    dimregpj, dimregtj, regpj, regtj, tabinject, matricekc):
    """ Handle of weather inputs """
    # Data preparation in ctype format
    descripteursmailles = \
        descripteursmailles.transpose().reshape(descripteursmailles.size,1)
    regpj = regpj.transpose().reshape(regpj.size, 1)
    regtj = regtj.transpose().reshape(regtj.size, 1)
    tabinject = tabinject.transpose().reshape(tabinject.size, 1)
    matricekc = matricekc.transpose().reshape(matricekc.size, 1)
    nom_c = c_char_p(nom.encode())
    nmailles_c = c_int(nmailles)
    topologiemailles_c = (c_int * nmailles)(*topologiemailles)
    ndescript_c = c_int(ndescript)
    sizetab = nmailles * ndescript
    descripteursmailles_c = (c_double * sizetab)(*descripteursmailles)
    dt_c = c_double(dt0)
    nsortietransfert_c = c_int(nsortietransfert)
    maillesortietransfert_c = (c_int*nsortietransfert)(*maillesortietransfert)
    nparametres_c = c_int(nparametres)
    njeux_c = c_int(njeux)
    sizetab = njeux * nparametres
    matriceparametres = matriceparametres.transpose()
    matriceparametres = matriceparametres.reshape(matriceparametres.size, 1)
    matriceparametres_c = (c_double * sizetab)(*matriceparametres)
    jeumaille_c = (c_int * nmailles)(*jeumaille)
    handleforcage_c = c_int(handleforcage)
    dimregpj_c = c_int(dimregpj)
    dimregtj_c = c_int(dimregtj)
    regpj_c = (c_double * dimregpj)(*regpj)
    regtj_c = (c_double * dimregtj)(*regtj)
    sizetab = 2 * nmailles
    tabinject_c = (c_int * sizetab)(*tabinject)
    sizetab = 366 * nmailles
    matricekc_c = (c_double * sizetab)(*matricekc)
    # calling the library
    valeur = MY_LIBRARY.CreerModele(nom_c, nmailles_c, \
        byref(topologiemailles_c), ndescript_c, byref(descripteursmailles_c), \
        dt_c, nsortietransfert_c, byref(maillesortietransfert_c), \
        nparametres_c, njeux_c, byref(matriceparametres_c), \
        byref(jeumaille_c), handleforcage_c, dimregpj_c, dimregtj_c, \
        byref(regpj_c), byref(regtj_c), byref(tabinject_c), \
        byref(matricekc_c))
    # return values in standard types
    return valeur

def getdimmodele(handlemodele):
    """ Sizes of model Handle """
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
    nmailles_c = c_int()
    nsortietransfert_c = c_int()
    nbuffer_c = c_int()
    dt_c = c_double()
    # calling the library
    valeur = MY_LIBRARY.GetDimModele(handlemodele_c, byref(nmailles_c), \
        byref(nsortietransfert_c), byref(nbuffer_c), byref(dt_c))
    # return values in standard types
    return{'nmailles':nmailles_c.value, 'nsortietransfert':nsortietransfert_c.value,
            'nbuffer':nbuffer_c.value, 'pdt':dt_c.value}

def initmodele(handlemodele, tdeb, etatproductionzero, \
    etattransfertzero, bufferproductionzero):
    """ State initialization of model Handle """
    # Get dimensions and ravel
    dimep1 = etatproductionzero.shape[0]
    dimep2 = etatproductionzero.shape[1]
    #etatproductionzero = etatproductionzero.ravel()
    dimet1 = etattransfertzero.shape[0]
    dimet2 = etattransfertzero.shape[1]
    #etattransfertzero = etattransfertzero.ravel()
    dimbp1 = bufferproductionzero.shape[0]
    dimbp2 = bufferproductionzero.shape[1]
    #bufferproductionzero = bufferproductionzero.ravel()
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
    tm = np.zeros((9, 1))
    tm[0] = tdeb.timetuple().tm_sec
    tm[1] = tdeb.timetuple().tm_min
    tm[2] = tdeb.timetuple().tm_hour
    tm[3] = tdeb.timetuple().tm_mday
    tm[4] = tdeb.timetuple().tm_mon - 1
    tm[5] = tdeb.timetuple().tm_year - 1850
    tm[6] = tdeb.timetuple().tm_wday + 1
    tm[7] = tdeb.timetuple().tm_yday - 1
    tm[8] = tdeb.timetuple().tm_isdst
    tm_c = (c_double * 9)(*tm)
    etatproductionzero = \
        etatproductionzero.reshape(etatproductionzero.size, 1)
    sizetab = dimep1 * dimep2
    etatproductionzero_c = (c_double * sizetab)(*etatproductionzero)
    dimep1_c = c_int(dimep1)
    dimep2_c = c_int(dimep2)
    etattransfertzero = \
        etattransfertzero.reshape(etattransfertzero.size, 1)
    sizetab = dimet1 * dimet2
    etattransfertzero_c = (c_double * sizetab)(*etattransfertzero)
    dimet1_c = c_int(dimet1)
    dimet2_c = c_int(dimet2)
    bufferproductionzero = \
        bufferproductionzero.reshape(bufferproductionzero.size, 1)
    sizetab = dimbp1 * dimbp2
    bufferproductionzero_c = (c_double * sizetab)(*bufferproductionzero)
    dimbp1_c = c_int(dimbp1)
    dimbp2_c = c_int(dimbp2)
    # calling the library
    valeur = MY_LIBRARY.InitModele(handlemodele_c, byref(tm_c), \
        byref(etatproductionzero_c), dimep1_c, dimep2_c, \
        byref(etattransfertzero_c), dimet1_c, dimet2_c, \
        byref(bufferproductionzero_c), dimbp1_c, dimbp2_c)
    # return values in standard types
    return valeur

def runmordor(handlemodele, tfin):
    """ Run the spatialized Modor for the model Handle """
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
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
    tm_c = (c_double * 9)(*tm)
    # calling the library
    valeur = MY_LIBRARY.RunMordor(handlemodele_c, byref(tm_c))
    # return values in standard types
    return valeur

def getintercept(handlemodele, numintercept):
    """ Get the flux and the state of the model Handle """
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
    numintercept_c = c_int(numintercept)
    intercept_c = POINTER(c_double)()
    # calling the library
    valeur = MY_LIBRARY.GetIntercept(handlemodele_c, numintercept_c, \
        byref(intercept_c))
    # return values in standard types
    return valeur, intercept_c

def getetatmodele(handlemodele):
    """ Get the state of the model """
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
    etatproduction_c = POINTER(c_double)()
    etattransfert_c = POINTER(c_double)()
    bufferproduction_c = POINTER(c_double)()
    qmoyen_c = POINTER(c_double)()
    # calling the library
    valeur = MY_LIBRARY.GetEtatModele(handlemodele_c, byref(etatproduction_c), \
        byref(etattransfert_c), byref(bufferproduction_c), byref(qmoyen_c))
    if valeur != 0:
        return None
    # return values in c_types
    return{'etatproduction':etatproduction_c, \
            'etattransfert':etattransfert_c, \
            'bufferproduction':bufferproduction_c, \
            'qmoyen': qmoyen_c}

def getdateetat(handlemodele):
    """ Get the date associated with the state of the model """
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
    ptr_tm_etat_c = POINTER(c_double)()
    # calling the library
    valeur = MY_LIBRARY.GetDateEtat(handlemodele_c, byref(ptr_tm_etat_c))
    # return values in standard types
    return valeur, ptr_tm_etat_c

def geterreur():
    """ Error message """
    # Data preparation in ctype format
    MY_LIBRARY.GetErreur.restype = POINTER(c_char)
    # calling the library
    valeur = MY_LIBRARY.GetErreur()
    # renvoie du message
    return string_at(valeur)
    
def getversion():
    """ Mordor code version """
    # Data preparation in ctype format
    MY_LIBRARY.VersionModele.restype = POINTER(c_char)
    # calling the library
    valeur = MY_LIBRARY.VersionModele()
    # renvoie du message
    return string_at(valeur)

def detruiremodele(handlemodele):
    """ Delete the hydrological model """
    # Data preparation in ctype format
    handlemodele_c = c_int(handlemodele)
    # calling the library
    valeur = MY_LIBRARY.DetruireModele(handlemodele_c)
    # return values in standard types
    return valeur

def detruireforcage(handleforcage):
    """ Delete the inputs """
    # Data preparation in ctype format
    handleforcage_c = c_int(handleforcage)
    # calling the library
    valeur = MY_LIBRARY.DetruireForcage(handleforcage_c)
    # return values in standard types
    return valeur
    
def mktime(ptr_tm):
    """  Conversion date -> time
         Update fields of the tm structure
         Give the elapsed time in days since 1850
    """
    # Data preparation in ctype format
    ptr_tm_fin_c = (c_double * 9)(*ptr_tm)
    # calling the library
    valeur = MY_LIBRARY.mktime_(byref(ptr_tm_fin_c))
    # return values in standard types
    return valeur, ptr_tm_fin_c

