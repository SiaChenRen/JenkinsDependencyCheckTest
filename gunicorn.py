[Unit]
Description=gunicorn daemon
After=network.target

[Service]
Type=notify
User=root
Group=www-data
WorkingDirectory=/data # location of app
ExecStart=/usr/local/bin/gunicorn "app:create_app()" -b 0.0.0.0:80 -w 8
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
