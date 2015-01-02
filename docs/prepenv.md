Prepare Your Environment
-----------------------

#### Server Environment

I am currently running this script under the following conditions:

* [Ubuntu server 14.04.1 LTS](http://www.ubuntu.com/download/server)
* Python 2.7.6
* [Elasticsearch 1.4.0](http://www.elasticsearch.org)
* [FireEye NX Series](http://www.fireeye.com) w/ optional IPS module enabled

Other versions/variations have not been tested but it should relatively straightforward to work through any dependencies.

For help setting up Elasticsearch: [here is a good tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-logstash-and-kibana-to-centralize-and-visualize-logs-on-ubuntu-14-04).

[elasticsearch.org](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html) also has a [helpful guide](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html) for installing from repositories.

> **IMPORTANT:** Elasticsearch does not provide any security by default.
> It can be secured but I leave that exercise up to you and Google.
> Consider how you deploy this carefully as it will contain information
> you probably do not want easily accessible and/or tampered with.

My current test environment is two desktop machines with 4GB of RAM and i5 processors serving a two node cluster. The only change was to increase the heap memory size to 1GB.

####Elasticsearch Template

If you use Logstash to ship logs to Elasticsearch, a template is created automatically that adds an additional .raw sub field to every string field. We need to do that here too otherwise multi-word strings will be broken up and you'll hate dealing with that in Kibana.

The template is located in `firestic_ES_template.sh` located in the `prep_files` directory. You can run from a shell prompt...or, for your copy/paste convenience, here is the template and curl statement:

```Shell
curl -XPUT localhost:9200/_template/firestic_1 -d '
{
	"template" : "firestic-*",
	"settings" : {
		"number_of_shards" : 5,
		"index.refresh_interval" : "5s"
	},
	"mappings" : {
		"_default_" : {
			"_all" : {"enabled" : true},
			"dynamic_templates" : [{
				"string_fields" : {
					"match" : "*",
					"match_mapping_type" : "string",
					"mapping" : {
						"type" : "string", "index" : "analyzed", "omit_norms" : true,
						"fields" : {
							"raw" : {"type": "string", "index" : "not_analyzed", "ignore_above" : 256}
						}
					}
				}
			}]
		}
	}
}'
```

#### Configure FireEye to Send Notifications

* In your FireEye appliance, click on "Settings" then "Notifications"
* click "http" at the top of table
* Add a new http server
	* The server url is the ip address or hostname plus port of the machine where the script will run. For example: `http://192.168.1.2:8888`
	* Set the following:
		* Notification: All Events
    	* Delivery: Per Event
    	* Default Provider: Generic
    	* Message Format: JSON Extended
	* Make sure "enabled" is checked and click the "Update" button
