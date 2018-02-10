# Raft 实现 - Election
#study/distribute-system

## 简介
election 作为 raft 的第一阶段，用于选出一个 leader，以供后续的同步操作。
election 的原理十分简单，即和真实的 election 类似，由某个 candidate 发起 votes，若是它得到了最多票，则其成为leader，否则本次 election 失败，自己转化成 follwer. 
。

## 算法实现
算法其实看起来很简单，然而实现方式才是关键，究竟如何实现才会保证可读性和好的维护性（_不容易出bug_）。

我第一次实现的时候，没有仔细多想，就直接开始实现，后来发现很多 bug 都难以解决，也许这就是一个小小的架构吧。

我所谓的直接实现，其实就是一个 raft server 应该做什么，然后就让他做什么，这也是比较直觉的想法。举个例子就是说，某个 raft server 作为 candidate 接收到了来自 leader 的 heartbeat，然后就直接停止了当前 request votes 的行为，这样做不好的原因就是你需要考虑各种情况下的行为，一旦考虑不对就可能出现 bug. 

那更优雅的方式是什么呢？
role → behavior
我们在接收到某种事件的时候，不直接做出响应，而是转变 role，而每种转换带来的行为，我们在其他地方集中管理，仅仅这样思路的转变，带来的效果却是拔群的.

那么按照这样的思路我们怎么实现 raft 呢？
1. 确定 raft 的 role
2. 确定每种 role 行为以及其转变 role 的时机
3. 解决线程安全的问题
4. ElectSelf & RequestVotes 的行为
5. SendHeartbeat & AcceptHeart 的行为

### raft 的 role
这个很简单，主要分为 follower candidate leader 三种，转化规则是：

follower → candidate → leader
↑----------------↓----------------↓

### 每种role的行为
**follower**
* 设置一个 timer，如果 timeout 了，role 会成为 candidate. timer 可以被 requestVotes 和 heartbeat 请求重置.

**candidate**
* 该身份持续时间比较短，因为成为 candidate 后需要立即发出 requestVotes 请求. 如果请求返回的结果同意的票数超过一半（这里是一个比较 tricky 的方法，因为本来只要是最多票即可，但是分布式的情况下比较难分辨这一点），role 转换成 leader，否则成为 follower. 这里需要注意的是，如果在请求过程中接收到 heartbeat 是需要将 role 变成 follower 的，因此如果采用直接写的方法，这段控制将会比较麻烦（需要单开一个线程监听相应的状态），如果采用 role 转化的方法就无须担心这点，在 role 上面作加锁做同步即可.

**leader**
* 作为 leader，需要完成的事情是不停地发出 heartbeat 信号以通知各个其他 server 自己存在.
* leader 可以转变为 follower，转变的时机是接受到来自其他 server 的 requestVotes 请求和 heartbeat 请求时发现请求中带着的 term 超过自己则转化成 follower

### 解决线程安全
线程安全的问题是必须考虑的问题，因为 Raft server 必然是一个多线程的问题：
* follower 需要一个 timer 的线程一直在等待触发
* 每一个 server 监听来自 leader 的 heartbeat
* 每一个 server 监听 candidate 的 requestVotes 请求

那么需要保护的变量是哪些呢？
* role
* curruentTerm
* voteFor

在实际过程中为了方便处理，这三个变量我设了两个锁，role 单独一个锁，currentTerm 和 voteFor 共享一把锁。

除此之外，我们还需要两个 flag 来标记 server 是否处于 waitingForElectSelf(即 timer 已经设置) 以及是否处于 sendingHeartbeats 的状态，这个也需要两把锁。

### ElectSelf & RequestVotes 的行为
ElectSelf 是属于 candidate 的行为，在成为 candidate 之后，立即触发这一行为：
1. 自增 currentTerm
2. 将 voteFor 记为 self
3. 向其他 server 发出 RequestVotes 的请求
4. 等待并搜集其他 server 的 response，若得到的票数(包括自己)超过一半并且未发现有超过自己 term 存在，则成功成为 leader。
5. 失败的情况较多：
* 在 electSelf 得过程中发现自己收到了来自 leader 的 heartbeat，失败
* 得到的票数少于一半，失败

6. 若失败，更新 voteFor 为 null，更新 currentTerm 到已知最新的
7. 若成功，转变成为 leader

RequestVotes 是由 candidate 发出，任何一个 Raft server 都得实现相应这个服务的相应方法，需要做如下事情：
若满足 term > currentTerm || term == currentTerm && voteFor == nullRFID（term 是来自 candidate 发出的请求中的参数，nullRFID 用以表示没有投任何票）则做如下的事情：
	* grant 本次 RequestVotes
	* 重置 electSelf 的 timer
	* 更新 currentTerm
	* 设置 voteFor 为 candidate

若不满足上述条件，则:
	* deny 本次 RequestVotes
	* 回复自己的 currentTerm 以供 candidate 自己更新

### SendHeartbeat & AcceptHeartbeat 的行为
SendHeartbeat 是 leader 的行为，每隔一段时间(小于 electSelf 的 waiting time)都要发出通知，告知其他的 server 自己作为 leader 的存在，可以重置其他 server 的 electSelf timer。

 SendHeartbeat 会带上自己的 server ID 和 currentTerm，如果得到 success 的 reply，则不做任何事情，否则：
    * 将自己的 voteFor 设为 nullRFID
    * 更新 currentTerm 如果有必要
    * role 更新为 follower

AcceptHeartbeat 的行为(在之后的博客我们会知道，AcceptHeartbeat 的其实就是 AppendEntries 的一个空请求)比较简单：
如果 AcceptHeartbeat 的请求中的(其实就是 leader 的) term >= currentTerm:
	* 将 voteFor  设置为 leaderID
	* 重置 electSelf timer
	* 更新 currentTerm
	* 通知 leader 此次 Heartbeat 成功通知到了

若未满足：
* 通知 leader 本次 Heartbeat 失败

## Reference
1. [extended Raft paper ](http://nil.csail.mit.edu/6.824/2016/papers/raft-extended.pdf)
2. [illustrated Raft guide ](http://thesecretlivesofdata.com/raft/)
