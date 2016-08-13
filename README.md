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

## Deployment setup

1. Create a new Raspberry Pi 3 application (e.g. `cnavbot`) on [resin.io](https://dashboard.resin.io/)
2. Add resin remote to the `cnav-bot` repository, e.g.:

    ```
    $ git remote add resin username@git.resin.io:username/cnavbot.git
    ```

3. Enable Picamera by adding these variables to Fleet Configuration:
    ```
    RESIN_HOST_CONFIG_gpu_mem=256
    RESIN_HOST_CONFIG_fixup_file=fixup_x.dat
    RESIN_HOST_CONFIG_start_file=start_x.elf
    ```

4. Download resin.io application device OS and flash it on an SD card ([etcher.io](https://www.etcher.io/) recommended)
5. Put the SD card in the Raspberry Pi and wait for it to update (check status on [resin.io](https://dashboard.resin.io/) dashboard)

## Deployment 

    $ make deploy

## SSH into the container using local network 

1. Set the `CLIENT_PUBKEY` environment variable to your public key in resin.io dashboard, on OSX you can copy it with:
    ```
    $ cat ~/.ssh/id_rsa.pub | pbcopy
    ```

2. Deploy the application:
    ```
    $ make deploy
    ```

3. SSH into a container using local address (you can get it from resin.io dashboard or using [resin-cli](https://github.com/resin-io/resin-cli)), e.g.:
    ```
    $ ./ssh.sh 192.168.1.15
    ```
