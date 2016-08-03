# cnav-bot
Autonomous vehicle system using [pi2go](http://www.pi2go.co.uk/) integrated robot and Raspberry Pi.

## Required hardware

* [pi2go](http://www.pi2go.co.uk/)
* Raspberry Pi 3
* Picamera

## Local installation

    $ git clone https://github.com/konradko/cnav-bot
    $ cd cnav-bot
    $ mkvirtualenv cnav-bot -a .
    $ make

## Deployment setup

1. Create a new Raspberry Pi 3 application (e.g. `cnavbot`) on [resin.io](https://dashboard.resin.io/)
2. Add resin remote to the `cnav-bot` repository, e.g.:

    ```
    $ git remote add resin username@git.resin.io:username/cnavbot.git
    ```

3. Download resin.io application device OS and flash it on an SD card ([etcher.io](https://www.etcher.io/) recommended)
4. Put the SD card in the Raspberry Pi and wait for it to update (check status on [resin.io](https://dashboard.resin.io/) dashboard)

## Deployment 

    $ make deploy

