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
import swift.common.swob as swob
import swift.common.utils as utils
import time


def create_sig(inspector, expires, key):
    inspector = ' '.join(inspector).lower()
    expires = float(expires)
    hmac_body = '%s\n%s'.format(inspector, expires)
    sig = hmac.new(key, hmac_body, hashlib.sha1).hexdigest()
    return sig


class InspectorError(Exception):
    pass


class InspectorMiddleware(object):
    """Swift Inspector Middleware use for inspecting Swift requests."""
    def __init__(self, app, conf, *args, **kwargs):
        self.app = app
        self.logger = utils.get_logger(conf, log_route='informant')
        self.hmac_key = conf.get('hmac_key')

    def handle_error(self, msg, env, start_response):
        def _start_response(status, headers, exc_info=None):
            """start_response wrapper to add request status to env."""
            headers.append(('Inspector-Error', msg))
            start_response(status, headers, exc_info)
        return self.app(env, _start_response)

    def handle_request(self, env, start_response):
        req = swob.Request(env)

        inspector = req.headers.get('inspector', '').lower().split()
        if self.hmac_key:
            expires = req.headers.get('inspector_expires', '')
            sig = req.headers.get('inspector_sig', '')
            try:
                if sig == '':
                    raise InspectorError('Missing Header: Inspector-Sig')
                if expires == '':
                    raise InspectorError('Missing Header: Inspector-Expires')
                if float(expires) < time.time():
                    raise InspectorError(
                        'Invalid Header: Inspector-Expires has expired')
                valid_sig = create_sig(inspector, expires, self.hmac_key)
                if sig != valid_sig:
                    raise InspectorError('Invalid Signature')
            except InspectorError as e:
                return self.handle_error(str(e), env, start_response)
            except ValueError:
                return self.handle_error(
                    'Invalid Header: Inspector-Expires must be an integer',
                    env, start_response)

        start = time.time()

        def _start_response(status, headers, exc_info=None):
            """start_response wrapper to add request status to env."""
            end = time.time()
            headers.append(('Inspector-Timing', str(end - start)))
            start_response(status, headers, exc_info)

        return self.app(env, _start_response)

    def __call__(self, env, start_response):
        if 'HTTP_INSPECTOR' in env:
            return self.handle_request(env, start_response)
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)
    utils.register_swift_info('inspector')

    def informant_filter(app):
        return InspectorMiddleware(app, conf)
    return informant_filter
