.. BRDF Descriptors documentation master file, created by
   sphinx-quickstart on Fri Jul 14 18:44:46 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BRDF Descriptors's documentation!
============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   
General Design Idea
====================

The BRDF descriptors module is supposed to access BRDF descriptors from products. In particular, this means that it will retrieve sets of linear kernel model parameters (isotropic, volumetric and geometric kernel weights) for a particular region (defined as a MODIS tile) and time stamp. Currently, the BRDF descriptors are based on the MODIS MCD43 product, which is assumed available in the system that is running things. The module will do the following things:

1. Find the relevant MCD43 files for the period and region of interest. The period of interest is specified as dates, and the region is specified as a MODIS tile (e.g. "h19v10").
2. Check that all data is OK and so on (i.e. no missing MCD43A1 and MCD43A2 files).
3. Allow the user to retrieve the kernels, a valid pixels mask and a measure of uncertainty for a particular date and spectral band.





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
