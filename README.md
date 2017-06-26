# OMS环境需求:
<pre>
python 2.7.x
django 1.7.11
</pre>

# salt_api.conf：
<pre>
external_auth:
  pam:
    test:
      - .*
      - '@wheel'
      - '@runner'
      - 'grains.*'
      - 'status.*'
      - 'sys.*'
      - 'test.*'

rest_cherrypy:
  port: 7000
  host: 0.0.0.0
  ssl_crt: /etc/ssl/private/cert.pem
  ssl_key: /etc/ssl/private/key.pem
  webhook_disable_auth: True
  webhook_url: /hook
</pre>
