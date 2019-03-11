from datetime import datetime, timedelta
import pytest


from Invoicecreator.items import Activity


type = 'development'
description = 'fixing errors'
rate = 55

starttime = '10:15'
endtime = '15:15'

# provide activities for testing
@pytest.fixture
def act1():
    """activity with corresponding times and quantity"""
    act = Activity(type, description, rate, datetime.strptime(starttime, '%H:%M'), datetime.strptime(endtime, '%H:%M'), 5)

    return act

@pytest.fixture
def act2():
    """activitiy with different times and quantity"""
    act2 = Activity(type, description, rate, datetime.strptime(starttime, '%H:%M'), datetime.strptime(endtime, '%H:%M'),
                    10)

    return act2

@pytest.fixture
def act3():
    act3 = Activity(type, description, rate, datetime.strptime(starttime, '%H:%M'), datetime.strptime(endtime, '%H:%M'))

    return act3

#### Tests

def test_qty_calculation(act1):
    """check if duration of activity is calculated correctly"""
    assert act1.calculate_qty() == act1.qty

def test_compare_qty(act1, act2):
    """check if calculated and given quantity are the same"""
    res = []
    res.append(act1.compare_qty())
    res.append(act2.compare_qty())
    assert res == [True, False]

def test_calculate_sum(act1):
    """check if sum is calculated correctly"""

    assert act1.compute_sum() == 275







