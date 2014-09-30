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

# import swift_inspector.handlers
# import swift_inspector.nodes
# import swift_inspector.timing

# inspector_handlers = {
#     'handlers': swift_inspector.handlers.wrapper,
#     'nodes': swift_inspector.nodes.wrapper,
#     'timing': swift_inspector.timing.wrapper
# }


def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


inspector_proxy_handlers = {}
inspector_account_handlers = {}
inspector_container_handlers = {}
inspector_object_handlers = {}


for server_type in ['proxy', 'account', 'container', 'object']:
    for inspector_name in ['handlers', 'nodes', 'timing']:
        mod = import_from('swift_inspector.inspectors', inspector_name)
        try:
            inspector_proxy_handlers[inspector_name] = getattr(
                mod, '{0}_wrapper'.format(server_type))
        except AttributeError:
            continue

print inspector_proxy_handlers  