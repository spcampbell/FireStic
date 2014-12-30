# FireStic - Python script for indexing FireEye json alerts
# into Elasticsearch over http...and some alerting too
#
# Please see: https://github.com/gnonai/firestic
#
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz  		# pip install pytz


def sendAlert(theJson, fsconfig):

    # Prepare alert data to include in email
    emailData = gatherEmailData(theJson, fsconfig.myTimezone)

    # Build html version of message
    htmlEmail = buildHTMLMessage(emailData)

    # Build text version of message
    textEmail = buildTextMessage(emailData)

    # Email subject
    subjectLine = "FireStic Alert - " + emailData['alertname'] + " - "
    subjectLine += emailData['alertid'] + " - " + emailData['action']

    # ---------------------------------------

    # Send SMS
    if emailData['alertname'] in fsconfig.smsTypeAlertOn:
        if emailData['action'] in fsconfig.smsActionAlertOn:
            txtMessages = splitForSMS(textEmail, emailData['alertid'])
            for txtMessage in txtMessages:
                msg = MIMEMultipart('alternative')
                msg['From'] = fsconfig.fromEmail
                msg['To'] = fsconfig.toSMS
                msg.attach(MIMEText(txtMessage, 'plain'))
                s = smtplib.SMTP(fsconfig.smtpServer, fsconfig.smtpPort)
                s.sendmail(fsconfig.fromEmail, fsconfig.toSMS, msg.as_string())
                s.quit()

    # ---------------------------------------

    # Send email
    if emailData['alertname'] in fsconfig.emailTypeAlertOn:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subjectLine
        msg['From'] = fsconfig.fromEmail
        msg['To'] = fsconfig.toEmail
        part1 = MIMEText(textEmail, 'plain')
        part2 = MIMEText(htmlEmail, 'html')
        msg.attach(part1)
        msg.attach(part2)
        s = smtplib.SMTP(fsconfig.smtpServer, fsconfig.smtpPort)
        s.sendmail(fsconfig.fromEmail, fsconfig.toEmail, msg.as_string())
        s.quit()

    # ---------------------------------------


def buildHTMLMessage(emailData):
    # HTML version of message
    htmlEmail = u"""\
    <html><head><style>
    #outertable table, th, td {
        border: 1px solid #85CEFF;
        border-collapse: collapse;
        padding: 8px;
        text-align: left;   }
    #inntertable table, th, td {
        border: 0px solid black;
        border-collapse: collapse;
        padding: 6px;
        text-align: left;
        font-size: .9em;    }
    .highlight {
        background-color: #85CEFF;
        font-weight: bold;  	}
    .action {
        padding: 4px;
        background-color: orange;
        font-weight:bold;	}
    body {
        font-family: Verdana, Arial;
        font-size: 100%;    }
    </style></head><body>
    <table id="outertable">
        <tr><td><table id="innertable">
            <tr class="highlight"><td>""" + emailData['alertname'] + u" - " + emailData['alertid'] + u"""</td></tr>
            <tr><td>""" + emailData['timestamp'] + u"""</td></tr>
            <tr><td>Action: <span class="action">""" + emailData['action'] + u"""</span></td></tr>
            <tr><td>Threat Name: """ + emailData['threatname'] + u"""</td></tr>
            <tr><td>Threat Info: """ + emailData['threatinfo'] + u"""</td></tr>
            <tr><td>Severity: """ + emailData['severity'] + u"""</td></tr>
            <tr><td><a href=\"""" + emailData['alerturl'] + u"""\">FireEye Alert Link</a></td></tr>
        </table></td></tr>
        <tr><td><table id="innertable">
            <tr class="highlight"><td>Source</td></tr>
            <tr><td>""" + emailData['sourceip'] + u"""</td></tr>
            <tr><td>Hostname: """ + emailData['sourcehostname'] + u"""</td></tr>
            <tr><td>""" + emailData['sourcecity'] + u", " + emailData['sourceregion'] + u"""</td></tr>
            <tr><td>""" + emailData['sourcecountry'] + u"""</td></tr>
            <tr><td>ASN: """ + emailData['sourceasn'] + u"""</td></tr>
        </table></td></tr>
        <tr><td><table id="innertable">
            <tr class="highlight"><td>Destination</td></tr>
            <tr><td>""" + emailData['destinationip'] + u"""</td></tr>
            <tr><td>Hostname: """ + emailData['destinationhostname'] + u"""</td></tr>
            <tr><td>""" + emailData['destinationcity'] + u", " + emailData['destinationregion'] + u"""</td></tr>
            <tr><td>""" + emailData['destinationcountry'] + u"""</td></tr>
            <tr><td>ASN: """ + emailData['destinationasn'] + u"""</td></tr>
        </table></td></tr>
    </table></body></html>"""

    return encode_for_html(htmlEmail)


def buildTextMessage(emailData):
    # text version of message (also used for SMS)
    textEmail = u'ID: ' + emailData['alertid'] + u'\n'
    textEmail += u'Type: ' + emailData['alertname'] + u'\n'
    textEmail += u'Action: ' + emailData['action'] + u'\n'
    textEmail += u'Severity: ' + emailData['severity'] + u'\n'
    textEmail += u'Threat: ' + emailData['threatname'] + u'\n'
    textEmail += u'Source: ' + emailData['sourceip'] + u'\n'
    textEmail += emailData['sourcecity'] + u','
    textEmail += emailData['sourceregion'] + u'\n'
    textEmail += emailData['sourcecountry'] + u'\n'
    textEmail += emailData['sourceasn'] + u'\n'
    textEmail += u'Destination: ' + emailData['destinationip'] + u'\n'
    textEmail += emailData['destinationcity'] + u','
    textEmail += emailData['destinationregion'] + u'\n'
    textEmail += emailData['destinationcountry'] + u'\n'
    textEmail += emailData['destinationasn']

    return textEmail


def encode_for_html(unicode_data, encoding='ascii'):
    try:
        return unicode_data.encode(encoding, 'xmlcharrefreplace')
    except:
        print "encode_for_html failed for: "
        print unicode_data
        return " "


def splitForSMS(fullText, alertID):
    texts = []
    words = fullText.split(' ')
    curtext = ''
    for word in words:
        # for the first word, drop the space
        if len(curtext) == 0:
            curtext += word

        # check if there's enough space left in the current message
        elif len(curtext) <= 155 - (len(word) + 1):
            curtext += ' ' + word

        # not enough space. make a new message
        else:
            texts.append(curtext)
            curtext = '(' + alertID + '...) ' + word
    if curtext != '':
        texts.append(curtext)

    return texts


def gatherEmailData(alertData, myTimezone):
    # The process of gathering our data from the json sent over by FireEye is
    # complicated by the various permutations of how that data is presented,
    # plus the common situation where there is less data in some than in others.
    # It is likely that some of the following checks (especially the setdefault calls)
    # are redundant or unnecessary. However, without a definitive answer on what
    # all of the possibilities are, the code tries to cover the worst case scenario,
    # which may not ever happen. There is also a possibility that a variation will
    # cause an exception.

    severityLevels = {u'crit': u'Critical', u'majr': u'Major', u'minr': u'Minor'}
    emptyValue = u'N/A'
    emailData = {}

    emailData['timestamp'] = aslocaltimestr(alertData['@timestamp'], myTimezone)

    alertData = alertData.setdefault('alert', {})

    emailData['alertname'] = alertData.setdefault('name', emptyValue)
    emailData['alertid'] = str(alertData['id'])

    emailData['severity'] = alertData.setdefault('severity', emptyValue)
    if emailData['severity'] in severityLevels:
        emailData['severity'] = severityLevels[emailData['severity']]

    emailData['alerturl'] = alertData.setdefault('alert-url', emptyValue)

    # ips-events provide a signature name and possible a CVE-ID
    # everything else tries to provide info on the malware
    if emailData['alertname'] == u'ips-event':
        emailData['threatname'] = alertData.setdefault('explanation', {}).setdefault('ips-detected', {}).setdefault('sig-name', emptyValue)
        emailData['threatinfo'] = alertData.setdefault('explanation', {}).setdefault('ips-detected', {}).setdefault('cve-id', emptyValue)
        if (emailData['threatinfo'] != emptyValue) and (emailData['threatinfo'] is not None) and (emailData['threatinfo'] != ''):
            emailData['threatinfo'] = u'<a href="http://www.cvedetails.com/cve/' + emailData['threatinfo'] + u'/">' + emailData['threatinfo'] + u' on cvedetails.com</a>'
        else:
            emailData['threatinfo'] = emptyValue
        emailData['action'] = alertData.setdefault('explanation', {}).setdefault('ips-detected', {}).setdefault('action-taken', emptyValue)
    else:
        # sometimes the malware field is an array, sometimes not
        if isinstance(alertData.setdefault('explanation', {}).setdefault('malware-detected', {}).setdefault('malware', {}), list):
            mwNames = []
            mwInfo = []
            for element in alertData['explanation']['malware-detected']['malware']:
                # if (element.has_key('name')) and (element['name'] is not None):
                if ('name' in element) and (element['name'] is not None):
                    mwNames.append(element['name'])
                # if (element.has_key('original')) and (element['original'] is not None):
                if ('original' in element) and (element['original'] is not None):
                    mwNames.append(element['original'])
                # if (element.has_key('stype')) and (element['stype'] is not None):
                if ('stype' in element) and (element['stype'] is not None):
                    mwInfo.append(element['stype'])

            if len(mwNames):
                emailData['threatname'] = ', '.join(mwNames)
            else:
                emailData['threatname'] = emptyValue
            if len(mwInfo):
                emailData['threatinfo'] = ', '.join(mwInfo)
            else:
                emailData['threatinfo'] = emptyValue
        else:
            emailData['threatname'] = alertData['explanation']['malware-detected']['malware'].setdefault('name', emptyValue)
            emailData['threatinfo'] = alertData['explanation']['malware-detected']['malware'].setdefault('stype', emptyValue)

        emailData['action'] = alertData.setdefault('action', emptyValue)

    emailData['sourceip'] = alertData.setdefault('src', {}).setdefault('ip', emptyValue)
    emailData['destinationip'] = alertData.setdefault('dst', {}).setdefault('ip', emptyValue)

    # source detail
    if alertData['src'].setdefault('geoip', {}) is None:
        alertData['src']['geoip'] = {}
    if alertData['src']['geoip'].setdefault('city', emptyValue) is None:
        alertData['src']['geoip']['city'] = emptyValue
    emailData['sourcecity'] = alertData['src']['geoip']['city']
    if alertData['src']['geoip'].setdefault('region_code', emptyValue) is None:
        alertData['src']['geoip']['region_code'] = emptyValue
    emailData['sourceregion'] = alertData['src']['geoip']['region_code']
    if alertData['src']['geoip'].setdefault('country_name', emptyValue) is None:
        alertData['src']['geoip']['country_name'] = emptyValue
    emailData['sourcecountry'] = alertData['src']['geoip']['country_name']
    if alertData['src']['geoip'].setdefault('asn', emptyValue) is None:
        alertData['src']['geoip']['asn'] = emptyValue
    emailData['sourceasn'] = alertData['src']['geoip']['asn']
    if alertData['src']['geoip'].setdefault('hostname', emptyValue) is None:
        alertData['src']['geoip']['hostname'] = emptyValue
    emailData['sourcehostname'] = alertData['src']['geoip']['hostname']

    # destination detail
    if alertData['dst'].setdefault('geoip', {}) is None:
        alertData['dst']['geoip'] = {}
    if alertData['dst']['geoip'].setdefault('city', emptyValue) is None:
        alertData['dst']['geoip']['city'] = emptyValue
    emailData['destinationcity'] = alertData['dst']['geoip']['city']
    if alertData['dst']['geoip'].setdefault('region_code', emptyValue) is None:
        alertData['dst']['geoip']['region_code'] = emptyValue
    emailData['destinationregion'] = alertData['dst']['geoip']['region_code']
    if alertData['dst']['geoip'].setdefault('country_name', emptyValue) is None:
        alertData['dst']['geoip']['country_name'] = emptyValue
    emailData['destinationcountry'] = alertData['dst']['geoip']['country_name']
    if alertData['dst']['geoip'].setdefault('asn', emptyValue) is None:
        alertData['dst']['geoip']['asn'] = emptyValue
    emailData['destinationasn'] = alertData['dst']['geoip']['asn']
    if alertData['dst']['geoip'].setdefault('hostname', emptyValue) is None:
        alertData['dst']['geoip']['hostname'] = emptyValue
    emailData['destinationhostname'] = alertData['dst']['geoip']['hostname']

    return emailData


def aslocaltimestr(utc_str, myTimezone):
    utc_dt = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    local_tz = pytz.timezone(myTimezone)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt).strftime('%m-%d-%Y %H:%M:%S %Z%z')
