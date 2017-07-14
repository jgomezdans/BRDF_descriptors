#!/usr/bin/env python

import datetime
import numpy as np

import pytest
from distutils import dir_util

from brdf_descriptors.BRDF_descriptors import process_time_input


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
        
        



