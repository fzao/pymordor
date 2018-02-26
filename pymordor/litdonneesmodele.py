# -*- coding: utf-8 -*-
"""
    Wrapper for the library 'libLitDonneesModele' of MORDOR-TS

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys, os
from ctypes import *
import numpy as np

MAXPOSTES = 1500
MAXCARREAU = 2000
MAXCONTRAINTES = 1500
LENSTR = 200
LIBMORDOR = os.environ.get('LIBMORDOR')

if sys.platform.startswith('linux'):
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'/libLitDonneesModele.so')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libLitDonneesModele.so. Check the environmental variable LIBMORDOR.')
elif sys.platform.startswith('win'):
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'\libLitDonneesModele.dll')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libLitDonneesModele.dll. Check the environmental variable LIBMORDOR.')
else:
    raise Exception(u'unsupported OS')

def litpostes(unite, adresse):
    """ Read all the data files (rain and weather) """
    # Data preparation in ctype format
    u_c = c_int(unite)
    adresse_c = c_char_p(adresse.encode())
    npostes_c = c_int()
    sizetab = 4 * MAXPOSTES
    carapostes_c = (c_double * sizetab)(0.0)
    sizetab = LENSTR*MAXPOSTES
    nompostes_c = (c_char * sizetab)()
    fichpostes_c = (c_char * sizetab)()

    # calling the library
    MY_LIBRARY.lit_postes(byref(u_c), adresse_c, byref(npostes_c), \
           byref(carapostes_c), byref(nompostes_c), byref(fichpostes_c))

    # return values in standard types
    npostes = npostes_c.value
    car = np.array(carapostes_c)
    cara = car.reshape(4, MAXPOSTES).transpose()
    carac = cara[0:npostes, :]
    nomp = str(nompostes_c.value)
    nompo = nomp.replace("\\n", " ")
    nompos = nompo.split()
    fic = str(fichpostes_c.value)
    fich = fic.replace("\\n", " ")
    fiche = fich.split()

    return npostes, carac, nompos, fiche

def litmaillage(unite, adresse):
    """ Read the mesh of the watershed (Carreau format) """
    # Data preparation in ctype format
    u_c = c_int(unite)
    adresse_c = c_char_p(adresse.encode())
    nmailles_c = c_int()
    topologie_c = (c_int * MAXCARREAU)()
    contraintes_c = (c_int * MAXCARREAU)()
    sizetab = 7*MAXCARREAU
    descripteurs_c = (c_double * sizetab)(0.0)

    # calling the library
    MY_LIBRARY.lit_maillage(byref(u_c), adresse_c, byref(nmailles_c), \
          byref(topologie_c), byref(descripteurs_c), byref(contraintes_c))

    # return values in standard types
    nmailles = nmailles_c.value
    top = np.array(topologie_c)
    topo = top[0:nmailles]
    con = np.array(contraintes_c)
    cont = con[0:nmailles]
    des = np.array(descripteurs_c)
    desc = des.reshape(7, MAXCARREAU).transpose()
    descr = desc[0:nmailles, :]
    #descri = np.delete(descr, np.s_[4], axis=1)

    return nmailles, topo, cont, descr

def litcontraintes(unite, adresse):
    """ Read a list of constraints on the points of a mesh """
    # Data preparation in ctype format
    u_c = c_int(unite)
    adresse_c = c_char_p(adresse.encode())
    ncontraintes_c = c_int()
    sizetab = MAXCONTRAINTES * 2
    xy_c = (c_double * sizetab)(0.0)
    sizetab = 2*MAXCONTRAINTES
    typec_c = (c_char * sizetab)()
    sizetab = LENSTR*MAXCONTRAINTES
    noms_c = (c_char * sizetab)()
    fichiers_c = (c_char * sizetab)()

    # calling the library
    MY_LIBRARY.lit_contraintes(byref(u_c), adresse_c, byref(ncontraintes_c), \
       byref(xy_c), byref(typec_c), byref(noms_c), byref(fichiers_c))

    # return values in standard types
    ncontraintes = ncontraintes_c.value
    xy_ = np.array(xy_c)
    xy__ = xy_.reshape(2, MAXCONTRAINTES).transpose()
    xy___ = xy__[0:ncontraintes, :]
    ty_ = str(typec_c.value)
    typ = ty_.replace("\\n", " ")
    typec = typ.split()
    no_ = str(noms_c.value)
    nom = no_.replace("\\n", " ")
    noms = nom.split()
    fic = str(fichiers_c.value)
    fich = fic.replace("\\n", " ")
    fiche = fich.split()

    return ncontraintes, xy___, typec, noms, fiche
