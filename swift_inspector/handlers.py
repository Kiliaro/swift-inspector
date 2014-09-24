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


def wrapper(env, start_response, app, config):
    def _start_response(status, headers, exc_info=None):
        """start_response wrapper to add request status to env."""
        headers.append(('Inspector-Handlers-Proxy',
                        env.get('SERVER_NAME', 'Unknown')))
        # TODO(hurricanerix): Currently researching how to obtain what
        # account/container/object server(s) the request was sent to.
        headers.append(('Inspector-Handlers', 'Unknown'))
        return start_response(status, headers, exc_info)

    return _start_response