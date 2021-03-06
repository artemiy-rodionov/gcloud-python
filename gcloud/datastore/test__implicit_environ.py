# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest2


class Test_get_default_connection(unittest2.TestCase):

    def setUp(self):
        from gcloud.datastore._testing import _setup_defaults
        _setup_defaults(self)

    def tearDown(self):
        from gcloud.datastore._testing import _tear_down_defaults
        _tear_down_defaults(self)

    def _callFUT(self):
        from gcloud.datastore._implicit_environ import get_default_connection
        return get_default_connection()

    def test_default(self):
        self.assertEqual(self._callFUT(), None)

    def test_preset(self):
        from gcloud.datastore._testing import _monkey_defaults

        SENTINEL = object()
        with _monkey_defaults(connection=SENTINEL):
            self.assertEqual(self._callFUT(), SENTINEL)


class Test_get_default_dataset_id(unittest2.TestCase):

    def setUp(self):
        from gcloud.datastore._testing import _setup_defaults
        _setup_defaults(self)

    def tearDown(self):
        from gcloud.datastore._testing import _tear_down_defaults
        _tear_down_defaults(self)

    def _callFUT(self):
        from gcloud.datastore._implicit_environ import get_default_dataset_id
        return get_default_dataset_id()

    def test_default(self):
        self.assertEqual(self._callFUT(), None)

    def test_preset(self):
        from gcloud.datastore._testing import _monkey_defaults

        SENTINEL = object()
        with _monkey_defaults(dataset_id=SENTINEL):
            self.assertEqual(self._callFUT(), SENTINEL)


class Test__get_production_dataset_id(unittest2.TestCase):

    def _callFUT(self):
        from gcloud.datastore import _implicit_environ
        return _implicit_environ._get_production_dataset_id()

    def test_no_value(self):
        import os
        from gcloud._testing import _Monkey

        environ = {}
        with _Monkey(os, getenv=environ.get):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)

    def test_value_set(self):
        import os
        from gcloud._testing import _Monkey
        from gcloud.datastore._implicit_environ import _DATASET_ENV_VAR_NAME

        MOCK_DATASET_ID = object()
        environ = {_DATASET_ENV_VAR_NAME: MOCK_DATASET_ID}
        with _Monkey(os, getenv=environ.get):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, MOCK_DATASET_ID)


class Test__get_gcd_dataset_id(unittest2.TestCase):

    def _callFUT(self):
        from gcloud.datastore import _implicit_environ
        return _implicit_environ._get_gcd_dataset_id()

    def test_no_value(self):
        import os
        from gcloud._testing import _Monkey

        environ = {}
        with _Monkey(os, getenv=environ.get):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)

    def test_value_set(self):
        import os
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        MOCK_DATASET_ID = object()
        environ = {
            _implicit_environ._GCD_DATASET_ENV_VAR_NAME: MOCK_DATASET_ID,
        }
        with _Monkey(os, getenv=environ.get):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, MOCK_DATASET_ID)


class Test_app_engine_id(unittest2.TestCase):

    def _callFUT(self):
        from gcloud.datastore import _implicit_environ
        return _implicit_environ.app_engine_id()

    def test_no_value(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        with _Monkey(_implicit_environ, app_identity=None):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)

    def test_value_set(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        APP_ENGINE_ID = object()
        APP_IDENTITY = _AppIdentity(APP_ENGINE_ID)
        with _Monkey(_implicit_environ, app_identity=APP_IDENTITY):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, APP_ENGINE_ID)


class Test_compute_engine_id(unittest2.TestCase):

    def _callFUT(self):
        from gcloud.datastore import _implicit_environ
        return _implicit_environ.compute_engine_id()

    def _monkeyConnection(self, connection):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        def _factory(host, timeout):
            connection.host = host
            connection.timeout = timeout
            return connection

        return _Monkey(_implicit_environ, HTTPConnection=_factory)

    def test_bad_status(self):
        connection = _HTTPConnection(404, None)
        with self._monkeyConnection(connection):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)

    def test_success(self):
        COMPUTE_ENGINE_ID = object()
        connection = _HTTPConnection(200, COMPUTE_ENGINE_ID)
        with self._monkeyConnection(connection):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, COMPUTE_ENGINE_ID)

    def test_socket_raises(self):
        connection = _TimeoutHTTPConnection()
        with self._monkeyConnection(connection):
            dataset_id = self._callFUT()
            self.assertEqual(dataset_id, None)


class Test__determine_default_dataset_id(unittest2.TestCase):

    def _callFUT(self, dataset_id=None):
        from gcloud.datastore import _implicit_environ
        return _implicit_environ._determine_default_dataset_id(
            dataset_id=dataset_id)

    def _determine_default_helper(self, prod=None, gcd=None, gae=None,
                                  gce=None, dataset_id=None):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        _callers = []

        def prod_mock():
            _callers.append('prod_mock')
            return prod

        def gcd_mock():
            _callers.append('gcd_mock')
            return gcd

        def gae_mock():
            _callers.append('gae_mock')
            return gae

        def gce_mock():
            _callers.append('gce_mock')
            return gce

        patched_methods = {
            '_get_production_dataset_id': prod_mock,
            '_get_gcd_dataset_id': gcd_mock,
            'app_engine_id': gae_mock,
            'compute_engine_id': gce_mock,
        }

        with _Monkey(_implicit_environ, **patched_methods):
            returned_dataset_id = self._callFUT(dataset_id)

        return returned_dataset_id, _callers

    def test_no_value(self):
        dataset_id, callers = self._determine_default_helper()
        self.assertEqual(dataset_id, None)
        self.assertEqual(callers,
                         ['prod_mock', 'gcd_mock', 'gae_mock', 'gce_mock'])

    def test_explicit(self):
        DATASET_ID = object()
        dataset_id, callers = self._determine_default_helper(
            dataset_id=DATASET_ID)
        self.assertEqual(dataset_id, DATASET_ID)
        self.assertEqual(callers, [])

    def test_prod(self):
        DATASET_ID = object()
        dataset_id, callers = self._determine_default_helper(prod=DATASET_ID)
        self.assertEqual(dataset_id, DATASET_ID)
        self.assertEqual(callers, ['prod_mock'])

    def test_gcd(self):
        DATASET_ID = object()
        dataset_id, callers = self._determine_default_helper(gcd=DATASET_ID)
        self.assertEqual(dataset_id, DATASET_ID)
        self.assertEqual(callers, ['prod_mock', 'gcd_mock'])

    def test_gae(self):
        DATASET_ID = object()
        dataset_id, callers = self._determine_default_helper(gae=DATASET_ID)
        self.assertEqual(dataset_id, DATASET_ID)
        self.assertEqual(callers, ['prod_mock', 'gcd_mock', 'gae_mock'])

    def test_gce(self):
        DATASET_ID = object()
        dataset_id, callers = self._determine_default_helper(gce=DATASET_ID)
        self.assertEqual(dataset_id, DATASET_ID)
        self.assertEqual(callers,
                         ['prod_mock', 'gcd_mock', 'gae_mock', 'gce_mock'])


class Test_set_default_dataset_id(unittest2.TestCase):

    def setUp(self):
        from gcloud.datastore._testing import _setup_defaults
        _setup_defaults(self)

    def tearDown(self):
        from gcloud.datastore._testing import _tear_down_defaults
        _tear_down_defaults(self)

    def _callFUT(self, dataset_id=None):
        from gcloud.datastore._implicit_environ import set_default_dataset_id
        return set_default_dataset_id(dataset_id=dataset_id)

    def test_raises(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        _called_dataset_id = []

        def mock_determine(dataset_id):
            _called_dataset_id.append(dataset_id)
            return None

        with _Monkey(_implicit_environ,
                     _determine_default_dataset_id=mock_determine):
            self.assertRaises(EnvironmentError, self._callFUT)

        self.assertEqual(_called_dataset_id, [None])

    def test_set_correctly(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        self.assertEqual(_implicit_environ._DEFAULTS.dataset_id, None)

        DATASET_ID = object()
        _called_dataset_id = []

        def mock_determine(dataset_id):
            _called_dataset_id.append(dataset_id)
            return DATASET_ID

        with _Monkey(_implicit_environ,
                     _determine_default_dataset_id=mock_determine):
            self._callFUT()

        self.assertEqual(_implicit_environ._DEFAULTS.dataset_id, DATASET_ID)
        self.assertEqual(_called_dataset_id, [None])


class Test__lazy_property_deco(unittest2.TestCase):

    def _callFUT(self, deferred_callable):
        from gcloud.datastore._implicit_environ import _lazy_property_deco
        return _lazy_property_deco(deferred_callable)

    def test_on_function(self):
        def test_func():
            pass  # pragma: NO COVER never gets called

        lazy_prop = self._callFUT(test_func)
        self.assertTrue(lazy_prop._deferred_callable is test_func)
        self.assertEqual(lazy_prop._name, 'test_func')

    def test_on_staticmethod(self):
        def test_func():
            pass  # pragma: NO COVER never gets called

        lazy_prop = self._callFUT(staticmethod(test_func))
        self.assertTrue(lazy_prop._deferred_callable is test_func)
        self.assertEqual(lazy_prop._name, 'test_func')


class Test_lazy_loading(unittest2.TestCase):

    def setUp(self):
        from gcloud.datastore._testing import _setup_defaults
        _setup_defaults(self, implicit=True)

    def tearDown(self):
        from gcloud.datastore._testing import _tear_down_defaults
        _tear_down_defaults(self)

    def test_prop_on_wrong_class(self):
        from gcloud.datastore._implicit_environ import _LazyProperty

        # Don't actually need a callable for ``method`` since
        # __get__ will just return ``self`` in this test.
        data_prop = _LazyProperty('dataset_id', None)

        class FakeEnv(object):
            dataset_id = data_prop

        self.assertTrue(FakeEnv.dataset_id is data_prop)
        self.assertTrue(FakeEnv().dataset_id is data_prop)

    def test_descriptor_for_dataset_id(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        self.assertFalse(
            'dataset_id' in _implicit_environ._DEFAULTS.__dict__)

        DEFAULT = object()

        with _Monkey(_implicit_environ,
                     _determine_default_dataset_id=lambda: DEFAULT):
            lazy_loaded = _implicit_environ._DEFAULTS.dataset_id

        self.assertEqual(lazy_loaded, DEFAULT)
        self.assertTrue(
            'dataset_id' in _implicit_environ._DEFAULTS.__dict__)

    def test_descriptor_for_connection(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        self.assertFalse(
            'connection' in _implicit_environ._DEFAULTS.__dict__)

        DEFAULT = object()

        with _Monkey(_implicit_environ, get_connection=lambda: DEFAULT):
            lazy_loaded = _implicit_environ._DEFAULTS.connection

        self.assertEqual(lazy_loaded, DEFAULT)
        self.assertTrue(
            'connection' in _implicit_environ._DEFAULTS.__dict__)


class Test_get_connection(unittest2.TestCase):

    def _callFUT(self):
        from gcloud.datastore._implicit_environ import get_connection
        return get_connection()

    def test_it(self):
        from gcloud import credentials
        from gcloud.datastore.connection import Connection
        from gcloud.test_credentials import _Client
        from gcloud._testing import _Monkey

        client = _Client()
        with _Monkey(credentials, client=client):
            found = self._callFUT()
        self.assertTrue(isinstance(found, Connection))
        self.assertTrue(found._credentials is client._signed)
        self.assertTrue(client._get_app_default_called)


class Test_set_default_connection(unittest2.TestCase):

    def setUp(self):
        from gcloud.datastore._testing import _setup_defaults
        _setup_defaults(self)

    def tearDown(self):
        from gcloud.datastore._testing import _tear_down_defaults
        _tear_down_defaults(self)

    def _callFUT(self, connection=None):
        from gcloud.datastore._implicit_environ import set_default_connection
        return set_default_connection(connection=connection)

    def test_set_explicit(self):
        from gcloud.datastore import _implicit_environ

        self.assertEqual(_implicit_environ.get_default_connection(), None)
        fake_cnxn = object()
        self._callFUT(connection=fake_cnxn)
        self.assertEqual(_implicit_environ.get_default_connection(), fake_cnxn)

    def test_set_implicit(self):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ

        self.assertEqual(_implicit_environ.get_default_connection(), None)

        fake_cnxn = object()
        with _Monkey(_implicit_environ, get_connection=lambda: fake_cnxn):
            self._callFUT()

        self.assertEqual(_implicit_environ.get_default_connection(), fake_cnxn)


class _AppIdentity(object):

    def __init__(self, app_id):
        self.app_id = app_id

    def get_application_id(self):
        return self.app_id


class _HTTPResponse(object):

    def __init__(self, status, data):
        self.status = status
        self.data = data

    def read(self):
        return self.data


class _BaseHTTPConnection(object):

    host = timeout = None

    def __init__(self):
        self._close_count = 0
        self._called_args = []
        self._called_kwargs = []

    def request(self, method, uri, **kwargs):
        self._called_args.append((method, uri))
        self._called_kwargs.append(kwargs)

    def close(self):
        self._close_count += 1


class _HTTPConnection(_BaseHTTPConnection):

    def __init__(self, status, project_id):
        super(_HTTPConnection, self).__init__()
        self.status = status
        self.project_id = project_id

    def getresponse(self):
        return _HTTPResponse(self.status, self.project_id)


class _TimeoutHTTPConnection(_BaseHTTPConnection):

    def getresponse(self):
        import socket
        raise socket.timeout('timed out')
