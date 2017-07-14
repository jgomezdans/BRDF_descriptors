#!/usr/bin/env python

"""Retrieve BRDF shape descriptors from MCD43A1 and MCD43A2 MODIS products.
BRDF descriptors are here assumed to be the weights to the linear kernel
model fit to the data. In this case, we assume that the MODIS set of 
kernels have been used.
"""

# KaFKA A fast Kalman filter implementation for raster based datasets.
# Copyright (c) 2017 J Gomez-Dans. All rights reserved.
#
# This file is part of KaFKA.
#
# KaFKA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KaFKA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KaFKA.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import glob
import fnmatch


import numpy as np
import gdal

__author__ = "J Gomez-Dans"
__copyright__ = "Copyright 2017 J Gomez-Dans"
__version__ = "1.0 (13.07.2017)"
__license__ = "GPLv3"
__email__ = "j.gomez-dans@ucl.ac.uk"


def process_time_input(timestamp):
    """Processes a timestamp given either as (i) a string in 
    "%Y-%m-%d" format, (ii) a string in "%Y%j" format or
    (iii) a datetime.datetime object. Returns a datetime.datetime
    ojbect, and raises ValueError if none of the options fits."""
    if type(timestamp) == datetime.datetime:
        output_time = timestamp
    elif type(timestamp) == str:
        try: 
            output_time = datetime.datetime.strptime(timestamp, 
                                                    "%Y-%m-%d")
        except ValueError:
            try:
                output_time = datetime.datetime.strptime(timestamp, 
                                                    "%Y%j")
            except ValueError:
                raise ValueError("The passed timestamp wasn't either " +
                    'a "%Y-%m-%d" string, a "%Y%j" string')
    else:
        raise ValueError("You can only use a string or a datetime object")
    return output_time


class RetrieveBRDFDescriptors(object):
    """Retrieving BRDF descriptors."""
    def __init__ (self, tile, mcd43a1_dir, start_time, end_time=None, 
            mcd43a2_dir=None):
        """The class needs to locate the data granules. We assume that
        these are available somewhere in the filesystem and that we can
        index them by location (MODIS tile name e.g. "h19v10") and
        time. The user can give a folder for the MCD43A1 and A2 granules,
        and if the second is ignored, it will be assumed that they are
        in the same folder. We also need a starting date (either a
        datetime object, or a string in "%Y-%m-%d" or "%Y%j" format. If
        the end time is not specified, it will be set to the date of the
        latest granule found."""

        self.tile = tile
        self.start_time = process_time_input(start_time)
        if end_time is not None:
            self.end_time = process_time_input(end_time)
        else:
            self.end_time = None

        
    
