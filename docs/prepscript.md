Prepare The Script and Dependencies
-----------------------------------

#### Python Module Dependencies:

You will need to install the following python modules:

- [pygeoip](https://github.com/appliedsec/pygeoip)
- [pytz](http://pytz.sourceforge.net)
- [elasticsearch](http://www.elasticsearch.org/guide/en/elasticsearch/client/python-api/current/)
- [pystache](https://github.com/defunkt/pystache)
- [premailer](http://www.peterbe.com/plog/premailer.py)

`pip install <module name>` should get you set up.

(To install pip on Ubuntu, run: `sudo apt-get install python-pip`)

> NOTE: If [premailer](http://www.peterbe.com/plog/premailer.py) throws errors on install, it is usually due to
> package dependencies missing in the OS related to `lxml`. For Ubuntu, try this:
>
> - Uninstall premailer if you tried to install and got errors: `sudo pip uninstall premailer`
> - Install dependencies : `sudo apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev python2.7-dev`
> - Reinstall premailer: `sudo pip install premailer`
>
> More help here: http://stackoverflow.com/questions/5178416/pip-install-lxml-error
>

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

Place the files in the `geoip` folder.

The script accomodates different database files for internal vs. external devices. However, **you will need to create the geoip database for your internal addresses and locations**. Here is the best instruction I have found on how to do that: [Generate Local MaxMind Database](https://blog.vladionescu.com/geo-location-for-internal-networks/). It uses [mmutils](https://github.com/mteodoro/mmutils). The article describes adding your internal network locations and private ip addresses to the MaxMind CSV files. However, **you will want to make your own CSV files with only internal networks and locations then compile them to a new .dat for the best result.** The process is basically the same and fairly straightforward once you see how the two .csv files are organizing the data.

>   **TIP:** Do not open the csv files you create in Microsoft Excel as it will
>   completely wreck it out and will never compile. Use Open Office or a text
>   editor. Make sure the file is of type UNIX and not MAC or Windows. You
>   should be able to set this in most decent text editors (Notepad++,
>   TextWrangler, etc, etc)

#### FireStic Script Configuration

All configuration options are now located in `fsconfig.py`. Please configure the settings below in that file.

####firestic.py Settings:

|setting name|example|description|
|----------|------------|-------------|
|esIndex|`'firestic'`|Elasticsearch index to use. `-YYYY.MM.DD` will be appended ala Logstash|
|extGeoipDatabase|`'geoip/GeoLiteCity.dat'`|Geoip database for external (internet) addresses|
|intGeoipDatabase|`'geoip/YourLocations.dat'`|Geoip database for internal (LAN) addresses. If you want to map these ip addresses to geo coordinates, you'll have to create the file. See the [Geoip Setup section above](#geoip-setup). You can use the same file as `extGeoipDatabase` but it will not resolve internal addresses|
|ASNGeoipDatabase|`'geoip/GeoIPASNum.dat'`|Geoip database for external address ASN info|
|localASN|`'your_org_name'`|ASN for internal ip addresses. Since internal addresses are private, this is used in the ASN field|
|httpServerIP|`'192.168.1.2'`|ip address for http server to listen on|
|httpServerPort|`8888`|Port for http server to listen on|
|logfile|`'firestic_error.log'`|File for logging errors|
|sendAlerts|`True`|Turn email/SMS alerts off `False` or on `True`|

####firestic_alert.py Settings

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
