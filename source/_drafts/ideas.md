layout: ideas
title: ideas
tags: Log
date: 2017-03-12 12:42:08
---
## Accumulations
1. React 对 props 的某个属性进行 {} 分解取值，若该属性为 undefined 的话，会报出 "React component returning cannot read property '__reactInternalInstance$' of null"。
2. less+css modular 使用：如果直接使用 npm start 来编译得到的报错信息会有点奇观（不准确），理应使用 webpack 亲自打包
3. 使用 bootstrap3 的 modal
4. let i in array 中的 i 是字符串
5. 使用 function(){} 定义匿名函数会导致无法识别 this，可以使用 arrow function 来代替
6. sass 的 loader 和 less 的使用有区别
7. react 中的 input 标签 value 不要用 要用 defaultValue
8. this.props read only
9. 无法使用普通结点来进行 getElementById
10. vs code 的 jsconfig.json 中最后一个属性不要带逗号
11. jsconfig.json 和 eslint 的简单用法
12. 我遇到这样的一个问题，就是当使用 redux 的 connect 函数时，webpack 在打包的时候发现 setState 这个函数并没有被加入，最终我只是发现了这一原因，但是没有发现为什么会这样，只知道最终只是通过重新 `npm install react redux react-redux --save` 来解决了问题。
13. jquery 似乎会对结点元素进行某种处理，我在使用 jquery 操纵 x3dom 标签的时候发现并不能如期运行。
14. ES6 的语法过了一遍，但是还需要一个星期的时间来重新巩固一下
15. css 的模块化使用方法 less 的基本使用
16. webpack-server 结合 express 来得到一个实时保存更新的 server
17. eslint 的简单使用
18. vscode 的 jsconfig.json 的简单使用
19. redux 的 middleware，用来处理异步流
20. 笃行慎言

## Questions
1. 最顶层的元素设置 margin-top 不会影响父容器的高度？
2. 在 script 标签中，放入 static/xxx.js 和 /static/xxx.js 的区别？
3. dispatch 多个 action？
4. react 中组件有些状态与 view 无关，如何处理这样的状态？
5. react 组件构造时机以及过载出错的影响？
6. 在 ajax 请求中 setState 会立即更新组件但是若是此刻出错，那么就会无法得到出错信息！
7. 优雅地用数组给对象赋值
8. 正则匹配 匹配策略

# 02/26~03/03
## Accumulations
1. node 对象的 onclick 方法设置，两种，直接用 node.onclick 设置可以带参数，需要注意的是如果想要带参数，需要使用匿名函数
2. onclick 可以接收参数，该参数是触发的 node
3. V8 javascript engine 三个优势：hidden class, dynamic cached object's member, effient garbage collector
4. 动态加载 js 文件执行并放入 callback
5. onmousedown -> onmousemove -> onmouseup -> onclick onwheelmove (x3dom 可以优化的地方)

## Questions
### 1. 闭包的好处（函数名减少）
### 2. html 的 DOM 详解
### 3. html 的 事件触发流程
### 4. script 位置对执行的影响，以及执行的流程
### 5. git merge 时发生了什么?
发生 conflict 的情况有两种：一种是不同 branch 之间的 merge 时发生，还有一种是同一 branch 上由于同步开发，出现相同父节点上出现了两次不同的 commit（实际上只有本人和远程的差异，再具体点说就是合作者与自己拥有同一个父节点，并且在我提交下一个 commit 之前已经提交了一个 commit，这时候我发现无论我 pull 还是 push 都会出现 conflicts ）。
对于这种情况，首先我想强调的是，不必紧张，git 是会保存所有的东西的，你们所有的更改都会保存下来。

```
A -----> B1(sb else's commit) ---> C
|                                  | 
\                                  /
 ------> B2(your commit)----------
```

首先，你得了解你的 repo 处在什么状态——实际上是处于一个 merge 状态，这种状态你需要处理所有 unmerged file。
然后，你有两个选择，手动消除 unmerged 的地方，然后使用 `git add <file>` 来表示 merge 完毕，之后就可以提交新的 commit（需要注意的是这时的 commit 是一个 merge 类型的结点，它有两个父节点，这点下面会因此而出现意外情况）。在提交新的 commit 之前，你还可以使用 `git merge --abort` 来取消这次 merge。

但是如果出现这样的情况，merge 完毕后发现自己的 merge 做的有问题，不必担心，由上面的图可以知道，之前的冲突结点都保存着，那么该如何恢复呢？
很简单，通过 revert 恢复是最安全的方式（注意，revert 和 reset 不一样，reset 是恢复到参数指定的 commit 的状态，而 revert 是回滚指定 commit 的状态到上一次 commit）
但是如果你使用 `git revert <B2's SHA>` 会出 conflicts，这是因为你理解错了 revert 的含义（通过 git revert --abort 可以回滚）,而出现 conflicts 的原因是一般 revert 只会用作 `revert HEAD`，因此 git 知道回滚到当前 commit 的上一次 commit的方法，没有其他选择，若是回滚到指定版本的话，git 并不知道如何跨 commit 回滚，因此必须要人来手动 merge 一下。
在这里的情况我们得使用 `git revert HEAD`，但是即使如此，仍然不对，而且是出错，这是因为，回滚 C 的时候，发现 C 有两个父节点，因此必须指定回滚到哪一个结点才行，那么如何知道相应父节点的编号呢？通过 `git log` 即可查看父节点的顺序，有了顺序使用 `git revert HEAD -m <number>` 来回滚到指定的父节点（注意编号从 1 开始）。

# 03-05~03-11
## Accumulations
1. 看了 es5 的[博客](http://dmitrysoshnikov.com/ecmascript/chapter-7-2-oop-ecmascript-implementation/)，需要写一篇总结性的博客。
2. webpack file-loader 的使用在于可以打包文件到指定位置，此外利用好 webpack 的 publicPath 可以指定生成的文件（所有的文件，因此如果 file-loader 加入的目录，那么这个目录也会出现在 publicPath 下面）的位置，下面是一个简单的例子：
    ```javscript
    module.exports = {
        module: {
        loaders: [
                { test: /\.(png|jpe?g|gif|svg|woff|woff2|ttf|eot|ico)\??/,
                    loader: 'file?name=static/[name].[hash].[ext]'},

            ]
        },
    }
    ```
3. 写了两次 dropdown 的样式，总结一下思路：

    a. 基本结构是

    ```html
    <div class='dropdown'>
        <div class='dropdown-title'/>
        <ul class='dropdown-menu'>
            <li>...</li>
            ...
        </ul>
    </div>
    ```
    b. 唯一需要注意的是，可以通过 `background: url(...) no-repeat` 再加上相应的绝对定位来实现各种相应功能，此外用 js 动态改 style 可以使用 node.style.BackgroundImage = 'url(...)';
4. 学习了 display: flex 的布局方式，这种布局特别方便同一个 div 下的多个同级元素排列，推荐学习地址 [froggy flex](http://flexboxfroggy.com/)
5. 了解了 progressive web app 这个概念
6. React 的 setState 的工作原理是通过 merge 来达到新的状态的
7. 充分理解了 view 和 state 分离的好处
    
    所谓分离 view 和 state 的基本思想我个人感觉来自于 MVC，state 实际上意味着 Model，view 也就是 View，然后分离了 view 和 state，自然需要有单独的控制模块，也就是 Control，在 React 的设计模式中，view 负责根据 state（包括 props）来 render 出对应的 view instance，而 state 的设计属于 Model，而如何响应相应的事件来触发 state 的变化是需要自己来设计的（其实将 state 转换成 view 也是 control 的一部分，这部分 react 帮我们做好了），而这部分便是 control 的部分。

    react 做好了分离，但是比起 redux 这类状态管理器来说，缺少了**全局状态**这个概念，所谓全局状态实际上就是为了 web app 各个组件之间的交互而需要的，除此之外 redux 还将 control 部分抽离出来，让开发者集中管理。
8. react 的 diff 算法：基于了这样一个假设若是某个结点的类型不一致，那么以此为根的树基本上和之前不一致，此外通过强制让开发者提供同一级别的相同类型结点提供 local 的 key，来达到不必多次比较以发现前后乱序但一致的结点的效果

## Questions
### 1. 代理模式是什么？
### 2. js call 的用法？
### 3. js 如何在大型项目中，如何处理交流接口的难题？
尝试使用 typescript
### 4. react 多次 rendering？
### 5. react virtual dom 结点对 onclick 的影响？
### 6. react 属性 key 能否使用？
### 7. 如何高效地使用 css？
### 10. html css 的绘制流程？

## Plan
### 1: 看阮一峰的 es6 博客
### 2：学习 [virtual dom](https://github.com/Matt-Esch/virtual-dom)
### 3: bootstrap 的使用
### 4: less 的使用
### 5: eslint