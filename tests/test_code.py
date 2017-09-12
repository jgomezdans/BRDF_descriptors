#!/usr/bin/env python
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
print (sys.path)
import datetime
import numpy as np

import pytest
from distutils import dir_util

from BRDF_descriptors.BRDF_descriptors import process_time_input
from BRDF_descriptors.BRDF_descriptors import find_granules
from BRDF_descriptors.BRDF_descriptors import RetrieveBRDFDescriptors


def test_time_string1():
    test_string = "2015-03-21"
    retval = process_time_input ( test_string )
    target = datetime.datetime(2015,3,21)
    assert retval == target

def test_time_string2():
    test_string = "2015080"
    retval = process_time_input ( test_string )
    target = datetime.datetime(2015,3,21)
    assert retval == target

def test_time_string3():
    test_string = datetime.datetime(2015,3,21)
    retval = process_time_input ( test_string )
    target = datetime.datetime(2015,3,21)
    assert retval == target

def test_time_string3():
    with pytest.raises(ValueError):
        test_string = 25
        retval = process_time_input ( test_string )
    
def test_time_stringfail():
    with pytest.raises(ValueError):
        test_string = "If I should fall from grace with god"
        retval = process_time_input ( test_string )
        
def test_findgranules1(monkeypatch):
    #find_granules(dire, tile, product, start_time, end_time):
    files=['/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016001.h20v11.006.2016174080052.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016002.h20v11.006.2016174082609.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016003.h20v11.006.2016174085337.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016004.h20v11.006.2016174091417.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016005.h20v11.006.2016174094032.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016006.h20v11.006.2016174100944.hdf']

    monkeypatch.setattr("BRDF_descriptors.BRDF_descriptors.locate", lambda x, y:files)
    granules = find_granules("/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/", 
                             "h20v11", "A2", datetime.datetime(2016,1,1),
                             None)
    assert set(granules.values()) == set(files)

def test_findgranules2(monkeypatch):
    #find_granules(dire, tile, product, start_time, end_time):
    files=[]
    with pytest.raises(IOError):
        monkeypatch.setattr("BRDF_descriptors.BRDF_descriptors.locate", lambda x, y:files)
        granules = find_granules("/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/", 
                                "h20v11", "A2", datetime.datetime(2016,1,1),
                                None)

def test_findgranules3(monkeypatch):
    #find_granules(dire, tile, product, start_time, end_time):
    files=['/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016001.h20v11.006.2016174080052.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016002.h20v11.006.2016174082609.hdf',
           '/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/MCD43A2.A2016003.h20v11.006.2016174085337.hdf']
    monkeypatch.setattr("BRDF_descriptors.BRDF_descriptors.locate", lambda x, y:files)
    granules = find_granules("/data/selene/ucfajlg/S2_AC/MCD43/Pretoria/", 
                                "h20v11", "A2", datetime.datetime(2016,1,1),
                                datetime.datetime(2016,1,3))
    assert set(granules.values()) == set(files)
    
