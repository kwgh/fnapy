#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016  <>
#
# Distributed under terms of the MIT license.

# Python modules
from __future__ import unicode_literals
from contextlib import closing

# Project modules
from fnapy.utils import Message
from tests import make_requests_get_mock, fake_manager
from tests.offline import ContextualTest


def test_query_messages(monkeypatch, fake_manager):
    context = ContextualTest(monkeypatch, fake_manager, 'query_messages', 'messages_query')
    with closing(context):
        fake_manager.query_messages(paging=1)


def test_update_messages(monkeypatch, fake_manager):
    context = ContextualTest(monkeypatch, fake_manager, 'update_messages', 'messages_update')
    with closing(context):
        message1 = Message(action='mark_as_read', id=u'6F9EF013-6387-F433-C3F5-4AAEF32AA317')
        message1.subject = 'order_information'
        fake_manager.update_messages([message1])


