import multiprocessing
debug = True
loglevel = 'debug'
bind = '127.0.0.1:8080' # 绑定与Nginx通信的端口
# pidfile = '/var/run/gunicorn.pid'
# accesslog = '/var/log/gunicorn_acess.log'
# errorlog = '/var/log/gunicorn_error.log'
workers = multiprocessing.cpu_count() # * 2 + 1
worker_class='eventlet'
