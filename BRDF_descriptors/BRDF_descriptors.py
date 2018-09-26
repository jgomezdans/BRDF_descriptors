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
from pathlib import Path

import numpy as np
import gdal

__author__ = "J Gomez-Dans"
__copyright__ = "Copyright 2017, 2018 J Gomez-Dans"
__license__ = "GPLv3"
__email__ = "j.gomez-dans@ucl.ac.uk"

GDAL2NUMPY = {gdal.GDT_Byte:   np.uint8,
              gdal.GDT_UInt16:   np.uint16,
              gdal.GDT_Int16:   np.int16,
              gdal.GDT_UInt32:   np.uint32,
              gdal.GDT_Int32:   np.int32,
              gdal.GDT_Float32:   np.float32,
              gdal.GDT_Float64:   np.float64,
              gdal.GDT_CInt16:   np.complex64,
              gdal.GDT_CInt32:   np.complex64,
              gdal.GDT_CFloat32:   np.complex64,
              gdal.GDT_CFloat64:   np.complex128
              }

def find_granules(dire, tile, product, start_time, end_time):
    """Find MCD43 granules based on folder, tile and product type (A1
    or A2). Returns a dictionary of datetimes of the products and
    granules, or raises an IOError exception if not files found."""
    times = []
    fnames = []
    path = Path(dire)
    start_year = start_time.year
    end_year = end_time.year
    granules_start = path.rglob(f"**/MCD43{product:s}.A{start_year:4d}*.{tile:s}.*.hdf")
    granules = [f  for f in granules_start] 
    if end_year != start_year:
        granules_end = path.rglob(f"**/MCD43{product:s}.A{end_year:4d}*.{tile:s}.*.hdf")
        granules = granules + [f for f in granules_end] 
    granules = list(set(granules))
    if len(granules) == 0:
        raise IOError("Couldn't find any MCD43%s files in %s" % (product, dire))
    for granule in granules:
        fich = os.path.basename (granule)
        timex = datetime.datetime.strptime(fich.split(".")[1][1:], "%Y%j")
        if timex >= start_time and \
            (end_time is None or timex <= end_time ):
            times.append (timex)
            fnames.append(granule.as_posix())
    return dict(list(zip(times, fnames)))


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


def open_gdal_dataset(fname, roi=None):
    g = gdal.Open(fname)
    if g is None:
        raise IOError("Can't open %s" % fname)
    if roi is None:
        data = g.ReadAsArray()
    else:
        ulx, uly, lrx, lry = roi
        xoff = ulx
        yoff = uly
        xcount = lrx - ulx
        ycount = lry - uly
        data = g.ReadAsArray(xoff, yoff, xcount, ycount).astype(
                             GDAL2NUMPY[g.GetRasterBand(1).DataType])
    return data


def process_masked_kernels(band_no, a1_granule, a2_granule,
                           band_transfer=None, roi=None):
    if band_transfer is not None:
        band_no = band_transfer[band_no]

    fname_a1 = 'HDF4_EOS:EOS_GRID:"%s":MOD_Grid_BRDF:' % (a1_granule)
    fname_a2 = 'HDF4_EOS:EOS_GRID:"%s":MOD_Grid_BRDF:' % (a2_granule)
    try:
        fdata = fname_a1 + 'BRDF_Albedo_Parameters_Band%d' % (band_no)
    except TypeError:
        fdata = fname_a1 + 'BRDF_Albedo_Parameters_%s' % (band_no)

    fsnow = fname_a2 + 'Snow_BRDF_Albedo'
    fland = fname_a2 + 'BRDF_Albedo_LandWaterType'
    func = fname_a2 + 'BRDF_Albedo_Uncertainty'   # % a2_granule
    try:
        fqa = fname_a2 + 'BRDF_Albedo_Band_Quality_Band%d' % band_no
    except TypeError:
        fqa = fname_a1 + 'BRDF_Albedo_Band_Mandatory_Quality_%s' % band_no

    for fname in [fdata, fsnow, fland, fqa]:
        data = open_gdal_dataset(fname, roi)
        if fname.find("Albedo_Parameters") >= 0:
            # Read kernels, post process
            kernels = process_kernels(data)
        elif fname.find("Snow") >= 0:
            # Read snow mask... post process
            snow = process_snow(data)
        elif fname.find("XXXXXLandWaterType") >= 0:
            shp = data.shape
            land = np.in1d(data, [1, 3, 4, 5])    # data == 1 # Only land
            land = land.reshape(shp)

        # elif fname.find("BRDF_Albedo_Uncertainty") >= 0:
        #    unc = process_unc (data)
        elif fname.find("BRDF_Albedo_Band_Quality") >= 0 or \
                fname.find("BRDF_Albedo_Band_Mandatory_Quality") >= 0:
            qa = np.where(data <= 1, True, False)   # Best & good
            qa_val = data*1

    # Create mask:
    # 1. Ignore snow
    # 2. Only land
    # 3. Only good and best
    mask = snow * qa   # *land * qa
    qa_val = np.where(mask, qa_val, np.nan)
    return kernels, mask, qa_val


def process_unc(unc):
    """Process uncertainty. Fuck know what it means..."""
    unc = np.where(unc == 32767, np.nan, unc/1000.)


def process_snow(snow):
    """Returns True if snow free albedo retrieval"""
    return np.where(snow == 0, True, False)


def process_kernels(kernels):
    """Scales the kernels, maybe does other things"""
    kernels = np.where(kernels == 32767, np.nan, kernels/1000.)
    return kernels


class RetrieveBRDFDescriptors(object):
    """Retrieving BRDF descriptors."""

    def __init__(self, tile, mcd43a1_dir, start_time, end_time=None,
                 mcd43a2_dir=None, roi=None):
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
        if os.path.exists(mcd43a1_dir):
            self.mcd43a1_dir = mcd43a1_dir
        else:
            raise IOError("mcd43a1_dir does not exist!")
        self.a1_granules = find_granules(self.mcd43a1_dir, tile, "A1",
                                         self.start_time, self.end_time)
        if mcd43a2_dir is None:
            self.mcd43a2_dir = mcd43a1_dir
        else:
            if os.path.exists(mcd43a2_dir):
                self.mcd43a2_dir = mcd43a2_dir
            else:
                raise IOError("mcd43a2_dir does not exist!")
        self.a2_granules = find_granules(self.mcd43a2_dir, tile, "A2",
                                         self.start_time, self.end_time)
        a1_dates = set(self.a1_granules.keys())
        a2_dates = set(self.a2_granules.keys())
        if a1_dates != a2_dates:
            raise ValueError("A1 and A2 product files do not overlap!")

        self.band_transfer = None

        if roi is not None:
            assert len(roi) == 4,\
                        f"ROI box needs 4 elements! It has only {len(roi)}!"
            ulx, uly, lrx, lry = roi
            assert(ulx < lrx), f" ulx{ulx} !< lrx{lrx}"
            assert(uly < lry), f" uly{uly} !< lry{lry}"
            self.roi = roi
        else:
            self.roi = None
    def get_brdf_descriptors(self, band_no, date):
        #        if not (1 <= band_no <= 7) :
        #            raise ValueError ("Bands can only go from 1 to 7!")

        the_date = process_time_input(date)
        try:
            a1_granule = self.a1_granules[the_date]
        except KeyError:
            return None
        a2_granule = self.a2_granules[the_date]
        kernels, mask, qa = process_masked_kernels(band_no, a1_granule,
                                                   a2_granule,
                                                   band_transfer=self.band_transfer,
                                                   roi=self.roi)
        return kernels, mask, qa


if __name__ == "__main__":
    mcd43a1_dir = "/group_workspaces/cems2/qa4ecv/vol2/modis.c6.brdf/ladsweb.nascom.nasa.gov/allData/6/MCD43A1/2015/"
    mcd43a2_dir = "/group_workspaces/cems2/qa4ecv/vol2/modis.c6.brdf/ladsweb.nascom.nasa.gov/allData/6/MCD43A2/2015/"
    rr = RetrieveBRDFDescriptors("h17v05",
                                 mcd43a1_dir, 
                                 "2015-01-01", mcd43a2_dir=mcd43a2_dir,
                                 end_time="2015-12-31")
    roi=[1100, 640, 1400,740]
    rr_chunk = RetrieveBRDFDescriptors("h17v05",
                                 mcd43a1_dir,
                                 "2015-01-01", 
                                 mcd43a2_dir=mcd43a2_dir,
                                 end_time="2015-12-31",
                                    roi=roi)
