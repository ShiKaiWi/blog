---
title: WebServer-Architecture
tags: http webserver
---

## Web Server Software
Web Server Software is different from Web Server Program whose number is much greater.

## Accepting Client Connections
Identification is main work in this proceduer:
+ Use `reverse DNS` to find out the hostname for some particular IP but this feature is always disabled because of its monster waste of time.
+ `ident` protocool makes server send a request to the client who is always running identd Identification Protocol daemon software. However, this is not common in public internet because its dangerous and unsecurity.

## 
 