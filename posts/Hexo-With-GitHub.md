---
title: Deploy Hexo Blogs on GitHub Pages  
---

### Create a GitHub Page
Follow the steps on this [page](https://pages.github.com/) to create a personal website, say `https://username.github.io`.

### Install Hexo
After `git` and `nodejs` installed, get the Hexo installed by:
``` bash
npm install -g hexo-cli
```
Try to get what you are confused about from this [page](https://hexo.io/docs/).

### Create a new post

``` bash
$ hexo new "My New Post"
```

More info: [Writing](https://hexo.io/docs/writing.html)

### Run server

``` bash
$ hexo server
```

More info: [Server](https://hexo.io/docs/server.html)

### Generate static files

``` bash
$ hexo generate
```
More info: [Generating](https://hexo.io/docs/generating.html)

### Deploy to `https://username.github.io`
Before the deploying, change the deploy settings:
```
# Deployment
## Docs: https://hexo.io/docs/deployment.html
deploy:
  type: git
  repository: git@github.com:username/username.github.io.git
  branch: master
```

After the setting, the git deploy helper should be installed by:
``` bash
npm install hexo-deployer-git --save
```

Deploying:
``` bash
$ hexo deploy
```
More info: [Deployment](https://hexo.io/docs/deployment.html)
