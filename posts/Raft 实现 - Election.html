<!DOCTYPE html>
<html>
    <head>
        <title>Raft 实现 - Election</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="created" content="2018-01-17T09:18:40+0800"/>
        <meta name="modified" content="2018-01-31T00:37:20+0800"/>
        <meta name="tags" content="study/distribute-system, study"/>
        <meta name="last device" content="Xikai’s MBP"/>
    </head>
    <body>
        <div class="note-wrapper">
            <h1>Raft 实现 - Election</h1>
<p><span class='hashtag'>#study/distribute-system</span></p>
<br>
<h2>简介</h2>
<p>election 作为 raft 的第一阶段，用于选出一个 leader，以供后续的同步操作。</p>
<p>election 的原理十分简单，即和真实的 election 类似，由某个 candidate 发起 votes，若是它得到了最多票，则其成为leader，否则本次 election 失败，自己转化成 follwer. </p>
<p>。</p>
<br>
<h2>算法实现</h2>
<p>算法其实看起来很简单，然而实现方式才是关键，究竟如何实现才会保证可读性和好的维护性（/不容易出bug/）。</p>
<br>
<p>我第一次实现的时候，没有仔细多想，就直接开始实现，后来发现很多 bug 都难以解决，也许这就是一个小小的架构吧。</p>
<br>
<p>我所谓的直接实现，其实就是一个 raft server 应该做什么，然后就让他做什么，这也是比较直觉的想法。举个例子就是说，某个 raft server 作为 candidate 接收到了来自 leader 的 heartbeat，然后就直接停止了当前 request votes 的行为，这样做不好的原因就是你需要考虑各种情况下的行为，一旦考虑不对就可能出现 bug. </p>
<br>
<p>那更优雅的方式是什么呢？</p>
<p>role → behavior</p>
<p>我们在接收到某种事件的时候，不直接做出响应，而是转变 role，而每种转换带来的行为，我们在其他地方集中管理，仅仅这样思路的转变，带来的效果却是拔群的.</p>
<br>
<p>那么按照这样的思路我们怎么实现 raft 呢？</p>
<ol start="1"><li>确定 raft 的 role
</li><li>确定每种 role 行为以及其转变 role 的时机
</li><li>解决线程安全的问题
</li><li>ElectSelf & RequestVotes 的行为
</li><li>SendHeartbeat & AcceptHeart 的行为
</li></ol>
<br>
<h3>raft 的 role</h3>
<p>这个很简单，主要分为 follower candidate leader 三种，转化规则是：</p>
<br>
<p>follower → candidate → leader</p>
<p>↑----------------↓----------------↓</p>
<br>
<h3>每种role的行为</h3>
<p><i>follower</i></p>
<ul><li>设置一个 timer，如果 timeout 了，role 会成为 candidate. timer 可以被 requestVotes 和 heartbeat 请求重置.
</li></ul>
<br>
<p><i>candidate</i></p>
<ul><li>该身份持续时间比较短，因为成为 candidate 后需要立即发出 requestVotes 请求. 如果请求返回的结果同意的票数超过一半（这里是一个比较 tricky 的方法，因为本来只要是最多票即可，但是分布式的情况下比较难分辨这一点），role 转换成 leader，否则成为 follower. 这里需要注意的是，如果在请求过程中接收到 heartbeat 是需要将 role 变成 follower 的，因此如果采用直接写的方法，这段控制将会比较麻烦（需要单开一个线程监听相应的状态），如果采用 role 转化的方法就无须担心这点，在 role 上面作加锁做同步即可.
</li></ul>
<br>
<p><i>leader</i></p>
<ul><li>作为 leader，需要完成的事情是不停地发出 heartbeat 信号以通知各个其他 server 自己存在.
</li><li>leader 可以转变为 follower，转变的时机是接受到来自其他 server 的 requestVotes 请求和 heartbeat 请求时发现请求中带着的 term 超过自己则转化成 follower
</li></ul>
<br>
<h3>解决线程安全</h3>
<p>线程安全的问题是必须考虑的问题，因为 Raft server 必然是一个多线程的问题：</p>
<ul><li>follower 需要一个 timer 的线程一直在等待触发
</li><li>每一个 server 监听来自 leader 的 heartbeat
</li><li>每一个 server 监听 candidate 的 requestVotes 请求
</li></ul>
<br>
<p>那么需要保护的变量是哪些呢？</p>
<ul><li>role
</li><li>curruentTerm
</li><li>voteFor
</li></ul>
<br>
<p>在实际过程中为了方便处理，这三个变量我设了两个锁，role 单独一个锁，currentTerm 和 voteFor 共享一把锁。</p>
<br>
<p>除此之外，我们还需要两个 flag 来标记 server 是否处于 waitingForElectSelf(即 timer 已经设置) 以及是否处于 sendingHeartbeats 的状态，这个也需要两把锁。</p>
<br>
<h3>ElectSelf & RequestVotes 的行为</h3>
<p>ElectSelf 是属于 candidate 的行为，在成为 candidate 之后，立即触发这一行为：</p>
<ol start="1"><li>自增 currentTerm
</li><li>将 voteFor 记为 self
</li><li>向其他 server 发出 RequestVotes 的请求
</li><li>等待并搜集其他 server 的 response，若得到的票数(包括自己)超过一半并且未发现有超过自己 term 存在，则成功成为 leader。
</li><li>失败的情况较多：
</li></ol>
<ul><li>在 electSelf 得过程中发现自己收到了来自 leader 的 heartbeat，失败
</li><li>得到的票数少于一半，失败
</li></ul>
<br>
<ol start="6"><li>若失败，更新 voteFor 为 null，更新 currentTerm 到已知最新的
</li><li>若成功，转变成为 leader
</li></ol>
<br>
<p>RequestVotes 是由 candidate 发出，任何一个 Raft server 都得实现相应这个服务的相应方法，需要做如下事情：</p>
<p>若满足 term > currentTerm || term == currentTerm && voteFor == nullRFID（term 是来自 candidate 发出的请求中的参数，nullRFID 用以表示没有投任何票）则做如下的事情：</p>
<ul><li>  grant 本次 RequestVotes
</li><li>  重置 electSelf 的 timer
</li><li>  更新 currentTerm
</li><li>  设置 voteFor 为 candidate
</li></ul>
<br>
<p>若不满足上述条件，则:</p>
<ul><li>  deny 本次 RequestVotes
</li><li>  回复自己的 currentTerm 以供 candidate 自己更新
</li></ul>
<br>
<h3>SendHeartbeat & AcceptHeartbeat 的行为</h3>
<p>SendHeartbeat 是 leader 的行为，每隔一段时间(小于 electSelf 的 waiting time)都要发出通知，告知其他的 server 自己作为 leader 的存在，可以重置其他 server 的 electSelf timer。</p>
<br>
<p> SendHeartbeat 会带上自己的 server ID 和 currentTerm，如果得到 success 的 reply，则不做任何事情，否则：</p>
<ul><li>    将自己的 voteFor 设为 nullRFID
</li><li>    更新 currentTerm 如果有必要
</li><li>    role 更新为 follower
</li></ul>
<br>
<p>AcceptHeartbeat 的行为(在之后的博客我们会知道，AcceptHeartbeat 的其实就是 AppendEntries 的一个空请求)比较简单：</p>
<p>如果 AcceptHeartbeat 的请求中的(其实就是 leader 的) term >= currentTerm:</p>
<ul><li>  将 voteFor  设置为 leaderID
</li><li>  重置 electSelf timer
</li><li>  更新 currentTerm
</li><li>  通知 leader 此次 Heartbeat 成功通知到了
</li></ul>
<br>
<p>若未满足：</p>
<ul><li> 通知 leader 本次 Heartbeat 失败
</li></ul>
<br>
<h2>Reference</h2>
<ol start="1"><li><a href="http://nil.csail.mit.edu/6.824/2016/papers/raft-extended.pdf">extended Raft paper </a>
</li><li><a href="http://thesecretlivesofdata.com/raft/">illustrated Raft guide </a></li></ol>

        </div>
        <script type="text/javascript">
            (function() {

    var doc_ols = document.getElementsByTagName("ol");

    for ( i=0; i<doc_ols.length; i++) {

        var ol_start = doc_ols[i].getAttribute("start") - 1;
        doc_ols[i].setAttribute("style", "counter-reset:ol " + ol_start + ";");

    }

})();
        </script>
        <style>
            html,body,div,span,applet,object,iframe,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,abbr,acronym,address,big,cite,code,del,dfn,em,img,ins,kbd,q,s,samp,small,strike,strong,sub,sup,tt,var,b,u,i,center,dl,dt,dd,ol,ul,li,fieldset,form,label,legend,table,caption,tbody,tfoot,thead,tr,th,td,article,aside,canvas,details,embed,figure,figcaption,footer,header,hgroup,menu,nav,output,ruby,section,summary,time,mark,audio,video{margin:0;padding:0;border:0;font:inherit;font-size:100%;vertical-align:baseline}html{line-height:1}ol,ul{list-style:none}table{border-collapse:collapse;border-spacing:0}caption,th,td{text-align:left;font-weight:normal;vertical-align:middle}q,blockquote{quotes:none}q:before,q:after,blockquote:before,blockquote:after{content:"";content:none}a img{border:none}article,aside,details,figcaption,figure,footer,header,hgroup,main,menu,nav,section,summary{display:block}*{-moz-box-sizing:border-box;-webkit-box-sizing:border-box;box-sizing:border-box}html{font-size:87.5%;line-height:1.57143em}html{font-size:14px;line-height:1.6em;-webkit-text-size-adjust:100%}body{background:#fcfcfc;color:#545454;text-rendering:optimizeLegibility;font-family:"AvenirNext-Regular"}a{color:#de4c4f;text-decoration:none}h1{font-family:"AvenirNext-Medium";color:#333;font-size:1.6em;line-height:1.3em;margin-bottom:.78571em}h2{font-family:"AvenirNext-Medium";color:#333;font-size:1.3em;line-height:1em;margin-bottom:.62857em}h3{font-family:"AvenirNext-Medium";color:#333;font-size:1.15em;line-height:1em;margin-bottom:.47143em}p{margin-bottom:1.57143em;hyphens:auto}hr{height:1px;border:0;background-color:#dedede;margin:-1px auto 1.57143em auto}ul,ol{margin-bottom:.31429em}ul ul,ul ol,ol ul,ol ol{margin-bottom:0px}ol li:before{content:counter(ol) ".";counter-increment:ol;color:#e06e73;text-align:right;display:inline-block;min-width:1em;margin-right:0.5em}b,strong{font-family:"AvenirNext-Bold"}i,em{font-family:"AvenirNext-Italic"}code{font-family:"Menlo-Regular"}.text-overflow-ellipsis{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.sf_code_syntax_string{color:#D33905}.sf_code_syntax_comment{color:#838383}.sf_code_syntax_documentation_comment{color:#128901}.sf_code_syntax_number{color:#0E73A2}.sf_code_syntax_project{color:#5B2599}.sf_code_syntax_keyword{color:#0E73A2}.sf_code_syntax_character{color:#1B00CE}.sf_code_syntax_preprocessor{color:#920448}.note-wrapper{max-width:46em;margin:0px auto;padding:1.57143em 3.14286em}.note-wrapper.spotlight-preview{overflow-x:hidden}u{text-decoration:none;background-image:linear-gradient(to bottom, rgba(0,0,0,0) 50%,#e06e73 50%);background-repeat:repeat-x;background-size:2px 2px;background-position:0 1.05em}s{color:#878787}p{margin-bottom:0.1em}hr{margin-bottom:0.7em;margin-top:0.7em}ul li{text-indent:-0.35em}ul li:before{content:"•";color:#e06e73;display:inline-block;margin-right:0.3em}ul ul{margin-left:1.25714em}ol li{text-indent:-1.45em}ol ol{margin-left:1.25714em}blockquote{display:block;margin-left:-1em;padding-left:0.8em;border-left:0.2em solid #e06e73}.todo-list ul{margin-left:1.88571em}.todo-list li{text-indent:-1.75em}.todo-list li:before{content:"";display:static;margin-right:0px}.todo-checkbox{text-indent:-1.7em}.todo-checkbox svg{margin-right:0.3em;position:relative;top:0.2em}.todo-checkbox svg #check{display:none}.todo-checkbox.todo-checked #check{display:inline}.todo-checkbox.todo-checked .todo-text{text-decoration:line-through;color:#878787}.code-inline{display:inline;background:white;border:solid 1px #dedede;padding:0.2em 0.5em;font-size:0.9em}.code-multiline{display:block;background:white;border:solid 1px #dedede;padding:0.7em 1em;font-size:0.9em;overflow-x:auto}.hashtag{display:inline-block;color:white;background:#b8bfc2;padding:0.0em 0.5em;border-radius:1em;text-indent:0}.hashtag a{color:#fff}.address a{color:#545454;background-image:linear-gradient(to bottom, rgba(0,0,0,0) 50%,#0da35e 50%);background-repeat:repeat-x;background-size:2px 2px;background-position:0 1.05em}.address svg{position:relative;top:0.2em;display:inline-block;margin-right:0.2em}.color-preview{display:inline-block;width:1em;height:1em;border:solid 1px rgba(0,0,0,0.3);border-radius:50%;margin-right:0.1em;position:relative;top:0.2em;white-space:nowrap}.color-code{margin-right:0.2em;font-family:"Menlo-Regular";font-size:0.9em}.color-hash{opacity:0.4}.ordered-list-number{color:#e06e73;text-align:right;display:inline-block;min-width:1em}.arrow svg{position:relative;top:0.08em;display:inline-block;margin-right:0.15em;margin-left:0.15em}.arrow svg #rod{stroke:#545454}.arrow svg #point{fill:#545454}mark{color:inherit;display:inline-block;padding:0px 4px;background-color:#fcffc0}img{max-width:100%;height:auto}

        </style>
    </body>
</html>
