#!/bin/zsh

scp -r ~/PycharmProjects/kitchenConsumer pi@192.168.4.131:/home/pi/barcode
ssh pi@192.168.4.131 'sudo systemctl restart kitchen-consumer.service'