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

import handlers
import nodes
import timing

inspector_handlers = {
    'handlers': handlers.wrapper,
    'nodes': nodes.wrapper,
    'timing': timing.wrapper
}
