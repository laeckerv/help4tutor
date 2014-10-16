#!/usr/bin/env py.test
"""
Test Modul for groupsetup module
"""

__author__ = 'mahieke'

import pytest
import help4tutor.groupsetup as gs


setup = gs.GroupSetup('.config', './')

def test_load_group_file():
