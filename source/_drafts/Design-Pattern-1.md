---
title: Design-Pattern-1
tags: Design-Pattern ES6
---

## some functions
模拟耗时操作
```javascript
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function work(ms) {
  console.log('Taking a break...');
  await sleep(ms);
  console.log('Two second later');
}
```

demo();
## Decorator
```javascript
function decorator(func) {
    function tfunc(){
        console.log("##decorator##");
        func.apply(undefined, tfunc.arguments);
    }
    return tfunc;
}

function func(s1, s2) {
    console.log(s1, s2);
}

decorator(func)("Hello, World");
```

Memorizer

```javascript
function memorizer(func, hashFunc) {
    let memorizer = {};
    function run() {
        let inputs = run.arguments;
        let keyString = '';
        for(let index in inputs) {
            if (inputs.hasOwnProperty(index)){
                keyString += inputs[index];
            }
        }
        let key = hashFunc ? hashFunc.apply(undefined, inputs) : keyString;
        return memorizer[key] || func.apply(undefined, inputs);
    }
    return run;
}

function addTwoNum(a,b) {
    return a + b;
}
```

## Proxy
### What
Requests =-=-=-=-=-=-=-=-=-=> Instance
    \=========> Proxy ==========/
也就是说 Proxy 可以被外界当作 Instance 来使用，从而达到在外界不知道 Instance 的情况下，完成了需要 Intance 的任务。

### Why
那么究竟为什么需要使用 Proxy 来代替 Instance 来做到这一点呢？
结合具体场景大概有这么几种情况下，Proxy 的值得使用：
1. Remote Proxy: 这种情况下实际上是对远程通信的一种封装，当然远程通信的服务端使用的也是 oop 思想，在约定好通信规则后，便可以通过 remote proxy 在本地完全无需感知 remote instance 的情况下，直接完成相应的任务
2. Virtual Proxy: 这种情况一般是指 Instance 的创建过程比较耗时，因此通过 Proxy 来做到 create on demand
3. Protection Proxy: 当 Instance 存在访问权限的时候，可以通过 Proxy 来做，也就是把访问的控制逻辑放在 proxy 中S
4. Smart Reference： 当需要在访问 Instance 的时候进行某些功能增强，可以通过 Proxy 来做，个人觉得，这点包含了第三点

# Behavior Pattern
## Command
类似于 callback，用于处理事件响应，比如一个 app 的 button 的 onClick 事件被触发了，那么如何处理 onClick 这个事件呢？
使用 Command 模式的话，就会使用 Command 这个类来封装这个事件的处理，这个 Command 类包含方法 execute，其中会绑定一个 receiver，也就是这个命令的接受者，并且定义了 receiver 的响应逻辑。
举个 OpenCommand 的例子，用户点击了 open button，那么 OpenCommand 的 execute 方法就会被调用，那么怎么实现这个 execute 方法呢？
```javascript
class OpenCommand extends Command {
    constructor(app) {
        this._app = app;
    }

    execute() {
        const file = askUserForDocName();
        if (file) {
            this._app.openDoc(file);
        }
    }
}
```

