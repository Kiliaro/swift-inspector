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


def _get_handler(env):
    protocol = env.get('SERVER_PROTOCOL').lower().split('/')[0]
    server_name = env.get('SERVER_NAME', None)
    port = env.get('SERVER_PORT', None)
    path = env.get('PATH_INFO', '')
    handler = '{0}://{1}:{2}{3}'.format(protocol, server_name, port, path)
    return handler


def proxy_wrapper(env, start_response, app, config):
    def _start_response(status, headers, exc_info=None):
        """start_response wrapper to add request status to env."""
        headers.append(('Inspector-Handlers-Proxy', _get_handler(env)))
        return start_response(status, headers, exc_info)
    return _start_response


def object_wrapper(env, start_response, app, config):
    def _start_response(status, headers, exc_info=None):
        """start_response wrapper to add request status to env."""
        headers.append(('Inspector-Handlers-Object', _get_handler(env)))
        return start_response(status, headers, exc_info)
    return _start_response
