>title: React-源码阅读-Component-Update
>date: 2017-07-07 01:55:38
>tags: react 源码 Component setState

# ReactComponent 的更新流程

## 如何开始
我是直接通过跑一个 react 的例子发现在 setState 操作出去的时候， performUpdateIfnecessary 开始了运行。

我们就从 ReactCompositeComponent 的 performUpdateIfnecessary 看起：

```javascript
/**
  * If any of `_pendingElement`, `_pendingStateQueue`, or `_pendingForceUpdate`
  * is set, update the component.
  *
  * @param {ReactReconcileTransaction} transaction
  * @internal
  */
performUpdateIfNecessary: function(transaction) {
  if (this._pendingElement != null) {
    ReactReconciler.receiveComponent(
      this,
      this._pendingElement,
      transaction,
      this._context,
    );
  } else if (this._pendingStateQueue !== null || this._pendingForceUpdate) {
    this.updateComponent(
      transaction,
      this._currentElement,
      this._currentElement,
      this._context,
      this._context,
    );
  } else {
    var callbacks = this._pendingCallbacks;
    this._pendingCallbacks = null;
    if (callbacks) {
      for (var j = 0; j < callbacks.length; j++) {
        transaction
          .getReactMountReady()
          .enqueue(callbacks[j], this.getPublicInstance());
      }
    }
    this._updateBatchNumber = null;
  }
}
```

这个函数发现会有几种执行情况，如果 this._pendingElement 存在的话，会直接调用 ReactReconciler.receiveComponent 来更新，如果不存在但是 _pendingStateQueue 或者 强制更新 被 set 了，那么 updateComponent 便会被调用，最后如果上述条件都没有满足，那么只会去执行嵌入的  callback。

我们先看使用 updateComponent 的情况
首先记住 updateComponent 参数的意义：

```javascript
updateComponent: function(
  transaction,
  prevParentElement,
  nextParentElement,
  prevUnmaskedContext,
  nextUnmaskedContext,
) {
  //...
  var prevProps = prevParentElement.props;
  var nextProps = nextParentElement.props;
  //...
  var nextState = this._processPendingState(nextProps, nextContext);
  //...
  if (shouldUpdate) {
    this._pendingForceUpdate = false;
    // Will set `this.props`, `this.state` and `this.context`.
    this._performComponentUpdate(
      nextParentElement,
      nextProps,
      nextState,
      nextContext,
      transaction,
      nextUnmaskedContext,
    );
  } else {
    // If it's determined that a component should not update, we still want
    // to set props and state but we shortcut the rest of the update.
    this._currentElement = nextParentElement;
    this._context = nextUnmaskedContext;
    inst.props = nextProps;
    inst.state = nextState;
    inst.context = nextContext;
  }

  if (callbacks) {
    for (var j = 0; j < callbacks.length; j++) {
      transaction
        .getReactMountReady()
        .enqueue(callbacks[j], this.getPublicInstance());
    }
  }
}
```

然后注意到传入的参数是当前的 element 和 context，因此这里只是做 state 的更新。
this._processPendingState 这个函数会用来计算 nextState：

```javascript
 _processPendingState: function(props, context) {
    var inst = this._instance;
    var queue = this._pendingStateQueue;
    var replace = this._pendingReplaceState;
    this._pendingReplaceState = false;
    this._pendingStateQueue = null;

    if (!queue) {
      return inst.state;
    }

    if (replace && queue.length === 1) {
      return queue[0];
    }

    var nextState = replace ? queue[0] : inst.state;
    var dontMutate = true;
    for (var i = replace ? 1 : 0; i < queue.length; i++) {
      var partial = queue[i];
      let partialState = typeof partial === 'function'
        ? partial.call(inst, nextState, props, context)
        : partial;
      if (partialState) {
        if (dontMutate) {
          dontMutate = false;
          nextState = Object.assign({}, nextState, partialState);
        } else {
          Object.assign(nextState, partialState);
        }
      }
    }

    return nextState;
  },
```

这个函数有趣的地方在于：
1. 会把你所有的 setState 填入的状态融合起来，也就是说很有可能只有最后一次的 State 有效果
2. state 也可以传入一个 function

有了新的 state 之后，便会进入 this._performComponentUpdate 这个函数的调用：

```javascript
_performComponentUpdate: function(
  nextElement,
  nextProps,
  nextState,
  nextContext,
  transaction,
  unmaskedContext,
) {
  var inst = this._instance;
  //...
  if (inst.componentWillUpdate) {
    if (__DEV__) {
      measureLifeCyclePerf(
        () => inst.componentWillUpdate(nextProps, nextState, nextContext),
        this._debugID,
        'componentWillUpdate',
      );
    } else {
      inst.componentWillUpdate(nextProps, nextState, nextContext);
    }
  }
  this._currentElement = nextElement;
  this._context = unmaskedContext;
  inst.props = nextProps;
  inst.state = nextState;
  inst.context = nextContext;

  if (inst.unstable_handleError) {
    this._updateRenderedComponentWithErrorHandling(
      transaction,
      unmaskedContext,
    );
  } else {
    this._updateRenderedComponent(transaction, unmaskedContext);
  }

  //... ComponentDidUpdate
}
```

这个函数在 componentWillUpdate 和 componentDidUpdate 之间调用了：

```javascript
this._updateRenderedComponent(transaction, unmaskedContext);
```

我们继续看 _updateRenderedComponent:
```javascript
/**
  * Call the component's `render` method and update the DOM accordingly.
  *
  * @param {ReactReconcileTransaction} transaction
  * @internal
  */
_updateRenderedComponent: function(transaction, context) {
  var nextRenderedElement = this._renderValidatedComponent();
  this._updateRenderedComponentWithNextElement(
    transaction,
    context,
    nextRenderedElement,
    false /* safely */,
  );
},
```

 this._renderValidatedComponent 里面表明要看 _updateRenderedComponentWithoutOwnerOrContext：

```javascript
/**
  * @protected
  */
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

可以看出来这个会调用 render 方法，调用了 render 方法后就会返回 一个 新的 element。

再回到 _updateRenderedComponent:

```javascript
/**
  * Call the component's `render` method and update the DOM accordingly.
  *
  * @param {ReactReconcileTransaction} transaction
  * @internal
  */
_updateRenderedComponent: function(transaction, context) {
  var nextRenderedElement = this._renderValidatedComponent();
  this._updateRenderedComponentWithNextElement(
    transaction,
    context,
    nextRenderedElement,
    false /* safely */,
  );
},
```

拿到了 render 出来的 element 就会调用 _updateRenderedComponentWithNextElement:

```javascript
/**
  * Call the component's `render` method and update the DOM accordingly.
  *
  * @param {ReactReconcileTransaction} transaction
  * @internal
  */
_updateRenderedComponentWithNextElement: function(
  transaction,
  context,
  nextRenderedElement,
  safely,
) {
  var prevComponentInstance = this._renderedComponent;
  var prevRenderedElement = prevComponentInstance._currentElement;

  //...

  if (shouldUpdateReactComponent(prevRenderedElement, nextRenderedElement)) {
    ReactReconciler.receiveComponent(
      prevComponentInstance,
      nextRenderedElement,
      transaction,
      this._processChildContext(context),
    );
  }
  //...
```

到这里会发现 首先调用 shouldUpdateReactComponent，注意这个和生命周期里面的 shouldComponentUpdate 不同。
如果返回 true，那么直接调用 ReactReconciler 的 receiveComponent 来进行更新。

那么我们就先看一下 shoudlUpdateReactComponent:

```javascript
/**
* Given a `prevElement` and `nextElement`, determines if the existing
* instance should be updated as opposed to being destroyed or replaced by a new
* instance. Both arguments are elements. This ensures that this logic can
* operate on stateless trees without any backing instance.
*
* @param {?object} prevElement
* @param {?object} nextElement
* @return {boolean} True if the existing instance should be updated.
* @protected
*/
function shouldUpdateReactComponent(prevElement, nextElement) {
  var prevEmpty = prevElement === null || prevElement === false;
  var nextEmpty = nextElement === null || nextElement === false;
  if (prevEmpty || nextEmpty) {
    return prevEmpty === nextEmpty;
  }

  var prevType = typeof prevElement;
  var nextType = typeof nextElement;
  if (prevType === 'string' || prevType === 'number') {
    return nextType === 'string' || nextType === 'number';
  } else {
    return (
      nextType === 'object' &&
      prevElement.type === nextElement.type &&
      prevElement.key === nextElement.key
    );
  }
}
```

注意这段代码的注释部分，该函数返回 true 意味着更新当前的 instance，而不是直接 destroy 掉，若是返回 false，那么就是说当前的 instance 会被销毁加替代。
为 true 的条件很简单：
1. 如果是 string 或者 number 直接返回 true
2. 如果是 object 必须保证 type 和 key 一致

让我们在回到上层代码，考虑 shoudlUpdateReactComponent 结果为 true 的时候，ReactConciler.ReceiveComponent 的调用：

```javascript
//_updateRenderedComponentWithNextElement: function
ReactReconciler.receiveComponent(
        prevComponentInstance,
        nextRenderedElement,
        transaction,
        this._processChildContext(context),
      );
```

这里有段 context 的处理，但是考虑到目前 context 的使用并不是很频繁，我们直接跳过。
我们再看一下 ReactReconciler.receiveComponent 的实现：

```javascript
// ReactReconciler.receiveComponent
/**
  * Update a component using a new element.
  *
  * @param {ReactComponent} internalInstance
  * @param {ReactElement} nextElement
  * @param {ReactReconcileTransaction} transaction
  * @param {object} context
  * @internal
  */
receiveComponent: function(
  internalInstance,
  nextElement,
  transaction,
  context,
) {
  var prevElement = internalInstance._currentElement;

  if (nextElement === prevElement && context === internalInstance._context) {
    // Since elements are immutable after the owner is rendered,
    // we can do a cheap identity compare here to determine if this is a
    // superfluous reconcile. It's possible for state to be mutable but such
    // change should trigger an update of the owner which would recreate
    // the element. We explicitly check for the existence of an owner since
    // it's possible for an element created outside a composite to be
    // deeply mutated and reused.

    // TODO: Bailing out early is just a perf optimization right?
    // TODO: Removing the return statement should affect correctness?
    return;
  }
  //...
  internalInstance.receiveComponent(nextElement, transaction, context);
  //...
},
```

这段代码这里省略了一些 ref 的处理，不过以后也可以详细谈。
这里会做一次检查，会做一次 reference 的比较，如果相同，那么自然就没有必要去更新。
然后在使用传入的 internalInstance.receiveComponent 去做真正的更新。

那么我们直接看 ReactComponent 的 receiveComponent：

```javascript
receiveComponent: function(nextElement, transaction, nextContext) {
  var prevElement = this._currentElement;
  var prevContext = this._context;

  this._pendingElement = null;

  this.updateComponent(
    transaction,
    prevElement,
    nextElement,
    prevContext,
    nextContext,
  );
}
```

然后我们发现居然又回到了 updateComponent 这个函数，因此现在有两个问题：
1. 上次调用和这次调用那里不同？
2. 如果不同，是一种递归的话，在哪里停止？
第一个问题是容易回答的，肯定不同，不同之处在于 this 发生了变化，其实这个 instance 是这样来的：

```javascript
/**
  * Call the component's `render` method and update the DOM accordingly.
  *
  * @param {ReactReconcileTransaction} transaction
  * @internal
  */
_updateRenderedComponentWithNextElement: function(
  transaction,
  context,
  nextRenderedElement,
  safely,
) {
  var prevComponentInstance = this._renderedComponent;
  //...
```

而 this._renderedComponent 的唯一 assignment 是在 _updateRenderedComponentWithNextElement 的另一条条件分支里面，也就是说当需要替换 component 的时候，会将产生这个 assignment：

```javascript
_updateRenderedComponentWithNextElement: function(
  transaction,
  context,
  nextRenderedElement,
  safely,
) {
  var prevComponentInstance = this._renderedComponent;
  var prevRenderedElement = prevComponentInstance._currentElement;

  //...

if (shouldUpdateReactComponent(prevRenderedElement, nextRenderedElement)) {
  ReactReconciler.receiveComponent(
    prevComponentInstance,
    nextRenderedElement,
    transaction,
    this._processChildContext(context),
  );
} else {
  var oldHostNode = ReactReconciler.getHostNode(prevComponentInstance);
  var nodeType = ReactNodeTypes.getType(nextRenderedElement);
  this._renderedNodeType = nodeType;
  var child = this._instantiateReactComponent(
    nextRenderedElement,
    nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
  );
  this._renderedComponent = child;
  //...
```

这里试想如果是第一次进入这个函数，this.\_renderedComponent 肯定是 undefined，而 nextRenderedElement 肯定不是空的，也就说一定会进入第二个分支，然后将新的 element 实例化成新的 this.\_renderedComponent。
因此所有的秘密都停留在了 this._instantiateReactComponent 里面了。

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

  if (node === null || node === false) {
    instance = ReactEmptyComponent.create(instantiateReactComponent);
  } else if (typeof node === 'object') {
    var element = node;
    var type = element.type;
    if (typeof type !== 'function' && typeof type !== 'string') {
      var info = '';
      if (__DEV__) {
        if (
          type === undefined ||
          (typeof type === 'object' &&
            type !== null &&
            Object.keys(type).length === 0)
        ) {
          info +=
            ' You likely forgot to export your component from the file ' +
            "it's defined in.";
        }
      }
      info += getDeclarationErrorAddendum(element._owner);
      invariant(
        false,
        'Element type is invalid: expected a string (for built-in components) ' +
          'or a class/function (for composite components) but got: %s.%s',
        type == null ? type : typeof type,
        info,
      );
    }

    // Special case string values
    if (typeof element.type === 'string') {
      instance = ReactHostComponent.createInternalComponent(element);
    } else if (isInternalComponentType(element.type)) {
      // This is temporarily available for custom components that are not string
      // representations. I.e. ART. Once those are updated to use the string
      // representation, we can drop this code path.
      instance = new element.type(element);

      // We renamed this. Allow the old name for compat. :(
      if (!instance.getHostNode) {
        instance.getHostNode = instance.getNativeNode;
      }
    } else {
      instance = new ReactCompositeComponentWrapper(element);
    }
  } else if (typeof node === 'string' || typeof node === 'number') {
    instance = ReactHostComponent.createInstanceForText(node);
  } else {
    invariant(false, 'Encountered invalid React node of type %s', typeof node);
  }

  if (__DEV__) {
    warning(
      typeof instance.mountComponent === 'function' &&
        typeof instance.receiveComponent === 'function' &&
        typeof instance.getHostNode === 'function' &&
        typeof instance.unmountComponent === 'function',
      'Only React Components can be mounted.',
    );
  }

  // These two fields are used by the DOM and ART diffing algorithms
  // respectively. Instead of using expandos on components, we should be
  // storing the state needed by the diffing algorithms elsewhere.
  instance._mountIndex = 0;
  instance._mountImage = null;

  if (__DEV__) {
    instance._debugID = shouldHaveDebugID ? nextDebugID++ : 0;
  }

  // Internal instances should fully constructed at this point, so they should
  // not get any new fields added to them at this point.
  if (__DEV__) {
    if (Object.preventExtensions) {
      Object.preventExtensions(instance);
    }
  }

  return instance;
}
```

这段代码其实简单的看来就是处理三种不同的 ReactElement：
1. string, number => 直接使用 ReactHostComponent.createInstanceForText 来进行实例化

```javascript
//...
 else if (typeof node === 'string' || typeof node === 'number') {
    instance = ReactHostComponent.createInstanceForText(node);
//...
```

2. 是 object 并且其 type 字段又是 string，那么就会使用 ReactHostComponent.createInternalComponent 来进行实例化

```javascript
//...
 if (typeof element.type === 'string') {
      instance = ReactHostComponent.createInternalComponent(element);
    }
//...
```

3. 是 CompositeElement，会使用 ReactCompositeComponentWrapper 来进行实例化，其中会做一次检查，检查是否是是自定义的 type（只要定义了 mountComponent 和 receiveComponent 就行了）

因此在回到我们之前的问题：

```javascript
_updateRenderedComponentWithNextElement: function(
  transaction,
  context,
  nextRenderedElement,
  safely,
) {
  var prevComponentInstance = this._renderedComponent;
  var prevRenderedElement = prevComponentInstance._currentElement;

  //...

if (shouldUpdateReactComponent(prevRenderedElement, nextRenderedElement)) {
  ReactReconciler.receiveComponent(
    prevComponentInstance,
    nextRenderedElement,
    transaction,
    this._processChildContext(context),
  );
} else {
  var oldHostNode = ReactReconciler.getHostNode(prevComponentInstance);
  var nodeType = ReactNodeTypes.getType(nextRenderedElement);
  this._renderedNodeType = nodeType;
  var child = this._instantiateReactComponent(
    nextRenderedElement,
    nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
  );
  this._renderedComponent = child;
  //...
```

这个 child 实际上就是被实例化出来的一个新的 Component（注意为什么是 child，是因为 nextRenderedElement 是用当前 Component 的 render 函数形成的），所以 第一个问题解决了：
>1. 上次调用和这次调用那里不同？
>2. 如果不同，是一种递归的话，在哪里停止？

那么第二个问题是怎么解决的呢？
直观上看这个递归的结束很简单，就是最后没有了 child，所以这里就不深究了。

```javascript
//...
else if (isInternalComponentType(element.type)) {
      // This is temporarily available for custom components that are not string
      // representations. I.e. ART. Once those are updated to use the string
      // representation, we can drop this code path.
      instance = new element.type(element);

      // We renamed this. Allow the old name for compat. :(
      if (!instance.getHostNode) {
        instance.getHostNode = instance.getNativeNode;
      }
    } else {
      instance = new ReactCompositeComponentWrapper(element);
    }
//...
```
   
再回到之前的 _updateRenderedComponentWithNextElement，把接下来的处理看掉：

  ```javascript
  // _updateRenderedComponentWithNextElement: function()
  if (shouldUpdateReactComponent(prevRenderedElement, nextRenderedElement)) {
    ReactReconciler.receiveComponent(
      prevComponentInstance,
      nextRenderedElement,
      transaction,
      this._processChildContext(context),
    );
  } 
  else {
    var oldHostNode = ReactReconciler.getHostNode(prevComponentInstance);
    var nodeType = ReactNodeTypes.getType(nextRenderedElement);
    this._renderedNodeType = nodeType;
    var child = this._instantiateReactComponent(
      nextRenderedElement,
      nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
    );
    this._renderedComponent = child;

    var nextMarkup = ReactReconciler.mountComponent(
      child,
      transaction,
      this._hostParent,
      this._hostContainerInfo,
      this._processChildContext(context),
      debugID,
    );

    ReactReconciler.unmountComponent(
      prevComponentInstance,
      safely,
      false /* skipLifecycle */,
    );

    if (__DEV__) {
      if (debugID !== 0) {
        var childDebugIDs = child._debugID !== 0 ? [child._debugID] : [];
        ReactInstrumentation.debugTool.onSetChildren(debugID, childDebugIDs);
      }
    }

    this._replaceNodeWithMarkup(
      oldHostNode,
      nextMarkup,
      prevComponentInstance,
    );
  }
},
```

这块总的来说就是在 shouldUpdateReactComponent 返回 false 的时候：
1. 保存老的 hostNode
2. instantiate 新的 ReactComponent
3. mount 这个新的 instance，拿到 markup
4. unmount 旧的 instance
5. 重新渲染 hostNode 下的 dom


## ReactDOMComponent
其实 ReactCompositeComponent 不会做具体的更新的。
在 performUpdateIfNecessary 中的第一个条件表明，如果存在 pendingElement 那么会直接调用 ReactReconciler.receiveComponent。

```javascript
/**
  * If any of `_pendingElement`, `_pendingStateQueue`, or `_pendingForceUpdate`
  * is set, update the component.
  *
  * @param {ReactReconcileTransaction} transaction
  * @internal
  */
performUpdateIfNecessary: function(transaction) {
  if (this._pendingElement != null) {
    ReactReconciler.receiveComponent(
      this,
      this._pendingElement,
      transaction,
      this._context,
    );
  }
```

而 ReactReconciler.receiveComponent 中的具体做法是：

```javascript
// ReactReconciler.receiveComponent
/**
  * Update a component using a new element.
  *
  * @param {ReactComponent} internalInstance
  * @param {ReactElement} nextElement
  * @param {ReactReconcileTransaction} transaction
  * @param {object} context
  * @internal
  */
receiveComponent: function(
  internalInstance,
  nextElement,
  transaction,
  context,
) {
  var prevElement = internalInstance._currentElement;

  if (nextElement === prevElement && context === internalInstance._context) {
    // Since elements are immutable after the owner is rendered,
    // we can do a cheap identity compare here to determine if this is a
    // superfluous reconcile. It's possible for state to be mutable but such
    // change should trigger an update of the owner which would recreate
    // the element. We explicitly check for the existence of an owner since
    // it's possible for an element created outside a composite to be
    // deeply mutated and reused.

    // TODO: Bailing out early is just a perf optimization right?
    // TODO: Removing the return statement should affect correctness?
    return;
  }
  //...
  internalInstance.receiveComponent(nextElement, transaction, context);
  //...
},
```

又把 receiveComponent delegate 给了这个 Component 的 instance，我们再看 ReactCompositeComponent.receiveComponent：

```javascript
  receiveComponent: function(nextElement, transaction, nextContext) {
    var prevElement = this._currentElement;
    var prevContext = this._context;

    this._pendingElement = null;

    this.updateComponent(
      transaction,
      prevElement,
      nextElement,
      prevContext,
      nextContext,
    );
  },
```

再看 updateComponent：

```javascript
/**
   * Perform an update to a mounted component. The componentWillReceiveProps and
   * shouldComponentUpdate methods are called, then (assuming the update isn't
   * skipped) the remaining update lifecycle methods are called and the DOM
   * representation is updated.
   *
   * By default, this implements React's rendering and reconciliation algorithm.
   * Sophisticated clients may wish to override this.
   *
   * @param {ReactReconcileTransaction} transaction
   * @param {ReactElement} prevParentElement
   * @param {ReactElement} nextParentElement
   * @internal
   * @overridable
   */
  updateComponent: function(
    transaction,
    prevParentElement,
    nextParentElement,
    prevUnmaskedContext,
    nextUnmaskedContext,
  ) {
    if (shouldUpdate) {
      this._pendingForceUpdate = false;
      // Will set `this.props`, `this.state` and `this.context`.
      this._performComponentUpdate(
        nextParentElement,
        nextProps,
        nextState,
        nextContext,
        transaction,
        nextUnmaskedContext,
      );
    } else {
    //...
```

再看 _performComponentUpdate:

```javascript
/**
   * Merges new props and state, notifies delegate methods of update and
   * performs update.
   *
   * @param {ReactElement} nextElement Next element
   * @param {object} nextProps Next public object to set as properties.
   * @param {?object} nextState Next object to set as state.
   * @param {?object} nextContext Next public object to set as context.
   * @param {ReactReconcileTransaction} transaction
   * @param {?object} unmaskedContext
   * @private
   */
  _performComponentUpdate: function(
    nextElement,
    nextProps,
    nextState,
    nextContext,
    transaction,
    unmaskedContext,
  ) {
    var inst = this._instance;

    var hasComponentDidUpdate = !!inst.componentDidUpdate;
    var prevProps;
    var prevState;
    if (hasComponentDidUpdate) {
      prevProps = inst.props;
      prevState = inst.state;
    }
    //...
    this._currentElement = nextElement;
    this._context = unmaskedContext;
    inst.props = nextProps;
    inst.state = nextState;
    inst.context = nextContext;

    if (inst.unstable_handleError) {
      this._updateRenderedComponentWithErrorHandling(
        transaction,
        unmaskedContext,
      );
    } else {
      this._updateRenderedComponent(transaction, unmaskedContext);
    }
    //...
```

因此我们又要看 _updateRenderedComponent:

```javascript
  /**
   * Call the component's `render` method and update the DOM accordingly.
   *
   * @param {ReactReconcileTransaction} transaction
   * @internal
   */
  _updateRenderedComponent: function(transaction, context) {
    var nextRenderedElement = this._renderValidatedComponent();
    this._updateRenderedComponentWithNextElement(
      transaction,
      context,
      nextRenderedElement,
      false /* safely */,
    );
  },
```

进入 _updateRenderedComponentWithNextElement:

```javascript
/**
   * Call the component's `render` method and update the DOM accordingly.
   *
   * @param {ReactReconcileTransaction} transaction
   * @internal
   */
  _updateRenderedComponentWithNextElement: function(
    transaction,
    context,
    nextRenderedElement,
    safely,
  ) {
    var prevComponentInstance = this._renderedComponent;
    var prevRenderedElement = prevComponentInstance._currentElement;

    var debugID = 0;
    if (__DEV__) {
      debugID = this._debugID;
    }

    if (shouldUpdateReactComponent(prevRenderedElement, nextRenderedElement)) {
      ReactReconciler.receiveComponent(
        prevComponentInstance,
        nextRenderedElement,
        transaction,
        this._processChildContext(context),
      );
    } else {
      var oldHostNode = ReactReconciler.getHostNode(prevComponentInstance);
      var nodeType = ReactNodeTypes.getType(nextRenderedElement);
      this._renderedNodeType = nodeType;
      var child = this._instantiateReactComponent(
        nextRenderedElement,
        nodeType !== ReactNodeTypes.EMPTY /* shouldHaveDebugID */,
      );
      this._renderedComponent = child;

      var nextMarkup = ReactReconciler.mountComponent(
        child,
        transaction,
        this._hostParent,
        this._hostContainerInfo,
        this._processChildContext(context),
        debugID,
      );

      ReactReconciler.unmountComponent(
        prevComponentInstance,
        safely,
        false /* skipLifecycle */,
      );

      if (__DEV__) {
        if (debugID !== 0) {
          var childDebugIDs = child._debugID !== 0 ? [child._debugID] : [];
          ReactInstrumentation.debugTool.onSetChildren(debugID, childDebugIDs);
        }
      }

      this._replaceNodeWithMarkup(
        oldHostNode,
        nextMarkup,
        prevComponentInstance,
      );
    }
  },
```

这里注意，根据我们之前的说明：

```javascript
/**
   * Call the component's `render` method and update the DOM accordingly.
   *
   * @param {ReactReconcileTransaction} transaction
   * @internal
   */
  _updateRenderedComponentWithNextElement: function(
    transaction,
    context,
    nextRenderedElement,
    safely,
  ) {
    var prevComponentInstance = this._renderedComponent;
    var prevRenderedElement = prevComponentInstance._currentElement;

    var debugID = 0;
    if (__DEV__) {
      debugID = this._debugID;
    }

    if (shouldUpdateReactComponent(prevRenderedElement, nextRenderedElement)) {
      ReactReconciler.receiveComponent(
        prevComponentInstance,
        nextRenderedElement,
        transaction,
        this._processChildContext(context),
      );
    } else {
```

这里的 prevComponentInstance 实际上是 this（这个也是一个 ComponentInstance）的 render 函数返回的 ReactElement 的 Component Instance，然后 nextRenderedElement 是当前的被更新了的 ReactElement，如果我们假设这个 prevComponentInstance 是一个 ReactDOMComponent 的话，那么一切就会进入 ReactDOMComponent 的 receiveComponent，并且接受的参数就是 nextRenderedElement，我们看一下：

```javascript
/**
   * Receives a next element and updates the component.
   *
   * @internal
   * @param {ReactElement} nextElement
   * @param {ReactReconcileTransaction|ReactServerRenderingTransaction} transaction
   * @param {object} context
   */
  receiveComponent: function(nextElement, transaction, context) {
    var prevElement = this._currentElement;
    this._currentElement = nextElement;
    this.updateComponent(transaction, prevElement, nextElement, context);
  },
```

在看 updateComponent：

```javascript
  /**
   * Updates a DOM component after it has already been allocated and
   * attached to the DOM. Reconciles the root DOM node, then recurses.
   *
   * @param {ReactReconcileTransaction} transaction
   * @param {ReactElement} prevElement
   * @param {ReactElement} nextElement
   * @internal
   * @overridable
   */
  updateComponent: function(transaction, prevElement, nextElement, context) {
    var lastProps = prevElement.props;
    var nextProps = this._currentElement.props;

    switch (this._tag) {
      case 'input':
        lastProps = ReactDOMInput.getHostProps(this, lastProps);
        nextProps = ReactDOMInput.getHostProps(this, nextProps);
        break;
      case 'option':
        lastProps = ReactDOMOption.getHostProps(this, lastProps);
        nextProps = ReactDOMOption.getHostProps(this, nextProps);
        break;
      case 'select':
        lastProps = ReactDOMSelect.getHostProps(this, lastProps);
        nextProps = ReactDOMSelect.getHostProps(this, nextProps);
        break;
      case 'textarea':
        lastProps = ReactDOMTextarea.getHostProps(this, lastProps);
        nextProps = ReactDOMTextarea.getHostProps(this, nextProps);
        break;
      default:
        if (
          typeof lastProps.onClick !== 'function' &&
          typeof nextProps.onClick === 'function'
        ) {
          transaction
            .getReactMountReady()
            .enqueue(trapClickOnNonInteractiveElement, this);
        }
        break;
    }

    assertValidProps(this, nextProps);
    var isCustomComponentTag = isCustomComponent(this._tag, nextProps);
    this._updateDOMProperties(
      lastProps,
      nextProps,
      transaction,
      isCustomComponentTag,
    );
    this._updateDOMChildren(lastProps, nextProps, transaction, context);

    switch (this._tag) {
      case 'input':
        // Update the wrapper around inputs *after* updating props. This has to
        // happen after `_updateDOMProperties`. Otherwise HTML5 input validations
        // raise warnings and prevent the new value from being assigned.
        ReactDOMInput.updateWrapper(this);
        break;
      case 'textarea':
        ReactDOMTextarea.updateWrapper(this);
        break;
      case 'select':
        // <select> value update needs to occur after <option> children
        // reconciliation
        transaction.getReactMountReady().enqueue(postUpdateSelectWrapper, this);
        break;
    }
  },
```

这段代码真的比较简单，唯一值得看的是 this._updateDOMChildren 这个函数:
```javascript
/**
   * Reconciles the children with the various properties that affect the
   * children content.
   *
   * @param {object} lastProps
   * @param {object} nextProps
   * @param {ReactReconcileTransaction} transaction
   * @param {object} context
   */
  _updateDOMChildren: function(lastProps, nextProps, transaction, context) {
    var lastContent = CONTENT_TYPES[typeof lastProps.children]
      ? lastProps.children
      : null;
    var nextContent = CONTENT_TYPES[typeof nextProps.children]
      ? nextProps.children
      : null;

    var lastHtml =
      lastProps.dangerouslySetInnerHTML &&
      lastProps.dangerouslySetInnerHTML.__html;
    var nextHtml =
      nextProps.dangerouslySetInnerHTML &&
      nextProps.dangerouslySetInnerHTML.__html;

    // Note the use of `!=` which checks for null or undefined.
    var lastChildren = lastContent != null ? null : lastProps.children;
    var nextChildren = nextContent != null ? null : nextProps.children;

    // If we're switching from children to content/html or vice versa, remove
    // the old content
    var lastHasContentOrHtml = lastContent != null || lastHtml != null;
    var nextHasContentOrHtml = nextContent != null || nextHtml != null;
    if (lastChildren != null && nextChildren == null) {
      this.updateChildren(null, transaction, context);
    } else if (lastHasContentOrHtml && !nextHasContentOrHtml) {
      this.updateTextContent('');
      if (__DEV__) {
        ReactInstrumentation.debugTool.onSetChildren(this._debugID, []);
      }
    }

    if (nextContent != null) {
      if (lastContent !== nextContent) {
        this.updateTextContent('' + nextContent);
        if (__DEV__) {
          setAndValidateContentChildDev.call(this, nextContent);
        }
      }
    } else if (nextHtml != null) {
      if (lastHtml !== nextHtml) {
        this.updateMarkup('' + nextHtml);
      }
      if (__DEV__) {
        ReactInstrumentation.debugTool.onSetChildren(this._debugID, []);
      }
    } else if (nextChildren != null) {
      if (__DEV__) {
        setAndValidateContentChildDev.call(this, null);
      }

      this.updateChildren(nextChildren, transaction, context);
    }
  },
```

这段代码告诉我得看 updateChildren 这个函数，而这个函数是来自于其它类，最终在 ReactMultiChild 中找到：
```javascript
/**
   * @param {?object} nextNestedChildrenElements Nested child element maps.
   * @param {ReactReconcileTransaction} transaction
   * @final
   * @protected
   */
  _updateChildren: function(nextNestedChildrenElements, transaction, context) {
    var prevChildren = this._renderedChildren;
    var removedNodes = {};
    var mountImages = [];
    var nextChildren = this._reconcilerUpdateChildren(
      prevChildren,
      nextNestedChildrenElements,
      mountImages,
      removedNodes,
      transaction,
      context,
    );
    if (!nextChildren && !prevChildren) {
      return;
    }
    var updates = null;
    var name;
    // `nextIndex` will increment for each child in `nextChildren`, but
    // `lastIndex` will be the last index visited in `prevChildren`.
    var nextIndex = 0;
    var lastIndex = 0;
    // `nextMountIndex` will increment for each newly mounted child.
    var nextMountIndex = 0;
    var lastPlacedNode = null;
    for (name in nextChildren) {
      if (!nextChildren.hasOwnProperty(name)) {
        continue;
      }
      var prevChild = prevChildren && prevChildren[name];
      var nextChild = nextChildren[name];
      if (prevChild === nextChild) {
        updates = enqueue(
          updates,
          this.moveChild(prevChild, lastPlacedNode, nextIndex, lastIndex),
        );
        lastIndex = Math.max(prevChild._mountIndex, lastIndex);
        prevChild._mountIndex = nextIndex;
      } else {
        if (prevChild) {
          // Update `lastIndex` before `_mountIndex` gets unset by unmounting.
          lastIndex = Math.max(prevChild._mountIndex, lastIndex);
          // The `removedNodes` loop below will actually remove the child.
        }
        // The child must be instantiated before it's mounted.
        updates = enqueue(
          updates,
          this._mountChildAtIndex(
            nextChild,
            mountImages[nextMountIndex],
            lastPlacedNode,
            nextIndex,
            transaction,
            context,
          ),
        );
        nextMountIndex++;
      }
      nextIndex++;
      lastPlacedNode = ReactReconciler.getHostNode(nextChild);
    }
    // Remove children that are no longer present.
    for (name in removedNodes) {
      if (removedNodes.hasOwnProperty(name)) {
        updates = enqueue(
          updates,
          this._unmountChild(prevChildren[name], removedNodes[name]),
        );
      }
    }
    if (updates) {
      processQueue(this, updates);
    }
    this._renderedChildren = nextChildren;

    if (__DEV__) {
      setChildrenForInstrumentation.call(this, nextChildren);
    }
  },
```

还得看 this._reconcilerUpdateChildren 这个函数：

```javascript
_reconcilerUpdateChildren: function(
    prevChildren,
    nextNestedChildrenElements,
    mountImages,
    removedNodes,
    transaction,
    context,
  ) {
    var nextChildren;
    var selfDebugID = 0;
    if (__DEV__) {
      selfDebugID = getDebugID(this);
      if (this._currentElement) {
        try {
          ReactCurrentOwner.current = this._currentElement._owner;
          nextChildren = flattenStackChildren(
            nextNestedChildrenElements,
            selfDebugID,
          );
        } finally {
          ReactCurrentOwner.current = null;
        }
        ReactChildReconciler.updateChildren(
          prevChildren,
          nextChildren,
          mountImages,
          removedNodes,
          transaction,
          this,
          this._hostContainerInfo,
          context,
          selfDebugID,
        );
        return nextChildren;
      }
    }
    nextChildren = flattenStackChildren(
      nextNestedChildrenElements,
      selfDebugID,
    );
    ReactChildReconciler.updateChildren(
      prevChildren,
      nextChildren,
      mountImages,
      removedNodes,
      transaction,
      this,
      this._hostContainerInfo,
      context,
      selfDebugID,
    );
    return nextChildren;
  },
```

又得看 ReactChildReconciler.updateChildren 这个函数：
```javascript
/**
   * Updates the rendered children and returns a new set of children.
   *
   * @param {?object} prevChildren Previously initialized set of children.
   * @param {?object} nextChildren Flat child element maps.
   * @param {ReactReconcileTransaction} transaction
   * @param {object} context
   * @return {?object} A new set of child instances.
   * @internal
   */
  updateChildren: function(
    prevChildren,
    nextChildren,
    mountImages,
    removedNodes,
    transaction,
    hostParent,
    hostContainerInfo,
    context,
    selfDebugID, // 0 in production and for roots
  ) {
    // We currently don't have a way to track moves here but if we use iterators
    // instead of for..in we can zip the iterators and check if an item has
    // moved.
    // TODO: If nothing has changed, return the prevChildren object so that we
    // can quickly bailout if nothing has changed.
    if (!nextChildren && !prevChildren) {
      return;
    }
    var name;
    var prevChild;
    for (name in nextChildren) {
      if (!nextChildren.hasOwnProperty(name)) {
        continue;
      }
      prevChild = prevChildren && prevChildren[name];
      var prevElement = prevChild && prevChild._currentElement;
      var nextElement = nextChildren[name];
      if (
        prevChild != null &&
        shouldUpdateReactComponent(prevElement, nextElement)
      ) {
        ReactReconciler.receiveComponent(
          prevChild,
          nextElement,
          transaction,
          context,
        );
        nextChildren[name] = prevChild;
      } else {
        // The child must be instantiated before it's mounted.
        var nextChildInstance = instantiateReactComponent(nextElement, true);
        nextChildren[name] = nextChildInstance;
        // Creating mount image now ensures refs are resolved in right order
        // (see https://github.com/facebook/react/pull/7101 for explanation).
        var nextChildMountImage = ReactReconciler.mountComponent(
          nextChildInstance,
          transaction,
          hostParent,
          hostContainerInfo,
          context,
          selfDebugID,
        );
        mountImages.push(nextChildMountImage);
        if (prevChild) {
          removedNodes[name] = ReactReconciler.getHostNode(prevChild);
          ReactReconciler.unmountComponent(
            prevChild,
            false /* safely */,
            false /* skipLifecycle */,
          );
        }
      }
    }
    // Unmount children that are no longer present.
    for (name in prevChildren) {
      if (
        prevChildren.hasOwnProperty(name) &&
        !(nextChildren && nextChildren.hasOwnProperty(name))
      ) {
        prevChild = prevChildren[name];
        removedNodes[name] = ReactReconciler.getHostNode(prevChild);
        ReactReconciler.unmountComponent(
          prevChild,
          false /* safely */,
          false /* skipLifecycle */,
        );
      }
    }
  },
```

到这里基本上结束了，这个函数会遍历所有 children，然后对其调用 ReactReconciler.receiveComponent（如果只是更新的话）或者 直接走 mount 新节点／unmount 旧节点的流程。

## 更新触发起点
现在有一个重要的问题其实还没解决，那就是哪里是更新触发的起点，即究竟是通过哪一个函数触发了更新（也就是说调用了 performUpdateIfnecessary 这个函数）:

```javascript
function runBatchedUpdates(transaction) {
  var len = transaction.dirtyComponentsLength;
  invariant(
    len === dirtyComponents.length,
    "Expected flush transaction's stored dirty-components length (%s) to " +
      'match dirty-components array length (%s).',
    len,
    dirtyComponents.length,
  );

  // Since reconciling a component higher in the owner hierarchy usually (not
  // always -- see shouldComponentUpdate()) will reconcile children, reconcile
  // them before their children by sorting the array.
  dirtyComponents.sort(mountOrderComparator);

  // Any updates enqueued while reconciling must be performed after this entire
  // batch. Otherwise, if dirtyComponents is [A, B] where A has children B and
  // C, B could update twice in a single batch if C's render enqueues an update
  // to B (since B would have already updated, we should skip it, and the only
  // way we can know to do so is by checking the batch counter).
  updateBatchNumber++;

  for (var i = 0; i < len; i++) {
    // If a component is unmounted before pending changes apply, it will still
    // be here, but we assume that it has cleared its _pendingCallbacks and
    // that performUpdateIfNecessary is a noop.
    var component = dirtyComponents[i];

    ReactReconciler.performUpdateIfNecessary(
      component,
      transaction.reconcileTransaction,
      updateBatchNumber,
    );
  }
}
```

然后再向上追溯:
```javascript
var flushBatchedUpdates = function() {
  // ReactUpdatesFlushTransaction's wrappers will clear the dirtyComponents
  // array and perform any updates enqueued by mount-ready handlers (i.e.,
  // componentDidUpdate) but we need to check here too in order to catch
  // updates enqueued by setState callbacks.
  while (dirtyComponents.length) {
    var transaction = ReactUpdatesFlushTransaction.getPooled();
    transaction.perform(runBatchedUpdates, null, transaction);
    ReactUpdatesFlushTransaction.release(transaction);
  }
```

发现在 ReactDefaultBatchingStrategy 这个文件中:

```javascript
var RESET_BATCHED_UPDATES = {
  initialize: emptyFunction,
  close: function() {
    ReactDefaultBatchingStrategy.isBatchingUpdates = false;
  },
};

var FLUSH_BATCHED_UPDATES = {
  initialize: emptyFunction,
  close: ReactUpdates.flushBatchedUpdates.bind(ReactUpdates),
};

var TRANSACTION_WRAPPERS = [FLUSH_BATCHED_UPDATES, RESET_BATCHED_UPDATES];

function ReactDefaultBatchingStrategyTransaction() {
  this.reinitializeTransaction();
}

Object.assign(ReactDefaultBatchingStrategyTransaction.prototype, Transaction, {
  getTransactionWrappers: function() {
    return TRANSACTION_WRAPPERS;
  },
});

var transaction = new ReactDefaultBatchingStrategyTransaction();

var ReactDefaultBatchingStrategy = {
  isBatchingUpdates: false,

  /**
   * Call the provided function in a context within which calls to `setState`
   * and friends are batched such that components aren't updated unnecessarily.
   */
  batchedUpdates: function(callback, a, b, c, d, e) {
    var alreadyBatchingUpdates = ReactDefaultBatchingStrategy.isBatchingUpdates;

    ReactDefaultBatchingStrategy.isBatchingUpdates = true;

    // The code is written this way to avoid extra allocations
    if (alreadyBatchingUpdates) {
      return callback(a, b, c, d, e);
    } else {
      return transaction.perform(callback, null, a, b, c, d, e);
    }
  },
};

module.exports = ReactDefaultBatchingStrategy;
```

react 很经典的一个 transaction 处理，然后再去找 ReactDefaultBatchingStrategy 的使用，由于 DOM 和 Native 的应用场景不同，这个 Strategy 是动态插入的，我们可以看 DOM 的场景：

```javascript
// ReactDOMStackInjection.js
var alreadyInjected = false;

function inject() {
  if (alreadyInjected) {
    // TODO: This is currently true because these injections are shared between
    // the client and the server package. They should be built independently
    // and not share any injection state. Then this problem will be solved.
    return;
  }
  alreadyInjected = true;

  ReactGenericBatching.injection.injectStackBatchedUpdates(
    ReactUpdates.batchedUpdates,
  );

  ReactHostComponent.injection.injectGenericComponentClass(ReactDOMComponent);

  ReactHostComponent.injection.injectTextComponentClass(ReactDOMTextComponent);

  ReactEmptyComponent.injection.injectEmptyComponentFactory(function(
    instantiate,
  ) {
    return new ReactDOMEmptyComponent(instantiate);
  });

  ReactUpdates.injection.injectReconcileTransaction(ReactReconcileTransaction);
  /*********this-line*****************/
  ReactUpdates.injection.injectBatchingStrategy(ReactDefaultBatchingStrategy);
  /*********this-line*****************/

  ReactComponentEnvironment.injection.injectEnvironment(
    ReactComponentBrowserEnvironment,
  );

  findDOMNode._injectStack(function(inst) {
    inst = getHostComponentFromComposite(inst);
    return inst ? ReactDOMComponentTree.getNodeFromInstance(inst) : null;
  });
}

module.exports = {
  inject: inject,
};
```

然后就去看 ReactUpdates 的 injection:

```javascript
var ReactUpdatesInjection = {
  injectReconcileTransaction: function(ReconcileTransaction) {
    invariant(
      ReconcileTransaction,
      'ReactUpdates: must provide a reconcile transaction class',
    );
    ReactUpdates.ReactReconcileTransaction = ReconcileTransaction;
  },

  injectBatchingStrategy: function(_batchingStrategy) {
    invariant(
      _batchingStrategy,
      'ReactUpdates: must provide a batching strategy',
    );
    invariant(
      typeof _batchingStrategy.batchedUpdates === 'function',
      'ReactUpdates: must provide a batchedUpdates() function',
    );
    invariant(
      typeof _batchingStrategy.isBatchingUpdates === 'boolean',
      'ReactUpdates: must provide an isBatchingUpdates boolean attribute',
    );
    batchingStrategy = _batchingStrategy;
  },

  getBatchingStrategy: function() {
    return batchingStrategy;
  },
};

//...
var ReactUpdates = {
  /**
   * React references `ReactReconcileTransaction` using this property in order
   * to allow dependency injection.
   *
   * @internal
   */
  ReactReconcileTransaction: null,

  batchedUpdates: batchedUpdates,
  enqueueUpdate: enqueueUpdate,
  flushBatchedUpdates: flushBatchedUpdates,
  injection: ReactUpdatesInjection,
};

```

这个时候，需要把调用栈反过来看一下：
ReactUpdates.injection inject 了 ReactDefaultBatchingUpdates， 而 ReactDefaultBatchingUpdates 是一个 transaction，在其中一个 tansaction_wrapper 中，调用了 ReactUpdates.flushBatchedUpdates，然后在 flushBatchedUpdates 中又调用了 runBatchedUpdates 这个函数，而这个函数直接调用了 ReactReconciler 的 performUpdateIfNecessary，这个函数又把 performUpdateIfNecessary 的具体任务 delegate 到具体的 instance。

那么接下来应该如何继续探究下去呢？继续往上追溯，ReactUpdatesInjection 中提供了一个接口 getBatchingStrategy，就顺着它就行了。但是没发现有用的信息。

这个时候，我们在从 setState 开始看起:
```javascript
ReactComponent.prototype.setState = function(partialState, callback) {
  invariant(
    typeof partialState === 'object' ||
      typeof partialState === 'function' ||
      partialState == null,
    'setState(...): takes an object of state variables to update or a ' +
      'function which returns an object of state variables.',
  );
  this.updater.enqueueSetState(this, partialState, callback, 'setState');
};
```

这个是 ReactBaseClasses，老实说不是很清楚这个 class 有什么作用，基本上函数都是空的，不过如果这个 updater 用的不是默认值呢？我们可以从 enqueueSetState 这个方法入手，有这么几个类 ReactPartialRenderer 和 ReactUpdateQueue，但是 ReactPartialRenderer 是 server rendering，所以只看 ReactUpdateQueue 即可:
```javascript
/**
   * Sets a subset of the state. This only exists because _pendingState is
   * internal. This provides a merging strategy that is not available to deep
   * properties which is confusing. TODO: Expose pendingState or don't use it
   * during the merge.
   *
   * @param {ReactClass} publicInstance The instance that should rerender.
   * @param {object} partialState Next partial state to be merged with state.
   * @param {?function} callback Called after state is updated.
   * @param {?string} Name of the calling function in the public API.
   * @internal
   */
  enqueueSetState: function(
    publicInstance,
    partialState,
    callback,
    callerName,
  ) {
    if (__DEV__) {
      ReactInstrumentation.debugTool.onSetState();
      warning(
        partialState != null,
        'setState(...): You passed an undefined or null state object; ' +
          'instead, use forceUpdate().',
      );
    }

    var internalInstance = getInternalInstanceReadyForUpdate(publicInstance);

    if (!internalInstance) {
      return;
    }

    var queue =
      internalInstance._pendingStateQueue ||
      (internalInstance._pendingStateQueue = []);
    queue.push(partialState);

    callback = callback === undefined ? null : callback;
    if (callback !== null) {
      if (__DEV__) {
        warnOnInvalidCallback(callback, callerName);
      }
      if (internalInstance._pendingCallbacks) {
        internalInstance._pendingCallbacks.push(callback);
      } else {
        internalInstance._pendingCallbacks = [callback];
      }
    }

    enqueueUpdate(internalInstance);
  },
```

这个函数表明 partialState 会被存在 internalInstance._pendingStateQueue 中，然后会调用 enquereUpdate，这个函数实际上来自 ReactUpdates.js 中:

```javascript
/**
 * Mark a component as needing a rerender, adding an optional callback to a
 * list of functions which will be executed once the rerender occurs.
 */
function enqueueUpdate(component) {
  ensureInjected();

  // Various parts of our code (such as ReactCompositeComponent's
  // _renderValidatedComponent) assume that calls to render aren't nested;
  // verify that that's the case. (This is called by each top-level update
  // function, like setState, forceUpdate, etc.; creation and
  // destruction of top-level components is guarded in ReactMount.)

  if (!batchingStrategy.isBatchingUpdates) {
    batchingStrategy.batchedUpdates(enqueueUpdate, component);
    return;
  }

  dirtyComponents.push(component);
  if (component._updateBatchNumber == null) {
    component._updateBatchNumber = updateBatchNumber + 1;
  }
}
```

这个 batchedUpdates 其实就是上面提供的 ReactDefaultBatchingStrategy:

```javascript
var ReactDefaultBatchingStrategy = {
  isBatchingUpdates: false,

  /**
   * Call the provided function in a context within which calls to `setState`
   * and friends are batched such that components aren't updated unnecessarily.
   */
  batchedUpdates: function(callback, a, b, c, d, e) {
    var alreadyBatchingUpdates = ReactDefaultBatchingStrategy.isBatchingUpdates;

    ReactDefaultBatchingStrategy.isBatchingUpdates = true;

    // The code is written this way to avoid extra allocations
    if (alreadyBatchingUpdates) {
      return callback(a, b, c, d, e);
    } else {
      return transaction.perform(callback, null, a, b, c, d, e);
    }
  },
};
```

结合两段代码来看实际上是有两种情况，一种是正在 batching，还有一种是还没开始 batching，很容易理解，但是到目前为止似乎这个 BatchingStrategy 并没有做到 batching 这个功能，暂时先不管，继续往下看，在 transaction 的 perform 完成后，肯定是要调用 其创建时定义的 wrapper，我们也即是之前提到的:

```javascript
var RESET_BATCHED_UPDATES = {
  initialize: emptyFunction,
  close: function() {
    ReactDefaultBatchingStrategy.isBatchingUpdates = false;
  },
};

var FLUSH_BATCHED_UPDATES = {
  initialize: emptyFunction,
  close: ReactUpdates.flushBatchedUpdates.bind(ReactUpdates),
};
```
ReactUpdates.flushBatchedUpdates 被调用了，如果再深入下去，就可以回到我们开头的部分了。

目前总体看来还有一个问题，就是 setState 似乎完全不是 enqueue 的机制，但是它函数名还这么写，我们看到的是立即更新，并没有停一下再更新。
真的是这样吗？
看到这样一篇[文章](https://www.bennadel.com/blog/2893-setstate-state-mutation-operation-may-be-synchronous-in-reactjs.htm)，文中指只有在 onClick 的实践处理中 setState 是 equeue 机制的，在 event not managed by react 中又是同步的。

后来我进行断点调试，一步一步地进行两种情况的执行顺序，然后我发现，如果是通过 props 定义的事件响应，那么当使用 setState 的时候，触发的 enqueueUpdate:

```javascript

/**
 * Mark a component as needing a rerender, adding an optional callback to a
 * list of functions which will be executed once the rerender occurs.
 */
function enqueueUpdate(component) {
  ensureInjected();

  // Various parts of our code (such as ReactCompositeComponent's
  // _renderValidatedComponent) assume that calls to render aren't nested;
  // verify that that's the case. (This is called by each top-level update
  // function, like setState, forceUpdate, etc.; creation and
  // destruction of top-level components is guarded in ReactMount.)

  if (!batchingStrategy.isBatchingUpdates) {
    batchingStrategy.batchedUpdates(enqueueUpdate, component);
    return;
  }

  dirtyComponents.push(component);
  if (component._updateBatchNumber == null) {
    component._updateBatchNumber = updateBatchNumber + 1;
  }
}
```

中的 batchingStrategy.isBatchingUpdates 是 true 的，也就是说 setState 本身是处于一个 update 的 transaction 中的，所以 batchingStrategy.batchedUpdates 是不会调用的，因此如果不断的 setState 就会产生 state 本身不更新，并且将传入的 partialstate 逐步 batching，最终在触发 React 的 onClick 事件中引发的外层 update transaction 的 close 函数中进行最终的 update。
