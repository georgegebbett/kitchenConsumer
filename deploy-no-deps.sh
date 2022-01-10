#!/bin/zsh

scp ~/PycharmProjects/kitchenConsumer/* pi@192.168.4.131:/home/pi/barcode/kitchenConsumer
ssh pi@192.168.4.131 'sudo systemctl restart kitchen-consumer.service'