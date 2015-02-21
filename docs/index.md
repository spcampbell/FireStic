### **FireStic**

#### A python script that accepts [FireEye](https://www.fireeye.com) alerts as json over http and indexes (puts) the data into [Elasticsearch](http://www.elasticsearch.org)...and notifies you too.

>   **DISCLAIMER:** This script is still being developed and may contain numerous
>   bugs, flaws and discrepencies. It may cause various types of damage and will
>   likely make your hair turn grey and fall out. I am not liable for any
>   situations which result from the use of this code. There is no stated or
>   implied warranty. It may chip, rip, rattle or run down the hill...all
>   without warning. Use at your own risk. I am not a professional programmer
>   and only offer this code as documentation of my humble attempt at solving a
>   problem for my own needs.

#### The latest version is always in the [master branch on github](https://github.com/spcampbell/FireStic/tree/master).

See [changelog](https://github.com/spcampbell/FireStic/blob/develop/CHANGELOG.md) for changes beginning 2/20/15


#### Highlights

**Concerning Elasticsearch:**

- Put FireEye alerts into [Elasticsearch](http://www.elasticsearch.org)
- Handles the variability of FireEye alert structure
- Alternative to using [Logstash](http://logstash.net) which can get quite complex with FireEye alerts
- Accepts alerts formatted in `JSON Extended` over http
- Adds geoip information to alert using [pygeoip](https://github.com/appliedsec/pygeoip)
- Allows for different geoip databases for internal vs. external ip addresses
- Adds hostname information by performing a DNS lookup on both source and destination ip addresses

**Concerning Notifications:**

- Send notifications via email and SMS
- Notifications can be turned on/off completely, by alert type, or by FireEye action
- Customizable HTML email messages allow for easy reading and detail highlighting
- SMS message are correctly split at 160 characters
- Uses [mustache](http://mustache.github.io) templates (via [pystache](https://github.com/defunkt/pystache)) for designing notification messages
- Automatically puts CSS inline before sending using [premailer](http://www.peterbe.com/plog/premailer.py)
- Notifications include additional information like hostname and location

>   **NOTE:** Currently, the [os-changes] field is not included in the indexing
>   process as it can vary quite a bit and more examples are needed before
>   general patterns can be uncovered. Including this data is a top priority as
>   this field is a goldmine of information related to an incident. For now, if the
>   [os-changes] field is found in the json, the entire [os-changes] tree is saved
>   to a file called oschanges.json to use in developing the code.
>
>   **UPDATE:** if [os-changes] exists and includes information in [malicious-alert],
>   then that data is now appended to the end of the email. There will be a section
>   for each OS analyzed. This is key information for understanding what happened.

#### Documentation Quick Reference
- [Prepare Your Environment](prepenv)
    - Server Environment
    - Elasticsearch Template
    - Configure FireEye to Send Notifications
- [Prepare The Script and Dependencies](prepscript)
    - Python Module Dependencies
    - Geoip Setup
    - FireStic Script Configuration
        - firestic.py Settings
        - firestic_alert.py Settings
- [Start the Show](start)
    - Running the Script
    - Send Some Test Alerts
- [Customizing Notification Templates](templates)
- [Other Stuff](other)
    - Kibana Template (optional)
- [TODO](TODO)

#### License

The MIT License (MIT)

Copyright (c) 2014

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
