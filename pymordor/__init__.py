"""
Python wrapper of the hydrological code MORDOR_TS

Author(s) : Fabrice Zaoui (EDF R&D LNHE)

Copyright EDF 2016-2018

"""

__author__ = "Fabrice Zaoui"
__copyright__ = "Copyright EDF 2016"
__license__ = "GPL"
__maintainer__ = "Fabrice Zaoui"
__email__ = "fabrice.zaoui@edf.fr"
__status__ = "Implementation"
__version__ = "0.02"
__all__ = ['litdonneesmodele', 'mordorglobal', 'modelehydro', 'utils',
           'hm_mordor', 'hf_mordor']

from pymordor import litdonneesmodele
from pymordor import mordorglobal
from pymordor import modelehydro
from pymordor import utils
from pymordor import hm_mordor
from pymordor import hf_mordor
