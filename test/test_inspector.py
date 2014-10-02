# Copyright 2014 Richard Hawkins
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import hmac
import time
import unittest

from swift_inspector.middleware import proxy


VALID_INSPECTORS = 'Timing'

ERROR_MSG_MISSING_SIG = 'Missing Header: Inspector-Sig'
ERROR_MSG_MISSING_EXPIRES = 'Missing Header: Inspector-Expires'
ERROR_MSG_EXPIRED = 'Invalid Header: Inspector-Expires has expired'
ERROR_MSG_INVALID_SIG = 'Invalid Signature'
ERROR_MSG_INVALID_EXPIRES = (
    'Invalid Header: Inspector-Expires must be an integer')
ERROR_MSG_INVALID_INSPECTOR = 'Invalid Inspectors: {0}'

status = None
headers = None
exc_info = None


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def start_response(s, h, e=None):
    global status, headers, exc_info
    status[0] = s
    headers[0] = h
    exc_info[0] = e


def get_response():
    global status, headers, exc_info
    return (status[0], headers[0], exc_info[0])


def reset_response():
    global status, headers, exc_info
    status = [None]
    headers = [None]
    exc_info = [None]


def get_fake_app(config=None):
    if config is None:
        config = {'hmac_key': ''}

    headers = [('Content-type', 'text/plain')]

    def fake_app(environ, start_response):
        start_response('200 OK', headers)
        return ['']

    return proxy.InspectorMiddleware(fake_app, config)


def _make_env(inspector=None, expires=None, sig=None):
    env = {}

    if inspector is not None:
        env['HTTP_INSPECTOR'] = inspector
    if expires is not None:
        env['HTTP_INSPECTOR_EXPIRES'] = str(expires)
    if sig is not None:
        env['HTTP_INSPECTOR_SIG'] = sig

    return env


class TestInspector(unittest.TestCase):

    def setUp(self):
        reset_response()

    def test_no_headers_added_wihtout_inspector(self):
        app = get_fake_app()
        env = _make_env()

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        for h, v in headers:
            h = h.lower()
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_timing_headers_added_with_inspector(self):
        app = get_fake_app()
        env = _make_env(inspector='Timing')

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        timing_inspector = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-timing':
                timing_inspector = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(timing_inspector is not None)
        self.assertTrue(is_float(timing_inspector))
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_timing_headers_added_with_inspector_auth(self):
        hmac_key = 'Password1'
        app = get_fake_app(config={'hmac_key': hmac_key})
        inspector = 'Timing'
        expires = int(time.time() + 86400)
        sig = hmac.new(hmac_key, '{0}\n{1}'.format(inspector.lower(), expires),
                       hashlib.sha1).hexdigest()
        env = _make_env(inspector=inspector, expires=expires, sig=sig)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        timing_inspector = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-timing':
                timing_inspector = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(timing_inspector is not None)
        self.assertTrue(is_float(timing_inspector))
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_error_headers_added_with_missing_sig(self):
        hmac_key = 'Password1'
        app = get_fake_app(config={'hmac_key': hmac_key})
        inspector = 'Timing'
        expires = int(time.time() + 86400)
        env = _make_env(inspector=inspector, expires=expires)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        inspector_error = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-error':
                inspector_error = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(inspector_error == ERROR_MSG_MISSING_SIG)
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_error_headers_added_with_missing_expires(self):
        hmac_key = 'Password1'
        app = get_fake_app(config={'hmac_key': hmac_key})
        inspector = 'Timing'
        expires = int(time.time() + 86400)
        sig = hmac.new(hmac_key, '%s\n%s'.format(inspector.lower(), expires),
                       hashlib.sha1).hexdigest()
        env = _make_env(inspector=inspector, sig=sig)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        inspector_error = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-error':
                inspector_error = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(inspector_error == ERROR_MSG_MISSING_EXPIRES)
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_error_headers_added_with_expired_value(self):
        hmac_key = 'Password1'
        app = get_fake_app(config={'hmac_key': hmac_key})
        inspector = 'Timing'
        expires = int(time.time() - 900)
        sig = hmac.new(hmac_key, '%s\n%s'.format(inspector.lower(), expires),
                       hashlib.sha1).hexdigest()
        env = _make_env(inspector=inspector, expires=expires, sig=sig)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        inspector_error = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-error':
                inspector_error = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(inspector_error == ERROR_MSG_EXPIRED)
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_error_headers_added_with_invalid_sig(self):
        hmac_key = 'Password1'
        app = get_fake_app(config={'hmac_key': hmac_key})
        invalid_key = 'INVALID'
        inspector = 'Timing'
        expires = int(time.time() + 86400)
        sig = hmac.new(invalid_key, '%s\n%s'.format(inspector.lower(),
                       expires), hashlib.sha1).hexdigest()
        env = _make_env(inspector=inspector, expires=expires, sig=sig)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        inspector_error = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-error':
                inspector_error = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(inspector_error == ERROR_MSG_INVALID_SIG)
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_error_headers_added_with_invalid_expires(self):
        hmac_key = 'Password1'
        app = get_fake_app(config={'hmac_key': hmac_key})
        inspector = 'Timing'
        expires = 'abc'
        sig = hmac.new(hmac_key, '%s\n%s'.format(inspector.lower(), expires),
                       hashlib.sha1).hexdigest()
        env = _make_env(inspector=inspector, expires=expires, sig=sig)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        inspector_error = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-error':
                inspector_error = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(inspector_error == ERROR_MSG_INVALID_EXPIRES)
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

    def test_error_headers_added_with_invalid_inspector(self):
        app = get_fake_app()
        inspector = 'Foo Timing Bar'
        env = _make_env(inspector=inspector)

        body = ''.join(app(env, start_response))
        (status, headers, exc_info) = get_response()

        inspector_error = None
        for h, v in headers:
            h = h.lower()
            if h == 'inspector-error':
                inspector_error = v
                break
            self.assertFalse(h.startswith('inspector'),
                             'True is not false ("{0}", "{1}")'.format(h, v))

        self.assertTrue(inspector_error ==
                        ERROR_MSG_INVALID_INSPECTOR.format('Foo, Bar'))
        self.assertEqual(status, '200 OK')
        self.assertEqual(exc_info, None)
        self.assertTrue(body == '')

if __name__ == '__main__':
    unittest.main()
