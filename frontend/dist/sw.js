if(!self.define){let e,i={};const n=(n,s)=>(n=new URL(n+".js",s).href,i[n]||new Promise((i=>{if("document"in self){const e=document.createElement("script");e.src=n,e.onload=i,document.head.appendChild(e)}else e=n,importScripts(n),i()})).then((()=>{let e=i[n];if(!e)throw new Error(`Module ${n} didn’t register its module`);return e})));self.define=(s,r)=>{const o=e||("document"in self?document.currentScript.src:"")||location.href;if(i[o])return;let c={};const t=e=>n(e,o),d={module:{uri:o},exports:c,require:t};i[o]=Promise.all(s.map((e=>d[e]||t(e)))).then((e=>(r(...e),c)))}}define(["./workbox-15aa4474"],(function(e){"use strict";self.skipWaiting(),e.clientsClaim(),e.precacheAndRoute([{url:"assets/index-032db19c.css",revision:null},{url:"assets/index-d49c5c91.js",revision:null},{url:"index.html",revision:"3f3787b4a3836179e918dc4ae3a85b48"},{url:"registerSW.js",revision:"1872c500de691dce40960bb85481de07"},{url:"favicon.ico",revision:"a8e60bc6b9bc9a9d68f3abf9872aedc2"},{url:"apple-touch-icon.png",revision:"9b350c9b919bc10c0476273651a1c79d"},{url:"pwa-192x192.png",revision:"590661131cb0de408fac1553bae89630"},{url:"pwa-512x512.png",revision:"b562299719e3de7b01f742b763b9eedf"},{url:"manifest.webmanifest",revision:"54185469b9662151ad5744049dc69fd3"}],{}),e.cleanupOutdatedCaches(),e.registerRoute(new e.NavigationRoute(e.createHandlerBoundToURL("index.html"),{denylist:[/^\/api/]}))}));
