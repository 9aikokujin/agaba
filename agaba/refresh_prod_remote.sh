#!/bin/bash

ssh "$REMOTE_USER@$REMOTE_HOST" "echo '$PASSWORD' | sudo -S sh -c 'cd /home/ubuntu/agaba/infra/prod && ./refresh_prod.sh'" 
