"""Prepare real-location context assets. Images do not establish operation locations."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];A=R/'assets/locations'
A.mkdir(parents=True,exist_ok=True)
shutil.copyfile(R/'research/locations/paris.jpg',A/'paris.jpg')
records={
 'Germany':{'city':'Berlin','place':'Potsdamer Platz','coordinates':[13.3761,52.5096],'image':'berlin_panorama.jpg','kind':'Gerçek 360° panorama','credit':'HDRI Haven / Poly Haven; kopya: pmndrs/drei-assets','source':'https://polyhaven.com/a/potsdamer_platz','download':'https://raw.githubusercontent.com/pmndrs/drei-assets/master/hdri/potsdamer_platz_1k.hdr','license':'CC0 (HDRI Haven / Poly Haven)','coordinate_basis':'Potsdamer Platz yer işareti referansı; fotoğrafın kamera GPS konumu doğrulanmadı.'},
 'UK':{'city':'Londra','place':'Adams Place Bridge','coordinates':[-.0192,51.5060],'image':'london_panorama.jpg','kind':'Gerçek 360° panorama','credit':'HDRI Haven / Poly Haven; kopya: pmndrs/drei-assets','source':'https://polyhaven.com/a/adams_place_bridge','download':'https://raw.githubusercontent.com/pmndrs/drei-assets/master/hdri/adams_place_bridge_1k.hdr','license':'CC0 (HDRI Haven / Poly Haven)','coordinate_basis':'Canary Wharf / köprü için yaklaşık yer işareti referansı; kamera GPS konumu doğrulanmadı.'},
 'France':{'city':'Paris','place':'Eiffel Kulesi','coordinates':[2.2945,48.8584],'image':'paris.jpg','kind':'Gerçek fotoğraf · kaynak galeri küçük resmi','credit':'Wildo Coda, Paris photoblog (2018); eddyte/paris-photoblog','source':'https://github.com/eddyte/paris-photoblog/blob/dev/gallerie.html','download':'https://raw.githubusercontent.com/eddyte/paris-photoblog/dev/images/toureiffelmini.jpg','license':'Kaynak © 2018 Wildo Coda; açık yeniden kullanım lisansı belirtilmiyor. CC0 değildir.','coordinate_basis':'Eiffel Kulesi yer işareti referansı; fotoğrafın kamera GPS konumu doğrulanmadı.'},
 'Italy':{'city':'Venedik','place':'Lagün kıyısı · Venice Sunset','coordinates':[12.36,45.4298],'image':'venice_panorama.jpg','kind':'Gerçek 360° panorama','credit':'HDRI Haven / Poly Haven; kopya: pmndrs/drei-assets','source':'https://polyhaven.com/a/venice_sunset','download':'https://raw.githubusercontent.com/pmndrs/drei-assets/master/hdri/venice_sunset_1k.hdr','license':'CC0 (HDRI Haven / Poly Haven)','coordinate_basis':'Venedik doğu kıyısı için yaklaşık kent referansı; kamera GPS konumu doğrulanmadı.'}
}
for d in records.values():
 d['sha256']=hashlib.sha256((A/d['image']).read_bytes()).hexdigest()
 d['role']='Geographic context only; not incident evidence, target-city attribution or a camera geolocation.'
 d['processing']='Radiance HDR panorama converted to display JPEG' if d['image'].endswith('_panorama.jpg') else 'Original small gallery preview; no generative editing'
(A/'locations.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('4 real context images catalogued; landmark/city references explicitly separated from operation targets.')
