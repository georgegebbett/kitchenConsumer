#!/bin/zsh

scp -r ~/PycharmProjects/kitchenConsumer pi@192.168.1.132:/home/pi/barcode
ssh pi@kitchen.local 'sudo systemctl restart kitchen-consumer.service'