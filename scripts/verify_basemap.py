"""Regressions for blocked OSM images and honest offline fallbacks.

All tile responses below are SYNTHETIC TEST FIXTURES. They are not exported as
maps, observations, or preview screenshots. No live OSM requests are required.
"""
from pathlib import Path
import struct
import zlib
import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, Error as PlaywrightError

R = Path(__file__).resolve().parents[1]
HTML_PATH = R / 'output' / 'PROFESYONEL_SUNUM.html'
OSM = 'https://tile.openstreetmap.org/**'
APP = 'https://sunum.test/'


def png_fixture():
    """A real decodable PNG, so HTTP 403 cannot be mistaken for image success."""
    width = height = 256
    row = b'\x00' + bytes((47, 79, 104)) * width
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(row * height)) + chunk(b'IEND', b'')


PNG = png_fixture()


def visible_tiles(page):
    return page.locator('.leaflet-tile-pane .leaflet-tile').evaluate_all(
        '(nodes) => nodes.filter(e => e.getBoundingClientRect().width > 0 && '
        'e.getBoundingClientRect().height > 0 && '
        'getComputedStyle(e).visibility !== "hidden" && '
        'getComputedStyle(e).display !== "none" && '
        'getComputedStyle(e.closest(".leaflet-layer") || e).display !== "none").length'
    )


def assert_fallback(page):
    page.wait_for_function('document.body.dataset.tiles === "fallback"', timeout=10000)
    page.wait_for_timeout(500)
    assert visible_tiles(page) == 0, 'Blocked/unverified tiles remained visible over the embedded map'
    assert 'ÇEVRİMİÇİ' not in page.locator('#atlas-status').inner_text()
    assert page.locator('.leaflet-overlay-pane path').count() > 30
    assert page.evaluate('Object.values(map._layers).filter(l=>l.getPopup?.()).length') == 6
    assert page.evaluate('D.analysis.records.length') == 311


def make_context(browser, html, handler):
    context = browser.new_context(viewport={'width': 1440, 'height': 950})
    context.route('https://sunum.test/**', lambda r: r.fulfill(content_type='text/html', body=html))
    context.route('https://sunum.test/api/gdelt-cloud', lambda r: r.fulfill(content_type='application/json', body='{"status":"key_not_configured","message":"SYNTHETIC TEST: no Cloud service"}'))
    context.route('https://sunum.test/api/gdelt-doc', lambda r: r.fulfill(content_type='application/json', body='{"status":"request_failed","message":"SYNTHETIC TEST: no DOC service"}'))
    context.route('https://api.gdeltproject.org/**', lambda r: r.abort())
    context.route(OSM, handler)
    return context


def main():
    html = HTML_PATH.read_text()
    outcomes = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])

        # Double-click-compatible embedded mode must not ask a public tile service
        # to serve a page with no HTTP origin/referrer.
        calls = []
        ctx = make_context(browser, html, lambda r: (calls.append(r.request.url), r.abort()))
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(html)
        page.evaluate('openAtlas()')
        page.wait_for_timeout(1500)
        assert page.evaluate('location.protocol') == 'about:'
        assert page.evaluate('document.body.dataset.tiles') == 'embedded'
        assert not calls, 'about:blank requested OSM tiles without an HTTP origin'
        assert visible_tiles(page) == 0
        assert page.evaluate('D.analysis.records.length') == 311
        page.evaluate("Object.values(map._layers).find(l=>l.getTooltip?.()?.getContent().startsWith('Almanya')).openPopup()")
        assert '298' in page.locator('.leaflet-popup').inner_text()
        assert page.evaluate('Object.values(map._layers).filter(l=>l.getPopup?.()).length') == 6
        assert not errors, errors
        outcomes.append('about:blank embedded map: no OSM requests; country polygon evidence intact')
        ctx.close()

        # A real file URL is attempted independently. Enterprise browser policy may
        # forbid file navigation; that is reported as unverified, not a pass.
        file_calls = []
        ctx = make_context(browser, html, lambda r: (file_calls.append(r.request.url), r.abort()))
        page = ctx.new_page()
        try:
            page.goto(HTML_PATH.as_uri(), wait_until='domcontentloaded', timeout=10000)
        except PlaywrightError as e:
            if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(e):
                raise
            outcomes.append('file:// navigation: blocked by Chromium enterprise policy; about:blank behavior verified separately')
        else:
            page.evaluate('openAtlas()')
            page.wait_for_timeout(1500)
            assert page.evaluate('location.protocol') == 'file:'
            assert page.evaluate('document.body.dataset.tiles') == 'embedded'
            assert not file_calls, 'Local-file presentation requested OSM tiles'
            assert visible_tiles(page) == 0
            outcomes.append('file:// embedded map: no OSM requests')
        ctx.close()

        # Exact regression: a valid PNG with HTTP 403 is still an access error.
        # Leaflet's old <img onload> path displayed this kind of response.
        for label, status, content_type, body in [
            ('403 decodable PNG', 403, 'image/png', PNG),
            ('200 HTML error', 200, 'text/html', '<h1>Access blocked</h1>'),
            ('200 invalid PNG', 200, 'image/png', b'not an image'),
        ]:
            tile_calls = []
            def respond(route, _request=None, *, status=status, content_type=content_type, body=body):
                tile_calls.append(route.request.url)
                route.fulfill(status=status, content_type=content_type, headers={'Access-Control-Allow-Origin': '*'}, body=body)
            ctx = make_context(browser, html, respond)
            page = ctx.new_page()
            page.goto(APP, wait_until='domcontentloaded')
            page.evaluate('openAtlas()')
            assert_fallback(page)
            assert tile_calls, 'HTTP map did not exercise the tile fetch path'
            outcomes.append(label + ': removed and correctly labelled as fallback')
            ctx.close()

        # Network rejection, including CORS-like fetch failure, cannot be online.
        ctx = make_context(browser, html, lambda r: r.abort())
        page = ctx.new_page()
        page.goto(APP, wait_until='domcontentloaded')
        page.evaluate('openAtlas()')
        assert_fallback(page)
        outcomes.append('network failure: clean embedded fallback')
        ctx.close()

        # Success and a later failure exercise the state transition that used to
        # remain online forever after the first loaded tile.
        state = {'fail': False, 'successes': 0, 'failures': 0}
        def transitioning(route):
            status = 403 if state['fail'] else 200
            state['failures' if state['fail'] else 'successes'] += 1
            route.fulfill(status=status, content_type='image/png', headers={'Access-Control-Allow-Origin': '*'}, body=PNG)
        ctx = make_context(browser, html, transitioning)
        page = ctx.new_page()
        page.goto(APP, wait_until='domcontentloaded')
        page.evaluate('openAtlas()')
        page.wait_for_function('document.body.dataset.tiles === "online"', timeout=10000)
        page.wait_for_timeout(1600)
        assert state['successes'] > 0
        assert visible_tiles(page) > 0
        assert 'ÇEVRİMİÇİ' in page.locator('#atlas-status').inner_text()
        state['fail'] = True
        page.evaluate('map.panBy([900, 0], {animate: false})')
        assert_fallback(page)
        assert state['failures'] > 0
        # In-flight completions must not switch the failed layer back online.
        page.wait_for_timeout(1000)
        assert page.evaluate('document.body.dataset.tiles') == 'fallback'
        assert visible_tiles(page) == 0
        outcomes.append('valid PNG -> later 403: online state revoked and all raster tiles removed')
        ctx.close()
        browser.close()

    report = {
        'automated_checks_passed': True,
        'test_responses': 'SYNTHETIC FIXTURES ONLY; no map screenshots or scientific observations generated',
        'file_navigation': 'blocked_by_chromium_enterprise_policy' if any('blocked by Chromium enterprise policy' in x for x in outcomes) else 'verified',
        'non_http_branch_verified_via_about_blank': True,
        'live_OSM_verified': False,
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'outcomes': outcomes,
    }
    (R / 'output' / 'BASEMAP_DOGRULAMA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    for outcome in outcomes:
        print('UNVERIFIED:' if 'blocked by Chromium enterprise policy' in outcome else 'PASS:', outcome)
    print('All fixture responses are synthetic; no real basemap or API findings were generated.')


if __name__ == '__main__':
    main()
