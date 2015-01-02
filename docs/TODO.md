TODO
----

* ~~Move documentation to RTFD~~ *Done*
* ~~Put config items in standalone file.~~ *Done*.
* Code to deal with os-changes data and index into Elasticsearch. Need to determine best relationship strategy (in code vs. nesting vs. parent-child)
* Set up alerting config so type vs action is configurable for each possibility
* Better logging with comprehensive exception handling to logs
* Daemonize
* Easy install via PyPI
* Add option to use SSL
* Add multi-thread capability (or refactor for use with NGINX/Apache)
* Examine possibility of gathering IOCs from os-changes. Would put in STIX or openIOC format. Maybe hand off for scans.
* Research other data gathering options for incorporating in alert.
* Initiate Redline scan with winexe?
* Kick off scan using another tool like Google's GRR?