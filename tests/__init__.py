# coding: utf-8

# Python
from __future__ import unicode_literals, print_function
import os
import re
from codecs import open
from contextlib import contextmanager

# Third-party
import requests
import pytest

# Project
from fnapy.fnapy_manager import FnapyManager
from fnapy.connection import FnapyConnection
from fnapy.config import URL, HEADERS
from fnapy.utils import *


# DATA
offer_data1 = {'product_reference':'0711719247159',
        'offer_reference':'B76A-CD5-153',
        'price':15, 'product_state':11, 'quantity':10, 
        'description': 'New product - 2-3 days shipping, from France'}

offer_data2 = {'product_reference':'5030917077418',
        'offer_reference':'B067-F0D-75E',
        'price':20, 'product_state':11, 'quantity':16, 
        'description': 'New product - 2-3 days shipping, from France'}

offer_data3 = {'product_reference': '5051889022091',
               'offer_reference': '561C-385-9BE',
               'price': 10.55, 'product_state': 11, 'quantity': 16,
               'description': 'New product - Blu-ray disc - 2-3 days shipping, from France'}

# # SICP
# offer_data3 = {'product_reference':'9780262510875',
#         'offer_reference':'B76A-CD5-444',
#         'price':80, 'product_state':11, 'quantity':10, 
#         'description': 'New product - 2-3 days shipping, from France'}

# # Batman V Superman L'aube de la justice 
# offer_data4 = {'product_reference':'5051889562672',
#         'offer_reference':'B067-F0D-444',
#         'price':20, 'product_state':11, 'quantity':16, 
#         'description': 'New product - 2-3 days shipping, from France'}

offers_data = [offer_data1, offer_data2, offer_data3]


# FUNCTIONS
# TODO Use mock instead of sending request to the server
@pytest.fixture
def setup():
    partner_id = os.environ.get('FNAC_PARTNER_ID')
    shop_id    = os.environ.get('FNAC_SHOP_ID')
    key        = os.environ.get('FNAC_KEY')
    from fnapy.connection import FnapyConnection
    connection = FnapyConnection(partner_id, shop_id, key)
    manager = FnapyManager(connection)
    manager.authenticate()
    # We make sure we always have the offers with the right values
    offers_update_response = manager.update_offers(offers_data)
    return {'manager': manager, 'response': offers_update_response}


@pytest.fixture
def fake_manager(monkeypatch):
    monkeypatch.setattr('requests.post', make_requests_get_mock('auth_response.xml'))
    partner_id = os.environ.get('FNAC_PARTNER_ID')
    shop_id    = os.environ.get('FNAC_SHOP_ID')
    key        = os.environ.get('FNAC_KEY')
    connection = FnapyConnection(partner_id, shop_id, key)
    manager = FnapyManager(connection)
    manager.authenticate()
    return manager


def make_requests_get_mock(filename):
    def mockreturn(*args, **kwargs):
        response = requests.Response()
        with open(os.path.join(os.path.dirname(__file__), 'assets', filename), 'r', 'utf-8') as fd:
            response._content = fd.read().encode('utf-8')
        return response
    return mockreturn


def make_simple_text_mock(filename):
    def mockreturn(*args, **kwargs):
        with open(os.path.join(os.path.dirname(__file__), 'assets', filename), 'r', 'utf-8') as fd:
            return fd.read()
    return mockreturn


@contextmanager
def assert_raises(exception_class, msg=None):
    """Check that an exception is raised and its message contains `msg`."""
    with pytest.raises(exception_class) as exception:
        yield
    if msg is not None:
        message = '%s' % exception
        assert msg.lower() in message.lower()


def xml_is_valid(xml_dict, xml_valid_keys):
    """Return True if all the keys in the XML dictionary are valid"""
    if len(xml_dict) == 0:
        return False, 'The XML dictionary is empty.'
    keys = [tag for tag in xml_dict.keys() if not tag.startswith('@')]
    if len(keys) == 0:
        return False, 'The XML dictionary contains no valid keys.'
    invalid_keys = set(keys).difference(xml_valid_keys)
    # pytest.fail(xml_valid_keys)
    result = len(invalid_keys) == 0
    if result:
        return True, ''
    else:
        msg = 'The XML has the following invalid keys {}'.format(invalid_keys)
        if len(invalid_keys) == 1 and 'error' in invalid_keys:
            print(xml_dict['error'])
        return False, msg


def response_is_valid(action, service):
    """The response is valid if it contains the elements defined in the API"""
    request = load_xml_request(action) 
    request = set_credentials(request)
    response = post(service, request).text
    xml_dict = xml2dict(response).get(service + '_response', {})
    result, error = xml_is_valid(xml_dict, RESPONSE_ELEMENTS[service])
    if result:
        save_xml_response(response, action)
    elif result is False:
        pytest.fail(error)
    return result


def request_is_valid(request, action, service):
    """The request is valid if it contains the same information as in the valid XML request file"""
    expected = load_xml_request(action)
    expected_dict = xml2dict(expected).get(service, {})
    request_dict = request.dict[service]
    credentials = ('@partner_id', '@shop_id', '@token')
    result = all(request_dict.get(k, None) == v for k, v in expected_dict.items() if k not in credentials)

    if not result:
        pytest.fail('Invalid request:\n{0}\nshould be:\n{1}'.format(request, expected))
    else:
        return result
        
