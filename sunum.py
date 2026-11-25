#!/usr/bin/env python3
"""Sunumu tek komutla başlatır.

    python sunum.py                  # sunucu + tarayıcı (tam ekran); slaytları siz geçirirsiniz
    python sunum.py --elle           # otomatik oynatma olmadan, ok tuşlarıyla
    python sunum.py --yeniden-uret   # önce HTML/PPTX/PDF ve belgeleri yeniden üret, sonra başlat
    python sunum.py --pptx           # PowerPoint dosyasını varsayılan uygulamada aç
    python sunum.py --pdf            # PDF yedeğini aç
    python sunum.py --kontrol        # birim testleri + sunum doğrulaması

Yalnız Python 3 standart kitaplığı gerekir (yeniden üretim ve kontrol hariç).
Durdurmak için bu pencerede Ctrl+C.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
SCRIPTS = ROOT / 'scripts'
HTML = OUT / 'AKADEMIK_ODAKLI_SUNUM.html'
sys.path.insert(0, str(SCRIPTS))


def free_port(preferred: int = 8765) -> int:
    for port in [preferred, *range(8766, 8800)]:
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise SystemExit('Boş bir yerel port bulunamadı.')


def find_browser() -> str | None:
    """Chrome / Edge / Chromium: --app ve tam ekran bayraklarını destekleyen tarayıcılar."""
    names = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'msedge', 'chrome']
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    candidates = []
    if platform.system() == 'Windows':
        for base in [os.environ.get('PROGRAMFILES', ''), os.environ.get('PROGRAMFILES(X86)', ''), os.environ.get('LOCALAPPDATA', '')]:
            candidates += [Path(base) / 'Google/Chrome/Application/chrome.exe', Path(base) / 'Microsoft/Edge/Application/msedge.exe']
    elif platform.system() == 'Darwin':
        candidates += [Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
                       Path('/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'),
                       Path('/Applications/Chromium.app/Contents/MacOS/Chromium')]
    for c in candidates:
        if str(c) and c.is_file():
            return str(c)
    return None


def open_presentation(url: str, fullscreen: bool = True) -> str:
    exe = find_browser()
    if exe:
        profile = tempfile.mkdtemp(prefix='sunum-tarayici-')
        args = [exe, f'--app={url}', f'--user-data-dir={profile}', '--no-first-run', '--no-default-browser-check',
                '--autoplay-policy=no-user-gesture-required']
        if fullscreen:
            args.append('--start-fullscreen')
        if platform.system() == 'Linux':
            args.append('--enable-speech-dispatcher')  # Linux'ta tarayıcı sesi için gerekli
        try:
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f'{Path(exe).name} (tam ekran uygulama penceresi; çıkmak için F11 ya da Alt+F4)'
        except OSError:
            pass
    webbrowser.open(url)
    return 'varsayılan tarayıcı (tam ekran için ekrandaki düğmeye tıklayın ya da F11)'


def open_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f'Dosya bulunamadı: {path}. Önce: python sunum.py --yeniden-uret')
    if platform.system() == 'Windows':
        os.startfile(path)  # type: ignore[attr-defined]
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', str(path)])
    else:
        subprocess.Popen(['xdg-open', str(path)])


def run(cmd: list[str]) -> None:
    print('→', ' '.join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def rebuild() -> None:
    for script in ['build_interactive.py', 'export_editorial.py', 'export_academic_documents.py']:
        run([sys.executable, str(SCRIPTS / script)])


def check() -> None:
    run([sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_*.py'])
    run([sys.executable, str(SCRIPTS / 'verify_concise.py'), '--check-pptx'])


def linux_voice_hint() -> None:
    """Linux'ta sesli anlatım speech-dispatcher + espeak-ng (Türkçe) ister; eksikse nasıl kurulacağını söyler."""
    if platform.system() != 'Linux':
        return
    missing = [n for n in ('speech-dispatcher', 'espeak-ng') if not shutil.which(n)]
    if missing:
        print('Not: Sesli anlatım için şu paketler gerekli: ' + ' '.join(missing))
        print('     Ubuntu/Debian: sudo apt install speech-dispatcher espeak-ng')
        print('     Fedora: sudo dnf install speech-dispatcher espeak-ng   ·   Arch: sudo pacman -S speech-dispatcher espeak-ng')
        print('     Ses olmadan da sunum çalışır; anlatım alttaki şeritte yazılı görünür.\n')


def serve(autoplay: bool, open_browser: bool, port: int | None) -> None:
    import serve_presentation as sp
    if not HTML.is_file():
        raise SystemExit('Sunum dosyası yok. Önce: python sunum.py --yeniden-uret')
    port = port or free_port()
    sp.Handler.gateway = sp.CloudGateway(sp.load_key())
    sp.Handler.port = port
    server = sp.ThreadingHTTPServer(('127.0.0.1', port), sp.Handler)
    url = f'http://127.0.0.1:{port}/' + ('?autoplay=1' if autoplay else '')
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f'\nSunum hazır: {url}')
    if open_browser:
        print('Açıldı:', open_presentation(url, fullscreen=autoplay))
    print('Slaytları siz geçirirsiniz: →, Boşluk, PageDown ya da tıklama · ←: geri · N: konuşma notları · F11: tam ekran' if autoplay
          else 'Elle mod · Boşluk: otomatik akışı başlat · ←/→: slayt')
    print('Kapatmak için bu pencerede Ctrl+C.\n', flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print('\nSunucu kapatıldı.')
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--elle', action='store_true', help='otomatik oynatma olmadan aç')
    p.add_argument('--yeniden-uret', action='store_true', help='önce bütün çıktıları yeniden üret')
    p.add_argument('--pptx', action='store_true', help='PowerPoint dosyasını aç')
    p.add_argument('--pdf', action='store_true', help='PDF yedeğini aç')
    p.add_argument('--kontrol', action='store_true', help='testleri ve sunum doğrulamasını çalıştır')
    p.add_argument('--tarayici-acma', action='store_true', help='yalnız sunucuyu başlat (tarayıcı açma)')
    p.add_argument('--osint', action='store_true', help='sunumdaki kaynakları, haber bağlantılarını ve alan adlarını açık kaynaklarla doğrula')
    p.add_argument('--port', type=int)
    a = p.parse_args()
    if a.yeniden_uret:
        rebuild()
    if a.kontrol:
        check()
        return
    if a.osint:
        run([sys.executable, str(SCRIPTS / 'osint_dogrula.py')])
        return
    if a.pptx:
        open_file(OUT / 'AKADEMIK_ODAKLI_SUNUM.pptx')
        return
    if a.pdf:
        open_file(OUT / 'AKADEMIK_ODAKLI_SUNUM.pdf')
        return
    serve(autoplay=not a.elle, open_browser=not a.tarayici_acma, port=a.port)


if __name__ == '__main__':
    main()
