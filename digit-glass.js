// Optical material: Oliver Nemo, MIT; see vendor/LICENSE-Oliver-Nemo.txt.
// Adaptation: supersampled alpha -> exact subpixel Euclidean SDF, texture-backed geometry, event-only rendering.
import {glyphSDF} from './distance.mjs';
import {VS_FULLSCREEN, FS_GLASS} from './vendor/shaders.js';
export function createDigitGlass(canvas, clock, cells) {
  const gl=canvas.getContext('webgl2',{alpha:false,antialias:false,preserveDrawingBuffer:true});
  if(!gl) throw Error('WebGL2 unavailable; readable CSS glass enabled');
  const compile=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
  // Float distance texture avoids byte-channel carry interpolation artifacts.
  const floatLinear=gl.getExtension('OES_texture_float_linear');
  const fs=FS_GLASS;
  const p=gl.createProgram();gl.attachShader(p,compile(gl.VERTEX_SHADER,VS_FULLSCREEN));gl.attachShader(p,compile(gl.FRAGMENT_SHADER,fs));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));
  gl.useProgram(p);const loc=n=>gl.getUniformLocation(p,n), f=(n,v)=>gl.uniform1f(loc(n),v),i=(n,v)=>gl.uniform1i(loc(n),v),v2=(n,a,b)=>gl.uniform2f(loc(n),a,b);
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([0,0,1,0,0,1,1,1]),gl.STATIC_DRAW);const a=gl.getAttribLocation(p,'aPos');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
  const tex=(unit)=>{const t=gl.createTexture();gl.activeTexture(gl.TEXTURE0+unit);gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);return t;};
  const bg=tex(0), sdf=tex(1); i('uSrc',0);i('uBlurSrc',0);i('uDigitSDF',1);
  const params={uBevel:5,uHeight:8,uSizeAdaptation:0,uIOR:1.48,uDispersion:0,uBlurPlateau:0,uBlurRim:0,uOpticalDensity:0,uMips:1,uSpecular:.55,uSpecPower:18,uHighlightAdapt:0,uHighlightWidth:.8,uHighlightSharpness:1,uHighlightBase:.8,uFresnel:1,uSat:1,uBright:0,uTintAmount:.008,uTintAdapt:0,uShadow:0,uShadowSize:4,uShadowOffset:2,uEdgeLine:.28,uEdgeWidth:.6,uEdgeDark:.08,uRefractScale:1,uMeniscus:1};
  for(const [k,v] of Object.entries(params))f(k,v);gl.uniform3f(loc('uTintColor'),.75,.77,.8);v2('uLightDir',-.6,.8);
  const mask=document.createElement('canvas'), ctx=mask.getContext('2d',{willReadFrequently:true}), env=document.createElement('canvas'), ec=env.getContext('2d');
  let key='';window.glassQA={draws:0,updates:[],glError:()=>gl.getError(),source:'Oliverrr2424/webgl-apple-liquid-glass V1 FS_GLASS, e8030bd'};
  function update(){
    const chars=cells.map(c=>c.lastElementChild?.textContent||'').join('');const nextKey=[innerWidth,innerHeight,getComputedStyle(clock).fontSize,chars,document.documentElement.dataset.style].join('|');if(key===nextKey)return;
    const mode=document.documentElement.dataset.style;
    // Neutral white finishes: retain upstream optics; no dispersion or stretched rims.
    const materials={glass:{uFinish:0,uBevel:5,uHeight:3,uTintAmount:.62,uSpecular:.38,uBlurPlateau:0,uDispersion:0,uEdgeLine:.16},frost:{uFinish:1,uBevel:5,uHeight:2,uTintAmount:.82,uSpecular:.12,uBlurPlateau:12,uDispersion:0,uEdgeLine:.08},prism:{uFinish:2,uBevel:4,uHeight:3,uTintAmount:.66,uSpecular:.48,uBlurPlateau:0,uDispersion:0,uEdgeLine:.34}};
    gl.useProgram(p);for(const [n,v] of Object.entries(materials[mode]||materials.glass))f(n,v);gl.uniform3f(loc('uTintColor'),1,1,1);
    const start=performance.now(), w=innerWidth,h=innerHeight, scale=2, sw=w*scale,sh=h*scale,dpr=Math.min(devicePixelRatio||1,2);
    let old;
    if(key&&canvas.width===Math.round(w*dpr)&&canvas.height===Math.round(h*dpr)&&!matchMedia('(prefers-reduced-motion: reduce)').matches){old=document.createElement('canvas');old.width=w;old.height=h;old.getContext('2d').drawImage(canvas,0,0);Object.assign(old.style,{position:'fixed',inset:'0',width:'100%',height:'100%',pointerEvents:'none'});canvas.after(old);}
    key=nextKey;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);mask.width=sw;mask.height=sh;env.width=w;env.height=h;ctx.scale(scale,scale);gl.viewport(0,0,canvas.width,canvas.height);v2('uRes',w,h);
    const style=getComputedStyle(clock),size=parseFloat(style.fontSize);ctx.font=`${style.fontWeight} ${size}px ${style.fontFamily}`;ctx.fillStyle='white';const metrics=ctx.measureText('88:88');const baseline=(size-metrics.fontBoundingBoxAscent-metrics.fontBoundingBoxDescent)/2+metrics.fontBoundingBoxAscent;
    for(const cell of cells){const box=cell.getBoundingClientRect();if(cell.classList.contains('colon')){for(const y of [.32,.68]){ctx.beginPath();ctx.arc(box.x+box.width/2,box.y+box.height*y,size*.0525,0,Math.PI*2);ctx.fill();}}else{const glyph=cell.lastElementChild;if(glyph){const b=glyph.getBoundingClientRect();ctx.fillText(glyph.textContent,b.x,b.y+baseline);}}}
    const data=glyphSDF(ctx.getImageData(0,0,sw,sh).data,sw,sh,scale);
    // A uniform black scene cannot show displaced detail. Do not fabricate it.
    ec.fillStyle='#000';ec.fillRect(0,0,w,h);
    // Canvas is top-down; upstream glass uses bottom-up pixel coordinates.
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,bg);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.SRGB8_ALPHA8,gl.RGBA,gl.UNSIGNED_BYTE,env);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
    gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,sdf);gl.texImage2D(gl.TEXTURE_2D,0,floatLinear?gl.R32F:gl.R16F,sw,sh,0,gl.RED,gl.FLOAT,data);
    // Material outputs only digits; backdrop pass is the same source canvas.
    gl.clearColor(0,0,0,1);gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(p);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);gl.disable(gl.BLEND);
    window.glassQA.draws++;window.glassQA.updates.push({chars,ms:performance.now()-start,w,h});
    if(old){const anim=old.animate([{opacity:1},{opacity:0}],{duration:680,easing:'cubic-bezier(.22,.75,.18,1)'});anim.onfinish=()=>old.remove();}
  }
  return {update};
}
