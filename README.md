# Maxsus agent

Telefon va noutbukda doimiy ishlaydigan shaxsiy AI agent. Agent Claude (Anthropic) modelida ishlaydi,
siz bilan **Telegram** orqali gaplashadi, shuning uchun telefoningizdagi va noutbukingizdagi
Telegram ilovasidan bir xil agentga yozasiz: suhbat va xotira umumiy.

## Imkoniyatlar

- 💬 Telegram bot (faqat siz uchun ochiq: ID bo'yicha himoyalangan)
- 💻 Terminal rejimi: `python -m agent cli`
- 🧠 Uzoq muddatli xotira: agent siz haqingizdagi muhim faktlarni eslab qoladi (`/memory`)
- 🌐 Internetdan qidirish va sahifalarni o'qish
- 🕒 Hozirgi vaqtni biladi (Toshkent vaqti, sozlanadi)
- 🗂 Barcha ma'lumot lokal SQLite faylida (`data/agent.db`)

## Tez boshlash

1. Telegramda [@BotFather](https://t.me/BotFather) ga `/newbot` deb yozing va tokenni oling.
2. [@userinfobot](https://t.me/userinfobot) orqali o'zingizning Telegram ID raqamingizni bilib oling.
3. [Anthropic Console](https://platform.claude.com/settings/keys) dan API kalit oling.
4. O'rnating:

```bash
git clone https://github.com/Habibullohme/maxsus_agent.git
cd maxsus_agent
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # keyin .env ichini to'ldiring
python -m agent telegram         # yoki: python -m agent cli
```

Telegram buyruqlari: `/start`, `/new` (yangi suhbat), `/memory` (xotiradagi faktlar).

## Doimiy ishlatish (24/7)

Bot qayerda ishga tushsa, o'sha qurilma yoniq bo'lishi kerak. Telefon va noutbuk faqat Telegram orqali ulanadi.

| Variant | Qanday |
|---|---|
| **Linux noutbuk** | `deploy/maxsus-agent.service` faylidagi ko'rsatmalar (systemd, avtomatik qayta ishga tushadi) |
| **Docker** (Windows/macOS/Linux, VPS) | `docker compose up -d --build` |
| **Windows** | Task Scheduler → "At log on" → `.venv\Scripts\python.exe -m agent telegram` |
| **Android telefon** | [Termux](https://termux.dev) ichida: `pkg install python git`, so'ng yuqoridagi qadamlar |

Eng ishonchli yo'l — arzon VPS serverda Docker bilan ishga tushirish: noutbuk yopiq bo'lsa ham agent ishlaydi.

## GitHub'dagi yashil katakchalar

Commitlar GitHub profilingizdagi hissa (contribution) grafigida ko'rinishi uchun:

1. Commit muallifining emaili GitHub akkauntingizga bog'langan bo'lishi kerak. Shu repo uchun allaqachon sozlangan;
   yangi kompyuterda bir marta ishga tushiring:
   ```bash
   ./scripts/setup-git.sh --global
   ```
2. Commitlar **asosiy (default) branch**ga tushishi kerak — boshqa branchdagi commitlar faqat
   asosiy branchga merge qilingandan keyin hisoblanadi.
3. Repo fork bo'lmasligi kerak (bu repo fork emas ✅).
4. Agar repo private bo'lsa: GitHub → profil → **Contribution settings** → "Private contributions" ni yoqing.

## Tuzilishi

```
agent/
  brain.py         Claude bilan suhbat sikli va asboblar
  memory.py        SQLite: suhbatlar va faktlar
  telegram_bot.py  Telegram bot
  cli.py           Terminal rejimi
  config.py        Sozlamalar (.env)
deploy/            systemd servis fayli
scripts/           yordamchi skriptlar
```
