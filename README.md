## Chatti
匿名聊天室，能创建房间，并通过分享的url加入聊天  
仅为api部分，需要相应前端支持 (test.html仅作测试，功能不齐)

[Api文档](https://www.showdoc.cc/771889282903906?page_id=4283096614900797)

## 安装
- - -
在合适目录下执行：
>$ git clone https://github.com/Stareven233/Chatti.git  
>$ cd chatti  

安装依赖：
>$ python -m virtualenv venv  
>$ source venv/Scripts/activate  
>$ pip install -r requirements.txt  

数据库：
>安装redis并启动，可以去掉其持久化  

部署：
>安装并启动Nginx  
>代理"/"、"/socket.io"的5000端口  
>"/"需要设置proxy_set_header Host $host;  
>为"/static/"下的静态资源设置代理  


## 启动
- - -
>$ python chatti.py
