# -*- coding: utf-8 -*-
"""
    Basic functions for MORDOR-TS

    Author(s) : Fabrice Zaoui

    Copyright EDF 2016

"""

import datetime
import numpy as np

def lambert2geo(x, y):
    """
    Change Lambert II coordinates (x,y) (m) into geographical \
    coordinates (latitude, longitude)
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
    longitude = DELTA + g/N #  radians !
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

    return latitude, longitude

def datenum(date):
    """
    Change the date format : Year/Month/Day/Hour/Minute/Second \
    to a scalar number
    """
    annee = date[0]
    mois = date[1]
    jour = date[2]
    heure = date[3]
    mn = date[4]
    seconde = date[5]

    rep = ((np.mod(annee, 100) != 0) & (np.mod(annee, 4) == 0)) \
        | (np.mod(annee, 400) == 0)

    decimal_part = (seconde * (1. /(24. * 3600.))) + \
        (mn * (1. / (24. * 60.))) + (heure * (1. / 24.))

    # convert of month and day
    integer_part = jour + np.floor((mois * 3057. - 3007.) / 100.)

    # Beyond February
    integer_part = integer_part + ((mois < 3) - 1)

    # Beyond February and non leap year
    integer_part = integer_part + (((mois < 3) | (rep)) -1);

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

    return scalaire

def datevec(n):
    """
    Genrate a date vector [Y,M,D,H,Mn,S] from a scalar number
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
    temp = n - (365.0 * year + np.ceil(0.25 * year) - \
        np.ceil(0.01 * year) + np.ceil(0.0025 * year))
    mask = (temp <= 0)
    if mask:
        year = year - 1
        n = n - (365.0 * year + np.ceil(0.25 * year) - \
        np.ceil(0.01 * year) + np.ceil(0.0025 * year))
    else:
        n = temp

    # month
    month = int(n / 29)

    # valeurs de retour
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

    return y, mo, d, h, m, s

def calcidjour(datedeb, datefin):
    """
    Gives the number of the day of the year for all the days between two dates
    ex.:
       datefirst = datetime.date(2008, 2, 1)
       datelast = datetime.date(2009, 12, 31)
       id_jour = calcidjour(datefirst, datelast)
    """
    date_gen = [datedeb + datetime.timedelta(days=x) for x in range(0, (datefin-datedeb).days)]
    id_jour= [[date_gen[x].timetuple().tm_yday] for x in range(0, len(date_gen))]

    return id_jour

