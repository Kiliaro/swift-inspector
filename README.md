Swift Inspector
===============

Swift middleware to relay information about a request back to the client.

Current Inspectors
------------------

* Timing - Adds the "Inspector-Timing" header to the request indicating the
  amount of time it took the proxy server to process the request.

```Shell
$ curl -i -XGET -H'x-auth-token: AUTH_tkd03626426c8647aeba7eb150330e8be6' http://127.0.0.1:8080/v1/AUTH_test/example_container -H'inspector: timing'
HTTP/1.1 200 OK
...
Inspector-Timing: 0.0140538215637

example_object
```

* Locations - Adds the "Inspector-Locations" header to the request indicating 
  what account/container/object servers the path resides on.

```Shell
$ curl -i -XGET -H'x-auth-token: AUTH_tkd03626426c8647aeba7eb150330e8be6' http://127.0.0.1:8080/v1/AUTH_test/example_container -H'inspector: locations'
HTTP/1.1 200 OK
...
Inspector-Locations: http://127.0.0.1:6041/sdb4/178, http://127.0.0.1:6021/sdb2/178, http://127.0.0.1:6011/sdb1/178

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
# hmac_key = Password1
#
# exclude - List of inspector names separated by spaces to exclude.  This 
#           will cause a invalid inspector error if a request attempts to
#           request it.
# exclude = Locations
```

* Restart your proxy servers.