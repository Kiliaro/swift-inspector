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
import urllib

import swift.common.ring as ring
import swift.common.storage_policy as storage_policy
import swift.common.swob as swob
import swift.proxy.controllers.base as controllers


def proxy_wrapper(env, start_response, app, config):
    swift_dir = config.get('swift_dir')
    request = swob.Request(env)

    def _start_response(status, headers, exc_info=None):
        """start_response wrapper to add request status to env."""
        try:
            version, account, container, obj = request.split_path(
                2, 4, rest_with_last=True)
        except ValueError:
            headers.append(('Inspector-Nodes', ''))
            return start_response(status, headers, exc_info)

        if account is not None:
            account = urllib.unquote(account)
        if container is not None:
            container = urllib.unquote(container)
        if obj is not None:
            obj = urllib.unquote(obj)

        storage_policy_index = None
        if obj is not None:
            container_info = controllers.get_container_info(
                {'PATH_INFO': '/{0}/{1}/{2}'.format(
                    version, account, container)},
                app, swift_source='LE')
            storage_policy_index = container_info['storage_policy']
            obj_ring = storage_policy.POLICIES.get_object_ring(
                storage_policy_index, swift_dir)
            partition, nodes = obj_ring.get_nodes(
                account, container, obj)
            more_nodes = obj_ring.get_more_nodes(partition)
            nodes_template = ('http://{ip}:{port}/{device}/{partition}')
        elif container is not None:
            partition, nodes = ring.Ring(
                swift_dir, ring_name='container').get_nodes(account, container)
            more_nodes = ring.Ring(
                swift_dir, ring_name='container').get_more_nodes(partition)
            nodes_template = ('http://{ip}:{port}/{device}/{partition}')
        else:
            partition, nodes = ring.Ring(
                swift_dir, ring_name='account').get_nodes(account)
            more_nodes = ring.Ring(
                swift_dir, ring_name='account').get_more_nodes(partition)
            nodes_template = ('http://{ip}:{port}/{device}/{partition}')

        object_nodes = []
        for node in nodes:
            object_nodes.append(nodes_template.format(
                ip=node['ip'],
                port=node['port'],
                device=node['device'],
                partition=partition,
                account=urllib.quote(account),
                container=urllib.quote(container or ''),
                obj=urllib.quote(obj or '')))
        headers.append(('Inspector-Nodes', ', '.join(object_nodes)))

        object_more_nodes = []
        for node in more_nodes:
            object_more_nodes.append(nodes_template.format(
                ip=node['ip'],
                port=node['port'],
                device=node['device'],
                partition=partition,
                account=urllib.quote(account),
                container=urllib.quote(container or ''),
                obj=urllib.quote(obj or '')))
        headers.append(('Inspector-More-Nodes', ', '.join(
            object_more_nodes)))

        return start_response(status, headers, exc_info)

    return _start_response
