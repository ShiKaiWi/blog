---
title: ES6-异步编程
date: 2017-04-03 00:36:55
tags: Javascript 异步编程
---
## 异步编程
异步编程是 Javascript 的一大特色，因为 Javascript 是单线程工作，因此如果没有异步方式的话，基本上用户体验将会是无法忍受的。

因此 Javascript 的语法对异步的看重使得其对异步编程用了比较大的力气去优化，本文将会对直到 ES7 的异步编程方式进行总结：
1. Callback
2. Promise
3. Generator
4. asyn + await

但是在阐述这些方式之前，有一个概念需要事先阐述的是 Javascript 的事件循环。

### 事件循环(event loop)
event loop 是 Javascript 作为单线程语言完成非阻塞处理的重要机制，但其本身很容易理解，就是 Javascript 解释器的实现中会维护一个队列，task queue，当在执行语句中出现异步函数（比如 setTimeout）的时候，这样的函数是不会立即执行的，而是会被挂起，当空闲的时候，Javascript 解释器会处理这个异步操作，当处理完毕后，会在 task queue 里面插入一个事件，这个事件一般绑定了定义好的 callback。

下面是一个最简单的一个例子是：

```javascript
setTimeout(()=>console.log('World'), 0)
console.log('Hello')
// output: "Hello\nWorld" 
```

结果是在意料之中的，这是因为当调用 setTimeout 函数时，你即使设置了 timeout 是 0ms，callback 函数的执行仍然会被放入 task queue 里，等到当前的 call stack 被清空后（这里停止的时机我还不是很清楚，可能是 call stack 清空，但也可能是其他判定条件，比如跑了指定长度的代码）再回来从 task queue 里面取出最新的 event 来处理，也就是执行回调。

### 异步编程方式
有了 event loop 这个概念，那么对于操作异步函数就有帮助了，下面总结异步编程的方式，为了便于说明和调试，在需要使用异步函数的时候，本文都会使用 setTimeout 这个异步函数，其实本质上他和其他异步函数没什么区别，如果设置了 timeout 参数，就可看成其他异步函数的工作时间（这和 Java 中使用 Thread.sleep() 模拟线程运行是一个道理），下面会罗列目前 Javascript 的异步处理的几种常见的方式。

由于 setTimeout 的书写方式和正常异步函数不一致，此外不想在每次写 setTimeout 的时候，总是设置 timeout，所以先将其包装一下：

```javascript
var afunc = (callback) => setTimeout(callback,1000)
```
此外，需要强调的是，这里所说的是异步编程方式，而不是异步函数，所谓异步编程方式（Asynchronized Programming)是指编写含有异步函数的代码的方式。
#### Callback
所谓的 Callback 是最原始的方式，也就说说直接将 callback 函数作为异步函数的参数传入，比如：
```javascript
afunc(()=>{
    console.log("Hello");
    afunc(()=>{
        console.log("World");
        afunc(()=>console.log("!"));
    })
})
//output: Hello\nWorld\n!
```

当然如果写成原来的样子，应该是：

```javascript
setTimeout(()=>{
    console.log("Hello");
    setTimeout(()=>{
        console.log("World");
        setTimeout(()=>console.log('!'),1000);
    },1000)
},1000)
```

(之后就会直接使用 afunc)

可以发现这样写不很方便，而且很丑，于是在 ES6 中 Promise 应运而生。

#### Promise
Promise 会提供刚好的异步编程体验，同样的例子可以这么写：
```javascript
new Promise((resolve,reject)=>{
    afunc(()=>{console.log("Hello");resolve();})
}).then(()=>new Promise((resolve)=>afunc(()=>{console.log("World");resolve()})))
.then(()=>new Promise((resolve)=>afunc(()=>{console.log("!");resolve()})))
```
这样就写成了链式的调用，但看上去非常繁琐，实际上我们可以将 afunc 封装一下：(为了不起冲突，命名成 afuncp)
```javascript
var afuncp = (callback)=>{
    return new Promise((resolve)=>{
        setTimeout(()=>{
            callback();resolve()
            }, 1000);
    })
}

// then the statement can be expressed as:
afuncp(()=>console.log("Hello"))
.then(()=>afuncp(()=>console.log("World")))
.then(()=>afuncp(()=>console.log("!")))
```
是不是简洁多了？
这里的改写实际上和 fs 中的 readFile 和 fs-readfile-promise 类似。

但即使如此，还有更方便的写法。

#### Generator
如果能把异步编程的方式写成同步形式，那岂不是更加美观？

Generator 应运而生。

如果使用 Generator 的话，上面的写法将会变成：（注意这里使用的是 afuncp 而不是 afunc，当然使用 afunc 也是可以的，但是在下面要使用 Promise 的特性时就行不通了）
```javascript
function* genHelloWorld(){
    yield afuncp(()=>console.log("Hello"));
    yield afuncp(()=>console.log("World"));
    yield afuncp(()=>console.log("!"));
}

var g = genHelloWorld();
g.next()
g.next()
g.next()
```
但是这么写却是不对的，（你可以发现三个字符串是同时出现的）为什么呢？因为虽然通过利用 Generator 执行到下一个 yield 会停止的特性来做到了，这样顺序执行了三个异步操作，但是和之前两个异步操作不一样，因为我们之前写的异步操作是有先后关系的，后一个异步操作必须是在前一个异步操作完成之后才能执行的。

也就是说 Generator 其实本身不支持异步操作的依赖执行（就是前一个先执行了，才能执行下一个），但是具备记录上次执行位置和状态使得它有可能完成异步编程方式，而其所欠缺的只是一个使得依赖执行能够运作的机制（姑且成为依赖运行器）。

下面我们就来实现这个机制，这个机制的关键地方在于控制依赖，以及自动运行：
```javascript
function genController(gen){
    let g = gen();
    function next(){
        let res = g.next();
        if(!res.done){
            res.value.then(next);
        }
    }
    next();
}

// now let's run genHelloWorld
genContorller(genHelloWorld);
```
如果想在 production 环境中使用这样的机制，可以考虑 co 这个模块。

#### async + await
通过上面的例子可以看出来，Generator 虽然在表达异步编程上非常具有优势，但是容易发现需要自己定义依赖运行器，于是 async 函数应运而生，其本质还是 Generator 但是却自带了依赖运行器。
下面试试，async 的写法：
```javascript
async function genHelloWorld() {
    await afuncp(()=>console.log("Hello"));
    await afuncp(()=>console.log("World"));
    await afuncp(()=>console.log("!"));
}
genHelloWorld();
```
很完美！

#### Promise 的实现

之前有个工作上的前辈让我实现一个 Promise，叫我半个小时写出来一个有 resolve、then 功能的 Promise 类，结果我花了一晚上才实现出来。
代码如下：
```javascript
class PPromise {
    constructor(asyncF) {
        this.cb = null; 
        this.resolve = this.resolve.bind(this);
        this.then = this.then.bind(this);
        // convert resolve to async function calling
        asyncF.apply(null, [(data)=>setTimeout(()=>this.resolve(data),0)])
    }

    resolve(data) {
            var cb = this.cb;
            if (cb!==null)
                cb.apply(null,[data]);
    }

    then(cb) {
        var newPromise = new PPromise(()=>null);
        // link the next promise in the cb
        this.cb = (data)=>{
            var d = cb.apply(null,[data]) 
            newPromise.resolve(d); 
        }   
        return newPromise;
    }
}
```
实现的时候有两点需要注意的是：
1. new Promise((resolve)=>resolve(data)).then(console.log) 这个 resolve 调用是会被挂起的，这点也是这行代码 `asyncF.apply(null, [(data)=>setTimeout(()=>this.resolve(data),0)])` 的作用。
2. then 返回的是一个什么？ 答案是还是一个 Promise，这里的实现是返回一个新的 Promise 然后在当前 Promise 的 callback 中调用新 Promise 的 resolve 方法。