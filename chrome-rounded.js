// Chrome on macOS can resolve ui-rounded to the ordinary SF face. Safari's
// approved generic must remain untouched. Compare actual raster output, not
// CSS.supports/font-family (both accept unresolved generic names).
export async function chromeRoundedFallback(clock) {
  if (!/Chrome\//.test(navigator.userAgent) || /Edg\//.test(navigator.userAgent)) return;
  const canvas = document.createElement('canvas');
  canvas.width = 800; canvas.height = 140;
  const ctx = canvas.getContext('2d', {willReadFrequently: true});
  const raster = family => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = `600 100px ${family}`;
    ctx.fillText('0123456789', 10, 110);
    return canvas.toDataURL();
  };
  const original = getComputedStyle(clock).fontFamily;
  const withoutRounded = original.replace(/ui-rounded\s*,\s*/i, '').replace(/"SF Pro Rounded"\s*,\s*/i, '');
  if (raster(original) !== raster(withoutRounded)) return;
  // Locally hosted original OFL font: no installation, remote CDN, or SF copy.
  const face = new FontFace('Clock Rounded', 'url("assets/Nunito.ttf")', {weight: '200 1000'});
  try {
    await face.load();
    document.fonts.add(face);
    clock.style.fontFamily = `"Clock Rounded", ${original}`;
  } catch (_) { /* Retain readable original metrics if font loading is denied. */ }
}
