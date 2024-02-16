#!/bin/bash

cp rlogging.service /etc/systemd/system
systemctl daemon-reload
systemctl enable rlogging
systemctl start rlogging
systemctl status rlogging
