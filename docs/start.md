Start the Show
--------------

#### Running the Script

On one of your Elasticsearch nodes, run the script from the command line like this:

`sudo python firestic.py`

Check that it is running and accessible by going to the following in another computer's browser:

`http://<ip address where script is running>:<port>/ping`

for example: `http://192.168.1.2:8888/ping`

At present, all exceptions are not being logged to file. You'll want to be able to see any exceptions that get thrown to stdout so running it from the console is preferred. Please report any issues you run across.

I will daemonize the script later. For now, this will have to do.

> **TIP:** Use [screen](http://www.gnu.org/software/screen/) to keep it running after log out.
> Then you can ssh in from anywhere and check stdout as well as stop/start. This is a great
> pseudo-service type of functionality and works very well.

#### Send Some Test Alerts

In your FireEye appliance, back on the notifications screen, look just under the table for a "Test-Fire" button. You can select the various types of alerts from the drop and down and click the button to send a test alert. I suggest doing a test notification for each one. If all is well, you'll see a single line per alert in the terminal where you are running the script (...and hopefully no exceptions are thrown) that looks like:

`<Fire.Eye.ip.address> - - [16/Dec/2014 08:08:09] "POST / HTTP/1.1" 200 -`

Now check Elasticsearch to make sure the alerts made it. You can look in Kibana (preferred) or run the following:

`curl -XGET localhost:9200/firestic*/_search?pretty`

Finally, if you are using notifications, check your email and/or text messages and make sure they came through.

Check for errors by looking for exceptions thrown to the screen and also in the log file (`firestic_error.log` by default).
