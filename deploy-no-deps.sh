#!/bin/zsh

scp ~/PycharmProjects/kitchenConsumer/* pi@192.168.4.131:/home/pi/barcode/kitchenConsumer
ssh pi@kitchen.local 'sudo systemctl restart kitchen-consumer.service'