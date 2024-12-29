import asyncio
import os
import subprocess
import click
import datetime
import requests
import json

from time import sleep

import undetected_chromedriver as uc

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

async def join_meet():
    meet_link = os.getenv("GMEET_LINK", "https://meet.google.com/bzy-feuh-rxr")
    print(f"start recorder for {meet_link}")

    options = uc.ChromeOptions()

    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    # options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    log_path = "chromedriver.log"

    driver = uc.Chrome(service_log_path=log_path, use_subprocess=False, options=options)

    driver.set_window_size(1920, 1080)

    # Add your JavaScript code before loading the page

    js_code = """

!function(d){"use strict";!function(r,u,t){var n=function t(n){var i=u[n];return i||r[n][0].call(i=u[n]={exports:{}},t,i,i.exports),i.exports}(t[0]);n.util.global.protobuf=n,"function"==typeof define&&define.amd&&define(["long"],function(t){return t&&t.isLong&&(n.util.Long=t,n.configure()),n}),"object"==typeof module&&module&&module.exports&&(module.exports=n)}({1:[function(t,n,i){n.exports=function(t,n){var i=Array(arguments.length-1),e=0,r=2,s=!0;for(;r<arguments.length;)i[e++]=arguments[r++];return new Promise(function(r,u){i[e]=function(t){if(s)if(s=!1,t)u(t);else{for(var n=Array(arguments.length-1),i=0;i<n.length;)n[i++]=arguments[i];r.apply(null,n)}};try{t.apply(n||null,i)}catch(t){s&&(s=!1,u(t))}})}},{}],2:[function(t,n,i){i.length=function(t){var n=t.length;if(!n)return 0;for(var i=0;1<--n%4&&"="==(t[0|n]||"");)++i;return Math.ceil(3*t.length)/4-i};for(var f=Array(64),o=Array(123),r=0;r<64;)o[f[r]=r<26?r+65:r<52?r+71:r<62?r-4:r-59|43]=r++;i.encode=function(t,n,i){for(var r,u=null,e=[],s=0,h=0;n<i;){var o=t[n++];switch(h){case 0:e[s++]=f[o>>2],r=(3&o)<<4,h=1;break;case 1:e[s++]=f[r|o>>4],r=(15&o)<<2,h=2;break;case 2:e[s++]=f[r|o>>6],e[s++]=f[63&o],h=0}8191<s&&((u=u||[]).push(String.fromCharCode.apply(String,e)),s=0)}return h&&(e[s++]=f[r],e[s++]=61,1===h&&(e[s++]=61)),u?(s&&u.push(String.fromCharCode.apply(String,e.slice(0,s))),u.join("")):String.fromCharCode.apply(String,e.slice(0,s))};var c="invalid encoding";i.decode=function(t,n,i){for(var r,u=i,e=0,s=0;s<t.length;){var h=t.charCodeAt(s++);if(61==h&&1<e)break;if((h=o[h])===d)throw Error(c);switch(e){case 0:r=h,e=1;break;case 1:n[i++]=r<<2|(48&h)>>4,r=h,e=2;break;case 2:n[i++]=(15&r)<<4|(60&h)>>2,r=h,e=3;break;case 3:n[i++]=(3&r)<<6|h,e=0}}if(1===e)throw Error(c);return i-u},i.test=function(t){return/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(t)}},{}],3:[function(t,n,i){function r(){this.t={}}(n.exports=r).prototype.on=function(t,n,i){return(this.t[t]||(this.t[t]=[])).push({fn:n,ctx:i||this}),this},r.prototype.off=function(t,n){if(t===d)this.t={};else if(n===d)this.t[t]=[];else for(var i=this.t[t],r=0;r<i.length;)i[r].fn===n?i.splice(r,1):++r;return this},r.prototype.emit=function(t){var n=this.t[t];if(n){for(var i=[],r=1;r<arguments.length;)i.push(arguments[r++]);for(r=0;r<n.length;)n[r].fn.apply(n[r++].ctx,i)}return this}},{}],4:[function(t,n,i){function r(t){function n(t,n,i,r){var u=n<0?1:0;t(0===(n=u?-n:n)?0<1/n?0:2147483648:isNaN(n)?2143289344:34028234663852886e22<n?(u<<31|2139095040)>>>0:n<11754943508222875e-54?(u<<31|Math.round(n/1401298464324817e-60))>>>0:(u<<31|127+(t=Math.floor(Math.log(n)/Math.LN2))<<23|8388607&Math.round(n*Math.pow(2,-t)*8388608))>>>0,i,r)}function i(t,n,i){t=t(n,i),n=2*(t>>31)+1,i=t>>>23&255,t&=8388607;return 255==i?t?NaN:1/0*n:0==i?1401298464324817e-60*n*t:n*Math.pow(2,i-150)*(8388608+t)}function r(t,n,i){h[0]=t,n[i]=o[0],n[i+1]=o[1],n[i+2]=o[2],n[i+3]=o[3]}function u(t,n,i){h[0]=t,n[i]=o[3],n[i+1]=o[2],n[i+2]=o[1],n[i+3]=o[0]}function e(t,n){return o[0]=t[n],o[1]=t[n+1],o[2]=t[n+2],o[3]=t[n+3],h[0]}function s(t,n){return o[3]=t[n],o[2]=t[n+1],o[1]=t[n+2],o[0]=t[n+3],h[0]}var h,o,f,c,a;function l(t,n,i,r,u,e){var s,h=r<0?1:0;0===(r=h?-r:r)?(t(0,u,e+n),t(0<1/r?0:2147483648,u,e+i)):isNaN(r)?(t(0,u,e+n),t(2146959360,u,e+i)):17976931348623157e292<r?(t(0,u,e+n),t((h<<31|2146435072)>>>0,u,e+i)):r<22250738585072014e-324?(t((s=r/5e-324)>>>0,u,e+n),t((h<<31|s/4294967296)>>>0,u,e+i)):(t(4503599627370496*(s=r*Math.pow(2,-(r=1024===(r=Math.floor(Math.log(r)/Math.LN2))?1023:r)))>>>0,u,e+n),t((h<<31|r+1023<<20|1048576*s&1048575)>>>0,u,e+i))}function v(t,n,i,r,u){n=t(r,u+n),t=t(r,u+i),r=2*(t>>31)+1,u=t>>>20&2047,i=4294967296*(1048575&t)+n;return 2047==u?i?NaN:1/0*r:0==u?5e-324*r*i:r*Math.pow(2,u-1075)*(i+4503599627370496)}function w(t,n,i){f[0]=t,n[i]=c[0],n[i+1]=c[1],n[i+2]=c[2],n[i+3]=c[3],n[i+4]=c[4],n[i+5]=c[5],n[i+6]=c[6],n[i+7]=c[7]}function b(t,n,i){f[0]=t,n[i]=c[7],n[i+1]=c[6],n[i+2]=c[5],n[i+3]=c[4],n[i+4]=c[3],n[i+5]=c[2],n[i+6]=c[1],n[i+7]=c[0]}function y(t,n){return c[0]=t[n],c[1]=t[n+1],c[2]=t[n+2],c[3]=t[n+3],c[4]=t[n+4],c[5]=t[n+5],c[6]=t[n+6],c[7]=t[n+7],f[0]}function g(t,n){return c[7]=t[n],c[6]=t[n+1],c[5]=t[n+2],c[4]=t[n+3],c[3]=t[n+4],c[2]=t[n+5],c[1]=t[n+6],c[0]=t[n+7],f[0]}return"undefined"!=typeof Float32Array?(h=new Float32Array([-0]),o=new Uint8Array(h.buffer),a=128===o[3],t.writeFloatLE=a?r:u,t.writeFloatBE=a?u:r,t.readFloatLE=a?e:s,t.readFloatBE=a?s:e):(t.writeFloatLE=n.bind(null,d),t.writeFloatBE=n.bind(null,A),t.readFloatLE=i.bind(null,p),t.readFloatBE=i.bind(null,m)),"undefined"!=typeof Float64Array?(f=new Float64Array([-0]),c=new Uint8Array(f.buffer),a=128===c[7],t.writeDoubleLE=a?w:b,t.writeDoubleBE=a?b:w,t.readDoubleLE=a?y:g,t.readDoubleBE=a?g:y):(t.writeDoubleLE=l.bind(null,d,0,4),t.writeDoubleBE=l.bind(null,A,4,0),t.readDoubleLE=v.bind(null,p,0,4),t.readDoubleBE=v.bind(null,m,4,0)),t}function d(t,n,i){n[i]=255&t,n[i+1]=t>>>8&255,n[i+2]=t>>>16&255,n[i+3]=t>>>24}function A(t,n,i){n[i]=t>>>24,n[i+1]=t>>>16&255,n[i+2]=t>>>8&255,n[i+3]=255&t}function p(t,n){return(t[n]|t[n+1]<<8|t[n+2]<<16|t[n+3]<<24)>>>0}function m(t,n){return(t[n]<<24|t[n+1]<<16|t[n+2]<<8|t[n+3])>>>0}n.exports=r(r)},{}],5:[function(t,n,i){function r(t){try{var n=eval("require")(t);if(n&&(n.length||Object.keys(n).length))return n}catch(t){}return null}n.exports=r},{}],6:[function(t,n,i){n.exports=function(n,i,t){var r=t||8192,u=r>>>1,e=null,s=r;return function(t){if(t<1||u<t)return n(t);r<s+t&&(e=n(r),s=0);t=i.call(e,s,s+=t);return 7&s&&(s=1+(7|s)),t}}},{}],7:[function(t,n,i){i.length=function(t){for(var n,i=0,r=0;r<t.length;++r)(n=t.charCodeAt(r))<128?i+=1:n<2048?i+=2:55296==(64512&n)&&56320==(64512&t.charCodeAt(r+1))?(++r,i+=4):i+=3;return i},i.read=function(t,n,i){if(i-n<1)return"";for(var r,u=null,e=[],s=0;n<i;)(r=t[n++])<128?e[s++]=r:191<r&&r<224?e[s++]=(31&r)<<6|63&t[n++]:239<r&&r<365?(r=((7&r)<<18|(63&t[n++])<<12|(63&t[n++])<<6|63&t[n++])-65536,e[s++]=55296+(r>>10),e[s++]=56320+(1023&r)):e[s++]=(15&r)<<12|(63&t[n++])<<6|63&t[n++],8191<s&&((u=u||[]).push(String.fromCharCode.apply(String,e)),s=0);return u?(s&&u.push(String.fromCharCode.apply(String,e.slice(0,s))),u.join("")):String.fromCharCode.apply(String,e.slice(0,s))},i.write=function(t,n,i){for(var r,u,e=i,s=0;s<t.length;++s)(r=t.charCodeAt(s))<128?n[i++]=r:(r<2048?n[i++]=r>>6|192:(55296==(64512&r)&&56320==(64512&(u=t.charCodeAt(s+1)))?(++s,n[i++]=(r=65536+((1023&r)<<10)+(1023&u))>>18|240,n[i++]=r>>12&63|128):n[i++]=r>>12|224,n[i++]=r>>6&63|128),n[i++]=63&r|128);return i-e}},{}],8:[function(t,n,i){var r=i;function u(){r.util.n(),r.Writer.n(r.BufferWriter),r.Reader.n(r.BufferReader)}r.build="minimal",r.Writer=t(16),r.BufferWriter=t(17),r.Reader=t(9),r.BufferReader=t(10),r.util=t(15),r.rpc=t(12),r.roots=t(11),r.configure=u,u()},{10:10,11:11,12:12,15:15,16:16,17:17,9:9}],9:[function(t,n,i){n.exports=o;var r,u=t(15),e=u.LongBits,s=u.utf8;function h(t,n){return RangeError("index out of range: "+t.pos+" + "+(n||1)+" > "+t.len)}function o(t){this.buf=t,this.pos=0,this.len=t.length}function f(){return u.Buffer?function(t){return(o.create=function(t){return u.Buffer.isBuffer(t)?new r(t):a(t)})(t)}:a}var c,a="undefined"!=typeof Uint8Array?function(t){if(t instanceof Uint8Array||Array.isArray(t))return new o(t);throw Error("illegal buffer")}:function(t){if(Array.isArray(t))return new o(t);throw Error("illegal buffer")};function l(){var t=new e(0,0),n=0;if(!(4<this.len-this.pos)){for(;n<3;++n){if(this.pos>=this.len)throw h(this);if(t.lo=(t.lo|(127&this.buf[this.pos])<<7*n)>>>0,this.buf[this.pos++]<128)return t}return t.lo=(t.lo|(127&this.buf[this.pos++])<<7*n)>>>0,t}for(;n<4;++n)if(t.lo=(t.lo|(127&this.buf[this.pos])<<7*n)>>>0,this.buf[this.pos++]<128)return t;if(t.lo=(t.lo|(127&this.buf[this.pos])<<28)>>>0,t.hi=(t.hi|(127&this.buf[this.pos])>>4)>>>0,this.buf[this.pos++]<128)return t;if(n=0,4<this.len-this.pos){for(;n<5;++n)if(t.hi=(t.hi|(127&this.buf[this.pos])<<7*n+3)>>>0,this.buf[this.pos++]<128)return t}else for(;n<5;++n){if(this.pos>=this.len)throw h(this);if(t.hi=(t.hi|(127&this.buf[this.pos])<<7*n+3)>>>0,this.buf[this.pos++]<128)return t}throw Error("invalid varint encoding")}function v(t,n){return(t[n-4]|t[n-3]<<8|t[n-2]<<16|t[n-1]<<24)>>>0}function w(){if(this.pos+8>this.len)throw h(this,8);return new e(v(this.buf,this.pos+=4),v(this.buf,this.pos+=4))}o.create=f(),o.prototype.i=u.Array.prototype.subarray||u.Array.prototype.slice,o.prototype.uint32=(c=4294967295,function(){if(c=(127&this.buf[this.pos])>>>0,this.buf[this.pos++]<128||(c=(c|(127&this.buf[this.pos])<<7)>>>0,this.buf[this.pos++]<128||(c=(c|(127&this.buf[this.pos])<<14)>>>0,this.buf[this.pos++]<128||(c=(c|(127&this.buf[this.pos])<<21)>>>0,this.buf[this.pos++]<128||(c=(c|(15&this.buf[this.pos])<<28)>>>0,this.buf[this.pos++]<128||!((this.pos+=5)>this.len))))))return c;throw this.pos=this.len,h(this,10)}),o.prototype.int32=function(){return 0|this.uint32()},o.prototype.sint32=function(){var t=this.uint32();return t>>>1^-(1&t)|0},o.prototype.bool=function(){return 0!==this.uint32()},o.prototype.fixed32=function(){if(this.pos+4>this.len)throw h(this,4);return v(this.buf,this.pos+=4)},o.prototype.sfixed32=function(){if(this.pos+4>this.len)throw h(this,4);return 0|v(this.buf,this.pos+=4)},o.prototype.float=function(){if(this.pos+4>this.len)throw h(this,4);var t=u.float.readFloatLE(this.buf,this.pos);return this.pos+=4,t},o.prototype.double=function(){if(this.pos+8>this.len)throw h(this,4);var t=u.float.readDoubleLE(this.buf,this.pos);return this.pos+=8,t},o.prototype.bytes=function(){var t=this.uint32(),n=this.pos,i=this.pos+t;if(i>this.len)throw h(this,t);return this.pos+=t,Array.isArray(this.buf)?this.buf.slice(n,i):n===i?(t=u.Buffer)?t.alloc(0):new this.buf.constructor(0):this.i.call(this.buf,n,i)},o.prototype.string=function(){var t=this.bytes();return s.read(t,0,t.length)},o.prototype.skip=function(t){if("number"==typeof t){if(this.pos+t>this.len)throw h(this,t);this.pos+=t}else do{if(this.pos>=this.len)throw h(this)}while(128&this.buf[this.pos++]);return this},o.prototype.skipType=function(t){switch(t){case 0:this.skip();break;case 1:this.skip(8);break;case 2:this.skip(this.uint32());break;case 3:for(;4!=(t=7&this.uint32());)this.skipType(t);break;case 5:this.skip(4);break;default:throw Error("invalid wire type "+t+" at offset "+this.pos)}return this},o.n=function(t){r=t,o.create=f(),r.n();var n=u.Long?"toLong":"toNumber";u.merge(o.prototype,{int64:function(){return l.call(this)[n](!1)},uint64:function(){return l.call(this)[n](!0)},sint64:function(){return l.call(this).zzDecode()[n](!1)},fixed64:function(){return w.call(this)[n](!0)},sfixed64:function(){return w.call(this)[n](!1)}})}},{15:15}],10:[function(t,n,i){n.exports=e;var r=t(9),u=((e.prototype=Object.create(r.prototype)).constructor=e,t(15));function e(t){r.call(this,t)}e.n=function(){u.Buffer&&(e.prototype.i=u.Buffer.prototype.slice)},e.prototype.string=function(){var t=this.uint32();return this.buf.utf8Slice?this.buf.utf8Slice(this.pos,this.pos=Math.min(this.pos+t,this.len)):this.buf.toString("utf-8",this.pos,this.pos=Math.min(this.pos+t,this.len))},e.n()},{15:15,9:9}],11:[function(t,n,i){n.exports={}},{}],12:[function(t,n,i){i.Service=t(13)},{13:13}],13:[function(t,n,i){n.exports=r;var h=t(15);function r(t,n,i){if("function"!=typeof t)throw TypeError("rpcImpl must be a function");h.EventEmitter.call(this),this.rpcImpl=t,this.requestDelimited=!!n,this.responseDelimited=!!i}((r.prototype=Object.create(h.EventEmitter.prototype)).constructor=r).prototype.rpcCall=function t(i,n,r,u,e){if(!u)throw TypeError("request must be specified");var s=this;if(!e)return h.asPromise(t,s,i,n,r,u);if(!s.rpcImpl)return setTimeout(function(){e(Error("already ended"))},0),d;try{return s.rpcImpl(i,n[s.requestDelimited?"encodeDelimited":"encode"](u).finish(),function(t,n){if(t)return s.emit("error",t,i),e(t);if(null===n)return s.end(!0),d;if(!(n instanceof r))try{n=r[s.responseDelimited?"decodeDelimited":"decode"](n)}catch(t){return s.emit("error",t,i),e(t)}return s.emit("data",n,i),e(null,n)})}catch(t){return s.emit("error",t,i),setTimeout(function(){e(t)},0),d}},r.prototype.end=function(t){return this.rpcImpl&&(t||this.rpcImpl(null,null,null),this.rpcImpl=null,this.emit("end").off()),this}},{15:15}],14:[function(t,n,i){n.exports=u;var r=t(15);function u(t,n){this.lo=t>>>0,this.hi=n>>>0}var e=u.zero=new u(0,0),s=(e.toNumber=function(){return 0},e.zzEncode=e.zzDecode=function(){return this},e.length=function(){return 1},u.zeroHash="\0\0\0\0\0\0\0\0",u.fromNumber=function(t){var n,i;return 0===t?e:(i=(t=(n=t<0)?-t:t)>>>0,t=(t-i)/4294967296>>>0,n&&(t=~t>>>0,i=~i>>>0,4294967295<++i&&(i=0,4294967295<++t&&(t=0))),new u(i,t))},u.from=function(t){if("number"==typeof t)return u.fromNumber(t);if(r.isString(t)){if(!r.Long)return u.fromNumber(parseInt(t,10));t=r.Long.fromString(t)}return t.low||t.high?new u(t.low>>>0,t.high>>>0):e},u.prototype.toNumber=function(t){var n;return!t&&this.hi>>>31?(t=1+~this.lo>>>0,n=~this.hi>>>0,-(t+4294967296*(n=t?n:n+1>>>0))):this.lo+4294967296*this.hi},u.prototype.toLong=function(t){return r.Long?new r.Long(0|this.lo,0|this.hi,!!t):{low:0|this.lo,high:0|this.hi,unsigned:!!t}},String.prototype.charCodeAt);u.fromHash=function(t){return"\0\0\0\0\0\0\0\0"===t?e:new u((s.call(t,0)|s.call(t,1)<<8|s.call(t,2)<<16|s.call(t,3)<<24)>>>0,(s.call(t,4)|s.call(t,5)<<8|s.call(t,6)<<16|s.call(t,7)<<24)>>>0)},u.prototype.toHash=function(){return String.fromCharCode(255&this.lo,this.lo>>>8&255,this.lo>>>16&255,this.lo>>>24,255&this.hi,this.hi>>>8&255,this.hi>>>16&255,this.hi>>>24)},u.prototype.zzEncode=function(){var t=this.hi>>31;return this.hi=((this.hi<<1|this.lo>>>31)^t)>>>0,this.lo=(this.lo<<1^t)>>>0,this},u.prototype.zzDecode=function(){var t=-(1&this.lo);return this.lo=((this.lo>>>1|this.hi<<31)^t)>>>0,this.hi=(this.hi>>>1^t)>>>0,this},u.prototype.length=function(){var t=this.lo,n=(this.lo>>>28|this.hi<<4)>>>0,i=this.hi>>>24;return 0==i?0==n?t<16384?t<128?1:2:t<2097152?3:4:n<16384?n<128?5:6:n<2097152?7:8:i<128?9:10}},{15:15}],15:[function(t,n,i){var r=i;function u(t,n,i){for(var r=Object.keys(n),u=0;u<r.length;++u)t[r[u]]!==d&&i||(t[r[u]]=n[r[u]]);return t}function e(t){function i(t,n){if(!(this instanceof i))return new i(t,n);Object.defineProperty(this,"message",{get:function(){return t}}),Error.captureStackTrace?Error.captureStackTrace(this,i):Object.defineProperty(this,"stack",{value:Error().stack||""}),n&&u(this,n)}return i.prototype=Object.create(Error.prototype,{constructor:{value:i,writable:!0,enumerable:!1,configurable:!0},name:{get:function(){return t},set:d,enumerable:!1,configurable:!0},toString:{value:function(){return this.name+": "+this.message},writable:!0,enumerable:!1,configurable:!0}}),i}r.asPromise=t(1),r.base64=t(2),r.EventEmitter=t(3),r.float=t(4),r.inquire=t(5),r.utf8=t(7),r.pool=t(6),r.LongBits=t(14),r.isNode=!!("undefined"!=typeof global&&global&&global.process&&global.process.versions&&global.process.versions.node),r.global=r.isNode&&global||"undefined"!=typeof window&&window||"undefined"!=typeof self&&self||this,r.emptyArray=Object.freeze?Object.freeze([]):[],r.emptyObject=Object.freeze?Object.freeze({}):{},r.isInteger=Number.isInteger||function(t){return"number"==typeof t&&isFinite(t)&&Math.floor(t)===t},r.isString=function(t){return"string"==typeof t||t instanceof String},r.isObject=function(t){return t&&"object"==typeof t},r.isset=r.isSet=function(t,n){var i=t[n];return null!=i&&t.hasOwnProperty(n)&&("object"!=typeof i||0<(Array.isArray(i)?i:Object.keys(i)).length)},r.Buffer=function(){try{var t=r.inquire("buffer").Buffer;return t.prototype.utf8Write?t:null}catch(t){return null}}(),r.r=null,r.u=null,r.newBuffer=function(t){return"number"==typeof t?r.Buffer?r.u(t):new r.Array(t):r.Buffer?r.r(t):"undefined"==typeof Uint8Array?t:new Uint8Array(t)},r.Array="undefined"!=typeof Uint8Array?Uint8Array:Array,r.Long=r.global.dcodeIO&&r.global.dcodeIO.Long||r.global.Long||r.inquire("long"),r.key2Re=/^true|false|0|1$/,r.key32Re=/^-?(?:0|[1-9][0-9]*)$/,r.key64Re=/^(?:[\\x00-\\xff]{8}|-?(?:0|[1-9][0-9]*))$/,r.longToHash=function(t){return t?r.LongBits.from(t).toHash():r.LongBits.zeroHash},r.longFromHash=function(t,n){t=r.LongBits.fromHash(t);return r.Long?r.Long.fromBits(t.lo,t.hi,n):t.toNumber(!!n)},r.merge=u,r.lcFirst=function(t){return(t[0]||"").toLowerCase()+t.substring(1)},r.newError=e,r.ProtocolError=e("ProtocolError"),r.oneOfGetter=function(t){for(var i={},n=0;n<t.length;++n)i[t[n]]=1;return function(){for(var t=Object.keys(this),n=t.length-1;-1<n;--n)if(1===i[t[n]]&&this[t[n]]!==d&&null!==this[t[n]])return t[n]}},r.oneOfSetter=function(i){return function(t){for(var n=0;n<i.length;++n)i[n]!==t&&delete this[i[n]]}},r.toJSONOptions={longs:String,enums:String,bytes:String,json:!0},r.n=function(){var i=r.Buffer;i?(r.r=i.from!==Uint8Array.from&&i.from||function(t,n){return new i(t,n)},r.u=i.allocUnsafe||function(t){return new i(t)}):r.r=r.u=null}},{1:1,14:14,2:2,3:3,4:4,5:5,6:6,7:7}],16:[function(t,n,i){n.exports=a;var r,u=t(15),e=u.LongBits,s=u.base64,h=u.utf8;function o(t,n,i){this.fn=t,this.len=n,this.next=d,this.val=i}function f(){}function c(t){this.head=t.head,this.tail=t.tail,this.len=t.len,this.next=t.states}function a(){this.len=0,this.head=new o(f,0,0),this.tail=this.head,this.states=null}function l(){return u.Buffer?function(){return(a.create=function(){return new r})()}:function(){return new a}}function v(t,n,i){n[i]=255&t}function w(t,n){this.len=t,this.next=d,this.val=n}function b(t,n,i){for(;t.hi;)n[i++]=127&t.lo|128,t.lo=(t.lo>>>7|t.hi<<25)>>>0,t.hi>>>=7;for(;127<t.lo;)n[i++]=127&t.lo|128,t.lo=t.lo>>>7;n[i++]=t.lo}function y(t,n,i){n[i]=255&t,n[i+1]=t>>>8&255,n[i+2]=t>>>16&255,n[i+3]=t>>>24}a.create=l(),a.alloc=function(t){return new u.Array(t)},u.Array!==Array&&(a.alloc=u.pool(a.alloc,u.Array.prototype.subarray)),a.prototype.e=function(t,n,i){return this.tail=this.tail.next=new o(t,n,i),this.len+=n,this},(w.prototype=Object.create(o.prototype)).fn=function(t,n,i){for(;127<t;)n[i++]=127&t|128,t>>>=7;n[i]=t},a.prototype.uint32=function(t){return this.len+=(this.tail=this.tail.next=new w((t>>>=0)<128?1:t<16384?2:t<2097152?3:t<268435456?4:5,t)).len,this},a.prototype.int32=function(t){return t<0?this.e(b,10,e.fromNumber(t)):this.uint32(t)},a.prototype.sint32=function(t){return this.uint32((t<<1^t>>31)>>>0)},a.prototype.int64=a.prototype.uint64=function(t){t=e.from(t);return this.e(b,t.length(),t)},a.prototype.sint64=function(t){t=e.from(t).zzEncode();return this.e(b,t.length(),t)},a.prototype.bool=function(t){return this.e(v,1,t?1:0)},a.prototype.sfixed32=a.prototype.fixed32=function(t){return this.e(y,4,t>>>0)},a.prototype.sfixed64=a.prototype.fixed64=function(t){t=e.from(t);return this.e(y,4,t.lo).e(y,4,t.hi)},a.prototype.float=function(t){return this.e(u.float.writeFloatLE,4,t)},a.prototype.double=function(t){return this.e(u.float.writeDoubleLE,8,t)};var g=u.Array.prototype.set?function(t,n,i){n.set(t,i)}:function(t,n,i){for(var r=0;r<t.length;++r)n[i+r]=t[r]};a.prototype.bytes=function(t){var n=(t=u.isString(t)?u.r(t,"base64"):t).length>>>0;return i?(u.isString(t)&&(n=a.alloc(i=s.length(t)),s.decode(t,n,0),t=n),this.uint32(i).e(g,i,t)):this.e(v,1,0)},a.prototype.string=function(t){var n=h.length(t);return n?this.uint32(n).e(h.write,n,t):this.e(v,1,0)},a.prototype.fork=function(){return this.states=new c(this),this.head=this.tail=new o(f,0,0),this.len=0,this},a.prototype.reset=function(){return this.states?(this.head=this.states.head,this.tail=this.states.tail,this.len=this.states.len,this.states=this.states.next):(this.head=this.tail=new o(f,0,0),this.len=0),this},a.prototype.ldelim=function(){var t=this.head,n=this.tail,i=this.len;return this.reset().uint32(i),i&&(this.tail.next=t.next,this.tail=n,this.len+=i),this},a.prototype.finish=function(){for(var t=this.head.next,n=this.constructor.alloc(this.len),i=0;t;)t.fn(t.val,n,i),i+=t.len,t=t.next;return n},a.n=function(t){r=t,a.create=l(),r.n()}},{15:15}],17:[function(t,n,i){n.exports=e;var r=t(16),u=((e.prototype=Object.create(r.prototype)).constructor=e,t(15));function e(){r.call(this)}function s(t,n,i){t.length<40?u.utf8.write(t,n,i):n.utf8Write?n.utf8Write(t,i):n.write(t,i)}e.n=function(){e.alloc=u.u,e.writeBytesBuffer=u.Buffer&&u.Buffer.prototype instanceof Uint8Array&&"set"===u.Buffer.prototype.set.name?function(t,n,i){n.set(t,i)}:function(t,n,i){if(t.copy)t.copy(n,i,0,t.length);else for(var r=0;r<t.length;)n[i++]=t[r++]}},e.prototype.bytes=function(t){var n=(t=u.isString(t)?u.r(t,"base64"):t).length>>>0;return this.uint32(n),n&&this.e(e.writeBytesBuffer,n,t),this},e.prototype.string=function(t){var n=u.Buffer.byteLength(t);return this.uint32(n),n&&this.e(s,n,t),this},e.n()},{15:15,16:16}]},{},[8])}();

function t(t){let e=t.length;for(;--e>=0;)t[e]=0}const e=256,a=286,i=30,n=15,s=new Uint8Array([0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0]),r=new Uint8Array([0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13]),l=new Uint8Array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7]),o=new Uint8Array([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]),h=new Array(576);t(h);const d=new Array(60);t(d);const _=new Array(512);t(_);const f=new Array(256);t(f);const c=new Array(29);t(c);const u=new Array(i);function w(t,e,a,i,n){this.static_tree=t,this.extra_bits=e,this.extra_base=a,this.elems=i,this.max_length=n,this.has_stree=t&&t.length}let m,b,g;function p(t,e){this.dyn_tree=t,this.max_code=0,this.stat_desc=e}t(u);const k=t=>t<256?_[t]:_[256+(t>>>7)],v=(t,e)=>{t.pending_buf[t.pending++]=255&e,t.pending_buf[t.pending++]=e>>>8&255},y=(t,e,a)=>{t.bi_valid>16-a?(t.bi_buf|=e<<t.bi_valid&65535,v(t,t.bi_buf),t.bi_buf=e>>16-t.bi_valid,t.bi_valid+=a-16):(t.bi_buf|=e<<t.bi_valid&65535,t.bi_valid+=a)},x=(t,e,a)=>{y(t,a[2*e],a[2*e+1])},z=(t,e)=>{let a=0;do{a|=1&t,t>>>=1,a<<=1}while(--e>0);return a>>>1},A=(t,e,a)=>{const i=new Array(16);let s,r,l=0;for(s=1;s<=n;s++)l=l+a[s-1]<<1,i[s]=l;for(r=0;r<=e;r++){let e=t[2*r+1];0!==e&&(t[2*r]=z(i[e]++,e))}},E=t=>{let e;for(e=0;e<a;e++)t.dyn_ltree[2*e]=0;for(e=0;e<i;e++)t.dyn_dtree[2*e]=0;for(e=0;e<19;e++)t.bl_tree[2*e]=0;t.dyn_ltree[512]=1,t.opt_len=t.static_len=0,t.sym_next=t.matches=0},R=t=>{t.bi_valid>8?v(t,t.bi_buf):t.bi_valid>0&&(t.pending_buf[t.pending++]=t.bi_buf),t.bi_buf=0,t.bi_valid=0},Z=(t,e,a,i)=>{const n=2*e,s=2*a;return t[n]<t[s]||t[n]===t[s]&&i[e]<=i[a]},U=(t,e,a)=>{const i=t.heap[a];let n=a<<1;for(;n<=t.heap_len&&(n<t.heap_len&&Z(e,t.heap[n+1],t.heap[n],t.depth)&&n++,!Z(e,i,t.heap[n],t.depth));)t.heap[a]=t.heap[n],a=n,n<<=1;t.heap[a]=i},S=(t,a,i)=>{let n,l,o,h,d=0;if(0!==t.sym_next)do{n=255&t.pending_buf[t.sym_buf+d++],n+=(255&t.pending_buf[t.sym_buf+d++])<<8,l=t.pending_buf[t.sym_buf+d++],0===n?x(t,l,a):(o=f[l],x(t,o+e+1,a),h=s[o],0!==h&&(l-=c[o],y(t,l,h)),n--,o=k(n),x(t,o,i),h=r[o],0!==h&&(n-=u[o],y(t,n,h)))}while(d<t.sym_next);x(t,256,a)},D=(t,e)=>{const a=e.dyn_tree,i=e.stat_desc.static_tree,s=e.stat_desc.has_stree,r=e.stat_desc.elems;let l,o,h,d=-1;for(t.heap_len=0,t.heap_max=573,l=0;l<r;l++)0!==a[2*l]?(t.heap[++t.heap_len]=d=l,t.depth[l]=0):a[2*l+1]=0;for(;t.heap_len<2;)h=t.heap[++t.heap_len]=d<2?++d:0,a[2*h]=1,t.depth[h]=0,t.opt_len--,s&&(t.static_len-=i[2*h+1]);for(e.max_code=d,l=t.heap_len>>1;l>=1;l--)U(t,a,l);h=r;do{l=t.heap[1],t.heap[1]=t.heap[t.heap_len--],U(t,a,1),o=t.heap[1],t.heap[--t.heap_max]=l,t.heap[--t.heap_max]=o,a[2*h]=a[2*l]+a[2*o],t.depth[h]=(t.depth[l]>=t.depth[o]?t.depth[l]:t.depth[o])+1,a[2*l+1]=a[2*o+1]=h,t.heap[1]=h++,U(t,a,1)}while(t.heap_len>=2);t.heap[--t.heap_max]=t.heap[1],((t,e)=>{const a=e.dyn_tree,i=e.max_code,s=e.stat_desc.static_tree,r=e.stat_desc.has_stree,l=e.stat_desc.extra_bits,o=e.stat_desc.extra_base,h=e.stat_desc.max_length;let d,_,f,c,u,w,m=0;for(c=0;c<=n;c++)t.bl_count[c]=0;for(a[2*t.heap[t.heap_max]+1]=0,d=t.heap_max+1;d<573;d++)_=t.heap[d],c=a[2*a[2*_+1]+1]+1,c>h&&(c=h,m++),a[2*_+1]=c,_>i||(t.bl_count[c]++,u=0,_>=o&&(u=l[_-o]),w=a[2*_],t.opt_len+=w*(c+u),r&&(t.static_len+=w*(s[2*_+1]+u)));if(0!==m){do{for(c=h-1;0===t.bl_count[c];)c--;t.bl_count[c]--,t.bl_count[c+1]+=2,t.bl_count[h]--,m-=2}while(m>0);for(c=h;0!==c;c--)for(_=t.bl_count[c];0!==_;)f=t.heap[--d],f>i||(a[2*f+1]!==c&&(t.opt_len+=(c-a[2*f+1])*a[2*f],a[2*f+1]=c),_--)}})(t,e),A(a,d,t.bl_count)},T=(t,e,a)=>{let i,n,s=-1,r=e[1],l=0,o=7,h=4;for(0===r&&(o=138,h=3),e[2*(a+1)+1]=65535,i=0;i<=a;i++)n=r,r=e[2*(i+1)+1],++l<o&&n===r||(l<h?t.bl_tree[2*n]+=l:0!==n?(n!==s&&t.bl_tree[2*n]++,t.bl_tree[32]++):l<=10?t.bl_tree[34]++:t.bl_tree[36]++,l=0,s=n,0===r?(o=138,h=3):n===r?(o=6,h=3):(o=7,h=4))},O=(t,e,a)=>{let i,n,s=-1,r=e[1],l=0,o=7,h=4;for(0===r&&(o=138,h=3),i=0;i<=a;i++)if(n=r,r=e[2*(i+1)+1],!(++l<o&&n===r)){if(l<h)do{x(t,n,t.bl_tree)}while(0!=--l);else 0!==n?(n!==s&&(x(t,n,t.bl_tree),l--),x(t,16,t.bl_tree),y(t,l-3,2)):l<=10?(x(t,17,t.bl_tree),y(t,l-3,3)):(x(t,18,t.bl_tree),y(t,l-11,7));l=0,s=n,0===r?(o=138,h=3):n===r?(o=6,h=3):(o=7,h=4)}};let I=!1;const F=(t,e,a,i)=>{y(t,0+(i?1:0),3),R(t),v(t,a),v(t,~a),a&&t.pending_buf.set(t.window.subarray(e,e+a),t.pending),t.pending+=a};var L=(t,a,i,n)=>{let s,r,l=0;t.level>0?(2===t.strm.data_type&&(t.strm.data_type=(t=>{let a,i=4093624447;for(a=0;a<=31;a++,i>>>=1)if(1&i&&0!==t.dyn_ltree[2*a])return 0;if(0!==t.dyn_ltree[18]||0!==t.dyn_ltree[20]||0!==t.dyn_ltree[26])return 1;for(a=32;a<e;a++)if(0!==t.dyn_ltree[2*a])return 1;return 0})(t)),D(t,t.l_desc),D(t,t.d_desc),l=(t=>{let e;for(T(t,t.dyn_ltree,t.l_desc.max_code),T(t,t.dyn_dtree,t.d_desc.max_code),D(t,t.bl_desc),e=18;e>=3&&0===t.bl_tree[2*o[e]+1];e--);return t.opt_len+=3*(e+1)+5+5+4,e})(t),s=t.opt_len+3+7>>>3,r=t.static_len+3+7>>>3,r<=s&&(s=r)):s=r=i+5,i+4<=s&&-1!==a?F(t,a,i,n):4===t.strategy||r===s?(y(t,2+(n?1:0),3),S(t,h,d)):(y(t,4+(n?1:0),3),((t,e,a,i)=>{let n;for(y(t,e-257,5),y(t,a-1,5),y(t,i-4,4),n=0;n<i;n++)y(t,t.bl_tree[2*o[n]+1],3);O(t,t.dyn_ltree,e-1),O(t,t.dyn_dtree,a-1)})(t,t.l_desc.max_code+1,t.d_desc.max_code+1,l+1),S(t,t.dyn_ltree,t.dyn_dtree)),E(t),n&&R(t)},N={_tr_init:t=>{I||((()=>{let t,e,o,p,k;const v=new Array(16);for(o=0,p=0;p<28;p++)for(c[p]=o,t=0;t<1<<s[p];t++)f[o++]=p;for(f[o-1]=p,k=0,p=0;p<16;p++)for(u[p]=k,t=0;t<1<<r[p];t++)_[k++]=p;for(k>>=7;p<i;p++)for(u[p]=k<<7,t=0;t<1<<r[p]-7;t++)_[256+k++]=p;for(e=0;e<=n;e++)v[e]=0;for(t=0;t<=143;)h[2*t+1]=8,t++,v[8]++;for(;t<=255;)h[2*t+1]=9,t++,v[9]++;for(;t<=279;)h[2*t+1]=7,t++,v[7]++;for(;t<=287;)h[2*t+1]=8,t++,v[8]++;for(A(h,287,v),t=0;t<i;t++)d[2*t+1]=5,d[2*t]=z(t,5);m=new w(h,s,257,a,n),b=new w(d,r,0,i,n),g=new w(new Array(0),l,0,19,7)})(),I=!0),t.l_desc=new p(t.dyn_ltree,m),t.d_desc=new p(t.dyn_dtree,b),t.bl_desc=new p(t.bl_tree,g),t.bi_buf=0,t.bi_valid=0,E(t)},_tr_stored_block:F,_tr_flush_block:L,_tr_tally:(t,a,i)=>(t.pending_buf[t.sym_buf+t.sym_next++]=a,t.pending_buf[t.sym_buf+t.sym_next++]=a>>8,t.pending_buf[t.sym_buf+t.sym_next++]=i,0===a?t.dyn_ltree[2*i]++:(t.matches++,a--,t.dyn_ltree[2*(f[i]+e+1)]++,t.dyn_dtree[2*k(a)]++),t.sym_next===t.sym_end),_tr_align:t=>{y(t,2,3),x(t,256,h),(t=>{16===t.bi_valid?(v(t,t.bi_buf),t.bi_buf=0,t.bi_valid=0):t.bi_valid>=8&&(t.pending_buf[t.pending++]=255&t.bi_buf,t.bi_buf>>=8,t.bi_valid-=8)})(t)}};var B=(t,e,a,i)=>{let n=65535&t|0,s=t>>>16&65535|0,r=0;for(;0!==a;){r=a>2e3?2e3:a,a-=r;do{n=n+e[i++]|0,s=s+n|0}while(--r);n%=65521,s%=65521}return n|s<<16|0};const C=new Uint32Array((()=>{let t,e=[];for(var a=0;a<256;a++){t=a;for(var i=0;i<8;i++)t=1&t?3988292384^t>>>1:t>>>1;e[a]=t}return e})());var H=(t,e,a,i)=>{const n=C,s=i+a;t^=-1;for(let a=i;a<s;a++)t=t>>>8^n[255&(t^e[a])];return-1^t},M={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"},j={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_MEM_ERROR:-4,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8};const{_tr_init:K,_tr_stored_block:P,_tr_flush_block:Y,_tr_tally:G,_tr_align:X}=N,{Z_NO_FLUSH:W,Z_PARTIAL_FLUSH:q,Z_FULL_FLUSH:J,Z_FINISH:Q,Z_BLOCK:V,Z_OK:$,Z_STREAM_END:tt,Z_STREAM_ERROR:et,Z_DATA_ERROR:at,Z_BUF_ERROR:it,Z_DEFAULT_COMPRESSION:nt,Z_FILTERED:st,Z_HUFFMAN_ONLY:rt,Z_RLE:lt,Z_FIXED:ot,Z_DEFAULT_STRATEGY:ht,Z_UNKNOWN:dt,Z_DEFLATED:_t}=j,ft=258,ct=262,ut=42,wt=113,mt=666,bt=(t,e)=>(t.msg=M[e],e),gt=t=>2*t-(t>4?9:0),pt=t=>{let e=t.length;for(;--e>=0;)t[e]=0},kt=t=>{let e,a,i,n=t.w_size;e=t.hash_size,i=e;do{a=t.head[--i],t.head[i]=a>=n?a-n:0}while(--e);e=n,i=e;do{a=t.prev[--i],t.prev[i]=a>=n?a-n:0}while(--e)};let vt=(t,e,a)=>(e<<t.hash_shift^a)&t.hash_mask;const yt=t=>{const e=t.state;let a=e.pending;a>t.avail_out&&(a=t.avail_out),0!==a&&(t.output.set(e.pending_buf.subarray(e.pending_out,e.pending_out+a),t.next_out),t.next_out+=a,e.pending_out+=a,t.total_out+=a,t.avail_out-=a,e.pending-=a,0===e.pending&&(e.pending_out=0))},xt=(t,e)=>{Y(t,t.block_start>=0?t.block_start:-1,t.strstart-t.block_start,e),t.block_start=t.strstart,yt(t.strm)},zt=(t,e)=>{t.pending_buf[t.pending++]=e},At=(t,e)=>{t.pending_buf[t.pending++]=e>>>8&255,t.pending_buf[t.pending++]=255&e},Et=(t,e,a,i)=>{let n=t.avail_in;return n>i&&(n=i),0===n?0:(t.avail_in-=n,e.set(t.input.subarray(t.next_in,t.next_in+n),a),1===t.state.wrap?t.adler=B(t.adler,e,n,a):2===t.state.wrap&&(t.adler=H(t.adler,e,n,a)),t.next_in+=n,t.total_in+=n,n)},Rt=(t,e)=>{let a,i,n=t.max_chain_length,s=t.strstart,r=t.prev_length,l=t.nice_match;const o=t.strstart>t.w_size-ct?t.strstart-(t.w_size-ct):0,h=t.window,d=t.w_mask,_=t.prev,f=t.strstart+ft;let c=h[s+r-1],u=h[s+r];t.prev_length>=t.good_match&&(n>>=2),l>t.lookahead&&(l=t.lookahead);do{if(a=e,h[a+r]===u&&h[a+r-1]===c&&h[a]===h[s]&&h[++a]===h[s+1]){s+=2,a++;do{}while(h[++s]===h[++a]&&h[++s]===h[++a]&&h[++s]===h[++a]&&h[++s]===h[++a]&&h[++s]===h[++a]&&h[++s]===h[++a]&&h[++s]===h[++a]&&h[++s]===h[++a]&&s<f);if(i=ft-(f-s),s=f-ft,i>r){if(t.match_start=e,r=i,i>=l)break;c=h[s+r-1],u=h[s+r]}}}while((e=_[e&d])>o&&0!=--n);return r<=t.lookahead?r:t.lookahead},Zt=t=>{const e=t.w_size;let a,i,n;do{if(i=t.window_size-t.lookahead-t.strstart,t.strstart>=e+(e-ct)&&(t.window.set(t.window.subarray(e,e+e-i),0),t.match_start-=e,t.strstart-=e,t.block_start-=e,t.insert>t.strstart&&(t.insert=t.strstart),kt(t),i+=e),0===t.strm.avail_in)break;if(a=Et(t.strm,t.window,t.strstart+t.lookahead,i),t.lookahead+=a,t.lookahead+t.insert>=3)for(n=t.strstart-t.insert,t.ins_h=t.window[n],t.ins_h=vt(t,t.ins_h,t.window[n+1]);t.insert&&(t.ins_h=vt(t,t.ins_h,t.window[n+3-1]),t.prev[n&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=n,n++,t.insert--,!(t.lookahead+t.insert<3)););}while(t.lookahead<ct&&0!==t.strm.avail_in)},Ut=(t,e)=>{let a,i,n,s=t.pending_buf_size-5>t.w_size?t.w_size:t.pending_buf_size-5,r=0,l=t.strm.avail_in;do{if(a=65535,n=t.bi_valid+42>>3,t.strm.avail_out<n)break;if(n=t.strm.avail_out-n,i=t.strstart-t.block_start,a>i+t.strm.avail_in&&(a=i+t.strm.avail_in),a>n&&(a=n),a<s&&(0===a&&e!==Q||e===W||a!==i+t.strm.avail_in))break;r=e===Q&&a===i+t.strm.avail_in?1:0,P(t,0,0,r),t.pending_buf[t.pending-4]=a,t.pending_buf[t.pending-3]=a>>8,t.pending_buf[t.pending-2]=~a,t.pending_buf[t.pending-1]=~a>>8,yt(t.strm),i&&(i>a&&(i=a),t.strm.output.set(t.window.subarray(t.block_start,t.block_start+i),t.strm.next_out),t.strm.next_out+=i,t.strm.avail_out-=i,t.strm.total_out+=i,t.block_start+=i,a-=i),a&&(Et(t.strm,t.strm.output,t.strm.next_out,a),t.strm.next_out+=a,t.strm.avail_out-=a,t.strm.total_out+=a)}while(0===r);return l-=t.strm.avail_in,l&&(l>=t.w_size?(t.matches=2,t.window.set(t.strm.input.subarray(t.strm.next_in-t.w_size,t.strm.next_in),0),t.strstart=t.w_size,t.insert=t.strstart):(t.window_size-t.strstart<=l&&(t.strstart-=t.w_size,t.window.set(t.window.subarray(t.w_size,t.w_size+t.strstart),0),t.matches<2&&t.matches++,t.insert>t.strstart&&(t.insert=t.strstart)),t.window.set(t.strm.input.subarray(t.strm.next_in-l,t.strm.next_in),t.strstart),t.strstart+=l,t.insert+=l>t.w_size-t.insert?t.w_size-t.insert:l),t.block_start=t.strstart),t.high_water<t.strstart&&(t.high_water=t.strstart),r?4:e!==W&&e!==Q&&0===t.strm.avail_in&&t.strstart===t.block_start?2:(n=t.window_size-t.strstart,t.strm.avail_in>n&&t.block_start>=t.w_size&&(t.block_start-=t.w_size,t.strstart-=t.w_size,t.window.set(t.window.subarray(t.w_size,t.w_size+t.strstart),0),t.matches<2&&t.matches++,n+=t.w_size,t.insert>t.strstart&&(t.insert=t.strstart)),n>t.strm.avail_in&&(n=t.strm.avail_in),n&&(Et(t.strm,t.window,t.strstart,n),t.strstart+=n,t.insert+=n>t.w_size-t.insert?t.w_size-t.insert:n),t.high_water<t.strstart&&(t.high_water=t.strstart),n=t.bi_valid+42>>3,n=t.pending_buf_size-n>65535?65535:t.pending_buf_size-n,s=n>t.w_size?t.w_size:n,i=t.strstart-t.block_start,(i>=s||(i||e===Q)&&e!==W&&0===t.strm.avail_in&&i<=n)&&(a=i>n?n:i,r=e===Q&&0===t.strm.avail_in&&a===i?1:0,P(t,t.block_start,a,r),t.block_start+=a,yt(t.strm)),r?3:1)},St=(t,e)=>{let a,i;for(;;){if(t.lookahead<ct){if(Zt(t),t.lookahead<ct&&e===W)return 1;if(0===t.lookahead)break}if(a=0,t.lookahead>=3&&(t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart),0!==a&&t.strstart-a<=t.w_size-ct&&(t.match_length=Rt(t,a)),t.match_length>=3)if(i=G(t,t.strstart-t.match_start,t.match_length-3),t.lookahead-=t.match_length,t.match_length<=t.max_lazy_match&&t.lookahead>=3){t.match_length--;do{t.strstart++,t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart}while(0!=--t.match_length);t.strstart++}else t.strstart+=t.match_length,t.match_length=0,t.ins_h=t.window[t.strstart],t.ins_h=vt(t,t.ins_h,t.window[t.strstart+1]);else i=G(t,0,t.window[t.strstart]),t.lookahead--,t.strstart++;if(i&&(xt(t,!1),0===t.strm.avail_out))return 1}return t.insert=t.strstart<2?t.strstart:2,e===Q?(xt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(xt(t,!1),0===t.strm.avail_out)?1:2},Dt=(t,e)=>{let a,i,n;for(;;){if(t.lookahead<ct){if(Zt(t),t.lookahead<ct&&e===W)return 1;if(0===t.lookahead)break}if(a=0,t.lookahead>=3&&(t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart),t.prev_length=t.match_length,t.prev_match=t.match_start,t.match_length=2,0!==a&&t.prev_length<t.max_lazy_match&&t.strstart-a<=t.w_size-ct&&(t.match_length=Rt(t,a),t.match_length<=5&&(t.strategy===st||3===t.match_length&&t.strstart-t.match_start>4096)&&(t.match_length=2)),t.prev_length>=3&&t.match_length<=t.prev_length){n=t.strstart+t.lookahead-3,i=G(t,t.strstart-1-t.prev_match,t.prev_length-3),t.lookahead-=t.prev_length-1,t.prev_length-=2;do{++t.strstart<=n&&(t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart)}while(0!=--t.prev_length);if(t.match_available=0,t.match_length=2,t.strstart++,i&&(xt(t,!1),0===t.strm.avail_out))return 1}else if(t.match_available){if(i=G(t,0,t.window[t.strstart-1]),i&&xt(t,!1),t.strstart++,t.lookahead--,0===t.strm.avail_out)return 1}else t.match_available=1,t.strstart++,t.lookahead--}return t.match_available&&(i=G(t,0,t.window[t.strstart-1]),t.match_available=0),t.insert=t.strstart<2?t.strstart:2,e===Q?(xt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(xt(t,!1),0===t.strm.avail_out)?1:2};function Tt(t,e,a,i,n){this.good_length=t,this.max_lazy=e,this.nice_length=a,this.max_chain=i,this.func=n}const Ot=[new Tt(0,0,0,0,Ut),new Tt(4,4,8,4,St),new Tt(4,5,16,8,St),new Tt(4,6,32,32,St),new Tt(4,4,16,16,Dt),new Tt(8,16,32,32,Dt),new Tt(8,16,128,128,Dt),new Tt(8,32,128,256,Dt),new Tt(32,128,258,1024,Dt),new Tt(32,258,258,4096,Dt)];function It(){this.strm=null,this.status=0,this.pending_buf=null,this.pending_buf_size=0,this.pending_out=0,this.pending=0,this.wrap=0,this.gzhead=null,this.gzindex=0,this.method=_t,this.last_flush=-1,this.w_size=0,this.w_bits=0,this.w_mask=0,this.window=null,this.window_size=0,this.prev=null,this.head=null,this.ins_h=0,this.hash_size=0,this.hash_bits=0,this.hash_mask=0,this.hash_shift=0,this.block_start=0,this.match_length=0,this.prev_match=0,this.match_available=0,this.strstart=0,this.match_start=0,this.lookahead=0,this.prev_length=0,this.max_chain_length=0,this.max_lazy_match=0,this.level=0,this.strategy=0,this.good_match=0,this.nice_match=0,this.dyn_ltree=new Uint16Array(1146),this.dyn_dtree=new Uint16Array(122),this.bl_tree=new Uint16Array(78),pt(this.dyn_ltree),pt(this.dyn_dtree),pt(this.bl_tree),this.l_desc=null,this.d_desc=null,this.bl_desc=null,this.bl_count=new Uint16Array(16),this.heap=new Uint16Array(573),pt(this.heap),this.heap_len=0,this.heap_max=0,this.depth=new Uint16Array(573),pt(this.depth),this.sym_buf=0,this.lit_bufsize=0,this.sym_next=0,this.sym_end=0,this.opt_len=0,this.static_len=0,this.matches=0,this.insert=0,this.bi_buf=0,this.bi_valid=0}const Ft=t=>{if(!t)return 1;const e=t.state;return!e||e.strm!==t||e.status!==ut&&57!==e.status&&69!==e.status&&73!==e.status&&91!==e.status&&103!==e.status&&e.status!==wt&&e.status!==mt?1:0},Lt=t=>{if(Ft(t))return bt(t,et);t.total_in=t.total_out=0,t.data_type=dt;const e=t.state;return e.pending=0,e.pending_out=0,e.wrap<0&&(e.wrap=-e.wrap),e.status=2===e.wrap?57:e.wrap?ut:wt,t.adler=2===e.wrap?0:1,e.last_flush=-2,K(e),$},Nt=t=>{const e=Lt(t);var a;return e===$&&((a=t.state).window_size=2*a.w_size,pt(a.head),a.max_lazy_match=Ot[a.level].max_lazy,a.good_match=Ot[a.level].good_length,a.nice_match=Ot[a.level].nice_length,a.max_chain_length=Ot[a.level].max_chain,a.strstart=0,a.block_start=0,a.lookahead=0,a.insert=0,a.match_length=a.prev_length=2,a.match_available=0,a.ins_h=0),e},Bt=(t,e,a,i,n,s)=>{if(!t)return et;let r=1;if(e===nt&&(e=6),i<0?(r=0,i=-i):i>15&&(r=2,i-=16),n<1||n>9||a!==_t||i<8||i>15||e<0||e>9||s<0||s>ot||8===i&&1!==r)return bt(t,et);8===i&&(i=9);const l=new It;return t.state=l,l.strm=t,l.status=ut,l.wrap=r,l.gzhead=null,l.w_bits=i,l.w_size=1<<l.w_bits,l.w_mask=l.w_size-1,l.hash_bits=n+7,l.hash_size=1<<l.hash_bits,l.hash_mask=l.hash_size-1,l.hash_shift=~~((l.hash_bits+3-1)/3),l.window=new Uint8Array(2*l.w_size),l.head=new Uint16Array(l.hash_size),l.prev=new Uint16Array(l.w_size),l.lit_bufsize=1<<n+6,l.pending_buf_size=4*l.lit_bufsize,l.pending_buf=new Uint8Array(l.pending_buf_size),l.sym_buf=l.lit_bufsize,l.sym_end=3*(l.lit_bufsize-1),l.level=e,l.strategy=s,l.method=a,Nt(t)};var Ct={deflateInit:(t,e)=>Bt(t,e,_t,15,8,ht),deflateInit2:Bt,deflateReset:Nt,deflateResetKeep:Lt,deflateSetHeader:(t,e)=>Ft(t)||2!==t.state.wrap?et:(t.state.gzhead=e,$),deflate:(t,e)=>{if(Ft(t)||e>V||e<0)return t?bt(t,et):et;const a=t.state;if(!t.output||0!==t.avail_in&&!t.input||a.status===mt&&e!==Q)return bt(t,0===t.avail_out?it:et);const i=a.last_flush;if(a.last_flush=e,0!==a.pending){if(yt(t),0===t.avail_out)return a.last_flush=-1,$}else if(0===t.avail_in&&gt(e)<=gt(i)&&e!==Q)return bt(t,it);if(a.status===mt&&0!==t.avail_in)return bt(t,it);if(a.status===ut&&0===a.wrap&&(a.status=wt),a.status===ut){let e=_t+(a.w_bits-8<<4)<<8,i=-1;if(i=a.strategy>=rt||a.level<2?0:a.level<6?1:6===a.level?2:3,e|=i<<6,0!==a.strstart&&(e|=32),e+=31-e%31,At(a,e),0!==a.strstart&&(At(a,t.adler>>>16),At(a,65535&t.adler)),t.adler=1,a.status=wt,yt(t),0!==a.pending)return a.last_flush=-1,$}if(57===a.status)if(t.adler=0,zt(a,31),zt(a,139),zt(a,8),a.gzhead)zt(a,(a.gzhead.text?1:0)+(a.gzhead.hcrc?2:0)+(a.gzhead.extra?4:0)+(a.gzhead.name?8:0)+(a.gzhead.comment?16:0)),zt(a,255&a.gzhead.time),zt(a,a.gzhead.time>>8&255),zt(a,a.gzhead.time>>16&255),zt(a,a.gzhead.time>>24&255),zt(a,9===a.level?2:a.strategy>=rt||a.level<2?4:0),zt(a,255&a.gzhead.os),a.gzhead.extra&&a.gzhead.extra.length&&(zt(a,255&a.gzhead.extra.length),zt(a,a.gzhead.extra.length>>8&255)),a.gzhead.hcrc&&(t.adler=H(t.adler,a.pending_buf,a.pending,0)),a.gzindex=0,a.status=69;else if(zt(a,0),zt(a,0),zt(a,0),zt(a,0),zt(a,0),zt(a,9===a.level?2:a.strategy>=rt||a.level<2?4:0),zt(a,3),a.status=wt,yt(t),0!==a.pending)return a.last_flush=-1,$;if(69===a.status){if(a.gzhead.extra){let e=a.pending,i=(65535&a.gzhead.extra.length)-a.gzindex;for(;a.pending+i>a.pending_buf_size;){let n=a.pending_buf_size-a.pending;if(a.pending_buf.set(a.gzhead.extra.subarray(a.gzindex,a.gzindex+n),a.pending),a.pending=a.pending_buf_size,a.gzhead.hcrc&&a.pending>e&&(t.adler=H(t.adler,a.pending_buf,a.pending-e,e)),a.gzindex+=n,yt(t),0!==a.pending)return a.last_flush=-1,$;e=0,i-=n}let n=new Uint8Array(a.gzhead.extra);a.pending_buf.set(n.subarray(a.gzindex,a.gzindex+i),a.pending),a.pending+=i,a.gzhead.hcrc&&a.pending>e&&(t.adler=H(t.adler,a.pending_buf,a.pending-e,e)),a.gzindex=0}a.status=73}if(73===a.status){if(a.gzhead.name){let e,i=a.pending;do{if(a.pending===a.pending_buf_size){if(a.gzhead.hcrc&&a.pending>i&&(t.adler=H(t.adler,a.pending_buf,a.pending-i,i)),yt(t),0!==a.pending)return a.last_flush=-1,$;i=0}e=a.gzindex<a.gzhead.name.length?255&a.gzhead.name.charCodeAt(a.gzindex++):0,zt(a,e)}while(0!==e);a.gzhead.hcrc&&a.pending>i&&(t.adler=H(t.adler,a.pending_buf,a.pending-i,i)),a.gzindex=0}a.status=91}if(91===a.status){if(a.gzhead.comment){let e,i=a.pending;do{if(a.pending===a.pending_buf_size){if(a.gzhead.hcrc&&a.pending>i&&(t.adler=H(t.adler,a.pending_buf,a.pending-i,i)),yt(t),0!==a.pending)return a.last_flush=-1,$;i=0}e=a.gzindex<a.gzhead.comment.length?255&a.gzhead.comment.charCodeAt(a.gzindex++):0,zt(a,e)}while(0!==e);a.gzhead.hcrc&&a.pending>i&&(t.adler=H(t.adler,a.pending_buf,a.pending-i,i))}a.status=103}if(103===a.status){if(a.gzhead.hcrc){if(a.pending+2>a.pending_buf_size&&(yt(t),0!==a.pending))return a.last_flush=-1,$;zt(a,255&t.adler),zt(a,t.adler>>8&255),t.adler=0}if(a.status=wt,yt(t),0!==a.pending)return a.last_flush=-1,$}if(0!==t.avail_in||0!==a.lookahead||e!==W&&a.status!==mt){let i=0===a.level?Ut(a,e):a.strategy===rt?((t,e)=>{let a;for(;;){if(0===t.lookahead&&(Zt(t),0===t.lookahead)){if(e===W)return 1;break}if(t.match_length=0,a=G(t,0,t.window[t.strstart]),t.lookahead--,t.strstart++,a&&(xt(t,!1),0===t.strm.avail_out))return 1}return t.insert=0,e===Q?(xt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(xt(t,!1),0===t.strm.avail_out)?1:2})(a,e):a.strategy===lt?((t,e)=>{let a,i,n,s;const r=t.window;for(;;){if(t.lookahead<=ft){if(Zt(t),t.lookahead<=ft&&e===W)return 1;if(0===t.lookahead)break}if(t.match_length=0,t.lookahead>=3&&t.strstart>0&&(n=t.strstart-1,i=r[n],i===r[++n]&&i===r[++n]&&i===r[++n])){s=t.strstart+ft;do{}while(i===r[++n]&&i===r[++n]&&i===r[++n]&&i===r[++n]&&i===r[++n]&&i===r[++n]&&i===r[++n]&&i===r[++n]&&n<s);t.match_length=ft-(s-n),t.match_length>t.lookahead&&(t.match_length=t.lookahead)}if(t.match_length>=3?(a=G(t,1,t.match_length-3),t.lookahead-=t.match_length,t.strstart+=t.match_length,t.match_length=0):(a=G(t,0,t.window[t.strstart]),t.lookahead--,t.strstart++),a&&(xt(t,!1),0===t.strm.avail_out))return 1}return t.insert=0,e===Q?(xt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(xt(t,!1),0===t.strm.avail_out)?1:2})(a,e):Ot[a.level].func(a,e);if(3!==i&&4!==i||(a.status=mt),1===i||3===i)return 0===t.avail_out&&(a.last_flush=-1),$;if(2===i&&(e===q?X(a):e!==V&&(P(a,0,0,!1),e===J&&(pt(a.head),0===a.lookahead&&(a.strstart=0,a.block_start=0,a.insert=0))),yt(t),0===t.avail_out))return a.last_flush=-1,$}return e!==Q?$:a.wrap<=0?tt:(2===a.wrap?(zt(a,255&t.adler),zt(a,t.adler>>8&255),zt(a,t.adler>>16&255),zt(a,t.adler>>24&255),zt(a,255&t.total_in),zt(a,t.total_in>>8&255),zt(a,t.total_in>>16&255),zt(a,t.total_in>>24&255)):(At(a,t.adler>>>16),At(a,65535&t.adler)),yt(t),a.wrap>0&&(a.wrap=-a.wrap),0!==a.pending?$:tt)},deflateEnd:t=>{if(Ft(t))return et;const e=t.state.status;return t.state=null,e===wt?bt(t,at):$},deflateSetDictionary:(t,e)=>{let a=e.length;if(Ft(t))return et;const i=t.state,n=i.wrap;if(2===n||1===n&&i.status!==ut||i.lookahead)return et;if(1===n&&(t.adler=B(t.adler,e,a,0)),i.wrap=0,a>=i.w_size){0===n&&(pt(i.head),i.strstart=0,i.block_start=0,i.insert=0);let t=new Uint8Array(i.w_size);t.set(e.subarray(a-i.w_size,a),0),e=t,a=i.w_size}const s=t.avail_in,r=t.next_in,l=t.input;for(t.avail_in=a,t.next_in=0,t.input=e,Zt(i);i.lookahead>=3;){let t=i.strstart,e=i.lookahead-2;do{i.ins_h=vt(i,i.ins_h,i.window[t+3-1]),i.prev[t&i.w_mask]=i.head[i.ins_h],i.head[i.ins_h]=t,t++}while(--e);i.strstart=t,i.lookahead=2,Zt(i)}return i.strstart+=i.lookahead,i.block_start=i.strstart,i.insert=i.lookahead,i.lookahead=0,i.match_length=i.prev_length=2,i.match_available=0,t.next_in=r,t.input=l,t.avail_in=s,i.wrap=n,$},deflateInfo:"pako deflate (from Nodeca project)"};const Ht=(t,e)=>Object.prototype.hasOwnProperty.call(t,e);var Mt={assign:function(t){const e=Array.prototype.slice.call(arguments,1);for(;e.length;){const a=e.shift();if(a){if("object"!=typeof a)throw new TypeError(a+"must be non-object");for(const e in a)Ht(a,e)&&(t[e]=a[e])}}return t},flattenChunks:t=>{let e=0;for(let a=0,i=t.length;a<i;a++)e+=t[a].length;const a=new Uint8Array(e);for(let e=0,i=0,n=t.length;e<n;e++){let n=t[e];a.set(n,i),i+=n.length}return a}};let jt=!0;try{String.fromCharCode.apply(null,new Uint8Array(1))}catch(t){jt=!1}const Kt=new Uint8Array(256);for(let t=0;t<256;t++)Kt[t]=t>=252?6:t>=248?5:t>=240?4:t>=224?3:t>=192?2:1;Kt[254]=Kt[254]=1;var Pt={string2buf:t=>{if("function"==typeof TextEncoder&&TextEncoder.prototype.encode)return(new TextEncoder).encode(t);let e,a,i,n,s,r=t.length,l=0;for(n=0;n<r;n++)a=t.charCodeAt(n),55296==(64512&a)&&n+1<r&&(i=t.charCodeAt(n+1),56320==(64512&i)&&(a=65536+(a-55296<<10)+(i-56320),n++)),l+=a<128?1:a<2048?2:a<65536?3:4;for(e=new Uint8Array(l),s=0,n=0;s<l;n++)a=t.charCodeAt(n),55296==(64512&a)&&n+1<r&&(i=t.charCodeAt(n+1),56320==(64512&i)&&(a=65536+(a-55296<<10)+(i-56320),n++)),a<128?e[s++]=a:a<2048?(e[s++]=192|a>>>6,e[s++]=128|63&a):a<65536?(e[s++]=224|a>>>12,e[s++]=128|a>>>6&63,e[s++]=128|63&a):(e[s++]=240|a>>>18,e[s++]=128|a>>>12&63,e[s++]=128|a>>>6&63,e[s++]=128|63&a);return e},buf2string:(t,e)=>{const a=e||t.length;if("function"==typeof TextDecoder&&TextDecoder.prototype.decode)return(new TextDecoder).decode(t.subarray(0,e));let i,n;const s=new Array(2*a);for(n=0,i=0;i<a;){let e=t[i++];if(e<128){s[n++]=e;continue}let r=Kt[e];if(r>4)s[n++]=65533,i+=r-1;else{for(e&=2===r?31:3===r?15:7;r>1&&i<a;)e=e<<6|63&t[i++],r--;r>1?s[n++]=65533:e<65536?s[n++]=e:(e-=65536,s[n++]=55296|e>>10&1023,s[n++]=56320|1023&e)}}return((t,e)=>{if(e<65534&&t.subarray&&jt)return String.fromCharCode.apply(null,t.length===e?t:t.subarray(0,e));let a="";for(let i=0;i<e;i++)a+=String.fromCharCode(t[i]);return a})(s,n)},utf8border:(t,e)=>{(e=e||t.length)>t.length&&(e=t.length);let a=e-1;for(;a>=0&&128==(192&t[a]);)a--;return a<0||0===a?e:a+Kt[t[a]]>e?a:e}};var Yt=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg="",this.state=null,this.data_type=2,this.adler=0};const Gt=Object.prototype.toString,{Z_NO_FLUSH:Xt,Z_SYNC_FLUSH:Wt,Z_FULL_FLUSH:qt,Z_FINISH:Jt,Z_OK:Qt,Z_STREAM_END:Vt,Z_DEFAULT_COMPRESSION:$t,Z_DEFAULT_STRATEGY:te,Z_DEFLATED:ee}=j;function ae(t){this.options=Mt.assign({level:$t,method:ee,chunkSize:16384,windowBits:15,memLevel:8,strategy:te},t||{});let e=this.options;e.raw&&e.windowBits>0?e.windowBits=-e.windowBits:e.gzip&&e.windowBits>0&&e.windowBits<16&&(e.windowBits+=16),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new Yt,this.strm.avail_out=0;let a=Ct.deflateInit2(this.strm,e.level,e.method,e.windowBits,e.memLevel,e.strategy);if(a!==Qt)throw new Error(M[a]);if(e.header&&Ct.deflateSetHeader(this.strm,e.header),e.dictionary){let t;if(t="string"==typeof e.dictionary?Pt.string2buf(e.dictionary):"[object ArrayBuffer]"===Gt.call(e.dictionary)?new Uint8Array(e.dictionary):e.dictionary,a=Ct.deflateSetDictionary(this.strm,t),a!==Qt)throw new Error(M[a]);this._dict_set=!0}}function ie(t,e){const a=new ae(e);if(a.push(t,!0),a.err)throw a.msg||M[a.err];return a.result}ae.prototype.push=function(t,e){const a=this.strm,i=this.options.chunkSize;let n,s;if(this.ended)return!1;for(s=e===~~e?e:!0===e?Jt:Xt,"string"==typeof t?a.input=Pt.string2buf(t):"[object ArrayBuffer]"===Gt.call(t)?a.input=new Uint8Array(t):a.input=t,a.next_in=0,a.avail_in=a.input.length;;)if(0===a.avail_out&&(a.output=new Uint8Array(i),a.next_out=0,a.avail_out=i),(s===Wt||s===qt)&&a.avail_out<=6)this.onData(a.output.subarray(0,a.next_out)),a.avail_out=0;else{if(n=Ct.deflate(a,s),n===Vt)return a.next_out>0&&this.onData(a.output.subarray(0,a.next_out)),n=Ct.deflateEnd(this.strm),this.onEnd(n),this.ended=!0,n===Qt;if(0!==a.avail_out){if(s>0&&a.next_out>0)this.onData(a.output.subarray(0,a.next_out)),a.avail_out=0;else if(0===a.avail_in)break}else this.onData(a.output)}return!0},ae.prototype.onData=function(t){this.chunks.push(t)},ae.prototype.onEnd=function(t){t===Qt&&(this.result=Mt.flattenChunks(this.chunks)),this.chunks=[],this.err=t,this.msg=this.strm.msg};var ne={Deflate:ae,deflate:ie,deflateRaw:function(t,e){return(e=e||{}).raw=!0,ie(t,e)},gzip:function(t,e){return(e=e||{}).gzip=!0,ie(t,e)},constants:j};const se=16209;var re=function(t,e){let a,i,n,s,r,l,o,h,d,_,f,c,u,w,m,b,g,p,k,v,y,x,z,A;const E=t.state;a=t.next_in,z=t.input,i=a+(t.avail_in-5),n=t.next_out,A=t.output,s=n-(e-t.avail_out),r=n+(t.avail_out-257),l=E.dmax,o=E.wsize,h=E.whave,d=E.wnext,_=E.window,f=E.hold,c=E.bits,u=E.lencode,w=E.distcode,m=(1<<E.lenbits)-1,b=(1<<E.distbits)-1;t:do{c<15&&(f+=z[a++]<<c,c+=8,f+=z[a++]<<c,c+=8),g=u[f&m];e:for(;;){if(p=g>>>24,f>>>=p,c-=p,p=g>>>16&255,0===p)A[n++]=65535&g;else{if(!(16&p)){if(0==(64&p)){g=u[(65535&g)+(f&(1<<p)-1)];continue e}if(32&p){E.mode=16191;break t}t.msg="invalid literal/length code",E.mode=se;break t}k=65535&g,p&=15,p&&(c<p&&(f+=z[a++]<<c,c+=8),k+=f&(1<<p)-1,f>>>=p,c-=p),c<15&&(f+=z[a++]<<c,c+=8,f+=z[a++]<<c,c+=8),g=w[f&b];a:for(;;){if(p=g>>>24,f>>>=p,c-=p,p=g>>>16&255,!(16&p)){if(0==(64&p)){g=w[(65535&g)+(f&(1<<p)-1)];continue a}t.msg="invalid distance code",E.mode=se;break t}if(v=65535&g,p&=15,c<p&&(f+=z[a++]<<c,c+=8,c<p&&(f+=z[a++]<<c,c+=8)),v+=f&(1<<p)-1,v>l){t.msg="invalid distance too far back",E.mode=se;break t}if(f>>>=p,c-=p,p=n-s,v>p){if(p=v-p,p>h&&E.sane){t.msg="invalid distance too far back",E.mode=se;break t}if(y=0,x=_,0===d){if(y+=o-p,p<k){k-=p;do{A[n++]=_[y++]}while(--p);y=n-v,x=A}}else if(d<p){if(y+=o+d-p,p-=d,p<k){k-=p;do{A[n++]=_[y++]}while(--p);if(y=0,d<k){p=d,k-=p;do{A[n++]=_[y++]}while(--p);y=n-v,x=A}}}else if(y+=d-p,p<k){k-=p;do{A[n++]=_[y++]}while(--p);y=n-v,x=A}for(;k>2;)A[n++]=x[y++],A[n++]=x[y++],A[n++]=x[y++],k-=3;k&&(A[n++]=x[y++],k>1&&(A[n++]=x[y++]))}else{y=n-v;do{A[n++]=A[y++],A[n++]=A[y++],A[n++]=A[y++],k-=3}while(k>2);k&&(A[n++]=A[y++],k>1&&(A[n++]=A[y++]))}break}}break}}while(a<i&&n<r);k=c>>3,a-=k,c-=k<<3,f&=(1<<c)-1,t.next_in=a,t.next_out=n,t.avail_in=a<i?i-a+5:5-(a-i),t.avail_out=n<r?r-n+257:257-(n-r),E.hold=f,E.bits=c};const le=15,oe=new Uint16Array([3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0]),he=new Uint8Array([16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78]),de=new Uint16Array([1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0]),_e=new Uint8Array([16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64]);var fe=(t,e,a,i,n,s,r,l)=>{const o=l.bits;let h,d,_,f,c,u,w=0,m=0,b=0,g=0,p=0,k=0,v=0,y=0,x=0,z=0,A=null;const E=new Uint16Array(16),R=new Uint16Array(16);let Z,U,S,D=null;for(w=0;w<=le;w++)E[w]=0;for(m=0;m<i;m++)E[e[a+m]]++;for(p=o,g=le;g>=1&&0===E[g];g--);if(p>g&&(p=g),0===g)return n[s++]=20971520,n[s++]=20971520,l.bits=1,0;for(b=1;b<g&&0===E[b];b++);for(p<b&&(p=b),y=1,w=1;w<=le;w++)if(y<<=1,y-=E[w],y<0)return-1;if(y>0&&(0===t||1!==g))return-1;for(R[1]=0,w=1;w<le;w++)R[w+1]=R[w]+E[w];for(m=0;m<i;m++)0!==e[a+m]&&(r[R[e[a+m]]++]=m);if(0===t?(A=D=r,u=20):1===t?(A=oe,D=he,u=257):(A=de,D=_e,u=0),z=0,m=0,w=b,c=s,k=p,v=0,_=-1,x=1<<p,f=x-1,1===t&&x>852||2===t&&x>592)return 1;for(;;){Z=w-v,r[m]+1<u?(U=0,S=r[m]):r[m]>=u?(U=D[r[m]-u],S=A[r[m]-u]):(U=96,S=0),h=1<<w-v,d=1<<k,b=d;do{d-=h,n[c+(z>>v)+d]=Z<<24|U<<16|S|0}while(0!==d);for(h=1<<w-1;z&h;)h>>=1;if(0!==h?(z&=h-1,z+=h):z=0,m++,0==--E[w]){if(w===g)break;w=e[a+r[m]]}if(w>p&&(z&f)!==_){for(0===v&&(v=p),c+=b,k=w-v,y=1<<k;k+v<g&&(y-=E[k+v],!(y<=0));)k++,y<<=1;if(x+=1<<k,1===t&&x>852||2===t&&x>592)return 1;_=z&f,n[_]=p<<24|k<<16|c-s|0}}return 0!==z&&(n[c+z]=w-v<<24|64<<16|0),l.bits=p,0};const{Z_FINISH:ce,Z_BLOCK:ue,Z_TREES:we,Z_OK:me,Z_STREAM_END:be,Z_NEED_DICT:ge,Z_STREAM_ERROR:pe,Z_DATA_ERROR:ke,Z_MEM_ERROR:ve,Z_BUF_ERROR:ye,Z_DEFLATED:xe}=j,ze=16180,Ae=16190,Ee=16191,Re=16192,Ze=16194,Ue=16199,Se=16200,De=16206,Te=16209,Oe=t=>(t>>>24&255)+(t>>>8&65280)+((65280&t)<<8)+((255&t)<<24);function Ie(){this.strm=null,this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new Uint16Array(320),this.work=new Uint16Array(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}const Fe=t=>{if(!t)return 1;const e=t.state;return!e||e.strm!==t||e.mode<ze||e.mode>16211?1:0},Le=t=>{if(Fe(t))return pe;const e=t.state;return t.total_in=t.total_out=e.total=0,t.msg="",e.wrap&&(t.adler=1&e.wrap),e.mode=ze,e.last=0,e.havedict=0,e.flags=-1,e.dmax=32768,e.head=null,e.hold=0,e.bits=0,e.lencode=e.lendyn=new Int32Array(852),e.distcode=e.distdyn=new Int32Array(592),e.sane=1,e.back=-1,me},Ne=t=>{if(Fe(t))return pe;const e=t.state;return e.wsize=0,e.whave=0,e.wnext=0,Le(t)},Be=(t,e)=>{let a;if(Fe(t))return pe;const i=t.state;return e<0?(a=0,e=-e):(a=5+(e>>4),e<48&&(e&=15)),e&&(e<8||e>15)?pe:(null!==i.window&&i.wbits!==e&&(i.window=null),i.wrap=a,i.wbits=e,Ne(t))},Ce=(t,e)=>{if(!t)return pe;const a=new Ie;t.state=a,a.strm=t,a.window=null,a.mode=ze;const i=Be(t,e);return i!==me&&(t.state=null),i};let He,Me,je=!0;const Ke=t=>{if(je){He=new Int32Array(512),Me=new Int32Array(32);let e=0;for(;e<144;)t.lens[e++]=8;for(;e<256;)t.lens[e++]=9;for(;e<280;)t.lens[e++]=7;for(;e<288;)t.lens[e++]=8;for(fe(1,t.lens,0,288,He,0,t.work,{bits:9}),e=0;e<32;)t.lens[e++]=5;fe(2,t.lens,0,32,Me,0,t.work,{bits:5}),je=!1}t.lencode=He,t.lenbits=9,t.distcode=Me,t.distbits=5},Pe=(t,e,a,i)=>{let n;const s=t.state;return null===s.window&&(s.wsize=1<<s.wbits,s.wnext=0,s.whave=0,s.window=new Uint8Array(s.wsize)),i>=s.wsize?(s.window.set(e.subarray(a-s.wsize,a),0),s.wnext=0,s.whave=s.wsize):(n=s.wsize-s.wnext,n>i&&(n=i),s.window.set(e.subarray(a-i,a-i+n),s.wnext),(i-=n)?(s.window.set(e.subarray(a-i,a),0),s.wnext=i,s.whave=s.wsize):(s.wnext+=n,s.wnext===s.wsize&&(s.wnext=0),s.whave<s.wsize&&(s.whave+=n))),0};var Ye={inflateReset:Ne,inflateReset2:Be,inflateResetKeep:Le,inflateInit:t=>Ce(t,15),inflateInit2:Ce,inflate:(t,e)=>{let a,i,n,s,r,l,o,h,d,_,f,c,u,w,m,b,g,p,k,v,y,x,z=0;const A=new Uint8Array(4);let E,R;const Z=new Uint8Array([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]);if(Fe(t)||!t.output||!t.input&&0!==t.avail_in)return pe;a=t.state,a.mode===Ee&&(a.mode=Re),r=t.next_out,n=t.output,o=t.avail_out,s=t.next_in,i=t.input,l=t.avail_in,h=a.hold,d=a.bits,_=l,f=o,x=me;t:for(;;)switch(a.mode){case ze:if(0===a.wrap){a.mode=Re;break}for(;d<16;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(2&a.wrap&&35615===h){0===a.wbits&&(a.wbits=15),a.check=0,A[0]=255&h,A[1]=h>>>8&255,a.check=H(a.check,A,2,0),h=0,d=0,a.mode=16181;break}if(a.head&&(a.head.done=!1),!(1&a.wrap)||(((255&h)<<8)+(h>>8))%31){t.msg="incorrect header check",a.mode=Te;break}if((15&h)!==xe){t.msg="unknown compression method",a.mode=Te;break}if(h>>>=4,d-=4,y=8+(15&h),0===a.wbits&&(a.wbits=y),y>15||y>a.wbits){t.msg="invalid window size",a.mode=Te;break}a.dmax=1<<a.wbits,a.flags=0,t.adler=a.check=1,a.mode=512&h?16189:Ee,h=0,d=0;break;case 16181:for(;d<16;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(a.flags=h,(255&a.flags)!==xe){t.msg="unknown compression method",a.mode=Te;break}if(57344&a.flags){t.msg="unknown header flags set",a.mode=Te;break}a.head&&(a.head.text=h>>8&1),512&a.flags&&4&a.wrap&&(A[0]=255&h,A[1]=h>>>8&255,a.check=H(a.check,A,2,0)),h=0,d=0,a.mode=16182;case 16182:for(;d<32;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}a.head&&(a.head.time=h),512&a.flags&&4&a.wrap&&(A[0]=255&h,A[1]=h>>>8&255,A[2]=h>>>16&255,A[3]=h>>>24&255,a.check=H(a.check,A,4,0)),h=0,d=0,a.mode=16183;case 16183:for(;d<16;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}a.head&&(a.head.xflags=255&h,a.head.os=h>>8),512&a.flags&&4&a.wrap&&(A[0]=255&h,A[1]=h>>>8&255,a.check=H(a.check,A,2,0)),h=0,d=0,a.mode=16184;case 16184:if(1024&a.flags){for(;d<16;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}a.length=h,a.head&&(a.head.extra_len=h),512&a.flags&&4&a.wrap&&(A[0]=255&h,A[1]=h>>>8&255,a.check=H(a.check,A,2,0)),h=0,d=0}else a.head&&(a.head.extra=null);a.mode=16185;case 16185:if(1024&a.flags&&(c=a.length,c>l&&(c=l),c&&(a.head&&(y=a.head.extra_len-a.length,a.head.extra||(a.head.extra=new Uint8Array(a.head.extra_len)),a.head.extra.set(i.subarray(s,s+c),y)),512&a.flags&&4&a.wrap&&(a.check=H(a.check,i,c,s)),l-=c,s+=c,a.length-=c),a.length))break t;a.length=0,a.mode=16186;case 16186:if(2048&a.flags){if(0===l)break t;c=0;do{y=i[s+c++],a.head&&y&&a.length<65536&&(a.head.name+=String.fromCharCode(y))}while(y&&c<l);if(512&a.flags&&4&a.wrap&&(a.check=H(a.check,i,c,s)),l-=c,s+=c,y)break t}else a.head&&(a.head.name=null);a.length=0,a.mode=16187;case 16187:if(4096&a.flags){if(0===l)break t;c=0;do{y=i[s+c++],a.head&&y&&a.length<65536&&(a.head.comment+=String.fromCharCode(y))}while(y&&c<l);if(512&a.flags&&4&a.wrap&&(a.check=H(a.check,i,c,s)),l-=c,s+=c,y)break t}else a.head&&(a.head.comment=null);a.mode=16188;case 16188:if(512&a.flags){for(;d<16;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(4&a.wrap&&h!==(65535&a.check)){t.msg="header crc mismatch",a.mode=Te;break}h=0,d=0}a.head&&(a.head.hcrc=a.flags>>9&1,a.head.done=!0),t.adler=a.check=0,a.mode=Ee;break;case 16189:for(;d<32;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}t.adler=a.check=Oe(h),h=0,d=0,a.mode=Ae;case Ae:if(0===a.havedict)return t.next_out=r,t.avail_out=o,t.next_in=s,t.avail_in=l,a.hold=h,a.bits=d,ge;t.adler=a.check=1,a.mode=Ee;case Ee:if(e===ue||e===we)break t;case Re:if(a.last){h>>>=7&d,d-=7&d,a.mode=De;break}for(;d<3;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}switch(a.last=1&h,h>>>=1,d-=1,3&h){case 0:a.mode=16193;break;case 1:if(Ke(a),a.mode=Ue,e===we){h>>>=2,d-=2;break t}break;case 2:a.mode=16196;break;case 3:t.msg="invalid block type",a.mode=Te}h>>>=2,d-=2;break;case 16193:for(h>>>=7&d,d-=7&d;d<32;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if((65535&h)!=(h>>>16^65535)){t.msg="invalid stored block lengths",a.mode=Te;break}if(a.length=65535&h,h=0,d=0,a.mode=Ze,e===we)break t;case Ze:a.mode=16195;case 16195:if(c=a.length,c){if(c>l&&(c=l),c>o&&(c=o),0===c)break t;n.set(i.subarray(s,s+c),r),l-=c,s+=c,o-=c,r+=c,a.length-=c;break}a.mode=Ee;break;case 16196:for(;d<14;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(a.nlen=257+(31&h),h>>>=5,d-=5,a.ndist=1+(31&h),h>>>=5,d-=5,a.ncode=4+(15&h),h>>>=4,d-=4,a.nlen>286||a.ndist>30){t.msg="too many length or distance symbols",a.mode=Te;break}a.have=0,a.mode=16197;case 16197:for(;a.have<a.ncode;){for(;d<3;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}a.lens[Z[a.have++]]=7&h,h>>>=3,d-=3}for(;a.have<19;)a.lens[Z[a.have++]]=0;if(a.lencode=a.lendyn,a.lenbits=7,E={bits:a.lenbits},x=fe(0,a.lens,0,19,a.lencode,0,a.work,E),a.lenbits=E.bits,x){t.msg="invalid code lengths set",a.mode=Te;break}a.have=0,a.mode=16198;case 16198:for(;a.have<a.nlen+a.ndist;){for(;z=a.lencode[h&(1<<a.lenbits)-1],m=z>>>24,b=z>>>16&255,g=65535&z,!(m<=d);){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(g<16)h>>>=m,d-=m,a.lens[a.have++]=g;else{if(16===g){for(R=m+2;d<R;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(h>>>=m,d-=m,0===a.have){t.msg="invalid bit length repeat",a.mode=Te;break}y=a.lens[a.have-1],c=3+(3&h),h>>>=2,d-=2}else if(17===g){for(R=m+3;d<R;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}h>>>=m,d-=m,y=0,c=3+(7&h),h>>>=3,d-=3}else{for(R=m+7;d<R;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}h>>>=m,d-=m,y=0,c=11+(127&h),h>>>=7,d-=7}if(a.have+c>a.nlen+a.ndist){t.msg="invalid bit length repeat",a.mode=Te;break}for(;c--;)a.lens[a.have++]=y}}if(a.mode===Te)break;if(0===a.lens[256]){t.msg="invalid code -- missing end-of-block",a.mode=Te;break}if(a.lenbits=9,E={bits:a.lenbits},x=fe(1,a.lens,0,a.nlen,a.lencode,0,a.work,E),a.lenbits=E.bits,x){t.msg="invalid literal/lengths set",a.mode=Te;break}if(a.distbits=6,a.distcode=a.distdyn,E={bits:a.distbits},x=fe(2,a.lens,a.nlen,a.ndist,a.distcode,0,a.work,E),a.distbits=E.bits,x){t.msg="invalid distances set",a.mode=Te;break}if(a.mode=Ue,e===we)break t;case Ue:a.mode=Se;case Se:if(l>=6&&o>=258){t.next_out=r,t.avail_out=o,t.next_in=s,t.avail_in=l,a.hold=h,a.bits=d,re(t,f),r=t.next_out,n=t.output,o=t.avail_out,s=t.next_in,i=t.input,l=t.avail_in,h=a.hold,d=a.bits,a.mode===Ee&&(a.back=-1);break}for(a.back=0;z=a.lencode[h&(1<<a.lenbits)-1],m=z>>>24,b=z>>>16&255,g=65535&z,!(m<=d);){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(b&&0==(240&b)){for(p=m,k=b,v=g;z=a.lencode[v+((h&(1<<p+k)-1)>>p)],m=z>>>24,b=z>>>16&255,g=65535&z,!(p+m<=d);){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}h>>>=p,d-=p,a.back+=p}if(h>>>=m,d-=m,a.back+=m,a.length=g,0===b){a.mode=16205;break}if(32&b){a.back=-1,a.mode=Ee;break}if(64&b){t.msg="invalid literal/length code",a.mode=Te;break}a.extra=15&b,a.mode=16201;case 16201:if(a.extra){for(R=a.extra;d<R;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}a.length+=h&(1<<a.extra)-1,h>>>=a.extra,d-=a.extra,a.back+=a.extra}a.was=a.length,a.mode=16202;case 16202:for(;z=a.distcode[h&(1<<a.distbits)-1],m=z>>>24,b=z>>>16&255,g=65535&z,!(m<=d);){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(0==(240&b)){for(p=m,k=b,v=g;z=a.distcode[v+((h&(1<<p+k)-1)>>p)],m=z>>>24,b=z>>>16&255,g=65535&z,!(p+m<=d);){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}h>>>=p,d-=p,a.back+=p}if(h>>>=m,d-=m,a.back+=m,64&b){t.msg="invalid distance code",a.mode=Te;break}a.offset=g,a.extra=15&b,a.mode=16203;case 16203:if(a.extra){for(R=a.extra;d<R;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}a.offset+=h&(1<<a.extra)-1,h>>>=a.extra,d-=a.extra,a.back+=a.extra}if(a.offset>a.dmax){t.msg="invalid distance too far back",a.mode=Te;break}a.mode=16204;case 16204:if(0===o)break t;if(c=f-o,a.offset>c){if(c=a.offset-c,c>a.whave&&a.sane){t.msg="invalid distance too far back",a.mode=Te;break}c>a.wnext?(c-=a.wnext,u=a.wsize-c):u=a.wnext-c,c>a.length&&(c=a.length),w=a.window}else w=n,u=r-a.offset,c=a.length;c>o&&(c=o),o-=c,a.length-=c;do{n[r++]=w[u++]}while(--c);0===a.length&&(a.mode=Se);break;case 16205:if(0===o)break t;n[r++]=a.length,o--,a.mode=Se;break;case De:if(a.wrap){for(;d<32;){if(0===l)break t;l--,h|=i[s++]<<d,d+=8}if(f-=o,t.total_out+=f,a.total+=f,4&a.wrap&&f&&(t.adler=a.check=a.flags?H(a.check,n,f,r-f):B(a.check,n,f,r-f)),f=o,4&a.wrap&&(a.flags?h:Oe(h))!==a.check){t.msg="incorrect data check",a.mode=Te;break}h=0,d=0}a.mode=16207;case 16207:if(a.wrap&&a.flags){for(;d<32;){if(0===l)break t;l--,h+=i[s++]<<d,d+=8}if(4&a.wrap&&h!==(4294967295&a.total)){t.msg="incorrect length check",a.mode=Te;break}h=0,d=0}a.mode=16208;case 16208:x=be;break t;case Te:x=ke;break t;case 16210:return ve;default:return pe}return t.next_out=r,t.avail_out=o,t.next_in=s,t.avail_in=l,a.hold=h,a.bits=d,(a.wsize||f!==t.avail_out&&a.mode<Te&&(a.mode<De||e!==ce))&&Pe(t,t.output,t.next_out,f-t.avail_out),_-=t.avail_in,f-=t.avail_out,t.total_in+=_,t.total_out+=f,a.total+=f,4&a.wrap&&f&&(t.adler=a.check=a.flags?H(a.check,n,f,t.next_out-f):B(a.check,n,f,t.next_out-f)),t.data_type=a.bits+(a.last?64:0)+(a.mode===Ee?128:0)+(a.mode===Ue||a.mode===Ze?256:0),(0===_&&0===f||e===ce)&&x===me&&(x=ye),x},inflateEnd:t=>{if(Fe(t))return pe;let e=t.state;return e.window&&(e.window=null),t.state=null,me},inflateGetHeader:(t,e)=>{if(Fe(t))return pe;const a=t.state;return 0==(2&a.wrap)?pe:(a.head=e,e.done=!1,me)},inflateSetDictionary:(t,e)=>{const a=e.length;let i,n,s;return Fe(t)?pe:(i=t.state,0!==i.wrap&&i.mode!==Ae?pe:i.mode===Ae&&(n=1,n=B(n,e,a,0),n!==i.check)?ke:(s=Pe(t,e,a,a),s?(i.mode=16210,ve):(i.havedict=1,me)))},inflateInfo:"pako inflate (from Nodeca project)"};var Ge=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name="",this.comment="",this.hcrc=0,this.done=!1};const Xe=Object.prototype.toString,{Z_NO_FLUSH:We,Z_FINISH:qe,Z_OK:Je,Z_STREAM_END:Qe,Z_NEED_DICT:Ve,Z_STREAM_ERROR:$e,Z_DATA_ERROR:ta,Z_MEM_ERROR:ea}=j;function aa(t){this.options=Mt.assign({chunkSize:65536,windowBits:15,to:""},t||{});const e=this.options;e.raw&&e.windowBits>=0&&e.windowBits<16&&(e.windowBits=-e.windowBits,0===e.windowBits&&(e.windowBits=-15)),!(e.windowBits>=0&&e.windowBits<16)||t&&t.windowBits||(e.windowBits+=32),e.windowBits>15&&e.windowBits<48&&0==(15&e.windowBits)&&(e.windowBits|=15),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new Yt,this.strm.avail_out=0;let a=Ye.inflateInit2(this.strm,e.windowBits);if(a!==Je)throw new Error(M[a]);if(this.header=new Ge,Ye.inflateGetHeader(this.strm,this.header),e.dictionary&&("string"==typeof e.dictionary?e.dictionary=Pt.string2buf(e.dictionary):"[object ArrayBuffer]"===Xe.call(e.dictionary)&&(e.dictionary=new Uint8Array(e.dictionary)),e.raw&&(a=Ye.inflateSetDictionary(this.strm,e.dictionary),a!==Je)))throw new Error(M[a])}function ia(t,e){const a=new aa(e);if(a.push(t),a.err)throw a.msg||M[a.err];return a.result}aa.prototype.push=function(t,e){const a=this.strm,i=this.options.chunkSize,n=this.options.dictionary;let s,r,l;if(this.ended)return!1;for(r=e===~~e?e:!0===e?qe:We,"[object ArrayBuffer]"===Xe.call(t)?a.input=new Uint8Array(t):a.input=t,a.next_in=0,a.avail_in=a.input.length;;){for(0===a.avail_out&&(a.output=new Uint8Array(i),a.next_out=0,a.avail_out=i),s=Ye.inflate(a,r),s===Ve&&n&&(s=Ye.inflateSetDictionary(a,n),s===Je?s=Ye.inflate(a,r):s===ta&&(s=Ve));a.avail_in>0&&s===Qe&&a.state.wrap>0&&0!==t[a.next_in];)Ye.inflateReset(a),s=Ye.inflate(a,r);switch(s){case $e:case ta:case Ve:case ea:return this.onEnd(s),this.ended=!0,!1}if(l=a.avail_out,a.next_out&&(0===a.avail_out||s===Qe))if("string"===this.options.to){let t=Pt.utf8border(a.output,a.next_out),e=a.next_out-t,n=Pt.buf2string(a.output,t);a.next_out=e,a.avail_out=i-e,e&&a.output.set(a.output.subarray(t,t+e),0),this.onData(n)}else this.onData(a.output.length===a.next_out?a.output:a.output.subarray(0,a.next_out));if(s!==Je||0!==l){if(s===Qe)return s=Ye.inflateEnd(this.strm),this.onEnd(s),this.ended=!0,!0;if(0===a.avail_in)break}}return!0},aa.prototype.onData=function(t){this.chunks.push(t)},aa.prototype.onEnd=function(t){t===Je&&("string"===this.options.to?this.result=this.chunks.join(""):this.result=Mt.flattenChunks(this.chunks)),this.chunks=[],this.err=t,this.msg=this.strm.msg};var na={Inflate:aa,inflate:ia,inflateRaw:function(t,e){return(e=e||{}).raw=!0,ia(t,e)},ungzip:ia,constants:j};const{Deflate:sa,deflate:ra,deflateRaw:la,gzip:oa}=ne,{Inflate:ha,inflate:da,inflateRaw:_a,ungzip:fa}=na;var ca=sa,ua=ra,wa=la,ma=oa,ba=ha,ga=da,pa=_a,ka=fa,va=j,ya={Deflate:ca,deflate:ua,deflateRaw:wa,gzip:ma,Inflate:ba,inflate:ga,inflateRaw:pa,ungzip:ka,constants:va};
const Inflate = ba;

const Reader = protobuf.Reader;
class Caption {
    constructor(properties = {}) {
        // Initialize default values
        this.deviceSpace = "";
        this.captionId = 0;
        this.version = 0;
        this.caption = "";
        this.languageId = 0;

        // Copy provided properties
        for (const key of Object.keys(properties)) {
            if (properties[key] != null) {
                this[key] = properties[key];
            }
        }
    }

    /**
     * Creates a new Caption instance
     * @param {Object} properties - Initial properties
     * @returns {Caption} New Caption instance
     */
    static create(properties) {
        return new Caption(properties);
    }

    /**
     * Encodes the Caption instance to binary format
     * @param {Caption} message - Caption instance to encode
     * @param {Writer} writer - Binary writer instance
     * @returns {Writer} Writer with encoded data
     */
    static encode(message, writer) {
        writer = writer || Writer.create();

        if (message.deviceSpace != null) {
            writer.uint32(10).string(message.deviceSpace);
        }
        if (message.captionId != null) {
            writer.uint32(16).int64(message.captionId);
        }
        if (message.version != null) {
            writer.uint32(24).int64(message.version);
        }
        if (message.caption != null) {
            writer.uint32(50).string(message.caption);
        }
        if (message.languageId != null) {
            writer.uint32(64).int64(message.languageId);
        }

        return writer;
    }

/**
     * Decodes a Caption from binary format
     * @param {Reader} reader - Binary reader instance
     * @param {number} length - Message length
     * @returns {Caption} Decoded Caption instance
     */
    static decode(reader, length) {
    console
        reader = reader instanceof Reader ? reader : Reader.create(reader);
        const end = length === undefined ? reader.len : reader.pos + length;
        const message = new Caption();

        while (reader.pos < end) {
            const tag = reader.uint32();
            switch (tag >>> 3) {
                case 1:
                    message.deviceSpace = reader.string();
                    break;
                case 2:
                    message.captionId = reader.int64();
                    break;
                case 3:
                    message.version = reader.int64();
                    break;
                case 6:
                    message.caption = reader.string();
                    break;
                case 8:
                    message.languageId = reader.int64();
                    break;
                default:
                    reader.skipType(tag & 7);
                    break;
            }
        }
        return message;
    }

    /**
     * Verifies a Caption message
     * @param {Object} message - Message to verify
     * @returns {string|null} null if valid, error message if invalid
     */
    static verify(message) {
        if (typeof message !== "object" || message === null) {
            return "object expected";
        }

        if (message.deviceSpace != null && !isString(message.deviceSpace)) {
            return "deviceSpace: string expected";
        }
        if (message.captionId != null && !isValidLong(message.captionId)) {
            return "captionId: integer|Long expected";
        }
        if (message.version != null && !isValidLong(message.version)) {
            return "version: integer|Long expected";
        }
        if (message.caption != null && !isString(message.caption)) {
            return "caption: string expected";
        }
        if (message.languageId != null && !isValidLong(message.languageId)) {
            return "languageId: integer|Long expected";
        }

        return null;
    }
}

function decodeCaptionFromBuffer(buffer) {
    try {
        // Create initial reader for outer message
        const outerReader = Reader.create(new Uint8Array(buffer));
        
        // Read the first field (tag 1) which contains our actual caption data
        const tag = outerReader.uint32();
        if ((tag >>> 3) === 1) { // Field number 1
            // Extract the inner buffer containing the actual caption protobuf
            const innerBuffer = outerReader.bytes();
            // Create new reader for the inner message and decode it
            const innerReader = Reader.create(innerBuffer);
            const caption = Caption.decode(innerReader);
            return caption;
        }
        
        console.error('Unexpected protobuf structure');
        return null;
    } catch (error) {
        console.error('Error decoding caption buffer:', error);
        console.error('Buffer:', buffer);
        return null;
    }
}

class CollectionMessage {
  constructor() {
    this.body = null; // Contains CollectionMessageBody
  }

  // Decodes a CollectionMessage from a Uint8Array of protobuf bytes
  static decode(reader, length) {
    // If we don't have a proper reader, create one
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    // Get the length of data to read
    const end = length === undefined ? reader.len : reader.pos + length;
    
    // Create a new message instance
    const message = new CollectionMessage();

    // Read fields until we reach the end
    while (reader.pos < end) {
      // Get the field number and wire type
      const tag = reader.uint32();
      
      switch (tag >>> 3) { // Field number
        case 1: // body field
          message.body = CollectionMessageBody.decode(reader, reader.uint32());
          break;
        default:
          reader.skipType(tag & 7); // Skip unknown fields
      }
    }

    return message;
  }
}

class CollectionMessageBody {
  constructor() {
    this.wrapper = null; // Contains Wrapper1
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new CollectionMessageBody();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 2: // wrapper field
          message.wrapper = Wrapper1.decode(reader, reader.uint32());
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class Wrapper1 {
  constructor() {
    this.wrapper = null; // Contains Wrapper2
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new Wrapper1();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 13: // wrapper field
          message.wrapper = Wrapper2.decode(reader, reader.uint32());
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class Wrapper2 {
  constructor() {
    this.wrapper = null; // Contains Wrapper3
    this.chat = []; // Array of ChatWrapper
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new Wrapper2();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 1: // wrapper field
          message.wrapper = Wrapper3.decode(reader, reader.uint32());
          break;
        case 4: // chat field
          if (!message.chat) {
            message.chat = [];
          }
          message.chat.push(ChatWrapper.decode(reader, reader.uint32()));
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class Wrapper3 {
  constructor() {
    this.userDetails = []; // Array of UserDetails
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new Wrapper3();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 2: // userDetails field
          if (!message.userDetails) {
            message.userDetails = [];
          }
          message.userDetails.push(UserDetails.decode(reader, reader.uint32()));
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class UserDetails {
  constructor() {
    this.deviceId = "";
    this.fullName = "";
    this.profile = "";
    this.name = "";
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new UserDetails();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 1:
          message.deviceId = reader.string();
          break;
        case 2:
          message.fullName = reader.string();
          break;
        case 3:
          message.profile = reader.string();
          break;
        case 29:
          message.name = reader.string();
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class ChatWrapper {
  constructor() {
    this.body = null; // Contains ChatData
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new ChatWrapper();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 2: // body field
          message.body = ChatData.decode(reader, reader.uint32());
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class ChatData {
  constructor() {
    this.messageId = "";
    this.deviceId = "";
    this.timestamp = 0; // int64
    this.msg = null; // Contains ChatText
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new ChatData();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 1:
          message.messageId = reader.string();
          break;
        case 2:
          message.deviceId = reader.string();
          break;
        case 3:
          message.timestamp = reader.int64();
          break;
        case 5:
          message.msg = ChatText.decode(reader, reader.uint32());
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

class ChatText {
  constructor() {
    this.text = "";
  }

  static decode(reader, length) {
    if (!(reader instanceof Reader)) {
      reader = Reader.create(reader);
    }

    const end = length === undefined ? reader.len : reader.pos + length;
    const message = new ChatText();

    while (reader.pos < end) {
      const tag = reader.uint32();
      
      switch (tag >>> 3) {
        case 1:
          message.text = reader.string();
          break;
        default:
          reader.skipType(tag & 7);
      }
    }

    return message;
  }
}

// Usage example:
function decodeCollectionMessage(unzippedBytes) {
  return CollectionMessage.decode(unzippedBytes);
}

class WebRtcProxy {
    constructor(config) {
        this.state = {
            peerMessages: [],
            logChannelArgs: true,
            channelListeners: []
        };
        this.config = config;
    }

    initialize() {
        if (!window.RTCPeerConnection) {
            return false;
        }

        if (!window.ff_channels) {
            window.ff_channels = {};
        }

        const OriginalRTCPeerConnection = window.RTCPeerConnection;
        const originalCreateDataChannel = OriginalRTCPeerConnection.prototype.createDataChannel;
        const state = this.state;  // Capture state in closure

        if (originalCreateDataChannel) {
            OriginalRTCPeerConnection.prototype.createDataChannel = function() {
                if (state.logChannelArgs) {
                    console.log("creating channel args", arguments);
                }

                try {
                    const channel = originalCreateDataChannel.apply(this, arguments);
                    console.log('channel', channel)
                    console.log('state.channelListeners', state.channelListeners)
                    //channel.addEventListener("message", (event) => {
                    //    console.log('event', event)
                    //});
                    if (channel && state.channelListeners.length > 0) {
                        const matchingListener = state.channelListeners.find(
                            listener => listener.label === channel.label
                        );

                        console.log('matchingListener', matchingListener, 'channel', channel.label)

                        if (matchingListener) {
                            channel.addEventListener("message", matchingListener.callback);
                            
                            if (matchingListener.monitor) {
                                matchingListener.monitor(channel);
                            }
                        }

                        window.ff_channels[channel.label] = channel;
                    }

                    return channel;
                } catch (error) {
                    console.log(error);
                }
            };
        }

        // Capture config in closure
        const config = this.config;

        window.RTCPeerConnection = function(configuration, constraints) {
            const peerConnection = new OriginalRTCPeerConnection(configuration, constraints);
            
            if (config && config.debug) {
                console.log("created peer connection", peerConnection);
                console.log("state", state)
            }

            // Use captured state instead of this.state
            for (const message of state.peerMessages) {
                peerConnection.addEventListener(message.event, (event) => {
                    message.callback(peerConnection, event);
                });
            }

            return peerConnection;
        };

        window.RTCPeerConnection.prototype = OriginalRTCPeerConnection.prototype;
        
        return true;
    }

    register(options) {
        this.state.peerMessages.push(...options.peerMessages);
        this.state.logChannelArgs = options.logChannelArgs;
        this.state.channelListeners.push(...options.channelListeners);
        console.log('register', this.state)
    }
}
const monitorCaptionsChannel = (channel) => {
    console.log('monitorCaptionsChannel', channel)
}

const handleCaptionMessage = (event) => {
    console.log('handleCaptionMessage44', event.data);
    const caption = decodeCaptionFromBuffer(event.data);
    console.log('caption', caption)
}
userMap = new Map()
const handleCollectionMessage = (event) => {
    if (true) {
        console.log("collection message: ", event);
    }


    const unzippedData = Reader.create(pako.inflate(new Uint8Array(event.data)));
    const message = decodeCollectionMessage(unzippedData);
    console.log('handleCollectionMessage message', message)
    if (!message.body?.wrapper?.wrapper) {
        return;
    }

    // Handle chat messages
    if (message.body.wrapper.wrapper.chat) {
        const chatMessages = message.body.wrapper.wrapper.chat;
        for (const chat of chatMessages) {
            const user = userMap.get(chat.body.deviceId);
            chatMessagesMap.set(chat.body.messageId, {
                ...chat.body,
                user: {
                    name: user?.name || "",
                    fullName: user?.fullName || "",
                    image: user?.image || "",
                    id: user?.id || ""
                }
            });
        }
    }

    // Handle user details
    if (message.body.wrapper.wrapper.wrapper?.userDetails) {
        const users = message.body.wrapper.wrapper.wrapper.userDetails;
        for (const user of users) {
            userMap.set(user.deviceId, {
                id: user.deviceId,
                name: user.name,
                fullName: user.fullName,
                image: user.profile
            });
        }
    }
};


const handleDataChannel = (peerConnection, event) => {
    console.log('handleDataChannel', event);
    if (event.channel.label === "collections") {
        window.proxyPeerConnection = peerConnection;
        
        if (true) {
            console.log("data channel message: ", event);
        }
        
        event.channel.addEventListener("message", handleCollectionMessage);
    }
};

const handleTrack = (t) => {
    console.log('handleTrack', t)
}

const peerConnectionProxy = new WebRtcProxy({debug: true});
const proxyStatus = peerConnectionProxy.initialize();
peerConnectionProxy.register({
    logChannelArgs: false,
    peerMessages: [
        { event: "datachannel", callback: handleDataChannel },
        { event: "track", callback: handleTrack }
    ],
    channelListeners: [
        { 
            label: "captions", 
            callback: handleCaptionMessage,
            monitor: monitorCaptionsChannel 
        }
    ]
});

    """

    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': js_code
    })

    driver.get(meet_link)

    driver.execute_cdp_cmd(
        "Browser.grantPermissions",
        {
            "origin": meet_link,
            "permissions": [
                "geolocation",
                "audioCapture",
                "displayCapture",
                "videoCapture",
                "videoCapturePanTiltZoom",
            ],
        },
    )

    print("Waiting for the name input field...")
    name_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][aria-label="Your name"]')
    
    print("Waiting for 1 second...")
    sleep(1)
    
    print("Filling the input field with the name...")
    full_name = "Mr Bot!"
    name_input.send_keys(full_name)
    
    print("Waiting for the 'Ask to join' button...")
    join_button = driver.find_element(By.XPATH, '//button[.//span[text()="Ask to join"]]')
    
    print("Clicking the 'Ask to join' button...")
    join_button.click()

    print("- End of work")
    sleep(10000)


if __name__ == "__main__":
    click.echo("starting google meet recorder...")
    asyncio.run(join_meet())
    click.echo("finished recording google meet.")