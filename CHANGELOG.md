###Change log for [FireStic](https://github.com/spcampbell/FireStic)

**Master branch is the latest release**

####9/25/2017
- changed time format so it is same for all alerts. Fireeye may have updated code which changed this so they are all the same. Previously, IPS events were different than all other alerts. Now they all match IPS events.

####3/9/2015
- Added script in `testing` folder for uploading test json data to FireStic
- Bug fix: malware-data was not being included fully if field was not an array
- New screen shot of email alert added

####2/20/15
- If [os-changes] exists, extracting [malicious-alert] from [os-changes] for each OS analyzed during this alert. This is sent both to Elasticsearch and also appended to the bottom of the HTML email notification. Shows the type of malicious activity that FireEye saw. This is very helpful for a quick context on what is going on.
- Color for severity in HTML email notification is now red/orange/yellow for critical/major/minor levels. Mustache template tag added to HTML template in CSS section for color.
- Documentation added that better explain how to handle errors installing premailer. See [Read the Docs](http://firestic.rtfd.org/)

####2/17/15
- Bug fixes. Was not handling malicious-alert info correctly. Error has been corrected.
