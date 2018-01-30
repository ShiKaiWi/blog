>title: CSS-Animation
>date: 2017-07-25 23:23:04
>tags: css

## transform
transform 是变换的基础，常用的操作主要有 scale，rotate，translate(translateX/Y)。
在使用的时候会遇到以下几个注意点：
1. scale 和 rotate 操作肯定是需要指定变换原点的，那么默认的原点是什么呢？答案是中心。
2. 那么根据 1，如果我们不想使用中心作为变换原点怎么办？答案是使用 transform-origin。
3. 还有一个 rotate，仅仅有一个转换原点还不够，还有旋转方向的设定，比如 rotate(45deg) 其实是指逆时针旋转 45 度。
4. 此外，translateY(-50%) 的 50% 是指元素本身的一半高度。
5. 其实要做二维变换可以是使用 matrix(a, b, c, d, tx, ty) 来做任意的转换


## transition
transition 其实就是一种简单的动画，和 animation 的区别只是在于没法将动画过程进行细分，只能对开始和最后的设定值进行动画设定，并且可以使用 timing-function 来控制动画的播放。
MDN 上的定义：transition: <property> <duration> <timing-function> <delay>;

## animation
animation 必须配合 @keyframe 来使用，其实就是高级版的 transition。

## bezier function
由于 timing-function 比较容易使用的是 bezier function（贝塞尔函数），所以想要对它多了解一点。
