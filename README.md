# OMS环境需求:
<pre>
python 2.7.x
django 1.7.11
requests
IPy
PyYAML
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
# 创建数据库及创建用户
<pre>
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
</pre>

# 通过salt-api添加服务器
![salt-minion](images/5DE3EB0E-6582-4E1D-8411-1FB0065C5C26.png)
![accept_key_1](images/1562F3E5-3788-4A47-A913-D3BE1D0FB7EA.png)
![accept_key_2](images/99035F49-DD81-40BC-B7A9-27969212522D.png)

# 系统设置
# git仓库设置
# saltstack功能介绍
# 安装软件包
