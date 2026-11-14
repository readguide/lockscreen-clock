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
  const glyphCache=new Map();
  let key='', material='';window.glassQA={draws:0,sdfBuilds:0,textureUploads:0,programs:1,geometryUpdates:[],updates:[],glError:()=>gl.getError(),source:'Oliverrr2424/webgl-apple-liquid-glass V1 FS_GLASS, e8030bd'};
  function update(){
    const chars=cells.map(c=>c.lastElementChild?.textContent||'').join('');const nextKey=[innerWidth,innerHeight,devicePixelRatio,getComputedStyle(clock).font,chars].join('|');
    const mode=document.documentElement.dataset.style;
    // Neutral white finishes: retain upstream optics; no dispersion or stretched rims.
    // Upstream Schlick Fresnel + directional specular/inner line, tuned for a black
    // scene: white transmission remains legible, no invented wallpaper or dispersion.
    const materials={
      glass:{uFinish:0,uBevel:7,uHeight:4,uTintAmount:.58,uSpecular:.72,uSpecPower:29.5,uFresnel:.65,uHighlightWidth:.72,uHighlightSharpness:1,uBlurPlateau:0,uDispersion:0,uEdgeLine:.24,uEdgeWidth:.6},
      frost:{uFinish:1,uBevel:5,uHeight:2,uTintAmount:.82,uSpecular:.16,uSpecPower:29.5,uFresnel:.65,uHighlightWidth:.8,uHighlightSharpness:1,uBlurPlateau:12,uDispersion:0,uEdgeLine:.10,uEdgeWidth:.6},
      prism:{uFinish:2,uBevel:4,uHeight:3,uTintAmount:.64,uSpecular:.85,uSpecPower:29.5,uFresnel:.65,uHighlightWidth:.6,uHighlightSharpness:1.15,uBlurPlateau:0,uDispersion:0,uEdgeLine:.42,uEdgeWidth:.5}
    };
    gl.useProgram(p);for(const [n,v] of Object.entries(materials[mode]||materials.glass))f(n,v);gl.uniform3f(loc('uTintColor'),1,1,1);
    const start=performance.now();
    if(key!==nextKey){
      const beforeBuilds=window.glassQA.sdfBuilds;
      const w=innerWidth,h=innerHeight, scale=2, sw=w*scale,sh=h*scale,dpr=Math.min(devicePixelRatio||1,2);
      key=nextKey;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);env.width=w;env.height=h;gl.viewport(0,0,canvas.width,canvas.height);v2('uRes',w,h);
      const style=getComputedStyle(clock),size=parseFloat(style.fontSize);ctx.font=`${style.fontWeight} ${size}px ${style.fontFamily}`;ctx.fillStyle='white';const metrics=ctx.measureText('88:88');const baseline=(size-metrics.fontBoundingBoxAscent-metrics.fontBoundingBoxDescent)/2+metrics.fontBoundingBoxAscent;
      // Cache each padded glyph field independently of material and viewport position.
      // A 24px exterior margin exceeds every finish's bevel/shadow reach.
      const data=new Float32Array(sw*sh);data.fill(24);
      for(const cell of cells){
        const box=cell.getBoundingClientRect(),glyph=cell.lastElementChild;
        if(!glyph)continue;
        const b=glyph.getBoundingClientRect(),pad=24;
        const x=Math.floor((box.x-pad)*scale),y=Math.floor((box.y-pad)*scale);
        const cw=Math.ceil((box.width+pad*2)*scale),ch=Math.ceil((box.height+pad*2)*scale);
        const gx=b.x-x/scale,gy=b.y-y/scale;
        const cacheKey=[ctx.font,cw,ch,glyph.textContent,gx,gy,box.height,scale].join('|');
        let field=glyphCache.get(cacheKey);
        if(!field){
          const tile=document.createElement('canvas');tile.width=cw;tile.height=ch;
          const tc=tile.getContext('2d',{willReadFrequently:true});tc.scale(scale,scale);tc.font=ctx.font;tc.fillStyle='white';
          if(cell.classList.contains('colon')){for(const cy of [.32,.68]){tc.beginPath();tc.arc(box.x+box.width/2-x/scale,box.y+box.height*cy-y/scale,size*.0525,0,Math.PI*2);tc.fill();}}
          else tc.fillText(glyph.textContent,gx,gy+baseline);
          field=glyphSDF(tc.getImageData(0,0,cw,ch).data,cw,ch,scale);
          window.glassQA.sdfBuilds++;
          // Bound memory across arbitrary resizes; evict only cached CPU tiles.
          if(glyphCache.size>=64)glyphCache.delete(glyphCache.keys().next().value);
          glyphCache.set(cacheKey,field);
        }
        for(let ty=Math.max(0,-y);ty<Math.min(ch,sh-y);ty++){
          for(let tx=Math.max(0,-x);tx<Math.min(cw,sw-x);tx++){
            const target=(y+ty)*sw+x+tx;data[target]=Math.min(data[target],field[ty*cw+tx]);
          }
        }
      }
      // A uniform black scene cannot show displaced detail. Do not fabricate it.
      ec.fillStyle='#000';ec.fillRect(0,0,w,h);
      // Canvas is top-down; upstream glass uses bottom-up pixel coordinates.
      gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,bg);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.SRGB8_ALPHA8,gl.RGBA,gl.UNSIGNED_BYTE,env);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
      gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,sdf);gl.texImage2D(gl.TEXTURE_2D,0,floatLinear?gl.R32F:gl.R16F,sw,sh,0,gl.RED,gl.FLOAT,data);
      window.glassQA.textureUploads+=2;
      window.glassQA.geometryUpdates.push({chars,ms:performance.now()-start,builds:window.glassQA.sdfBuilds-beforeBuilds});
    }
    if(mode==='classic'){material=mode;return;}
    if(material===mode && window.glassQA.lastDrawKey===key)return;
    material=mode;window.glassQA.lastDrawKey=key;
    // Material outputs only digits; backdrop pass is the same source canvas.
    gl.clearColor(0,0,0,1);gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(p);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);gl.disable(gl.BLEND);
    window.glassQA.draws++;window.glassQA.updates.push({chars,ms:performance.now()-start,w:innerWidth,h:innerHeight});
  }
  return {update};
}
