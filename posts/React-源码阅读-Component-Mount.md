---
title: React-源码阅读-Component-Mount
date: 2017-07-01 00:06:29
tags: react
---
## Mount 一个 Component
### callstack
ReactDomStackEntry => ReactMount => InstantiateReactComponent => CompositeComponent

### ReactMount
Interfaces:
1. scrollMonitor
2. renderSubtreeIntoContainer
3. render
4. unmountComponentAtNode

### _renderNewRootComponent
1. 检查
2. call instantiateReactComponent 得到 componentInstance
3. call ReactUpdates.batchedUpdates

然后 ReactUpdates.batchedUpdates 会 call batchingStrategy.batchedUpdates，而这个实际上是在 call 一个在 ReactUpdates.injection 中注入 batchingStrategy，而实际上注入的是 ReactDefaultBatchingStragety，里面实际就是一个 transaction，并且除了一些特殊的初始化工作，就是调用了传给 ReactUpdates.bacthedUpdates 的 callback
而这个 callback 是：batchedMountComponentIntoNode

### batchedMountComponentIntoNode
1. 实例化一个 ReactUpdates.ReactReconcileTransaction
2. 然后 perform mountComponentIntoNode, 会传入 transcaction 和 instance

这里需要了解一下 ReactUpdates.ReactReconcileTransaction, 这个变量和 ReactUpdates.batchUpdates 一样都是动态注入（其实我不明白为什么要这样做），默认的注入是在 ReactDomStackInjection 里面做的，里面做了大量的 transaction 必要的注入，此外还使用 pooledClass wrappert 一下来提升性能。

和 batchingStrategy 一样，主要其实还是调用 callback。

不过这个 transaction 的调用是这样的：

```javascript
transaction.perform(
    mountComponentIntoNode,
    null,
    componentInstance,
    container,
    transaction,
    shouldReuseMarkup,
    context,
  );
```
也就是说把自己作为参数传给了 mountComponentIntoNode

### mountComponentIntoNode
1. call ReactReconciler.mountComponent 产生 markup
2. 设置 `wrapperInstance._renderedComponent._topLevelWrapper = wrapperInstance`
3. call _mountImageIntoNode 传入产生的 markup

这里需要知道 ReactReconciler.mountComponent 是做什么的。
```javascript
mountComponent: function(
    internalInstance,
    transaction,
    hostParent,
    hostContainerInfo,
    context,
    parentDebugID, // 0 in production and for roots
  ) {
    if (__DEV__) {
      if (internalInstance._debugID !== 0) {
        ReactInstrumentation.debugTool.onBeforeMountComponent(
          internalInstance._debugID,
          internalInstance._currentElement,
          parentDebugID,
        );
      }
    }
    var markup = internalInstance.mountComponent(
      transaction,
      hostParent,
      hostContainerInfo,
      context,
      parentDebugID,
    );
    if (
      internalInstance._currentElement &&
      internalInstance._currentElement.ref != null
    ) {
      transaction.getReactMountReady().enqueue(attachRefs, internalInstance);
    }
    if (__DEV__) {
      if (internalInstance._debugID !== 0) {
        ReactInstrumentation.debugTool.onMountComponent(
          internalInstance._debugID,
        );
      }
    }
    return markup;
  }
```
这里可以看到是把 mount 的工作 delegate 给了 internalInstance.mountComponent, 所以我们还得去看 ReactComponent.mountCompoent 方法, 然而 react 内部其实没有 ReactComponent 这个类，看着它的 type 定义发现 ReactBaseClasses 是 React.Component, 但是又发现这个类，并没有什么 mountCompnent 定义，并且很多函数的定义都是 dummy 的（这里有点不明白），于是我想这应该是一个基类定义吧，然后我又找到了 ReactDOMComponent，这个似乎才是真正会使用到的 ReactComponent。

在 mountComponent 中做了很多具体的工作，总结来说就是产生具体的 html element:

```javascript
if (!tagContent && omittedCloseTags[this._tag]) {
        mountImage = tagOpen + '/>';
      } else {
        mountImage = tagOpen + '>' + tagContent + '</' + type + '>';
      }
}
```

值得一提的是，这个 mountImage 的含义是 html 内容的意思，并且还是 string 类型的，然后:

```javascript
/**
   * Generates root tag markup then recurses. This method has side effects and
   * is not idempotent.
   *
   * @internal
   * @param {ReactReconcileTransaction|ReactServerRenderingTransaction} transaction
   * @param {?ReactDOMComponent} the parent component instance
   * @param {?object} info about the host container
   * @param {object} context
   * @return {string} The computed markup.
   */
  mountComponent: function(
    transaction,
    hostParent,
    hostContainerInfo,
    context,
  ) {
      //...
  }
```

注释里面表明 markup 也是类似的含义。

### _mountImageIntoNode
会根据 shouldReuseMarkup，
**true**：
获取 rootElement，call ReactMarkupChecksum 传入 markup， rootElement，如果返回 true，意味着可以使用 `ReactDOMComponentTree.precacheNode(instance, rootElement)` 来做到快速 mount，然后直接返回，所用的工作就算完成了。

这里需要知道 React.MarkupChecksum.canReuseMarkup 的实现：
```javascript
/**
   * @param {string} markup to use
   * @param {DOMElement} element root React element
   * @returns {boolean} whether or not the markup is the same
   */
  canReuseMarkup: function(markup, element) {
    var existingChecksum = element.getAttribute(
      ReactMarkupChecksum.CHECKSUM_ATTR_NAME,
    );
    existingChecksum = existingChecksum && parseInt(existingChecksum, 10);
    var markupChecksum = adler32(markup);
    return markupChecksum === existingChecksum;
  }
```
这里一目了然，对于react render 出来的 element 肯定会把一个 checksum 存到  ReactMarkupChecksum.CHECKSUM\_ATTR_NAME 中去。

这里还需要知道 ReactDOMComponentTree.precachedNode 的具体实现：

```javascript
/**
 * Drill down (through composites and empty components) until we get a host or
 * host text component.
 *
 * This is pretty polymorphic but unavoidable with the current structure we have
 * for `_renderedChildren`.
 */
function getRenderedHostOrTextFromComponent(component) {
  var rendered;
  while ((rendered = component._renderedComponent)) {
    component = rendered;
  }
  return component;
}

//...

/**
 * Populate `_hostNode` on the rendered host/text component with the given
 * DOM node. The passed `inst` can be a composite.
 */
function precacheNode(inst, node) {
  var hostInst = getRenderedHostOrTextFromComponent(inst);
  hostInst._hostNode = node;
  node[internalInstanceKey] = hostInst;
}
```

这里非常需要知道 inst._renderedComponent 是什么。
我找来找去发现，一个 instance 的 _renderedComponent 是在 ReactCompositeComponent 中赋值的：
```javascript
performInitialMount: function(
    renderedElement,
    hostParent,
    hostContainerInfo,
    transaction,
    context,
  ) {
    // If not a stateless component, we now render
    if (renderedElement === undefined) {
      renderedElement = this._renderValidatedComponent();
    }

    var nodeType = ReactNodeTypes.getType(renderedElement);
    this._renderedNodeType = nodeType;
    var child = this._instantiateReactComponent(
      renderedElement,
      nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
    );
    this._renderedComponent = child;

    var debugID = 0;
    if (__DEV__) {
      debugID = this._debugID;
    }

    var markup = ReactReconciler.mountComponent(
      child,
      transaction,
      hostParent,
      hostContainerInfo,
      this._processChildContext(context),
      debugID,
    );

    if (__DEV__) {
      if (debugID !== 0) {
        var childDebugIDs = child._debugID !== 0 ? [child._debugID] : [];
        ReactInstrumentation.debugTool.onSetChildren(debugID, childDebugIDs);
      }
    }

    return markup;
  }
```
这段代码可以说是相当顶层的调用，所以不用太深入去看（因为我们正在一个 call stack 的追踪当中），记住我们的目的是要找到 _renderedComponent 的赋值语句，发现是：

```javascript
if (renderedElement === undefined) {
      renderedElement = this._renderValidatedComponent();
    }

var nodeType = ReactNodeTypes.getType(renderedElement);
this._renderedNodeType = nodeType;
var child = this._instantiateReactComponent(
    renderedElement,
    nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
);
this._renderedComponent = child;
```
（其实 renderedElement 是由 this 的 \_constructComponent 函数生成的一个 ReactComponent Instance，所以之后用 this._instantiateReactComponent 生成出来的是 child，这个下面会仔细提到）
它存储了一个 ReactComponent 的 instance，但是我们要知道，先前的代码是存在一个**链表**结构的，所以要注意之后 child 还被执行了什么操作————还被使用 ReactReconciler.mountComponent 执行了一遍，而这个 method 是被分析过的，并且它是通过调用 ReactComponent 的 Instance 的 mountComponent 的方法来进行真正的 mount 工作。

循环调用：
performInitialMount => ReactReconciler.mountComponent => Component.mountComponent
       ||                                                         ||
        \======================================================== /


为了搞清楚这块调用逻辑，我试图追踪 this._renderedComponent 的改动轨迹：
```javascript
// 在 ReactCompositeComponent 中
performInitialMount: function(
    renderedElement,
    hostParent,
    hostContainerInfo,
    transaction,
    context,
  ) {
    // If not a stateless component, we now render
    if (renderedElement === undefined) {
      renderedElement = this._renderValidatedComponent();
    }

    var nodeType = ReactNodeTypes.getType(renderedElement);
    this._renderedNodeType = nodeType;
    var child = this._instantiateReactComponent(
      renderedElement,
      nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
    );
    this._renderedComponent = child;
    //...
    var markup = ReactReconciler.mountComponent(
      child, // 这里被调用了
      transaction,
      hostParent,
      hostContainerInfo,
      this._processChildContext(context),
      debugID,
    );
```

这段代码中的 child 生成也是需要注意的，也就是说 this._instantiateReactComponent 这个 function 做的是什么事情呢？
```javascript
/**
 * Given a ReactNode, create an instance that will actually be mounted.
 *
 * @param {ReactNode} node
 * @param {boolean} shouldHaveDebugID
 * @return {object} A new instance of the element's constructor.
 * @protected
 */
function instantiateReactComponent(node, shouldHaveDebugID) {
  var instance;
  //...
```
不深入这段代码可以发现这是一段根据 ReactNode（关于 ReactNode 的定义需要仔细研究）来 instance 一个 ReactComponent 的 instance 的方法。

那么我们在深入到 ReactReconciler 的代码中看一下这个 child（ReactComponent 的 instance）究竟被用来做什么了。
```javascript
/**
   * Initializes the component, renders markup, and registers event listeners.
   *
   * @param {ReactComponent} internalInstance
   * @param {ReactReconcileTransaction|ReactServerRenderingTransaction} transaction
   * @param {?object} the containing host component instance
   * @param {?object} info about the host container
   * @return {?string} Rendered markup to be inserted into the DOM.
   * @final
   * @internal
   */
  mountComponent: function(
    internalInstance,
    transaction,
    hostParent,
    hostContainerInfo,
    context,
    parentDebugID, // 0 in production and for roots
  ) {
    if (__DEV__) {
      if (internalInstance._debugID !== 0) {
        ReactInstrumentation.debugTool.onBeforeMountComponent(
          internalInstance._debugID,
          internalInstance._currentElement,
          parentDebugID,
        );
      }
    }
    var markup = internalInstance.mountComponent(// 直接又调用了 ReactComponent 的mountComponent 的方法
      transaction,
      hostParent,
      hostContainerInfo,
      context,
      parentDebugID,
    );
//...
```
这里需要注意的是， 这个 internalInstance 是之前的 child，但是这个 child 不一定是 ReactCompositeComponent 类型的 Instance，也有可能是其他类型的 Component 的 Instance，不过我们可以先看，如果是 ReactCompositeComponent 类型的 Instance 的话，怎么处理？
```javascript
// ReactCompositeComponent.js
/**
   * Initializes the component, renders markup, and registers event listeners.
   *
   * @param {ReactReconcileTransaction|ReactServerRenderingTransaction} transaction
   * @param {?object} hostParent
   * @param {?object} hostContainerInfo
   * @param {?object} context
   * @return {?string} Rendered markup to be inserted into the DOM.
   * @final
   * @internal
   */
  mountComponent: function(
    transaction,
    hostParent,
    hostContainerInfo,
    context,
  ) {
    this._context = context;
    this._mountOrder = nextMountID++;
    this._hostParent = hostParent;
    this._hostContainerInfo = hostContainerInfo;

    var publicProps = this._currentElement.props;
    var publicContext = this._processContext(context);

    var Component = this._currentElement.type;

    var updateQueue = transaction.getUpdateQueue();

    // Initialize the public class
    var doConstruct = shouldConstruct(Component);
    var inst = this._constructComponent(
      doConstruct,
      publicProps,
      publicContext,
      updateQueue,
    );
    var renderedElement; // 注意这个 renderedElement

    // Support functional components
    if (!doConstruct && (inst == null || inst.render == null)) {
      renderedElement = inst; // 同时当 doConstruct 和 inst 为空的时候，持有一份 inst，应该其实就是空
      if (__DEV__) {
        warning(
          !Component.childContextTypes,
          '%s(...): childContextTypes cannot be defined on a functional component.',
          Component.displayName || Component.name || 'Component',
        );
      }
//...
    var markup;
    if (inst.unstable_handleError) {
      markup = this.performInitialMountWithErrorHandling(
        renderedElement,  
        hostParent,
        hostContainerInfo,
        transaction,
        context,
      );
    } else {
      markup = this.performInitialMount(
        renderedElement,
        hostParent,
        hostContainerInfo,
        transaction,
        context,
      );
    }

```
需要注意的是，这里的 this 其实就是之前的 child，所以这里会很奇怪，取了 child 的属性，然后又调用 _constructrComponent 方法来进行:
```javascript
_constructComponent: function(
    doConstruct,
    publicProps,
    publicContext,
    updateQueue,
  ) {
    if (__DEV__) {
      ReactCurrentOwner.current = this;
      try {
        return this._constructComponentWithoutOwner(
          doConstruct,
          publicProps,
          publicContext,
          updateQueue,
        );
      } finally {
        ReactCurrentOwner.current = null;
      }
    } else {
      return this._constructComponentWithoutOwner(
        doConstruct,
        publicProps,
        publicContext,
        updateQueue,
      );
    }
  },

_constructComponentWithoutOwner: function(
    doConstruct,
    publicProps,
    publicContext,
    updateQueue,
  ) {
    var Component = this._currentElement.type; // 注意这里

    if (doConstruct) {
      if (__DEV__) {
        return measureLifeCyclePerf(
          () => new Component(publicProps, publicContext, updateQueue),
          this._debugID,
          'ctor',
        );
      } else {
        return new Component(publicProps, publicContext, updateQueue);
      }
    }
  }
//...
```

最终 又新建了一个 Component 的 instance，我们来从一开始追溯到这里，看看 `var Component = this._currentElement.type` 这句里面的 Component 究竟和 child 是什么关系:
`var Component = child._currentElement.type;` （因为这里的 this 就是 child）
所以这里返回的又是和 child 本身类型相同的 Instance（也许这里类型不一致），非常古怪。

然后在回到之前的代码，我们发现，performInitialMount method 又被调用了，并且传入 this 就是 child 和 renderedElement 就是 null 或者是上面提到的用 child 的 _currentElement.type 构造出来的 Instance。

这个时候，我们发现原来：
```javascript

performInitialMount: function(
    renderedElement,
    hostParent,
    hostContainerInfo,
    transaction,
    context,
  ) {
    // If not a stateless component, we now render
    if (renderedElement === undefined) {
      renderedElement = this._renderValidatedComponent();
    }
    var nodeType = ReactNodeTypes.getType(renderedElement);
    this._renderedNodeType = nodeType;
    var child = this._instantiateReactComponent(
      renderedElement,
      nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
    );
    this._renderedComponent = child;

//...

/**
   * @private
   */
  _renderValidatedComponent: function() {
    var renderedElement;
    if (
      __DEV__ ||
      this._compositeType !== ReactCompositeComponentTypes.StatelessFunctional
    ) {
      ReactCurrentOwner.current = this;
      try {
        renderedElement = this._renderValidatedComponentWithoutOwnerOrContext();
      } finally {
        ReactCurrentOwner.current = null;
      }
    } else {
      renderedElement = this._renderValidatedComponentWithoutOwnerOrContext();
    }
    invariant(
      // TODO: An `isValidNode` function would probably be more appropriate
      renderedElement === null ||
        renderedElement === false ||
        React.isValidElement(renderedElement),
      '%s.render(): A valid React element (or null) must be returned. You may have ' +
        'returned undefined, an array or some other invalid object.',
      this.getName() || 'ReactCompositeComponent',
    );

    return renderedElement;
  }

//...

 _renderValidatedComponentWithoutOwnerOrContext: function() {
    var inst = this._instance;
    var renderedElement;

    if (__DEV__) {
      renderedElement = measureLifeCyclePerf(
        () => inst.render(),
        this._debugID,
        'render',
      );
    } else {
      renderedElement = inst.render();
    }

    if (__DEV__) {
      // We allow auto-mocks to proceed as if they're returning null.
      if (renderedElement === undefined && inst.render._isMockFunction) {
        // This is probably bad practice. Consider warning here and
        // deprecating this convenience.
        renderedElement = null;
      }
    }

    return renderedElement;
  }
```
观察这三个方法，发现这个 链表 结构原来是如此搭建起来的，所以 precacheNode 做的遍历实际上就是找到最终的子节点，用一个 随机生成的 key 来存储。

**false**：
就不会进行上面的这一段处理，也就是说不会重用以前的 markup，而是直接生成将 markup 插入到响应的 dom node 里面去。
