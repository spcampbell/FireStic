Modifying Notification Templates
--------------------------------

Two templates are provided for configuring the layout of notifications. One for HTML and one for text. Email notifications include both to accomodate all viewing requirements at the client. SMS text messages use the text template only.

The templates are found in the `mustache_templates` directory: `template.html` and `template.txt`

Mustache variable tags are used to place the data inside each template. These are the funny looking `{{somedata}}` parts scattered throughout the template. Currently, all available tags are being used in the notifications, but more will be added soon. The goal is to have any of the alert data available and easily inserted using these tags.

The HTML template is a simple garden-variety HTML page. The CSS is at the top and the message body below. It can be opened in a browser as you play with the layout to allow for easy design work. The CSS is moved inline by the alert script automatically at run time to allow email clients to handle it gracefully.

The text template is intentionally very basic so that SMS messages do not get out of hand. The alert script splits the final rendered message into 160 character sections and sends them individually. Be careful about putting too much in the text version and overwhelming your phone with massive SMS messages.

**Currently available variable tags:**

|tag                        |description                                    |
|---------------------------|-----------------------------------------------|
|`{{alertid}}`              |Alert id from FireEye system                   |
|`{{alertname}}`            |Alert type (e.g. malware-callback)             |
|`{{timestamp}}`            |When event occurred                            |
|`{{action}}`               |Action taken by FireEye system (e.g. blocked)  |
|`{{severity}}`             |Severity assigned by FireEye system            |
|`{{threatname}}`           |If ips-event, this is the signature name. Otherwise, a list of malware names found|
|`{{threatinfo}}`           |If ips-event, this is a link to the CVE ID on cvedetails.com. Otherwise, a list of malware types found|
|`{{sourceip}}`             |Source ip address                              |
|`{{sourcehostname}}`       |Source host name                               |
|`{{sourcecity}}`           |Source city per geoip query                    |
|`{{sourceregion}}`         |Source state/region per geoip query            |
|`{{sourcecountry}}`        |Source country per geoip query                 |
|`{{sourceasn}}`            |Source ASN per geoip query                     |
|`{{destinationip}}`        |Destination ip address                         |
|`{{destinationhostname}}`   |Destination host name                          |
|`{{destinationcity}}`       |Destination city per geoip query               |
|`{{destinationregion}}`    |Destination state/region per geoip query       |
|`{{destinationcountry}}`   |Destination country per geoip query            |
|`{{destinationasn}}`       |Destination ASN per geoip query                |