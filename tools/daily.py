# Daily ayah poster for @quran_kgz (runs on GitHub Actions).
# MODE=daily  -> image of today's ayah + caption + buttons, sent to the channel
# MODE=promo  -> app announcement with an "open app" button
# MODE=test   -> only renders images into out/ (nothing is sent)
import json, os, random, datetime, math, sys
from PIL import Image, ImageDraw, ImageFont, features

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_AR = os.path.join(ROOT, 'fonts', 'hafs.otf')
FONT_B = os.path.join(ROOT, 'fonts', 'Inter-Bold.otf')
FONT_M = os.path.join(ROOT, 'fonts', 'Inter-Medium.otf')
CHAT = os.environ.get('CHAT', '@quran_kgz')
BOT = 'quran_kgz_bot'
START = datetime.date(2026, 10, 30)
G1, G2 = (10, 38, 30), (24, 74, 59)
GOLD, CREAM, SOFT = (214, 180, 110), (243, 236, 216), (190, 205, 195)
AN = '٠١٢٣٤٥٦٧٨٩'

if not features.check('raqm'):
    sys.exit('Pillow is missing raqm: Arabic text would be broken')


def bg(w, h):
    im = Image.new('RGB', (w, h), G1)
    d = ImageDraw.Draw(im)
    cx, cy, R = w / 2, h * 0.42, math.hypot(w, h) / 1.6
    for r in range(int(R), 0, -6):
        t = r / R
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(G2[i] * (1 - t) + G1[i] * t) for i in range(3)))
    return im


def frame(d, w, h, s):
    d.rectangle([int(26 * s), int(26 * s), w - int(26 * s), h - int(26 * s)], outline=GOLD, width=max(2, int(3 * s)))
    d.rectangle([int(38 * s), int(38 * s), w - int(38 * s), h - int(38 * s)], outline=(120, 100, 60), width=max(1, int(1 * s)))


def wrap(d, text, font, maxw, rtl=False):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font, direction='rtl' if rtl else None) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ayah_image(n, a, ar, kg, name, path):
    W = H = 1080
    im = bg(W, H)
    d = ImageDraw.Draw(im)
    frame(d, W, H, 1.6)
    fl = ImageFont.truetype(FONT_B, 30)
    d.text((W / 2, 108), 'КҮНДҮН АЯТЫ', font=fl, fill=GOLD, anchor='mm')
    maxw = W - 220
    ar_full = ar.replace('۞', '').strip() + ' ' + ''.join(AN[int(c)] for c in str(a))
    # fit Arabic + Kyrgyz into the middle area (y 160..900)
    for sa, sk in [(64, 40), (58, 37), (52, 34), (46, 31), (42, 28), (38, 26), (34, 24)]:
        fa = ImageFont.truetype(FONT_AR, sa)
        fk = ImageFont.truetype(FONT_M, sk)
        la = wrap(d, ar_full, fa, maxw, rtl=True)
        lk = wrap(d, kg, fk, maxw)
        ha, hk = len(la) * sa * 1.75, len(lk) * sk * 1.42
        total = ha + 70 + hk
        if total <= 720:
            break
    y = 160 + (740 - total) / 2
    for ln in la:
        d.text((W / 2, y + sa * 0.85), ln, font=fa, fill=GOLD, anchor='mm', direction='rtl')
        y += sa * 1.75
    y += 20
    d.line([(W / 2 - 110, y + 14), (W / 2 + 110, y + 14)], fill=GOLD, width=2)
    d.ellipse([W / 2 - 6, y + 8, W / 2 + 6, y + 20], fill=GOLD)
    y += 50
    for ln in lk:
        d.text((W / 2, y + sk * 0.7), ln, font=fk, fill=CREAM, anchor='mm')
        y += sk * 1.42
    fr = ImageFont.truetype(FONT_B, 32)
    d.text((W / 2, 948), f'«{name}» сүрөсү, {n}:{a}', font=fr, fill=CREAM, anchor='mm')
    fs = ImageFont.truetype(FONT_M, 24)
    d.text((W / 2, 992), 'Курандын кыргызча мааниси · @quran_kgz', font=fs, fill=SOFT, anchor='mm')
    im.save(path, quality=92)


def promo_image(path):
    W, H, s = 1280, 720, 2
    im = bg(W, H)
    d = ImageDraw.Draw(im)
    frame(d, W, H, 1.2)
    d.text((W / 2, 175), 'القرآن الكريم', font=ImageFont.truetype(FONT_AR, 120), fill=GOLD, anchor='mm', direction='rtl')
    d.text((W / 2, 350), 'Курандын кыргызча мааниси', font=ImageFont.truetype(FONT_B, 66), fill=CREAM, anchor='mm')
    d.line([(W / 2 - 180, 425), (W / 2 + 180, 425)], fill=GOLD, width=3)
    d.ellipse([W / 2 - 9, 416, W / 2 + 9, 434], fill=GOLD)
    fm = ImageFont.truetype(FONT_M, 40)
    d.text((W / 2, 500), 'Арабча текст · кыргызча жана орусча мааниси', font=fm, fill=SOFT, anchor='mm')
    d.text((W / 2, 562), 'Шейх Махер аль-Муайклинин окуусу · 114 сүрө', font=fm, fill=SOFT, anchor='mm')
    im.save(path, quality=92)


def candidates():
    idx = json.load(open(os.path.join(ROOT, 'data', 'index.json'), encoding='utf-8'))
    out = []
    for s in idx:
        d = json.load(open(os.path.join(ROOT, 'data', f's{s["n"]}.json'), encoding='utf-8'))
        for i, ar, kg, ru in d['ayat']:
            if 40 <= len(kg) <= 330 and len(ar) <= 260:
                out.append((s['n'], i, ar, kg, d['kg']))
    random.Random(2026).shuffle(out)
    return out


def send(method, files=None, **data):
    import requests
    tok = os.environ['BOT_TOKEN']
    r = requests.post(f'https://api.telegram.org/bot{tok}/{method}', data=data, files=files, timeout=60)
    print(method, r.status_code, r.text[:300])
    r.raise_for_status()
    return r.json()


def main():
    mode = os.environ.get('MODE', 'daily')
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    if mode in ('daily', 'test'):
        c = candidates()
        day = (datetime.date.today() - START).days
        n, a, ar, kg, name = c[day % len(c)]
        p = os.path.join(ROOT, 'out', f'ayah_{n}_{a}.jpg')
        ayah_image(n, a, ar, kg, name, p)
        caption = f'📖 Күндүн аяты\n\n{kg}\n\n— «{name}» сүрөсү, {n}:{a}\n\n📢 @quran_kgz'
        kb = {'inline_keyboard': [
            [{'text': '📖 Тиркемеде окуу жана угуу', 'url': f'https://t.me/{BOT}?startapp=s{n}-{a}'}],
            [{'text': '📢 Канал: Курандын кыргызча мааниси', 'url': 'https://t.me/quran_kgz'}]]}
        print('ayah', n, a, len(c), 'candidates')
        if mode == 'daily':
            with open(p, 'rb') as f:
                send('sendPhoto', files={'photo': f}, chat_id=CHAT, caption=caption[:1024], reply_markup=json.dumps(kb))
    if mode in ('promo', 'test'):
        p = os.path.join(ROOT, 'out', 'promo.jpg')
        promo_image(p)
        caption = ('📖 Курандын кыргызча мааниси — эми Telegram тиркемесинде!\n\n'
                   'Арабча текст, кыргызча жана орусча мааниси, Шейх Махер аль-Муайклинин окуусу — бир жерде.\n\n'
                   '▶️ Ар бир аятты угуу, окулуп жаткан аят белгиленип турат\n'
                   '⭐ Аяттарды сактоо\n🔍 Котормодон сөз издөө\n\n'
                   '👇 Төмөнкү баскычты басып ачыңыз')
        kb = {'inline_keyboard': [[{'text': '📖 Тиркемени ачуу', 'url': f'https://t.me/{BOT}?startapp'}]]}
        if mode == 'promo':
            with open(p, 'rb') as f:
                send('sendPhoto', files={'photo': f}, chat_id=CHAT, caption=caption, reply_markup=json.dumps(kb))


if __name__ == '__main__':
    main()
