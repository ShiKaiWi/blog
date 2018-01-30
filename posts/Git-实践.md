>title: Git-实践
>date: 2017-03-05 14:51:47
>tags: git

### 1. git merge 时发生了什么? 如何处理？

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

### 2. arc 如何结合 phabricator 使用？
phabricator 是一种工程代码管理集成工具，arc 是进行 phabricator 上的 code review 的重要工具，那么如何使用 arc 呢？
#### 安装 arc
参考 [这里](https://secure.phabricator.com/book/phabricator/article/arcanist_quick_start/)
#### 一次 feature/bug 的提交过程
1. `git pull` 保证 master 分支最新
2. `git checkout -b feature/xxx` 进行代码开发
3. `git add <files needed to be committed>; git commit -m "..."` commit 代码
4. `arc diff` 这个时候提交 diff，根据提示需要指定 diff 的 base，如果你只是 commit 过一次，那么一般使用 HEAD^ 作为 base（这也是默认选项）如果觉得不放心的话，最好使用 `arc diff --preiview` 来确认一下自己这次 diff 的提交是否出错
5. 代码 review 时出现需要改动的地方，那么改动代码后，使用 `git commit --amend` 来进行 commit，这样就会保证始终只有一次 commit，这样的话，就会方便每次 arc diff 的时候，不必指定 base
6. review 通过以后 `arc land` 会将该分支 merge 到 master

#### 如果 land diff 的时候发现 master 已经更新，并且 merge 有冲突
1. 本地 merge 一次（解决冲突、add file、commit）
2. 再次更新 diff，将 base 设为最新的 master head，等待 review
更好的解决办法是：
1. `git checkout master`
2. `git pull`
3. `git checkout <diff-branch>`
4. `git rebase master`
5. 若是出现冲突，merge 完毕后，可以使用 `rebase --continue`
6. `arc diff HEAD^`

### 3. git 如何切换到任意结点下的某一个文件？
`git checkout <commit-hash> path/to/file`
