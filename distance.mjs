// Exact separable squared Euclidean distance transform (lower envelope of parabolas).
// Original implementation of the Felzenszwalb/Huttenlocher algorithm.
export function squaredEDT(input,w,h) {
  const out=new Float64Array(input), n=Math.max(w,h), f=new Float64Array(n), d=new Float64Array(n), z=new Float64Array(n+1), v=new Int32Array(n);
  function line(length){
    let k=0;v[0]=0;z[0]=-Infinity;z[1]=Infinity;
    for(let q=1;q<length;q++){
      let s;
      do {const p=v[k];s=((f[q]+q*q)-(f[p]+p*p))/(2*q-2*p);if(s<=z[k])k--;else break;}while(k>=0);
      k++;v[k]=q;z[k]=s;z[k+1]=Infinity;
    }
    k=0;for(let q=0;q<length;q++){while(z[k+1]<q)k++;d[q]=(q-v[k])**2+f[v[k]];}
  }
  for(let x=0;x<w;x++){for(let y=0;y<h;y++)f[y]=out[y*w+x];line(h);for(let y=0;y<h;y++)out[y*w+x]=d[y];}
  for(let y=0;y<h;y++){for(let x=0;x<w;x++)f[x]=out[y*w+x];line(w);for(let x=0;x<w;x++)out[y*w+x]=d[x];}
  return out;
}
export function glyphSDF(alpha,w,h,scale){
  const inner=new Float64Array(w*h),outer=new Float64Array(w*h);
  for(let j=0;j<w*h;j++){
    const a=alpha[j*4+3]/255;
    outer[j]=a===1?0:a===0?1e12:Math.max(0,.5-a)**2;
    inner[j]=a===0?0:a===1?1e12:Math.max(0,a-.5)**2;
  }
  const a=squaredEDT(outer,w,h),b=squaredEDT(inner,w,h),result=new Float32Array(w*h);
  for(let j=0;j<result.length;j++)result[j]=(Math.sqrt(a[j])-Math.sqrt(b[j]))/scale;
  return result;
}
