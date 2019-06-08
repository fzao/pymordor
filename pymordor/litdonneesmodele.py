# -*- coding: utf-8 -*-
"""
    Wrapper for the library 'libLitDonneesModele' of MORDOR-TS

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""
import sys
import os
from ctypes import *
import numpy as np

MAXPOSTES = 1500
MAXCARREAU = 2000
MAXCONTRAINTES = 1500
LENSTR = 200
LIBMORDOR = os.environ.get('LIBMORDOR')

if sys.platform.startswith('linux') | sys.platform.startswith('darwin'):
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'/libLitDonneesModele.so')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libLitDonneesModele.so. Check the environmental variable LIBMORDOR.')
elif sys.platform.startswith('win'):
    try:
        MY_LIBRARY = CDLL(LIBMORDOR+'\\libLitDonneesModele.dll')
    except Exception:
        raise Exception('unable to load the dynamic library: \
libLitDonneesModele.dll. Check the environmental variable LIBMORDOR.')
else:
    raise Exception(u'unsupported OS')


def litpostes(postfile):
    """
    Read all the data files (rain and weather)
    :param postfile: the name (string char) of the file defining the positions
    :return: a dictionary of information on the positions
    """
    # Data preparation in ctype format
    if os.path.isfile(postfile):
        u_c = c_int(np.random.randint(10, 1000000))
        adresse_c = c_char_p(postfile.encode())
        npostes_c = c_int()
        sizetab = 4 * MAXPOSTES
        carapostes_c = (c_double * sizetab)(0.0)
        sizetab = LENSTR*MAXPOSTES
        nompostes_c = (c_char * sizetab)()
        fichpostes_c = (c_char * sizetab)()
        # Calling the library
        MY_LIBRARY.lit_postes(byref(u_c), adresse_c, byref(npostes_c),
                              byref(carapostes_c), byref(nompostes_c),
                              byref(fichpostes_c))
        # Return values in standard types
        npostes = npostes_c.value
        car = np.array(carapostes_c)
        cara = car.reshape(4, MAXPOSTES).transpose()
        carac = cara[0:npostes, :]
        nomp = str(nompostes_c.value)
        nomp = nomp.replace("b", "")
        nomp = nomp.replace("'", "")
        nompo = nomp.replace("\\n", " ")
        nompos = nompo.split()
        fic = str(fichpostes_c.value)
        fic = fic.replace("b", "")
        fic = fic.replace("'", "")
        fich = fic.replace("\\n", " ")
        fiche = fich.split()
        return {'npostes': npostes, 'carapostes': carac, 'nompostes': nompos,
                'fichpostes': fiche}
    else:
        return None


def litmaillage(meshfile):
    """
    Read the mesh of the watershed (Carreau format)
    :param meshfile: the name (string char) of the file defining
                        the hydrological mesh
    :return: a dictionary of information on the mesh
    """
    if os.path.isfile(meshfile):
        # Data preparation in ctype format
        u_c = c_int(np.random.randint(10, 1000000))
        adresse_c = c_char_p(meshfile.encode())
        nmailles_c = c_int()
        nbandes_c = c_int()
        topologie_c = (c_int * MAXCARREAU)()
        contraintes_c = (c_int * MAXCARREAU)()
        sizevar = 7 * MAXCARREAU
        descripteurs_c = (c_double * sizevar)(0.0)
        sizevar = 10 * MAXCARREAU
        alt_c = (c_double * sizevar)(0.0)
        # Calling the library
        MY_LIBRARY.lit_maillage_bandes(byref(u_c), adresse_c,
                                       byref(nmailles_c), byref(nbandes_c),
                                       byref(topologie_c),
                                       byref(descripteurs_c),
                                       byref(contraintes_c), byref(alt_c))
        # Return values in standard types
        nmailles = nmailles_c.value
        nbandes = nbandes_c.value
        top = np.array(topologie_c)
        topo = top[0:nmailles]
        con = np.array(contraintes_c)
        cont = con[0:nmailles]
        des = np.array(descripteurs_c)
        desc = des.reshape(7, MAXCARREAU).transpose()
        descr = desc[0:nmailles, :]
        alt = np.array(alt_c)
        alti = alt.reshape(10, MAXCARREAU).transpose()
        altit = alti[0:nmailles, 0:nbandes]
        nval = np.sum(cont > 0)
        cntr = np.zeros((nval, 2))
        k = 0
        for i in range(nmailles):
            if cont[i] > 0:
                cntr[k, 0] = i+1
                cntr[k, 1] = cont[i]
                k = k + 1
        return {'nmailles': nmailles, 'nbandes': nbandes, 'topologie': topo,
                'descripteurs': descr,
                'contraintes': cont, 'altitudes': altit, 'cntr': cntr}
    else:
        return None


def litcontraintes(confile):
    """
    Read a list of constraints on the points of a mesh
    :param confile: the name (string char) of the file defining the constraints
    :return: a dictionary of information on the constraints
    """
    if os.path.isfile(confile):
        # Data preparation in ctype format
        u_c = c_int(np.random.randint(10, 1000000))
        adresse_c = c_char_p(confile.encode())
        ncontraintes_c = c_int()
        sizetab = MAXCONTRAINTES * 2
        xy_c = (c_double * sizetab)(0.0)
        sizetab = 2*MAXCONTRAINTES
        typec_c = (c_char * sizetab)()
        sizetab = LENSTR*MAXCONTRAINTES
        noms_c = (c_char * sizetab)()
        fichiers_c = (c_char * sizetab)()
        # calling the library
        MY_LIBRARY.lit_contraintes(byref(u_c), adresse_c,
                                   byref(ncontraintes_c),
                                   byref(xy_c), byref(typec_c),
                                   byref(noms_c), byref(fichiers_c))
        # Return values in standard types
        ncontraintes = ncontraintes_c.value
        xy_ = np.array(xy_c)
        xy__ = xy_.reshape(2, MAXCONTRAINTES).transpose()
        xy___ = xy__[0:ncontraintes, :]
        ty_ = str(typec_c.value)
        ty_ = ty_.replace("b", "")
        ty_ = ty_.replace("'", "")
        typ = ty_.replace("\\n", " ")
        typec = typ.split()
        no_ = str(noms_c.value)
        no_ = no_.replace("b", "")
        no_ = no_.replace("'", "")
        nom = no_.replace("\\n", " ")
        noms = nom.split()
        fic = str(fichiers_c.value)
        fic = fic.replace("b", "")
        fic = fic.replace("'", "")
        fich = fic.replace("\\n", " ")
        fiche = fich.split()
        return {'ncontraintes': ncontraintes, 'xy': xy___, 'typec': typec,
                'noms': noms, 'fichiers': fiche}
    else:
        return None


def litficmeteo(rep, temps, nom_bv):
    """
    Read weather information from files
    :param rep: the folder where are located the files of the weather
    :param temps: a dictionary concerning the calculation times
    :param nom_bv: name of the watershed
    :return: a dictionary containing values for the rain and the temperatures
                for all the period
    """
    # Folders and filenames
    reprain = rep + "/Meteo/Precip/"
    if temps['dt'] == 86400:
        reptmin = rep + "/Meteo/Tn/"
        reptmax = rep + "/Meteo/Tx/"
    elif temps['dt'] == 3600:
        reptmin = rep + "/Meteo/Tair/"
        reptmax = reptmin
    else:
        return None
    radrain = reprain + "Forcage_carreau_" + nom_bv
    radtmin = reptmin + "Forcage_carreau_" + nom_bv
    radtmax = reptmax + "Forcage_carreau_" + nom_bv
    # Read files
    a1 = temps["date1"].year
    a2 = temps["date2"].year
    id_d = temps["date1"].timetuple().tm_yday
    id_f = id_d + temps["ndates"]
    filerain = radrain + "_" + str(a1) + ".txt"
    # rain = np.loadtxt(filerain) #AP# 20180724
    rain = np.loadtxt(filerain,skiprows=id_d-1)
    filetmin = radtmin + "_" + str(a1) + ".txt"
    #tmin = np.loadtxt(filetmin) #AP# 20180724
    tmin = np.loadtxt(filetmin,skiprows=id_d-1)
    filetmax = radtmax + "_" + str(a1) + ".txt"
    #tmax = np.loadtxt(filetmax) #AP# 20180724
    tmax = np.loadtxt(filetmax,skiprows=id_d-1)
    for i in list(range(a1+1, a2+1)):
        filerain = radrain + "_" + str(i) + ".txt"
        rain = np.vstack((rain, np.loadtxt(filerain)))
        filetmin = radtmin + "_" + str(i) + ".txt"
        tmin = np.vstack((tmin, np.loadtxt(filetmin)))
        filetmax = radtmax + "_" + str(i) + ".txt"
        tmax = np.vstack((tmax, np.loadtxt(filetmax)))
    return {'rain': rain, 'tmin': tmin, 'tmax': tmax}
