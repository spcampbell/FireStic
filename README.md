### **FireStic**

#### A python script that accepts [FireEye](https://www.fireeye.com) alerts as json over http and indexes (puts) the data into [Elasticsearch](http://www.elasticsearch.org)...and notifies you too.

#### Full documentation is located at: [Read The Docs](http://firestic.rtfd.org)

>   **DISCLAIMER:** This script is still being developed and may contain numerous
>   bugs, flaws and discrepencies. It may cause various types of damage and will
>   likely make your hair turn grey and fall out. I am not liable for any
>   situations which result from the use of this code. There is no stated or
>   implied warranty. It may chip, rip, rattle or run down the hill...all
>   without warning. Use at your own risk. I am not a professional programmer
>   and only offer this code as documentation of my humble attempt at solving a
>   problem for my own needs.

#### The latest version is always in `master`.
#### Last update to master: 2/20/2015

See [changelog](changelog.md) for changes beginning 2/20/15

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

#### License

The MIT License (MIT)

Copyright (c) 2014

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.