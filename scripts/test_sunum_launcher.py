"""Tek komut başlatıcı: sunucu gerçekten ayağa kalkar, sunumu ve autoplay parametresini sunar."""
import socket, subprocess, sys, time, unittest, urllib.request
from pathlib import Path
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
import sunum


class LauncherTests(unittest.TestCase):
    def test_free_port_is_bindable(self):
        port = sunum.free_port(8765)
        with socket.socket() as s:
            s.bind(('127.0.0.1', port))

    def test_one_command_serves_autoplay_deck(self):
        port = sunum.free_port(8795)
        proc = subprocess.Popen([sys.executable, str(R / 'sunum.py'), '--tarayici-acma', '--port', str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            body = None
            for _ in range(50):
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/?autoplay=1', timeout=2) as r:
                        body = r.read().decode()
                    break
                except OSError:
                    time.sleep(.2)
            self.assertIsNotNone(body, 'server did not start')
            self.assertIn('start-overlay', body)
            self.assertIn("q.get('autoplay')", body)
        finally:
            proc.terminate(); proc.wait(5)


if __name__ == '__main__':
    unittest.main()
