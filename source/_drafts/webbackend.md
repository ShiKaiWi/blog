---
title: webbackend
tags:
---
## ACC
1. join query
jobs = db.session.query(Job).filter(Job.user_id == User.id).\
                        filter(company_id == User.company_id).\
                        order_by(Job.created_at.desc()
2. requests
send a post request with json data, use this way:
requests.post(url, headers={'x-user': '2', 'x-corp': '0', 'content-type':'application/json', 'charset':'utf-8'}, json=input)

3. Mysql 是有 Json 类型的
4. difference between put and post and get
5. datetime timestamp unix—timestamp 的区别
6. json 解析返回数据 json.loads
7. sqlalchemy: 
    >On CentOS:
    >sudo yum install mysql-devel
    >sudo pip install MySQL-Python
8. python encode
9. os.path.basename("").startswith("")
## Question
1. python 的子类需要显式调用父类的 构造方法 吗？
2. python 的测试
3. 究竟在哪里比较适合做异常、错误检查？
4. python sys.path.append()