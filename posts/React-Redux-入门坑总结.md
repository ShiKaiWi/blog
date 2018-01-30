>title: React-Redux 入门坑总结
>date: 2017-02-27 09:13:14
>tags: Web

## Abstract
我这个星期基本上在工作之余都在研究 React 和 Redux，我之前对这部分知识完全没用接触过，期间遇到很多坑，尤其是在想自己能够完成一个独立的比较小的 React App 的时候，发现出现了很多意想不到的事情，下面是我这个星期的总结。

注意，本文不是 React 和 Redux 的 tutorial，按道理讲，官方文档已经写的比较好了，但是对于新手来说可能不是很容易上手，因此，如果你看完了官方文档，在自己动手实现自己的第一个 React App 的时候，如果先看一下本文可能会得到一些启示，从而绕过一些坑。

文章分为两个部分，第一部分是关于 React 的内容，第二部分是关于 Redux 的内容（需要注意的是，React 和 Redux 不是必须一起使用的，实际上本文写的时候，Redux 已经有式微的趋势了）。

文中使用的原本 code 来自于 facebook 的 React 项目的 [tutorial](https://codepen.io/ericnakagawa/pen/vXpjwZ?editors=0010)。

## 阅读之前最好先看过……
1. React 的 [tutorial](https://codepen.io/ericnakagawa/pen/vXpjwZ?editors=0010)。
2. webpack 的简单介绍
3. Redux 的基础部分

## React
首先对 React 的特点做一个总结，React 是 facebook 推出的一个前端框架（注意前端不一定是指 web），其最大的特点在于，**视图组件化**。

我两年前（2015）的时候，还没有接触到 React 这种东西，那时候我只知道 Dom 编程，当时就感觉，开发前端页面非常繁琐，尤其是再结合 PHP 使用，其主要问题就是 JS 代码就是脚本，复用性不高，视图的响应逻辑逻辑很混乱，而 React 很好地解决了这个问题，通过将想要构建的视图直接分解成具有层级的组件，这样就可以大大提高视图组件的复用性，此外，每一个组件都具备相应的 props 和 state，前者是组件的属性值，后者是组件的状态，两者的区别就在于：前者是由父组件提供的组件属性（所以在组件内部是只读的），后者是私有的组件属性（用于保存这个组件的状态，从而实现自更新）:

```javascript
// 这是 ReactComponent.js 的一段代码
ReactComponent.prototype.setState = function (partialState, callback) {
  !(typeof partialState === 'object' || typeof partialState === 'function' || partialState == null) ? process.env.NODE_ENV !== 'production' ? invariant(false, 'setState(...): takes an object of state variables to update or a function which returns an object of state variables.') : _prodInvariant('85') : void 0;
  this.updater.enqueueSetState(this, partialState);
  if (callback) {
    this.updater.enqueueCallback(this, callback, 'setState');
  }
};
```

其中最重要的一段代码就是   `this.updater.enqueueSetState(this, partialState);`，可以看出来，当使用了 setState 后，便会将新的状态放入 updater 的更新队列中。


### 搭建起一个可以构建 React App 的本地环境
之所以会提到这一点，是因为 facebook 提供的 [starter code](https://codepen.io/ericnakagawa/pen/vXpjwZ?editors=0010) 是在线的版本，当你把代码复制到本地的时候，根本就用不了。

这时候必须使用到一个方便的工具了，叫做 [webpack](https://webpack.github.io/)，这是一个打包 js 代码的工具，通过简单的配置，便可以使用其将所有的 js 代码打包起来，比如叫做 _bundle.js_，然后直接在 _index.html_ 中引用这个脚本。

但是，仅仅如此还不够，因为上述代码使用的是 ES6 + JSX 的形式，因此必须还得配置好 webpack 的配置文件 _webpack.config.js_，在 webpack 这个工具之中有 loader 这个概念，loader 的意思其实就是解析其他形式的语言到 js 的形式，由第三方提供，在这里我们使用 babel 这个 loader，此外必须安装 babel 的另外两个 loader：
```bash
npm i babel-loader babel-preset-es2015 babel-preset-react babel-core -S
```
然后要在 _webpack.config.js_ 里配置好：

```javascript
module.exports = {
    entry:'./index.js',
    output:{
        filename:"bundle.js",
        path:path.resolve(__dirname,'dist')
    },
    module:{
        loaders:[
          {
            test: /(\.jsx|\.js)$/,
            loaders: 'babel-loader',
            query:{
                presets:['es2015','react','stage-0']
            },
          },
          {
            test: /\.scss$/,
            loaders: ['style', 'css', 'sass'],
          },
          {
            test: /\.html$/,
            loader: 'file?name=[name].[ext]'
          },
        ],

  }
};
```

### 使用 JSX 的注意点
JSX 其实就是将 html 的标签引入进了 js 中，但是在使用上也有必须要注意的问题，我是第一次使用 JSX，因此就遇到了一些问题。
1. JSX 本质上就是一个 expression，这一点很重要，因此它可以被 return 返回，可以用数组存储
2. JSX 的 tag 必须成对出现，这一点和 xml 的语法很像，不可省略（若是省略，首 tag 之后的内容会被认为全在 tag 之内）
2. JSX 中虽然可以通过 `{var}` 这样的方式，来加入上下文的出现的变量，但是在 JSX 的 tag 之间不能出现 expression 以外的 statement，这里之所以会提到这一点是因为想说不要试图通过在 tag 之间加入 for 循环来进行相同类型的 element 的生成（想要达到这一效果，可以使用数组来存储中间的 element，然后最后一起提供给 render 函数

### React 组件的书写
写 React 组件有两种方法：class 继承 或者 提供一个 function。

在使用 class 继承的时候，有一点必须要注意，class 是 ES6 的语法，因此必须使用 babel-ex2015 这个 loader 来解析，此外根据 es6 的语法，在 class 内部使用方法的时候，必须通过 `this` 来引用。

在使用 function 的时候，一种简洁的方法便是使用 arrow function，但是需要注意的是 arrow function 的时候，提供的参数只有一个，就是用来赋给 props 的，code 里面的例子：

```javascript
const Board = ({nextPlayer,squares,handleClick})=>{...}
```

### javascript 的自动插入 semicolon (ASI, auto semicolon insertion)
这一点是我这次过程中才发现的，真的让我很无力，关于这一点有很详细的文档记载，可以参考这个 SO [问答](http://stackoverflow.com/questions/2846283/what-are-the-rules-for-javascripts-automatic-semicolon-insertion-asi)，在这里我只想强调一点，就是关于 return 的 ASI：

```javascript
return
{
    a:1,
    b:2
}
// will be transformed to:
return ;
{
    a:1,
    b:2,
};
```

## Redux
Redux 的设计思想在我看来还是很先进的，在这里先以我的理解做一下简单的总结。

虽然说 React 和 Redux 和 React 没有必然联系，但是在我看来，没有类似于 React 的这种**视图组件化**的思想的话，那么 Redux 就是空中楼阁，Redux 的设计理念是对 React 的一大应用，它所做的事情其实就是将**视图的响应逻辑集中化**，React 组件在设计庞大之后，将会出现难以避免的视图响应逻辑复杂（复杂之处在于不同组件之间的交互），这也是为什么 React 的官方文档里总是提倡 **lift up state**，通过这样来避免小组件之间的通信。

在 Redux 的设计之外，有一个重要的理念，就是 Component 和 Container 的设计思想，这也是 Redux 官方文档推荐的一篇 [post](https://medium.com/@dan_abramov/smart-and-dumb-components-7ca2f9a7c7d0)。这和 React 的 **lift up state** 思想很相似，其实在最后所有的状态都集中到的那个 Component 就是这里的 Container，因此 Redux 在与 React 的结合使用中，你会发现，Redux 实际上将 state 从 Component 中抽离了，当然也并非存在于 Container，而是存在于全局，Container 只是访问全局 state 的地方而已，那么 UI 的更新又是如何做的呢？Redux 通过 state 的改变，然后将这种改变映射到 props 中去，然后会导致相应的 Component UI 发生变化。

### Redux 的流程
官方文档的 tutorial 写的很好了，但是我看完之后，真正轮到我实现的时候又变得懵逼了，究其原因其实在于不理解 Redux 的控制流程。

因此 Redux 的入门坑就在于如何正确理解它的控制流程，下面是我的理解：
state 作为存储于全局的变量，只要在一开始正确设置了 store，那么在这个 App 的内部任何地方都可以访问到 App 的状态（通过 `store.getState()`）

reducer 实际上就是做了一件事，描述了整个状态机，(previous state, action) => (next state)

在设计的时候，要分别实现相应的 Component 和 Container，其中 Container 中不要涉及 state 的访问，它对 Redux 是一无所知的，而 Container 负责做两件事，分别对应着两个个需要实现的函数：mapStateToProps 和 mapDispatchToProps。

其实这两个函数的名字可以任意取，但是这样取可以表明他们的含义，从名字可以看出它们都是给 Component 的 props 赋值，但赋值的对象和目的有所区别，前者负责描述 (current state) => (current props)，也就是在状态改变的时候如何更新 UI；后者做的是将 dispatch 动作赋值给 Component 的 props 中的事件属性，比如 onclick ，一般只会执行一次，用于触发 action，从而依据自定义的 reducer 推动 state 的更新。

因此，整个触发流程便是含有 dispatch action 的 onClick 被触发了，然后 reducer 指明了下一个 state，然后 mapStateToProps 被调用了，然后 Component 被重新绘制了。
