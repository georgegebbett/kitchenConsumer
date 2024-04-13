#!/bin/zsh

scp -r ~/PycharmProjects/kitchenConsumer pi@192.168.0.223:/home/pi/barcode
#ssh pi@kitchen.local 'sudo systemctl restart kitchen-consumer.service'