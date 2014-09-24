![Swift-Inspector Logo](https://raw.githubusercontent.com/hurricanerix/swift-inspector/master/resources/swift-inspector.png)

Swift Inspector
===============

Swift middleware to relay information about a request back to the client.

Current Inspectors
------------------

* Timing - Adds the "Inspector-Timing" header to the request indicating the
  amount of time it took the proxy server to process the request.

```Shell
$ curl -i -H'Inspector: Timing' -XGET -H'x-auth-token: AUTH_tkd03626426c8647aeba7eb150330e8be6' http://127.0.0.1:8080/v1/AUTH_test/example_container
HTTP/1.1 200 OK
...
Inspector-Timing: 0.0140538215637

example_object
```

* Nodes - Adds the "Inspector-Nodes" and "Inspector-More-Nodes" headers to the
  request.  "Inspector-Nodes" indicates what account/container/object servers
  the path resides on.  "Inspector-More-Nodes" indicates extra nodes for a
  partition for hinted handoff.

```Shell
$ curl -i -H'Inspector: Nodes' -XGET -H'x-auth-token: AUTH_tkd03626426c8647aeba7eb150330e8be6' http://127.0.0.1:8080/v1/AUTH_test/example_container
HTTP/1.1 200 OK
...
Inspector-Nodes: http://127.0.0.1:6042/sdb4/802, http://127.0.0.1:6032/sdb3/802, http://127.0.0.1:6022/sdb2/802
Inspector-More-Nodes: http://127.0.0.1:6012/sdb1/802

example_object
```

Configuration
-------------

* Add inspector to your pipeline, preferably immediatly after catch_errors.

```INI
pipeline = catch_errors inspector ...
```

* Add the inspector filter.

```INI
[filter:inspector]
use = egg:swift_inspector#swift_inspector
# hmac_key - Key to restrict access to the inspector feature.  if set, will
#            require the additional headers 'Inspector-Expires'
#            and 'Inspector-Sig'. Inspector-Expires represents a unix timestamp
#            indicating when access to the feature should be cut off.
#            Inspector-Sig is the signature used to sign the inspectors to
#            allow access to.
hmac_key = Password1
#
# exclude - List of inspector names separated by spaces to exclude.  This 
#           will cause a invalid inspector error if a request attempts to
#           request it.
exclude = Nodes
```

* Restart your proxy servers.
