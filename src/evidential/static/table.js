var vi=Object.create;var qn=Object.defineProperty;var Ci=Object.getOwnPropertyDescriptor;var Ai=Object.getOwnPropertyNames;var $i=Object.getPrototypeOf,Ni=Object.prototype.hasOwnProperty;var Ei=(t,e)=>()=>(e||t((e={exports:{}}).exports,e),e.exports);var Li=(t,e,r,n)=>{if(e&&typeof e=="object"||typeof e=="function")for(let o of Ai(e))!Ni.call(t,o)&&o!==r&&qn(t,o,{get:()=>e[o],enumerable:!(n=Ci(e,o))||n.enumerable});return t};var Ti=(t,e,r)=>(r=t!=null?vi($i(t)):{},Li(e||!t||!t.__esModule?qn(r,"default",{value:t,enumerable:!0}):r,t));var Yn=Ei((Pc,Wr)=>{var Wn={},Oi=function(e){e.version="0.11.2";function r(x){for(var _="",k=x.length-1;k>=0;)_+=x.charAt(k--);return _}function n(x,_){for(var k="";k.length<_;)k+=x;return k}function o(x,_){var k=""+x;return k.length>=_?k:n("0",_-k.length)+k}function s(x,_){var k=""+x;return k.length>=_?k:n(" ",_-k.length)+k}function i(x,_){var k=""+x;return k.length>=_?k:k+n(" ",_-k.length)}function a(x,_){var k=""+Math.round(x);return k.length>=_?k:n("0",_-k.length)+k}function l(x,_){var k=""+x;return k.length>=_?k:n("0",_-k.length)+k}var c=Math.pow(2,32);function f(x,_){if(x>c||x<-c)return a(x,_);var k=Math.round(x);return l(k,_)}function u(x,_){return _=_||0,x.length>=7+_&&(x.charCodeAt(_)|32)===103&&(x.charCodeAt(_+1)|32)===101&&(x.charCodeAt(_+2)|32)===110&&(x.charCodeAt(_+3)|32)===101&&(x.charCodeAt(_+4)|32)===114&&(x.charCodeAt(_+5)|32)===97&&(x.charCodeAt(_+6)|32)===108}var p=[["Sun","Sunday"],["Mon","Monday"],["Tue","Tuesday"],["Wed","Wednesday"],["Thu","Thursday"],["Fri","Friday"],["Sat","Saturday"]],d=[["J","Jan","January"],["F","Feb","February"],["M","Mar","March"],["A","Apr","April"],["M","May","May"],["J","Jun","June"],["J","Jul","July"],["A","Aug","August"],["S","Sep","September"],["O","Oct","October"],["N","Nov","November"],["D","Dec","December"]];function h(x){x[0]="General",x[1]="0",x[2]="0.00",x[3]="#,##0",x[4]="#,##0.00",x[9]="0%",x[10]="0.00%",x[11]="0.00E+00",x[12]="# ?/?",x[13]="# ??/??",x[14]="m/d/yy",x[15]="d-mmm-yy",x[16]="d-mmm",x[17]="mmm-yy",x[18]="h:mm AM/PM",x[19]="h:mm:ss AM/PM",x[20]="h:mm",x[21]="h:mm:ss",x[22]="m/d/yy h:mm",x[37]="#,##0 ;(#,##0)",x[38]="#,##0 ;[Red](#,##0)",x[39]="#,##0.00;(#,##0.00)",x[40]="#,##0.00;[Red](#,##0.00)",x[45]="mm:ss",x[46]="[h]:mm:ss",x[47]="mmss.0",x[48]="##0.0E+0",x[49]="@",x[56]='"\u4E0A\u5348/\u4E0B\u5348 "hh"\u6642"mm"\u5206"ss"\u79D2 "'}var m={};h(m);var y=[],g=0;for(g=5;g<=8;++g)y[g]=32+g;for(g=23;g<=26;++g)y[g]=0;for(g=27;g<=31;++g)y[g]=14;for(g=50;g<=58;++g)y[g]=14;for(g=59;g<=62;++g)y[g]=g-58;for(g=67;g<=68;++g)y[g]=g-58;for(g=72;g<=75;++g)y[g]=g-58;for(g=67;g<=68;++g)y[g]=g-57;for(g=76;g<=78;++g)y[g]=g-56;for(g=79;g<=81;++g)y[g]=g-34;var w=[];w[5]=w[63]='"$"#,##0_);\\("$"#,##0\\)',w[6]=w[64]='"$"#,##0_);[Red]\\("$"#,##0\\)',w[7]=w[65]='"$"#,##0.00_);\\("$"#,##0.00\\)',w[8]=w[66]='"$"#,##0.00_);[Red]\\("$"#,##0.00\\)',w[41]='_(* #,##0_);_(* \\(#,##0\\);_(* "-"_);_(@_)',w[42]='_("$"* #,##0_);_("$"* \\(#,##0\\);_("$"* "-"_);_(@_)',w[43]='_(* #,##0.00_);_(* \\(#,##0.00\\);_(* "-"??_);_(@_)',w[44]='_("$"* #,##0.00_);_("$"* \\(#,##0.00\\);_("$"* "-"??_);_(@_)';function E(x,_,k){for(var H=x<0?-1:1,S=x*H,W=0,v=1,z=0,tt=1,I=0,et=0,st=Math.floor(S);I<_&&(st=Math.floor(S),z=st*v+W,et=st*I+tt,!(S-st<5e-8));)S=1/(S-st),W=v,v=z,tt=I,I=et;if(et>_&&(I>_?(et=tt,z=W):(et=I,z=v)),!k)return[0,H*z,et];var zt=Math.floor(H*z/et);return[zt,H*z-zt*et,et]}function L(x,_,k){if(x>2958465||x<0)return null;var H=x|0,S=Math.floor(86400*(x-H)),W=0,v=[],z={D:H,T:S,u:86400*(x-H)-S,y:0,m:0,d:0,H:0,M:0,S:0,q:0};if(Math.abs(z.u)<1e-6&&(z.u=0),_&&_.date1904&&(H+=1462),z.u>.9999&&(z.u=0,++S==86400&&(z.T=S=0,++H,++z.D)),H===60)v=k?[1317,10,29]:[1900,2,29],W=3;else if(H===0)v=k?[1317,8,29]:[1900,1,0],W=6;else{H>60&&--H;var tt=new Date(1900,0,1);tt.setDate(tt.getDate()+H-1),v=[tt.getFullYear(),tt.getMonth()+1,tt.getDate()],W=tt.getDay(),H<60&&(W=(W+6)%7),k&&(W=Y(tt,v))}return z.y=v[0],z.m=v[1],z.d=v[2],z.S=S%60,S=Math.floor(S/60),z.M=S%60,S=Math.floor(S/60),z.H=S,z.q=W,z}e.parse_date_code=L;var N=new Date(1899,11,31,0,0,0),O=N.getTime(),C=new Date(1900,2,1,0,0,0);function R(x,_){var k=x.getTime();return _?k-=1262304e5:x>=C&&(k+=864e5),(k-(O+(x.getTimezoneOffset()-N.getTimezoneOffset())*6e4))/864e5}function j(x){return x.toString(10)}e._general_int=j;var B=(function(){var _=/(?:\.0*|(\.\d*[1-9])0+)$/;function k(I){return I.indexOf(".")==-1?I:I.replace(_,"$1")}var H=/(?:\.0*|(\.\d*[1-9])0+)[Ee]/,S=/(E[+-])(\d)$/;function W(I){return I.indexOf("E")==-1?I:I.replace(H,"$1E").replace(S,"$10$2")}function v(I){var et=I<0?12:11,st=k(I.toFixed(12));return st.length<=et||(st=I.toPrecision(10),st.length<=et)?st:I.toExponential(5)}function z(I){var et=k(I.toFixed(11));return et.length>(I<0?12:11)||et==="0"||et==="-0"?I.toPrecision(6):et}function tt(I){var et=Math.floor(Math.log(Math.abs(I))*Math.LOG10E),st;return et>=-4&&et<=-1?st=I.toPrecision(10+et):Math.abs(et)<=9?st=v(I):et===10?st=I.toFixed(10).substr(0,12):st=z(I),k(W(st.toUpperCase()))}return tt})();e._general_num=B;function U(x,_){switch(typeof x){case"string":return x;case"boolean":return x?"TRUE":"FALSE";case"number":return(x|0)===x?x.toString(10):B(x);case"undefined":return"";case"object":if(x==null)return"";if(x instanceof Date)return Ot(14,R(x,_&&_.date1904),_)}throw new Error("unsupported value in General format: "+x)}e._general=U;function Y(x,_){_[0]-=581;var k=x.getDay();return x<60&&(k=(k+6)%7),k}var X="\u0E50\u0E51\u0E52\u0E53\u0E54\u0E55\u0E56\u0E57\u0E58\u0E59".split("");function Nt(x,_,k,H){var S="",W=0,v=0,z=k.y,tt,I=0;switch(x){case 98:z=k.y+543;case 121:switch(_.length){case 1:case 2:tt=z%100,I=2;break;default:tt=z%1e4,I=4;break}break;case 109:switch(_.length){case 1:case 2:tt=k.m,I=_.length;break;case 3:return d[k.m-1][1];case 5:return d[k.m-1][0];default:return d[k.m-1][2]}break;case 100:switch(_.length){case 1:case 2:tt=k.d,I=_.length;break;case 3:return p[k.q][0];default:return p[k.q][1]}break;case 104:switch(_.length){case 1:case 2:tt=1+(k.H+11)%12,I=_.length;break;default:throw"bad hour format: "+_}break;case 72:switch(_.length){case 1:case 2:tt=k.H,I=_.length;break;default:throw"bad hour format: "+_}break;case 77:switch(_.length){case 1:case 2:tt=k.M,I=_.length;break;default:throw"bad minute format: "+_}break;case 115:if(_!="s"&&_!="ss"&&_!=".0"&&_!=".00"&&_!=".000")throw"bad second format: "+_;return k.u===0&&(_=="s"||_=="ss")?o(k.S,_.length):(H>=2?v=H===3?1e3:100:v=H===1?10:1,W=Math.round(v*(k.S+k.u)),W>=60*v&&(W=0),_==="s"?W===0?"0":""+W/v:(S=o(W,2+H),_==="ss"?S.substr(0,2):"."+S.substr(2,_.length-1)));case 90:switch(_){case"[h]":case"[hh]":tt=k.D*24+k.H;break;case"[m]":case"[mm]":tt=(k.D*24+k.H)*60+k.M;break;case"[s]":case"[ss]":tt=((k.D*24+k.H)*60+k.M)*60+Math.round(k.S+k.u);break;default:throw"bad abstime format: "+_}I=_.length===3?1:2;break;case 101:tt=z,I=1;break}var et=I>0?o(tt,I):"";return et}function dt(x){var _=3;if(x.length<=_)return x;for(var k=x.length%_,H=x.substr(0,k);k!=x.length;k+=_)H+=(H.length>0?",":"")+x.substr(k,_);return H}var mt=(function(){var _=/%/g;function k(D,M,A){var J=M.replace(_,""),T=M.length-J.length;return mt(D,J,A*Math.pow(10,2*T))+n("%",T)}function H(D,M,A){for(var J=M.length-1;M.charCodeAt(J-1)===44;)--J;return mt(D,M.substr(0,J),A/Math.pow(10,3*(M.length-J)))}function S(D,M){var A,J=D.indexOf("E")-D.indexOf(".")-1;if(D.match(/^#+0.0E\+0$/)){if(M==0)return"0.0E+0";if(M<0)return"-"+S(D,-M);var T=D.indexOf(".");T===-1&&(T=D.indexOf("E"));var P=Math.floor(Math.log(M)*Math.LOG10E)%T;if(P<0&&(P+=T),A=(M/Math.pow(10,P)).toPrecision(J+1+(T+P)%T),A.indexOf("e")===-1){var nt=Math.floor(Math.log(M)*Math.LOG10E);for(A.indexOf(".")===-1?A=A.charAt(0)+"."+A.substr(1)+"E+"+(nt-A.length+P):A+="E+"+(nt-P);A.substr(0,2)==="0.";)A=A.charAt(0)+A.substr(2,T)+"."+A.substr(2+T),A=A.replace(/^0+([1-9])/,"$1").replace(/^0+\./,"0.");A=A.replace(/\+-/,"-")}A=A.replace(/^([+-]?)(\d*)\.(\d*)[Ee]/,function(gt,yt,_t,it){return yt+_t+it.substr(0,(T+P)%T)+"."+it.substr(P)+"E"})}else A=M.toExponential(J);return D.match(/E\+00$/)&&A.match(/e[+-]\d$/)&&(A=A.substr(0,A.length-1)+"0"+A.charAt(A.length-1)),D.match(/E\-/)&&A.match(/e\+/)&&(A=A.replace(/e\+/,"e")),A.replace("e","E")}var W=/# (\?+)( ?)\/( ?)(\d+)/;function v(D,M,A){var J=parseInt(D[4],10),T=Math.round(M*J),P=Math.floor(T/J),nt=T-P*J,gt=J;return A+(P===0?"":""+P)+" "+(nt===0?n(" ",D[1].length+1+D[4].length):s(nt,D[1].length)+D[2]+"/"+D[3]+o(gt,D[4].length))}function z(D,M,A){return A+(M===0?"":""+M)+n(" ",D[1].length+2+D[4].length)}var tt=/^#*0*\.([0#]+)/,I=/\).*[0#]/,et=/\(###\) ###\\?-####/;function st(D){for(var M="",A,J=0;J!=D.length;++J)switch(A=D.charCodeAt(J)){case 35:break;case 63:M+=" ";break;case 48:M+="0";break;default:M+=String.fromCharCode(A)}return M}function zt(D,M){var A=Math.pow(10,M);return""+Math.round(D*A)/A}function ae(D,M){var A=D-Math.floor(D),J=Math.pow(10,M);return M<(""+Math.round(A*J)).length?0:Math.round(A*J)}function Vr(D,M){return M<(""+Math.round((D-Math.floor(D))*Math.pow(10,M))).length?1:0}function It(D){return D<2147483647&&D>-2147483648?""+(D>=0?D|0:D-1|0):""+Math.floor(D)}function ut(D,M,A){if(D.charCodeAt(0)===40&&!M.match(I)){var J=M.replace(/\( */,"").replace(/ \)/,"").replace(/\)/,"");return A>=0?ut("n",J,A):"("+ut("n",J,-A)+")"}if(M.charCodeAt(M.length-1)===44)return H(D,M,A);if(M.indexOf("%")!==-1)return k(D,M,A);if(M.indexOf("E")!==-1)return S(M,A);if(M.charCodeAt(0)===36)return"$"+ut(D,M.substr(M.charAt(1)==" "?2:1),A);var T,P,nt,gt,yt=Math.abs(A),_t=A<0?"-":"";if(M.match(/^00+$/))return _t+f(yt,M.length);if(M.match(/^[#?]+$/))return T=f(A,0),T==="0"&&(T=""),T.length>M.length?T:st(M.substr(0,M.length-T.length))+T;if(P=M.match(W))return v(P,yt,_t);if(M.match(/^#+0+$/))return _t+f(yt,M.length-M.indexOf("0"));if(P=M.match(tt))return T=zt(A,P[1].length).replace(/^([^\.]+)$/,"$1."+st(P[1])).replace(/\.$/,"."+st(P[1])).replace(/\.(\d*)$/,function(Lt,Ee){return"."+Ee+n("0",st(P[1]).length-Ee.length)}),M.indexOf("0.")!==-1?T:T.replace(/^0\./,".");if(M=M.replace(/^#+([0.])/,"$1"),P=M.match(/^(0*)\.(#*)$/))return _t+zt(yt,P[2].length).replace(/\.(\d*[1-9])0*$/,".$1").replace(/^(-?\d*)$/,"$1.").replace(/^0\./,P[1].length?"0.":".");if(P=M.match(/^#{1,3},##0(\.?)$/))return _t+dt(f(yt,0));if(P=M.match(/^#,##0\.([#0]*0)$/))return A<0?"-"+ut(D,M,-A):dt(""+(Math.floor(A)+Vr(A,P[1].length)))+"."+o(ae(A,P[1].length),P[1].length);if(P=M.match(/^#,#*,#0/))return ut(D,M.replace(/^#,#*,/,""),A);if(P=M.match(/^([0#]+)(\\?-([0#]+))+$/))return T=r(ut(D,M.replace(/[\\-]/g,""),A)),nt=0,r(r(M.replace(/\\/g,"")).replace(/[0#]/g,function(Lt){return nt<T.length?T.charAt(nt++):Lt==="0"?"0":""}));if(M.match(et))return T=ut(D,"##########",A),"("+T.substr(0,3)+") "+T.substr(3,3)+"-"+T.substr(6);var it="";if(P=M.match(/^([#0?]+)( ?)\/( ?)([#0?]+)/))return nt=Math.min(P[4].length,7),gt=E(yt,Math.pow(10,nt)-1,!1),T=""+_t,it=mt("n",P[1],gt[1]),it.charAt(it.length-1)==" "&&(it=it.substr(0,it.length-1)+"0"),T+=it+P[2]+"/"+P[3],it=i(gt[2],nt),it.length<P[4].length&&(it=st(P[4].substr(P[4].length-it.length))+it),T+=it,T;if(P=M.match(/^# ([#0?]+)( ?)\/( ?)([#0?]+)/))return nt=Math.min(Math.max(P[1].length,P[4].length),7),gt=E(yt,Math.pow(10,nt)-1,!0),_t+(gt[0]||(gt[1]?"":"0"))+" "+(gt[1]?s(gt[1],nt)+P[2]+"/"+P[3]+i(gt[2],nt):n(" ",2*nt+1+P[2].length+P[3].length));if(P=M.match(/^[#0?]+$/))return T=f(A,0),M.length<=T.length?T:st(M.substr(0,M.length-T.length))+T;if(P=M.match(/^([#0?]+)\.([#0]+)$/)){T=""+A.toFixed(Math.min(P[2].length,10)).replace(/([^0])0+$/,"$1"),nt=T.indexOf(".");var $e=M.indexOf(".")-nt,qr=M.length-T.length-$e;return st(M.substr(0,$e)+T+M.substr(M.length-qr))}if(P=M.match(/^00,000\.([#0]*0)$/))return nt=ae(A,P[1].length),A<0?"-"+ut(D,M,-A):dt(It(A)).replace(/^\d,\d{3}$/,"0$&").replace(/^\d*$/,function(Lt){return"00,"+(Lt.length<3?o(0,3-Lt.length):"")+Lt})+"."+o(nt,P[1].length);switch(M){case"###,##0.00":return ut(D,"#,##0.00",A);case"###,###":case"##,###":case"#,###":var Ne=dt(f(yt,0));return Ne!=="0"?_t+Ne:"";case"###,###.00":return ut(D,"###,##0.00",A).replace(/^0\./,".");case"#,###.00":return ut(D,"#,##0.00",A).replace(/^0\./,".");default:}throw new Error("unsupported format |"+M+"|")}function Ae(D,M,A){for(var J=M.length-1;M.charCodeAt(J-1)===44;)--J;return mt(D,M.substr(0,J),A/Math.pow(10,3*(M.length-J)))}function Ve(D,M,A){var J=M.replace(_,""),T=M.length-J.length;return mt(D,J,A*Math.pow(10,2*T))+n("%",T)}function Ut(D,M){var A,J=D.indexOf("E")-D.indexOf(".")-1;if(D.match(/^#+0.0E\+0$/)){if(M==0)return"0.0E+0";if(M<0)return"-"+Ut(D,-M);var T=D.indexOf(".");T===-1&&(T=D.indexOf("E"));var P=Math.floor(Math.log(M)*Math.LOG10E)%T;if(P<0&&(P+=T),A=(M/Math.pow(10,P)).toPrecision(J+1+(T+P)%T),!A.match(/[Ee]/)){var nt=Math.floor(Math.log(M)*Math.LOG10E);A.indexOf(".")===-1?A=A.charAt(0)+"."+A.substr(1)+"E+"+(nt-A.length+P):A+="E+"+(nt-P),A=A.replace(/\+-/,"-")}A=A.replace(/^([+-]?)(\d*)\.(\d*)[Ee]/,function(gt,yt,_t,it){return yt+_t+it.substr(0,(T+P)%T)+"."+it.substr(P)+"E"})}else A=M.toExponential(J);return D.match(/E\+00$/)&&A.match(/e[+-]\d$/)&&(A=A.substr(0,A.length-1)+"0"+A.charAt(A.length-1)),D.match(/E\-/)&&A.match(/e\+/)&&(A=A.replace(/e\+/,"e")),A.replace("e","E")}function Q(D,M,A){if(D.charCodeAt(0)===40&&!M.match(I)){var J=M.replace(/\( */,"").replace(/ \)/,"").replace(/\)/,"");return A>=0?Q("n",J,A):"("+Q("n",J,-A)+")"}if(M.charCodeAt(M.length-1)===44)return Ae(D,M,A);if(M.indexOf("%")!==-1)return Ve(D,M,A);if(M.indexOf("E")!==-1)return Ut(M,A);if(M.charCodeAt(0)===36)return"$"+Q(D,M.substr(M.charAt(1)==" "?2:1),A);var T,P,nt,gt,yt=Math.abs(A),_t=A<0?"-":"";if(M.match(/^00+$/))return _t+o(yt,M.length);if(M.match(/^[#?]+$/))return T=""+A,A===0&&(T=""),T.length>M.length?T:st(M.substr(0,M.length-T.length))+T;if(P=M.match(W))return z(P,yt,_t);if(M.match(/^#+0+$/))return _t+o(yt,M.length-M.indexOf("0"));if(P=M.match(tt))return T=(""+A).replace(/^([^\.]+)$/,"$1."+st(P[1])).replace(/\.$/,"."+st(P[1])),T=T.replace(/\.(\d*)$/,function(Lt,Ee){return"."+Ee+n("0",st(P[1]).length-Ee.length)}),M.indexOf("0.")!==-1?T:T.replace(/^0\./,".");if(M=M.replace(/^#+([0.])/,"$1"),P=M.match(/^(0*)\.(#*)$/))return _t+(""+yt).replace(/\.(\d*[1-9])0*$/,".$1").replace(/^(-?\d*)$/,"$1.").replace(/^0\./,P[1].length?"0.":".");if(P=M.match(/^#{1,3},##0(\.?)$/))return _t+dt(""+yt);if(P=M.match(/^#,##0\.([#0]*0)$/))return A<0?"-"+Q(D,M,-A):dt(""+A)+"."+n("0",P[1].length);if(P=M.match(/^#,#*,#0/))return Q(D,M.replace(/^#,#*,/,""),A);if(P=M.match(/^([0#]+)(\\?-([0#]+))+$/))return T=r(Q(D,M.replace(/[\\-]/g,""),A)),nt=0,r(r(M.replace(/\\/g,"")).replace(/[0#]/g,function(Lt){return nt<T.length?T.charAt(nt++):Lt==="0"?"0":""}));if(M.match(et))return T=Q(D,"##########",A),"("+T.substr(0,3)+") "+T.substr(3,3)+"-"+T.substr(6);var it="";if(P=M.match(/^([#0?]+)( ?)\/( ?)([#0?]+)/))return nt=Math.min(P[4].length,7),gt=E(yt,Math.pow(10,nt)-1,!1),T=""+_t,it=mt("n",P[1],gt[1]),it.charAt(it.length-1)==" "&&(it=it.substr(0,it.length-1)+"0"),T+=it+P[2]+"/"+P[3],it=i(gt[2],nt),it.length<P[4].length&&(it=st(P[4].substr(P[4].length-it.length))+it),T+=it,T;if(P=M.match(/^# ([#0?]+)( ?)\/( ?)([#0?]+)/))return nt=Math.min(Math.max(P[1].length,P[4].length),7),gt=E(yt,Math.pow(10,nt)-1,!0),_t+(gt[0]||(gt[1]?"":"0"))+" "+(gt[1]?s(gt[1],nt)+P[2]+"/"+P[3]+i(gt[2],nt):n(" ",2*nt+1+P[2].length+P[3].length));if(P=M.match(/^[#0?]+$/))return T=""+A,M.length<=T.length?T:st(M.substr(0,M.length-T.length))+T;if(P=M.match(/^([#0]+)\.([#0]+)$/)){T=""+A.toFixed(Math.min(P[2].length,10)).replace(/([^0])0+$/,"$1"),nt=T.indexOf(".");var $e=M.indexOf(".")-nt,qr=M.length-T.length-$e;return st(M.substr(0,$e)+T+M.substr(M.length-qr))}if(P=M.match(/^00,000\.([#0]*0)$/))return A<0?"-"+Q(D,M,-A):dt(""+A).replace(/^\d,\d{3}$/,"0$&").replace(/^\d*$/,function(Lt){return"00,"+(Lt.length<3?o(0,3-Lt.length):"")+Lt})+"."+o(0,P[1].length);switch(M){case"###,###":case"##,###":case"#,###":var Ne=dt(""+yt);return Ne!=="0"?_t+Ne:"";default:if(M.match(/\.[0#?]*$/))return Q(D,M.slice(0,M.lastIndexOf(".")),A)+st(M.slice(M.lastIndexOf(".")))}throw new Error("unsupported format |"+M+"|")}return function(M,A,J){return(J|0)===J?Q(M,A,J):ut(M,A,J)}})();function rt(x){for(var _=[],k=!1,H=0,S=0;H<x.length;++H)switch(x.charCodeAt(H)){case 34:k=!k;break;case 95:case 42:case 92:++H;break;case 59:_[_.length]=x.substr(S,H-S),S=H+1}if(_[_.length]=x.substr(S),k===!0)throw new Error("Format |"+x+"| unterminated string ");return _}e._split=rt;var xt=/\[[HhMmSs\u0E0A\u0E19\u0E17]*\]/;function At(x){for(var _=0,k="",H="";_<x.length;)switch(k=x.charAt(_)){case"G":u(x,_)&&(_+=6),_++;break;case'"':for(;x.charCodeAt(++_)!==34&&_<x.length;);++_;break;case"\\":_+=2;break;case"_":_+=2;break;case"@":++_;break;case"B":case"b":if(x.charAt(_+1)==="1"||x.charAt(_+1)==="2")return!0;case"M":case"D":case"Y":case"H":case"S":case"E":case"m":case"d":case"y":case"h":case"s":case"e":case"g":return!0;case"A":case"a":case"\u4E0A":if(x.substr(_,3).toUpperCase()==="A/P"||x.substr(_,5).toUpperCase()==="AM/PM"||x.substr(_,5).toUpperCase()==="\u4E0A\u5348/\u4E0B\u5348")return!0;++_;break;case"[":for(H=k;x.charAt(_++)!=="]"&&_<x.length;)H+=x.charAt(_);if(H.match(xt))return!0;break;case".":case"0":case"#":for(;_<x.length&&("0#?.,E+-%".indexOf(k=x.charAt(++_))>-1||k=="\\"&&x.charAt(_+1)=="-"&&"0#".indexOf(x.charAt(_+2))>-1););break;case"?":for(;x.charAt(++_)===k;);break;case"*":++_,(x.charAt(_)==" "||x.charAt(_)=="*")&&++_;break;case"(":case")":++_;break;case"1":case"2":case"3":case"4":case"5":case"6":case"7":case"8":case"9":for(;_<x.length&&"0123456789".indexOf(x.charAt(++_))>-1;);break;case" ":++_;break;default:++_;break}return!1}e.is_date=At;function G(x,_,k,H){for(var S=[],W="",v=0,z="",tt="t",I,et,st,zt="H";v<x.length;)switch(z=x.charAt(v)){case"G":if(!u(x,v))throw new Error("unrecognized character "+z+" in "+x);S[S.length]={t:"G",v:"General"},v+=7;break;case'"':for(W="";(st=x.charCodeAt(++v))!==34&&v<x.length;)W+=String.fromCharCode(st);S[S.length]={t:"t",v:W},++v;break;case"\\":var ae=x.charAt(++v),Vr=ae==="("||ae===")"?ae:"t";S[S.length]={t:Vr,v:ae},++v;break;case"_":S[S.length]={t:"t",v:" "},v+=2;break;case"@":S[S.length]={t:"T",v:_},++v;break;case"B":case"b":if(x.charAt(v+1)==="1"||x.charAt(v+1)==="2"){if(I==null&&(I=L(_,k,x.charAt(v+1)==="2"),I==null))return"";S[S.length]={t:"X",v:x.substr(v,2)},tt=z,v+=2;break}case"M":case"D":case"Y":case"H":case"S":case"E":z=z.toLowerCase();case"m":case"d":case"y":case"h":case"s":case"e":case"g":if(_<0||I==null&&(I=L(_,k),I==null))return"";for(W=z;++v<x.length&&x.charAt(v).toLowerCase()===z;)W+=z;z==="m"&&tt.toLowerCase()==="h"&&(z="M"),z==="h"&&(z=zt),S[S.length]={t:z,v:W},tt=z;break;case"A":case"a":case"\u4E0A":var It={t:z,v:z};if(I==null&&(I=L(_,k)),x.substr(v,3).toUpperCase()==="A/P"?(I!=null&&(It.v=I.H>=12?"P":"A"),It.t="T",zt="h",v+=3):x.substr(v,5).toUpperCase()==="AM/PM"?(I!=null&&(It.v=I.H>=12?"PM":"AM"),It.t="T",v+=5,zt="h"):x.substr(v,5).toUpperCase()==="\u4E0A\u5348/\u4E0B\u5348"?(I!=null&&(It.v=I.H>=12?"\u4E0B\u5348":"\u4E0A\u5348"),It.t="T",v+=5,zt="h"):(It.t="t",++v),I==null&&It.t==="T")return"";S[S.length]=It,tt=z;break;case"[":for(W=z;x.charAt(v++)!=="]"&&v<x.length;)W+=x.charAt(v);if(W.slice(-1)!=="]")throw'unterminated "[" block: |'+W+"|";if(W.match(xt)){if(I==null&&(I=L(_,k),I==null))return"";S[S.length]={t:"Z",v:W.toLowerCase()},tt=W.charAt(1)}else W.indexOf("$")>-1&&(W=(W.match(/\$([^-\[\]]*)/)||[])[1]||"$",At(x)||(S[S.length]={t:"t",v:W}));break;case".":if(I!=null){for(W=z;++v<x.length&&(z=x.charAt(v))==="0";)W+=z;S[S.length]={t:"s",v:W};break}case"0":case"#":for(W=z;++v<x.length&&"0#?.,E+-%".indexOf(z=x.charAt(v))>-1;)W+=z;S[S.length]={t:"n",v:W};break;case"?":for(W=z;x.charAt(++v)===z;)W+=z;S[S.length]={t:z,v:W},tt=z;break;case"*":++v,(x.charAt(v)==" "||x.charAt(v)=="*")&&++v;break;case"(":case")":S[S.length]={t:H===1?"t":z,v:z},++v;break;case"1":case"2":case"3":case"4":case"5":case"6":case"7":case"8":case"9":for(W=z;v<x.length&&"0123456789".indexOf(x.charAt(++v))>-1;)W+=x.charAt(v);S[S.length]={t:"D",v:W};break;case" ":S[S.length]={t:z,v:z},++v;break;case"$":S[S.length]={t:"t",v:"$"},++v;break;default:if(",$-+/():!^&'~{}<>=\u20ACacfijklopqrtuvwxzP".indexOf(z)===-1)throw new Error("unrecognized character "+z+" in "+x);S[S.length]={t:"t",v:z},++v;break}var ut=0,Ae=0,Ve;for(v=S.length-1,tt="t";v>=0;--v)switch(S[v].t){case"h":case"H":S[v].t=zt,tt="h",ut<1&&(ut=1);break;case"s":(Ve=S[v].v.match(/\.0+$/))&&(Ae=Math.max(Ae,Ve[0].length-1)),ut<3&&(ut=3);case"d":case"y":case"M":case"e":tt=S[v].t;break;case"m":tt==="s"&&(S[v].t="M",ut<2&&(ut=2));break;case"X":break;case"Z":ut<1&&S[v].v.match(/[Hh]/)&&(ut=1),ut<2&&S[v].v.match(/[Mm]/)&&(ut=2),ut<3&&S[v].v.match(/[Ss]/)&&(ut=3)}switch(ut){case 0:break;case 1:I.u>=.5&&(I.u=0,++I.S),I.S>=60&&(I.S=0,++I.M),I.M>=60&&(I.M=0,++I.H);break;case 2:I.u>=.5&&(I.u=0,++I.S),I.S>=60&&(I.S=0,++I.M);break}var Ut="",Q;for(v=0;v<S.length;++v)switch(S[v].t){case"t":case"T":case" ":case"D":break;case"X":S[v].v="",S[v].t=";";break;case"d":case"m":case"y":case"h":case"H":case"M":case"s":case"e":case"b":case"Z":S[v].v=Nt(S[v].t.charCodeAt(0),S[v].v,I,Ae),S[v].t="t";break;case"n":case"?":for(Q=v+1;S[Q]!=null&&((z=S[Q].t)==="?"||z==="D"||(z===" "||z==="t")&&S[Q+1]!=null&&(S[Q+1].t==="?"||S[Q+1].t==="t"&&S[Q+1].v==="/")||S[v].t==="("&&(z===" "||z==="n"||z===")")||z==="t"&&(S[Q].v==="/"||S[Q].v===" "&&S[Q+1]!=null&&S[Q+1].t=="?"));)S[v].v+=S[Q].v,S[Q]={v:"",t:";"},++Q;Ut+=S[v].v,v=Q-1;break;case"G":S[v].t="t",S[v].v=U(_,k);break}var D="",M,A;if(Ut.length>0){Ut.charCodeAt(0)==40?(M=_<0&&Ut.charCodeAt(0)===45?-_:_,A=mt("n",Ut,M)):(M=_<0&&H>1?-_:_,A=mt("n",Ut,M),M<0&&S[0]&&S[0].t=="t"&&(A=A.substr(1),S[0].v="-"+S[0].v)),Q=A.length-1;var J=S.length;for(v=0;v<S.length;++v)if(S[v]!=null&&S[v].t!="t"&&S[v].v.indexOf(".")>-1){J=v;break}var T=S.length;if(J===S.length&&A.indexOf("E")===-1){for(v=S.length-1;v>=0;--v)S[v]==null||"n?".indexOf(S[v].t)===-1||(Q>=S[v].v.length-1?(Q-=S[v].v.length,S[v].v=A.substr(Q+1,S[v].v.length)):Q<0?S[v].v="":(S[v].v=A.substr(0,Q+1),Q=-1),S[v].t="t",T=v);Q>=0&&T<S.length&&(S[T].v=A.substr(0,Q+1)+S[T].v)}else if(J!==S.length&&A.indexOf("E")===-1){for(Q=A.indexOf(".")-1,v=J;v>=0;--v)if(!(S[v]==null||"n?".indexOf(S[v].t)===-1)){for(et=S[v].v.indexOf(".")>-1&&v===J?S[v].v.indexOf(".")-1:S[v].v.length-1,D=S[v].v.substr(et+1);et>=0;--et)Q>=0&&(S[v].v.charAt(et)==="0"||S[v].v.charAt(et)==="#")&&(D=A.charAt(Q--)+D);S[v].v=D,S[v].t="t",T=v}for(Q>=0&&T<S.length&&(S[T].v=A.substr(0,Q+1)+S[T].v),Q=A.indexOf(".")+1,v=J;v<S.length;++v)if(!(S[v]==null||"n?(".indexOf(S[v].t)===-1&&v!==J)){for(et=S[v].v.indexOf(".")>-1&&v===J?S[v].v.indexOf(".")+1:0,D=S[v].v.substr(0,et);et<S[v].v.length;++et)Q<A.length&&(D+=A.charAt(Q++));S[v].v=D,S[v].t="t",T=v}}}for(v=0;v<S.length;++v)S[v]!=null&&"n?".indexOf(S[v].t)>-1&&(M=H>1&&_<0&&v>0&&S[v-1].v==="-"?-_:_,S[v].v=mt(S[v].t,S[v].v,M),S[v].t="t");var P="";for(v=0;v!==S.length;++v)S[v]!=null&&(P+=S[v].v);return P}e._eval=G;var ct=/\[[=<>]/,ft=/\[(=|>[=]?|<[>=]?)(-?\d+(?:\.\d*)?)\]/;function ht(x,_){if(_==null)return!1;var k=parseFloat(_[2]);switch(_[1]){case"=":if(x==k)return!0;break;case">":if(x>k)return!0;break;case"<":if(x<k)return!0;break;case"<>":if(x!=k)return!0;break;case">=":if(x>=k)return!0;break;case"<=":if(x<=k)return!0;break}return!1}function Et(x,_){var k=rt(x),H=k.length,S=k[H-1].indexOf("@");if(H<4&&S>-1&&--H,k.length>4)throw new Error("cannot find right format for |"+k.join("|")+"|");if(typeof _!="number")return[4,k.length===4||S>-1?k[k.length-1]:"@"];switch(k.length){case 1:k=S>-1?["General","General","General",k[0]]:[k[0],k[0],k[0],"@"];break;case 2:k=S>-1?[k[0],k[0],k[0],k[1]]:[k[0],k[1],k[0],"@"];break;case 3:k=S>-1?[k[0],k[1],k[0],k[2]]:[k[0],k[1],k[2],"@"];break;case 4:break}var W=_>0?k[0]:_<0?k[1]:k[2];if(k[0].indexOf("[")===-1&&k[1].indexOf("[")===-1)return[H,W];if(k[0].match(ct)!=null||k[1].match(ct)!=null){var v=k[0].match(ft),z=k[1].match(ft);return ht(_,v)?[H,k[0]]:ht(_,z)?[H,k[1]]:[H,k[v!=null&&z!=null?2:1]]}return[H,W]}function Ot(x,_,k){k==null&&(k={});var H="";switch(typeof x){case"string":x=="m/d/yy"&&k.dateNF?H=k.dateNF:H=x;break;case"number":x==14&&k.dateNF?H=k.dateNF:H=(k.table!=null?k.table:m)[x],H==null&&(H=k.table&&k.table[y[x]]||m[y[x]]),H==null&&(H=w[x]||"General");break}if(u(H,0))return U(_,k);_ instanceof Date&&(_=R(_,k.date1904));var S=Et(H,_);if(u(S[1]))return U(_,k);if(_===!0)_="TRUE";else if(_===!1)_="FALSE";else if(_===""||_==null)return"";return G(S[1],_,k,S[0])}function at(x,_){if(typeof _!="number"){_=+_||-1;for(var k=0;k<392;++k){if(m[k]==null){_<0&&(_=k);continue}if(m[k]==x){_=k;break}}_<0&&(_=391)}return m[_]=x,_}e.load=at,e._table=m,e.get_table=function(){return m},e.load_table=function(_){for(var k=0;k!=392;++k)_[k]!==void 0&&at(_[k],k)},e.init_table=h,e.format=Ot};Oi(Wn);typeof Wr<"u"&&typeof DO_NOT_EXPORT_SSF>"u"&&(Wr.exports=Wn)});var he=["*","\u2020","\u2021","\xA7","\xB6","#","+","\u25C6","\u25C7","\u25B3"];function Ur(t,e={},r=t){let n=e.footnote_marks||"symbols";if(n==="letters")return String.fromCharCode(96+(t-1)%26+1);if(n==="numbers")return String(t);let o=Math.min(he.length,Math.max(0,r-he.length));return t<=o*2?he[Math.floor((t-1)/2)].repeat((t-1)%2+1):t<=he.length+o?he[t-o-1]:String(t-he.length-o)}function Un(t,e,r){for(let n of t.querySelectorAll("sup[data-footnote-index]"))n.textContent=Ur(Number(n.dataset.footnoteIndex),r,e)}function b(t,e={},r=[]){let n=document.createElement(t);for(let[s,i]of Object.entries(e))i==null||i===!1||(s==="class"?n.className=i:s==="dataset"?Object.assign(n.dataset,i):s==="style"&&typeof i=="object"?Object.assign(n.style,i):s.startsWith("on")&&typeof i=="function"?n.addEventListener(s.slice(2),i):s==="html"?n.innerHTML=i:n.setAttribute(s,i));let o=Array.isArray(r)?r:[r];for(let s of o)s==null||s===!1||n.append(s instanceof Node?s:document.createTextNode(String(s)));return n}function Kr(t){return typeof t=="object"?JSON.stringify(t):String(t)}function $t(t,e){let r=t.stub;return r==null||!e?!1:Array.isArray(r)?r.includes(e.name):r===e.name}function me(t){let e=document.createDocumentFragment(),r=String(t??""),n=/\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_|`([^`]+)`/g,o=0;for(let s of r.matchAll(n)){s.index>o&&e.append(document.createTextNode(r.slice(o,s.index)));let[i,a,l,c,f,u]=s,p=a??l??c??f??u??i;u!=null?e.append(b("code",{},p)):a!=null||l!=null?e.append(b("strong",{},p)):e.append(b("em",{},p)),o=s.index+i.length}return o<r.length&&e.append(document.createTextNode(r.slice(o))),e}function Pi(t){switch(t){case"oldstyle":case"oldstyle-tabular":return"oldstyle-nums tabular-nums";case"proportional":case"lining-proportional":return"lining-nums proportional-nums";case"oldstyle-proportional":return"oldstyle-nums proportional-nums";case"lining":case"tabular":case"lining-tabular":return"lining-nums tabular-nums";case"default":case"auto":case"none":return"normal";default:return null}}function Jt(t,e,r){let n={...t},o=Pi(e.figure_style??r.figure_style);return o&&(n.fontVariantNumeric=o),e.font&&(n.fontFamily=e.font),n}function Kn(t){if(!t.length)return"";let e=[],r=t[0],n=t[0];for(let o=1;o<=t.length;o++){let s=t[o];if(s===n+1){n=s;continue}e.push(r===n?String(r):`${r}\u2013${n}`),r=s,n=s}return e.join(", ")}function ge(t){let e=t.type==="number"?"right":"left";return{textAlign:t.align||(t.viz==="chip"?"center":e)}}var so=Ti(Yn(),1);var Zn="0123456789-",Jn="\u2070\xB9\xB2\xB3\u2074\u2075\u2076\u2077\u2078\u2079\u207B";function Xn(t){let e=/^(-?\d+(?:\.\d+)?)E([+-]?\d+)$/.exec(t);if(!e)return t;let r=String(Number(e[2])).replace(/[\d-]/g,n=>Jn[Zn.indexOf(n)]);return`${e[1]} \xD7 10${r}`}function Qn(t){return[...t.matchAll(/(-?\d+(?:\.\d+)?) × 10(⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g)].map(e=>({index:e.index,length:e[0].length,mantissa:e[1],exponent:e[2].replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]/g,r=>Zn[Jn.indexOf(r)])}))}var io={usd:"$",eur:"\u20AC",gbp:"\xA3",aud:'"A$"',cad:'"C$"',cny:'"\xA5"',jpy:'"\xA5"',inr:'"\u20B9"',krw:'"\u20A9"',ngn:'"\u20A6"',sek:'"kr"'};function ao(t){return io[t]?.replaceAll('"',"")??null}var to=["num","usd","eur","gbp","aud","cad","cny","jpy","inr","krw","ngn","sek","pct"],eo={k:',"k"',m:',,"M"',b:',,,"B"',t:',,,,"T"'},Le=["0","0.0","0.00","0.000","0.0000"],Yr=new Map([["compact",new Intl.NumberFormat("en",{notation:"compact",minimumFractionDigits:1,maximumFractionDigits:1})]]);function Ri(t){if(Yr.has(t))return Yr.get(t);let e=/^compact([1-9]|1\d|2[01])$/.exec(t);if(!e)return null;let r=new Intl.NumberFormat("en",{notation:"compact",minimumSignificantDigits:1,maximumSignificantDigits:Number(e[1])});return Yr.set(t,r),r}function Di(){let t={id:"0",fract:"# ?/?",sci:"0.00E+0",mult:'#,##0.0"x"',mult0:'#,##0"x"',mult1:'#,##0.0"x"',mult2:'#,##0.00"x"',date:"yyyy-mm-dd",datetime:"yyyy-mm-dd HH:MM:SS",ddd:"ddd",dddd:"dddd",mmm:"mmm",mmmm:"mmmm","mmm-yy":"mmm-yy",yyyy:"yyyy",quarter:"quarter",qq:"qq",shortdate:"mmm d/yy",longdate:"mmmm d, yyyy",fulldate:"dddd mmmm d, yyyy",mdy:"m/d/y",dmy:"d/m/y",hms:"H:MM:SS AM/PM"};for(let e=0;e<=4;e++)t[`num${e}`]=`#,##${Le[e]}`;for(let e=0;e<=3;e++)t[`pct${e}`]=`#,##${Le[e]}%`;for(let[e,r]of Object.entries(eo))for(let n=0;n<=2;n++)t[`num${n}${e}`]=`#,##${Le[n]}${r}`;for(let[e,r]of Object.entries(io)){for(let n=0;n<=2;n++)t[`${e}${n}`]=`${r}#,##${Le[n]}`;t[`${e}0k`]=`${r}#,##0,"k"`,t[`${e}1k`]=`${r}#,##0.0,"k"`,t[`${e}2k`]=`${r}#,##0.00,"k"`;for(let[n,o]of Object.entries(eo))for(let s=0;s<=2;s++)t[`${e}${s}${n}`]=`${r}#,##${Le[s]}${o}`}return t}var Ke=Di(),Bi=new Set(["date","ddd","dddd","mmm","mmmm","mmm-yy","yyyy","quarter","qq","shortdate","longdate","fulldate","mdy","dmy","hms"]);function qe(t){return t?Bi.has(t.toLowerCase())?!0:/\b(yyyy|yy|mmmm|mmm|dd|ddd|dddd|hh|ss|AM|PM)\b/i.test(t):!1}function zi(t,e){let r="0",n="";if(e&&e.max!=null&&isFinite(e.max)){let o=Math.abs(e.max);t==="pct"?o<.1?r="2":o<1&&(r="1"):o<10?r="2":o<100&&(r="1"),t!=="pct"&&(o>=1e12?(n="t",r="1"):o>=1e9?(n="b",r="1"):o>=1e6?(n="m",r="1"):o>=4e3&&(n="k",r="0"))}return t+r+n}function Ue(t){if(typeof t!="string")return t;let e=t.split(" "),r=t;return r.includes(":")||(r=r+"T00:00:00"),e.length>2&&(r=e[0]+" "+e[1]),r=r.replace(/\.([^\s]+)/,""),r=r.replace("Z",""),r=r.replace(/[+-]\d{2}:?\d{2}$/,""),r=r.replace(" ","T"),r}function be(t){if(t instanceof Date)return Number.isNaN(t.getTime())?null:t;if(typeof t=="number"){if(Math.abs(t)>=1e11){let e=new Date(t);if(!Number.isNaN(e.getTime()))return new Date(e.getUTCFullYear(),e.getUTCMonth(),e.getUTCDate(),e.getUTCHours(),e.getUTCMinutes(),e.getUTCSeconds())}return null}return typeof t=="string"&&!Number.isNaN(Date.parse(Ue(t)))?new Date(Ue(t)):null}function Ii(t,e,r="sunday"){let n=Ke[e]||e,o=typeof t=="number"?t:typeof t=="string"&&!Number.isNaN(Number(t))?Number(t):null;if(o===null||!e)return t;if(e==="ddd"||e==="dddd"||n==="ddd"||n==="dddd"){if(o>=1&&o<=7){let s=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],i=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],a=r==="sunday"?o-1:o===7?0:o;return e==="ddd"||n==="ddd"?s[a]:i[a]}return be(o)||t}return e==="mmm"||e==="mmmm"||n.includes("mmm")?o>=1&&o<=12?new Date(2024,o-1,1):be(o)||t:e==="yyyy"||n.includes("yyyy")?o>=1900&&o<=2100?new Date(o,0,1):be(o)||t:t}function ro(t,e=!1){let r=t instanceof Date?t:be(t);if(!r)return null;let n=Math.floor(r.getMonth()/3)+1;return e?`Q${n}`:`${r.getFullYear()}-Q${n}`}var Fi=["year","month","week","day","hour","minute","second"],lo={year:365.25*24*60*60*1e3,month:365.25/12*24*60*60*1e3,week:10080*60*1e3,day:1440*60*1e3,hour:3600*1e3,minute:60*1e3,second:1e3};function ji(t){for(let e of Fi)if(t>=lo[e])return e;return"second"}function Gi(t){if(t instanceof Date)return t.getTime();if(typeof t=="number")return t;let e=String(t),r=Date.parse(e);return Number.isNaN(r)?Date.parse(Ue(e)):r}function Hi(t,e,r=Date.now()){let n=Gi(t);if(!Number.isFinite(n))return null;let o=e===!0||e==="auto"?ji(Math.abs(n-r)):String(e),s=lo[o];if(!s)return null;let i=Math.round((n-r)/s);return new Intl.RelativeTimeFormat(void 0,{numeric:"auto"}).format(i,o)}function pt(t,e,r={}){let{range:n,type:o,fallback:s,firstDayOfWeek:i="sunday"}=r,a=s??(t==null?"\u2013":String(t));if(t==null)return a;if(t==="Total")return"Total";if(r.relative){let c=Hi(t,r.relative,r.now);if(c!=null)return c}let l=e;if(l||(o&&/date|time/i.test(o)?l="date":(typeof t=="number"||typeof t=="string"&&t.trim()!==""&&!Number.isNaN(Number(t)))&&(l="num")),!l)return typeof t=="object"?JSON.stringify(t):a;if(l==="bytes")return Vi(Number(t));if(l==="duration")return qi(Number(t));if(l==="roman")return Ki(Number(t));if(l==="flag")return Yi(String(t));try{let c=Ii(t,l,i);if(typeof c=="string"&&(o&&/date|time/i.test(o)?c=be(c)||c:o&&/int|decimal|float|double|number/i.test(o)||!Number.isNaN(Number(c))&&!qe(l)?c=Number(c):!Number.isNaN(Date.parse(Ue(c)))&&qe(l)&&(c=be(c)||c)),typeof c=="number"&&!Number.isFinite(c))return a;if(l.startsWith("compact")){let p=Ri(l);return p&&typeof c=="number"?c===0?"0":p.format(c):a}let f=l;if((c===0||c==="0")&&l.length===3&&to.includes(l))f=`${l}0`;else if(l.length===3&&to.includes(l)){let p=n;!p&&typeof c=="number"&&(p={min:c,max:c}),f=zi(l,p)}if(f==="quarter")return ro(c)??a;if(f==="qq")return ro(c,!0)??a;if(f=Ke[f]||f,f=f.replace(/'/g,'"'),typeof c=="number"&&f.includes('"Q"')&&(c<1||c>4))return"";let u=so.default.format(f,c,{date1970:!0});return(u==null||u==="")&&(u=a),l==="sci"?Xn(u):u}catch{return typeof t=="object"?JSON.stringify(t):a}}var no=["B","KB","MB","GB","TB","PB"];function Vi(t){if(!isFinite(t))return String(t);let e=Math.abs(t),r=0;for(;e>=1024&&r<no.length-1;)e/=1024,r+=1;let n=t<0?"-":"",o=e>=100||r===0?0:e>=10?1:2;return`${n}${e.toFixed(o)} ${no[r]}`}function qi(t){if(!isFinite(t))return String(t);let e=t<0?"-":"",r=Math.round(Math.abs(t)),n=Math.floor(r/86400);r%=86400;let o=Math.floor(r/3600);r%=3600;let s=Math.floor(r/60);r%=60;let i=[];return n&&i.push(`${n}d`),o&&i.push(`${o}h`),s&&i.push(`${s}m`),(r||i.length===0)&&i.push(`${r}s`),e+i.join(" ")}var Ui=[[1e3,"M"],[900,"CM"],[500,"D"],[400,"CD"],[100,"C"],[90,"XC"],[50,"L"],[40,"XL"],[10,"X"],[9,"IX"],[5,"V"],[4,"IV"],[1,"I"]];function Ki(t){if(!Number.isInteger(t)||t<=0||t>=4e3)return String(t);let e=t,r="";for(let[n,o]of Ui)for(;e>=n;)r+=o,e-=n;return r}var Wi={ABW:"AW",AFG:"AF",AGO:"AO",AIA:"AI",ALA:"AX",ALB:"AL",AND:"AD",ARE:"AE",ARG:"AR",ARM:"AM",ASM:"AS",ATA:"AQ",ATF:"TF",ATG:"AG",AUS:"AU",AUT:"AT",AZE:"AZ",BDI:"BI",BEL:"BE",BEN:"BJ",BES:"BQ",BFA:"BF",BGD:"BD",BGR:"BG",BHR:"BH",BHS:"BS",BIH:"BA",BLM:"BL",BLR:"BY",BLZ:"BZ",BMU:"BM",BOL:"BO",BRA:"BR",BRB:"BB",BRN:"BN",BTN:"BT",BVT:"BV",BWA:"BW",CAF:"CF",CAN:"CA",CCK:"CC",CHE:"CH",CHL:"CL",CHN:"CN",CIV:"CI",CMR:"CM",COD:"CD",COG:"CG",COK:"CK",COL:"CO",COM:"KM",CPV:"CV",CRI:"CR",CUB:"CU",CUW:"CW",CXR:"CX",CYM:"KY",CYP:"CY",CZE:"CZ",DEU:"DE",DJI:"DJ",DMA:"DM",DNK:"DK",DOM:"DO",DZA:"DZ",ECU:"EC",EGY:"EG",ERI:"ER",ESH:"EH",ESP:"ES",EST:"EE",ETH:"ET",FIN:"FI",FJI:"FJ",FLK:"FK",FRA:"FR",FRO:"FO",FSM:"FM",GAB:"GA",GBR:"GB",GEO:"GE",GGY:"GG",GHA:"GH",GIB:"GI",GIN:"GN",GLP:"GP",GMB:"GM",GNB:"GW",GNQ:"GQ",GRC:"GR",GRD:"GD",GRL:"GL",GTM:"GT",GUF:"GF",GUM:"GU",GUY:"GY",HKG:"HK",HMD:"HM",HND:"HN",HRV:"HR",HTI:"HT",HUN:"HU",IDN:"ID",IMN:"IM",IND:"IN",IOT:"IO",IRL:"IE",IRN:"IR",IRQ:"IQ",ISL:"IS",ISR:"IL",ITA:"IT",JAM:"JM",JEY:"JE",JOR:"JO",JPN:"JP",KAZ:"KZ",KEN:"KE",KGZ:"KG",KHM:"KH",KIR:"KI",KNA:"KN",KOR:"KR",KWT:"KW",LAO:"LA",LBN:"LB",LBR:"LR",LBY:"LY",LCA:"LC",LIE:"LI",LKA:"LK",LSO:"LS",LTU:"LT",LUX:"LU",LVA:"LV",MAC:"MO",MAF:"MF",MAR:"MA",MCO:"MC",MDA:"MD",MDG:"MG",MDV:"MV",MEX:"MX",MHL:"MH",MKD:"MK",MLI:"ML",MLT:"MT",MMR:"MM",MNE:"ME",MNG:"MN",MNP:"MP",MOZ:"MZ",MRT:"MR",MSR:"MS",MTQ:"MQ",MUS:"MU",MWI:"MW",MYS:"MY",MYT:"YT",NAM:"NA",NCL:"NC",NER:"NE",NFK:"NF",NGA:"NG",NIC:"NI",NIU:"NU",NLD:"NL",NOR:"NO",NPL:"NP",NRU:"NR",NZL:"NZ",OMN:"OM",PAK:"PK",PAN:"PA",PCN:"PN",PER:"PE",PHL:"PH",PLW:"PW",PNG:"PG",POL:"PL",PRI:"PR",PRK:"KP",PRT:"PT",PRY:"PY",PSE:"PS",PYF:"PF",QAT:"QA",REU:"RE",ROU:"RO",RUS:"RU",RWA:"RW",SAU:"SA",SDN:"SD",SEN:"SN",SGP:"SG",SGS:"GS",SHN:"SH",SJM:"SJ",SLB:"SB",SLE:"SL",SLV:"SV",SMR:"SM",SOM:"SO",SPM:"PM",SRB:"RS",SSD:"SS",STP:"ST",SUR:"SR",SVK:"SK",SVN:"SI",SWE:"SE",SWZ:"SZ",SXM:"SX",SYC:"SC",SYR:"SY",TCA:"TC",TCD:"TD",TGO:"TG",THA:"TH",TJK:"TJ",TKL:"TK",TKM:"TM",TLS:"TL",TON:"TO",TTO:"TT",TUN:"TN",TUR:"TR",TUV:"TV",TWN:"TW",TZA:"TZ",UGA:"UG",UKR:"UA",UMI:"UM",URY:"UY",USA:"US",UZB:"UZ",VAT:"VA",VCT:"VC",VEN:"VE",VGB:"VG",VIR:"VI",VNM:"VN",VUT:"VU",WLF:"WF",WSM:"WS",YEM:"YE",ZAF:"ZA",ZMB:"ZM",ZWE:"ZW"};function oo(t){return String.fromCodePoint(...[...t].map(e=>127462+e.charCodeAt(0)-65))}function Yi(t){let e=String(t).trim().toUpperCase();if(/^[A-Z]{3}$/.test(e)){let r=Wi[e];return r?oo(r):t}return/^[A-Z]{2}$/.test(e)?oo(e):t}function Ft(t){if(t==null)return"";let e=String(t);return(e.includes(".")?e.slice(e.lastIndexOf(".")+1):e).replace(/_/g," ").replace(/\b\w/g,n=>n.toUpperCase())}function Mt(t){let e=String(t??"");if(!e.includes(" \xD7 10"))return e;let r=Qn(e);if(!r.length)return e;let n=document.createDocumentFragment(),o=0;for(let s of r){n.append(document.createTextNode(e.slice(o,s.index)));let i=document.createElement("span");i.className="et-scientific",i.setAttribute("role","math"),i.setAttribute("aria-label",`${s.mantissa} times 10 to the power of ${s.exponent}`),i.append(document.createTextNode(`${s.mantissa} \xD7 10`));let a=document.createElement("sup");a.className="et-scientific-exponent",a.textContent=s.exponent,i.append(a),n.append(i),o=s.index+s.length}return n.append(document.createTextNode(e.slice(o))),n}var Vt=(t,e=0,r=1)=>ye(_e(e,t),r);var le=t=>{t._clipped=!1,t._unclipped=t.slice(0);for(let e=0;e<=3;e++)e<3?((t[e]<0||t[e]>255)&&(t._clipped=!0),t[e]=Vt(t[e],0,255)):e===3&&(t[e]=Vt(t[e],0,1));return t};var co={};for(let t of["Boolean","Number","String","Function","Array","Date","RegExp","Undefined","Null"])co[`[object ${t}]`]=t.toLowerCase();function V(t){return co[Object.prototype.toString.call(t)]||"object"}var F=(t,e=null)=>t.length>=3?Array.prototype.slice.call(t):V(t[0])=="object"&&e?e.split("").filter(r=>t[0][r]!==void 0).map(r=>t[0][r]):t[0];var Kt=t=>{if(t.length<2)return null;let e=t.length-1;return V(t[e])=="string"?t[e].toLowerCase():null};var{PI:We,min:ye,max:_e}=Math,Rt=We*2,Ye=We/3,fo=We/180,uo=180/We;var q={format:{},autodetect:[]};var Zr=class{constructor(...e){let r=this;if(V(e[0])==="object"&&e[0].constructor&&e[0].constructor===this.constructor)return e[0];let n=Kt(e),o=!1;if(!n){o=!0,q.sorted||(q.autodetect=q.autodetect.sort((s,i)=>i.p-s.p),q.sorted=!0);for(let s of q.autodetect)if(n=s.test(...e),n)break}if(q.format[n]){let s=q.format[n].apply(null,o?e:e.slice(0,-1));r._rgb=le(s)}else throw new Error("unknown format: "+e);r._rgb.length===3&&r._rgb.push(1)}toString(){return V(this.hex)=="function"?this.hex():`[${this._rgb.join(",")}]`}},$=Zr;var po="2.6.0";var Ze=(...t)=>new Ze.Color(...t);Ze.Color=$;Ze.version=po;var K=Ze;var Zi=(...t)=>{t=F(t,"cmyk");let[e,r,n,o]=t,s=t.length>4?t[4]:1;return o===1?[0,0,0,s]:[e>=1?0:255*(1-e)*(1-o),r>=1?0:255*(1-r)*(1-o),n>=1?0:255*(1-n)*(1-o),s]},ho=Zi;var{max:mo}=Math,Ji=(...t)=>{let[e,r,n]=F(t,"rgb");e=e/255,r=r/255,n=n/255;let o=1-mo(e,mo(r,n)),s=o<1?1/(1-o):0,i=(1-e-o)*s,a=(1-r-o)*s,l=(1-n-o)*s;return[i,a,l,o]},go=Ji;$.prototype.cmyk=function(){return go(this._rgb)};K.cmyk=(...t)=>new $(...t,"cmyk");q.format.cmyk=ho;q.autodetect.push({p:2,test:(...t)=>{if(t=F(t,"cmyk"),V(t)==="array"&&t.length===4)return"cmyk"}});var Jr=t=>Math.round(t*100)/100,Xi=(...t)=>{let e=F(t,"hsla"),r=Kt(t)||"lsa";return e[0]=Jr(e[0]||0),e[1]=Jr(e[1]*100)+"%",e[2]=Jr(e[2]*100)+"%",r==="hsla"||e.length>3&&e[3]<1?(e[3]=e.length>3?e[3]:1,r="hsla"):e.length=3,`${r}(${e.join(",")})`},bo=Xi;var Qi=(...t)=>{t=F(t,"rgba");let[e,r,n]=t;e/=255,r/=255,n/=255;let o=ye(e,r,n),s=_e(e,r,n),i=(s+o)/2,a,l;return s===o?(a=0,l=Number.NaN):a=i<.5?(s-o)/(s+o):(s-o)/(2-s-o),e==s?l=(r-n)/(s-o):r==s?l=2+(n-e)/(s-o):n==s&&(l=4+(e-r)/(s-o)),l*=60,l<0&&(l+=360),t.length>3&&t[3]!==void 0?[l,a,i,t[3]]:[l,a,i]},Je=Qi;var{round:Xr}=Math,ta=(...t)=>{let e=F(t,"rgba"),r=Kt(t)||"rgb";return r.substr(0,3)=="hsl"?bo(Je(e),r):(e[0]=Xr(e[0]),e[1]=Xr(e[1]),e[2]=Xr(e[2]),(r==="rgba"||e.length>3&&e[3]<1)&&(e[3]=e.length>3?e[3]:1,r="rgba"),`${r}(${e.slice(0,r==="rgb"?3:4).join(",")})`)},yo=ta;var{round:Qr}=Math,ea=(...t)=>{t=F(t,"hsl");let[e,r,n]=t,o,s,i;if(r===0)o=s=i=n*255;else{let a=[0,0,0],l=[0,0,0],c=n<.5?n*(1+r):n+r-n*r,f=2*n-c,u=e/360;a[0]=u+1/3,a[1]=u,a[2]=u-1/3;for(let p=0;p<3;p++)a[p]<0&&(a[p]+=1),a[p]>1&&(a[p]-=1),6*a[p]<1?l[p]=f+(c-f)*6*a[p]:2*a[p]<1?l[p]=c:3*a[p]<2?l[p]=f+(c-f)*(2/3-a[p])*6:l[p]=f;[o,s,i]=[Qr(l[0]*255),Qr(l[1]*255),Qr(l[2]*255)]}return t.length>3?[o,s,i,t[3]]:[o,s,i,1]},Te=ea;var xo=/^rgb\(\s*(-?\d+),\s*(-?\d+)\s*,\s*(-?\d+)\s*\)$/,ko=/^rgba\(\s*(-?\d+),\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*([01]|[01]?\.\d+)\)$/,wo=/^rgb\(\s*(-?\d+(?:\.\d+)?)%,\s*(-?\d+(?:\.\d+)?)%\s*,\s*(-?\d+(?:\.\d+)?)%\s*\)$/,Mo=/^rgba\(\s*(-?\d+(?:\.\d+)?)%,\s*(-?\d+(?:\.\d+)?)%\s*,\s*(-?\d+(?:\.\d+)?)%\s*,\s*([01]|[01]?\.\d+)\)$/,So=/^hsl\(\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)%\s*,\s*(-?\d+(?:\.\d+)?)%\s*\)$/,vo=/^hsla\(\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)%\s*,\s*(-?\d+(?:\.\d+)?)%\s*,\s*([01]|[01]?\.\d+)\)$/,{round:_o}=Math,Co=t=>{t=t.toLowerCase().trim();let e;if(q.format.named)try{return q.format.named(t)}catch{}if(e=t.match(xo)){let r=e.slice(1,4);for(let n=0;n<3;n++)r[n]=+r[n];return r[3]=1,r}if(e=t.match(ko)){let r=e.slice(1,5);for(let n=0;n<4;n++)r[n]=+r[n];return r}if(e=t.match(wo)){let r=e.slice(1,4);for(let n=0;n<3;n++)r[n]=_o(r[n]*2.55);return r[3]=1,r}if(e=t.match(Mo)){let r=e.slice(1,5);for(let n=0;n<3;n++)r[n]=_o(r[n]*2.55);return r[3]=+r[3],r}if(e=t.match(So)){let r=e.slice(1,4);r[1]*=.01,r[2]*=.01;let n=Te(r);return n[3]=1,n}if(e=t.match(vo)){let r=e.slice(1,4);r[1]*=.01,r[2]*=.01;let n=Te(r);return n[3]=+e[4],n}};Co.test=t=>xo.test(t)||ko.test(t)||wo.test(t)||Mo.test(t)||So.test(t)||vo.test(t);var tn=Co;$.prototype.css=function(t){return yo(this._rgb,t)};K.css=(...t)=>new $(...t,"css");q.format.css=tn;q.autodetect.push({p:5,test:(t,...e)=>{if(!e.length&&V(t)==="string"&&tn.test(t))return"css"}});q.format.gl=(...t)=>{let e=F(t,"rgba");return e[0]*=255,e[1]*=255,e[2]*=255,e};K.gl=(...t)=>new $(...t,"gl");$.prototype.gl=function(){let t=this._rgb;return[t[0]/255,t[1]/255,t[2]/255,t[3]]};var{floor:ra}=Math,na=(...t)=>{t=F(t,"hcg");let[e,r,n]=t,o,s,i;n=n*255;let a=r*255;if(r===0)o=s=i=n;else{e===360&&(e=0),e>360&&(e-=360),e<0&&(e+=360),e/=60;let l=ra(e),c=e-l,f=n*(1-r),u=f+a*(1-c),p=f+a*c,d=f+a;switch(l){case 0:[o,s,i]=[d,p,f];break;case 1:[o,s,i]=[u,d,f];break;case 2:[o,s,i]=[f,d,p];break;case 3:[o,s,i]=[f,u,d];break;case 4:[o,s,i]=[p,f,d];break;case 5:[o,s,i]=[d,f,u];break}}return[o,s,i,t.length>3?t[3]:1]},Ao=na;var oa=(...t)=>{let[e,r,n]=F(t,"rgb"),o=ye(e,r,n),s=_e(e,r,n),i=s-o,a=i*100/255,l=o/(255-i)*100,c;return i===0?c=Number.NaN:(e===s&&(c=(r-n)/i),r===s&&(c=2+(n-e)/i),n===s&&(c=4+(e-r)/i),c*=60,c<0&&(c+=360)),[c,a,l]},$o=oa;$.prototype.hcg=function(){return $o(this._rgb)};K.hcg=(...t)=>new $(...t,"hcg");q.format.hcg=Ao;q.autodetect.push({p:1,test:(...t)=>{if(t=F(t,"hcg"),V(t)==="array"&&t.length===3)return"hcg"}});var sa=/^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/,ia=/^#?([A-Fa-f0-9]{8}|[A-Fa-f0-9]{4})$/,aa=t=>{if(t.match(sa)){(t.length===4||t.length===7)&&(t=t.substr(1)),t.length===3&&(t=t.split(""),t=t[0]+t[0]+t[1]+t[1]+t[2]+t[2]);let e=parseInt(t,16),r=e>>16,n=e>>8&255,o=e&255;return[r,n,o,1]}if(t.match(ia)){(t.length===5||t.length===9)&&(t=t.substr(1)),t.length===4&&(t=t.split(""),t=t[0]+t[0]+t[1]+t[1]+t[2]+t[2]+t[3]+t[3]);let e=parseInt(t,16),r=e>>24&255,n=e>>16&255,o=e>>8&255,s=Math.round((e&255)/255*100)/100;return[r,n,o,s]}throw new Error(`unknown hex color: ${t}`)},Xe=aa;var{round:Qe}=Math,la=(...t)=>{let[e,r,n,o]=F(t,"rgba"),s=Kt(t)||"auto";o===void 0&&(o=1),s==="auto"&&(s=o<1?"rgba":"rgb"),e=Qe(e),r=Qe(r),n=Qe(n);let a="000000"+(e<<16|r<<8|n).toString(16);a=a.substr(a.length-6);let l="0"+Qe(o*255).toString(16);switch(l=l.substr(l.length-2),s.toLowerCase()){case"rgba":return`#${a}${l}`;case"argb":return`#${l}${a}`;default:return`#${a}`}},tr=la;$.prototype.hex=function(t){return tr(this._rgb,t)};K.hex=(...t)=>new $(...t,"hex");q.format.hex=Xe;q.autodetect.push({p:4,test:(t,...e)=>{if(!e.length&&V(t)==="string"&&[3,4,5,6,7,8,9].indexOf(t.length)>=0)return"hex"}});var{cos:xe}=Math,ca=(...t)=>{t=F(t,"hsi");let[e,r,n]=t,o,s,i;return isNaN(e)&&(e=0),isNaN(r)&&(r=0),e>360&&(e-=360),e<0&&(e+=360),e/=360,e<1/3?(i=(1-r)/3,o=(1+r*xe(Rt*e)/xe(Ye-Rt*e))/3,s=1-(i+o)):e<2/3?(e-=1/3,o=(1-r)/3,s=(1+r*xe(Rt*e)/xe(Ye-Rt*e))/3,i=1-(o+s)):(e-=2/3,s=(1-r)/3,i=(1+r*xe(Rt*e)/xe(Ye-Rt*e))/3,o=1-(s+i)),o=Vt(n*o*3),s=Vt(n*s*3),i=Vt(n*i*3),[o*255,s*255,i*255,t.length>3?t[3]:1]},No=ca;var{min:fa,sqrt:ua,acos:da}=Math,pa=(...t)=>{let[e,r,n]=F(t,"rgb");e/=255,r/=255,n/=255;let o,s=fa(e,r,n),i=(e+r+n)/3,a=i>0?1-s/i:0;return a===0?o=NaN:(o=(e-r+(e-n))/2,o/=ua((e-r)*(e-r)+(e-n)*(r-n)),o=da(o),n>r&&(o=Rt-o),o/=Rt),[o*360,a,i]},Eo=pa;$.prototype.hsi=function(){return Eo(this._rgb)};K.hsi=(...t)=>new $(...t,"hsi");q.format.hsi=No;q.autodetect.push({p:2,test:(...t)=>{if(t=F(t,"hsi"),V(t)==="array"&&t.length===3)return"hsi"}});$.prototype.hsl=function(){return Je(this._rgb)};K.hsl=(...t)=>new $(...t,"hsl");q.format.hsl=Te;q.autodetect.push({p:2,test:(...t)=>{if(t=F(t,"hsl"),V(t)==="array"&&t.length===3)return"hsl"}});var{floor:ha}=Math,ma=(...t)=>{t=F(t,"hsv");let[e,r,n]=t,o,s,i;if(n*=255,r===0)o=s=i=n;else{e===360&&(e=0),e>360&&(e-=360),e<0&&(e+=360),e/=60;let a=ha(e),l=e-a,c=n*(1-r),f=n*(1-r*l),u=n*(1-r*(1-l));switch(a){case 0:[o,s,i]=[n,u,c];break;case 1:[o,s,i]=[f,n,c];break;case 2:[o,s,i]=[c,n,u];break;case 3:[o,s,i]=[c,f,n];break;case 4:[o,s,i]=[u,c,n];break;case 5:[o,s,i]=[n,c,f];break}}return[o,s,i,t.length>3?t[3]:1]},Lo=ma;var{min:ga,max:ba}=Math,ya=(...t)=>{t=F(t,"rgb");let[e,r,n]=t,o=ga(e,r,n),s=ba(e,r,n),i=s-o,a,l,c;return c=s/255,s===0?(a=Number.NaN,l=0):(l=i/s,e===s&&(a=(r-n)/i),r===s&&(a=2+(n-e)/i),n===s&&(a=4+(e-r)/i),a*=60,a<0&&(a+=360)),[a,l,c]},To=ya;$.prototype.hsv=function(){return To(this._rgb)};K.hsv=(...t)=>new $(...t,"hsv");q.format.hsv=Lo;q.autodetect.push({p:2,test:(...t)=>{if(t=F(t,"hsv"),V(t)==="array"&&t.length===3)return"hsv"}});var St={Kn:18,Xn:.95047,Yn:1,Zn:1.08883,t0:.137931034,t1:.206896552,t2:.12841855,t3:.008856452};var{pow:_a}=Math,xa=(...t)=>{t=F(t,"lab");let[e,r,n]=t,o,s,i,a,l,c;return s=(e+16)/116,o=isNaN(r)?s:s+r/500,i=isNaN(n)?s:s-n/200,s=St.Yn*rn(s),o=St.Xn*rn(o),i=St.Zn*rn(i),a=en(3.2404542*o-1.5371385*s-.4985314*i),l=en(-.969266*o+1.8760108*s+.041556*i),c=en(.0556434*o-.2040259*s+1.0572252*i),[a,l,c,t.length>3?t[3]:1]},en=t=>255*(t<=.00304?12.92*t:1.055*_a(t,1/2.4)-.055),rn=t=>t>St.t1?t*t*t:St.t2*(t-St.t0),er=xa;var{pow:Po}=Math,ka=(...t)=>{let[e,r,n]=F(t,"rgb"),[o,s,i]=wa(e,r,n),a=116*s-16;return[a<0?0:a,500*(o-s),200*(s-i)]},nn=t=>(t/=255)<=.04045?t/12.92:Po((t+.055)/1.055,2.4),on=t=>t>St.t3?Po(t,1/3):t/St.t2+St.t0,wa=(t,e,r)=>{t=nn(t),e=nn(e),r=nn(r);let n=on((.4124564*t+.3575761*e+.1804375*r)/St.Xn),o=on((.2126729*t+.7151522*e+.072175*r)/St.Yn),s=on((.0193339*t+.119192*e+.9503041*r)/St.Zn);return[n,o,s]},rr=ka;$.prototype.lab=function(){return rr(this._rgb)};K.lab=(...t)=>new $(...t,"lab");q.format.lab=er;q.autodetect.push({p:2,test:(...t)=>{if(t=F(t,"lab"),V(t)==="array"&&t.length===3)return"lab"}});var{sin:Ma,cos:Sa}=Math,va=(...t)=>{let[e,r,n]=F(t,"lch");return isNaN(n)&&(n=0),n=n*fo,[e,Sa(n)*r,Ma(n)*r]},nr=va;var Ca=(...t)=>{t=F(t,"lch");let[e,r,n]=t,[o,s,i]=nr(e,r,n),[a,l,c]=er(o,s,i);return[a,l,c,t.length>3?t[3]:1]},or=Ca;var Aa=(...t)=>{let e=F(t,"hcl").reverse();return or(...e)},Oo=Aa;var{sqrt:$a,atan2:Na,round:Ea}=Math,La=(...t)=>{let[e,r,n]=F(t,"lab"),o=$a(r*r+n*n),s=(Na(n,r)*uo+360)%360;return Ea(o*1e4)===0&&(s=Number.NaN),[e,o,s]},sr=La;var Ta=(...t)=>{let[e,r,n]=F(t,"rgb"),[o,s,i]=rr(e,r,n);return sr(o,s,i)},sn=Ta;$.prototype.lch=function(){return sn(this._rgb)};$.prototype.hcl=function(){return sn(this._rgb).reverse()};K.lch=(...t)=>new $(...t,"lch");K.hcl=(...t)=>new $(...t,"hcl");q.format.lch=or;q.format.hcl=Oo;["lch","hcl"].forEach(t=>q.autodetect.push({p:2,test:(...e)=>{if(e=F(e,t),V(e)==="array"&&e.length===3)return t}}));var Pa={aliceblue:"#f0f8ff",antiquewhite:"#faebd7",aqua:"#00ffff",aquamarine:"#7fffd4",azure:"#f0ffff",beige:"#f5f5dc",bisque:"#ffe4c4",black:"#000000",blanchedalmond:"#ffebcd",blue:"#0000ff",blueviolet:"#8a2be2",brown:"#a52a2a",burlywood:"#deb887",cadetblue:"#5f9ea0",chartreuse:"#7fff00",chocolate:"#d2691e",coral:"#ff7f50",cornflowerblue:"#6495ed",cornsilk:"#fff8dc",crimson:"#dc143c",cyan:"#00ffff",darkblue:"#00008b",darkcyan:"#008b8b",darkgoldenrod:"#b8860b",darkgray:"#a9a9a9",darkgreen:"#006400",darkgrey:"#a9a9a9",darkkhaki:"#bdb76b",darkmagenta:"#8b008b",darkolivegreen:"#556b2f",darkorange:"#ff8c00",darkorchid:"#9932cc",darkred:"#8b0000",darksalmon:"#e9967a",darkseagreen:"#8fbc8f",darkslateblue:"#483d8b",darkslategray:"#2f4f4f",darkslategrey:"#2f4f4f",darkturquoise:"#00ced1",darkviolet:"#9400d3",deeppink:"#ff1493",deepskyblue:"#00bfff",dimgray:"#696969",dimgrey:"#696969",dodgerblue:"#1e90ff",firebrick:"#b22222",floralwhite:"#fffaf0",forestgreen:"#228b22",fuchsia:"#ff00ff",gainsboro:"#dcdcdc",ghostwhite:"#f8f8ff",gold:"#ffd700",goldenrod:"#daa520",gray:"#808080",green:"#008000",greenyellow:"#adff2f",grey:"#808080",honeydew:"#f0fff0",hotpink:"#ff69b4",indianred:"#cd5c5c",indigo:"#4b0082",ivory:"#fffff0",khaki:"#f0e68c",laserlemon:"#ffff54",lavender:"#e6e6fa",lavenderblush:"#fff0f5",lawngreen:"#7cfc00",lemonchiffon:"#fffacd",lightblue:"#add8e6",lightcoral:"#f08080",lightcyan:"#e0ffff",lightgoldenrod:"#fafad2",lightgoldenrodyellow:"#fafad2",lightgray:"#d3d3d3",lightgreen:"#90ee90",lightgrey:"#d3d3d3",lightpink:"#ffb6c1",lightsalmon:"#ffa07a",lightseagreen:"#20b2aa",lightskyblue:"#87cefa",lightslategray:"#778899",lightslategrey:"#778899",lightsteelblue:"#b0c4de",lightyellow:"#ffffe0",lime:"#00ff00",limegreen:"#32cd32",linen:"#faf0e6",magenta:"#ff00ff",maroon:"#800000",maroon2:"#7f0000",maroon3:"#b03060",mediumaquamarine:"#66cdaa",mediumblue:"#0000cd",mediumorchid:"#ba55d3",mediumpurple:"#9370db",mediumseagreen:"#3cb371",mediumslateblue:"#7b68ee",mediumspringgreen:"#00fa9a",mediumturquoise:"#48d1cc",mediumvioletred:"#c71585",midnightblue:"#191970",mintcream:"#f5fffa",mistyrose:"#ffe4e1",moccasin:"#ffe4b5",navajowhite:"#ffdead",navy:"#000080",oldlace:"#fdf5e6",olive:"#808000",olivedrab:"#6b8e23",orange:"#ffa500",orangered:"#ff4500",orchid:"#da70d6",palegoldenrod:"#eee8aa",palegreen:"#98fb98",paleturquoise:"#afeeee",palevioletred:"#db7093",papayawhip:"#ffefd5",peachpuff:"#ffdab9",peru:"#cd853f",pink:"#ffc0cb",plum:"#dda0dd",powderblue:"#b0e0e6",purple:"#800080",purple2:"#7f007f",purple3:"#a020f0",rebeccapurple:"#663399",red:"#ff0000",rosybrown:"#bc8f8f",royalblue:"#4169e1",saddlebrown:"#8b4513",salmon:"#fa8072",sandybrown:"#f4a460",seagreen:"#2e8b57",seashell:"#fff5ee",sienna:"#a0522d",silver:"#c0c0c0",skyblue:"#87ceeb",slateblue:"#6a5acd",slategray:"#708090",slategrey:"#708090",snow:"#fffafa",springgreen:"#00ff7f",steelblue:"#4682b4",tan:"#d2b48c",teal:"#008080",thistle:"#d8bfd8",tomato:"#ff6347",turquoise:"#40e0d0",violet:"#ee82ee",wheat:"#f5deb3",white:"#ffffff",whitesmoke:"#f5f5f5",yellow:"#ffff00",yellowgreen:"#9acd32"},Xt=Pa;$.prototype.name=function(){let t=tr(this._rgb,"rgb");for(let e of Object.keys(Xt))if(Xt[e]===t)return e.toLowerCase();return t};q.format.named=t=>{if(t=t.toLowerCase(),Xt[t])return Xe(Xt[t]);throw new Error("unknown color name: "+t)};q.autodetect.push({p:5,test:(t,...e)=>{if(!e.length&&V(t)==="string"&&Xt[t.toLowerCase()])return"named"}});var Oa=t=>{if(V(t)=="number"&&t>=0&&t<=16777215){let e=t>>16,r=t>>8&255,n=t&255;return[e,r,n,1]}throw new Error("unknown num color: "+t)},Ro=Oa;var Ra=(...t)=>{let[e,r,n]=F(t,"rgb");return(e<<16)+(r<<8)+n},Do=Ra;$.prototype.num=function(){return Do(this._rgb)};K.num=(...t)=>new $(...t,"num");q.format.num=Ro;q.autodetect.push({p:5,test:(...t)=>{if(t.length===1&&V(t[0])==="number"&&t[0]>=0&&t[0]<=16777215)return"num"}});var{round:Bo}=Math;$.prototype.rgb=function(t=!0){return t===!1?this._rgb.slice(0,3):this._rgb.slice(0,3).map(Bo)};$.prototype.rgba=function(t=!0){return this._rgb.slice(0,4).map((e,r)=>r<3?t===!1?e:Bo(e):e)};K.rgb=(...t)=>new $(...t,"rgb");q.format.rgb=(...t)=>{let e=F(t,"rgba");return e[3]===void 0&&(e[3]=1),e};q.autodetect.push({p:3,test:(...t)=>{if(t=F(t,"rgba"),V(t)==="array"&&(t.length===3||t.length===4&&V(t[3])=="number"&&t[3]>=0&&t[3]<=1))return"rgb"}});var{log:ir}=Math,Da=t=>{let e=t/100,r,n,o;return e<66?(r=255,n=e<6?0:-155.25485562709179-.44596950469579133*(n=e-2)+104.49216199393888*ir(n),o=e<20?0:-254.76935184120902+.8274096064007395*(o=e-10)+115.67994401066147*ir(o)):(r=351.97690566805693+.114206453784165*(r=e-55)-40.25366309332127*ir(r),n=325.4494125711974+.07943456536662342*(n=e-50)-28.0852963507957*ir(n),o=255),[r,n,o,1]},ar=Da;var{round:Ba}=Math,za=(...t)=>{let e=F(t,"rgb"),r=e[0],n=e[2],o=1e3,s=4e4,i=.4,a;for(;s-o>i;){a=(s+o)*.5;let l=ar(a);l[2]/l[0]>=n/r?s=a:o=a}return Ba(a)},zo=za;$.prototype.temp=$.prototype.kelvin=$.prototype.temperature=function(){return zo(this._rgb)};K.temp=K.kelvin=K.temperature=(...t)=>new $(...t,"temp");q.format.temp=q.format.kelvin=q.format.temperature=ar;var{pow:lr,sign:Ia}=Math,Fa=(...t)=>{t=F(t,"lab");let[e,r,n]=t,o=lr(e+.3963377774*r+.2158037573*n,3),s=lr(e-.1055613458*r-.0638541728*n,3),i=lr(e-.0894841775*r-1.291485548*n,3);return[255*an(4.0767416621*o-3.3077115913*s+.2309699292*i),255*an(-1.2684380046*o+2.6097574011*s-.3413193965*i),255*an(-.0041960863*o-.7034186147*s+1.707614701*i),t.length>3?t[3]:1]},cr=Fa;function an(t){let e=Math.abs(t);return e>.0031308?(Ia(t)||1)*(1.055*lr(e,1/2.4)-.055):t*12.92}var{cbrt:ln,pow:ja,sign:Ga}=Math,Ha=(...t)=>{let[e,r,n]=F(t,"rgb"),[o,s,i]=[cn(e/255),cn(r/255),cn(n/255)],a=ln(.4122214708*o+.5363325363*s+.0514459929*i),l=ln(.2119034982*o+.6806995451*s+.1073969566*i),c=ln(.0883024619*o+.2817188376*s+.6299787005*i);return[.2104542553*a+.793617785*l-.0040720468*c,1.9779984951*a-2.428592205*l+.4505937099*c,.0259040371*a+.7827717662*l-.808675766*c]},fr=Ha;function cn(t){let e=Math.abs(t);return e<.04045?t/12.92:(Ga(t)||1)*ja((e+.055)/1.055,2.4)}$.prototype.oklab=function(){return fr(this._rgb)};K.oklab=(...t)=>new $(...t,"oklab");q.format.oklab=cr;q.autodetect.push({p:3,test:(...t)=>{if(t=F(t,"oklab"),V(t)==="array"&&t.length===3)return"oklab"}});var Va=(...t)=>{t=F(t,"lch");let[e,r,n]=t,[o,s,i]=nr(e,r,n),[a,l,c]=cr(o,s,i);return[a,l,c,t.length>3?t[3]:1]},Io=Va;var qa=(...t)=>{let[e,r,n]=F(t,"rgb"),[o,s,i]=fr(e,r,n);return sr(o,s,i)},Fo=qa;$.prototype.oklch=function(){return Fo(this._rgb)};K.oklch=(...t)=>new $(...t,"oklch");q.format.oklch=Io;q.autodetect.push({p:3,test:(...t)=>{if(t=F(t,"oklch"),V(t)==="array"&&t.length===3)return"oklch"}});$.prototype.alpha=function(t,e=!1){return t!==void 0&&V(t)==="number"?e?(this._rgb[3]=t,this):new $([this._rgb[0],this._rgb[1],this._rgb[2],t],"rgb"):this._rgb[3]};$.prototype.clipped=function(){return this._rgb._clipped||!1};$.prototype.darken=function(t=1){let e=this,r=e.lab();return r[0]-=St.Kn*t,new $(r,"lab").alpha(e.alpha(),!0)};$.prototype.brighten=function(t=1){return this.darken(-t)};$.prototype.darker=$.prototype.darken;$.prototype.brighter=$.prototype.brighten;$.prototype.get=function(t){let[e,r]=t.split("."),n=this[e]();if(r){let o=e.indexOf(r)-(e.substr(0,2)==="ok"?2:0);if(o>-1)return n[o];throw new Error(`unknown channel ${r} in mode ${e}`)}else return n};var{pow:Ua}=Math,Ka=1e-7,Wa=20;$.prototype.luminance=function(t,e="rgb"){if(t!==void 0&&V(t)==="number"){if(t===0)return new $([0,0,0,this._rgb[3]],"rgb");if(t===1)return new $([255,255,255,this._rgb[3]],"rgb");let r=this.luminance(),n=Wa,o=(i,a)=>{let l=i.interpolate(a,.5,e),c=l.luminance();return Math.abs(t-c)<Ka||!n--?l:c>t?o(i,l):o(l,a)},s=(r>t?o(new $([0,0,0]),this):o(this,new $([255,255,255]))).rgb();return new $([...s,this._rgb[3]])}return Ya(...this._rgb.slice(0,3))};var Ya=(t,e,r)=>(t=fn(t),e=fn(e),r=fn(r),.2126*t+.7152*e+.0722*r),fn=t=>(t/=255,t<=.03928?t/12.92:Ua((t+.055)/1.055,2.4));var lt={};var Qt=(t,e,r=.5,...n)=>{let o=n[0]||"lrgb";if(!lt[o]&&!n.length&&(o=Object.keys(lt)[0]),!lt[o])throw new Error(`interpolation mode ${o} is not defined`);return V(t)!=="object"&&(t=new $(t)),V(e)!=="object"&&(e=new $(e)),lt[o](t,e,r).alpha(t.alpha()+r*(e.alpha()-t.alpha()))};$.prototype.mix=$.prototype.interpolate=function(t,e=.5,...r){return Qt(this,t,e,...r)};$.prototype.premultiply=function(t=!1){let e=this._rgb,r=e[3];return t?(this._rgb=[e[0]*r,e[1]*r,e[2]*r,r],this):new $([e[0]*r,e[1]*r,e[2]*r,r],"rgb")};$.prototype.saturate=function(t=1){let e=this,r=e.lch();return r[1]+=St.Kn*t,r[1]<0&&(r[1]=0),new $(r,"lch").alpha(e.alpha(),!0)};$.prototype.desaturate=function(t=1){return this.saturate(-t)};$.prototype.set=function(t,e,r=!1){let[n,o]=t.split("."),s=this[n]();if(o){let i=n.indexOf(o)-(n.substr(0,2)==="ok"?2:0);if(i>-1){if(V(e)=="string")switch(e.charAt(0)){case"+":s[i]+=+e;break;case"-":s[i]+=+e;break;case"*":s[i]*=+e.substr(1);break;case"/":s[i]/=+e.substr(1);break;default:s[i]=+e}else if(V(e)==="number")s[i]=e;else throw new Error("unsupported value for Color.set");let a=new $(s,n);return r?(this._rgb=a._rgb,this):a}throw new Error(`unknown channel ${o} in mode ${n}`)}else return s};$.prototype.tint=function(t=.5,...e){return Qt(this,"white",t,...e)};$.prototype.shade=function(t=.5,...e){return Qt(this,"black",t,...e)};var Za=(t,e,r)=>{let n=t._rgb,o=e._rgb;return new $(n[0]+r*(o[0]-n[0]),n[1]+r*(o[1]-n[1]),n[2]+r*(o[2]-n[2]),"rgb")};lt.rgb=Za;var{sqrt:un,pow:ke}=Math,Ja=(t,e,r)=>{let[n,o,s]=t._rgb,[i,a,l]=e._rgb;return new $(un(ke(n,2)*(1-r)+ke(i,2)*r),un(ke(o,2)*(1-r)+ke(a,2)*r),un(ke(s,2)*(1-r)+ke(l,2)*r),"rgb")};lt.lrgb=Ja;var Xa=(t,e,r)=>{let n=t.lab(),o=e.lab();return new $(n[0]+r*(o[0]-n[0]),n[1]+r*(o[1]-n[1]),n[2]+r*(o[2]-n[2]),"lab")};lt.lab=Xa;var Dt=(t,e,r,n)=>{let o,s;n==="hsl"?(o=t.hsl(),s=e.hsl()):n==="hsv"?(o=t.hsv(),s=e.hsv()):n==="hcg"?(o=t.hcg(),s=e.hcg()):n==="hsi"?(o=t.hsi(),s=e.hsi()):n==="lch"||n==="hcl"?(n="hcl",o=t.hcl(),s=e.hcl()):n==="oklch"&&(o=t.oklch().reverse(),s=e.oklch().reverse());let i,a,l,c,f,u;(n.substr(0,1)==="h"||n==="oklch")&&([i,l,f]=o,[a,c,u]=s);let p,d,h,m;return!isNaN(i)&&!isNaN(a)?(a>i&&a-i>180?m=a-(i+360):a<i&&i-a>180?m=a+360-i:m=a-i,d=i+r*m):isNaN(i)?isNaN(a)?d=Number.NaN:(d=a,(f==1||f==0)&&n!="hsv"&&(p=c)):(d=i,(u==1||u==0)&&n!="hsv"&&(p=l)),p===void 0&&(p=l+r*(c-l)),h=f+r*(u-f),n==="oklch"?new $([h,p,d],n):new $([d,p,h],n)};var jo=(t,e,r)=>Dt(t,e,r,"lch");lt.lch=jo;lt.hcl=jo;var Qa=(t,e,r)=>{let n=t.num(),o=e.num();return new $(n+r*(o-n),"num")};lt.num=Qa;var tl=(t,e,r)=>Dt(t,e,r,"hcg");lt.hcg=tl;var el=(t,e,r)=>Dt(t,e,r,"hsi");lt.hsi=el;var rl=(t,e,r)=>Dt(t,e,r,"hsl");lt.hsl=rl;var nl=(t,e,r)=>Dt(t,e,r,"hsv");lt.hsv=nl;var ol=(t,e,r)=>{let n=t.oklab(),o=e.oklab();return new $(n[0]+r*(o[0]-n[0]),n[1]+r*(o[1]-n[1]),n[2]+r*(o[2]-n[2]),"oklab")};lt.oklab=ol;var sl=(t,e,r)=>Dt(t,e,r,"oklch");lt.oklch=sl;var{pow:dn,sqrt:pn,PI:hn,cos:Go,sin:Ho,atan2:il}=Math,Vo=(t,e="lrgb",r=null)=>{let n=t.length;r||(r=Array.from(new Array(n)).map(()=>1));let o=n/r.reduce(function(u,p){return u+p});if(r.forEach((u,p)=>{r[p]*=o}),t=t.map(u=>new $(u)),e==="lrgb")return al(t,r);let s=t.shift(),i=s.get(e),a=[],l=0,c=0;for(let u=0;u<i.length;u++)if(i[u]=(i[u]||0)*r[0],a.push(isNaN(i[u])?0:r[0]),e.charAt(u)==="h"&&!isNaN(i[u])){let p=i[u]/180*hn;l+=Go(p)*r[0],c+=Ho(p)*r[0]}let f=s.alpha()*r[0];t.forEach((u,p)=>{let d=u.get(e);f+=u.alpha()*r[p+1];for(let h=0;h<i.length;h++)if(!isNaN(d[h]))if(a[h]+=r[p+1],e.charAt(h)==="h"){let m=d[h]/180*hn;l+=Go(m)*r[p+1],c+=Ho(m)*r[p+1]}else i[h]+=d[h]*r[p+1]});for(let u=0;u<i.length;u++)if(e.charAt(u)==="h"){let p=il(c/a[u],l/a[u])/hn*180;for(;p<0;)p+=360;for(;p>=360;)p-=360;i[u]=p}else i[u]=i[u]/a[u];return f/=n,new $(i,e).alpha(f>.99999?1:f,!0)},al=(t,e)=>{let r=t.length,n=[0,0,0,0];for(let o=0;o<t.length;o++){let s=t[o],i=e[o]/r,a=s._rgb;n[0]+=dn(a[0],2)*i,n[1]+=dn(a[1],2)*i,n[2]+=dn(a[2],2)*i,n[3]+=a[3]*i}return n[0]=pn(n[0]),n[1]=pn(n[1]),n[2]=pn(n[2]),n[3]>.9999999&&(n[3]=1),new $(le(n))};var{pow:ll}=Math;function ce(t){let e="rgb",r=K("#ccc"),n=0,o=[0,1],s=[],i=[0,0],a=!1,l=[],c=!1,f=0,u=1,p=!1,d={},h=!0,m=1,y=function(C){if(C=C||["#fff","#000"],C&&V(C)==="string"&&K.brewer&&K.brewer[C.toLowerCase()]&&(C=K.brewer[C.toLowerCase()]),V(C)==="array"){C.length===1&&(C=[C[0],C[0]]),C=C.slice(0);for(let R=0;R<C.length;R++)C[R]=K(C[R]);s.length=0;for(let R=0;R<C.length;R++)s.push(R/(C.length-1))}return N(),l=C},g=function(C){if(a!=null){let R=a.length-1,j=0;for(;j<R&&C>=a[j];)j++;return j-1}return 0},w=C=>C,E=C=>C,L=function(C,R){let j,B;if(R==null&&(R=!1),isNaN(C)||C===null)return r;R?B=C:a&&a.length>2?B=g(C)/(a.length-2):u!==f?B=(C-f)/(u-f):B=1,B=E(B),R||(B=w(B)),m!==1&&(B=ll(B,m)),B=i[0]+B*(1-i[0]-i[1]),B=Vt(B,0,1);let U=Math.floor(B*1e4);if(h&&d[U])j=d[U];else{if(V(l)==="array")for(let Y=0;Y<s.length;Y++){let X=s[Y];if(B<=X){j=l[Y];break}if(B>=X&&Y===s.length-1){j=l[Y];break}if(B>X&&B<s[Y+1]){B=(B-X)/(s[Y+1]-X),j=K.interpolate(l[Y],l[Y+1],B,e);break}}else V(l)==="function"&&(j=l(B));h&&(d[U]=j)}return j};var N=()=>d={};y(t);let O=function(C){let R=K(L(C));return c&&R[c]?R[c]():R};return O.classes=function(C){if(C!=null){if(V(C)==="array")a=C,o=[C[0],C[C.length-1]];else{let R=K.analyze(o);C===0?a=[R.min,R.max]:a=K.limits(R,"e",C)}return O}return a},O.domain=function(C){if(!arguments.length)return o;f=C[0],u=C[C.length-1],s=[];let R=l.length;if(C.length===R&&f!==u)for(let j of Array.from(C))s.push((j-f)/(u-f));else{for(let j=0;j<R;j++)s.push(j/(R-1));if(C.length>2){let j=C.map((U,Y)=>Y/(C.length-1)),B=C.map(U=>(U-f)/(u-f));B.every((U,Y)=>j[Y]===U)||(E=U=>{if(U<=0||U>=1)return U;let Y=0;for(;U>=B[Y+1];)Y++;let X=(U-B[Y])/(B[Y+1]-B[Y]);return j[Y]+X*(j[Y+1]-j[Y])})}}return o=[f,u],O},O.mode=function(C){return arguments.length?(e=C,N(),O):e},O.range=function(C,R){return y(C,R),O},O.out=function(C){return c=C,O},O.spread=function(C){return arguments.length?(n=C,O):n},O.correctLightness=function(C){return C==null&&(C=!0),p=C,N(),p?w=function(R){let j=L(0,!0).lab()[0],B=L(1,!0).lab()[0],U=j>B,Y=L(R,!0).lab()[0],X=j+(B-j)*R,Nt=Y-X,dt=0,mt=1,rt=20;for(;Math.abs(Nt)>.01&&rt-- >0;)(function(){return U&&(Nt*=-1),Nt<0?(dt=R,R+=(mt-R)*.5):(mt=R,R+=(dt-R)*.5),Y=L(R,!0).lab()[0],Nt=Y-X})();return R}:w=R=>R,O},O.padding=function(C){return C!=null?(V(C)==="number"&&(C=[C,C]),i=C,O):i},O.colors=function(C,R){arguments.length<2&&(R="hex");let j=[];if(arguments.length===0)j=l.slice(0);else if(C===1)j=[O(.5)];else if(C>1){let B=o[0],U=o[1]-B;j=cl(0,C,!1).map(Y=>O(B+Y/(C-1)*U))}else{t=[];let B=[];if(a&&a.length>2)for(let U=1,Y=a.length,X=1<=Y;X?U<Y:U>Y;X?U++:U--)B.push((a[U-1]+a[U])*.5);else B=o;j=B.map(U=>O(U))}return K[R]&&(j=j.map(B=>B[R]())),j},O.cache=function(C){return C!=null?(h=C,O):h},O.gamma=function(C){return C!=null?(m=C,O):m},O.nodata=function(C){return C!=null?(r=K(C),O):r},O}function cl(t,e,r){let n=[],o=t<e,s=r?o?e+1:e-1:e;for(let i=t;o?i<s:i>s;o?i++:i--)n.push(i);return n}var fl=function(t){let e=[1,1];for(let r=1;r<t;r++){let n=[1];for(let o=1;o<=e.length;o++)n[o]=(e[o]||0)+e[o-1];e=n}return e},ul=function(t){let e,r,n,o;if(t=t.map(s=>new $(s)),t.length===2)[r,n]=t.map(s=>s.lab()),e=function(s){let i=[0,1,2].map(a=>r[a]+s*(n[a]-r[a]));return new $(i,"lab")};else if(t.length===3)[r,n,o]=t.map(s=>s.lab()),e=function(s){let i=[0,1,2].map(a=>(1-s)*(1-s)*r[a]+2*(1-s)*s*n[a]+s*s*o[a]);return new $(i,"lab")};else if(t.length===4){let s;[r,n,o,s]=t.map(i=>i.lab()),e=function(i){let a=[0,1,2].map(l=>(1-i)*(1-i)*(1-i)*r[l]+3*(1-i)*(1-i)*i*n[l]+3*(1-i)*i*i*o[l]+i*i*i*s[l]);return new $(a,"lab")}}else if(t.length>=5){let s,i,a;s=t.map(l=>l.lab()),a=t.length-1,i=fl(a),e=function(l){let c=1-l,f=[0,1,2].map(u=>s.reduce((p,d,h)=>p+i[h]*c**(a-h)*l**h*d[u],0));return new $(f,"lab")}}else throw new RangeError("No point in running bezier with only one color.");return e},qo=t=>{let e=ul(t);return e.scale=()=>ce(e),e};var jt=(t,e,r)=>{if(!jt[r])throw new Error("unknown blend mode "+r);return jt[r](t,e)},te=t=>(e,r)=>{let n=K(r).rgb(),o=K(e).rgb();return K.rgb(t(n,o))},ee=t=>(e,r)=>{let n=[];return n[0]=t(e[0],r[0]),n[1]=t(e[1],r[1]),n[2]=t(e[2],r[2]),n},dl=t=>t,pl=(t,e)=>t*e/255,hl=(t,e)=>t>e?e:t,ml=(t,e)=>t>e?t:e,gl=(t,e)=>255*(1-(1-t/255)*(1-e/255)),bl=(t,e)=>e<128?2*t*e/255:255*(1-2*(1-t/255)*(1-e/255)),yl=(t,e)=>255*(1-(1-e/255)/(t/255)),_l=(t,e)=>t===255?255:(t=255*(e/255)/(1-t/255),t>255?255:t);jt.normal=te(ee(dl));jt.multiply=te(ee(pl));jt.screen=te(ee(gl));jt.overlay=te(ee(bl));jt.darken=te(ee(hl));jt.lighten=te(ee(ml));jt.dodge=te(ee(_l));jt.burn=te(ee(yl));var Uo=jt;var{pow:xl,sin:kl,cos:wl}=Math;function Ko(t=300,e=-1.5,r=1,n=1,o=[0,1]){let s=0,i;V(o)==="array"?i=o[1]-o[0]:(i=0,o=[o,o]);let a=function(l){let c=Rt*((t+120)/360+e*l),f=xl(o[0]+i*l,n),p=(s!==0?r[0]+l*s:r)*f*(1-f)/2,d=wl(c),h=kl(c),m=f+p*(-.14861*d+1.78277*h),y=f+p*(-.29227*d-.90649*h),g=f+p*(1.97294*d);return K(le([m*255,y*255,g*255,1]))};return a.start=function(l){return l==null?t:(t=l,a)},a.rotations=function(l){return l==null?e:(e=l,a)},a.gamma=function(l){return l==null?n:(n=l,a)},a.hue=function(l){return l==null?r:(r=l,V(r)==="array"?(s=r[1]-r[0],s===0&&(r=r[1])):s=0,a)},a.lightness=function(l){return l==null?o:(V(l)==="array"?(o=l,i=l[1]-l[0]):(o=[l,l],i=0),a)},a.scale=()=>K.scale(a),a.hue(r),a}var Ml="0123456789abcdef",{floor:Sl,random:vl}=Math,Wo=()=>{let t="#";for(let e=0;e<6;e++)t+=Ml.charAt(Sl(vl()*16));return new $(t,"hex")};var{log:Yo,pow:Cl,floor:Al,abs:$l}=Math;function mn(t,e=null){let r={min:Number.MAX_VALUE,max:Number.MAX_VALUE*-1,sum:0,values:[],count:0};return V(t)==="object"&&(t=Object.values(t)),t.forEach(n=>{e&&V(n)==="object"&&(n=n[e]),n!=null&&!isNaN(n)&&(r.values.push(n),r.sum+=n,n<r.min&&(r.min=n),n>r.max&&(r.max=n),r.count+=1)}),r.domain=[r.min,r.max],r.limits=(n,o)=>gn(r,n,o),r}function gn(t,e="equal",r=7){V(t)=="array"&&(t=mn(t));let{min:n,max:o}=t,s=t.values.sort((a,l)=>a-l);if(r===1)return[n,o];let i=[];if(e.substr(0,1)==="c"&&(i.push(n),i.push(o)),e.substr(0,1)==="e"){i.push(n);for(let a=1;a<r;a++)i.push(n+a/r*(o-n));i.push(o)}else if(e.substr(0,1)==="l"){if(n<=0)throw new Error("Logarithmic scales are only possible for values > 0");let a=Math.LOG10E*Yo(n),l=Math.LOG10E*Yo(o);i.push(n);for(let c=1;c<r;c++)i.push(Cl(10,a+c/r*(l-a)));i.push(o)}else if(e.substr(0,1)==="q"){i.push(n);for(let a=1;a<r;a++){let l=(s.length-1)*a/r,c=Al(l);if(c===l)i.push(s[c]);else{let f=l-c;i.push(s[c]*(1-f)+s[c+1]*f)}}i.push(o)}else if(e.substr(0,1)==="k"){let a,l=s.length,c=new Array(l),f=new Array(r),u=!0,p=0,d=null;d=[],d.push(n);for(let y=1;y<r;y++)d.push(n+y/r*(o-n));for(d.push(o);u;){for(let g=0;g<r;g++)f[g]=0;for(let g=0;g<l;g++){let w=s[g],E=Number.MAX_VALUE,L;for(let N=0;N<r;N++){let O=$l(d[N]-w);O<E&&(E=O,L=N),f[L]++,c[g]=L}}let y=new Array(r);for(let g=0;g<r;g++)y[g]=null;for(let g=0;g<l;g++)a=c[g],y[a]===null?y[a]=s[g]:y[a]+=s[g];for(let g=0;g<r;g++)y[g]*=1/f[g];u=!1;for(let g=0;g<r;g++)if(y[g]!==d[g]){u=!0;break}d=y,p++,p>200&&(u=!1)}let h={};for(let y=0;y<r;y++)h[y]=[];for(let y=0;y<l;y++)a=c[y],h[a].push(s[y]);let m=[];for(let y=0;y<r;y++)m.push(h[y][0]),m.push(h[y][h[y].length-1]);m=m.sort((y,g)=>y-g),i.push(m[0]);for(let y=1;y<m.length;y+=2){let g=m[y];!isNaN(g)&&i.indexOf(g)===-1&&i.push(g)}}return i}var Zo=(t,e)=>{t=new $(t),e=new $(e);let r=t.luminance(),n=e.luminance();return r>n?(r+.05)/(n+.05):(n+.05)/(r+.05)};var{sqrt:Wt,pow:kt,min:Nl,max:El,atan2:Jo,abs:Xo,cos:ur,sin:Qo,exp:Ll,PI:ts}=Math;function es(t,e,r=1,n=1,o=1){var s=function(ht){return 360*ht/(2*ts)},i=function(ht){return 2*ts*ht/360};t=new $(t),e=new $(e);let[a,l,c]=Array.from(t.lab()),[f,u,p]=Array.from(e.lab()),d=(a+f)/2,h=Wt(kt(l,2)+kt(c,2)),m=Wt(kt(u,2)+kt(p,2)),y=(h+m)/2,g=.5*(1-Wt(kt(y,7)/(kt(y,7)+kt(25,7)))),w=l*(1+g),E=u*(1+g),L=Wt(kt(w,2)+kt(c,2)),N=Wt(kt(E,2)+kt(p,2)),O=(L+N)/2,C=s(Jo(c,w)),R=s(Jo(p,E)),j=C>=0?C:C+360,B=R>=0?R:R+360,U=Xo(j-B)>180?(j+B+360)/2:(j+B)/2,Y=1-.17*ur(i(U-30))+.24*ur(i(2*U))+.32*ur(i(3*U+6))-.2*ur(i(4*U-63)),X=B-j;X=Xo(X)<=180?X:B<=j?X+360:X-360,X=2*Wt(L*N)*Qo(i(X)/2);let Nt=f-a,dt=N-L,mt=1+.015*kt(d-50,2)/Wt(20+kt(d-50,2)),rt=1+.045*O,xt=1+.015*O*Y,At=30*Ll(-kt((U-275)/25,2)),ct=-(2*Wt(kt(O,7)/(kt(O,7)+kt(25,7))))*Qo(2*i(At)),ft=Wt(kt(Nt/(r*mt),2)+kt(dt/(n*rt),2)+kt(X/(o*xt),2)+ct*(dt/(n*rt))*(X/(o*xt)));return El(0,Nl(100,ft))}function rs(t,e,r="lab"){t=new $(t),e=new $(e);let n=t.get(r),o=e.get(r),s=0;for(let i in n){let a=(n[i]||0)-(o[i]||0);s+=a*a}return Math.sqrt(s)}var ns=(...t)=>{try{return new $(...t),!0}catch{return!1}};var os={cool(){return ce([K.hsl(180,1,.9),K.hsl(250,.7,.4)])},hot(){return ce(["#000","#f00","#ff0","#fff"],[0,.25,.75,1]).mode("rgb")}};var dr={OrRd:["#fff7ec","#fee8c8","#fdd49e","#fdbb84","#fc8d59","#ef6548","#d7301f","#b30000","#7f0000"],PuBu:["#fff7fb","#ece7f2","#d0d1e6","#a6bddb","#74a9cf","#3690c0","#0570b0","#045a8d","#023858"],BuPu:["#f7fcfd","#e0ecf4","#bfd3e6","#9ebcda","#8c96c6","#8c6bb1","#88419d","#810f7c","#4d004b"],Oranges:["#fff5eb","#fee6ce","#fdd0a2","#fdae6b","#fd8d3c","#f16913","#d94801","#a63603","#7f2704"],BuGn:["#f7fcfd","#e5f5f9","#ccece6","#99d8c9","#66c2a4","#41ae76","#238b45","#006d2c","#00441b"],YlOrBr:["#ffffe5","#fff7bc","#fee391","#fec44f","#fe9929","#ec7014","#cc4c02","#993404","#662506"],YlGn:["#ffffe5","#f7fcb9","#d9f0a3","#addd8e","#78c679","#41ab5d","#238443","#006837","#004529"],Reds:["#fff5f0","#fee0d2","#fcbba1","#fc9272","#fb6a4a","#ef3b2c","#cb181d","#a50f15","#67000d"],RdPu:["#fff7f3","#fde0dd","#fcc5c0","#fa9fb5","#f768a1","#dd3497","#ae017e","#7a0177","#49006a"],Greens:["#f7fcf5","#e5f5e0","#c7e9c0","#a1d99b","#74c476","#41ab5d","#238b45","#006d2c","#00441b"],YlGnBu:["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"],Purples:["#fcfbfd","#efedf5","#dadaeb","#bcbddc","#9e9ac8","#807dba","#6a51a3","#54278f","#3f007d"],GnBu:["#f7fcf0","#e0f3db","#ccebc5","#a8ddb5","#7bccc4","#4eb3d3","#2b8cbe","#0868ac","#084081"],Greys:["#ffffff","#f0f0f0","#d9d9d9","#bdbdbd","#969696","#737373","#525252","#252525","#000000"],YlOrRd:["#ffffcc","#ffeda0","#fed976","#feb24c","#fd8d3c","#fc4e2a","#e31a1c","#bd0026","#800026"],PuRd:["#f7f4f9","#e7e1ef","#d4b9da","#c994c7","#df65b0","#e7298a","#ce1256","#980043","#67001f"],Blues:["#f7fbff","#deebf7","#c6dbef","#9ecae1","#6baed6","#4292c6","#2171b5","#08519c","#08306b"],PuBuGn:["#fff7fb","#ece2f0","#d0d1e6","#a6bddb","#67a9cf","#3690c0","#02818a","#016c59","#014636"],Viridis:["#440154","#482777","#3f4a8a","#31678e","#26838f","#1f9d8a","#6cce5a","#b6de2b","#fee825"],Spectral:["#9e0142","#d53e4f","#f46d43","#fdae61","#fee08b","#ffffbf","#e6f598","#abdda4","#66c2a5","#3288bd","#5e4fa2"],RdYlGn:["#a50026","#d73027","#f46d43","#fdae61","#fee08b","#ffffbf","#d9ef8b","#a6d96a","#66bd63","#1a9850","#006837"],RdBu:["#67001f","#b2182b","#d6604d","#f4a582","#fddbc7","#f7f7f7","#d1e5f0","#92c5de","#4393c3","#2166ac","#053061"],PiYG:["#8e0152","#c51b7d","#de77ae","#f1b6da","#fde0ef","#f7f7f7","#e6f5d0","#b8e186","#7fbc41","#4d9221","#276419"],PRGn:["#40004b","#762a83","#9970ab","#c2a5cf","#e7d4e8","#f7f7f7","#d9f0d3","#a6dba0","#5aae61","#1b7837","#00441b"],RdYlBu:["#a50026","#d73027","#f46d43","#fdae61","#fee090","#ffffbf","#e0f3f8","#abd9e9","#74add1","#4575b4","#313695"],BrBG:["#543005","#8c510a","#bf812d","#dfc27d","#f6e8c3","#f5f5f5","#c7eae5","#80cdc1","#35978f","#01665e","#003c30"],RdGy:["#67001f","#b2182b","#d6604d","#f4a582","#fddbc7","#ffffff","#e0e0e0","#bababa","#878787","#4d4d4d","#1a1a1a"],PuOr:["#7f3b08","#b35806","#e08214","#fdb863","#fee0b6","#f7f7f7","#d8daeb","#b2abd2","#8073ac","#542788","#2d004b"],Set2:["#66c2a5","#fc8d62","#8da0cb","#e78ac3","#a6d854","#ffd92f","#e5c494","#b3b3b3"],Accent:["#7fc97f","#beaed4","#fdc086","#ffff99","#386cb0","#f0027f","#bf5b17","#666666"],Set1:["#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf","#999999"],Set3:["#8dd3c7","#ffffb3","#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5","#d9d9d9","#bc80bd","#ccebc5","#ffed6f"],Dark2:["#1b9e77","#d95f02","#7570b3","#e7298a","#66a61e","#e6ab02","#a6761d","#666666"],Paired:["#a6cee3","#1f78b4","#b2df8a","#33a02c","#fb9a99","#e31a1c","#fdbf6f","#ff7f00","#cab2d6","#6a3d9a","#ffff99","#b15928"],Pastel2:["#b3e2cd","#fdcdac","#cbd5e8","#f4cae4","#e6f5c9","#fff2ae","#f1e2cc","#cccccc"],Pastel1:["#fbb4ae","#b3cde3","#ccebc5","#decbe4","#fed9a6","#ffffcc","#e5d8bd","#fddaec","#f2f2f2"]};for(let t of Object.keys(dr))dr[t.toLowerCase()]=dr[t];var ss=dr;Object.assign(K,{average:Vo,bezier:qo,blend:Uo,cubehelix:Ko,mix:Qt,interpolate:Qt,random:Wo,scale:ce,analyze:mn,contrast:Zo,deltaE:es,distance:rs,limits:gn,valid:ns,scales:os,input:q,colors:Xt,brewer:ss});var ot=K;var bn=t=>typeof t=="number"&&Number.isFinite(t);function Pe(t,e){if(!Array.isArray(t)||!e)return[];let r=[],n=[],o=-1/0,s=()=>{n.length&&r.push(n),n=[]};for(let i of t){let a=i?.[e.x],l=i?.[e.y];if(bn(a)){if(a<=o)return[];o=a}if(!bn(a)||!bn(l)||l<0){s();continue}n.push({x:a,density:l})}return s(),r}function Tl(t,e,r){if(!e)return[];let n=0;for(let i of t)for(let a of i)n=Math.max(n,a.density);let o=e.density_max??n;if(!(o>0)||!(n>0))return[];let s=[];for(let i of t){let a=r(i[0].x)>r(i.at(-1).x)?[...i].reverse():i,l=[],c=()=>{if(l.length>1){let f=l[0].x,u=l.at(-1).x-f;u>0&&s.push({left:f,width:u,stops:l.map(p=>({offset:(p.x-f)/u*100,alpha:p.alpha}))})}l=[]};for(let f=1;f<a.length;f++){let u=a[f-1],p=a[f],d=r(u.x),h=r(p.x);if(d==null||h==null||!(h>d)){c();continue}let m=Math.max(0,d),y=Math.min(100,h);if(!(y>m))continue;let g=w=>{let E=(w-d)/(h-d);return Math.min(1,(u.density*(1-E)+p.density*E)/o)};if(l.length||l.push({x:m,alpha:g(m)}),u.density<o&&p.density>o||u.density>o&&p.density<o){let w=d+(o-u.density)/(p.density-u.density)*(h-d);w>m&&w<y&&l.push({x:w,alpha:1})}l.push({x:y,alpha:g(y)})}c()}return s}function is(t,e,r,n,o=()=>({})){let s=t.distribution,i=Tl(Pe(e[t.source],s),s,r);if(!i.length)return null;let a=b("div",{class:"et-mark et-mark-distribution","aria-hidden":"true",style:{height:`${s.height*100}%`}});for(let l of i){let c=l.stops.map(f=>`rgba(0, 0, 0, ${f.alpha}) ${f.offset}%`).join(", ");a.append(b("div",{class:"et-density-band-run",style:{left:`${l.left}%`,width:`${l.width}%`,backgroundColor:n,...o(l),maskImage:`linear-gradient(to right, ${c})`}}))}return a}function bt(t){return t==null||t===""||!Number.isFinite(Number(t))?null:Number(t)}function yn(t){return t&&typeof t=="object"?t.value??t.x??t.y:t}function pr(t,e){let r=1/0,n=-1/0,o=i=>{let a=bt(i);a==null||t.scale?.transform==="log"&&a<=0||(r=Math.min(r,a),n=Math.max(n,a))},s=t.encodings.filter(i=>i.kind==="stacked_bar");for(let i of e)if(!(i.render_type&&i.render_type!=="cell_data")){if(s.length){let a=s.map(f=>Math.max(0,bt(i[f.source])??0)),l=a.reduce((f,u)=>f+u,0),c=s.findIndex(f=>f.source===s[0].diverge_at);if(t.scale?.normalize==="percent")o(c>=0?-100:0),o(100);else if(c>=0){let f=a.slice(0,c).reduce((d,h)=>d+h,a[c]/2),u=a.slice(c+1).reduce((d,h)=>d+h,a[c]/2),p=Math.max(f,u);o(-p),o(p)}else o(0),o(l)}for(let a of t.encodings){let l=i[a.source];if(a.kind!=="stacked_bar")if(a.kind==="points")if(a.sources)for(let c of a.sources)o(i[c]);else for(let c of Array.isArray(l)?l:[])o(yn(c));else if(a.kind==="distribution")for(let c of Pe(l,a.distribution))for(let f of c)o(f.x);else if(a.kind==="strip"){for(let c of Array.isArray(l)?l:[])if(!(!c||typeof c!="object"))for(let f of["start","position","end","finish"])o(c[f])}else{for(let c of[a.source,a.high,...Object.values(a.parts||{})])o(i[c]);for(let c of a.outliers&&Array.isArray(i[a.outliers])?i[a.outliers]:[])o(c)}}}return r===1/0?null:{min:r,max:n}}var Oe=["#dbeafe","#1e40af"],Pl={green:["#f0fdf4","#16a34a"],blue:["#eff6ff","#2563eb"],red:["#fef2f2","#dc2626"],orange:["#fff7ed","#ea580c"],purple:["#faf5ff","#9333ea"],grey:["#f8fafc","#334155"],gray:["#f8fafc","#334155"]},Ol={viridis:["#440154","#472d7b","#3b528b","#2c728e","#21918c","#28ae80","#5ec962","#addc30","#fde725"],magma:["#000004","#1d1147","#51127c","#832681","#b73779","#e75263","#fc8961","#fec488","#fcfdbf"],plasma:["#0d0887","#4c02a1","#7e03a8","#aa2395","#cc4778","#e66c5c","#f89540","#fdc527","#f0f921"],inferno:["#000004","#210c4a","#57106e","#8a226a","#bc3754","#e45a31","#f98e09","#f9cb35","#fcffa4"],cividis:["#00224e","#1a386f","#434e6c","#61656f","#7d7c78","#9b9476","#bcae6c","#dec958","#fee838"],blues:["#f7fbff","#deebf7","#c6dbef","#9dcae1","#6aaed6","#4191c6","#2070b4","#08509b","#08306b"],reds:["#fff5f0","#fee0d2","#fcbba1","#fc9272","#fb694a","#ee3a2c","#ca181d","#a30f15","#67000d"],greens:["#f7fcf5","#e5f5e0","#c7e9c0","#a0d99b","#73c476","#40aa5d","#228a44","#006c2c","#00441b"],greys:["#ffffff","#f0f0f0","#d9d9d9","#bdbdbd","#959595","#727272","#515151","#242424","#000000"],oranges:["#fff5eb","#fee6ce","#fdd0a2","#fdae6a","#fd8c3b","#f16813","#d84801","#a53603","#7f2704"],purples:["#fcfbfd","#efedf5","#dadaeb","#bcbddc","#9e9ac8","#807cba","#6950a3","#53268f","#3f007d"],bugn:["#f7fcfd","#e5f5f9","#ccece6","#98d8c9","#65c2a3","#40ad75","#228a44","#006c2c","#00441b"],bupu:["#f7fcfd","#e0ecf4","#bfd3e6","#9ebcda","#8c95c6","#8c6ab1","#88409c","#800f7b","#4d004b"],gnbu:["#f7fcf0","#e0f3db","#ccebc5","#a7ddb5","#7accc4","#4db2d3","#2a8bbe","#0867ab","#084081"],orrd:["#fff7ec","#fee8c8","#fdd49e","#fdba83","#fc8c59","#ef6447","#d62f1e","#b20000","#7f0000"],pubu:["#fff7fb","#ece7f2","#d0d1e6","#a5bddb","#73a9cf","#358fc0","#056faf","#04598c","#023858"],rdpu:["#fff7f3","#fde0dd","#fcc5c0","#fa9eb5","#f767a1","#dc3397","#ad017e","#790177","#49006a"],ylgn:["#ffffe5","#f7fcb9","#d9f0a3","#acdd8e","#77c679","#40aa5c","#228343","#006737","#004529"],ylgnbu:["#ffffd9","#edf8b1","#c6e9b4","#7ecdbb","#40b5c4","#1d90c0","#225da8","#243392","#081d58"],ylorbr:["#ffffe5","#fff7bc","#fee390","#fec34f","#fe9829","#eb6f14","#cb4b02","#983404","#662506"],ylorrd:["#ffffcc","#ffeda0","#fed976","#feb24c","#fd8c3c","#fc4d2a","#e2191c","#bb0026","#800026"],rdbu:["#67001f","#bb2a34","#e58368","#fbceb7","#f6f7f7","#c0dceb","#68abd0","#2870b1","#053061"],rdylbu:["#a50026","#de402e","#f98e52","#fed485","#feffc0","#d1ecf4","#8ec2dc","#4f81ba","#313695"],rdylgn:["#a50026","#de402e","#f98e52","#fed481","#feffbe","#cbe982","#84ca66","#2aa054","#006837"],coolwarm:["#3b4cc0","#6282ea","#8db0fe","#b9d0f9","#dddcdc","#f5c4ac","#f4987a","#dd5f4b","#b40426"],bwr:["#0000ff","#4040ff","#8080ff","#c0c0ff","#fffefe","#ffbebe","#ff7e7e","#ff3e3e","#ff0000"],spectral:["#9e0142","#dd4a4c","#f98e52","#fed481","#ffffbe","#d6ee9b","#86cfa5","#3d95b8","#5e4fa2"],piyg:["#8e0152","#cb3289","#e897c4","#fad6ea","#f7f7f6","#d9f0bc","#9acd61","#589b28","#276419"],prgn:["#40004b","#7f3c8d","#ae8bbd","#dec9e2","#f6f7f6","#cbeac5","#7ec37f","#298440","#00441b"],brbg:["#543005","#995d13","#cfa256","#f1dfb3","#f4f5f5","#b4e2db","#58b0a7","#0c7169","#003c30"]},Re={...Pl,...Ol},hr=[["tab:blue","#1f77b4"],["tab:orange","#ff7f0e"],["tab:green","#2ca02c"],["tab:red","#d62728"],["tab:purple","#9467bd"],["tab:brown","#8c564b"],["tab:pink","#e377c2"],["tab:gray","#7f7f7f"],["tab:olive","#bcbd22"],["tab:cyan","#17becf"]],ls={...Object.fromEntries(hr),b:"#0000ff",g:"#008000",r:"#ff0000",c:"#00bfbf",m:"#bf00bf",y:"#bfbf00",k:"#000000",w:"#ffffff"};hr.forEach(([,t],e)=>{ls[`c${e}`]=t});function Z(t){return typeof t!="string"?t:ls[t.toLowerCase()]??t}var cs=new WeakMap;function gr(t,e){cs.set(t,e)}function Tt(t,e){return cs.get(e)?.(t)??Z(t)}function Me(t,e){return t&&typeof t=="object"&&!Array.isArray(t)&&typeof t.color=="string"&&Tt(t.color,e)||null}var as=new WeakMap;function Gt(t,e){if(e==null||e==="")return t.style.removeProperty("--et-cell-fill"),!0;let r=as.get(t.ownerDocument);r||(r=t.ownerDocument.createElement("span").style,as.set(t.ownerDocument,r)),r.backgroundColor="",r.backgroundColor=Z(e);let n=r.backgroundColor;return n?(t.style.setProperty("--et-cell-fill",n),!0):!1}function mr(t){return typeof t!="string"?Array.isArray(t)?t.map(Z):t:Re[t.toLowerCase()]}function br(t,e="tab10"){if(t<=0)return[];if(e==null||e==="tab10")return Array.from({length:t},(n,o)=>hr[o%hr.length][1]);let r=mr(e);return r?.length?r.length===1?Array(t).fill(r[0]):ot.scale(r).mode("lab").colors(t):Array(t).fill(Z("C0"))}function fs(t){try{return ot(t),!0}catch{return!1}}function Rl(t){if(!Array.isArray(t)||t.length<2)return null;let e=t.filter(o=>o&&typeof o.value=="number"&&isFinite(o.value)&&typeof o.color=="string"&&fs(Z(o.color)));if(e.length<2)return null;let r=[...e].sort((o,s)=>o.value-s.value),n=[];for(let o of r)(n.length===0||o.value>n[n.length-1].value)&&n.push(o);return n.length>=2?n:null}function _n(t){for(let e=1;e<t.length;e++)if(!(t[e]>t[e-1]))return!1;return!0}function Dl(t,e,r,n){let o=n.length,s=(o-1)/2;if(r>t&&r<e){let l=new Array(o);for(let c=0;c<o;c++)c<s?l[c]=t+c/s*(r-t):c>s?l[c]=r+(c-s)/(o-1-s)*(e-r):l[c]=r;return _n(l)?{palette:n,domain:l,midpoint:r}:null}if(r<=t){let l=n.slice(Math.floor(s));if(l.length<2)return null;let c=l.map((f,u)=>r+u/(l.length-1)*(e-r));return _n(c)?{palette:l,domain:c,midpoint:null}:null}let i=n.slice(0,Math.ceil(s)+1);if(i.length<2)return null;let a=i.map((l,c)=>t+c/(i.length-1)*(r-t));return _n(a)?{palette:i,domain:a,midpoint:null}:null}function Yt(t,e){let{colorPalette:r,defaultColorScale:n=Oe,mode:o="lch",min:s,max:i,midpoint:a,colorStops:l}=e,c=Rl(l);if(c){let C=c.map(B=>B.color),R=c.map(B=>B.value);return{scale:ot.scale(C).domain(R).mode(o).cache(!1),kind:"stops",colorPalette:C,minValue:R[0],maxValue:R[R.length-1],domain:R,midpoint:null}}let f=t.filter(C=>!isNaN(C)&&isFinite(C)),u=typeof s=="number"&&isFinite(s),p=typeof i=="number"&&isFinite(i);if(f.length===0&&!(u&&p))return null;let d=u?s:Math.min(...f),h=p?i:Math.max(...f);d<h||(d===h?h=d+1:[d,h]=[h,d]);let m;if(r&&r.length>0){let C=(mr(r)||[]).filter(fs);C.length>=2?m=C:C.length===1?m=[n[0]??"#ffffff",C[0]]:m=n}else m=n;let g=typeof a=="number"&&isFinite(a)&&m.length>=3,w=m,E=[d,h],L=null,N="linear";if(g){let C=Dl(d,h,a,m);C&&(w=C.palette,E=C.domain,L=C.midpoint,N="diverging")}return{scale:ot.scale(w).domain(E).mode(o),kind:N,colorPalette:w,minValue:d,maxValue:h,domain:E,midpoint:L}}function fe(t,e){return!isFinite(t)||isNaN(t)?e.colorPalette[0]:e.scale(e.project?e.project(t):t).hex()}function re(t,e="#ffffff",r=1){let n=ot(Z(t)),o=n.alpha()*r;if(o>=1)return n.alpha(1);let s=ot.valid(Z(e))?ot(Z(e)).alpha(1):ot("white");return ot.mix(s,n.alpha(1),Math.max(0,o),"rgb")}function we(t,e){try{let r=ot(Z(t)),n=re(r,e),o=ot.contrast(n,"#000000")>ot.contrast(n,"#ffffff")?"#000000":"#ffffff",s=n.luminance()<.5,i=(s?n.brighten(.5):n.darken(.5)).hex();return{backgroundColor:r.hex(),color:o,borderBottomColor:i,topBorderColor:s?"rgb(75 85 99)":"rgb(156 163 175)"}}catch{return null}}function ue(t,e){try{return re(t,e).luminance()<.5?"#ffffff":"#000000"}catch{return"inherit"}}function us(t,e){let r=new Map;for(let n of t){if(n.encodings&&n.encodings.length){let l=pr(n,e);l&&(r.set(n,l),r.set(n.name,l));continue}if(n.viz!=="bar"&&n.viz!=="color"&&n.viz!=="chip")continue;let o=n.color_options||{},s=(n.viz==="color"||n.viz==="chip")&&o.scale_column?o.scale_column:n.name,i=1/0,a=-1/0;for(let l of e){if(l.render_type==="row_total"||l.render_type==="row_subtotal"&&n.viz_include_subtotals===!1)continue;let c=l[s];if(c==null)continue;let f=Number(c);!isNaN(f)&&isFinite(f)&&(i=Math.min(i,f),a=Math.max(a,f))}if(i!==1/0&&a!==-1/0){o.min!=null&&isFinite(o.min)&&(i=o.min),o.max!=null&&isFinite(o.max)&&(a=o.max);let l={min:i,max:a};r.set(n,l),r.set(n.name,l)}}return r}function ds(t,e){let r=new Map;for(let n of t){if(!n.fmt||n.fmt.length!==3)continue;let o=1/0,s=-1/0;for(let i of e){if(i.render_type==="row_total"||i.render_type==="row_subtotal")continue;let a=Number(i[n.name]);!isNaN(a)&&isFinite(a)&&(o=Math.min(o,a),s=Math.max(s,a))}o!==1/0&&s!==-1/0&&r.set(n.name,{min:o,max:s})}return r}function xn(t,e,r,n="lch"){r=Array.isArray(r)?r.map(Z):r;let o=t.neutral_range;if(!o)return Yt([],{colorPalette:r,min:e.min,max:e.max,midpoint:t.midpoint,mode:n});let s=Yt([],{colorPalette:r,min:0,max:1,mode:n});return s.project=i=>{let a=.5;return i<o[0]?a=e.min<o[0]?.5*(i-e.min)/(o[0]-e.min):0:i>o[1]&&(a=e.max>o[1]?.5+.5*(i-o[1])/(e.max-o[1]):1),Math.max(0,Math.min(1,a))},s}function ps(t,e,r){let n=t.color_options||{};if(t.domain&&e.shared){let o=typeof t.domain=="string"?{}:t.domain;return xn({...o,midpoint:o.midpoint??n.midpoint},e,o.palette??n.color_scale??r??Oe,n.scale_mode)}if(typeof n.color_scale=="string"&&!Re[n.color_scale.toLowerCase()])throw new Error(`Unknown colour scale '${n.color_scale}'. Use one of ${Object.keys(Re).sort().join(", ")}, or a list of colours.`);return Yt([],{colorPalette:mr(n.color_scale),colorStops:n.color_stops,defaultColorScale:mr(r)??Oe,min:n.min??e.min,max:n.max??e.max,midpoint:n.midpoint,mode:n.scale_mode??"lch"})}function kn(t,e,r,n,o){let s=t.color_options||{},i=s.conditional_colors;if(i&&i in e){let f=e[i];return f&&typeof f=="string"?we(Tt(f,s),o):null}let a=s.scale_column||t.name,l=Number(e[a]);if(isNaN(l)||!n)return null;let c=l;if(n.kind!=="stops"){let f=s.min!=null&&isFinite(s.min)?s.min:r.min,u=s.max!=null&&isFinite(s.max)?s.max:r.max;Math.abs(u-f)<1e-10&&(c=(n.minValue+n.maxValue)/2)}return we(fe(c,n),o)}var wn=new WeakMap,Bl="[data-et-auto-contrast]";function Bt(t,e={}){wn.set(t,e),t.setAttribute("data-et-auto-contrast","")}function De(t){wn.delete(t),t.removeAttribute("data-et-auto-contrast")}function hs(t){return t.parentElement||t.getRootNode()?.host||null}function Mn(t){let e=t.ownerDocument.defaultView,r=new Map,n=new Map,o=new Map,s,i,a=f=>(r.has(f)||r.set(f,e.getComputedStyle(f)),r.get(f)),l=f=>{if(!f?.trim())return ot("#00000000");if(n.has(f))return n.get(f);let u;if(ot.valid(f))u=ot(f);else{s||=t.appendChild(t.ownerDocument.createElement("span")),s.style.display="none",s.style.backgroundColor="",s.style.backgroundColor=f;let p=e.getComputedStyle(s).backgroundColor;if(ot.valid(p))u=ot(p);else if(s.style.backgroundColor&&e.CanvasRenderingContext2D){if(!i){let d=t.ownerDocument.createElement("canvas");d.width=d.height=1,i=d.getContext("2d",{willReadFrequently:!0})}if(i){i.clearRect(0,0,1,1),i.fillStyle=p,i.fillRect(0,0,1,1);let[d,h,m,y]=i.getImageData(0,0,1,1).data;u=ot(d,h,m).alpha(y/255)}}}return u||=ot("#00000000"),n.set(f,u),u},c=f=>{if(!f)return re(l("Canvas"),"white");if(o.has(f))return o.get(f);let u=a(f),p=re(l(u.backgroundColor),c(hs(f)));if(f.classList.contains("et-td"))for(let d of["--et-row-tint","--et-cell-fill","--et-selection-tint"])p=re(l(u.getPropertyValue(d)),p);if(f.classList.contains("et-marks"))for(let d of f.querySelectorAll(":scope > .et-mark-background"))p=re(l(a(d).backgroundColor),p,Number(a(d).opacity||1));return o.set(f,p),p};return{style:a,color:l,background:c,destroy:()=>s?.remove()}}function Sn(t){let e=[...t.querySelectorAll(Bl)];if(!e.length)return;let r=Mn(t);try{let n=e.map(o=>{let s=wn.get(o),i;if(s?.mark){let a=r.color(r.style(o).getPropertyValue("--et-label-fill")),l=Number(r.style(s.mark).opacity||1);i=re(a,r.background(s.mark.parentElement),l)}else i=r.background(o);return[o,s?.policy==="cell"?we(i).color:ue(i)]});for(let[o,s]of n)o.style.color=s}finally{r.destroy()}}var yr=class{constructor(e,r){this.root=e,this.frame=r,this.view=e.ownerDocument.defaultView,this.schedule=()=>{this.pending||this.destroyed||(this.pending=!0,this.frame(()=>{this.pending=!1,this.destroyed||Sn(this.root)}))},this.observer=new this.view.MutationObserver(n=>{n.some(o=>this.ancestors.has(o.target)||o.target.tagName==="TR")&&this.schedule()}),this.media=this.view.matchMedia?.("(prefers-color-scheme: dark)"),this.media?.addEventListener("change",this.schedule),this.onPointer=n=>{let o=n.target.closest?.("tr")??null,s=n.relatedTarget?.closest?.("tr")??null;o!==s&&this.schedule()},e.addEventListener("pointerover",this.onPointer),e.addEventListener("pointerout",this.onPointer)}watch(){this.observer.disconnect(),this.ancestors=new Set;for(let e=this.root;e;e=hs(e))this.ancestors.add(e),this.observer.observe(e,{attributes:!0,attributeFilter:["class","style"],subtree:e===this.root})}destroy(){this.destroyed=!0,this.observer.disconnect(),this.media?.removeEventListener("change",this.schedule),this.root.removeEventListener("pointerover",this.onPointer),this.root.removeEventListener("pointerout",this.onPointer)}};var ms=new WeakMap,zl=["inside_start","inside_end","outside_start","outside_end","center","above","below"].map(t=>`et-mark-label-${t}`).concat(["et-mark-label-inside","et-mark-label-left","et-mark-label-start","et-mark-label-align-begin","et-mark-label-align-center","et-mark-label-align-end"]);function An(t,e,r){t.dataset.autoContrast="true",t.style.setProperty("--et-label-fill",e),t.style.color=ue(e),r&&Bt(t,{mark:r})}function $n(t){return Jt({...t.color?{color:Z(t.color)}:{},...t.font_weight?{fontWeight:t.font_weight}:{},...t.font_style?{fontStyle:t.font_style}:{}},t,{})}function vn(t,e,r,n){if(t.classList.remove(...zl),t.classList.add(`et-mark-label-${n}`),t.dataset.labelPosition=n,t.style.width="",t.style.color=e.color?Z(e.color):"",t.style.removeProperty("--et-label-fill"),delete t.dataset.autoContrast,De(t),["inside_start","inside_end","center"].includes(n)){t.style.left=`${r.leftPct}%`,t.style.width=`${Math.max(0,r.widthPct)}%`,t.classList.add("et-mark-label-inside");let s=n==="inside_start"?!r.negative:r.negative,i=e.align||(n==="center"?"center":s?"begin":"end");if(t.classList.add(`et-mark-label-align-${i}`),!e.color&&r.color){let a=n==="center"?r.leftPct+r.widthPct/2:s?r.leftPct:r.leftPct+r.widthPct;An(t,r.colorAt?r.colorAt(a):r.color,r.mark)}}else{let s=n==="outside_start"?!r.negative:r.negative;t.style.left=`${s?r.leftPct:r.leftPct+r.widthPct}%`,s&&["outside_start","outside_end"].includes(n)&&t.classList.add("et-mark-label-left")}}function Nn(t,e,r,n){let o=e.label||{},s;if(o.text!=null)s=String(o.text);else{let i=o.source!=null?r[o.source]:r[e.source];s=n?n(i,o):i==null?"":pt(i,o.format||t.fmt,{type:t.type,fallback:String(i)})}return s===""?"":`${o.prefix??""}${s}${o.suffix??""}`}function gs(t,e,r,n,o){let s=e.label||{},i=Nn(t,e,r,o);if(!i)return b("span",{class:"et-mark-label et-mark-label-empty"});let a=s.position||(e.kind==="bar"?"outside_end":"center"),l=b("span",{class:`et-mark-label et-mark-label-${a}`,title:i,"data-mark-label":"","data-overflow":s.overflow||"hide","data-min-width":s.min_width||0,style:$n(s)},b("span",{class:"et-mark-label-text"},Mt(i)));return n.leftPct!=null?(vn(l,s,n,a),s.auto&&ms.set(l,{spec:s,geometry:n,preferred:a})):n.pointPct!=null&&(l.style.left=`${n.pointPct}%`,a==="outside_start"&&l.classList.add("et-mark-label-left")),l}function Cn(t){let r=(t.classList.contains("et-mark-stack-label")?t.parentElement:t).getBoundingClientRect(),n=t.closest("td")?.getBoundingClientRect();if(!n||!(n.right>n.left))return null;if(!r.width)return!1;let o=t.querySelector(".et-mark-label-text")||t;return(t.classList.contains("et-mark-label-inside")||t.classList.contains("et-mark-stack-label")?o.getBoundingClientRect().width+6<=r.width:r.left>=n.left&&r.right<=n.right)&&r.width>=Number(t.dataset.minWidth||0)}function Il(t,{spec:e,geometry:r,preferred:n}){t.hidden=!1,vn(t,e,r,n);let o=Cn(t);if(o==null)return;if(o){t.style.visibility="";return}let s=n.startsWith("outside_")?n.replace("outside_","inside_"):n.replace("inside_","outside_");vn(t,e,r,s);let i=Cn(t);t.style.visibility=i?"":"hidden",t.hidden=!i}function _r(t){for(let e of t.querySelectorAll("[data-mark-label]")){let r=ms.get(e);if(r)Il(e,r);else if(e.dataset.overflow!=="show"){e.hidden=!1;let n=Cn(e);n!=null&&(e.style.visibility=n?"":"hidden",e.hidden=!n)}if(e.dataset.autoContrast){let n=e.ownerDocument.defaultView.getComputedStyle(e);e.style.color=ue(n.getPropertyValue("--et-label-fill").trim())}}Sn(t)}function En(t){if(Array.isArray(t))return["array",t.map(En)];if(t!==null&&typeof t=="object"){let e=t;return["object",Object.keys(e).sort().map(r=>[r,En(e[r])])]}return[typeof t,t]}function bs(t,e){let r=Array.from(t),n=Array.from(e);for(let o=0;o<Math.min(r.length,n.length);o++){let s=r[o].codePointAt(0)-n[o].codePointAt(0);if(s)return s}return r.length-n.length}function ys(t,e){let r=e.filter(s=>s!=null);if(t==="count")return r.length;if(["count_distinct","countdistinct","distinct_count"].includes(t))return new Set(r.map(s=>JSON.stringify(En(s)))).size;if(!r.length)return null;if(["min","max"].includes(t)&&r.every(s=>typeof s=="string"))return r.reduce((s,i)=>(t==="min"?bs(i,s)<0:bs(i,s)>0)?i:s);if(!r.every(s=>typeof s=="number"&&Number.isFinite(s)||typeof s=="boolean"))throw new TypeError(`summary ${t} requires numeric values (min/max also accept strings and ISO dates)`);let n=r.map(Number);if(t==="min")return r.reduce((s,i)=>i<s?i:s);if(t==="max")return r.reduce((s,i)=>i>s?i:s);if(t==="median"){let s=[...r].sort((a,l)=>Number(a)-Number(l)),i=Math.floor(s.length/2);return s.length%2?s[i]:(Number(s[i-1])+Number(s[i]))/2}let o=n.reduce((s,i)=>s+i,0);if(t==="sum")return o;if(["mean","avg","average","weighted_mean","weightedmean"].includes(t))return o/n.length;throw new TypeError(`Unknown summary aggregation ${t}`)}function Fl(t,e){if(!t.operation)return t.value;let r=t.source==null?e:e.map(o=>o[t.source]).filter(o=>o!=null),n=ys(t.operation,r);return n!=null&&(t.prefix||t.suffix)?`${t.prefix||""}${pt(n,t.format||"num",{type:"number",fallback:String(n)})}${t.suffix||""}`:n}function*jl(t,e,r){let n=0,o=t.length;for(;n<o;){let s=n+o>>>1;t[s].last<e?n=s+1:o=s}for(let s=n;s<t.length&&t[s].first<r;s++)yield t[s]}var Be=class{constructor(e,r,n){if(this.layout=e,this.indices=new Map(r.map((o,s)=>[o,s])),this.rank=new Map(n.map((o,s)=>[o,s])),this.ordered=[],this.cells=new WeakMap,this.tree=this.prepareGroups(e.groups||[],r),!e.groups?.length)for(let o of n)this.ordered.push(o);this.ordinals=new Map(this.ordered.map((o,s)=>[o,s])),this.folded=null}prepareGroups(e,r){return e.map(n=>{let o=n.members.map(i=>r[i]).filter(i=>this.rank.has(i)).sort((i,a)=>this.rank.get(i)-this.rank.get(a)),s=this.prepareGroups(n.children,r);if(!s.length)for(let i of o)this.ordered.push(i);return{group:n,members:o,children:s}}).filter(n=>n.members.length)}dataUnit(e,r=0,n=!1,o=0){return{kind:"data",row:e,depth:r,inset:n,toggleDepth:o,index:this.indices.get(e),ordinal:this.ordinals.get(e)}}fold(e,r){let n={units:[],starts:new Map,collapsedGroups:0,revision:r},o=(s,i=!1,a=0)=>s.map(({group:l,members:c,children:f})=>{let u=n.units.length;n.starts.set(l.id,u);let p=!!l.section?.collapsible&&e(l.id),d=i||l.section&&l.section.align!=="center"||l.summary?.position==="top",h=a+(l.section?.collapsible&&l.section.align!=="center"?1:0),m=[];if(p)n.units.push({kind:"collapsed",groupKey:l.id}),n.collapsedGroups++;else if(f.length)m=o(f,d,h);else for(let g of c)n.units.push(this.dataUnit(g,l.depth+1,d,h));let y=p&&l.section?.collapsed_summary&&!Object.keys(l.section.cells||{}).length&&l.summary?{...l.section,cells:l.summary.cells}:l.section;return{group:l,members:c,collapsed:p,children:m,inset:d,toggleDepth:a,childToggleDepth:h,heading:y,first:u,last:n.units.length-1}});if(n.tree=o(this.tree),!this.layout.groups?.length)for(let s of this.ordered)n.units.push(this.dataUnit(s));return this.folded=n,n}annotation(e,r,n,o,s,i=!1,a=0){let l=this.cells.get(n);l||(l=new WeakMap,this.cells.set(n,l));let c=l.get(o);return c||(c=Object.fromEntries(Object.entries(n.cells||{}).map(([f,u])=>[f,{...u,value:Fl(u,o)}])),l.set(o,c)),{kind:e,id:r,depth:s,toggleDepth:a,label:`${n.label}${i?" (cont.)":""}`,cells:c,style:n.style||{},rule:n.rule||"none",align:n.align||"left",labelColumn:n.label_column,labelStyle:n.label_style||{},continuation:i}}appendGroups(e,r,n,o,s){for(let i of jl(e,r,n)){let{group:a,members:l,collapsed:c,children:f,inset:u,toggleDepth:p,childToggleDepth:d,first:h,last:m,heading:y}=i;if(y&&s.push({...this.annotation("section",`${a.id}:section`,y,l,a.depth,h<r,p),groupKey:a.id,collapsible:!!y.collapsible,collapsed:c}),c)continue;let g=a.depth+(u&&a.summary?.indent!==!1?1:0),w=a.summary?.indent!==!1?d:p;if(a.summary?.position==="top"&&h>=r&&s.push(this.annotation("summary",`${a.id}:summary`,a.summary,l,g,!1,w)),f.length)this.appendGroups(f,r,n,o,s);else for(let E of o.slice(Math.max(r,h),Math.min(n,m+1)))s.push(E);a.summary?.position==="bottom"&&m<n&&s.push(this.annotation("summary",`${a.id}:summary`,a.summary,l,g,!1,w))}}page(e,r,n=null,{isCollapsed:o=()=>!1,anchorGroup:s=null,revision:i=0}={}){let{tree:a,units:l,starts:c,collapsedGroups:f}=this.folded?.revision===i?this.folded:this.fold(o,i),u=l.length,p=e==="all"||!(Number(e)>0)?Math.max(1,u):Number(e),d=Math.max(1,Math.ceil(u/p)),h=c.has(s)?Math.floor(c.get(s)/p):r,m=Math.min(Math.max(0,h),d-1),y=n?n(u):{pageCount:d,page:m,start:m*p,end:Math.min(u,(m+1)*p)},{start:g,end:w}=y,E=[];if(a.length)this.appendGroups(a,g,w,l,E);else for(let L of l.slice(g,w))E.push(L);return u&&w===u&&this.layout.grand_summary&&E.push(this.annotation("grand_summary","grand-summary",this.layout.grand_summary,this.ordered,0)),{...y,entries:E,rows:l.slice(g,w).filter(L=>L.kind==="data").map(L=>L.row),total:u,unitCount:w-g,matchingTotal:this.ordered.length,collapsedGroups:f}}};function _s(t,e,r,n,o,s=null,i={}){return new Be(t,e,r).page(n,o,s,i)}function xr(t,e,r,n){let o=new Map(e.map((u,p)=>[u,p])),s=new Map(r.map((u,p)=>[o.get(u),p])),i=new Set(t.legacy.filter(u=>u.row?.__group_key&&n(u.row.__group_key)).map(u=>u.row.__group_key)),a=u=>!(u.__ancestors||[]).some(p=>i.has(p)),l=[],c=[],f=()=>{c.sort((u,p)=>s.get(u)-s.get(p));for(let u of c)a(e[u])&&l.push(e[u]);c=[]};for(let u of t.legacy){if(u.index!=null){s.has(u.index)&&c.push(u.index);continue}f(),s.size&&u.members.some(p=>s.has(p))&&a(u.row)&&l.push(u.row)}return f(),l}function kr(t,e){return b("div",{class:"et-stats-line"},[b("span",{class:"et-stats-label"},`${t}: `),b("span",{class:"et-stats-value"},Mt(e))])}function Gl(t,e,r){let n=e.get(t.name)||{min:null,max:null,avg:null,nulls:0,distinct:0,trues:0,falses:0},o=String(t.type||"string").toUpperCase(),s=b("div",{class:"et-stats-summary"},[b("div",{class:"et-stats-type"},`${o} (nulls = ${pt(n.nulls,"num0")})`),b("div",{class:"et-stats-name"},`"${t.name}"`)]);if(t.type==="number"){let i=r.get(t.name)||(n.min!=null?{min:n.min,max:n.max}:void 0);for(let a of["min","max","avg"]){let l=n[a];s.append(kr(a,l==null?"\u2013":pt(l,t.fmt,{type:"number",range:i,fallback:String(l)})))}}else t.type==="boolean"?(s.append(kr("true",pt(n.trues,"num0"))),s.append(kr("false",pt(n.falses,"num0")))):s.append(kr("distinct",pt(n.distinct,"num0")));return s}function xs({columns:t,layout:e,stats:r,formatRanges:n,options:o,rowNumbers:s,selections:i,onLayout:a}){let l=b("tr",{class:"et-row et-stats-row"}),c=e.leaves.some(d=>d.span>1),f=()=>b("div",{class:"et-stats-footer"});s&&l.append(b("td",{class:"et-td et-row-num","data-column-index":0},c?b("div",{class:"et-stats et-stats-with-footer"},[b("div",{class:"et-stats-summary"}),f()]):""));let u=new Set(e.leaves.map(d=>t[d.start].name));for(let d of i.keys())u.has(d)||i.delete(d);for(let d of e.leaves){let O=function(){let C=h[y];if(i.has(m)&&i.set(m,C.name),L.dataset.statsColumn=C.name,w.replaceChildren(Gl(C,r,n)),N){let R=C.title||Ft(C.name),j=h[(y+1)%h.length];N.textContent=h.map((B,U)=>U===y?"\u25CF":"\u25CB").join(""),N.setAttribute("aria-label",`${E} statistics: ${R}, ${y+1} of ${h.length}. Show ${j.title||Ft(j.name)} statistics`),N.title=N.getAttribute("aria-label")}};var p=O;let h=t.slice(d.start,d.start+d.span),m=h[0].name,y=h.findIndex(C=>C.name===i.get(m));y<0&&(y=0);let g=b("div",{class:`et-stats${c?" et-stats-with-footer":""}`}),w=b("div",{"aria-live":d.span>1?"polite":null});g.append(w);let E=d.label||h[0].title||Ft(m),L=b("td",{class:`et-td et-stats-cell${$t(o,{name:m})?" et-stub":""}`,colspan:d.span,"data-column-start":d.start+(s?1:0)},g),N;if(c){let C=f();d.span>1&&(N=b("button",{type:"button",class:"et-stats-cycle"}),C.append(N),N.addEventListener("click",()=>{y=(y+1)%h.length,i.set(m,h[y].name),O(),a()})),g.append(C)}O(),l.append(L)}return l}function qt(t,e={},r=null){let n=r||($t(e,t)&&e.stub_head?e.stub_head:e.format_titles===!1?t.name:t.title??Ft(t.name));return e.all_caps&&(n=String(n).toUpperCase()),n}function Ln(t){return t?Array.isArray(t)?t.map(String):[String(t)]:[]}function ks(t){return Array.isArray(t)?t.join("\0"):String(t)}function Hl(t,e,r=null){let n=Array.from({length:e},()=>[]);function o(s,i,a){if(a>=e)return;let l=s;for(;l<i;){let c=t[l][a]??"",f=l+1;for(;f<i&&(t[f][a]??"")===c&&!(c===""&&f===r);)f++;n[a].push({label:c,span:f-l,start:l}),o(l,f,a+1),l=f}}return o(0,t.length,0),n}function Mr(t,e){if(e.order_columns_by_group===!1)return t;let r=new Map;for(let l of t){if(!l.column_group)continue;let c=ks(l.column_group);r.has(c)||r.set(c,[]),r.get(c).push(l)}let n=new Set,o=[];for(let l of t){let c=l.column_group;if(!c){o.push(l);continue}let f=ks(c);n.has(f)||(n.add(f),o.push(...r.get(f)))}let s=new Map;for(let l of o){if(!l.subcolumn_group)continue;let c=wr(l);s.has(c)||s.set(c,[]),s.get(c).push(l)}let i=[],a=new Set;for(let l of o){if(!l.subcolumn_group){i.push(l);continue}let c=wr(l);a.has(c)||(a.add(c),i.push(...s.get(c)))}return i}function wr(t){return JSON.stringify([Ln(t.column_group),t.subcolumn_group])}function ze(t,{breakAt:e=null}={}){let r=t.map(i=>Ln(i.column_group)),n=Math.max(0,...r.map(i=>i.length)),o=[],s=new Map;for(let i=0;i<t.length;){let a=t[i],l=i+1;if(a.subcolumn_group)for(;l<t.length&&wr(t[l])===wr(a);)l++;let c=l-i;o.push({start:i,span:c,label:a.subcolumn_group||null});for(let f=i;c>1&&f<l;f++)s.set(t[f].name,{left:f>i,right:f<l-1,label:a.subcolumn_group});i=l}return{depth:n,levels:Hl(r,n,e),leaves:o,joins:s}}function de(t,e,r,n){t.dataset.columnIndex=r+(n.rowNumbers?1:0);let o=n.subcolumns.get(e.name);o&&(t.classList.toggle("et-subcolumn-left",o.left),t.classList.toggle("et-subcolumn-right",o.right),t.setAttribute("aria-label",`${o.label}: ${e.title??Ft(e.name)}: ${t.textContent}`))}function ws(t){let e=b("span",{class:"et-th-title"});return String(t).split(`
`).forEach((r,n)=>{n>0&&e.append(b("br")),e.append(b("span",{class:"et-th-line"},r))}),e}function Ms({columns:t,rowNumbers:e,options:r,sort:n,onSort:o,onInfo:s}){let i=b("thead"),a=r.freeze_columns||0,{depth:l,levels:c,leaves:f}=ze(t,{breakAt:a>0?a-(e?1:0):null});l>0&&c.forEach((p,d)=>{let h=b("tr",{class:"et-header-groups"});e&&d===0&&h.append(b("th",{class:"et-th et-th-group et-row-num",rowspan:l,"data-column-start":0},""));for(let m of p){let y=b("th",{class:`et-th et-th-group${m.label?"":" et-th-group-blank"}`,colspan:m.span,scope:"colgroup","data-column-start":m.start+(e?1:0),"data-group":m.label,title:m.label||null},ws(m.label)),g=t.slice(m.start,m.start+m.span);g.length&&g.every(w=>w.highlight&&w.highlight===g[0].highlight)&&(y.style.backgroundColor=Z(g[0].highlight),!r.header_font_color&&!r.theme?.header_text&&Bt(y,{policy:"cell"})),h.append(y)}i.append(h)});let u=b("tr",{class:"et-header-leaves"});e&&u.append(b("th",{class:"et-th et-row-num","aria-label":"Row number","data-column-start":0},"#"));for(let p of f){let d=t[p.start],h=n?.column===d.name,m=h?n.direction:null,y=$t(r,d),g=d.rotate_title??(y?null:r.rotate_titles),w=`et-th${h?" et-th-sorted":""}${y?" et-stub-head":""}`;l>0&&!Ln(d.column_group).some(Boolean)&&(w+=" et-th-ungrouped"),g==="vertical"?w+=" et-th-vertical":typeof g=="number"&&(w+=" et-th-oblique");let E=d.info?String(d.info):null,L=b("th",{class:w+(p.label?" et-th-subcolumns":""),colspan:p.span,scope:p.span>1?"colgroup":"col","data-column-start":p.start+(e?1:0),style:Jt(p.label?{textAlign:"center"}:ge(d),d,r),"aria-sort":h?m==="asc"?"ascending":"descending":"none"});typeof g=="number"&&L.style.setProperty("--et-th-angle",`${g}deg`);let N=t.slice(p.start,p.start+p.span);d.highlight&&N.every(R=>R.highlight===d.highlight)&&(L.style.backgroundColor=Z(d.highlight),!r.header_font_color&&!r.theme?.header_text&&Bt(L,{policy:"cell"}));let O=b("span",{class:"et-th-inner"}),C=qt(d,r,p.label);O.append(ws(C)),E&&O.append(b("span",{class:"et-th-info",role:"img","aria-label":E},"\u24D8")),h&&O.append(b("span",{class:"et-sort-arrow"},m==="asc"?"\u25B2":"\u25BC")),L.append(O),r.sortable!==!1&&(L.tabIndex=0,L.addEventListener("click",()=>o(d.name)),L.addEventListener("keydown",R=>{R.key!=="Enter"&&R.key!==" "||(R.preventDefault(),o(d.name))}),L.dataset.column=d.name),E&&s?.(L,d),u.append(L)}return i.append(u),i}var Vl="http://www.w3.org/2000/svg",Sr={circle:"M0,-50 A50,50 0 1,1 0,50 A50,50 0 1,1 0,-50 Z",square:"M-50,-50 H50 V50 H-50 Z",rounded:"M-30,-50 H30 Q50,-50 50,-30 V30 Q50,50 30,50 H-30 Q-50,50 -50,30 V-30 Q-50,-50 -30,-50 Z",triangle:"M0,-50 L43.3012701892,25 H-43.3012701892 Z",diamond:"M0,-50 L37.5,0 0,50 -37.5,0 Z",cross:"M-17,-50 H17 V-17 H50 V17 H17 V50 H-17 V17 H-50 V-17 H-17 Z",star:"M0,-50 L11.8,-16.2 47.6,-15.5 19,6.2 29.4,40.5 0,20 -29.4,40.5 -19,6.2 -47.6,-15.5 -11.8,-16.2 Z",bar:"M-10,-50 H10 V50 H-10 Z"},F0=Object.keys(Sr),vr=(t="circle")=>Object.hasOwn(Sr,t)?Sr[t]:Sr.circle,vs=(t,e=0)=>t==="circle"?0:(e%360+360)%360;function Pt(t,e={}){let r=document.createElementNS(Vl,t);for(let[n,o]of Object.entries(e))r.setAttribute(n,String(o));return r}function ql(t){return t===!1?"none":typeof t=="string"?Z(t)||t:"var(--et-marker-outline, color-mix(in srgb, Canvas 60%, transparent))"}function Ie({shape:t="circle",angle:e=0,color:r="currentColor",outline:n,hollow:o=!1}={}){let s=Pt("svg",{viewBox:"-50 -50 100 100","aria-hidden":"true",class:"et-marker-svg"});return s.append(Pt("path",{d:vr(t),fill:o?"none":r,stroke:o&&n!==!1&&typeof n!="string"?r:ql(n),"stroke-width":1,"vector-effect":"non-scaling-stroke","stroke-linejoin":"round",transform:`rotate(${vs(t,e)})`})),s}function Fe(t,{shape:e="circle",angle:r=0,color:n,outline:o}={}){let s=vs(e,r);return t.dataset.shape=e,t.dataset.angle=String(s),t.style.backgroundColor=n,o===!1?t.style.boxShadow="none":typeof o=="string"&&(t.style.boxShadow=`0 0 0 1px ${Z(o)||o}`),s&&(t.style.transform=`${t.style.transform} rotate(${s}deg)`),e!=="circle"&&(t.classList.add("et-shaped-marker"),t.style.backgroundColor="transparent",t.style.color=n,t.style.boxShadow="none",t.style.borderRadius="0",t.append(Ie({shape:e,color:"currentColor",outline:o}))),t}var Ss={"\u25CF":["circle",!1],"\u25CB":["circle",!0],"\u25A0":["square",!1],"\u25A1":["square",!0],"\u25B2":["triangle",!1],"\u25B3":["triangle",!0],"\u25BC":["triangle",!1,180],"\u25C6":["diamond",!1],"\u25C7":["diamond",!0],"\u2605":["star",!1],"\u2606":["star",!0],"+":["cross",!1],"\u271A":["cross",!1],"\xD7":["cross",!1,45],"\u2715":["cross",!1,45]};function Cs(t,e){let r=e?t.symbol||"\u25CF":t.empty??t.symbol??"\u25CF",n=Object.hasOwn(Ss,r)?Ss[r]:null;return t.shape?{shape:t.shape,angle:t.angle||0,hollow:!e&&!!(t.empty&&n?.[1])}:n?{shape:n[0],hollow:n[1],angle:(t.angle||0)+(n[2]||0)}:null}var As="var(--et-accent, #2563eb)";function Tn(t){let e=t.sources||[],r=br(e.length,t.palette);return e.map((n,o)=>{let s={...t,source:n,color:t.color??r[o]};return gr(s,i=>Tt(i,t)),s})}function vt(t,e,r=As,n=Number(e?.[t.source])<0){if(n){let o=Z(t.color_negative)||Tt(e?.[t.color_negative_column],t);if(o)return o}if(t.color_column&&e){let o=Tt(e[t.color_column],t);if(o)return o}return Z(t.color)||r}function Cr(t,e=[],r={}){let n=t.legend;return(t.encodings||[]).flatMap(s=>s.kind==="strip"?Object.entries(s.colors||{}).map(([i,a])=>({key:i,color:Z(a)||As,enc:s})):s.sources?Tn(s).map(i=>({key:i.source,color:vt(i),enc:i})):[{key:s.source,color:vt(s),enc:s}]).map((s,i)=>{let a=e.find(c=>c!==t&&c.name===s.key),l=s.enc.names?.[s.key]??(s.enc.kind==="strip"?s.key:qt(a||{name:s.key},r));return{...s,name:l,label:Array.isArray(n)&&i<n.length?n[i]:n&&typeof n=="object"&&Object.hasOwn(n,s.key)?n[s.key]:l}})}function $s(t,e=!1){let r=e?`${t.label} (negative)`:t.label,n=t.enc.kind,o=e?vt(t.enc,null,t.color,!0):t.color,s=b("span",{class:`et-legend-swatch et-legend-swatch-${n}`,"aria-hidden":"true",style:{backgroundColor:o}});return(n==="point"||n==="points")&&Fe(s,{...t.enc,color:o}),b("li",{class:"et-legend-item"},[s,b("span",{class:"et-legend-label"},r)])}function Ns(t,e,r){let n=t.filter(c=>c.legend!==!1&&c.legend!=null&&c.encodings?.length);if(!n.length)return null;let o=n.some(c=>c.legend_options?.outline),s=b("aside",{class:`et-legends${o?" et-legends-outlined":""}`,"aria-label":"Legend"}),i=b("div",{class:"et-legend-groups"}),a=[],{leaves:l}=ze(t);for(let c of n){let f=t.indexOf(c),u=l.find(m=>f>=m.start&&f<m.start+m.span),p=qt(c,r,u?.label),d=b("div",{class:"et-legend-group",role:"group","aria-label":p},b("div",{class:"et-legend-column"},p)),h=b("ul",{class:"et-legend-items",role:"list"});for(let m of Cr(c,e,r))m.label!=null&&(h.append($s(m)),m.enc.color_negative&&h.append($s(m,!0)));h.childElementCount&&(d.append(h),i.append(d),a.push({group:d,column:c}))}if(!i.childElementCount)return null;for(let{group:c,column:f}of a)(f.legend_options?.column_names??i.childElementCount>1)||c.querySelector(".et-legend-column").remove();return s.append(i),s}function Ul(t,e,r){if(t==null)return e==null?0:1;if(e==null)return-1;if(r==="number"){let n=Number(t),o=Number(e);if(!isNaN(n)&&!isNaN(o))return n-o}return t instanceof Date||e instanceof Date?new Date(t)-new Date(e):typeof t=="string"&&typeof e=="string"?t.localeCompare(e,void 0,{numeric:!0,sensitivity:"base"}):t<e?-1:t>e?1:0}function Ls(t){if(t==null||typeof t=="boolean")return null;let e=String(t);if(e.trim()===""||isNaN(Number(e)))return null;let r=e.indexOf(".");return r===-1?0:e.length-r-1}var Es=["num","usd","eur","gbp","aud","cad","cny","jpy","inr","krw","ngn","sek","pct"];function Ts(t,e){let r=String(t||"num"),n=/^([a-z]+)(\d+)$/.exec(r);if(n&&Es.includes(n[1])||!Es.includes(r))return r;let o=r==="pct"?Math.max(0,e-2):e;return r+Math.min(o,r==="pct"?3:4)}function Pn(t,e){let r=new Set(e);for(let n of t)n.hide&&r.add(n.name);return r}function Ar(t,e){if(!t.some(o=>o.render_type&&o.render_type!=="cell_data"))return t;let n=new Set;for(let o of t){let s=o.__group_key;(o.render_type==="row_subtotal"||o.render_type==="row_total")&&s&&e(s)&&n.add(s)}return t.filter(o=>!(o.__ancestors||[]).some(i=>n.has(i)))}function $r(t,e,r,n){let o=r.trim().toLowerCase();if(!o)return t;let s=e.filter(l=>!n.has(l.name)),i=l=>s.some(c=>{let f=l[c.name];return f!=null&&String(f).toLowerCase().includes(o)}),a=new Set;for(let l of t){if(l.render_type&&l.render_type!=="cell_data"){l.render_type==="row_total"&&a.add(l.__group_key);continue}if(i(l))for(let c of l.__ancestors||[])a.add(c)}return t.filter(l=>l.render_type==="row_total"?!0:(l.render_type==="row_subtotal"||l.render_type==="row_section")&&a.has(l.__group_key)||i(l))}function Nr(t,e,r){if(!r)return t;let o=e.find(u=>u.name===r.column)?.sort_by||r.column,s=e.find(u=>u.name===o)?.type,i=r.direction==="asc"?1:-1,a=t.some(u=>u.render_type&&u.render_type!=="cell_data"),l=(u,p)=>{let d=u[o],h=p[o],m=Ul(d,h,s);return d==null||h===null||h===void 0?m:i*m};if(!a)return[...t].sort(l);let c=new Map;for(let u of t){if(u.render_type&&u.render_type!=="cell_data")continue;let p=u.__parent_key??"__root__";c.has(p)||c.set(p,[]),c.get(p).push(u)}for(let u of c.values())u.sort(l);let f=[];for(let u of t)if(u.render_type&&u.render_type!=="cell_data")f.push(u);else{let p=u.__parent_key??"__root__";f.push(c.get(p).shift())}return f}function Ps(t,e,r,n,o=t.some(s=>s.render_type&&s.render_type!=="cell_data")){let s=n,i=t.some(u=>!u.__row_builder&&(u.render_type==="row_subtotal"||u.render_type==="row_total"));if(!e||e==="all"||e<=0||i||s.collapsible)return{rows:t,pageCount:1,page:0,total:t.length,start:0};let a=t.length,l=Math.max(1,Math.ceil(a/e)),c=Math.min(Math.max(0,r),l-1),f=c*e;return{rows:t.slice(f,f+e),pageCount:l,page:c,total:a,start:f}}function Os(t,e){let r=e.filter(o=>!o.render_type||o.render_type==="cell_data"),n=new Map;for(let o of t){let s=null,i=null,a=0,l=0,c=0,f=0,u=0,p=new Set;for(let d of r){let h=d[o.name];if(h==null){c+=1;continue}if(p.add(typeof h=="object"?JSON.stringify(h):String(h)),o.type==="number"){let m=Number(h);!Number.isNaN(m)&&Number.isFinite(m)&&((s===null||m<s)&&(s=m),(i===null||m>i)&&(i=m),a+=m,l+=1)}else o.type==="boolean"&&(h===!0?f+=1:h===!1&&(u+=1))}n.set(o.name,{min:s,max:i,avg:l?a/l:null,nulls:c,distinct:p.size,trues:f,falses:u})}return n}function Rs(t,e,r){let n=new Array(t.length).fill(1);return t.forEach((o,s)=>{if(o.render_type!=="row_subtotal")return;let i=o.__level??e,a=1;if(r)for(let l=s+1;l<t.length&&(t[l].__level??e)>i;l++)a++;else for(let l=s-1;l>=0&&(t[l].__level??e)>i;l--)a++;n[s]=a}),n}function Er(t,e,r=0){if(!t||!e.section_indent)return;let n=r>0?` + ${r} * (var(--et-section-chevron-width, 0.75em) + var(--et-section-toggle-gap, 0.3em))`:"";return`calc(0.25rem + ${t*Math.max(0,Number(e.section_indent))}rem${n})`}function Ds(t,e,r){if(e>=r.dimCount)return 0;let n=t.__level??0,o=t.render_type||"cell_data";return o==="cell_data"?e===r.dimCount-1?0:2:o==="row_subtotal"&&e<n-1?2:0}function je(t,e){let r=e.row_shading;if(!r)return!1;let n=1,o=1;return Array.isArray(r)?(n=Math.max(1,Number(r[0])||1),o=Math.max(1,Number(r[1])||n)):typeof r=="number"&&(n=Math.max(1,r),o=n),t%(n+o)>=o}function Bs(t,e,r){if(!e||!r||!r.length||r[0].render_type==="row_section"||r[0].render_type==="row_total")return null;for(let n=e-1;n>=0;n-=1){let o=t[n];if(o.render_type==="row_section"){if(r[0].__parent_key&&r[0].__parent_key!==o.__group_key)return null;let s=o.__label;return s==null||s===""?null:{...o,__label:`${s} (cont.)`}}if(o.render_type==="row_total")break}return null}function ne(t,e){if(!Array.isArray(t))return[];let r=e.x,n=e.y,o=[];return t.forEach((s,i)=>{if(s==null){o.push([i,null,s]);return}let a=i,l;if(Array.isArray(s))a=s[0],l=bt(s[1]);else if(typeof s=="object"){let c=Object.keys(s),f=n||["y","value"].find(p=>p in s)||c.find(p=>zs(s[p])),u=r||["x","date"].find(p=>p in s)||c.find(p=>p!==f&&p!=="color"&&!zs(s[p]));a=u?s[u]:i,l=bt(f?s[f]:null)}else l=bt(s);o.push([a,l,s])}),e.type!=="change"||!e.delta?o:o.map(([s,i,a],l)=>{let c=o[l-1]?.[1];return[s,i==null||c==null?null:bt(i-c),a]})}function zs(t){return typeof t=="number"?Number.isFinite(t):typeof t=="string"?t.trim()!==""&&!isNaN(Number(t)):!1}function Kl(t,e){if(t.encodings?.length)return pr(t,e);let r=1/0,n=-1/0,o=s=>{let i=bt(s);i!=null&&(r=Math.min(r,i),n=Math.max(n,i))};for(let s of e)if(!(s.render_type&&s.render_type!=="cell_data"))if(t.viz==="sparkline")for(let[,i]of ne(s[t.name],t.sparkline_options||{}))o(i);else o(s[t.color_options?.scale_column||t.name]);return t.viz==="sparkline"&&r!==1/0&&o(t.sparkline_options?.reference),r===1/0?null:{min:r,max:n}}function Is(t,e,r){let n=new Map;for(let o of t){if(!o.domain)continue;let s=typeof o.domain=="string"?{name:o.domain}:o.domain;n.has(s.name)||n.set(s.name,{spec:{...s},members:[]});let i=n.get(s.name);Object.assign(i.spec,s),i.members.push(o)}for(let{spec:o,members:s}of n.values()){let i=1/0,a=-1/0,l=!1,c=!1;for(let u of s){let p=Kl(u,e);p&&(i=Math.min(i,p.min),a=Math.max(a,p.max));let d=u.encodings||[];c||=u.bar_options?.center||d.some(h=>h.center||h.side||h.diverge_at),l||=u.viz==="bar"||d.some(h=>["bar","stacked_bar"].includes(h.kind)&&!h.fit_to_data)||["bar","area"].includes(u.sparkline_options?.type)&&!u.sparkline_options.fit_to_data}i===1/0&&(i=0,a=1),o.bounds?[i,a]=o.bounds:((o.include_zero??l)&&(i=Math.min(i,0),a=Math.max(a,0)),o.neutral_range&&(i=Math.min(i,o.neutral_range[0]),a=Math.max(a,o.neutral_range[1]))),c&&(a=Math.max(Math.abs(i),Math.abs(a)),i=-a);let f={min:i,max:a,shared:!0};for(let u of s)r.set(u,f),r.set(u.name,f)}return r}function Fs(t,e=0){let r=/^(-?)(\d+)(?:\.(\d*))?(?:e([+-]?\d+))?$/i.exec(String(t));if(!r)return String(t);let n=r[2]+(r[3]||""),o=r[2].length+Number(r[4]||0)+e,s=(o<=0?"0":n.slice(0,o).padEnd(o,"0")).replace(/^0+(?=\d)/,""),i=(o<0?"0".repeat(-o)+n:n.slice(Math.max(0,o))).replace(/0+$/,"");return`${r[1]}${s.replace(/\B(?=(\d{3})+(?!\d))/g,",")}${i?`.${i}`:""}`}function Ht(t,e,r={}){if(t==null)return r.null_text??"\u2013";if(typeof t!="number"||!Number.isFinite(t))return String(t);let n=Ke[e]||e||"";if(qe(n)||e==="id"||r.relative||["date","datetime","time"].includes(r.type))return pt(t,e,{type:r.type,relative:r.relative,fallback:String(t)});let o=ao(/^([a-z]{3})(?:\d[kmbt]?)?$/.exec(e||"")?.[1]),s=n.split(";")[0],i=s.replace(/"[^"\n]*"/g,""),a=/^pct\d?$/.test(e||"")||i.includes("%"),l=Fs(Math.abs(t),a?2:0),c=s.search(/[0#?]/),f=[...s.matchAll(/"([^"\n]*)"/g)].filter(h=>!/^[kmbt]$/i.test(h[1])),u=o||(i.match(/[$€£¥₹₩₦]/)?.[0]??"")+f.filter(h=>h.index<c).map(h=>h[1]).join(""),p=a?"%":e==="bytes"?" bytes":/^duration/.test(e||"")?" seconds":o?"":f.filter(h=>h.index>c).map(h=>h[1]).join("");/^mult\d?$/.test(e||"")&&(p="x");let d=`${u}${l}${p}`;return t<0?r.bracket_negatives?`(${d})`:`-${d}`:d}function oe(t){return[t.name?`${t.name}${t.value?`: ${t.value}`:""}`:t.value,...(t.details||[]).map(e=>`${e.name}: ${e.value}`)].filter(Boolean).join(`
`)}function pe(t,e,r=e.source,n={}){let o=Cr(t,n.columns,n.options),s=o.find(i=>i.key===r&&i.enc===e)??o.find(i=>i.key===r&&i.enc.kind===e.kind);return s?.label??s?.name??e.names?.[r]??qt({name:r},n.options)}function Zt(t,e,r,{key:n=e.source,value:o=r[n],total:s,context:i={}}={}){let a=i.formatCode??t.fmt,l=f=>Ht(f,a,t),c={name:pe(t,e,n,i),value:l(o),color:vt(e,r),details:[]};if(["point","points"].includes(e.kind)&&o!=null&&Number.isFinite(Number(o))&&(c.xValue=Number(o)),e.kind==="stacked_bar"){let f=s?Number(o)/s:0,u=e.label?.share||t.scale?.normalize==="percent";c.value=u?pt(f,e.label?.format||"pct1"):l(o),c.details=[{name:u?"Value":"Share",value:u?l(o):pt(f,"pct1")},{name:"Total",value:l(s)}]}else if(e.kind==="range"){let f=r[e.high];c.value="",c.color=vt(e,r,void 0,Number(f)<Number(o)),c.details=[{name:pe(t,e,e.source,i),value:l(o)},{name:pe(t,e,e.high,i),value:l(f)},{name:"Change",value:l(Number(f)-Number(o))}]}else if(e.kind==="boxplot"){let f={minimum:e.whisker==="iqr"?"Lower whisker":"Minimum",q1:"Lower quartile",median:"Median",q3:"Upper quartile",maximum:e.whisker==="iqr"?"Upper whisker":"Maximum"};c.value="",c.details=Object.entries(f).map(([u,p])=>({name:p,value:l(r[e.parts?.[u]])}))}return c}function se(t,e,r,n,o,s=[]){let i=n&&typeof n=="object"&&!Array.isArray(n)?Object.entries(n).filter(([a,l])=>!s.includes(a)&&a!=="color"&&l!=null&&typeof l!="object").map(([a,l])=>({name:qt({name:a}),value:typeof l=="number"?Fs(l):String(l)})):[];return{name:String(t??"Value"),value:Ht(e,r),color:o,details:i}}var On=new WeakMap;function Gs(t){return On.get(t)||t}function Wl(t,e=1){let r=f=>`${f.shape||"circle"}:${f.angle||0}`,n=[...t].sort((f,u)=>r(f).localeCompare(r(u))||f.x-u.x||f.y-u.y),o=[],s=[],i,a,l,c=()=>{s.length>1&&new Set(s.map(f=>f.color)).size>1&&o.push(s)};for(let f of n){let u=s[0];(!f.opaque||!u||r(f)!==r(u)||Math.abs(f.width-u.width)>.01||Math.abs(f.height-u.height)>.01||Math.hypot(f.x-i,Math.max(l,f.y)-Math.min(a,f.y))>e)&&(c(),s=[],i=f.x,a=f.y,l=f.y),f.opaque&&(s.push(f),a=Math.min(a,f.y),l=Math.max(l,f.y))}return c(),o}var Hs="http://www.w3.org/2000/svg";function js(t,e,r){let n=document.createElementNS(Hs,"path");n.setAttribute("d",e);for(let[o,s]of Object.entries(r))n.setAttribute(o,s);t.append(n)}function Yl(t,e){let r=document.createElementNS(Hs,"svg");r.setAttribute("viewBox",`0 0 ${e} ${e}`),r.setAttribute("aria-hidden","true");let n=e/2,o=(s,i)=>`${n+Math.sin(s)*i},${n-Math.cos(s)*i}`;return t.forEach((s,i)=>{let a=i/t.length*2*Math.PI,l=(i+1)/t.length*2*Math.PI,c=f=>`M${o(a,f)} A${f},${f} 0 0 1 ${o(l,f)}`;js(r,`M${n},${n} L${o(a,n)} A${n},${n} 0 0 1 ${o(l,n)} Z`,{fill:s.color}),s.outline&&js(r,c(n+.5),{fill:"none",stroke:s.outline,"stroke-width":"1"})}),r}function Zl(t,e,r,n){if(t==="bar"){let a=r===0?-150:-50+r*100/n,l=r===n-1?150:-50+(r+1)*100/n;return{d:`M-150,${a} H150 V${l} H-150 Z`,transform:`rotate(${e})`}}let o=r/n*2*Math.PI,s=(r+1)/n*2*Math.PI,i=a=>`${Math.sin(a)*150},${-Math.cos(a)*150}`;return{d:`M0,0 L${i(o)} A150,150 0 ${s-o>Math.PI?1:0},1 ${i(s)} Z`}}function Jl(t,e){if(!t[0].shape||t[0].shape==="circle")return Yl(t,e);let r=Pt("svg",{viewBox:"-50 -50 100 100","aria-hidden":"true"}),n=Pt("defs"),o=Symbol.for("evidential.markerClusterCounter"),s=`et-marker-cluster-${document[o]=(document[o]||0)+1}`,i=t[0].shape,a=Pt("clipPath",{id:s});return a.append(Pt("path",{d:vr(i),transform:`rotate(${t[0].angle||0})`})),n.append(a),r.append(n),t.forEach((l,c)=>{let f=Zl(i,t[0].angle||0,c,t.length),u=Pt("clipPath",{id:`${s}-${c}`});u.append(Pt("path",f)),n.append(u);let p=Pt("g",{"clip-path":`url(#${s})`});if(p.append(Pt("path",{...f,fill:l.color})),r.append(p),l.outline){let d=Pt("g",{"clip-path":`url(#${s}-${c})`});d.append(Pt("path",{d:vr(i),fill:"none",stroke:l.outline,"stroke-width":1,"vector-effect":"non-scaling-stroke","stroke-linejoin":"round",transform:`rotate(${t[0].angle||0})`})),r.append(d)}}),r}function Lr(t){let e=[...t.querySelectorAll(".et-marks")];for(let o of e){for(let s of o.querySelectorAll(".et-point-composite"))s.remove();for(let s of o.querySelectorAll(".et-mark-point"))s.classList.remove("et-point-combined-member"),On.delete(s)}let r=t.ownerDocument.defaultView,n=e.map(o=>{let s=[...o.querySelectorAll(".et-mark-point")].map(i=>{let a=i.getBoundingClientRect(),l=r.getComputedStyle(i),c=i.dataset.shape||"circle",f=c==="circle"?l.backgroundColor:l.color,u=i.querySelector(".et-marker-svg path"),p=a.width>0&&a.height>0&&Number(l.opacity||1)===1&&l.visibility!=="hidden"&&ot.valid(f)&&ot(f).alpha()===1;return{node:i,x:a.left+a.width/2,y:a.top+a.height/2,shape:c,angle:Number(i.dataset.angle||0),width:a.width,height:a.height,color:p?ot(f).hex():f,opaque:p,outline:u?(r.getComputedStyle(u).stroke||u.getAttribute("stroke"))==="none"?null:r.getComputedStyle(u).stroke||u.getAttribute("stroke"):l.boxShadow==="none"?null:l.boxShadow.match(/(?:rgba?|color)\([^)]*\)/)?.[0]}});return Wl(s)});for(let o of n)for(let s of o){s.sort((l,c)=>l.node.compareDocumentPosition(c.node)&4?-1:1);let i=s[0].node,a=b("div",{class:"et-mark et-point-composite","aria-hidden":"true","data-point-count":s.length,style:{top:i.style.top,bottom:i.style.bottom,transform:i.style.transform.replace(/ rotate\([^)]*\)/g,""),left:`${s.reduce((l,c)=>l+parseFloat(c.node.style.left),0)/s.length}%`,width:i.style.width,height:i.style.height}},Jl(s,parseFloat(i.style.width)));for(let l of s)l.node.classList.add("et-point-combined-member"),On.set(l.node,a);s.at(-1).node.after(a)}}var Ct=new WeakMap,Tr=new WeakMap,Vs=10,Xl=0;function wt(t,e,{priority:r=1,navigate:n=!0}={}){if(Ct.set(t,{data:e,priority:r,navigate:n}),t.setAttribute("data-et-tooltip",""),t.namespaceURI==="http://www.w3.org/2000/svg"){let o=t.querySelector(":scope > title");o||(o=document.createElementNS(t.namespaceURI,"title"),t.append(o)),o.textContent=oe(e)}else t.title=oe(e);return t}function qs(t){return Ct.get(t)?.data}function Us(t,e,r){wt(t,{value:String(e.info)},{priority:0,navigate:!1}),t.dataset.etTooltipCell="",t.tabIndex=0,Tr.set(t,Ks(e,r))}function Ks(t,e,r=!1){let n={...e.tooltips,...t.tooltip_options};return{delay:(r?n.delay??0:n.text_delay??.8)*1e3,maxEntries:n.max_entries??Vs}}function Ws(t,e,r,n,o){if(Ct.delete(t),delete t.dataset.etTooltipCell,t.removeAttribute("tabindex"),!t.textContent&&!t.querySelector("[data-et-tooltip]"))return;if(e.tooltip===!1||typeof e.tooltip=="string"){for(let d of t.querySelectorAll("[data-et-tooltip]"))Ct.delete(d),d.removeAttribute("data-et-tooltip"),d.removeAttribute("title"),d.querySelector(":scope > title")?.remove();for(let d of t.querySelectorAll("[data-mark-label][title]"))d.removeAttribute("title");if(e.tooltip===!1)return}let s=[...t.querySelectorAll("[data-et-tooltip]")].filter(d=>Ct.get(d)?.navigate),i=typeof e.tooltip=="string"?e.tooltip.startsWith("@")?r[e.tooltip.slice(1)]:e.tooltip:null;if(typeof e.tooltip=="string"&&i==null)return;let a=r[e.name],l=typeof a=="number"&&Number.isFinite(a),c=typeof a=="string"&&!e.html&&!e.markdown;if(!s.length&&!l&&!c&&i==null)return;let f=i!=null?{value:String(i)}:{name:qt(e,n),value:s.length?"":Ht(a,o??e.fmt,e)};Ct.set(t,{data:f,priority:0,navigate:!1}),t.dataset.etTooltipCell="";let u=!!t.querySelector(".et-marks, .et-sparkline, .et-bar-cell, .et-symbols, .et-delta");Tr.set(t,Ks(e,n,u));let p=s.length?s.map(d=>oe(Ct.get(d).data)).join(`
`):oe(f);t.setAttribute("aria-label",p),(s.length||i!=null)&&(t.tabIndex=0);for(let d of t.querySelectorAll(".et-marks, .et-sparkline")){d.setAttribute("role","group");let h=d.classList.contains("et-sparkline-change")?d.getAttribute("aria-label"):null;d.setAttribute("aria-label",h?`${h}
${p}`:p)}}function Ys(t){return[...t.querySelectorAll("[data-et-tooltip]")].filter(e=>Ct.has(e))}function Rn(t,e,r,n){let o=n?.closest?.("[data-mark-label][data-et-tooltip]");if(o&&Ct.has(o))return[o];let s=Ys(t),i=t.querySelector(".et-sparkline");if(i){let u=i.getBoundingClientRect();if(e<u.left||e>u.right||r<u.top||r>u.bottom)return[];let p=s.filter(h=>h.dataset.sparklineObservation||h.tagName.toLowerCase()==="circle"),d=p.length?p:s;return d.length?[d.reduce((h,m)=>{let y=g=>{let w=g.getBoundingClientRect();return w.left+w.width/2};return Math.abs(y(m)-e)<Math.abs(y(h)-e)?m:h})]:[]}let a=s.filter(u=>{let p=u.getBoundingClientRect(),d=Ct.get(u).priority>=3?5:0;return p.width>0&&p.height>0&&e>=p.left-d&&e<=p.right+d&&r>=p.top-d&&r<=p.bottom+d}),l=Math.max(-1,...a.map(u=>Ct.get(u).priority)),c=a.filter(u=>Ct.get(u).priority===l);if(c.length&&c.every(u=>u.matches(".et-mark-stack-seg, .et-strip-seg, .et-strip-run")))return[c.find(u=>e<u.getBoundingClientRect().right)||c.at(-1)];if(c.length)return c;let f=n?.closest?.("[data-et-tooltip]");return f&&t.contains(f)&&Ct.has(f)?[f]:s.length?[]:[t]}var Pr=class{constructor(e){this.root=e,this.view=e.ownerDocument.defaultView,this.abort=new this.view.AbortController,this.popup=b("div",{class:"et-tooltip",role:"tooltip",id:`et-tooltip-${++Xl}`,popover:"manual"}),this.popup.hidden=!0,e.append(this.popup);let r=(n,o,s,i=!1)=>n.addEventListener(o,s,{signal:this.abort.signal,capture:i});r(e,"pointermove",n=>{if(n.pointerType==="touch")return;if(this.popup.contains(n.target)){this.cancelHide();return}let o=n.target.closest?.("[data-et-tooltip-cell]");if(!o){this.scheduleHide();return}let s=Rn(o,n.clientX,n.clientY,n.target);if(!s.length){this.scheduleHide();return}this.hover(s,o,n.clientX,n.clientY)}),r(e,"pointerleave",n=>{n.pointerType!=="touch"&&this.scheduleHide()}),r(this.popup,"pointerenter",()=>this.cancelHide()),r(this.popup,"pointerleave",n=>{n.pointerType!=="touch"&&this.scheduleHide()}),r(e,"pointerdown",()=>{this.touchInspection=null,clearTimeout(this.touchTimer)}),r(e,"pointerup",n=>{if(n.pointerType!=="touch")return;let o=n.target.closest?.("[data-et-tooltip-cell]");if(!o){this.hide();return}let s=this.values(Rn(o,n.clientX,n.clientY,n.target),o,n.clientX,n.clientY);this.touchInspection={data:s,x:n.clientX,y:n.clientY}}),r(e,"click",()=>{let n=this.touchInspection;this.touchInspection=null,n&&(clearTimeout(this.touchTimer),this.touchTimer=setTimeout(()=>{this.root.isConnected&&this.showData(n.data,this.root,n.x,n.y)},0))}),r(e,"focusin",n=>{let o=n.target.closest?.("[data-et-tooltip-cell]");n.target===o&&(this.keyboardCell=o,this.index=0,this.inspectKeyboard())}),r(e,"focusout",()=>{this.keyboardCell=null,this.hide()}),r(e,"keydown",n=>{if(n.key==="Escape"&&(!this.popup.hidden||this.pending)){n.preventDefault(),n.stopPropagation(),this.hide();return}if(!this.keyboardCell||!["ArrowLeft","ArrowRight","Home","End"].includes(n.key))return;let o=this.keyboardNodes().length;this.index=n.key==="Home"?0:n.key==="End"?o-1:(this.index+(n.key==="ArrowLeft"?-1:1)+o)%o,n.preventDefault(),n.stopPropagation(),this.inspectKeyboard()}),r(e,"scroll",()=>this.hide(),!0),r(this.view,"resize",()=>this.hide()),r(this.view,"scroll",()=>this.hide(),!0),r(e.ownerDocument,"pointerdown",n=>{n.composedPath().includes(e)||(this.touchInspection=null,clearTimeout(this.touchTimer),this.hide())}),r(e.ownerDocument,"keydown",n=>{n.key==="Escape"&&(!this.popup.hidden||this.pending)&&!n.composedPath().includes(e)&&(n.preventDefault(),this.hide())})}refresh(){this.hide(),this.keyboardCell=null;for(let e of this.root.querySelectorAll("[data-et-tooltip], .et-marks, [data-mark-label]"))e.removeAttribute("title"),e.querySelector(":scope > title")?.remove()}keyboardNodes(){let e=Ys(this.keyboardCell).filter(r=>Ct.get(r).navigate);return e.length?e:[this.keyboardCell]}inspectKeyboard(){let e=this.keyboardNodes()[this.index],r=e.getBoundingClientRect(),n=(Ct.get(e)?.priority||0)>=3?Rn(this.keyboardCell,r.left+r.width/2,r.top+r.height/2,e):[e],o=r.left+r.width/2,s=r.top+r.height/2;this.showData(this.values(n,this.keyboardCell,o,s,e),this.keyboardCell,o,r.bottom),this.active?.classList.remove("et-tooltip-active"),this.active=Gs(e),this.active.classList.add("et-tooltip-active")}values(e,r,n,o,s){let i=e.map((p,d)=>({node:p,index:d,...Ct.get(p)})).filter(p=>p.data),a=i.length>0&&i.every(p=>p.priority>=3),l=Tr.get(r)?.maxEntries??Vs;if(a&&i.length>l){for(let p of i){let d=p.node.getBoundingClientRect();n??=d.left+d.width/2,o??=d.top+d.height/2,p.distance=(d.left+d.width/2-n)**2+(d.top+d.height/2-o)**2}i.sort((p,d)=>p.distance-d.distance||+(d.node===s)-+(p.node===s))}let c=new Set,f=i.filter(p=>{let d=oe(p.data);return c.has(d)?!1:(c.add(d),!0)});return(a?f.slice(0,l):f).sort((p,d)=>(Number.isFinite(p.data.xValue)&&Number.isFinite(d.data.xValue)?p.data.xValue-d.data.xValue:0)||p.index-d.index).map(p=>p.data)}hover(e,r,n,o){this.cancelHide();let s=this.values(e,r,n,o),i=JSON.stringify(s),a=Tr.get(r)?.delay||0;if(!this.popup.hidden&&this.anchor===r){this.cancelPending(),this.showData(s,r,n,o);return}if(!a){this.cancelPending(),this.showData(s,r,n,o);return}if(this.pending?.cell===r&&this.pending.key===i){this.pending.x=n,this.pending.y=o;return}this.hide(),this.pending={cell:r,key:i,values:s,x:n,y:o},this.showTimer=setTimeout(()=>{let l=this.pending;this.pending=null,this.showTimer=null,l?.cell.isConnected&&this.showData(l.values,r,l.x,l.y)},a)}showData(e,r,n,o){if(this.cancelPending(),this.cancelHide(),!e.length){this.hide();return}let s=JSON.stringify(e);this.key!==s&&(this.popup.replaceChildren(...e.map(c=>b("div",{class:"et-tooltip-entry"},[c.color?b("span",{class:"et-tooltip-swatch","aria-hidden":"true",style:{backgroundColor:c.color}}):null,b("div",{class:"et-tooltip-content"},[c.name?b("span",{class:"et-tooltip-name"},`${c.name}${c.value?":":""}`):null,c.value?b("span",{class:"et-tooltip-value"},c.value):null,...(c.details||[]).map(f=>b("div",{class:"et-tooltip-detail"},[b("span",{},`${f.name}: `),b("span",{class:"et-tooltip-value"},f.value)]))])]))),this.key=s),this.anchor!==r&&this.anchor?.removeAttribute("aria-describedby"),this.anchor=r,r.setAttribute("aria-describedby",this.popup.id),this.popup.hidden=!1,this.popup.showPopover&&!this.popup.matches(":popover-open")&&this.popup.showPopover();let i=this.popup.getBoundingClientRect(),a=this.view.innerWidth,l=this.view.innerHeight;this.popup.style.left=`${Math.max(8,Math.min(n+12,a-i.width-8))}px`,this.popup.style.top=`${Math.max(8,Math.min(o+i.height+20>l?o-i.height-12:o+12,l-i.height-8))}px`}hide(){this.cancelPending(),this.cancelHide(),this.popup.hidePopover?.(),this.popup.hidden=!0,this.anchor?.removeAttribute("aria-describedby"),this.anchor=null,this.active?.classList.remove("et-tooltip-active"),this.active=null,this.key=null}scheduleHide(){this.cancelPending(),!this.hideTimer&&(this.hideTimer=setTimeout(()=>{this.hideTimer=null,this.hide()},120))}cancelHide(){clearTimeout(this.hideTimer),this.hideTimer=null}cancelPending(){clearTimeout(this.showTimer),this.showTimer=null,this.pending=null}destroy(){clearTimeout(this.touchTimer),this.cancelPending(),this.abort.abort(),this.hide(),this.popup.remove()}};function Dn(t,e=[0,0]){return t<e[0]?"down":t>e[1]?"up":"steady"}function Or(t,e,r="lch"){let n=t.steady||[0,0];if(!t.color_scale){let l={down:"var(--et-negative, #dc2626)",steady:"#b8bcc2",up:"var(--et-accent, #2563eb)"};return c=>Z(t.color)||l[Dn(c,n)]}let[o,s]=n;for(let l of e)l!=null&&Number.isFinite(l)&&(o=Math.min(o,l),s=Math.max(s,l));[o,s]=t.color_domain||[o,s];let i=Array.isArray(t.color_scale)?t.color_scale.map(Z):t.color_scale,a=Yt([],{colorPalette:i,min:0,max:1,mode:r});return l=>{let c=.5;return l<n[0]?c=o<n[0]?.5*(l-o)/(n[0]-o):0:l>n[1]&&(c=s>n[1]?.5+.5*(l-n[1])/(s-n[1]):1),fe(Math.max(0,Math.min(1,c)),a)}}function Zs(t,e,r){let n=e.width||64,o=e.height||18,s=Math.min(1.5,o/8),i=(o-2*s)/2,a=n/t.length,l=r||Or(e,t.map(p=>p[1])),c="http://www.w3.org/2000/svg",f=document.createElementNS(c,"svg");f.setAttribute("class","et-sparkline et-sparkline-change"),f.setAttribute("width",String(n)),f.setAttribute("height",String(o)),f.setAttribute("viewBox",`0 0 ${n} ${o}`),f.setAttribute("role","img");let u={up:0,steady:0,down:0,missing:0};return t.forEach(([,p])=>{p==null?u.missing++:u[Dn(p,e.steady)]++}),f.setAttribute("aria-label",`Changes: ${u.up} up, ${u.steady} steady, ${u.down} down, ${u.missing} missing`),t.forEach(([p,d,h],m)=>{if(d==null)return;let y=Dn(d,e.steady),g=document.createElementNS(c,"rect"),w=s+(y==="up"?0:y==="steady"?i/2:i);g.setAttribute("x",String((m+.15)*a)),g.setAttribute("y",String(w)),g.setAttribute("width",String(a*.7)),g.setAttribute("height",String(i)),g.setAttribute("rx",String(Math.min(.6,a*.35)));let E=Me(h,e)||l(d);g.setAttribute("fill",E),g.setAttribute("data-state",y);let L=se(p,d,e.y_fmt,h,E,[e.x,e.y,"x","y","value"]);L.details.push({name:"Change",value:y}),wt(g,L,{priority:2}),f.append(g)}),f}function Bn(t,e=[],r,n){let o=t.sparkline_options||{},s=t.color_options||{},i=typeof t.domain=="object"?t.domain:{},a=i.palette||s.color_scale||o.color_scale,l=a||Object.keys(s).length,c=s.min??o.color_domain?.[0],f=s.max??o.color_domain?.[1],u=o.type==="change";if(!l)return u?Or(o,[]):null;if(r?.shared){let h=xn({...i,midpoint:i.midpoint??s.midpoint},r,a||n,s.scale_mode),m=!i.neutral_range&&r.min===r.max;return Js(h,m,i.neutral_range?[r.min,...i.neutral_range,r.max]:void 0)}if(u&&!s.color_stops){let h=o.steady||[0,0],m=c??h[0],y=f??h[1];for(let g of e)c==null&&(m=Math.min(m,g)),f==null&&(y=Math.max(y,g));return Or({...o,color_scale:a||n||["#dbeafe","#1e40af"],color_domain:[m,y]},[],s.scale_mode)}let p=Yt(e,{colorPalette:a||n,colorStops:s.color_stops,min:c,max:f,midpoint:s.midpoint,mode:s.scale_mode});if(!p)return null;let d=!s.color_stops&&c==null&&f==null&&e.length&&e.every(h=>h===e[0]);return Js(p,d)}function Js(t,e,r){let n=o=>fe(e?(t.minValue+t.maxValue)/2:o,t);return n.breakpoints=r||(t.domain.length===t.colorPalette.length?t.domain:t.colorPalette.map((o,s)=>t.minValue+s/(t.colorPalette.length-1)*(t.maxValue-t.minValue))),n}function Xs(t,e,r,n){let o=new Map;for(let s of t){if(s.viz!=="sparkline")continue;let i=s.sparkline_options||{},a=s.color_options||{},l=[];if(!r?.get(s)?.shared&&!a.color_stops&&(a.color_scale||i.color_scale||Object.keys(a).length)&&!(i.color_domain||a.min!=null&&a.max!=null)){let f=1/0,u=-1/0;for(let p of e)if(!(p.render_type&&p.render_type!=="cell_data"))for(let[,d]of ne(p[s.name],i))d!=null&&(f=Math.min(f,d),u=Math.max(u,d));f!==1/0&&l.push(f,u)}let c=Bn(s,l,r?.get(s),n);c&&o.set(s,c)}return o}var Rr=class{constructor(){this.clear()}clear(){this.cache=null,this.visibility=null}get({rows:e,columns:r,options:n,search:o,hidden:s,sort:i,rowLayout:a}){let l=[e,r,n,o,JSON.stringify([...s].sort()),i?.column,i?.direction,a];if(this.cache&&l.every((g,w)=>Object.is(g,this.cache.key[w])))return this.cache.result;let c=Mr(r.filter(g=>!s.has(g.name)),n),f=$r(e,r,o,s),u=Nr(f,r,i),p=Is(r,u,us(c,u)),d=ds(c,u),h=new Map;if(n.align_decimals)for(let g of c){if(g.type!=="number"||g.align_decimals===!1)continue;let w=null;for(let E of u){let L=Ls(E[g.name]);L!==null&&(w=w===null?L:Math.max(w,L))}w!==null&&h.set(g.name,w)}let m=new Map;for(let g of c)if((g.viz==="color"||g.viz==="chip")&&p.has(g.name)){let w=ps(g,p.get(g)||p.get(g.name),n.color_scale);m.set(g,w),m.set(g.name,w)}let y={columns:c,sourceColumns:r,sorted:u,ranges:p,formatRanges:d,decimals:h,colorScales:m,sparklineScales:Xs(c,u,p,n.color_scale),sourceRows:e,rowLayout:a,hasGroups:!!a?.legacy||e.some(g=>g.render_type&&g.render_type!=="cell_data"),dimCount:(a?.legacy||[]).reduce((g,w)=>Math.max(g,w.row?.__level||0),e.reduce((g,w)=>Math.max(g,w.__level??0),0)),stats:n.column_stats?Os(c,e):null,displayProjection:a?.version&&!a.legacy?new Be(a,e,u):null};return this.cache={key:l,result:y},this.visibility=null,y}visible(e,r,n){if(this.visibility?.result===e&&this.visibility.groupVersion===r)return this.visibility;let o=e.rowLayout?.legacy?xr(e.rowLayout,e.sourceRows,e.sorted,n):Ar(e.sorted,n);return this.visibility={result:e,groupVersion:r,rows:o,insetGroups:new Set(o.filter(s=>s.render_type==="row_section"&&s.__align!=="center").map(s=>s.__group_key)),hasGroups:o.some(s=>s.render_type&&s.render_type!=="cell_data")},this.visibility}};function Ql(t){return 700+-600*(Math.min(Math.max(t-700,0),2300)/2300)}var Dr=class{constructor(e){this.advance=e,this.hold=null,this.fired=!1,this.onPointerUp=()=>this.stop()}consumeClick(){let e=this.fired;return this.fired=!1,e}start(e){this.stop(),this.fired=!1,this.hold={direction:e,start:performance.now(),timer:null},window.addEventListener("pointerup",this.onPointerUp),window.addEventListener("pointercancel",this.onPointerUp),window.addEventListener("blur",this.onPointerUp),this.hold.timer=setTimeout(()=>this.step(),700)}stop(){this.hold?.timer&&clearTimeout(this.hold.timer),this.hold=null,window.removeEventListener("pointerup",this.onPointerUp),window.removeEventListener("pointercancel",this.onPointerUp),window.removeEventListener("blur",this.onPointerUp)}step(){if(!this.hold)return;if(this.fired=!0,!this.advance(this.hold.direction)){this.stop();return}let r=Ql(performance.now()-this.hold.start);this.hold.timer=setTimeout(()=>this.step(),r)}};function Qs(t,e,r,n,o,s){let i=n.select?e[n.select]:void 0;if(n.select&&i!==void 0&&i!==null){let a=r!=null&&String(r)===String(i);t.classList.add("et-row-selectable"),t.tabIndex=0,t.dataset.selectKey=String(i),t.setAttribute("aria-selected",String(a)),a&&t.classList.add("et-row-selected");let l=c=>{c.target.closest&&c.target.closest("a, button, input, select, textarea")||(o.set("selected",a?null:i),o.save_changes(),c.type==="keydown"&&requestAnimationFrame(()=>{s(i)?.focus({preventScroll:!0})}))};t.addEventListener("click",l),t.addEventListener("keydown",c=>{c.target!==t||c.key!=="Enter"&&c.key!==" "||(c.preventDefault(),l(c))})}}var Br=class{constructor(e,r,n){Object.assign(this,{root:e,overlay:r,el:n}),this.loading=!1,this.shown=!1,this.showTimer=null,this.hideTimer=null,this.since=0}destroy(){clearTimeout(this.showTimer),clearTimeout(this.hideTimer)}set(e){if(this.loading=!!e,this.el.dataset.loading=String(this.loading),this.loading){if(this.hideTimer&&(clearTimeout(this.hideTimer),this.hideTimer=null),this.shown||this.showTimer)return;this.showTimer=setTimeout(()=>{this.showTimer=null,this.shown=!0,this.since=performance.now(),this.apply()},180)}else{if(this.showTimer){clearTimeout(this.showTimer),this.showTimer=null;return}if(!this.shown)return;let r=performance.now()-this.since,n=Math.max(120,600-r);this.hideTimer&&clearTimeout(this.hideTimer),this.hideTimer=setTimeout(()=>{this.hideTimer=null,this.shown=!1,this.apply()},n)}}apply(){this.root.classList.toggle("et-loading",this.shown),this.overlay.setAttribute("aria-hidden",String(!this.shown)),this.el.dataset.loading=String(this.loading),this.el.dataset.loadingShown=String(this.shown)}};var zr=class{constructor({root:e,dialog:r,button:n,placeholder:o,scroller:s,getOptions:i,rerender:a,resetBaseline:l,getPageSizeOverride:c,setPageSizeOverride:f,getPageMetrics:u,onExpand:p,onRestore:d,advancePage:h}){Object.assign(this,{root:e,dialog:r,button:n,placeholder:o,scroller:s,getOptions:i,rerender:a,resetBaseline:l,getPageSizeOverride:c,setPageSizeOverride:f,getPageMetrics:u,onExpand:p,onRestore:d,advancePage:h}),this.onKeyDown=m=>{if(this.destroyed||!this.expanded||!this.dialog?.open||!this.advancePage||m.defaultPrevented||m.altKey||m.ctrlKey||m.metaKey||m.shiftKey||m.isComposing||!["ArrowLeft","ArrowRight"].includes(m.key)||(m.composedPath?.()[0]||m.target)?.closest?.('input, textarea, select, [contenteditable]:not([contenteditable="false"]), [role="textbox"], [role="searchbox"], [role="combobox"], [role="slider"], [role="spinbutton"], [role="listbox"], [role="menu"], [role="menubar"], [role="tablist"], [role="radiogroup"]'))return;m.preventDefault(),m.stopPropagation(),this.advancePage(m.key==="ArrowRight"?"next":"prev")&&!this.dialog.contains(this.dialog.getRootNode().activeElement)&&this.dialog.focus({preventScroll:!0})},r&&(this.dialog.addEventListener("keydown",this.onKeyDown),this.dialog.addEventListener("close",()=>this.restore()),this.dialog.addEventListener("cancel",m=>{m.preventDefault(),this.close()}),this.backdropPress=!1,this.dialog.addEventListener("pointerdown",m=>{this.backdropPress=m.target===this.dialog}),this.dialog.addEventListener("click",m=>{let y=m.target===this.dialog&&this.backdropPress;this.backdropPress=!1,y&&this.close()})),this.expanded=!1,this.fitting=!1,this.destroyed=!1,this.frames=new Set,this.observer=new ResizeObserver(()=>{this.layoutPending||(this.layoutPending=!0,this.frame(()=>{this.layoutPending=!1,this.applyFrozenOffsets(),_r(this.root),Lr(this.root),this.expanded&&this.fit()}))}),this.observer.observe(s),e&&this.observer.observe(e)}observeTable(e){this.table!==e&&(this.table&&this.observer.unobserve(this.table),this.table=e,e&&this.observer.observe(e))}frame(e){let r=requestAnimationFrame(()=>{this.frames.delete(r),this.destroyed||e()});this.frames.add(r)}destroy(){this.destroyed=!0,this.expanded=!1,this.observer.disconnect(),this.dialog?.removeEventListener("keydown",this.onKeyDown);for(let e of this.frames)cancelAnimationFrame(e);this.frames.clear()}toggle(){if(this.expanded){this.close();return}this.expanded=!0,this.button.textContent="\xD7 Expand",this.button.title="Collapse table",this.button.setAttribute("aria-label","Collapse table"),this.button.setAttribute("aria-expanded","true"),this.dialog.append(this.root),this.dialog.showModal(),this.root.classList.add("et-expanded"),this.scroller.style.maxHeight="none",this.scroller.scrollTop=0,this.resetBaseline(),this.onExpand?.(),this.rerender(),this.dialog.focus({preventScroll:!0}),this.frame(()=>{this.applyFrozenOffsets(),this.fit()})}close(){this.dialog.open?this.dialog.close():this.restore()}restore(){this.destroyed||this.expanded&&(this.expanded=!1,this.setPageSizeOverride(null),this.placeholder.after(this.root),this.root.classList.remove("et-expanded"),this.button.textContent="\u26F6 Expand",this.button.title="Expand table",this.button.setAttribute("aria-label","Expand table"),this.button.setAttribute("aria-expanded","false"),this.resetBaseline(),this.onRestore?.(),this.rerender(),this.button.focus({preventScroll:!0}),this.frame(()=>this.applyFrozenOffsets()))}fit(){if(!this.expanded||this.fitting)return;let e=()=>{let n=this.scroller.querySelector("table");return[this.scroller.clientHeight,this.scroller.clientWidth,n?.getBoundingClientRect().height,n?.querySelector("tbody")?.getBoundingClientRect().height,this.getPageSizeOverride(),this.getPageMetrics?.()?.remaining].join(":")},r=this.getPageMetrics?.()?.projection;if(!(e()===this.lastFit&&r===this.lastProjection)){this.fitting=!0;try{let n=0,o=1/0,s=null;for(let i=0;i<12;i++){let a=this.scroller.querySelector("table"),l=a?.querySelector("tbody");if(!l)break;let c=a.getBoundingClientRect().height,f=l.getBoundingClientRect().height,u=this.scroller.clientHeight-2,p=u-(c-f);if(p<=0||f<=0)break;let d=this.getPageMetrics?.(),h=d?.count||l.children.length,m=d?d.remaining||h:1/0,y=Number(this.getPageSizeOverride())||h;if(c<=u){if(n=y,s=y,h>=m||o-n<=1)break}else if(o=y,y<=1||o-n<=1)break;let g=Math.floor(h*p/f),w;if(Number.isFinite(o)?n>0?w=Math.floor((n+o)/2):w=Math.max(1,Math.min(o-1,g)):w=Math.min(m,Math.max(y+1,g)),w===y)break;this.setPageSizeOverride(w),this.rerender()}s!=null&&s!==this.getPageSizeOverride()&&(this.setPageSizeOverride(s),this.rerender())}finally{this.lastFit=e(),this.lastProjection=r,this.fitting=!1}}}applyFrozenOffsets(){if(this.destroyed)return;let e=this.getOptions().freeze_columns||0,r=this.scroller.querySelector("table");if(!r)return;let n=0;for(let d of r.querySelectorAll("thead tr")){for(let h of d.children)h.style.top=`${n}px`;n+=d.getBoundingClientRect().height}let o=[...r.querySelectorAll("tbody [data-column-index]")],s=[...r.querySelectorAll("thead .et-axis-row [data-column-index], tfoot [data-column-index]")],i=[...r.querySelectorAll("[data-column-start]")],a=[...r.querySelectorAll(".et-display-heading:not(.et-display-align-center) > .et-display-label")];for(let d of a)if(d.classList.toggle("et-frozen-heading-label",e>0),d.style.left=e>0?window.getComputedStyle(d.parentElement).paddingLeft:"",e<=0)for(let h of["width","left","top","bottom"])d.style.removeProperty(`--et-heading-frozen-${h}`);for(let d of[...o,...s,...i])e<=0&&!d.classList.contains("et-frozen")||(d.style.left="",d.classList.remove("et-frozen","et-frozen-last"),d.tagName==="TD"&&(d.style.position=""));if(e<=0)return;let l=new Map,c=0,f=r.getBoundingClientRect().left,u=[...r.querySelectorAll("thead [data-column-start]")].filter(d=>d.colSpan===1);for(let d of[...o,...u]){let h=Number(d.dataset.columnIndex??d.dataset.columnStart);if(h<e&&!l.has(h)){let m=d.getBoundingClientRect();l.set(h,m.left-f),c=Math.max(c,(m.right??m.left+(m.width||0))-f)}}for(let d of a){let h=window.getComputedStyle(d.parentElement);d.style.setProperty("--et-heading-frozen-width",`${c}px`),d.style.setProperty("--et-heading-frozen-left",h.paddingLeft),d.style.setProperty("--et-heading-frozen-top",h.paddingTop),d.style.setProperty("--et-heading-frozen-bottom",h.paddingBottom)}let p=(d,h,m)=>{h>=e||!l.has(h)||(d.style.position="sticky",d.style.left=`${l.get(h)}px`,d.style.zIndex=String(m+e-h),d.classList.add("et-frozen"),h+d.colSpan===e&&d.classList.add("et-frozen-last"))};for(let d of o)p(d,Number(d.dataset.columnIndex),10);for(let d of s)p(d,Number(d.dataset.columnIndex),d.closest("thead")?30:10);for(let d of i){let h=Number(d.dataset.columnStart);h+d.colSpan<=e&&p(d,h,d.closest("thead")?30:10)}}};var Ir=class{constructor(){this.reset()}reset(){this.pages=[],this.current=null}project(e,r,n){let o=Math.max(1,Math.floor(Number(r)||10));this.pages.length||this.pages.push({start:0,size:o});let s=Math.max(0,Math.min(n,this.pages.length-1)),i=this.pages[s];i.size=o;let a=Math.min(i.start,e),l=Math.min(e,a+o);return this.pages[s+1]?.start!==l&&(this.pages.length=s+1),this.current={page:s,start:a,end:l,total:e,size:o},{page:s,start:a,end:l,total:e,variable:!0,pageCount:s+(l<e?2:1)}}move(e){if(!this.current)return null;let{page:r,end:n,total:o,size:s}=this.current;return e===r+1&&n<o&&!this.pages[e]&&this.pages.push({start:n,size:s}),this.pages[e]?{page:e,size:this.pages[e].size}:null}};function ti(t,e){e.gradientScales||=new Map;let r=t.gradient;if(!e.gradientScales.has(r)){let n=e.col.domain&&typeof e.col.domain=="object"?e.col.domain:{};e.gradientScales.set(r,Yt([],{colorPalette:r.color_scale??n.palette,colorStops:r.color_stops,min:r.min??e.lo,max:r.max??e.hi,midpoint:r.midpoint,mode:r.scale_mode}))}return e.gradientScales.get(r)}function Se(t,e,r,n){if(!t.gradient)return n;let o=ti(t,e),s=e.lo===e.hi&&t.gradient.min==null&&t.gradient.max==null&&!t.gradient.color_stops;return fe(s?(o.minValue+o.maxValue)/2:r,o)}function ie(t,e,r,n,o){let s=p=>Se(t,e,p,o),i=p=>{let d=(e.reverse?100-p:p)/100;return e.col.scale?.transform==="log"&&e.lo>0&&e.hi>e.lo?e.lo*Math.pow(e.hi/e.lo,d):e.lo+d*(e.hi-e.lo)},a=p=>s(i(p));if(!t.gradient)return{style:{},colorAt:s,at:a};let l=ti(t,e),c=new Set([r,n]);for(let p=1;p<32;p++)c.add(r+(n-r)*p/32);let f=l.domain.length===l.colorPalette.length?l.domain:l.colorPalette.map((p,d)=>l.minValue+d/(l.colorPalette.length-1)*(l.maxValue-l.minValue));for(let p of f){let d=e.pos(p);d!=null&&d>r&&d<n&&c.add(d)}return{style:{backgroundColor:"transparent",backgroundImage:`linear-gradient(to right, ${[...c].sort((p,d)=>p-d).map(p=>`${a(p)} ${100*(p-r)/(n-r||1)}%`).join(", ")})`},colorAt:s,at:a}}function ei(t){return!!t.encodings?.length||t.viz==="bar"}function ri(t,{rowNumbers:e=!1,link:r=!1}={}){if(!t.some(ei))return null;let n=b("colgroup"),o=()=>b("col",{class:"et-col-content"});e&&n.append(o());for(let s of t)n.append(ei(s)?b("col",{class:"et-col-chart"}):o());return r&&n.append(o()),n}function ni(t,e,r,n){let o=t.kind==="section",s=["et-row","et-display-row",`et-display-${t.kind}`,o?"et-row-section":t.kind==="summary"?"et-row-subtotal":"et-row-total",t.continuation?"et-row-continuation":"",`et-display-rule-${t.rule}`,je(r.shadingCounter.value++,n)?"et-row-shaded":""],i=b("tr",{class:s.filter(Boolean).join(" "),"data-display-id":t.id}),a=()=>{let u=b("span",{class:"et-display-label"});for(let[p,d]of Object.entries(t.labelStyle||{}))u.style.setProperty(p.replaceAll("_","-"),String(d));return o&&t.collapsible?u.append(b("button",{class:"et-section-toggle",type:"button","data-section-key":t.groupKey,"aria-expanded":String(!t.collapsed),"aria-label":`Toggle section ${t.label}`,onclick:p=>{p.stopPropagation(),r.toggleSection(t.groupKey)}},[b("span",{class:"et-section-chevron","aria-hidden":"true"},t.collapsed?"\u25B8":"\u25BE"),t.label])):u.append(document.createTextNode(t.label)),u},l=u=>{for(let[p,d]of Object.entries(t.style)){let h=p.replaceAll("_","-");["background","background-color"].includes(h)&&Gt(u,String(d))||u.style.setProperty(h,String(d))}},c=u=>{let p=t.align!=="center"&&Er(t.depth,n,t.toggleDepth);p&&(u.style.paddingLeft=p)};if(o&&!Object.keys(t.cells).length){let u=b("td",{class:`et-td et-display-heading et-display-align-${t.align}`,colspan:e.length+(r.rowNumbers?1:0)+(n.link?1:0)},a());return c(u),l(u),i.append(u),i}r.rowNumbers&&i.append(b("td",{class:"et-td et-row-num","data-column-index":0}));let f=e.find(u=>u.name===t.labelColumn)?.name||e.find(u=>$t(n,u))?.name||e[0]?.name;return e.forEach((u,p)=>{let d=b("td",{class:`et-td${$t(n,u)?" et-stub":""}`,style:{textAlign:u.align||(u.type==="number"?"right":"left")}}),h=t.cells[u.name];if(u.name===f&&(t.label||t.collapsible)&&(o&&d.classList.add("et-display-label-cell"),d.append(a()),c(d)),h){let m=h.value,y=m==null?u.null_text??n.null_text??"\u2013":typeof m=="string"?m:pt(m,h.format||u.fmt,{type:u.type,fallback:String(m)});d.append(b("span",{class:"et-display-value"},Mt(y)))}de(d,u,p,r),l(d),i.append(d)}),n.link&&i.append(b("td",{class:"et-td et-td-chevron"})),i}var tc=new Set(["http:","https:","mailto:","tel:"]);function ve(t,e=globalThis.document?.baseURI){if(t==null||t==="")return null;let r=String(t).trim();if(!r)return null;try{let n=e&&/^https?:/i.test(e)?e:"https://evidential.invalid/";return tc.has(new URL(r,n).protocol)?r:null}catch{return null}}function oi(t,e,r,n,o){let s=t.cap==="round",i=[e.pos(e.row[t.source]),e.pos(e.row[t.high])],a=f=>s&&i.some(u=>u===f)?"999px":"0",l=s?{borderRadius:`${a(r)} ${a(n)} ${a(n)} ${a(r)}`}:{},c=ie(t,e,r,n,o);return{...c,style:{...l,...c.style}}}function He(t,e=!1){return t==="top"?{top:"0",transform:e?"translate(-50%, 0)":"none"}:t==="bottom"?{top:"auto",bottom:"0",transform:e?"translate(-50%, 0)":"none"}:e?{top:"50%",transform:"translate(-50%, -50%)"}:{top:"50%",transform:"translateY(-50%)"}}function si(t,e,r,n){return!t.direction_marker||e===r?null:b("span",{class:"et-range-direction","data-direction":r>e?"right":"left","aria-hidden":"true",style:{color:n}})}function ec(t,e,r,n,o,s){let i=e[t.source],a=Array.isArray(i)?i:[],l=t.colors||{},c=h=>Z(l[String(h)])||"var(--et-accent, #2563eb)",f=h=>h&&typeof h=="object"?h.category??h.state??h.value:h,u=(h,m)=>{let y=f(m);return y!=null&&wt(h,se(pe(o,t,String(y),s),"",null,m,c(y),["category","state","value"]),{priority:2}),h};if(n!=null&&a.some(h=>h&&typeof h=="object"&&(h.start!=null||h.position!=null))){let h=b("div",{class:`et-mark-strip et-mark-strip-positioned${t.segmented===!1?" et-mark-strip-joined":""}`}),m=y=>Math.max(0,Math.min(100,(y-r)/n*100));return a.forEach((y,g)=>{if(!y||typeof y!="object")return;let w=Number(y.start??y.position);if(!isFinite(w))return;let E=y.end??y.finish;if(E==null){let C=a[g+1];E=C&&typeof C=="object"&&C.position!=null?C.position:r+n}let L=m(w),N=100-Math.max(L,m(Number(E))),O=b("div",{class:"et-strip-run",style:{left:`${L}%`,right:`${N}%`,backgroundColor:c(f(y))}});t.strip_labels&&f(y)!=null&&String(f(y))!==""&&O.append(b("span",{class:"et-strip-label"},String(f(y)).charAt(0))),h.append(u(O,y))}),h}let d=b("div",{class:`et-mark-strip${t.segmented===!1?" et-mark-strip-joined":""}`});for(let h of a){let m=f(h),y=b("span",{class:`et-strip-seg${t.segmented===!1?" et-strip-joined":""}`,style:{backgroundColor:m==null?"transparent":c(m)}});t.strip_labels&&m!=null&&String(m)!==""&&y.append(b("span",{class:"et-strip-label"},String(m).charAt(0))),d.append(u(y,h))}return d}function Ge(t,e,r,n,o,s="",i={}){let a=Math.max(0,Math.min(100,n)),l=Math.max(0,Math.min(100,n+o)),c=b("div",{class:"et-mark-stack-seg",style:{left:`${a}%`,width:`${Math.max(0,l-a)}%`,backgroundColor:vt(t,e,"var(--et-accent, #2563eb)")}}),f=(r.encodings||[]).filter(u=>u.kind==="stacked_bar").reduce((u,p)=>u+(Number(e[p.source])>0?Number(e[p.source]):0),0);if(wt(c,Zt(r,t,e,{total:f,context:i}),{priority:2}),s){let u=t.label?.align||(t.label?.position==="inside_start"?"begin":t.label?.position==="center"?"center":"end");u==="begin"?c.style.justifyContent="flex-start":u==="end"&&(c.style.justifyContent="flex-end");let p=t.label||{},d=b("span",{class:"et-mark-stack-label","data-mark-label":"","data-overflow":p.overflow||"hide","data-min-width":p.min_width||0,style:$n(p)},b("span",{class:"et-mark-label-text"},Mt(s)));p.color||An(d,vt(t,e,"var(--et-accent, #2563eb)"),c),c.append(d)}return c}function ii(t,e,r,n,o,s,i){if(!e.label)return"";if(e.label.share){let a=o?n/o:0;return pt(a,e.label.format||"pct0",{type:"number",fallback:`${Math.round(a*100)}%`})}return Nn(t,e,r,i)}function ai(t){let r=(1-(t[0].size!=null?Math.max(.05,Math.min(1,Number(t[0].size))):.7))/2*100;return b("div",{class:"et-mark et-mark-stack",style:{top:`${r}%`,bottom:`${r}%`}})}function rc(t,e,r,n,o,s,i,a){let l=e.map(E=>{let L=Number(r[E.source]);return isFinite(L)&&L>0?L:0}),c=l.reduce((E,L)=>E+L,0),f=n?l.map(E=>c?E/c*100:0):l,u=e.findIndex(E=>E.source===e[0].diverge_at),p=Math.max(Math.abs(o),Math.abs(s),1e-9),d=E=>E/p*50,h=ai(e),m=f[u],y=(E,L)=>ii(t,e[E],r,L,c,n,i),g=m/2;h.append(Ge(e[u],r,t,50-d(g),d(m/2),y(u,l[u]),a));for(let E=u-1;E>=0;E-=1){let L=f[E];h.append(Ge(e[E],r,t,50-d(g+L),d(L),y(E,l[E]),a)),g+=L}let w=m/2;h.append(Ge(e[u],r,t,50,d(m/2),"",a));for(let E=u+1;E<e.length;E+=1){let L=f[E];h.append(Ge(e[E],r,t,50+d(w),d(L),y(E,l[E]),a)),w+=L}return h}function nc(t,e,r,n,o,s,i){let a=(t.scale||{}).normalize==="percent";if(e[0].diverge_at)return rc(t,e,r,a,n,o,s,i);let l=e.map(d=>{let h=Number(r[d.source]);return isFinite(h)&&h>0?h:0}),c=l.reduce((d,h)=>d+h,0),f=ai(e),u=o-n||1,p=0;return e.forEach((d,h)=>{let m=a?c?l[h]/c*100:0:l[h],y=m/u*100;f.append(Ge(d,r,t,(p-n)/u*100,y,ii(t,d,r,l[h],c,a,s),i)),p+=m}),f}function oc(t,e,r,n,o,s){let i=e.parts||{},a=L=>bt(r[i[L]]),[l,c,f,u,p]=["minimum","q1","median","q3","maximum"].map(a);if([l,c,f,u,p].some(L=>L==null))return b("span",{class:"et-null"},"\u2013");let d=vt(e,r,"var(--et-accent, #2563eb)"),h=L=>Se(e,s,L,d),m=(L,N)=>{let O=Math.min(n(L),n(N)),C=Math.max(n(L),n(N));return{left:`${O}%`,width:`${C-O}%`,backgroundColor:d,...ie(e,s,O,C,d).style}},y=b("div",{class:"et-mark et-mark-box"}),g=Zt(t,e,r,{context:o});e.gradient&&(g.color=h(f)),wt(y,g),y.append(b("div",{class:"et-box-whisker",style:m(l,p)}));for(let L of[l,p])y.append(b("div",{class:"et-box-cap",style:{left:`${n(L)}%`,backgroundColor:h(L)}}));let w=m(c,u);y.append(b("div",{class:"et-box-iqr",style:{...w,borderColor:h(f),...e.gradient?{borderImageSource:w.backgroundImage,borderImageSlice:"1"}:{}}})),y.append(b("div",{class:"et-box-median",style:{left:`${n(f)}%`,backgroundColor:h(f)}}));let E=e.outliers&&Array.isArray(r[e.outliers])?r[e.outliers]:[];for(let L of E){let N=bt(L);N!=null&&y.append(wt(b("div",{class:"et-box-outlier",style:{left:`${n(N)}%`,backgroundColor:h(N)}}),{name:"Outlier",value:Ht(N,o.formatCode??t.fmt,t),color:h(N)},{priority:3}))}return y}function sc(t,e){let{col:r,row:n,track:o,clampPos:s,lo:i,hi:a,barCount:l,reverse:c,format:f,labelFor:u,context:p}=e,d=bt(n[t.source]);if(d==null)return;let h=t.size!=null?Number(t.size):l>1?Math.max(.25,.85-e.barIndex*.3):1;e.barIndex+=1;let m=vt(t,n,"var(--et-accent, #2563eb)"),y,g;if(t.side==="left"||t.side==="right"){let j=Math.max(Math.abs(i),Math.abs(a),1e-9),B=Math.max(0,Math.min(50,Math.abs(d)/j*50));g=B,y=t.side==="left"?50-B:50}else{let j=s(0),B=s(d);y=j??0,g=B!=null?B-y:0,g<0&&(y+=g,g=-g)}let w=ie(t,e,y,y+g,m),E=t.side==="left"?y:t.side==="right"?y+g:e.clampPos(d),L=w.at(E??y),N=Zt(r,t,n,{context:p});t.gradient&&(N.color=L),t.background&&o.prepend(b("div",{class:"et-mark et-mark-background",style:{inset:"0",backgroundColor:Z(t.background)||t.background}}));let O=t.pad==null?null:typeof t.pad=="number"?`${t.pad}px`:String(t.pad),C=O?typeof t.pad=="number"?`calc(${h*100}% - ${2*t.pad}px)`:`calc(${h*100}% - ${O} - ${O})`:`${h*100}%`,R=wt(b("div",{class:`et-mark et-mark-bar${t.side?` et-mark-bar-${t.side}`:""}`,style:{...He(t.valign),left:`${y}%`,width:`${Math.max(0,g)}%`,height:C,backgroundColor:m,...w.style,...t.gradient?{opacity:"1"}:{}}}),N,{priority:2});if(o.append(R),!t.hide_labels&&t.label){let j=t.center&&!t.label.position?{...t,label:{...t.label,position:"outside_start"}}:t;o.append(u(r,j,n,{leftPct:y,widthPct:g,mark:R,color:L,colorAt:w.at,negative:c?d>=0:d<0||t.side==="left"},f))}}function ic(t,e){let{col:r,row:n,track:o,clampPos:s,format:i,labelFor:a,context:l}=e,c=Array.isArray(n[t.source])?n[t.source]:[],f=t.size!=null?Number(t.size):t.sources?9:6,p=(t.sources?Tn(t).map(d=>({point:d,raw:n[d.source]})):c.map(d=>({point:t,raw:yn(d),observation:d}))).map(d=>({...d,pct:s(d.raw)})).filter(d=>d.pct!=null);if(t.connect&&p.length>1){let d=p.map(y=>y.pct),h=Math.min(...d),m=Math.max(...d);m>h&&o.append(b("div",{class:"et-mark et-mark-range et-point-connector","aria-hidden":"true",style:{...He(t.valign),left:`${h}%`,width:`${m-h}%`,height:"1px",backgroundColor:"var(--et-muted, #94a3b8)"}}))}for(let{point:d,raw:h,pct:m,observation:y}of p){let g=Se(t,e,Number(h),vt(d,n)),w=t.sources?Zt(r,d,n,{value:h,context:l}):se(pe(r,t,t.source,l),h,l.formatCode??r.fmt,y,g,["value","y"]);w.xValue=Number(h),t.gradient&&(w.color=g),o.append(wt(Fe(b("div",{class:"et-mark et-mark-point",style:{...He(t.valign,!0),left:`${m}%`,width:`${f}px`,height:`${f}px`,backgroundColor:g}}),{...d,color:g}),w,{priority:3})),t.label&&o.append(a(r,d,{...n,[d.source]:h},{pointPct:m},i))}}function ac(t,e){let{col:r,row:n,track:o,clampPos:s,format:i,labelFor:a,context:l}=e,c=bt(n[t.source]);if(c==null)return;let f=s(c);if(f==null)return;let u=t.size!=null?Number(t.size):7,p=Se(t,e,c,vt(t,n)),d=Zt(r,t,n,{context:l});t.gradient&&(d.color=p),o.append(wt(Fe(b("div",{class:"et-mark et-mark-point",style:{...He(t.valign,!0),left:`${f}%`,width:`${u}px`,height:`${u}px`,backgroundColor:p}}),{...t,color:p}),d,{priority:3})),t.label&&o.append(a(r,t,n,{pointPct:f},i))}function lc(t,e){let{col:r,row:n,track:o,lo:s,span:i,format:a,labelFor:l,context:c}=e;o.append(ec(t,n,s,i,r,c)),t.label&&o.append(l(r,t,n,{pointPct:50},a))}function cc(t,e){let{col:r,row:n,track:o,pos:s,format:i,labelFor:a,context:l}=e,c=bt(n[t.source]);if(c==null)return;let f=c,u=bt(n[t.high]);if(u==null)return;let p=s(f),d=s(u),h=Y=>Y==null||Y<0||Y>100,m=(t.overflow==="arrow"||t.cap==="arrow")&&h(p),y=(t.overflow==="arrow"||t.cap==="arrow")&&h(d);if(m&&(p=p!=null&&p>100?100:0),y&&(d=d!=null&&d<0?0:100),p==null||d==null)return;p=Math.max(0,Math.min(100,p)),d=Math.max(0,Math.min(100,d));let g=Math.min(p,d),w=Math.max(p,d),E=t.size!=null?Number(t.size):4,L=vt(t,n,"var(--et-accent, #2563eb)",u<f),N=oi(t,e,g,w,L),O=N.at(g),C=N.at(w),R=N.at((g+w)/2),j=Zt(r,t,n,{context:l});if(t.gradient&&(j.color=R),t.fill){let Y=b("div",{class:"et-mark et-mark-range-fill",style:{top:"15%",bottom:"15%",transform:"none",left:`${g}%`,width:`${Math.max(0,w-g)}%`,backgroundColor:L,...N.style}});m&&Y.append(b("span",{class:"et-mark-cap et-mark-arrow et-mark-arrow-start",style:{borderRightColor:O}})),y&&Y.append(b("span",{class:"et-mark-cap et-mark-arrow et-mark-arrow-end",style:{borderLeftColor:C}})),o.append(wt(Y,j));let X=si(t,p,d,R);X&&(X.style.left=`${(g+w)/2}%`,o.append(X)),t.label&&o.append(a(r,t,n,{pointPct:g},i));return}let B=b("div",{class:"et-mark et-mark-range",style:{...He(t.valign),left:`${g}%`,width:`${Math.max(0,w-g)}%`,height:`${E}px`,backgroundColor:L,...N.style}});if(t.cap==="line"||t.cap==="dot"){let Y=`et-mark-cap${t.cap==="dot"?" et-mark-cap-dot":""}`;m||B.append(b("span",{class:`${Y} et-mark-cap-start`,style:{backgroundColor:O}})),y||B.append(b("span",{class:`${Y} et-mark-cap-end`,style:{backgroundColor:C}}))}m&&B.append(b("span",{class:"et-mark-cap et-mark-arrow et-mark-arrow-start",style:{borderRightColor:O}})),y&&B.append(b("span",{class:"et-mark-cap et-mark-arrow et-mark-arrow-end",style:{borderLeftColor:C}}));let U=si(t,p,d,R);U&&B.append(U),o.append(wt(B,j)),t.label&&o.append(a(r,t,n,{pointPct:g},i))}function fc(t,e){let{col:r,row:n,track:o,clampPos:s,format:i,labelFor:a,context:l}=e;o.append(oc(r,t,n,s,l,e));let c=s(n[t.source]);t.label&&c!=null&&o.append(a(r,t,n,{pointPct:c},i))}function uc(t,e){let{col:r,row:n,track:o,pos:s,format:i,labelFor:a,context:l}=e,c=is(t,n,s,vt(t,n,"var(--et-accent, #2563eb)"),f=>ie(t,e,f.left,f.left+f.width).style);if(c){let f=Pe(n[t.source],t.distribution),u=0,p=0;for(let h of f)for(let m of h)u++,p=Math.max(p,m.density);let d=h=>Ht(h,l.formatCode??r.fmt,r);wt(c,{name:pe(r,t,t.source,l),value:"Density band",color:Se(t,e,(f[0][0].x+f.at(-1).at(-1).x)/2,vt(t,n)),details:[{name:"Support start",value:d(f[0][0].x)},{name:"Support end",value:d(f.at(-1).at(-1).x)},{name:"Peak density",value:Ht(p)},{name:"Samples",value:Ht(u)}]}),o.append(c),t.label&&o.append(a(r,t,n,{pointPct:50},i))}}function dc(t,e){t===e.stack[0]&&e.track.append(nc(e.col,e.stack,e.row,e.lo,e.hi,e.format,e.context))}var pc={bar:sc,points:ic,point:ac,range:cc,strip:lc,boxplot:fc,distribution:uc,stacked_bar:dc};function li(t,e){pc[t.kind]?.(t,e)}function Fr(t,e){let r=t.scale||{};if(e?.shared)return{lo:e.min,hi:e.max,span:e.max-e.min||1,transform:r.transform};let n=r.domain&&r.domain[0]!=null?Number(r.domain[0]):e?.min??0,o=r.domain&&r.domain[1]!=null?Number(r.domain[1]):e?.max??1,s=(t.encodings||[]).some(l=>l.kind==="bar"||l.kind==="stacked_bar"),i=(t.encodings||[]).filter(l=>l.kind==="bar"),a=i.length>0&&i.every(l=>l.fit_to_data)&&!(t.encodings||[]).some(l=>l.kind==="stacked_bar");return r.include_zero!==!1&&s&&!a&&r.transform!=="log"&&(r.domain?.[0]==null&&(n=Math.min(0,n)),r.domain?.[1]==null&&(o=Math.max(0,o))),(t.encodings||[]).some(l=>l.center||l.side||l.diverge_at)&&(!r.domain||n>=0)&&(o=Math.max(Math.abs(n),Math.abs(o)),n=-o),{lo:n,hi:o,span:o-n||1,transform:r.transform}}function zn(t,e,r=4,n=null){if(!isFinite(t)||!isFinite(e)||e<=t)return[];if(n==="log"&&t>0){let c=[];for(let f=Math.floor(Math.log10(t))-1;f<=Math.ceil(Math.log10(e));f+=1)for(let u of[1,2,5]){let p=u*Math.pow(10,f);p>=t&&p<=e&&c.push(Number(p.toPrecision(12)))}if(c.length)return c}let o=(e-t)/Math.max(1,r),s=Math.pow(10,Math.floor(Math.log10(o))),i=o/s,a=(i>=5?5:i>=2.5?2.5:i>=2?2:1)*s,l=[];for(let c=Math.ceil(t/a)*a;c<=e+a*1e-6;c+=a)l.push(Number(c.toFixed(10)));return l}function ci(t,e,r=4,n=null){if(n!=="log")return zn(t,e,r,n).map(s=>({value:s,major:!0}));if(!(t>0)||!Number.isFinite(e)||e<=t)return[];let o=new Map([[t,{value:t,major:!0}],[e,{value:e,major:!0}]]);for(let s=Math.floor(Math.log10(t));s<=Math.ceil(Math.log10(e));s++)for(let i=1;i<=9;i++){let a=Number((i*Math.pow(10,s)).toPrecision(12));a>=t&&a<=e&&!o.has(a)&&o.set(a,{value:a,major:i===1})}return[...o.values()].sort((s,i)=>s.value-i.value)}function jr(t,e,r,n=!1){let o=hc(t,e,r);return s=>{let i=o(s);return i==null?null:n?100-i:i}}function hc(t,e,r){if(r==="log"&&t>0&&e>t){let o=Math.log(t),s=Math.log(e)-o||1;return i=>{let a=bt(i);return a==null||a<=0?null:(Math.log(a)-o)/s*100}}let n=e-t||1;return o=>{let s=bt(o);return s!=null?(s-t)/n*100:null}}var In="http://www.w3.org/2000/svg",fi=Symbol.for("evidential.sparklineGradientCounter");function Fn(t,e,{min:r,max:n,top:o,bottom:s,origin:i,opacity:a=1}){let l=document.createElementNS(In,"linearGradient"),c=`et-sparkline-gradient-${document[fi]=(document[fi]||0)+1}`;l.setAttribute("id",c),l.setAttribute("gradientUnits","userSpaceOnUse"),l.setAttribute("x1","0"),l.setAttribute("x2","0"),l.setAttribute("y1",String(s)),l.setAttribute("y2",String(o)),l.setAttribute("spreadMethod","pad");let f=n-r||1,u=[...new Set([r,n,i,...e.breakpoints||[]])].filter(h=>h>=r&&h<=n).sort((h,m)=>h-m),p=new Set(u);for(let h=1;h<u.length;h++){let m=u[h-1],y=u[h],g=Math.max(1,Math.ceil(32*(y-m)/f));for(let w=1;w<g;w++)p.add(m+w/g*(y-m))}for(let h of[...p].sort((m,y)=>m-y)){let m=document.createElementNS(In,"stop");m.setAttribute("offset",String((h-r)/f));let y=e(h),g=y,w=1;if(ot.valid(y)){let L=ot(y);g=L.hex("rgb"),w=L.alpha()}let E=Array.isArray(a)?a[0]+(a[1]-a[0])*(h<i?(i-h)/(i-r||1):(h-i)/(n-i||1)):a;m.setAttribute("stop-color",g),m.setAttribute("stop-opacity",String(w*E)),l.append(m)}let d=t.querySelector("defs");return d||(d=document.createElementNS(In,"defs"),t.prepend(d)),d.append(l),`url(#${c})`}function Gn(t,e,r,n){let o=t.sparkline_options||{},s=ne(e,o),i=s.filter(G=>G[1]!=null);if(!i.length)return b("span",{class:"et-null"},"\u2013");let a=r||Bn(t,i.map(G=>G[1]),n);if(o.type==="change")return Zs(s,o,a);let l=o.width||64,c=o.height||18,f=1.5,u=i.map(G=>G[1]),p=Math.min(...u),d=Math.max(...u),h=bt(o.reference);h!=null&&(p=Math.min(p,h),d=Math.max(d,h)),o.fit_to_data||(p=Math.min(0,p),d=Math.max(0,d)),n?.shared&&(p=n.min,d=n.max);let m=d-p||1,y=G=>bt(G)??(typeof G=="string"&&/^\d{4}-\d\d-\d\d/.test(G)?Date.parse(G):NaN),g=s.map(G=>y(G[0])),w=g.every(Number.isFinite),E=w?Math.min(...g):0,L=w?Math.max(...g):s.length-1,N=Math.max(p,Math.min(d,h??0)),O=f+(c-f*2)*(1-(N-p)/m),C=s.map(([G,ct,ft],ht)=>({x:L>E?f+((w?g[ht]:ht)-E)/(L-E)*(l-f*2):l/2,y:ct==null?null:f+(c-f*2)*(1-(ct-p)/m),raw:[G,ct],source:ft})),R=Z(o.color)||"var(--et-accent, #2563eb)",j=G=>Me(G.source,o)||a?.(G.raw[1])||R,B="http://www.w3.org/2000/svg",U=document.createElementNS(B,"svg");U.setAttribute("class","et-sparkline"),U.setAttribute("width",String(l)),U.setAttribute("height",String(c)),U.setAttribute("viewBox",`0 0 ${l} ${c}`);let Y=([G,ct])=>{let ft=document.createElementNS(B,"title"),ht=Ht(ct,o.y_fmt);return ft.textContent=G==null||G===""?ht:`${G}: ${ht}`,ft};if(h!=null&&h>=p&&h<=d||h==null&&!o.fit_to_data&&p<0&&d>0){let G=document.createElementNS(B,"line");G.setAttribute("x1","0"),G.setAttribute("x2",String(l)),G.setAttribute("y1",String(O)),G.setAttribute("y2",String(O)),G.setAttribute("class","et-sparkline-reference"),G.setAttribute("stroke",o.reference_color||"color-mix(in srgb, CanvasText 20%, transparent)"),G.setAttribute("stroke-width","1"),h!=null&&(G.setAttribute("stroke-dasharray","2 2"),G.append(Y([null,h]))),U.append(G)}let X=o.type||"line",Nt={min:p,max:d,origin:N,top:f,bottom:c-f},dt=a&&(X==="line"||X==="area"||X==="bar")?Fn(U,a,Nt):R,mt=o.fill_opacity??(a?1:.22),rt=G=>a&&mt===1?dt:a||Array.isArray(mt)?Fn(U,a||(()=>G),{...Nt,opacity:mt}):G,xt=!!o.markers||X==="points",At=o.markers==="ends";if(X==="bar"){let G=l/C.length,ct=Math.max(1,G*.7);C.forEach(ft=>{if(ft.y==null)return;let ht=Math.min(ft.y,O),Et=document.createElementNS(B,"rect");Et.setAttribute("x",String(Math.max(0,ft.x-ct/2))),Et.setAttribute("y",String(ht)),Et.setAttribute("width",String(ct)),Et.setAttribute("height",String(Math.max(1,Math.abs(O-ft.y)))),Et.setAttribute("rx","0.5");let Ot=Me(ft.source,o)||(a?dt:j(ft));Et.setAttribute("fill",Ot),Et.append(Y(ft.raw)),wt(Et,se(ft.raw[0],ft.raw[1],o.y_fmt,ft.source,j(ft),[o.x,o.y,"x","y","value"]),{priority:2}),U.append(Et)})}else if(X!=="points"){let G=[],ct=[];for(let at of C)at.y==null?(ct.length&&G.push(ct),ct=[]):ct.push(at);ct.length&&G.push(ct);let ft=o.signed&&!a,ht=X==="area"?rt(R):null,Et=X==="area"&&ft?rt("var(--et-negative, #dc2626)"):null,Ot=a||Array.isArray(mt)?1:mt;for(let at of G){let x=at.map(k=>`${k.x},${k.y}`).join(" ");if(X==="area")if(ft){let k=mc(at,O);jn(B,U,k,O,H=>Math.min(H.y,O),ht,Ot),jn(B,U,k,O,H=>Math.max(H.y,O),Et,Ot)}else jn(B,U,at,O,k=>k.y,ht,Ot);let _=document.createElementNS(B,"polyline");_.setAttribute("points",x),_.setAttribute("fill","none"),_.setAttribute("stroke",dt),_.setAttribute("stroke-width","1.25"),_.setAttribute("stroke-linejoin","round"),_.setAttribute("stroke-linecap","round"),U.append(_)}}return C.forEach((G,ct)=>{if(G.y==null)return;let ft=ct===0||ct===C.length-1,ht=xt&&(!At||ft),Ot=Me(G.source,o)||Z(o.marker_color)||j(G),at;ht&&o.shape&&o.shape!=="circle"?(at=Ie({shape:o.shape,angle:o.angle,color:Ot,outline:o.outline??!1}),at.setAttribute("x",String(G.x-2.2)),at.setAttribute("y",String(G.y-2.2)),at.setAttribute("width","4.4"),at.setAttribute("height","4.4"),at.style.width=at.style.height="4.4px"):(at=document.createElementNS(B,"circle"),at.setAttribute("cx",String(G.x)),at.setAttribute("cy",String(G.y)),at.setAttribute("r",ht?"2.2":"2.5"),at.setAttribute("fill",ht?Ot:"transparent"),ht&&o.outline&&(at.setAttribute("stroke",o.outline===!0?"var(--et-marker-outline, color-mix(in srgb, Canvas 60%, transparent))":Z(o.outline)),at.setAttribute("stroke-width","1"))),at.dataset.sparklineObservation="true",at.append(Y(G.raw));let x=X==="area"&&o.signed&&!a&&!ht?G.raw[1]<(h??0)?"var(--et-negative, #dc2626)":R:ht?Ot:X==="bar"?j(G):a?.(G.raw[1])||R;wt(at,se(G.raw[0],G.raw[1],o.y_fmt,G.source,x,[o.x,o.y,"x","y","value"]),{priority:3}),U.append(at)}),U}function mc(t,e){let r=[];for(let n of t){let o=r.at(-1);if(o&&(o.y-e)*(n.y-e)<0){let s=(e-o.y)/(n.y-o.y);r.push({x:o.x+s*(n.x-o.x),y:e})}r.push(n)}return r}function jn(t,e,r,n,o,s,i){let a=document.createElementNS(t,"polygon"),l=r.map(c=>`${c.x},${o(c)}`).join(" ");a.setAttribute("points",`${l} ${r[r.length-1].x},${n} ${r[0].x},${n}`),a.setAttribute("fill",s),a.setAttribute("opacity",String(i)),e.append(a)}function ui(t,e,r,n,o={}){let s=(N,O,C,R,j)=>wt(gs(N,O,C,R,j),Zt(N,O,C,{context:o}),{priority:1,navigate:!1}),i=t.encodings||[],a=t.scale||{},{lo:l,hi:c,span:f}=Fr(t,r),u=i.some(N=>N.kind==="bar"&&N.direction==="left"),p=jr(l,c,a.transform,u),d=N=>{let O=p(N);return O==null?null:Math.max(0,Math.min(100,O))},h=b("div",{class:"et-marks"});if(h.setAttribute("role","img"),i.some(N=>["above","below"].includes(N.label?.position))&&h.classList.add("et-marks-tall"),a.gridlines)for(let N of zn(l,c,4,a.transform)){let O=p(N);O!=null&&h.append(b("div",{class:"et-mark-gridline",style:{left:`${Math.max(0,Math.min(100,O))}%`}}))}let m=i.filter(N=>N.kind==="bar"&&N.reference!=null).map(N=>({value:N.reference,color:N.reference_color,label:N.reference_label})),y=i.some(N=>N.center);y&&h.classList.add("et-marks-centered");let g=[...y?[{value:0,center:!0}]:[],...t.references||[],...m],w=document.createDocumentFragment();for(let N of g){if(N.value==null||!isFinite(Number(N.value)))continue;let O=p(Number(N.value));if(O==null)continue;let C=O;if(N.high!=null&&isFinite(Number(N.high))){let R=p(Number(N.high));if(R==null)continue;let j=Math.max(0,Math.min(100,Math.min(C,R))),B=Math.max(0,Math.min(100,Math.max(C,R)));if(B<=j)continue;w.append(b("div",{class:"et-mark-band",style:{left:`${j}%`,width:`${B-j}%`,backgroundColor:Z(N.color)}})),N.label&&h.append(b("span",{class:"et-mark-reference-label",style:{left:`${j}%`}},String(N.label)));continue}C<0||C>100||(h.append(b("div",{class:`et-mark-reference${N.center?" et-mark-centerline":""}`,style:{left:`${C}%`,backgroundColor:Z(N.color)||"var(--et-reference, #0f766e)"}})),N.label&&h.append(b("span",{class:"et-mark-reference-label",style:{left:`${C}%`}},String(N.label))))}h.prepend(w);let E={col:t,row:e,track:h,pos:p,clampPos:d,lo:l,hi:c,span:f,reverse:u,format:n,labelFor:s,context:o,barCount:i.filter(N=>N.kind==="bar").length,barIndex:0,stack:i.filter(N=>N.kind==="stacked_bar")};for(let N of i)li(N,E);h.querySelector(".et-mark, .et-mark-strip, .et-density-band")||h.append(b("span",{class:"et-null"},String(t.null_text??(n?n(null):"\u2013"))));let L=[...new Set([...h.querySelectorAll("[data-et-tooltip]:not([data-mark-label])")].map(N=>oe(qs(N))))].join(`
`);return h.setAttribute("aria-label",L||"No observations"),h}function di(t,e,r,n,o){let s=t.bar_options||{},i=Number(e),a=n?.shared||s.fit_to_data?n?.min??0:Math.min(0,n?.min??0),l=n?.shared||s.fit_to_data?n?.max??0:Math.max(0,n?.max??0),c=i<0,f=s.direction==="left",u=s.bar_color_column&&o?Tt(o[s.bar_color_column],s):null,p=c?Tt(o?.[s.bar_color_negative_column],s)||u||Z(s.bar_color_negative)||Z(s.bar_color)||"var(--et-negative, #dc2626)":u||Z(s.bar_color)||"var(--et-accent, #2563eb)",d=b("span",{class:`et-bar-label${s.hide_labels?" et-hidden":""}`},Mt(r)),h=s.background_color?{backgroundColor:s.background_color}:{},m=s.pad==null?null:typeof s.pad=="number"?`${s.pad}px`:String(s.pad),y;if(s.center){let g=Math.max(Math.abs(a),Math.abs(l),1e-9),w=Math.max(0,Math.min(100,Math.abs(i)/g*100))/2,E=b("div",{class:`et-bar et-bar-${c?"left":"right"}`,style:{width:`${w}%`,backgroundColor:p}}),L=b("div",{class:"et-bar-axis"}),N=b("div",{class:"et-bar-wrap"},[L,E]);d.classList.add(c?"et-bar-label-right":"et-bar-label-left"),y=b("div",{class:"et-bar-cell et-bar-center",style:h},[N,d])}else{let g=l-a||1,w=Math.max(0,Math.min(100,(i-a)/g*100)),E=b("div",{class:`et-bar${f?" et-bar-fill-left":""}`,style:{width:`${w}%`,backgroundColor:p}}),L=gc(s,a,g,f),N=b("div",{class:`et-bar-wrap${c?" et-bar-negative":""}`},[E,...L]);y=b("div",{class:"et-bar-cell",style:h},[N,d])}return m&&y.style.setProperty("--et-bar-pad",m),y}function gc(t,e,r,n){if(t.reference==null||!isFinite(Number(t.reference)))return[];let o=Math.max(0,Math.min(100,(Number(t.reference)-e)/r*100)),s=n?100-o:o,i=Z(t.reference_color)||"var(--et-reference, #0f766e)",a=[b("div",{class:"et-bar-reference",style:{left:`${s}%`,backgroundColor:i}})];if(t.reference_label){let l=s>60?"translateX(-100%)":s<40?"translateX(0)":"translateX(-50%)";a.push(b("span",{class:"et-bar-reference-label",style:{left:`${s}%`,color:i,transform:l}},String(t.reference_label)))}return a}function pi(t,e,r){let n=t.symbol_options||{},o=Number(e);if(e==null||e===""||Number.isNaN(o))return b("span",{class:"et-null"},r??"\u2013");let s=Math.max(0,Math.round(o)),i=n.max!=null?Math.max(s,Math.round(Number(n.max))):s,a=b("span",{class:"et-symbols",role:"img","aria-label":n.max!=null?`${s} of ${i} symbols`:`${s} symbols`});n.size!=null&&(a.style.fontSize=`${n.size}em`),n.gap!=null&&(a.style.gap=`${n.gap}em`);for(let l=0;l<i;l++){let c=l<s;if(n.image){a.append(b("img",{class:`et-symbol-image${c?"":" et-symbol-empty"}`,src:String(n.image),alt:"",loading:"lazy"}));continue}let f=Cs(n,c);if(f){let d=b("span",{class:`et-symbol-box et-symbol-box-${f.shape}${c?"":" et-symbol-empty"}`,"data-shape":f.shape,"data-angle":f.angle,"data-hollow":String(f.hollow),style:{width:n.size!=null?"1em":"0.85em",height:n.size!=null?"1em":"0.85em",color:Z(c?n.color:n.empty_color)||Z(n.color)||"currentColor"}},Ie({...f,outline:n.outline}));a.append(d);continue}let u=b("span",{class:`et-symbol${c?"":" et-symbol-empty"}`},c?n.symbol||"\u25CF":n.empty||n.symbol||"\u25CF"),p=c?n.color:n.empty_color;p&&(u.style.color=Z(p)),a.append(u)}return a}function bc(t){let e=t.neutral_range;if(typeof e=="string"){let r=e.match(/^\s*(-?\d+(?:\.\d+)?)\s*(?::|\.\.)\s*(-?\d+(?:\.\d+)?)\s*$/);if(r)return[Number(r[1]),Number(r[2])]}return Array.isArray(e)&&e.length===2?[Number(e[0]),Number(e[1])]:typeof e=="number"&&isFinite(e)?[-Math.abs(e),Math.abs(e)]:[t.neutral_min??0,t.neutral_max??0]}function Hn(t,e){let r=t.delta_options||{},n=e==null,o=n?0:Number(e),[s,i]=bc(r),a=n||(s==null||o>=s)&&(i==null||o<=i),l=o>0,c=a?!1:r.down_is_good?!l:l,f=a?"et-delta-neutral":c?"et-delta-good":"et-delta-bad",u=r.show_symbol===!1?"":a?"\u2013":l?"\u25B2":o<0?"\u25BC":"\u2013",p=t.fmt&&t.fmt.startsWith("pct")?pt(Math.abs(o),t.fmt,{type:"number",fallback:String(Math.abs(o))}):Math.abs(o).toLocaleString(void 0,{maximumFractionDigits:1}),d=r.show_value===!1||n?"":p,h=d?b("span",{class:"et-delta-value"},d):null,m=u?b("span",{class:"et-delta-indicator"},u):null,y=r.symbol_position==="left"?[m,h]:[h,m],g=[];for(let E of y)E&&(g.length&&g.push(" "),g.push(E));let w=["et-delta",f,r.chip?"et-delta-chip":""].filter(Boolean).join(" ");return b("span",{class:w},g.length?g:"\u2013")}function yc(t,e,r,n){let o=n.rules;if(!o)return null;for(let s of o)if(s.type==="substitute"&&!(s.columns!=="*"&&!s.columns.includes(t.name))&&!(s.rows&&!s.rows.includes(e.__row_id))){if(s.kind==="missing"){if(r==null)return s.text;continue}if(r!=null){if(s.kind==="zero"&&Number(r)===0||s.kind==="values"&&(s.values||[]).includes(r))return s.text;if(!isNaN(Number(r))){let i=Number(r);if(s.kind==="small"&&i<s.threshold||s.kind==="large"&&i>s.threshold)return s.text}}}return null}function _c(t,e,r){let n=r.rules;if(!n||!n.length)return{fmt:null,style:null};let o=null,s=null;for(let i of n)i.columns!=="*"&&!i.columns.includes(t.name)||i.rows&&!i.rows.includes(e.__row_id)||(i.fmt!=null&&(o=i.fmt),i.style&&(s={...s||{},...i.style}));return{fmt:o,style:s}}function xc(t,e,r,n,o,s,i,a){e.font_color&&(t.style.color=Z(e.font_color)),e.font_weight&&(t.style.fontWeight=e.font_weight),e.font_style&&(t.style.fontStyle=e.font_style);let l=e.footnote||a.footnote_column;if(i&&l&&r[l]){let c=String(r[l]).trim();if(c){let f=n.footnotes.find(u=>u.text===c);f||(f={text:c,index:n.footnotes.length+1,rows:new Set},n.footnotes.push(f)),f.rows.add((n.rowNumberBase||0)+o+1),t.append(b("sup",{class:"et-footnote-mark",title:c,"data-footnote-index":f.index}))}}if(s)for(let[c,f]of Object.entries(s))["background","background-color"].includes(c)&&Gt(t,f)||t.style.setProperty(c,f)}function hi({row:t,col:e,index:r,ctx:n,rowIndex:o,options:s,toggleGroup:i,isCollapsed:a,rowColorStyles:l}){let c=t.render_type==="row_total",f=t.render_type==="row_subtotal",u=t.__hide_cell||{},p=Jt(ge(e),e,s);s.section_indent&&(n.displayInset||n.insetGroups?.has(t.__parent_key))&&!f&&!c&&($t(s,e)||!s.stub&&r===0)&&(p.paddingLeft=Er(Number(n.displayInset)||1,s,n.displayToggleDepth));let d=n.accordion?Ds(t,r,n):0;if(d>0){let rt=r===0&&!n.rowNumbers?"0.25rem":"0.375rem";p.paddingLeft=`calc(${rt} + ${d}rem)`}let h=b("td",{class:`et-td${$t(s,e)?" et-stub":""}`,style:p}),m=_c(e,t,s),y=e.fmt_column&&t[e.fmt_column]!=null?String(t[e.fmt_column]):e.fmt,g=(rt=!0)=>{if(Ws(h,e,t,s,y),e.cell_style?.color&&(h.style.color=Z(e.cell_style.color)),xc(h,e,t,n,o,m.style,rt,s),e.font_color||e.cell_style?.color||m.style?.color){De(h);for(let xt of h.querySelectorAll(".et-chip"))De(xt),xt.style.color="inherit"}return h};if(n.section&&r<n.dimCount){let rt=c?0:f?(t.__level??n.dimCount)-1:n.dimCount-1;if(r===rt)f&&(h.rowSpan=n.rowspans?.[o]??1);else return r>rt?g(!1):null}l&&(Gt(h,l.backgroundColor),h.style.color=l.color,Bt(h,{policy:"cell"})),e.highlight&&Gt(h,e.highlight);let w=e.cell_style||{};w.background_column&&t[w.background_column]!=null?Gt(h,Tt(String(t[w.background_column]),w)):w.background&&Gt(h,w.background),(e.highlight||w.background||w.background_column)&&Bt(h,{policy:"cell"}),w.color&&(h.style.color=Z(w.color)),w.border&&(h.style.border=w.border),w.padding&&(h.style.padding=w.padding),e.viz_include_subtotals===!1&&f&&e.viz&&h.classList.add("et-no-viz");let E=(t.__level??0)-1;if(f&&r===E&&!n.section){let rt=b("button",{class:`et-chevron${a?"":" et-chevron-open"}`,type:"button","aria-label":`Toggle group ${t[e.name]??""}`,"aria-expanded":String(!a),onclick:xt=>{xt.stopPropagation(),i(t.__group_key,!0)}},"\u25B6");h.append(rt),h.dataset.groupKey=t.__group_key,h.addEventListener("click",xt=>{xt.stopPropagation(),i(t.__group_key,!1)})}let L=e.repeat_values===!1&&!f&&!c&&n.previousDetailRow&&Object.is(t[e.name],n.previousDetailRow[e.name]);if(u[e.name]||L)return g(!1);if(e.template){let rt=String(e.template).replace(/\{(\w+)\}/g,(xt,At)=>{let G=t[At];if(G==null)return"";let ct=(e.template_fmt||{})[At];return pt(G,ct,{type:e.type,fallback:Kr(G)})});return h.append(b("span",{class:"et-cell-value"},Mt(rt))),g()}let N=t[e.name],O=yc(e,t,N,s);if(O!=null)return h.append(b("span",{class:"et-cell-value et-substituted"},O)),g();if(N!=null&&(typeof N=="number"||typeof N=="string"&&N.trim()!==""&&!isNaN(Number(N)))){let rt=Number(N);e.blank_below!=null&&rt<e.blank_below&&(N=null),e.blank_above!=null&&rt>e.blank_above&&(N=null)}if(N==null&&!e.encodings?.length){if(e.viz==="delta")h.append(Hn(e,N));else{let rt=e.null_text??s.null_text??"\u2013";h.append(b("span",{class:"et-null"},String(rt)))}return g()}let C=e.fmt_column&&t[e.fmt_column]!=null?String(t[e.fmt_column]):e.fmt,j=(e.align_decimals??s.align_decimals)&&n.decimals.has(e.name)?Ts(C||"num",n.decimals.get(e.name)):C,B=m.fmt!=null?m.fmt:c&&e.total_fmt?e.total_fmt:f&&e.subtotal_fmt?e.subtotal_fmt:j,U=(rt,xt={})=>{if(rt==null)return String(e.null_text??s.null_text??"\u2013");let At=pt(rt,xt.format??B,{type:typeof rt=="number"?"number":e.type,range:n.formatRanges.get(e.name),fallback:Kr(rt),relative:e.relative});return Number(rt)<0&&e.bracket_negatives?`(${String(At).replace(/^-/,"")})`:At},Y=U(N);y=B;let X=null;if(e.viz==="color"&&!c&&!(f&&e.viz_include_subtotals===!1)){let rt=n.ranges.get(e)||n.ranges.get(e.name);(rt||(e.color_options||{}).conditional_colors)&&(X=kn(e,t,rt||{min:0,max:0},n.colorScales.get(e)||n.colorScales.get(e.name)))}let Nt=(e.red_negatives||e.negative_color)&&!isNaN(Number(N))&&Number(N)<0,dt=kc(e,N,Y,n,t,U,B);if(dt.classList?.contains("et-marks")){let rt=dt.querySelectorAll(":scope > .et-mark-band, :scope > .et-mark-gridline, :scope > .et-mark-reference");if(rt.length){h.classList.add("et-has-guides");for(let xt of[!1,!0]){let At=[...rt].filter(ct=>ct.classList.contains("et-mark-centerline")===xt);if(!At.length)continue;let G=b("div",{class:"et-cell-guide-track"},At);h.append(b("div",{class:`et-cell-guides${xt?" et-cell-guides-foreground":""}`,"aria-hidden":"true"},G))}}}Nt&&(dt.classList?.add("et-negative"),e.negative_color&&(dt.style.color=Z(e.negative_color)));let mt=e.link?ve(t[e.link]):null;return mt&&t.render_type!=="row_total"?h.append(b("a",{class:"et-cell-link",href:String(mt),target:e.link_new_tab?"_blank":null,rel:e.link_new_tab?"noopener noreferrer":null},e.link_label?e.link_label:dt)):h.append(dt),X&&(Gt(h,X.backgroundColor),h.style.color=X.color,h.classList.add("et-color-cell"),Bt(h,{policy:"cell"})),g()}function kc(t,e,r,n,o,s,i){let a=o.render_type==="row_subtotal",l;if(t.encodings&&t.encodings.length&&o.render_type!=="row_total")l=ui(t,o,n.ranges.get(t)||n.ranges.get(t.name),s,{columns:n.columns,options:n.options,formatCode:i});else if(t.viz==="bar"&&!(a&&t.viz_include_subtotals===!1)&&o.render_type!=="row_total")l=di(t,e,r,n.ranges.get(t)||n.ranges.get(t.name),o);else if(t.viz==="delta")l=Hn(t,e);else if(t.viz==="sparkline")l=Gn(t,e,n.sparklineScales?.get(t),n.ranges.get(t));else if(t.viz==="symbols")l=pi(t,e,r);else if(t.html)l=b("span",{html:String(e)});else if(t.markdown)l=b("span",{class:"et-cell-value"}),l.append(me(String(e)));else if(t.logo&&o[t.logo]){let c=String(o[t.logo]),f=t.logo_options||{};l=b("span",{class:"et-cell-media"},[b("img",{class:"et-cell-logo",src:`https://img.logo.dev/${encodeURIComponent(c)}`,alt:c,loading:"lazy",style:f.height?{height:`${f.height}px`}:{}}),b("span",{class:"et-cell-media-label"},Mt(r))])}else if(t.image&&o[t.image]){let c=t.image_options||{};l=b("span",{class:"et-cell-media"},[b("img",{class:"et-cell-image",src:String(o[t.image]),alt:String(c.alt||""),style:{...c.height?{height:`${c.height}px`}:{},...c.width?{width:`${c.width}px`}:{}}}),b("span",{class:"et-cell-media-label"},Mt(r))])}else if(t.icon_map&&t.icon_map[String(e)]!=null){let c=t.icon_map[String(e)];l=/^(https?:|data:|\/)/.test(c)?b("span",{class:"et-cell-icon"},[b("img",{class:"et-icon-image",src:c,alt:String(e),loading:"lazy",title:String(e)})]):b("span",{class:"et-cell-icon et-icon-glyph",title:String(e)},c)}else if(t.type==="boolean"&&t.boolean_options){let c=t.boolean_options,f=e===!0||e===1||e==="true",u=(f?c.true_text:c.false_text)??r,p=f?c.true_symbol:c.false_symbol;l=b("span",{class:`et-cell-value et-boolean ${f?"et-boolean-true":"et-boolean-false"}`},p?[b("span",{class:"et-boolean-symbol"},p),` ${u}`]:u)}else if(t.viz==="chip"){let c=n.ranges.get(t)||n.ranges.get(t.name),f=c||(t.color_options||{}).conditional_colors?kn(t,o,c||{min:0,max:0},n.colorScales.get(t)||n.colorScales.get(t.name)):null,u=b("span",{class:"et-chip"},Mt(r)),p=(t.chip_options||{}).min_width;p!=null&&(u.style.minWidth=typeof p=="number"?`${p}px`:String(p)),f&&(u.style.backgroundColor=f.backgroundColor,u.style.color=ue(f.backgroundColor),Bt(u)),l=u}else l=b("span",{class:"et-cell-value"},Mt(r));return l}function Gr(t,e,r,n,o){let s=r.options;t.render_type==="row_section"&&t.__combined?t={...t,render_type:"row_subtotal",__level:0,[e[0]?.name]:t.__label}:["row_total","row_subtotal"].includes(t.render_type)&&t.__label&&e[0]&&t[e[0].name]==null&&(t={...t,[e[0].name]:t.__label});let i=t.render_type||"cell_data";if(i!=="cell_data"&&(r.previousDetailRow=null),i==="row_section"){let m=e.length+(r.rowNumbers?1:0)+(s.link?1:0),y=t.__label??(e[0]?t[e[0].name]:""),g=t.__align==="center"?"center":"left",w=je(r.shadingCounter.value++,s);return b("tr",{class:`et-row et-row-section${w?" et-row-shaded":""}`},[b("td",{class:`et-td et-section-cell et-section-${g}`,colspan:m},String(y??""))])}if(i==="row_spacer"){let m=e.length+(r.rowNumbers?1:0)+(s.link?1:0),y=t.__height==null?{}:{height:typeof t.__height=="number"?`${t.__height}px`:String(t.__height)};return b("tr",{class:"et-row et-row-spacer"},[b("td",{class:"et-td et-spacer-cell",colspan:m,style:y})])}let a=i==="row_total",l=i==="row_subtotal",c=l&&t.__group_key&&o.isCollapsed(t.__group_key),f=s.link&&ve(t[s.link]),u=s.row_conditional_colors?t[s.row_conditional_colors]:null,p=typeof u=="string"?we(Tt(u,s)):null,d=b("tr",{class:["et-row",a?"et-row-total":"",l?"et-row-subtotal":"",t.__combined?"et-row-combined":"",f?"et-row-link":"",l?"et-row-collapsible":"",(i==="cell_data"||t.__combined)&&je(r.shadingCounter.value++,s)?"et-row-shaded":""].filter(Boolean).join(" ")});if(f&&d.addEventListener("click",()=>{window.location.href=f}),Qs(d,t,r.selected,s,o.model,o.findSelectedRow),r.rowNumbers){let m=b("td",{class:"et-td et-row-num","data-column-index":0},String((r.rowNumberBase||0)+n+1));p&&(Gt(m,p.backgroundColor),m.style.color=p.color,Bt(m,{policy:"cell"})),d.append(m)}let h=n;if(e.forEach((m,y)=>{let g=hi({row:t,col:m,index:y,ctx:r,rowIndex:h,options:s,toggleGroup:(w,E)=>o.toggleGroup(w,E),isCollapsed:c,rowColorStyles:p});g&&(de(g,m,y,r),d.append(g))}),s.link){let m=b("td",{class:"et-td et-td-chevron"});f&&m.append(b("span",{class:"et-row-chevron"},"\u203A")),d.append(m)}return r.previousDetailRow=i==="cell_data"?t:null,d}function mi(t,e,r,n){let o={...r},s=o.options,i=b("table",{class:`et-table${o.hasTopAxis?" et-has-top-axis":""}`}),a=ri(t,{rowNumbers:o.rowNumbers,link:!!s.link});a&&i.append(a);let l=n.header;!o.isEmpty&&o.stats&&l.append(n.statistics),o.hasTopAxis&&wc(l,t,o),i.append(l);let c=b("tbody");if(o.shadingCounter={value:0},o.previousDetailRow=null,o.isEmpty){c.classList.add("et-empty-body"),c.dataset.emptyMessage=o.emptyMessage;for(let f=0;f<o.emptyRows;f++)c.append(Mc(t,o))}else{if(o.continuationRow){let f=Gr(o.continuationRow,t,o,0,n);f.classList.add("et-row-continuation"),c.append(f)}if(o.displayEntries){for(let f of o.displayEntries)f.kind==="data"?(o.displayInset=f.inset?f.depth:0,o.displayToggleDepth=f.toggleDepth||0,c.append(Gr(f.row,t,o,f.ordinal-o.rowNumberBase,n))):(o.previousDetailRow=null,c.append(ni(f,t,o,s)));o.displayInset=!1,o.displayToggleDepth=0}else e.forEach((f,u)=>c.append(Gr(f,t,o,u,n)))}return i.append(c),o.hasBottomAxis&&i.append(b("tfoot",{},gi(t,o,"bottom"))),Un(i,o.footnotes.length,s),i}function wc(t,e,r){let n=new Set;if(!r.stats)for(let o of t.querySelector(".et-header-leaves").children){let s=Number(o.dataset.columnStart),i=s-(r.rowNumbers?1:0),a=e.slice(Math.max(0,i),i+o.colSpan);if(!(i>=0&&a.some(c=>c.encodings&&c.scale?.axis&&c.scale.axis_position!=="bottom"))){o.rowSpan=2;for(let c=s;c<s+o.colSpan;c++)n.add(c)}}t.append(gi(e,r,"top",n))}function gi(t,e,r,n=new Set){let o=e.options,s=b("tr",{class:`et-axis-row et-axis-row-${r}`});e.rowNumbers&&!n.has(0)&&s.append(b("td",{class:"et-td et-row-num","data-column-index":0}));for(let[i,a]of t.entries()){if(n.has(i+(e.rowNumbers?1:0)))continue;let l=a.scale||{},c=b("td",{class:`et-td${$t(o,a)?" et-stub":""}`});if(de(c,a,i,e),s.append(c),!a.encodings||!l.axis||(l.axis_position||"top")!==r)continue;c.classList.add("et-axis-cell");let{lo:f,hi:u}=Fr(a,e.ranges.get(a)||e.ranges.get(a.name)),p=(a.encodings||[]).some(m=>m.kind==="bar"&&m.direction==="left"),d=jr(f,u,l.transform,p),h=b("div",{class:"et-axis"});if(l.gradient){let m=[...a.encodings].reverse().find(y=>y.gradient);m&&h.append(b("span",{class:"et-axis-gradient","aria-hidden":"true",style:ie(m,{col:a,lo:f,hi:u,pos:d,reverse:p},0,100).style}))}for(let{value:m,major:y}of ci(f,u,4,l.transform)){let g=d(m);if(g==null)continue;let w=Math.max(0,Math.min(100,g)),E=y?pt(m,a.fmt||(Number.isInteger(m)?"num0":"num"),{type:a.type,range:e.formatRanges.get(a.name),fallback:String(m)}):"";h.append(b("span",{class:`et-axis-tick${y?"":" et-axis-tick-minor"}`,"aria-hidden":y?null:"true",style:{left:`${w}%`}},y?b("span",{class:`et-axis-label${w===0?" et-axis-label-start":w===100?" et-axis-label-end":""}`},Mt(E)):null))}c.append(h)}return o.link&&s.append(b("td",{class:"et-td"})),s}function Mc(t,e){let r=e.options,n=b("tr",{class:"et-row et-row-placeholder"}),o=null;e.rowNumbers&&(o=b("td",{class:"et-td et-row-num","data-column-index":0}),n.append(o));for(let[s,i]of t.entries()){let a=b("td",{class:"et-td",style:Jt(ge(i),i,r)});o||(o=a),de(a,i,s,e),n.append(a)}return r.link&&n.append(b("td",{class:"et-td et-td-chevron"})),o&&o.append(document.createTextNode("\xA0")),n}function bi(t,e,r){let{columns:n,hasGroups:o,dimCount:s}=t,{options:i,pageSize:a,pageIndex:l,expandedPage:c,isCollapsed:f,revision:u,anchorGroup:p,selected:d,emptyRows:h}=r,m=t.displayProjection?.page(a,l,c,{isCollapsed:f,revision:u,anchorGroup:p}),y=m||r.paginate(e.rows,e.hasGroups),{rows:g,start:w}=y,E=i.group_type==="section"&&o&&s>0,L=ze(n),N=m?m.entries.length===0:g.length===0,O=n.filter(C=>C.encodings&&C.scale?.axis);return{columns:n,rows:g,pagination:y,context:{columns:t.sourceColumns,options:i,ranges:t.ranges,formatRanges:t.formatRanges,decimals:t.decimals,colorScales:t.colorScales,sparklineScales:t.sparklineScales,hasGroups:o,dimCount:s,section:E,accordion:o&&!E&&s>0,layout:L,subcolumns:L.joins,rowNumbers:!!i.row_numbers,rowNumberBase:w,rowspans:E?Rs(g,s,i.subtotal_position!=="bottom"):null,continuationRow:m?null:Bs(e.rows,w,g),displayEntries:m?.entries,insetGroups:e.insetGroups,selected:d,stats:t.stats,footnotes:[],isEmpty:N,emptyRows:N?h:0,emptyMessage:i.empty_message||"No records",hasTopAxis:!N&&O.some(C=>C.scale.axis_position!=="bottom"),hasBottomAxis:!N&&O.some(C=>C.scale.axis_position==="bottom"),toggleSection:r.toggleSection}}}function yi(t){if(t==null)return"";let e=typeof t=="object"?JSON.stringify(t):String(t);return/[",\r\n]/.test(e)?`"${e.replaceAll('"','""')}"`:e}function _i(t,e){let r=[t.map(n=>yi(n.title||Ft(n.name))).join(",")];for(let n of e)r.push(t.map(o=>yi(n[o.name])).join(","));return r.join(`
`)}var wi={light:{surface:"#ffffff",text:"#172033",muted:"#64748b",accent:"#2563eb",positive:"#15803d",negative:"#dc2626",reference:"#0f766e",selection:"#8b1e2d"},dark:{surface:"#171b24",text:"#e5e7eb",muted:"#a6b0c0",accent:"#7da8ff",positive:"#4ade80",negative:"#fb7185",reference:"#5eead4",selection:"#fb7185"}};function xi(t){if(!ot.valid(t))return t;let e=ot(t),[r,n,o]=e.lch(),s=28+r*.72,i=0,a=n;for(let l=0;l<12;l++){let c=(i+a)/2;ot.lch(s,c,o).clipped()?a=c:i=c}return ot.lch(s,i,o).alpha(e.alpha()).hex()}var Sc=new Set(["color","background","backgroundColor","background-color","font_color","negative_color","highlight","outline","empty_color","marker_color","reference_color","color_negative","bar_color","bar_color_negative","background_color"]),vc=new Set(["members","cells","names","legend","legacy","rows","values","icon_map","template_fmt"]),Cc=new Set(["color_scale","palette"]),Ac={background:"bg",surface:"surface",text:"text",muted:"muted",border:"border",row_border:"row-border",header_bg:"header-bg",header_border:"header-border",header_text:"header-text",hover:"hover",shading:"shading",total_bg:"total-bg",total_text:"total-text",subtotal_bg:"subtotal-bg",link:"link",negative:"negative",positive:"positive",accent:"accent",font:"font",font_size:"font-size"};function ki(t,e={},r=n=>n){let n=e.theme||{},o=wi[t],s={...o,...Object.fromEntries(Object.entries(n).filter(([,u])=>u!=null))};s.surface=n.surface||n.dialog_background||n.background||e.background_color||o.surface,s.neutral=s.surface;for(let u of["surface","neutral","text","muted","accent","positive","negative"]){let p=Z(s[u]);s[u]=ot.valid(p)?p:r(p)}let i=new Map;function a(u,p=e.adapt_colors){if(typeof u!="string")return u;let d=`${!!p}:${u}`;if(i.has(d))return i.get(d);let h;if(u.startsWith("fixed:"))h=Z(u.slice(6));else if(u.startsWith("theme:")){let[m,y="1"]=u.slice(6).split("/"),g=Z(s[m]);h=ot.valid(g)?ot(g).alpha(Number(y)).hex():g||u}else{let m=Z(u);h=t==="dark"&&p?xi(m):m}return i.set(d,h),h}function l(u){if(Array.isArray(u))return u.map(h=>a(h));let p=typeof u=="string"?u.toLowerCase():"",d=p==="tab10"?br(10):Re[p];return d?t!=="dark"?d:/^(green|blue|red|orange|purple|grey|gray|blues|reds|greens|greys|oranges|purples|bugn|bupu|gnbu|orrd|pubu|rdpu|ylgn|ylgnbu|ylorbr|ylorrd)$/.test(p)?ot.scale([s.surface,xi(d.at(-1))]).mode("lab").colors(d.length):d.map(h=>a(h,!0)):u}function c(u,p=""){if(vc.has(p))return u;if(Cc.has(p))return l(u);if(Sc.has(p))return a(u);if(!u||typeof u!="object")return u;if(Array.isArray(u))return u.map(h=>c(h));if(p==="theme")return u;let d=Object.fromEntries(Object.entries(u).map(([h,m])=>[h,p==="colors"?a(m):c(m,h)]));return["gradient","color_options"].includes(p)&&!u.color_scale&&!u.color_stops&&(d.color_scale=f),u.sources&&!u.palette&&(d.palette=l("tab10")),gr(d,a),d}let f=t==="dark"?[s.surface,o.accent]:Oe;return{tokens:s,resolve:a,compile:c,defaultPalette:f}}function Ce(t){return t.parentElement||t.getRootNode()?.host||null}function $c(t,e,r=!1){if(r){for(let s=t;s;s=Ce(s))for(let i of["data-color-scheme","data-theme"]){let a=s.getAttribute(i);if(a==="light"||a==="dark")return a}for(let s=t;s;s=Ce(s)){if(s.classList.contains("dark"))return"dark";if(s.classList.contains("light"))return"light";let i=s.style.colorScheme?.replace(/\bonly\b/g,"").trim();if(i==="light"||i==="dark")return i}}let n=new Map,o=s=>s?(n.has(s)||n.set(s,e.getComputedStyle(s).colorScheme?.replace(/\bonly\b/g,"").trim()),n.get(s)):null;for(let s=t;s;s=Ce(s)){for(let l of["data-color-scheme","data-theme"]){let c=s.getAttribute(l);if(c==="light"||c==="dark")return c}if(s.classList.contains("dark"))return"dark";if(s.classList.contains("light"))return"light";let i=s.style.colorScheme?.replace(/\bonly\b/g,"").trim();if(i==="light"||i==="dark")return i;let a=o(s);if((a==="light"||a==="dark")&&a!==o(Ce(s)))return a}return null}var Hr=class{constructor(e,r,n,o){this.host=e,this.roots=r,this.getOptions=n,this.view=e.ownerDocument.defaultView,this.media=this.view.matchMedia?.("(prefers-color-scheme: dark)"),this.refresh=()=>{if(this.destroyed)return;let s=this.scheme();(s!==this.current||this.paintKey()!==this.lastPaint)&&(this.current=s,this.cache=null,o())},this.observer=new this.view.MutationObserver(this.refresh);for(let s=e;s;s=Ce(s))this.observer.observe(s,{attributes:!0,attributeFilter:["class","style","data-theme","data-color-scheme"]});this.media?.addEventListener("change",this.refresh),this.beforePrint=()=>{this.printing=!0,this.refresh()},this.afterPrint=()=>{this.printing=!1,this.refresh()},this.view.addEventListener("beforeprint",this.beforePrint),this.view.addEventListener("afterprint",this.afterPrint)}scheme(){if(this.printing)return"light";let e=this.getOptions().color_scheme,r=this.host,n=this.getOptions().theme_source||"auto",o=!1;for(let i=r;i;i=Ce(i))if(i.tagName==="MARIMO-ISLAND"){o=!0;break}let s=n==="host"||n==="auto"&&o;return s&&(r=r.ownerDocument.body||r.ownerDocument.documentElement),e&&e!=="auto"?e:$c(r,this.view,s)||(this.media?.matches?"dark":"light")}paintKey(){let e=this.view.getComputedStyle(this.roots[0]);return["surface","text","muted","accent","positive","negative"].map(r=>e.getPropertyValue?.(`--et-${r}`)).join("|")}prepare(e,r,n=null){let o=this.scheme();if(this.current=o,this.cache?.columns===e&&this.cache.options===r&&this.cache.rowLayout===n&&this.cache.scheme===o)return this.cache.result;this.apply(o,ki(o,r).tokens,r);let s=Mn(this.roots[0]),i;try{i=ki(o,r,c=>s.color(c).hex())}finally{s.destroy()}let a=i.compile(r);a.color_scale||=i.defaultPalette;let l={columns:i.compile(e),options:a,rowLayout:i.compile(n),colors:i};return this.cache={columns:e,options:r,rowLayout:n,scheme:o,result:l},this.lastPaint=this.paintKey(),l}apply(e,r,n){let o=(a,l)=>`color-mix(in srgb, ${a} ${l*100}%, transparent)`,s={bg:wi[e].surface,surface:r.surface,text:r.text,muted:r.muted,border:o(r.muted,.3),"row-border":o(r.muted,.22),"header-bg":r.surface,"header-border":o(r.text,.4),"header-text":r.text,hover:o(r.text,.08),shading:o(r.text,.04),"total-bg":o(r.muted,.16),"subtotal-bg":o(r.muted,.1),"total-text":r.text,link:r.accent,negative:r.negative,positive:r.positive,accent:r.accent,reference:r.reference,selection:r.selection,"axis-text":e==="light"?"#000000":r.text},i={...n.theme};i.background||=n.background_color,i.header_bg||=n.header_color,i.header_text||=n.header_font_color,i.total_bg||=n.total_row_color,i.total_text||=n.total_font_color,i.row_border||=typeof n.row_lines=="string"?n.row_lines:null;for(let[a,l]of Object.entries(Ac))i[a]&&(s[l]=Z(i[a]));for(let a of this.roots){a.dataset.colorScheme=e,a.style.colorScheme=e;for(let[l,c]of Object.entries(s))a.style.setProperty(`--et-${l}`,c);for(let l of["font","font-size"])s[l]||a.style.removeProperty(`--et-${l}`)}}destroy(){this.destroyed=!0,this.observer.disconnect(),this.media?.removeEventListener("change",this.refresh),this.view.removeEventListener("beforeprint",this.beforePrint),this.view.removeEventListener("afterprint",this.afterPrint),this.cache=null}};function Nc(t){if(t==null||t==="")return null;let e=String(t).trim();return typeof t=="number"||/^[+-]?\d+(\.\d+)?$/.test(e)?`calc(var(--et-font-size-base, 0.75rem) + ${Number(e)*.0625}rem)`:e}var Vn=class{constructor(e,r,n=r){this.model=e,this.el=r,this.container=n,this.destroyed=!1,this._state={sort:null,search:"",page:0,collapsed:new Set,sectionCollapsed:new Set,expanded:new Set,hidden:new Set,statsMembers:new Map},this._pipeline=new Rr,this._groupVersion=0,this._pageCount=1,this._pageSizeOverride=null,this._expandedPages=new Ir,this._expandedProjection=null,this._holdController=new Dr(o=>this._advance(o)),this._build()}get rows(){return this.model.get("rows")||[]}get columns(){return this._presentation?.columns||this.model.get("columns")||[]}get options(){return this._presentation?.options||this.model.get("options")||{}}_build(){this.root=b("div",{class:"et-root",dataset:{widget:"evidence-table"}}),this.titlebar=b("div",{class:"et-titlebar"}),this.toolbar=b("div",{class:"et-toolbar"}),this.scroller=b("div",{class:"et-scroller"}),this.body=b("div",{class:"et-body"},this.scroller),this.loadingOverlay=b("div",{class:"et-loading-overlay",role:"status","aria-live":"polite","aria-hidden":"true"},[b("span",{class:"et-spinner","aria-hidden":"true"}),"Processing\u2026"]),this.body.append(this.loadingOverlay),this.footer=b("div",{class:"et-footer"}),this.footnotesEl=b("div",{class:"et-footnotes"}),this.caption=b("div",{class:"et-caption"}),this.root.append(this.titlebar,this.toolbar,this.body,this.footer,this.footnotesEl,this.caption),this._loadingController=new Br(this.root,this.loadingOverlay,this.el);let e=this.options.default_sort;e&&e.column&&(this._state.sort={column:e.column,direction:e.direction==="asc"?"asc":"desc"}),this._baselineHeight=0,this._baselinePageSize=null,this.dialog=b("dialog",{class:"et-dialog","aria-label":"Expanded data table"}),this.expandBtn=b("button",{class:"et-text-btn et-expand-btn",type:"button",title:"Expand table","aria-label":"Expand table","aria-expanded":"false",onclick:()=>this._viewport.toggle()}),this.expandBtn.textContent="\u26F6 Expand",this.closeBtn=b("button",{class:"et-text-btn et-close-btn",type:"button",title:"Close expanded table (Esc)","aria-label":"Close expanded table",onclick:()=>this._viewport.close()}),this.closeBtn.textContent="\u2715",this.root.append(this.closeBtn),this._tooltips=new Pr(this.root),this.placeholder=document.createComment("evidence-table inline position"),this.container.append(this.placeholder,this.root,this.dialog),this._viewport=new zr({root:this.root,dialog:this.dialog,button:this.expandBtn,placeholder:this.placeholder,scroller:this.scroller,getOptions:()=>this.options,rerender:()=>this.render(),resetBaseline:()=>this._resetBaselineHeight(),getPageSizeOverride:()=>this._pageSizeOverride,setPageSizeOverride:r=>{this._pageSizeOverride=r},getPageMetrics:()=>this._pageMetrics,onExpand:()=>{this._inlinePage=this._state.page,this._state.page=0,this._pageSizeOverride=10,this._expandedPages.reset(),this._expandedProjection=null},onRestore:()=>{this._state.page=this._inlinePage??0},advancePage:r=>this._advance(r)}),this._theme=new Hr(this.el,[this.root,this.dialog],()=>this.model.get("options")||{},()=>this.render(!0)),this._contrast=new yr(this.root,r=>this._viewport.frame(r)),this.render(),this.setLoading(this.model.get("loading"))}_applyTheme(){this._presentation=this._theme.prepare(this.model.get("columns")||[],this.model.get("options")||{},this.model.get("row_layout"));let e=Nc(this.options.font_size)||this.options.theme?.font_size;for(let r of[this.root,this.dialog])e?r.style.setProperty("--et-font-size",e):r.style.removeProperty("--et-font-size")}destroy(){this.destroyed=!0,this._holdController.stop(),this._loadingController.destroy(),this._viewport.destroy(),this._contrast.destroy(),this._theme.destroy(),this._tooltips.destroy(),this._pipeline.clear(),this.dialog.remove(),this.placeholder.remove(),this.root.remove()}_defaultCollapsed(){return this.options.group_type==="section"?!1:this.options.collapsible&&this.options.collapsed!==!1}_isCollapsed(e){return this._defaultCollapsed()?!this._state.expanded.has(e):this._state.collapsed.has(e)}_toggleGroup(e,r=!1){let n=this._defaultCollapsed()?this._state.expanded:this._state.collapsed;n.has(e)?n.delete(e):n.add(e),this._groupVersion++,this._resetBaselineHeight(),this.render(),r&&[...this.scroller.querySelectorAll("td[data-group-key]")].find(s=>s.dataset.groupKey===e)?.querySelector("button.et-chevron")?.focus({preventScroll:!0})}_toggleSection(e){let r=this._state.sectionCollapsed;r.has(e)?r.delete(e):r.add(e),this._sectionAnchor=e,this._groupVersion++,this._resetBaselineHeight(),this.render();let n=[...this.scroller.querySelectorAll("button[data-section-key]")];(n.find(o=>o.dataset.sectionKey===e)||n[0])?.focus({preventScroll:!0})}_effectivePageSize(){return this._pageSizeOverride??this.options.page_size}_paginate(e,r){if(this._viewport.expanded){let o=this._expandedPages.project(e.length,this._effectivePageSize(),this._state.page);return{...o,rows:e.slice(o.start,o.end)}}let n=Ps(e,this._effectivePageSize(),this._state.page,this.options,r);return this._state.page=n.page,n}render(e=!1){this._tooltips.hide(),this._applyTheme();let r=this.options;this.root.style.maxWidth=this._viewport.expanded||r.width==null?"":typeof r.width=="number"?`${r.width}px`:String(r.width),this._viewport.expanded?this.scroller.style.maxHeight="none":r.max_height?this.scroller.style.maxHeight=typeof r.max_height=="number"?`${r.max_height}px`:r.max_height:this.scroller.style.maxHeight="",this.root.classList.toggle("et-wrap",!!r.wrap),this.root.classList.toggle("et-nowrap-titles",r.wrap_titles===!1),this.root.classList.toggle("et-no-row-lines",r.row_lines===!1),this.root.classList.toggle("et-no-border",r.border===!1),this.root.classList.toggle("et-row-shading",!!r.row_shading),this.root.classList.toggle("et-compact",!!r.compact),this.root.classList.toggle("et-stretch-off",r.stretch===!1),this.root.classList.toggle("et-group-gap",!!r.group_gap);let n=r.search&&this.toolbar.contains(this.root.getRootNode().activeElement);!e&&!n&&this._renderToolbar();let o=this._pipeline.get({rows:this.rows,columns:this.columns,options:r,rowLayout:this._presentation.rowLayout,search:this._state.search,hidden:Pn(this.columns,this._state.hidden),sort:this._state.sort}),{columns:s}=o;this._renderTitle(s);let i=this._pipeline.visible(o,this._groupVersion,w=>this._isCollapsed(w));e&&(this._expandedProjection=o),this._viewport.expanded&&(this._expandedProjection!==o||this._expandedGroupVersion!==this._groupVersion)&&(this._expandedPages.reset(),this._state.page=0,this._expandedProjection=o,this._expandedGroupVersion=this._groupVersion);let a=bi(o,i,{options:r,pageSize:this._effectivePageSize(),pageIndex:this._state.page,expandedPage:this._viewport.expanded?w=>this._expandedPages.project(w,this._effectivePageSize(),this._state.page):null,isCollapsed:w=>this._state.sectionCollapsed.has(w),revision:this._groupVersion,anchorGroup:this._sectionAnchor,selected:r.select?this.model.get("selected"):null,emptyRows:this._emptyRowCount(r),paginate:(w,E)=>this._paginate(w,E),toggleSection:w=>this._toggleSection(w)});this._sectionAnchor=null;let{rows:l,pageCount:c,page:f,total:u,start:p}=a.pagination;this._pageMetrics={count:a.context.displayEntries?a.pagination.unitCount:l.length,remaining:u-p,projection:o},this._state.page=f,this._pageCount=c;let d=null,h=0;for(let w of s){let E=w.rotate_title??($t(r,w)?null:r.rotate_titles);if(typeof E!="number")continue;d=E;let L=r.format_titles===!1?w.name:w.title||Ft(w.name);h=Math.max(h,String(L).length)}if(d!=null){let w=Math.abs(Math.sin(Math.abs(d)*Math.PI/180));this.root.style.setProperty("--et-th-oblique-height",`${Math.max(4,h*.62*w+1.5).toFixed(2)}em`),this.root.classList.add("et-oblique")}else this.root.classList.remove("et-oblique"),this.root.style.removeProperty("--et-th-oblique-height");this.scroller.replaceChildren();let{footnotes:m,isEmpty:y}=a.context;y&&!s.length?this.scroller.append(b("div",{class:"et-empty"},[b("span",{},r.empty_message||"No records")])):this.scroller.append(mi(s,l,a.context,{header:this._renderHeader(s,a.context),statistics:!y&&a.context.stats?this._renderStatsRow(s,a.context):null,model:this.model,isCollapsed:w=>this._isCollapsed(w),toggleGroup:(w,E)=>this._toggleGroup(w,E),findSelectedRow:w=>[...this.scroller.querySelectorAll("tr.et-row-selectable")].find(E=>E.dataset.selectKey===String(w))}));let g=!!r.caption||m.length>0||(r.footnotes||[]).length>0;this._renderFooter(f,c,u,g,a.pagination),this._renderFootnotes(m,r.footnotes),this.caption.replaceChildren(),r.caption&&this.caption.append(me(r.caption)),this._updateBaselineHeight(),this._viewport.observeTable(this.scroller.querySelector("table")),this._contrast.watch(),this._tooltips.refresh(),this._viewport.frame(()=>{this._viewport.applyFrozenOffsets(),_r(this.root),Lr(this.root),this._viewport.expanded&&this._viewport.fit()}),this.el.dataset.rowCount=String(a.pagination.matchingTotal??u),this.el.dataset.renderCount=String((Number(this.el.dataset.renderCount)||0)+1)}setLoading(e){this._loadingController.set(e)}_updateBaselineHeight(){if(this._viewport.expanded){this._resetBaselineHeight();return}let e=this._effectivePageSize();e!==this._baselinePageSize&&(this._baselinePageSize=e,this._baselineHeight=0,this.scroller.style.minHeight="");let r=this.scroller.getBoundingClientRect().height;r<=0||(this._baselineHeight=Math.max(this._baselineHeight||0,r),this.scroller.style.minHeight=`${Math.round(this._baselineHeight)}px`,this.el.dataset.baselineHeight=String(Math.round(this._baselineHeight)))}_renderTitle(e){let{title:r,subtitle:n,info:o,info_link:s,info_link_title:i}=this.options;this.titlebar.replaceChildren();let a=b("div",{class:"et-title-text"});if(r){let c=b("span",{class:"et-title"});if(c.append(me(r)),o){let f=b("span",{class:"et-info",title:o},"\u24D8"),u=ve(s);if(u){let p=b("a",{href:u,target:"_blank",rel:"noopener noreferrer",class:"et-info-link"},"\u24D8");p.title=o,i&&p.append(document.createTextNode(` ${i}`)),a.append(c," ",p)}else a.append(c," ",f)}else a.append(c)}if(n){let c=b("div",{class:"et-subtitle"});c.append(me(n)),a.append(c)}a.childElementCount&&this.titlebar.append(a);let l=Ns(e,this.columns,this.options);l&&this.titlebar.append(l)}_renderToolbar(){let e=this.options;this.toolbar.replaceChildren();let r=b("div",{class:"et-toolbar-left"}),n=b("div",{class:"et-toolbar-right"});if(e.search){let o=b("input",{class:"et-search",type:"search",placeholder:"Search","aria-label":"Search table",value:this._state.search});o.addEventListener("input",()=>{this._state.search=o.value,this._state.page=0,this.render(),requestAnimationFrame(()=>{let s=this.toolbar.querySelector(".et-search");s&&(s.focus(),s.setSelectionRange(s.value.length,s.value.length))})}),r.append(o)}this.toolbar.append(r,n),this.toolbar.classList.toggle("et-toolbar-empty",!r.childElementCount&&!n.childElementCount)}_emptyRowCount(e){if(this._viewport.expanded)return Math.min(200,Number(this._effectivePageSize())||10);let r=Number(e.empty_rows);if(Number.isFinite(r)&&r>0)return Math.min(Math.floor(r),200);let n=Number(this._effectivePageSize());return Number.isFinite(n)&&n>0?Math.min(Math.floor(n),200):10}_renderStatsRow(e,r){return xs({columns:e,layout:r.layout,stats:r.stats,formatRanges:r.formatRanges,options:this.options,rowNumbers:r.rowNumbers,selections:this._state.statsMembers,onLayout:()=>this._viewport.frame(()=>{this._viewport.applyFrozenOffsets(),this._viewport.expanded&&this._viewport.fit()})})}_renderHeader(e,r){return Ms({columns:e,rowNumbers:r.rowNumbers,options:this.options,onInfo:(n,o)=>Us(n,o,this.options),sort:this._state.sort,onSort:n=>{this._sortColumn(n),[...this.scroller.querySelectorAll("thead [data-column]")].find(s=>s.dataset.column===n)?.focus({preventScroll:!0})}})}_sortColumn(e){let r=this._state.sort;!r||r.column!==e?this._state.sort={column:e,direction:"desc"}:r.direction==="desc"?this._state.sort={column:e,direction:"asc"}:this._state.sort=null,this._state.page=0,this.render()}_renderFootnotes(e,r){this.footnotesEl.replaceChildren();let n=e.map(s=>({mark:Ur(s.index,this.options,e.length),text:s.text,rows:[...s.rows].sort((i,a)=>i-a)}));for(let s of r||[])n.push({mark:null,text:String(s),rows:[]});if(!n.length)return;let o=b("ol",{class:"et-footnotes-list"});for(let s of n){let i=b("li",{class:"et-footnote-item"});s.mark&&i.append(b("sup",{class:"et-footnote-mark"},s.mark)),i.append(document.createTextNode((s.mark?" ":"")+s.text)),s.rows.length&&i.append(b("span",{class:"et-footnote-rows"},` (rows ${Kn(s.rows)})`)),o.append(i)}this.footnotesEl.append(o)}_renderFooter(e,r,n,o,s={}){if(this.footer.replaceChildren(),this.root.classList.toggle("et-float-actions",r<=1&&!s.collapsedGroups&&!!o),r>1||s.variable&&e>0||s.collapsedGroups){let i=b("div",{class:"et-page-controls"}),a=this._effectivePageSize(),l=s.start==null?e*a+1:s.start+1,c=s.end==null?Math.min(n,(e+1)*a):s.end,f=(u,p,d)=>{let h=b("button",{class:"et-btn et-page-btn",type:"button",disabled:d,"aria-label":p==="next"?"Next page":"Previous page",title:this._viewport.expanded?p==="next"?"Next page (\u2192)":"Previous page (\u2190)":null},u);return h.addEventListener("pointerdown",m=>{m.button!==void 0&&m.button!==0||this._holdController.start(p)}),h.addEventListener("click",()=>{this._holdController.consumeClick()||this._gotoPage(this._state.page+(p==="next"?1:-1))}),h};i.append(f("\u2039","prev",e===0),b("span",{class:"et-page-current"},s.variable?String(e+1):`${e+1}/${r}`),f("\u203A","next",e>=r-1),b("span",{class:"et-page-info"},s.collapsedGroups?`(${l}\u2013${c} of ${n} items \xB7 ${s.matchingTotal} matching records)`:`(${l}\u2013${c} of ${n})`)),this.footer.append(i)}this.footer.append(this._renderActions())}_renderActions(){let e=b("div",{class:"et-table-actions"});return this.options.download&&e.append(b("button",{class:"et-text-btn et-download-btn",type:"button",title:"Download CSV","aria-label":"Download CSV",onclick:()=>this._downloadCsv()},"\u2913 Download")),e.append(this.expandBtn),e}_gotoPage(e){if(this._viewport.expanded){this._viewport.fit();let n=this._expandedPages.move(e);if(!n)return;this._pageSizeOverride=n.size,this._state.page=n.page,this.scroller.scrollTop=0,this.render(),this._viewport.fit();return}let r=Math.max(1,this._pageCount||1);this._state.page=Math.min(Math.max(0,e),r-1),this.render()}_advance(e){let r=this._state.page+(e==="next"?1:-1);return r<0||r>=this._pageCount?!1:(this._gotoPage(r),!0)}_resetBaselineHeight(){this._baselineHeight=0,this._baselinePageSize=null,this.scroller.style.minHeight=""}_downloadCsv(){let e=Pn(this.columns,this._state.hidden),r=Mr(this.columns.filter(f=>!e.has(f.name)),this.options),n=$r(this.rows,this.columns,this._state.search,e),o=Nr(n,this.columns,this._state.sort),s=this.model.get("row_layout"),i=s?.legacy?xr(s,this.rows,o,f=>this._isCollapsed(f)).filter(f=>!f.render_type||f.render_type==="cell_data"):s?.version?_s(s,this.rows,o,"all",0).rows:Ar(o,f=>this._isCollapsed(f)),a=new Blob([_i(r,i)],{type:"text/csv;charset=utf-8;"}),l=URL.createObjectURL(a),c=document.createElement("a");c.href=l,c.download=(this.options.title||"table").replace(/\s+/g,"_").toLowerCase()+".csv",c.click(),URL.revokeObjectURL(l)}};function Mi({model:t,el:e,container:r=e}){e.classList.add("evidential-widget");let n=new Vn(t,e,r),o=()=>n.render(),s=!1,i=()=>{n._pipeline.clear(),n._theme.cache=null,!s&&(s=!0,queueMicrotask(()=>{s=!1,n.destroyed||n.render()}))},a=()=>n.setLoading(t.get("loading")),l=()=>{let c=n._theme.cache?.options||{},f=t.get("options")||{};if(c===f){i();return}let u=new Set(["color_scheme","theme_source","adapt_colors","theme","color_scale","background_color","header_color","header_font_color","total_row_color","total_font_color"]);[...new Set([...Object.keys(c),...Object.keys(f)])].filter(d=>c[d]!==f[d]).every(d=>u.has(d))?n.render(!0):i()};return t.on("change:rows",i),t.on("change:columns",i),t.on("change:options",l),t.on("change:row_layout",i),t.on("change:loading",a),t.on("change:selected",o),()=>{t.off("change:rows",i),t.off("change:columns",i),t.off("change:options",l),t.off("change:row_layout",i),t.off("change:selected",o),t.off("change:loading",a),n.destroy()}}function Si(t,e,r){let n=t.shadowRoot||t.attachShadow({mode:"open"}),o=t.ownerDocument.createElement("style");o.textContent=`:host { display: block; min-width: 0; }
    *, *::before, *::after { box-sizing: border-box; }
    table { font: inherit; color: inherit; }
    .evidential-widget > :is(.et-root, .edg-root) { font-family: var(--et-font, Arial, sans-serif);
      font-style: normal; font-weight: normal; letter-spacing: normal;
      text-transform: none; text-indent: 0; text-align: start; }
    ${e}`;let s=t.ownerDocument.createElement("div");s.className="evidential-widget";let i=t.ownerDocument.createElement("style"),a=()=>{i.textContent=r?.get("options")?.css||""};return a(),r?.on("change:options",a),n.append(o,i,s),{mount:s,destroy(){r?.off("change:options",a),s.remove(),i.remove(),o.remove()}}}var Y1={render({el:t,model:e}){let r=Si(t,`/* Evidence-style table widget for Marimo. */

.evidential-widget {
  width: 100%;
  --et-bg: transparent;
  /* Opaque surface used by the fullscreen dialog and frozen columns. \`Canvas\`
     follows the active color-scheme, so it matches light/dark notebooks. */
  --et-surface: Canvas;
  --et-text: inherit;
  --et-muted: #94a3b8;
  --et-border: rgba(148, 163, 184, 0.3);
  --et-row-border: rgba(148, 163, 184, 0.22);
  --et-header-bg: var(--et-surface);
  --et-header-border: color-mix(in srgb, CanvasText 40%, transparent);
  --et-header-text: inherit;
  --et-hover: color-mix(in srgb, CanvasText 8%, transparent);
  --et-shading: color-mix(in srgb, CanvasText 4%, transparent);
  --et-total-bg: rgba(148, 163, 184, 0.16);
  --et-subtotal-bg: rgba(148, 163, 184, 0.1);
  --et-link: #2563eb;
  --et-negative: #dc2626;
  --et-accent: #2563eb;
  /* Evidence uses Tailwind's text-xs for the table; \`font_size\` can raise or
     lower it (absolutely, or relatively as \`+N\` / \`-N\` steps). */
  --et-font-size-base: 0.75rem;
  --et-font-size: var(--et-font-size-base);
  --et-section-chevron-width: 0.75em;
  --et-section-toggle-gap: 0.3em;
}

.et-root {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  font-size: var(--et-font-size);
  line-height: 1.25;
  color: var(--et-text);
  background: var(--et-bg);
}

.et-root.et-expanded {
  height: 100%;
  padding: 1.25rem 1.5rem;
  box-sizing: border-box;
  background: var(--et-surface);
}

.et-root.et-expanded .et-body {
  flex: 1 1 0;
  min-height: 0;
}

.et-root.et-expanded .et-scroller {
  flex: 1 1 0;
  min-height: 0;
  max-height: none;
}

.et-root.et-expanded > :not(.et-body) { flex-shrink: 0; }

/* -------------------------------------------------------------- loading --- */
/* Fade the current data out and "Processing\u2026" in over FADE_MS; the reveal is
   instant (transition: 0s) so new data appears the moment it is ready. */
.et-table { transition: opacity 0s; }
.et-root.et-loading .et-table {
  opacity: 0.45;
  transition: opacity 0.6s ease;
}
.et-loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: color-mix(in srgb, var(--et-surface) 55%, transparent);
  backdrop-filter: blur(1px);
  z-index: 40;
  font-size: 1.07em;
  color: var(--et-muted);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0s;
}
.et-root.et-loading .et-loading-overlay {
  opacity: 1;
  transition: opacity 0.6s ease;
}
.et-spinner {
  width: 1rem;
  height: 1.2em;
  border-radius: 50%;
  border: 2px solid color-mix(in srgb, CanvasText 25%, transparent);
  border-top-color: var(--et-accent);
  animation: et-spin 0.7s linear infinite;
}
@keyframes et-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) {
  .et-spinner { animation-duration: 2s; }
  .et-root.et-loading .et-table,
  .et-root.et-loading .et-loading-overlay { transition-duration: 0.01s; }
}

/* ------------------------------------------------------------- titlebar --- */
.et-titlebar:empty { display: none; }
.et-titlebar {
  margin-bottom: 0.35rem;
}
.et-titlebar:has(.et-legends) {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.4rem 1.5rem;
}
.et-titlebar:has(.et-legends) .et-title-text {
  flex: 1 1 12rem;
  min-width: 0;
  overflow-wrap: anywhere;
}
.et-legends {
  flex: 0 1 auto;
  min-width: 0;
  max-width: min(100%, 38rem);
  margin-left: auto;
  padding-inline-end: 0.375rem;
  box-sizing: border-box;
  font-size: 0.9em;
  line-height: 1.35;
}
.et-legends-outlined {
  border: 1px solid var(--et-header-border);
  padding: 0.4em 0.6em;
}
.et-legend-groups, .et-legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem 0.85rem;
}
.et-legend-groups { flex-direction: column; gap: 0.25rem; }
.et-legend-group {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  min-width: 0;
  max-width: 100%;
}
.et-legend-column { flex: 0 0 auto; font-weight: 600; white-space: nowrap; }
.et-legend-column::after { content: ":"; }
.et-legends .et-legend-items {
  flex: 1 1 auto;
  min-width: 0;
  list-style: none;
  padding: 0 0.1em 0 0;
  margin: 0;
  column-gap: 1.25em;
}
.et-legends .et-legend-item {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 0.4em;
  padding: 0;
  margin: 0;
  white-space: nowrap;
}
.et-legend-label { white-space: nowrap; }
.et-legend-column, .et-legend-label { color: color-mix(in srgb, currentColor 72%, transparent); }
.et-legend-swatch {
  flex: 0 0 0.75em;
  width: 0.75em;
  height: 0.75em;
}
.et-legend-swatch-bar { opacity: 0.55; }
.et-legend-swatch-point, .et-legend-swatch-points {
  border-radius: 50%;
  box-shadow: 0 0 0 1px color-mix(in srgb, Canvas 60%, transparent);
}
.et-legend-swatch-range { height: 2px; opacity: 0.9; }
.et-title {
  font-size: 1.4em;
  font-weight: 600;
}
.et-subtitle {
  color: var(--et-muted);
  font-size: 1.07em;
  margin-top: 0.1rem;
}
.et-info, .et-info-link {
  color: var(--et-muted);
  font-size: 1.07em;
  cursor: help;
  text-decoration: none;
}

/* -------------------------------------------------------------- toolbar --- */
.et-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.25rem 0 0.5rem;
}
.et-toolbar-empty { display: none; }
.et-toolbar-left { flex: 1 1 auto; }
.et-toolbar-right { display: flex; gap: 0.35rem; align-items: center; }
.et-search {
  width: 100%;
  max-width: 260px;
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--et-border);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  font: inherit;
  outline: none;
}
.et-search:focus { border-color: var(--et-accent); }
.et-btn, .et-icon-btn {
  border: 1px solid var(--et-border);
  background: transparent;
  color: inherit;
  border-radius: 6px;
  padding: 0.28rem 0.6rem;
  font: inherit;
  cursor: pointer;
  line-height: 1.2;
  touch-action: none;
  -webkit-user-select: none;
  user-select: none;
}
/* Text-only pagination arrows: the border stays (transparent) so the hitbox
   matches the old bordered button exactly. */
.et-page-btn {
  min-width: 2rem;
  border-color: transparent;
  background: transparent;
}
.et-page-btn:active { transform: scale(0.94); }
.et-icon-btn { padding: 0.22rem 0.5rem; font-size: 0.95rem; }
.et-btn:hover, .et-icon-btn:hover { background: var(--et-hover); }
.et-btn:disabled { opacity: 0.4; cursor: default; }

/* -------------------------------------------------------------- scroller -- */
.et-body {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
  width: 100%;
}
.et-scroller {
  position: relative;
  width: 100%;
  overflow: auto;
  border: 1px solid var(--et-border);
  border-radius: 8px;
}
/* border=False drops the frame around the whole table (and its rounded corners). */
.et-root.et-no-border .et-scroller {
  border: none;
  border-radius: 0;
}
.et-table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  margin: 0;
  /* ALA: lining (uppercase-height) tabular numerals in tables of figures. */
  font-variant-numeric: lining-nums tabular-nums;
}
.et-root.et-wrap .et-td { white-space: normal; }
.et-root:not(.et-wrap) .et-td { white-space: nowrap; }
/* Don't stretch the table: size columns to their content (ALA). */
.et-root.et-stretch-off .et-table { width: auto; }
/* In mixed tables, content columns use their intrinsic width while charts
   share the surplus. The table algorithm still accounts for cell padding,
   headers, sub-columns and unbreakable content. */
.et-col-content { width: 1px; }
/* White space as a grouping device (proximity): extra room around group
   boundaries instead of rules or fills. */
.et-root.et-group-gap .et-row-subtotal .et-td,
.et-root.et-group-gap .et-row-total .et-td {
  padding-top: 0.85rem;
}
/* compact density */
.et-root.et-compact .et-td,
.et-root.et-compact .et-th {
  padding-top: 0.1rem;
  padding-bottom: 0.1rem;
}
.et-root.et-compact .et-toolbar { padding: 0.15rem 0 0.3rem; }

/* row-number column */
.et-row-num {
  width: 1px;
  white-space: nowrap;
  text-align: right;
  color: var(--et-muted);
  font-variant-numeric: lining-nums tabular-nums;
}

/* column info icon */
.et-th-info {
  color: var(--et-muted);
  font-size: 0.85em;
}
.et-table thead th,
.et-table thead td {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--et-header-bg);
  color: var(--et-header-text);
}
.et-header-groups th { top: 0; }
.et-th {
  text-align: left;
  font-weight: 600;
  /* Evidence: py-1, first column pl-1 pr-3, others pl-1.5 pr-3. */
  padding: 0.25rem 0.75rem 0.25rem 0.375rem;
  border-bottom: 1px solid var(--et-header-border);
  white-space: nowrap;
  /* Multi-line titles sit on the header rule. */
  vertical-align: bottom;
  user-select: none;
  cursor: pointer;
}
/* Titles may wrap; an explicit \`\\n\` always forces a break (see table.js). Set
   \`wrap_titles=False\` to keep every line as long as it needs to be. */
.et-th-title { white-space: normal; }
.et-root.et-nowrap-titles .et-th-title { white-space: nowrap; }
.et-th:first-child { padding-left: 0.25rem; }
.et-th-group {
  text-align: center;
  font-size: inherit;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: var(--et-muted);
  /* Symmetric padding so the label is centred over its columns. */
  padding-left: 0.75rem;
  padding-right: 0.75rem;
  position: relative;
  /* The inset rule below replaces the full-width cell border. */
  border-bottom: none;
}
.et-th-group:first-child { padding-left: 0.75rem; }
/* A bold rule under the spanner, inset 3px from each edge. */
.et-th-group::after {
  content: "";
  position: absolute;
  left: 3px;
  right: 3px;
  bottom: 0;
  height: 2px;
  background: var(--et-header-border);
}
.et-th-group:not(:last-child) { border-right: none; }
.et-th-group-blank { cursor: default; }
/* An ungrouped column's blank spanner cell gets no rule. */
.et-th-group-blank::after { display: none; }
.et-th:not(.et-th-group):hover { background: var(--et-hover); }
.et-th-inner { display: inline-flex; align-items: center; gap: 0.3rem; }
.et-th-sorted { color: var(--et-accent); }
.et-sort-arrow { font-size: 0.8em; }

/* ----------------------------------------------------------------- rows --- */
.et-td {
  --et-cell-fill: transparent;
  --et-row-tint: transparent;
  --et-selection-tint: transparent;
  /* Evidence: py-1, first column pl-1 pr-3, others pl-1.5 pr-3. */
  padding: 0.25rem 0.75rem 0.25rem 0.375rem;
  border-bottom: 1px solid var(--et-row-border);
  vertical-align: middle;
  /* One paint order for all cells, including frozen columns: selection over
     the cell's color over the row tint. Alpha never fades text or graphics. */
  background-color: var(--et-bg);
  background-image:
    linear-gradient(var(--et-selection-tint), var(--et-selection-tint)),
    linear-gradient(var(--et-cell-fill, transparent), var(--et-cell-fill, transparent)),
    linear-gradient(var(--et-row-tint), var(--et-row-tint));
}
.et-td:first-child { padding-left: 0.25rem; }
/* Shared-header sub-columns retain separate widths and alignment. */
.et-td.et-subcolumn-left { padding-left: 0.15rem; }
.et-td.et-subcolumn-right { padding-right: 0.15rem; }
.et-root.et-no-row-lines .et-td { border-bottom: none; }
/* Outer rules remain visible even when detail row separators are disabled. */
.et-table tbody > tr:first-child > .et-td { border-top: 1px solid var(--et-border); }
.et-table tbody > tr:last-child > .et-td { border-bottom: 1px solid var(--et-border); }
.et-row-shaded .et-td { --et-row-tint: var(--et-shading); }
.et-row:hover .et-td { --et-row-tint: var(--et-hover); }
.et-row-total .et-td {
  font-weight: 600;
  --et-row-tint: var(--et-total-bg);
  color: var(--et-total-text, inherit);
  border-top: 1px solid var(--et-border);
}
.et-row-subtotal .et-td {
  font-weight: 600;
  --et-row-tint: var(--et-subtotal-bg);
}
.et-row-subtotal.et-row-collapsible { cursor: pointer; }
.et-row-link { cursor: pointer; }
/* Selectable rows (opts.select): a row click sets the \`selected\` trait. */
.et-row-selectable { cursor: pointer; }
.et-row.et-row-selected .et-td,
.et-row.et-row-selected:hover .et-td {
  --et-row-tint: transparent;
  --et-selection-tint: color-mix(in srgb, var(--et-accent) 16%, transparent);
}
.et-null { color: var(--et-muted); opacity: 0.75; }
.et-negative { color: var(--et-negative); }
/* A chip: the value in a rounded rectangle, coloured by the same rules as a
   colour cell. The text colour is the contrast colour (white on dark, black on
   light), set inline by \`calculateColorStyles\`. */
.et-chip {
  display: inline-block;
  box-sizing: border-box;
  padding: 0.05rem 0.5rem;
  border-radius: 0.375rem;
  font-weight: 600;
  line-height: 1.3;
  white-space: nowrap;
  /* Centre the label when a min-width makes the chip wider than its text. */
  text-align: center;
  background: color-mix(in srgb, var(--et-muted) 18%, transparent);
}
.et-cell-link { color: var(--et-link); text-decoration: none; }
.et-cell-link:hover { text-decoration: underline; }
.et-cell-media { display: inline-flex; align-items: center; gap: 0.35rem; }
.et-cell-image { height: 1.25em; width: auto; border-radius: 3px; }
.et-cell-logo { height: 1.25em; width: auto; border-radius: 3px; }
.et-td-chevron { width: 1.5rem; text-align: center; color: var(--et-muted); }
.et-row-chevron { font-size: 1.1rem; }

/* ------------------------------------------------------------ chevron --- */
.et-chevron {
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  display: inline-block;
  margin-right: 0.35rem;
  font-size: 0.6rem;
  color: var(--et-muted);
  transition: transform 0.15s ease;
}
.et-chevron-open { transform: rotate(90deg); }

/* ----------------------------------------------------------- bar viz ------ */
/* Pull the bar into the cell's padding (right + top/bottom) and push the value
   back out by the same amount, so the value keeps its position but the bar fills
   the row, leaving ~2px to the separators, without growing the cell. */
.et-bar-cell {
  /* The bar area's 50% must line up with the grid's content-box centre, so the
     right padding is shared between the cell and the centred bar area. */
  --et-bar-pad-right: 0.75rem;
  position: relative;
  display: block;
  min-width: 10rem;
  margin: -0.25rem calc(-1 * var(--et-bar-pad-right)) -0.25rem 0;
  padding: 0.25rem var(--et-bar-pad-right) 0.25rem 0;
}
.et-bar-wrap { position: absolute; inset: 0 4px 0 0; }
.et-bar-negative { left: 4px; right: 0; }
.et-bar {
  position: absolute;
  top: var(--et-bar-pad, 2px);
  bottom: var(--et-bar-pad, 2px);
  left: 0;
  min-width: 1px;
  /* rectangular (no rounded corners) */
  max-width: 100%;
  opacity: 0.35;
}
.et-bar-negative .et-bar { left: auto; right: 0; }
/* A leftward bar fills from the right edge \u2014 the mirror of the default, for a
   back-to-back ("tornado") league table. */
.et-bar-fill-left { left: auto; right: 0; }
/* A vertical benchmark rule at a value (\`bar(reference=N)\`); it is full height
   so it reads as one continuous line down the column, like the centre line. */
.et-bar-reference {
  position: absolute;
  top: var(--et-bar-pad, 0);
  bottom: var(--et-bar-pad, 0);
  width: 1px;
}
.et-bar-reference-label {
  /* A column-level caption: show it once, on the last row, like the source
     chart's "OECD median" note under the axis. */
  display: none;
  position: absolute;
  bottom: 0.1rem;
  padding: 0 0.25rem;
  font-size: 0.72em;
  line-height: 1.2;
  white-space: nowrap;
}
tbody tr:last-child .et-bar-reference-label { display: block; }
.et-bar-label { position: relative; z-index: 1; }
.et-hidden { visibility: hidden; }
.et-no-viz .et-bar-cell { display: none; }

/* Zero-centred "diverging" bar (\`.bar(center=True)\`): a centre line, the bar
   growing left (negative) or right (positive) by magnitude, and the value on
   the opposite side of the line (the Economist's league-table bar). */
/* Full height: the line and bars run edge-to-edge so the centre line reads as
   one continuous rule down the column (the cell's negative margins pull it into
   the row padding, joining the neighbouring rows). */
/* The value and the bar share the cell 50/50: a two-column grid puts the label in
   the half opposite the bar (the label is the in-flow item that gives the cell its
   height), while the axis and bar are absolutely positioned inside it. */
.et-bar-center {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  min-width: 8rem;
}
/* Full height: the line and bars run edge-to-edge so the centre line joins the
   neighbouring rows into one rule down the column. */
.et-bar-center .et-bar-wrap { inset: 0 var(--et-bar-pad-right) 0 0; }
.et-bar-center .et-bar { top: var(--et-bar-pad, 0); bottom: var(--et-bar-pad, 0); }
/* Under \`pad\`, the centre line's ends line up with the first/last bar: it is
   inset only at the top of the first row and the bottom of the last. */
tbody tr:first-child .et-bar-center .et-bar-axis { top: var(--et-bar-pad, 0); }
tbody tr:last-child .et-bar-center .et-bar-axis { bottom: var(--et-bar-pad, 0); }
.et-bar-center .et-bar-axis {
  position: absolute;
  z-index: 1;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  background: color-mix(in srgb, CanvasText 30%, transparent);
}
.et-bar-center .et-bar-right { left: 50%; }
.et-bar-center .et-bar-left { left: auto; right: 50%; }
.et-bar-center .et-bar-label {
  position: relative;
  z-index: 1;
  white-space: nowrap;
}
.et-bar-center .et-bar-label-left {
  grid-column: 1;
  justify-self: end;
  padding-right: 0.4rem;
}
.et-bar-center .et-bar-label-right {
  grid-column: 2;
  justify-self: start;
  padding-left: 0.4rem;
}

/* ---------------------------------------------------------- marks viz ------ */
/* A column composing several encodings (bar/point/range) over one scale. The
   track is full-height and pulls into the cell padding like the classic bar. */
.et-marks {
  --et-mark-pad-right: 0.75rem;
  position: relative;
  display: block;
  min-width: 10rem;
  height: 1.5em;
  margin: -0.25rem 0;
}
/* Stacks carry several values and labels in one coordinate area. */
.et-marks:has(.et-mark-stack) { min-width: 18rem; }
.et-mark { position: absolute; }
.et-mark-bar {
  top: 50%;
  transform: translateY(-50%);
  min-width: 1px;
  opacity: 0.55;
}
.et-mark-point {
  top: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  box-shadow: 0 0 0 1px color-mix(in srgb, Canvas 60%, transparent);
}
.et-mark-range {
  top: 50%;
  transform: translateY(-50%);
  min-width: 1px;
  opacity: 0.9;
}
.et-mark-range-fill {
  position: absolute;
  opacity: 0.2;
  border-radius: 2px;
}
.et-mark-stack {
  top: 15%;
  bottom: 15%;
  left: 0;
  right: 0;
}
.et-mark-stack-seg {
  position: absolute;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-width: 0;
}
.et-mark-stack-label {
  padding: 0 0.2rem;
  font-size: 0.8em;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: clip;
}
.et-mark-box {
  top: 15%;
  bottom: 15%;
  left: 0;
  right: 0;
}
.et-box-whisker {
  position: absolute;
  top: 50%;
  height: 1px;
  transform: translateY(-50%);
  opacity: 0.7;
}
.et-box-cap {
  position: absolute;
  top: 32%;
  bottom: 32%;
  width: 1px;
  transform: translateX(-50%);
  opacity: 0.8;
}
.et-box-iqr {
  position: absolute;
  top: 12%;
  bottom: 12%;
  border: 1px solid;
  box-sizing: border-box;
  opacity: 0.4;
}
.et-box-median {
  position: absolute;
  top: 12%;
  bottom: 12%;
  width: 2px;
  transform: translateX(-50%);
}
.et-box-outlier {
  position: absolute;
  top: 50%;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}
.et-mark-distribution {
  top: 50%;
  transform: translateY(-50%);
  left: 0;
  right: 0;
}
.et-density-band-run {
  position: absolute;
  top: 0;
  bottom: 0;
}
.et-mark-strip {
  position: absolute;
  top: 22%;
  bottom: 22%;
  left: 0;
  right: 0;
  display: flex;
  gap: 1px;
}
.et-strip-seg {
  flex: 1 1 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-width: 0;
}
.et-mark-strip-joined { gap: 0; }
.et-mark-strip-joined .et-strip-run { outline: none; }
.et-mark-strip-positioned { display: block; }
.et-strip-run {
  position: absolute;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  outline: 1px solid color-mix(in srgb, Canvas 70%, transparent);
}
.et-strip-label {
  font-size: 0.72em;
  line-height: 1;
  color: color-mix(in srgb, CanvasText 85%, transparent);
}
.et-mark-cap {
  position: absolute;
  top: 50%;
  width: 2px;
  height: 0.7em;
  transform: translate(-50%, -50%);
}
/* Both endpoints need explicit anchors; an automatic left position follows
   the cell's text alignment and can put the start cap halfway along the line. */
.et-mark-cap-start { left: 0; }
.et-mark-cap-end { right: 0; transform: translate(50%, -50%); }
.et-mark-cap-dot { width: 0.6em; height: 0.6em; border-radius: 50%; }
.et-range-direction {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0.6em;
  height: 0.6em;
  border-top: 2px solid currentColor;
  border-right: 2px solid currentColor;
  transform: translate(-50%, -50%) rotate(45deg);
  pointer-events: none;
}
.et-range-direction[data-direction="left"] { transform: translate(-50%, -50%) rotate(-135deg); }
.et-mark-arrow {
  width: 0;
  height: 0;
  border-top: 0.35em solid transparent;
  border-bottom: 0.35em solid transparent;
}
.et-mark-arrow-start {
  left: 0;
  border-right: 0.5em solid;
  transform: translate(-100%, -50%);
}
.et-mark-arrow-end {
  right: 0;
  border-left: 0.5em solid;
  transform: translate(100%, -50%);
}
.et-mark-reference {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  opacity: 0.6;
}
.et-mark-gridline {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: color-mix(in srgb, CanvasText 12%, transparent);
}
/* Cell-sized guides cannot enlarge the table's scrollable content. Horizontal
   padding follows the cell, including sub-columns and explicit style rules. */
.et-td.et-has-guides { position: relative; }
.et-cell-guides {
  position: absolute;
  inset: 0;
  box-sizing: border-box;
  padding-left: inherit;
  padding-right: inherit;
  overflow: hidden;
  pointer-events: none;
}
.et-cell-guide-track { position: relative; height: 100%; }
/* The origin must survive opaque bar fills. Keep ordinary guides behind the
   marks, with points and value labels still above the origin. */
.et-cell-guides-foreground { z-index: 1; }
.et-mark-centerline { z-index: 1; }
.et-marks-centered :is(.et-mark-point, .et-point-composite, .et-mark-label) { z-index: 2; }
.et-cell-guides .et-mark-gridline,
.et-cell-guides .et-mark-reference { top: 0; bottom: 0; }
.et-root .et-axis-row > .et-td { padding-top: 0; padding-bottom: 0; border: 0; }
/* A header span can make the first axis slot a later physical column. */
.et-axis-row > .et-td { padding-left: 0.375rem; }
.et-axis-row > .et-td[data-column-index="0"] { padding-left: 0.25rem; }
.et-axis-row > .et-td.et-subcolumn-left { padding-left: 0.15rem; }
.et-has-top-axis .et-header-leaves .et-th { border-bottom: 0; }
.et-root .et-has-top-axis .et-stats-row .et-stats-cell { border-bottom: 0; }
.et-axis {
  position: relative;
  height: calc(0.85em + 0.25rem);
  min-width: 60px;
}
.et-axis-tick {
  position: absolute;
  width: 0;
  font-size: 0.85em;
  line-height: 1;
  color: var(--et-axis-text, #000);
  bottom: 0.25rem;
  white-space: nowrap;
}
.et-axis-tick::after {
  content: "";
  position: absolute;
  left: 0;
  top: 100%;
  height: 0.25rem;
  border-left: 1px solid var(--et-axis-text, #000);
}
.et-axis-row-bottom .et-axis-tick { top: 0.25rem; bottom: auto; }
.et-axis-row-bottom .et-axis-tick::after { top: -0.25rem; }
.et-axis-tick-minor { bottom: 0.125rem; width: 0; height: 0; }
.et-axis-tick-minor::after { height: 0.125rem; }
.et-axis-row-bottom .et-axis-tick-minor { top: 0.125rem; bottom: auto; }
.et-axis-row-bottom .et-axis-tick-minor::after { top: -0.125rem; }
.et-mark-band {
  position: absolute;
  top: 0;
  bottom: 0;
  background: color-mix(in srgb, var(--et-reference, #0f766e) 14%, transparent);
}
.et-mark-reference-label {
  position: absolute;
  bottom: 0.1rem;
  font-size: 0.72em;
  line-height: 1.2;
  white-space: nowrap;
  transform: translateX(-50%);
}
.et-mark-label {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  padding: 0 0.2rem;
  font-size: 0.85em;
  line-height: 1.2;
  white-space: nowrap;
}
.et-mark-label-outside_start,
.et-mark-label-outside_end { transform: translate(0.15rem, -50%); }
.et-mark-label-center { transform: translate(-50%, -50%); }
.et-mark-label-inside {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  transform: translateY(-50%);
  box-sizing: border-box;
}
.et-mark-label-text { flex: 0 0 auto; }
.et-mark-label[hidden] { display: none; }
.et-mark-label-left { transform: translate(calc(-100% - 0.15rem), -50%); }
.et-mark-label-inside.et-mark-label-align-center { justify-content: center; }
.et-marks-tall { height: 2.8em; }
.et-mark-label-above { top: 0; transform: translateX(-50%); }
.et-mark-label-below { top: auto; bottom: 0; transform: translateX(-50%); }
.et-mark-label-inside.et-mark-label-start { justify-content: flex-start; }
.et-mark-label-inside.et-mark-label-align-begin { justify-content: flex-start; }
.et-mark-label-inside.et-mark-label-align-end { justify-content: flex-end; }

/* A boolean cell written as a labelled symbol (\`\u2713 Active\`). */
.et-boolean-symbol { font-weight: 600; }
.et-boolean-true .et-boolean-symbol { color: var(--et-positive, #16a34a); }
.et-boolean-false .et-boolean-symbol { color: var(--et-negative, #dc2626); }
/* A category mapped to a glyph or image (\`col.icons\`). */
.et-icon-glyph { font-size: 1.05em; line-height: 1; }
.et-icon-image { height: 1.1em; width: 1.1em; object-fit: contain; vertical-align: -0.15em; }

/* --------------------------------------------------------- symbol viz ------ */
/* A value repeated as glyphs, emoji or images (ratings, medal tables). */
.et-symbols {
  display: inline-flex;
  align-items: center;
  gap: 0.15em;
  line-height: 1;
}
.et-symbol { font-size: 1em; }
.et-symbol-empty { opacity: 0.3; }
.et-symbol-image { height: 1em; width: auto; object-fit: contain; }
.et-symbol-image.et-symbol-empty { opacity: 0.25; }
.et-symbol-box {
  display: inline-block;
  width: 0.85em;
  height: 0.85em;
  background-color: transparent;
  /* A glyph carries its own side bearings, a box none \u2014 so a box needs extra
     space (on top of the flex gap) to keep the run from reading as one bar. */
  margin: 0 0.14em;
}

/* Rotated headers (ALA): vertical 90\xB0 CCW, or oblique at a given angle. */
.et-th-vertical {
  vertical-align: bottom;
  white-space: nowrap;
}
.et-th-vertical .et-th-inner {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  align-items: flex-start;
}
.et-th-oblique {
  vertical-align: bottom;
  height: var(--et-th-oblique-height, 6rem);
  white-space: nowrap;
  position: relative;
  overflow: visible;
}
.et-th-oblique .et-th-inner {
  position: absolute;
  /* The baseline sits above the line-box bottom, so rotating about \`bottom\`
     shifts the glyphs left; offset enough to clear them. */
  left: 0.95rem;
  bottom: 0.5rem;
  display: inline-flex;
  transform-origin: left bottom;
  transform: rotate(var(--et-th-angle, -60deg));
  white-space: nowrap;
}
/* Give oblique headings room so they are not clipped (incl. the rounded corner). */
.et-root.et-oblique .et-scroller { padding-left: 0.5rem; padding-right: 6rem; }

.et-row-section .et-section-cell {
  font-weight: 600;
  text-align: left;
  border-top: 1px solid var(--et-header-border);
  border-bottom: 1px solid var(--et-header-border);
  --et-row-tint: var(--et-subtotal-bg);
}
.et-row-section .et-section-center { text-align: center; }
/* A blank spacer row (\`spacer_row\`): a gap with no rule. */
.et-row-spacer .et-spacer-cell {
  border: none;
  background: transparent;
  padding: 0;
  height: 0.5rem;
}
/* A combined section+summary row: the group label and its subtotal share one
   row, so give it the section rule while keeping the measure cells. */
.et-row-combined .et-td {
  border-top: 1px solid var(--et-header-border);
  border-bottom: 1px solid var(--et-header-border);
}
.et-caption {
  margin-top: 0.35rem;
  color: var(--et-muted);
  font-size: 1em;
  line-height: 1.35;
}
.et-caption:empty { display: none; }
.et-scientific { white-space: nowrap; }
.et-scientific-exponent {
  font-size: 0.75em;
  line-height: 0;
  vertical-align: baseline;
  position: relative;
  top: -0.45em;
}
.et-stub, .et-stub-head { text-align: left; }
.et-footnotes:empty { display: none; }
.et-footnotes {
  margin-top: 0.35rem;
  color: var(--et-muted);
  font-size: 1em;
}
.et-footnotes-list {
  margin: 0;
  padding-left: 1rem;
  list-style: none;
}
.et-footnote-item { line-height: 1.5; }
.et-footnote-mark {
  color: inherit;
  font-weight: normal;
  text-decoration: none;
  font-size: 0.7em;
  /* A smaller rise than native \`super\`; override the variable to fine-tune. */
  vertical-align: var(--et-footnote-rise, 0.25em);
  cursor: default;
}
.et-footnote-rows { color: var(--et-muted); }

/* ----------------------------------------------------------- delta ------- */
.et-delta { font-weight: 600; white-space: nowrap; }
/* \u25B2, \u25BC and \u2013 have different advance widths; give the indicator a fixed box so
   the numbers stay aligned down the column. */
.et-delta-indicator { display: inline-block; width: 1em; text-align: center; }
.et-delta-value { font-variant-numeric: lining-nums tabular-nums; }
.et-delta-good { color: var(--et-positive, #16a34a); }
.et-delta-bad { color: var(--et-negative); }
.et-delta-neutral { color: var(--et-muted); }
.et-delta-chip {
  display: inline-block;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  border: 1px solid currentColor;
}
.et-delta-chip.et-delta-good { background: color-mix(in srgb, var(--et-positive, #16a34a) 15%, transparent); }
.et-delta-chip.et-delta-bad { background: color-mix(in srgb, var(--et-negative) 15%, transparent); }
.et-delta-chip.et-delta-neutral { background: color-mix(in srgb, var(--et-muted) 15%, transparent); }

/* ----------------------------------------------------------- sparkline --- */
/* Scale to the text (the row's natural height) so a sparkline never makes the
   row taller; the viewBox keeps the aspect ratio, so width follows. */
.et-sparkline {
  display: inline-block;
  vertical-align: middle;
  overflow: visible;
  height: 1.25em;
  width: auto;
}

/* --------------------------------------------------------- color cell ----- */
.et-color-cell { position: relative; }

/* ------------------------------------------------------------ frozen ----- */
/* Frozen columns keep the same paint layers, over an opaque surface so
   horizontally scrolled content cannot bleed through translucent fills. */
.et-frozen { background-color: var(--et-surface) !important; }
.et-frozen-last,
.et-frozen-heading-label::before { box-shadow: 2px 0 4px -2px rgba(0, 0, 0, 0.25); }

/* For an ungrouped leaf at the freeze boundary, keep the marker outside
   the leaf and its blank spanners so their joins have no horizontal shadow. */
.et-table thead:has(.et-th-ungrouped.et-frozen-last) :is(.et-th-group-blank, .et-th-ungrouped).et-frozen-last {
  box-shadow: none;
}
.et-table thead:has(.et-th-ungrouped.et-frozen-last) :is(.et-th-group-blank, .et-th-ungrouped).et-frozen-last::before {
  content: "";
  position: absolute;
  inset: 0 -4px 0 auto;
  width: 4px;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.10), transparent);
  pointer-events: none;
}

/* --------------------------------------------------- column statistics -- */
/* The section is bounded by the same rule that separates the header from the
   columns, with matching vertical separators between the blocks. */
.et-stats-row .et-stats-cell {
  font-size: 0.96em;
  line-height: 1.35;
  color: var(--et-muted);
  text-align: left;
  vertical-align: top;
}
.et-root .et-stats-row .et-stats-cell {
  border-bottom: 1px solid var(--et-header-border);
}
.et-root .et-stats-row .et-stats-cell:not(:last-child),
.et-root .et-stats-row .et-row-num {
  border-right: 1px solid var(--et-header-border);
}
.et-stats {
  display: flex;
  flex-direction: column;
}
.et-stats-summary {
  display: flex;
  flex-direction: column;
  gap: 0.05rem;
}
.et-stats-with-footer .et-stats-summary { min-height: 7em; }
.et-stats-footer {
  height: 1.5rem;
  margin-top: 0.25rem;
  border-top: 1px solid var(--et-border);
  display: flex;
  align-items: center;
  justify-content: center;
}
.et-stats-cycle {
  border: none;
  border-radius: 3px;
  background: transparent;
  color: var(--et-text);
  font: inherit;
  font-size: 0.55rem;
  line-height: 1;
  min-height: 1.5rem;
  letter-spacing: 0.15em;
  padding: 0.15rem 0.35rem;
  cursor: pointer;
}
.et-stats-cycle:hover { background: var(--et-hover); }
.et-stats-cycle:focus-visible { outline: 2px solid var(--et-accent); }
.et-stats-type {
  font-size: 0.91em;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: var(--et-text);
}
.et-stats-name {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.91em;
  color: var(--et-muted);
  overflow-wrap: anywhere;
}
.et-stats-line { white-space: nowrap; }
.et-stats-value {
  color: var(--et-text);
  font-variant-numeric: lining-nums tabular-nums;
}

/* ------------------------------------------------------------ footer ----- */
.et-footer {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.75rem;
  padding: 0.45rem 0.15rem;
  color: var(--et-muted);
  font-size: 1.04em;
}
/* With no pager the footer has no row of its own, so when footnotes/caption sit
   below the table the actions float at the bottom-right and that content is not
   pushed down. With nothing below, the footer is an ordinary row. */
.et-root.et-float-actions .et-footer {
  position: absolute;
  right: 0.15rem;
  bottom: 0;
  padding: 0;
}
/* Expanded mode: a conventional close icon in the top-right corner; the footer's
   expand toggle steps aside for it. */
.et-text-btn.et-close-btn {
  position: absolute;
  top: 0.65rem;
  right: 0.6rem;
  display: none;
  /* Beat \`.et-text-btn { font: inherit }\`, which is later in this file. */
  font-size: 1.3rem;
  line-height: 1;
  color: var(--et-muted);
  padding: 0.15rem 0.4rem;
  border-radius: 0.4rem;
  background: color-mix(in srgb, var(--et-muted) 16%, transparent);
}
.et-text-btn.et-close-btn:hover {
  background: color-mix(in srgb, var(--et-muted) 26%, transparent);
  color: var(--et-text);
}
.et-root.et-expanded .et-close-btn { display: block; }
.et-page-controls { display: flex; align-items: center; gap: 0.4rem; }
/* Bottom-right actions are plain text, revealed while the pointer is over the
   table; they stay visible in the expanded (fullscreen) dialog. */
.et-table-actions {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-left: auto;
  opacity: 0;
  transition: opacity 0.5s ease;
}
.et-root:hover .et-table-actions,
.et-root:focus-within .et-table-actions,
.et-dialog .et-table-actions {
  opacity: 1;
}
.et-text-btn {
  border: none;
  background: none;
  padding: 0;
  margin: 0;
  font: inherit;
  color: inherit;
  line-height: 1.2;
  cursor: pointer;
}
.et-text-btn:hover { color: var(--et-text); }
.et-empty {
  padding: 2rem;
  text-align: center;
  color: var(--et-muted);
}
/* An empty table keeps its headers and shows blank placeholder rows under a
   translucent message, so it holds its height while data is pending. The overlay
   is a \`::after\` on the tbody, so it covers the rows but not the header. */
.et-empty-body { position: relative; }
.et-empty-body::after {
  content: attr(data-empty-message);
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--et-surface) 30%, transparent);
  color: var(--et-muted);
  font-size: 1.13em;
  pointer-events: none;
}

/* ----------------------------------------------------------- fullscreen -- */
.et-dialog {
  border: none;
  padding: 0;
  /* Tailwind preflight resets \`margin\` to 0, which overrides the UA's
     \`dialog:modal { margin: auto }\` and pins the modal to the top-left in
     Marimo. Restore centering explicitly. */
  inset: 0;
  margin: auto;
  box-sizing: border-box;
  width: 96vw;
  max-width: 96vw;
  height: 94vh;
  max-height: 94vh;
  border-radius: 12px;
  overflow: hidden;
  background: var(--et-surface);
  color: var(--et-text);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
}
.et-dialog::backdrop { background: rgba(15, 23, 42, 0.55); }

/* Display annotations are separate from data cells and follow the stripe cycle. */
.et-display-row .et-td { --et-row-tint: transparent; border-top: none; border-bottom: none; }
.et-display-row.et-row-shaded .et-td { --et-row-tint: var(--et-shading); }
.et-display-row .et-display-heading { font-weight: 600; text-align: left; }
.et-display-section .et-display-label-cell { font-weight: 600; }
.et-display-row .et-display-align-center { text-align: center; }
.et-display-heading > .et-display-label { display: inline-block; max-width: 100%; }
.et-frozen-heading-label { position: sticky; z-index: 10; }
.et-frozen-heading-label::before {
  content: "";
  position: absolute;
  pointer-events: none;
  left: calc(-1 * var(--et-heading-frozen-left));
  top: calc(-1 * var(--et-heading-frozen-top));
  bottom: calc(-1 * var(--et-heading-frozen-bottom));
  width: var(--et-heading-frozen-width);
}
.et-section-toggle {
  display: inline-flex;
  align-items: baseline;
  gap: var(--et-section-toggle-gap);
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: inherit;
  cursor: pointer;
}
.et-section-toggle:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
.et-section-chevron { flex: none; width: var(--et-section-chevron-width); text-align: center; }
.et-root .et-display-row.et-display-rule-above .et-td,
.et-root .et-display-row.et-display-rule-both .et-td { border-top: 1px solid var(--et-header-border); }
.et-root .et-display-row.et-display-rule-below .et-td,
.et-root .et-display-row.et-display-rule-both .et-td { border-bottom: 1px solid var(--et-header-border); }
.et-display-label + .et-display-value { margin-left: 0.6em; }

/* A widget-owned popover escapes scroll clipping and stays themed in fullscreen. */
.et-root .et-tooltip {
  position: fixed;
  inset: auto;
  margin: 0;
  z-index: 10000;
  box-sizing: border-box;
  max-width: min(28rem, calc(100vw - 16px));
  max-height: calc(100vh - 16px);
  overflow: auto;
  padding: 0.5rem 0.625rem;
  border: 1px solid var(--et-border, #cbd5e1);
  border-radius: 4px;
  background: var(--et-surface, var(--et-bg, white));
  color: var(--et-text, #0f172a);
  font-family: var(--et-font, Arial, sans-serif);
  font-size: 12px;
  line-height: 1.45;
  text-align: left;
  white-space: normal;
  box-shadow: 0 3px 12px rgb(0 0 0 / 18%);
  pointer-events: auto;
}
.et-root .et-tooltip[hidden] { display: none; }
.et-tooltip-entry { display: flex; align-items: baseline; gap: 0.4rem; }
.et-tooltip-entry + .et-tooltip-entry { margin-top: 0.3rem; }
.et-tooltip-swatch { width: 0.65em; height: 0.65em; flex: 0 0 0.65em; }
.et-tooltip-content { min-width: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
.et-tooltip-name { font-weight: 600; margin-right: 0.5em; }
.et-tooltip-value { font-variant-numeric: tabular-nums; }
.et-tooltip-detail { color: var(--et-text, #0f172a); }
.et-root [data-et-tooltip-cell]:focus-visible { outline: 2px solid var(--et-accent, #2563eb); outline-offset: -2px; }
.et-tooltip-active { outline: 2px solid var(--et-text, #0f172a); outline-offset: 2px; }
.et-point-combined-member { visibility: hidden; }
.et-point-composite { border-radius: 50%; }
.et-point-composite > svg { display: block; width: 100%; height: 100%; overflow: visible; }

/* Font-independent geometric markers shared by points, legends and ratings. */
.et-marker-svg { display: block; width: 100%; height: 100%; overflow: visible; }
.et-shaped-marker { background: transparent; }

/* A gradient key shares the axis coordinates and stays outside the detail rows. */
.et-axis-gradient { position: absolute; left: 0; right: 0; height: 3px; bottom: 0; }
.et-axis-row-bottom .et-axis-gradient { top: 0; bottom: auto; }

.et-axis-label { display: block; width: max-content; transform: translateX(-50%); }
.et-axis-label-start { transform: none; }
.et-axis-label-end { transform: translateX(-100%); }
`,e),n=Mi({el:t,model:e,container:r.mount});return()=>{n(),r.destroy()}}};export{Y1 as default};
