### **FireStic**

#### A python script that accepts FireEye alerts as json over http and indexes (puts) the data into Elasticsearch...and notifies you too.

>   **NOTE:** This script is still being developed and may contain numerous
>   bugs, flaws and discrepencies. It may cause various types of damage and will
>   likely make your hair turn grey and fall out. I am not liable for any
>   situations which result from the use of this code. There is no stated or
>   implied warranty. It may chip, rip, rattle or run down the hill...all
>   without warning. Use at your own risk. I am not a professional programmer
>   and only offer this code as documentation of my humble attempt at solving a
>   problem for my own needs.

#### Highlights

**Concerning Elasticsearch:**

- Put FireEye alerts into Elasticsearch
- Handles the variability of FireEye alert structure
- Alternative to using Logstash which can get quite complex with FireEye alerts
- Accepts alerts formatted in `JSON Extended` over http
- Adds geoip information to alert using pygeoip
- Allows for different geoip databases for internal vs. external ip addresses
- Adds hostname information by performing a DNS lookup on both source and destination ip addresses

**Concering Notifications:**

- Send notifications via email and SMS
- Notifications can be turned on/off completely, by alert type, or by FireEye action
- Builds HTML email message allowing for an easier to read notification
- Builds ascii text SMS message and splits it at 160 characters
- Uses mustache for easy to build message templates
- Automatically puts CSS inline before sending
- Notifications include additional information like hostname and location

>   **NOTE:** Currently, the [os-changes] field is not included in the indexing
>   process as it can vary quite a bit and more examples are needed before
>   general patterns can be uncovered. Including this data is a top priority as
>   this field is a goldmine of information related to an incident. For now, if the
>   [os-changes] field is found in the json, the entire [os-changes] tree is saved
>   to a file called oschanges.json to use in developing the code.

####Quick Reference
- [Prepare Your Environment](#prepare-your-environment)
    - [Environment](#environment)
    - [Elasticsearch Template Setup](#elasticsearch-template-setup)
    - [FireEye Setup](#fireeye-setup)
- [Prepare The Script and Dependencies](#prepare-the-script-and-dependencies)
    - [Python Module Dependencies](#python-module-dependencies)
    - [Geoip Setup](#geoip-setup)
    - [Script Configuration](#script-configuration)
        - [firestic.py Configuration Settings](#firesticpy-configuration-settings)
        - [firestic_alert.py Configuration Settings](#firestic_alertpy-configuration-settings)
- [Start the Show](#start-the-show)
    - [Running the Script](#running-the-script)
    - [Send Some Test Alerts](#send-some-test-alerts)
- [Other Stuff](#other-stuff)
    - [Kibana Demo Template (optional)](#kibana-demo-template-optional)
    - [TODO](#todo)

Prepare Your Environment
-----------------------

#### Environment

I am currently running this script under the following conditions:

* Ubuntu server 14.04.1 LTS
* Python 2.7.6
* [Elasticsearch 1.4.0](http://www.elasticsearch.org)
* [FireEye NX Series](http://www.fireeye.com) w/ optional IPS module enabled

Other versions/variations have not been tested but it should relatively straightforward to work through any dependencies.

For help setting up Elasticsearch, [HERE](https://www.digitalocean.com/community/tutorials/how-to-use-logstash-and-kibana-to-centralize-and-visualize-logs-on-ubuntu-14-04) is a good tutorial.

[elasticsearch.org](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html) also has a [helpful guide](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html) for installing from repositories.

> **IMPORTANT:** Elasticsearch does not provide any security by default.
> It can be secured but I leave that exercise up to you and Google.
> Consider how you deploy this carefully as it will contain information
> you probably do not want easily accessible and/or tampered with.

My current test environment is two desktop machines with 4GB of RAM and i5 processors serving a two node cluster. The only change was to increase the heap memory size to 1GB.

#### Elasticsearch Template Setup

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

#### FireEye Setup

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

Prepare The Script and Dependencies
-----------------------------------

#### Python Module Dependencies:

You will need to install the following python modules:

- pygeoip
- pytz
- elasticsearch
- pystache
- premailer

`pip install <module name>` should get you set up.

For reference, here are the other modules:

- smtplib
- email.mime.multipart
- email.mime.text
- json
- datetime
- BaseHTTPServer
- logging
- socket

#### Geoip Setup

Download the free GeoLite City and GeoLite ASN databases (the binary versions) from [MaxMind](http://dev.maxmind.com/geoip/legacy/geolite/).

Place the files in the geoip folder.

The script accomodates different database files for internal vs. external devices. However, you will need to create a geoip database for your internal addresses and locations. Here is the best instruction I have found on how to do that: [Generate Local MaxMind Database](https://blog.vladionescu.com/geo-location-for-internal-networks/). It uses [mmutils](https://github.com/mteodoro/mmutils). The article describes adding your internal network locations and private ip addresses to the MaxMind CSV files. However, you will want to make your own CSV files with only internal networks and locations then compile them to a new .dat for the best result. The process is basically the same and fairly straightforward once you see how the two .csv files are organizing the data.

>   **TIP:** Do not open the csv files you create in Microsoft Excel as it will
>   completely wreck it out and will never compile. Use Open Office or a text
>   editor. Make sure the file is of type UNIX and not MAC or Windows. You
>   should be able to set this in most decent text editors (Notepad++,
>   TextWrangler, etc, etc)

#### Script Configuration

~~Both firestic.py and firestic\_alert.py have configurations that need to be dealt with before running the script. These are located at the beginning of each script file (firestic.py and firestic_alert.py)~~

UPDATE: All configuration options are now located in `fsconfig.py`. Please configure the settings below in that file.

####firestic.py Configuration Settings:

|setting name|example|description|
|----------|------------|-------------|
|esIndex|`'firestic'`|Elasticsearch index to use. `-YYYY.MM.DD` will be appended ala Logstash|
|extGeoipDatabase|`'geoip/GeoLiteCity.dat'`|Geoip database for external (internet) addresses|
|intGeoipDatabase|`'geoip/YourLocations.dat'`|Geoip database for internal (LAN) addresses. You'll have to create this one. See the [Geoip Setup section above](#geoip-setup)|
|ASNGeoipDatabase|`'geoip/GeoIPASNum.dat'`|Geoip database for external address ASN info|
|localASN|`'your_org_name'`|ASN for internal ip addresses. Since internal addresses are private, this is used in the ASN field|
|httpServerIP|`'192.168.1.2'`|ip address for http server to listen on|
|httpServerPort|`8888`|Port for http server to listen on|
|logfile|`'firestic_error.log'`|File for logging errors|
|sendAlerts|`True`|Turn email/SMS alerts off `False` or on `True`|

####firestic_alert.py Configuration Settings
|setting name|example|description|
|-------------|---------------|---------------|
|smtpServer|`'relayserver.yourdomain.org'`|Your email server FQDN or ip address|
|smtpPort|`25`|Port on your email server|
|fromEmail|`'Firestic@donotreply.yourdomain.org'`|Where the email alerts show to come from|
|toEmail|`'securitydude@yourdomain.org'`|Who to send the email alerts to. Separate multiple addresses with commas|
|emailTypeAlertOn|`['ips-event','malware-callback','malware-object']`|The types of alerts to send an email for. Possible types are: `ips-event`, `malware-callback`, `malware-object`, `infection-match`, `domain-match`, `web-infection`|
|toSMS|`'aphonenumber@vtext.com'`|Who to send SMS alerts to. Format depends on the carrier. Separate multiple addresses with commas|
|smsTypeAlertOn|`['malware-callback','malware-object']`|Possible types are the same as those for emailTypeAlertOn|
|smsActionAlertOn|`['notified','alert']`|Only send SMS when these actions were reported by FireEye for this alert. Possible actions: `blocked`, `notified`, `alert`. Make this an empty array `[]` to not send SMS for anything|
|myTimezone|`'US/Eastern'`|Local timezone for conversion (@timestamp is UTC). Common US TZ: `US/Central` `US/Eastern` `US/Mountain` `US/Pacific`. See [HERE](http://stackoverflow.com/questions/13866926/python-pytz-list-of-timezones) for a full list.|

Start the Show
--------------

#### Running the Script

On one of your Elasticsearch nodes, run the script from the command line like this:

`sudo python firestic.py`

See if it is running and accessible from another machine by going to the following in a browser:

`http://<ip address where script is running>:<port>/ping`

for example: `http://192.168.1.2:8888/ping`

Note that all posible exceptions are not being logged to file. You'll want to be able to see any exceptions that get thrown to stdout so running it from the console is preferred. Please report any issues you run across.

I will daemonize the script later. For now, this will have to do.

> **TIP:** Use [screen](http://www.gnu.org/software/screen/) to keep it running after log out.
> Then you can ssh in from anywhere and check stdout as well as stop/start.

#### Send Some Test Alerts

In your FireEye appliance, back on the notifications screen, look just under the table for a "Test-Fire" button. You can select the various types of alerts from the drop and down and click the button to send a test alert. I suggest doing a test notification for each one. If all is well, you'll see a single line per alert in the terminal where you are running the script (...and hopefully no exceptions are thrown) that looks like:

`<Fire.Eye.ip.address> - - [16/Dec/2014 08:08:09] "POST / HTTP/1.1" 200 -`

Now check Elasticsearch to make sure the alerts made it. You can look in Kibana (preferred) or run the following:

`curl -XGET localhost:9200/firestic*/_search?pretty`

Other Stuff
-----------

#### Kibana Demo Template (optional)

To get you up and running quickly, a dashboard template for Kibana is available in the file `firestic_kibana.json` located in the `prep_files` directory.

#### TODO

* Move documentation to RTFD
* Code to deal with os-changes data and index into Elasticsearch. Need to determine best relationship strategy (in code vs. nesting vs. parent-child)
* Set up alerting config so type vs action is configurable for each possibility
* Better logging with comprehensive exception handling to logs
* ~~Put config items in standalone file.~~ *Done*.
* Daemonize
* Easy install via PyPI
* Add option to use SSL
* Add multi-thread capability (or refactor for use with NGINX/Apache)
* Examine possibility of gathering IOCs from os-changes. Would put in STIX or openIOC format. Maybe hand off for scans.
* Research other data gathering options for incorporating in alert.
* Initiate Redline scan with winexe?
* Kick off scan using another tool like Google's GRR?

#### Q: FireStic? Really? Where did you get that stupid name?

**A:** Because it indexes **FIRE**eye alerts into ela**STIC**search...and I'm not overly creative.
