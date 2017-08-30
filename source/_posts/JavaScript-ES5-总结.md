---
title: JavaScript ES5 总结
date: 2017-02-17 00:05:46
tags: JavaScript ECMA
---

## Abstract
JavaScript 的语法让我感到非常不舒服，究其原因其实是因为两点：
1. 动态语言
2. 原型编程

对于动态语言，我个人始终认为是不符合大型 project 的要求的，因为动态语言的特性导致阅读代码的时候非常不顺利，比如你看到一个 function 的参数时候，你完全不知道它是怎样的结构，但是像 Java 这样的强类型语言，每一个参数都有类型，就使得对于每一个参数你都知道它实实在在的含义（可以去查看参数类型的定义）。
此外原型编程，我迄今看不出其优势所在，不仅每一个对象的原型都可以被随意改变，而且根本没有访问控制。

但尽管如此，我个人认为 JavaScript 还是更加现代化的编程语言，比如它的 function 可以作为对象任意传递，这一点和 Python 类似，对于异步编程可以说是非常直观地支持。
然而 JavaScript 的发展在 2015 年 ES6 发布后，就迎来了非常大的增强，我想为了更好的学习 ES6，对之前版本的深层次的理解还是需要的，相当于打好基础才能更好地前进。
在本篇 post 中，我主要是对自己看过的 Dmitry Soshnikov 的一系列关于 ES3-ES5 的 [posts](http://dmitrysoshnikov.com) 总结，主要包含 JavaScript 中最迷惑人的两个部分：
1. 变量管理
2. 原型编程

## 变量管理
这里使用的变量管理并不是指硬件层面的实现，而是指 JavaScript 的变量存储的抽象模型。另外，在概念上，ES3 和 ES5 有着几个区别，因此会分别描述。
### ES3
#### Execution Context(EC)
在 JavaScript 中有两种 EC：global context 和 function context。
不同的 context 的管理是用 stack 模式管理的，举个例子，在 global context 下定义了一个 function func，那么整个 EC stack 就是：
```
EC Stack = {
    funcContext,
    globalContext,
}
```
如果从 funcContext 退出那么，EC Stack 将会只剩下 globalContext，符合 Stack 的管理方式。
EC 有着许多重要的 property，用以在运行时使用，而在本篇 post 中，着重强调变量管理这一个问题，因此会探究其相关属性。

#### Variable Object(VO) / Activation Object(AO)
VO 和 AO 其实类似于符号表(symbol table)，用以集中管理变量，并且这是 EC 的属性，在 ES6 之前是没有 var 之外的变量定义方式的(有隐式定义变量，下面会提到)，而对 var 的处理会在**静态分析**进行，并且将定义的变量名填入 VO/AO，但是并不会直接对其赋值，而是等到执行到赋值语句的时候才会：
```javascript
// now VO = {
//     a: undefined,
// }

console.log(a); // undefined
var a = 13;

// now VO = {
//     a: 13,
// }
```
这里既然都是符号表，为什么有 VO 和 AO 的区别呢？
VO 其实是指 global context 的符号表，而 AO 是指 function context 的符号表，之所以有这两者的区别是因为 function context 有着不一样的符号管理，总共包括三类符号：

1. arguments：即 function 的参数
2. functions：function 内部定义的 function，在静态分析期间，如果符号与 arguments、variables 中的有冲突，直接替代(function 提升)
3. variables：function 内部定义的变量，如果和 1、2 有冲突，在静态分析期间不会造成影响，在执行期间会直接替代 1 中的冲突项(理所当然的，后来覆盖)，与 2 的互相替代也符合后来覆盖原则

直接看一个例子就知道区别了：
```javascript
function func(f){
    console.log(f);
    var f = 4;
    function f(){}
    console.log(f);
}
func(3);
// output:
// [Function: f]
// 4
```
这段的最后还要说明一下隐式声明的问题，上面提到如果直接给一个变量赋值(不用 var)也是可以的，但是其实不是向 VO 中添加符号，而是给当前的 EC 下的 this 变量添加了一个属性而已。
看下面的例子：
```javascript
x = 3;
var a = 4;
delete a;
delete x;
console.log(a); // 4
console.log(x); // Reference Error
```

### Scope Chain(SC)
按道理说有了 EC 和 VO，那么便可以在任何一个特定的 EC 下进行变量访问，但是如果出现当前变量无法再当前 EC 下找到，那么该如何处理呢？为了解决这种情况，SC 被引入自然是很正常的事情，而 SC 和其他语言的构造方法基本一致：
```javascript
SC(ECStack[top]) = VO/AO + SC(ECStack[top-1]);
ECStack[0] === globalContext;
```
但需要注意的是，JavaScript 并没有 block 的概念，这是和其他主流语言的最大区别之一，也正因为如此只有 function 才能创造新的 context，因此常常会说一个 function 的 SC，但实际上是 EC 的 SC。因此对于 function 中的变量解析，自然是很重要的，但其实也很简单，只需要注意一点 **function 的 SC 是静态分析确立的**，会在运行前把需要用的变量的 Reference 记录下来：
```javascript
var x = 3;
function func(){
    console.log(x);
}
func(); // output: 3
x = 4;
func(); // output: 4
```

此外，with 和 catch 会把其引入的变量加入到当前 SC 的最前面:
```javascript
function func(){
    var obj  = {
        x: 3,
    }
    var x = 4;
    with(obj){
        console.log(x);
    }
}
func();// output: 3
```

还有一点比较重要的是，因为 JavaScript 的有着 prototype，因此当顺着 SC 找到最后，可以访问到 Object 的 prototype 上去，可以看下面这个例子：
```javascript
function foo() {
  console.log(x);
}
Object.prototype.x = 10;
foo(); // 10
```
#### 属性访问
讲到这里，有了 EC、VO、SC，我们看似便可以对几乎所有的变量进行访问了，但是还有一种情况没有考虑，那就是 object 的属性访问，而在属性访问中，还有一个特别的例子，就是 this 的属性访问。
##### Reference Type(RT)
属性访问问题解决的本质其实在于如何定义这样的访问方法，而 JS 的做法是通过 RT 来解决，RT 的产生只在两者情况下：

1. 处理变量名(identifier)[这里表明，普通变量的访问其实也是通过 RT 来解决的]
2. 处理属性访问符(property accessor)

而 RT 的基本结构如下：

```javascript
var foo = 3;
// fooReferenceType = {
//    base: null,  => null will be transformed to globalContext's VO
//    propertyName: foo,
//}
```

当引用 foo 变量的时候，首先便会得到一个 fooReferenceType，然后每一个 RT 都有一个获取属性值的方法(GetValue)，这样就解决了属性访问的问题(其实说到可以发现，JS 里所有的变量访问都是属性访问，只不过没有指定 object 的地方基本上使用的 SC 上一层 VO/AO)。
##### this 绑定
this 的使用一般是如下情况：

```javascript
function func() {
    console.log(this.x);
}
var obj = {x:1};
obj.func();
```

这里在 func 的内部如何知道 this 这个 object 是什么呢？这里就涉及到了 this 的 binding 问题。
其实 this 的绑定规则很简单，可以这么说 **this 的绑定完全由 function 的调用方式决定**，这是因为 this 绑定的 object 就是 **function 前面的变量的 RT 的 base**。

```javascript
var obj1 = {
    x: 1,
    func:function() {
        console.log(this.x);
        },
};
var obj2 = {
    x: 2,
    func: undefined,
};
obj1.func(); // output 1
obj2.func = obj1.func;
obj2.func(); // output 2
(obj2.func = obj1.func)(); // output undefined
```

这是一个很经典的例子，1 和 2 的输出根据上面的理论是理所当然的结果，但是最后一个 undefined 的结果可能就有点令人费解了。它背后的机制是这样的，`(obj2.func = obj1.func)` 括号内一个表达式，并不是一个变量名(identifier)，当然也不是属性访问器(property accessor)，因此对它解析不会产生 RT，也因此其 this 的绑定为 null，而 null 作为 this 的值在 non-strict 模式下是会被转化成 globalContext 的 VO 的。

## ES5
### Call Stack
将 EC 的称谓正式变为 Call Stack，本质并没有太多变化。
### Environment
ES5 管理变量的方式发生了比较大的变化，首先不在使用 VO 和 AO 了，统一成了 Environment，但是 Environment 分为两类，Variable Environment(VE) 和 Lexical Environment(LE) 两种，但是和 VO/AO 的分类并没有直接关系，其实 VE 本质上和 ES3 中的 VO/AO 是同一个东西，负责管理所有的变量访问，LE 的提出是为了解决这样一个特定问题：**with 下的 function expression 中的变量访问**：
```javascript
var x = 1;
function foo() {
    console.log(x);
}
 
with ({x: 2}) {
    // this is a function expression
    var bar = function () {
        console.log(x);
    };
    foo(); // 1, from VariableEnvrionment
    bar(); // 2, from LexicalEnvrionment
}
foo(); // 1
bar(); // still 2
```
其实一般情况下，LE 只是 VE 的一个复制值，但是当出现例子这种情况的时候，必须在不破坏 VE 的情况下(因为 `foo` 的调用需要用到 `x = 1`)，同时提供另一套 `{x: 2}` 会被先访问的 Environment(`bar` 的调用要用到 `x:2`)，于是会在进入 with block 的时候，保存好当前的 LE，同时改变 LE 为需要的 LE，在 with block 结束的时候恢复。
### Enviroment Record(ER)
每一个 Environment 的结构会包含一个 ER 以及一个 outer，outer 其实就是上一层的 Environment，这点和 SC 很类似，不过是不完全一样的，下面的一个例子可以说明问题：
```javascript
var x = 1;
function func() {
    var y = 2;
}

globalEnvironment = {
    environmentRecord: {
 
        // built-ins:
        Object: function,
        Array: function,
        // etc ...
    
        // our bindings:
        x: 1,
        func: function,

    },
 
    outer: null // no parent environment
 
};
 
// environment of the "foo" function
 
fooEnvironment = {
    environmentRecord: {
        y: 2,
    },
    outer: globalEnvironment
};
```

也许你有这样的疑惑，为什么需要做这样的改变呢？
答案是为了 Efficiency！
需要提到的是，规定(specification)并不提倡将 ER 实现为一个 simple object，这意味着各大 Engine 在这里可以提供自定义的优化！仔细想一想就会发现 SC 的设计会导致一层一层地查找某个变量，这个效率实在是太过低下，为什么不把会用到的变量放入当前 ER 中以提供直接的访问？此外还可以将不用到的变量不保存，这两点可以通过静态分析做到，V8 Engine 却是也是这样做的。
此外 environment record 有两种类型 decorative environment record(VER) 和 object environment record(OER)，两者的区别在于前者处理 function activition 以及 catch 时的 environment record(相当于以前的 AO)，后者用于处理 global context 下的 function、variable 以及 with 语句下的变量 binding，这只是规定(specification)上的区别，在实际实现中，并没有这个标志来指定 ER 的区别。

## 原型编程
### \_\_proto__ 和 prototype 的区别
在阐述原型之前，必须先澄清这两个概念的区别，其实说穿了也很简单，一个 object 的原型实际上就是 \_\_proto__，那么 prototype 又是什么呢？
直接看如下一个例子：

```javascript
function Constructor() {
    this.x = 3;
}
Constructor.prototype. y = 4;
var obj = new Constructor();
console.log(obj.__proto__ === Constructor.prototype) //true
console.log(obj.x, obj.y) //3, 4
```
看到这里你就知道了，当使用 `new Cnostructor()` 来创建对象的话，那么 Constructor 的 prototype 便会是新创建对象的 \_\_proto__。
值得注意的是，上面这个例子中，x 和 y 的查询是不同的，x 属于 obj 自己的属性，而 y 是属于其原型的属性。

因此一般说来，prototype 是 function 才有的属性，而所谓的原型编程实际上就是指使用 function 来进行 \_\_proto__ 的创建与传递。

另外，这里给出 Object 和 Function 的 \_\_proto__ 和 prototype:（注意 Object 和 Funtion 都是 function 类型的）

```nodejs
> Function.__proto__
[Function]
> Function.__proto__.__proto__
{}
> Function.__proto__.__proto__.__proto__
null
> Object.__proto__
[Function]
> Object.__proto__.__proto__
{}
> Object.__proto__.__proto__.__proto__
null
> Function.prototype
[Function]
> Object.prototype
{}
```
### 使用 prototype 来进行面向对象编程
在 ES6 之前，并没有 class 的对象，但即使到了 ES6，所谓的 class 不过是 syntax sugar，本质其实还是 prototype 编程。
面向对象的三大特点：封装、继承、多态，下面依次阐述。
#### 封装
这个现在即使在 ES6 也没有很好地解决办法，目前所知道的方法有两种
1. ES7 中出现以 # 表示私有属性
2. 此外使用 ES6 的 Symbol 也可以达到模拟私有属性的效果

#### 继承
这个在 ES6 之前的版本，其实是有方法进行继承模拟的，可以看下面的一个例子：

```javascript
function SupCls() {
    this.x = 1;
}
SupCls.prototype.y = 2;
var supCls = new SupCls();
console.log(supCls.x, supCls.y);
// output: 1, 2

// now we will make an inheritance
function SubCls() {
    this.z = 3;
}
SubCls.prototype = new SupCls();
SubCls.prototype.constructor = SubCls;
var subCls = new SubCls();
console.log(subCls.x, subCls.y, subCls.z);
// output: 1, 2, 3
console.log(subCls.__proto__);
// output: SubCls { x: 1, constructor: [Function: SubCls] }
console.log(subCls.hasOwnProperty('x'));
// output: false
```

这里解释一下最关键的一步，`SubCls.prototype =  new SupCls()`，这可以使得新创建的 subCls 的 \_\_proto__ 是 SupCls 的 prototype，从而使得其具有父类的属性。

除此之外还有一个令人迷惑的地方就是，为什么需要做 `SubCls.prototype.constructor = SubCls`？其实这步对于结果来说无关紧要，只是将 SubCls 的原型中的 constructor 指向正确的地方，如果没有这一步，上面的结果依然如此，也就是说 new 不会根据 prototype 的 constructor 来改变其行为，constructor 的存在只是给生成的 object 添加一个正确的引用。

其实这里有一个陷阱，那就是最后一条语句表明，x 不是 subCls 的instance属性！为什么会这样其实很好理解，因为 x 根据我们的做法是属于 SubCls 的 prototype 的属性，自然也是属于 subCls 的 \_\_proto__ 属性。

那么如何解决这个问题呢？
其实很简单，无非就是把 SupCls 中的 this 换成我们想要的，也就是 SubCls 中的 this，做一次 binding 就行了。

看下面的实现方式:

```javascript
function SupCls() {
    this.x = 1;
}
SupCls.prototype.y = 2;
var supCls = new SupCls();
console.log(supCls.x, supCls.y);
// output: 1, 2

// now we will make an inheritance
function SubCls() {
    this.z = 3;
    // binding is done here
    SubCls.supertype.constructor.apply(this);
}
SubCls.prototype = new SupCls();
SubCls.prototype.constructor = SubCls;
SubCls.supertype = SupCls.prototype;
var subCls = new SubCls();
console.log(subCls.x, subCls.y, subCls.z);
// output: 1, 2, 3
console.log(subCls.__proto__);
// output: SubCls { x: 1, constructor: [Function: SubCls] }
console.log(subCls.hasOwnProperty('x'));
// output: true
```

也许你以为到这里就解决问题了，但实际上还有一个问题！
你可以发现，SupCls 这个 function 被调用了两次，而这个是可以避免的，为什么这么说？我们看这两次的调用时机：
1. `SubCls.prototype = new SupCls();`
2. `SubCls.supertype.constructor.apply(this);`

明显可以发现第一次的调用其实没有必要，因此第一次的调用我们只是想要拿到 SupCls 的 prototype 信息，而不是以它为 constructor 创建的 instance 信息，所以为了避免这个，我们可以这样来结束讨论：
```javascript
function SupCls() {
    this.x = 1;
}
SupCls.prototype.y = 2;
var supCls = new SupCls();
console.log(supCls.x, supCls.y);
// output: 1, 2

// now we will make an inheritance
function SubCls() {
    this.z = 3;
    // binding is done here
    SubCls.supertype.constructor.apply(this);
}

// new part start
function middleConstructor() {}
middleConstructor.prototype = SupCls.prototype;
SubCls.prototype = new middleConstructor();
// new part end

SubCls.prototype.constructor = SubCls;
SubCls.supertype = SupCls.prototype;
var subCls = new SubCls();
console.log(subCls.x, subCls.y, subCls.z);
// output: 1, 2, 3
console.log(subCls.__proto__);
// output: SubCls { x: 1, constructor: [Function: SubCls] }
console.log(subCls.hasOwnProperty('x'));
// output: true
```

也许有人会有这样的疑惑，为什么不直接将 SupCls 的 prototype 赋给 SubCls 的 prototype，对此，我表示你自己一试，想一下就知道了原因了。

根据 Dmitry Soshnikov 的说法，ES6 class 的继承就是通过这样的方法实现的，不过我认为应该还是有出入的，这个还需要仔细探究一下。