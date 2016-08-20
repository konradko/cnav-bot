# cnav-bot
Autonomous vehicle system using [pi2go](http://www.pi2go.co.uk/) and Raspberry Pi.

## Required hardware

* [pi2go](http://www.pi2go.co.uk/)
* Raspberry Pi 3
* Picamera

## Local installation

    $ git clone https://github.com/konradko/cnav-bot
    $ cd cnav-bot
    $ mkvirtualenv cnav-bot -a .
    $ make
    $ make test


## Deployment setup

1. Create a new Raspberry Pi 3 application (e.g. `cnavbot`) on [resin.io](https://dashboard.resin.io/)
2. Add resin remote to the `cnav-bot` repository, e.g.:

    ```
    $ git remote add resin username@git.resin.io:username/cnavbot.git
    ```

3. Enable Picamera by adding these variables to Fleet Configuration:

| Fleet Configuration variable | Value |
| ------------- | ------------- |
| RESIN_HOST_CONFIG_gpu_mem | 256 |
| RESIN_HOST_CONFIG_fixup_file | fixup_x.dat |
| RESIN_HOST_CONFIG_start_file | start_x.elf |

4. Download resin.io application device OS and flash it on an SD card ([etcher.io](https://www.etcher.io/) recommended)
5. Put the SD card in the Raspberry Pi and wait for it to update (check status on [resin.io](https://dashboard.resin.io/) dashboard)


## Monitoring

### [Sentry](http://www.getsentry.com/)
Application exception tracking and alerting

| Environment variable | Example value | Description
| ------------- | ------------- | ------------- |
| SENTRY_DSN | https://user:pass@app.getsentry.com/appnum | [Sentry](getsentry.com) DSN address |


### [Papertrail](http://www.papertrailapp.com/)
System and application logs

| Environment variable | Example value | Description
| ------------- | ------------- | ------------- |
| PAPERTRAIL_HOST | logs.papertrailapp.com | [Papertrail](papertrailapp.com) host |
| PAPERTRAIL_PORT | 12345 | Papertrail host port |
| BOT_LOG_PATH | /data/log/cnavbot | Bot app log path |


### [Prometheus](http://www.prometheus.io/)
System metrics and alerting

| Environment variable | Example value | Description
| ------------- | ------------- | ------------- |
| SMTP_HOST | smtp.mailgun.org:1234 | SMTP host and port |
| SMTP_ACCOUNT | postmaster@mailgun.com | Email address to send from |
| SMTP_PASSWORD | password123 | Password for the email address |
| THRESHOLD_CPU | 70 | max % of CPU in use |
| THRESHOLD_FS | 40 | min % of filesystem available |
| THRESHOLD_MEM | 300  | min MB of mem available |
| LOCAL_STORAGE_RETENTION | 360h0m0s | Period of data retention |

The metrics dashboard will be available at http://your-device-ip/consoles/node.html (you can make it available on the internet by enabling Public URL in resin.io dashboard).


## Deployment 

    $ make deploy

## SSH into the container using local network 

1. Set the `CLIENT_PUBKEY` environment variable to your public key in resin.io dashboard, on OSX you can copy it with:
    ```
    $ cat ~/.ssh/id_rsa.pub | pbcopy
    ```

| Environment variable | Example value | Description
| ------------- | ------------- | ------------- |
| CLIENT_PUBKEY | ssh-rsa ASDF12312... | Your public key |


2. Deploy the application:
    ```
    $ make deploy
    ```

3. SSH into a container using local address (you can get it from resin.io dashboard or using [resin-cli](https://github.com/resin-io/resin-cli)), e.g.:
    ```
    $ ./ssh.sh 192.168.1.15
    ```
