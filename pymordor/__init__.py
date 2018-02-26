"""
Python wrapper of the hydrological code MORDOR_TS

Author(s) : Fabrice Zaoui (EDF R&D LNHE)

Copyright EDF 2016-2018

"""

__version__ = "0.02"

__all__ = ['litdonneesmodele', 'mordorglobal', 'modelehydro', 'utils']

from pymordor import litdonneesmodele
from pymordor import mordorglobal
from pymordor import modelehydro
from pymordor import utils

