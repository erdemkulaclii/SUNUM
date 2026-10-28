/* Display raster tiles only after a successful HTTP response and image decode.
 * Local documents use the embedded geographic layer without contacting OSM.
 */
function attachBasemap(map,statusNode){
 const state={mode:'embedded',reason:'local_document',acceptedTiles:0,httpStatus:null};
 const requestContexts=new Set();let raster=null,epoch=0;
 function label(mode,text,reason,httpStatus=null){state.mode=mode;state.reason=reason;state.httpStatus=httpStatus;document.body.dataset.tiles=mode;statusNode.textContent=text;statusNode.title=mode==='online'?'OpenStreetMap standart döşemeleri; doğrulanmış HTTP yanıtı.':'Gömülü Natural Earth sınır haritası. Sokak ayrıntısı içermez.';}
 function fallback(reason,httpStatus=null){
  if(state.mode==='fallback')return;
  ++epoch;state.acceptedTiles=0;
  label('fallback','GÖMÜLÜ HARİTA / OSM KULLANILAMIYOR',reason,httpStatus);
  for(const context of requestContexts){context.cancelled=true;context.controller.abort();clearTimeout(context.timeout)}
  requestContexts.clear();
  if(raster&&map.hasLayer(raster))map.removeLayer(raster);
 }
 const served=location.protocol==='http:'||location.protocol==='https:';
 if(!served||!navigator.onLine){
  label('embedded','GÖMÜLÜ HARİTA / NATURAL EARTH',served?'offline':'local_document');
  return {state};
 }
 label('loading','GÖMÜLÜ HARİTA / OSM DENENİYOR','checking');
 const VerifiedTiles=L.GridLayer.extend({
  createTile(coords,done){
   const tile=document.createElement('img');tile.alt='';tile.setAttribute('role','presentation');
   const generation=epoch,context={controller:new AbortController(),cancelled:false,timeout:null,url:null};
   tile._sunumContext=context;requestContexts.add(context);
   context.timeout=setTimeout(()=>{if(!context.cancelled&&generation===epoch)fallback('timeout')},12000);
   let finished=false;
   const complete=(error=null)=>{if(finished)return;finished=true;clearTimeout(context.timeout);requestContexts.delete(context);done(error,tile)};
   const fail=(reason,status=null)=>{if(context.cancelled||generation!==epoch)return;fallback(reason,status);complete(new Error(reason))};
   (async()=>{
    try{
     const url=`https://tile.openstreetmap.org/${coords.z}/${coords.x}/${coords.y}.png`;
     // Browser supplies the real HTTP origin/referrer. Do not forge either header.
     const response=await fetch(url,{mode:'cors',credentials:'omit',cache:'default',referrerPolicy:'strict-origin-when-cross-origin',signal:context.controller.signal});
     if(context.cancelled||generation!==epoch)return;
     if(!response.ok){fail('http_error',response.status);return}
     const contentType=(response.headers.get('Content-Type')||'').split(';')[0].trim().toLowerCase();
     if(contentType!=='image/png'){fail('unexpected_content_type',response.status);return}
     const blob=await response.blob();
     if(context.cancelled||generation!==epoch)return;
     if(blob.size===0||blob.size>2*1024*1024){fail('invalid_image_size',response.status);return}
     // Error response bodies never become <img> sources, even if they are valid PNGs.
     context.url=URL.createObjectURL(blob);
     tile.onload=()=>{
      if(context.cancelled||generation!==epoch)return;
      if(tile.naturalWidth!==256||tile.naturalHeight!==256){fail('invalid_tile_dimensions',response.status);return}
      state.acceptedTiles++;label('online','OPENSTREETMAP / ÇEVRİMİÇİ','http_image_verified',response.status);complete();
     };
     tile.onerror=()=>fail('image_decode_failed',response.status);
     tile.src=context.url;
    }catch(error){if(!context.cancelled&&generation===epoch)fail('network_or_cors_error')}
   })();
   return tile;
  }
 });
 raster=new VerifiedTiles({maxZoom:19,updateWhenIdle:true,updateWhenZooming:false,keepBuffer:1,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>'});
 raster.on('tileunload',event=>{const context=event.tile?._sunumContext;if(!context)return;context.cancelled=true;context.controller.abort();clearTimeout(context.timeout);requestContexts.delete(context);if(context.url)URL.revokeObjectURL(context.url)});
 raster.addTo(map);
 return {state};
}
