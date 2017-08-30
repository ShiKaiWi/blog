---
title: CSS-Tricks-Record
date: 2017-07-30 15:34:47
tags:
---

## 画尖角
#test-div {	
	position: absolute;
	width: 14em;
	padding: .6em .8em;
	border-radius: .3em;
	margin: .3em 0 0 -.2em;
	background: #fed;
	border: 1px solid rgba(0,0,0,.3);
	box-shadow: .05em .2em .6em rgba(0,0,0,.2);
	font-size: 75%;
}

#test-div:before {
	content: "";
	position: absolute;
	top: calc(50%);
	left: 100%;
	padding: .35em;
	background: inherit;
	border: inherit;
	border-right: 0;
	border-bottom: 0;
	transform: translateY(-50%) translateX(-50%) rotate(135deg) ;
}