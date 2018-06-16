# -*- coding: utf-8 -*-
"""
    Basic functions for MORDOR-TS

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016-2018

"""

import datetime
import numpy as np


def lambert2geo(x, y):
    """
    Change Lambert II coordinates (x,y) (m) into geographical \
    coordinates (latitude, longitude)
    :param x: x-coordinate
    :param y: y-coordinate
    :return: a dictionary of the new coordinates
    """
    taille = x.size
    XS = np.ones(taille)*600000.0
    YS = np.ones(taille)*8199695.768
    N = 0.7289686274
    C = 11745793.39
    E = 0.08248325676
    DELTA = 0.040792344
    r = np.sqrt(np.power(x-XS, 2)+np.power(y-YS, 2))
    g = np.arctan((x-XS)/(YS-y))
    longitude = DELTA + g/N  # radians !
    lambert = (-1.0/N)*np.log(np.abs(r/C))
    p = np.pi*42.0/180.0    # starting value
    f = 0.0
    q = 0.0
    v = 0.0
    o = 0.0
    while 1:
        if np.max(np.abs(v-p)) < 1.e-6:
            break
        f = p
        o = lambert - 0.5*np.log((1.0+np.sin(f))/(1.0-np.sin(f))) \
            + E/2.0*np.log((1.0+E*np.sin(f))/(1.0-E*np.sin(f)))
        f = p + 0.0001
        q = lambert - 0.5*np.log((1.0+np.sin(f))/(1.0-np.sin(f))) \
            + E/2.0*np.log((1.0+(E*np.sin(f)))/(1.0-E*np.sin(f)))
        v = p
        p = p-0.0001*o/(q-o)
    latitude = p
    return {'longitude': longitude, 'latitude': latitude}


def datenum(date):
    """
    Change the date format : Year/Month/Day/Hour/Minute/Second \
    to a scalar number
    :param date: a date as a list
    :return: the corresponding number (scalar value)
    """
    annee = date[0]
    mois = date[1]
    jour = date[2]
    heure = date[3]
    mn = date[4]
    seconde = date[5]
    rep = ((np.mod(annee, 100) != 0) & (np.mod(annee, 4) == 0)) \
        | (np.mod(annee, 400) == 0)
    decimal_part = (seconde * (1. / (24. * 3600.))) + \
        (mn * (1. / (24. * 60.))) + (heure * (1. / 24.))
    # convert of month and day
    integer_part = jour + np.floor((mois * 3057. - 3007.) / 100.)
    # Beyond February
    integer_part = integer_part + ((mois < 3) - 1)
    # Beyond February and non leap year
    integer_part = integer_part + (((mois < 3) | (rep)) - 1)
    # Conversion of years
    leap_year_case = annee * 365. + (annee / 4.) - np.floor(annee / 100.) +\
        np.floor(annee / 400.)
    not_leap_year_case = annee * 365. + np.floor(annee / 4.) + \
        1 - np.floor(annee / 100.) + np.floor(annee / 400.)
    rep = ((np.mod(annee, 100) != 0) & (np.mod(annee, 4) == 0))\
        | (np.mod(annee, 400) == 0)
    if rep:
        not_leap_year_case = 0
    else:
        leap_year_case = 0
    integer_part = integer_part + leap_year_case + not_leap_year_case
    scalaire = integer_part + decimal_part
    return {'scalar': scalaire}


def datevec(n):
    """
    Generate a date [Y,M,D,H,Mn,S] from a scalar number
    :param n:
    :return: a dictionary with the date information
    """
    common_year = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    leap_year = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    # hour, minute, second
    second = 86400. * (n - np.floor(n))
    hour = np.floor(second / 3600.)
    second = second - 3600. * hour
    minute = np.floor(second / 60.)
    second = second - 60. * minute
    # year
    n = np.floor(n)
    year = np.floor(n / 365.2425)
    temp = n - (365.0 * year + np.ceil(0.25 * year)
                - np.ceil(0.01 * year) + np.ceil(0.0025 * year))
    mask = (temp <= 0)
    if mask:
        year = year - 1
        n = n - (365.0 * year + np.ceil(0.25 * year)
                 - np.ceil(0.01 * year) + np.ceil(0.0025 * year))
    else:
        n = temp
    # month
    month = int(n / 29)
    # return value
    rep = ((np.mod(year, 100) != 0) & (np.mod(year, 4) == 0))\
        | (np.mod(year, 400) == 0)
    if rep:
        month_day_mat = leap_year[month]
    else:
        month_day_mat = common_year[month]
    if n > month_day_mat:
        month = month + 1
    if rep:
        month_day_mat = leap_year[month-1]
    else:
        month_day_mat = common_year[month-1]
    day = n - month_day_mat
    y = int(year)
    mo = int(month)
    d = int(day)
    h = int(hour)
    m = int(minute)
    s = second
    return {'year': y, 'month': mo, 'day': d,
            'hour': h, 'minute': m, 'second': s}


def calcidjour(datedeb, datefin, txunit):
    """
    Gives the number of the day of the year for all the days between two dates
    ex.:
       datefirst = datetime.date(2008, 2, 1)
       datelast = datetime.date(2009, 12, 31)
       id_jour = calcidjour(datefirst, datelast)
    :param datedeb: first date (datetime format)
    :param datefin: end date (datetime format)
    :return: number of days
    """
    delta = datefin - datedeb
    if txunit == 'days':
        longueur = delta.days + 1
        date_gen = [datedeb + datetime.timedelta(days=x)
                    for x in range(0, longueur)]
    elif txunit == 'hours':
        longueur = delta.days*24+delta.seconds/3600 + 1
        longueur = int(longueur)
        date_gen = [datedeb + datetime.timedelta(seconds=3600*x)
                    for x in range(0, longueur)]
    id_jour = [[date_gen[x].timetuple().tm_yday] for x in range(0, longueur)]

    return {'id_days': id_jour}


def time_prep(firstdate, lastdate, step):
    """
    Preparation of information on the calculation times
    :param firstdate: date of the begining of the calculation (datetime format)
    :param lastdate: date of the end of the calculation (datetime format)
    :param step: a character indicating the calculation step
                ('J' for days and 'H' for 'hours')
    :return: a dictionary of global information including the time period value
            ('ndates')
    """
    if isinstance(firstdate, datetime.datetime) & \
       isinstance(lastdate, datetime.datetime):
        diffdate = lastdate - firstdate
        if step == 'D':
            txunit = "days"
            dt = 86400
            ndates = int(diffdate.days + 1)
        elif step == 'H':
            txunit = "hours"
            dt = 3600
            ndates = int(diffdate.days * 24 + diffdate.seconds/3600 + 1)
        else:
            return None

    else:
        return None
    return{'dt': dt, 'date1': firstdate, 'date2': lastdate,
           'txunit': txunit, 'ndates': ndates, 'step': step}


def cutarray(tab, firstdate, lastdate, txunit):
    """
    Extraction of data from a time series
    :param tab: array of data
    :param firstdate: date of the begining of the calculation (datetime format)
    :param lastdate: date of the end of the calculation (datetime format)
    :param txunit: time step 'days' or 'hours'
    :return: 1D-array of values between firstdate and lastdate (time series)
    """
    nc = tab.shape[1]
    ndt = tab.shape[0]
    # check that all the time steps are present
    date1 = datetime.datetime(int(tab[0, 0]), int(tab[0, 1]), int(tab[0, 2]),
                              int(tab[0, 3]), int(tab[0, 4]))
    date2 = datetime.datetime(int(tab[-1, 0]), int(tab[-1, 1]),
                              int(tab[-1, 2]), int(tab[-1, 3]),
                              int(tab[-1, 4]))
    if date2 <= date1:
        return None
    else:
        delta = date2 - date1
    if txunit == 'days':
        nbok = delta.days + 1
    elif txunit == 'hours':
        nbok = int(delta.days*24 + delta.seconds/3600 + 1)
    if nbok != ndt:
        return None
    if firstdate >= lastdate:
        return None
    # indices for cutting
    i1 = 0
    i2 = ndt
    for i in range(0, ndt):
        datec = datetime.datetime(int(tab[i, 0]), int(tab[i, 1]),
                                  int(tab[i, 2]), int(tab[i, 3]),
                                  int(tab[i, 4]))
        if datec <= firstdate:
            i1 = i
        if datec <= lastdate:
            i2 = i
    # extracting results
    return tab[i1:i2, 5]


def upstream_list(maillage, id_exut):
    """
    upstream of id_exut
    :param maillage: dictionary of the hydrological mesh
    :param id_exut: outlet id number
    :return: 1D-array of cell numbers
    """
    nmailles = range(1, maillage['nmailles']+1)
    mailleamont = [id_exut]
    recherche = [id_exut]
    while len(recherche) > 0:
        ajout = []
        for i in range(0, len(recherche)):
            im = recherche[i]
            ajout.extend(np.take(nmailles,
                                 np.where(maillage['topologie'] == im))
                         .ravel().tolist())
        mailleamont.extend(ajout)
        recherche = ajout
    return np.array(mailleamont)
