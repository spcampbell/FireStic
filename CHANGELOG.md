###Change log for [FireStic](https://github.com/spcampbell/FireStic)

**Master branch is the latest release**

####2/20/15
- if [os-changes] exists, extracting [malicious-alert] from [os-changes] for each OS analyzed during this alert. This is sent both to Elasticsearch and also appended to the bottom of the HTML email notification.
- Color for severity in HTML email notification is now red/orange/yellow for critical/major/minor levels. Mustache template tag added to HTML template in CSS section for color.
- Documentation added that better explain how to handle errors installing premailer. See [Read the Docs](http://firestic.rtfd.org/)