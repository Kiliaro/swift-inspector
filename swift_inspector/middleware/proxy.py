# Copyright 2014-2015 Richard Hawkins
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

import swift.common.swob as swob
import swift.common.utils as utils

from swift_inspector.inspectors import inspector_handlers


def create_sig(inspector, expires, key):
    inspector = ' '.join(inspector).lower()
    expires = int(expires)
    hmac_body = '{0}\n{1}'.format(inspector, expires)
    sig = hmac.new(key, hmac_body, hashlib.sha1).hexdigest()
    return sig


class InspectorError(Exception):
    pass


class InspectorMiddleware(object):
    """Swift Inspector Middleware use for inspecting Swift requests."""
    def __init__(self, app, conf, default=None):
        self.app = app
        self.logger = utils.get_logger(conf, log_route='inspector')
        self.hmac_key = conf.get('hmac_key')
        self.swift_dir = conf.get('here', '/etc/swift')
        self.default = default

    def handle_error(self, msg, env, start_response):
        def _start_response(status, headers, exc_info=None):
            """start_response wrapper to add request status to env."""
            headers.append(('Inspector-Error', msg))
            start_response(status, headers, exc_info)
        return self.app(env, _start_response)

    def handle_request(self, env, start_response):
        req = swob.Request(env)

        inspector = req.headers.get('inspector', '').lower().split()
        if self.default:
            inspector = self.default + inspector
        
        if self.hmac_key:
            expires = req.headers.get('inspector_expires', '')
            sig = req.headers.get('inspector_sig', '')
            try:
                if sig == '':
                    raise InspectorError('Missing Header: Inspector-Sig')
                if expires == '':
                    raise InspectorError('Missing Header: Inspector-Expires')
                if int(expires) < int(time.time()):
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

        _start_response = start_response
        inspector_errors = []

        def inspector_start_response(status, headers, exc_info=None):
            if inspector_errors:
                errors = ', '.join(inspector_errors).title()
                headers.append(('Inspector-Error',
                                'Invalid Inspectors: {0}'.format(errors)))
            return _start_response(status, headers, exc_info)

        for i in inspector:
            i = i.lower()
            if i not in inspector_handlers['proxy']:
                inspector_errors.append(i)
                continue
            _start_response = inspector_handlers['proxy'][i](
                env, _start_response, self.app, {'swift_dir': self.swift_dir})
        return self.app(env, inspector_start_response)

    def __call__(self, env, start_response):
        if self.default or 'HTTP_INSPECTOR' in env:
            return self.handle_request(env, start_response)
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)
    exclude_inspectors = local_conf.get('exclude', '').lower().split()
    for inspector in exclude_inspectors:
        if inspector in inspector_handlers['proxy']:
            del inspector_handlers['proxy'][inspector]
    avaiable_inspectors = [i.title() for i in inspector_handlers['proxy']]
    default_inspectors = local_conf.get('default', '').title().split()
    utils.register_swift_info('inspector', inspectors=avaiable_inspectors, default=default_inspectors)

    def inspector_filter(app):
        return InspectorMiddleware(app, conf, default=default_inspectors)
    return inspector_filter
