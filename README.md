Dragon on wheels
================

`Dragon_on_wheels` is a simple SCGI/WSGI threaded server. Why do you
want to use it?

- It is very simple to use to install to read code.
- It provides standards WSGI and SCGI. So you can use standard tools like Django with it. And you can change `Dragon_on_wheels` layer any time to more complex solution like uWSGI.

Why do you NOT want to use `Dragon_on_wheels`?

- None thread-safe code. `Dragon_on_wheels` use threads.
- Python3. `Dragon_on_wheels` support Python2 only.

How to run simple WSGI application
==================================

Run SCGI-server
---------------

You can try `Dragon_on_wheels` without installation. To run
demo SCGI-server just get source codes and execute command

    python2 -m dragon_on_wheels

You have to get debug messages on your console:

    2016-01-09 01:51:19,225 24425:140234628392768 [INFO] Run demo server
    2016-01-09 01:51:19,225 24425:140234628392768 [INFO] UP on 127.0.0.1:9002
    2016-01-09 01:51:19,225 24425:140234628392768 [INFO] UP on 127.0.0.1:9003
    2016-01-09 01:51:19,225 24425:140234628392768 [INFO] UP on 127.0.0.1:9004

You start the server. In fact you start three servers: two WSGI applications,
and one buildin monitoring server. Look into
`dragon_on_wheels/__main__.py` for more details.

Right now you can call for statistics:

    $ netcat 127.0.0.1 9004
    SCGI_SERVER_Server_on_port_9003_error='Not enough data'
    SCGI_SERVER_uptime='14'
    SCGI_SERVER_uptime_str='14s'
    SCGI_SERVER_start_time='1452293569.68'
    SCGI_SERVER_pid='24544'
    SCGI_SERVER_start_at_asctime='Sat Jan  9 01:52:49 2016'
    SCGI_SERVER_version='1.1.1'
    SCGI_SERVER_online='0'
    SCGI_SERVER_requests='0'
    SCGI_SERVER_Server_on_port_9002_error='Not enough data'

You get statistics in `sh` format. After you preform a number of SCGI-requests, you
get more statistics like this:

    SCGI_SERVER_HG_error='Not enough data'
    SCGI_SERVER_LongPolling_online='0'
    SCGI_SERVER_LongPolling_online_time='30342.116116'
    SCGI_SERVER_LongPolling_online_time_average='18.3004319156'
    SCGI_SERVER_LongPolling_online_time_longest='50.0736629963'
    SCGI_SERVER_LongPolling_online_time_shortest='0.000838994979858'
    SCGI_SERVER_LongPolling_online_time_stddev='21.1128031609'
    SCGI_SERVER_LongPolling_online_time_str='08h 25m 42s'
    SCGI_SERVER_LongPolling_requests='1658'
    SCGI_SERVER_SCGI_online='0'
    SCGI_SERVER_SCGI_online_time='51.8729944229'
    SCGI_SERVER_SCGI_online_time_average='0.0211986082644'
    SCGI_SERVER_SCGI_online_time_longest='2.14451885223'
    SCGI_SERVER_SCGI_online_time_shortest='0.000619888305664'
    SCGI_SERVER_SCGI_online_time_stddev='0.146932912224'
    SCGI_SERVER_SCGI_online_time_str='51s'
    SCGI_SERVER_SCGI_requests='2447'
    SCGI_SERVER_online='0'
    SCGI_SERVER_pid='26436'
    SCGI_SERVER_requests='4105'
    SCGI_SERVER_start_at_asctime='Fri Nov 13 18:56:18 2015'
    SCGI_SERVER_start_time='1447430178.18'
    SCGI_SERVER_uptime='4863700'
    SCGI_SERVER_uptime_str='56d 07h 01m 40s'
    SCGI_SERVER_version='1.1.1'


Setup `nginx` as HTTP-frontend for SCGI server
----------------------------------------------

Example of part of `nginx` configuration file:

    server {
        server_name very_basic_scgi_server;
        listen 8001;
        location / {
            types {} default_type text/plain;
            return 200 "Nginx works!\nTry URLs /a, /b.";
        }
        location /a {
            include scgi_params;
            scgi_pass 127.0.0.1:9002;
        }
        location /b {
            include scgi_params;
            scgi_pass 127.0.0.1:9003;
        }
    }

If you `include` this file into `http {...}` section
of your main `nginx` configuration file, you get an
http-server on port 8001. Visit

- `http://127.0.0.1:8001/` (check nginx worked)
- `http://127.0.0.1:8001/a` (call SCGI server on 127.0.0.1:9002)
- `http://127.0.0.1:8001/b` (call SCGI server on 127.0.0.1:9003)

Now you get a full stack to run WSGI application.

    http://127.0.0.1:8001/a
       |
       |         http://127.0.0.1:8001/b
       |            |
       v            v
    .------HTTP(S)-----.
    |  .            .  |
    |  .    nginx   .  |
    |  .            .  |
    `--------SCGI------'
       |            |
       v            v
      port        port
    .-9002--------9003-.
    |                  |
    | dragon on wheels |
    |                  |
    `------------------'

You can write your own run-file with your own applications,
look into `dragon_on_wheels/__main__.py` for more code snippets.

In most cases, you need only one SCGI server, but you can
run a nmber of servers. For example: one for Django, and one
for low-level SCGI chat application.

Production `nginx` config
-------------------------

In production `nginx` configuration you have to keep in mind
security and safety `nginx` options. Like
`client_max_body_size`, `client_header_timeout`,
`client_body_timeout`, `send_timeout`... It is good idea
to protect your application on client side, using options like

    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";

Everybody knows the dangerous web app security risks.

Installtion
-----------

Previously you `Dragon_on_wheels` without installation. If you
are already satisfied, you can install it in your system by
standart way:

    sudo python2 setup.py install

Daemonization
-------------

First of all, you can create a special system user for SCGI server:

    useradd -m -g nobody -s /bin/true scgi

`Dragon_on_wheels` have not daemonization facilities. You can
use `nohup` in `rc.d`-script.
(Do not forget to drop privileges, using `su`/`sudo`.):

    start() {
      env --ignore-environment - \
      PYTHONPATH='...' \
      DJANGO_SETTINGS_MODULE='...' \
      su $USER -c "nohup YOUR_APPLICATION_SCRIPT >>$LOG_FILE </dev/null 2>&1 &"
      echo "$!" >$PID_FILE
    }
    stop() {
      kill "$(cat $PID_FILE)"
    }

Or you can get more modern way — `systemd`. The `.service`-script can
looks like this:

    [Unit]
    Description=Dragon on wheels SCGI server

    [Service]
    Type=simple
    # Environment="PYTHONPATH="
    # Environment="DJANGO_SETTINGS_MODULE="
    ExecStart=/usr/bin/python2 /home/scgi/apps/main_app.py
    ExecStop=/bin/kill $MAINPID
    User=scgi
    Group=nobody

    [Install]
    WantedBy=multi-user.target

Put it file to other `*.service` files. Usaly they places
into `/usr/lib/systemd/system`. Do no forget `systemctl daemon-reload`.

You can use many powerfull options of `systemd`: `PrivateNetwork=`,
`StandardOutput=`, `StandardError=`, `WorkingDirectory=`...
You may want to add `After=syslog.target` if you use `syslog` staff...
see `man 5 systemd.exec`
for mare details. And you can customise
Python Logging facilities. You can do it manually or using Djando
main configuration file.

How to run Django
=================

Easy as ordinary WSGI application:

    from django.core.servers.basehttp import get_internal_wsgi_application
    from dragon_on_wheels import WSGIServer, WSGI

    if __name__ == '__main__':
        WSGIServer([(
            ('127.0.0.1', 18008),
            WSGI(get_internal_wsgi_application(), 'SCGI', 10)
        )]).serve_forever()

This run-script runs Django as WSGI backend of SCGI server on `127.0.0.1:18008`
whith thread limit 10 and internal name `'SCGI'`.

You can combile Django applications with other WSGI application and `shell_stat`
buildin monitoring as shown before.

How to run Flask using `nginx`
==============================

Flask uses the Werkzeug routing system which founded on `PATH_INFO`
variable. Unfortunately, `nginx` does not provide `PATH_INFO`
variable in SCGI context by default.
So regular expression in location is work around. This is a
part of `nginx` configuration file:

    location ~ ^(?<script_name>/scgi)(?<path_info>/.*) {
        include scgi_params;
        scgi_param PATH_INFO $path_info;
        scgi_param SCRIPT_NAME $script_name;
        scgi_pass 127.0.0.1:9003;
    }

Everything else is configured as usual. If you Flask application
looks like this:

    from flask import Flask, request

    app = Flask(__name__)
    app.debug = True

    @app.route('/')
    def small():
        return 'Hello Flask!'

You can run it, using runscript like this:

    from dragon_on_wheels.server import Server
    from dragon_on_wheels.processors import WSGI, shell_stat

    from your_flask_module import app

    Server((
        (('127.0.0.1', 9003), WSGI(app, 'Flask_app_on_port_9003', 2)),
    )).serve_forever()

Of course, this is a minimal script. You can add `shell_stat`,
or customize logging.
