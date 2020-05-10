## Chatti
匿名聊天室，能创建房间，并通过分享的url加入聊天  
仅为api部分，需要相应前端支持 (test.html仅作测试，功能不齐)  

[Api文档](https://www.showdoc.cc/771889282903906?page_id=4283096614900797)  

## 安装
- - -
在合适目录下执行：
>$ git clone https://github.com/Stareven233/Chatti.git  
>$ cd chatti  

安装依赖 - windows：
>$ python -m virtualenv venv  
>$ source venv/Scripts/activate  
>$ pip install -r requirements.txt  

安装依赖 - ubuntu：
>$ virtualenv -p /usr/bin/python3 venv  
>$ source venv/bin/activate  
>$ pip3 install -r requirements.txt  

数据库：
>安装redis并启动，可以去掉其持久化  

部署 - ubuntu：
- apt安装nginx  
    - "/"设置index指令  
    - 代理"/static"下的静态资源  
    - 代理 "/v1"、"/socket.io"的5000端口  
- pip安装gunicorn
    - 需要配置worker_class='eventlet'  
- apt安装supervisor
    - 在/etc/supervisor/conf.d下创建配置文件  
    - supervisorctl update更新配置  

## 启动
- - -
windows：
>$ python chatti.py  

ubuntu：
>$ supervisorctl stop Chatti  

