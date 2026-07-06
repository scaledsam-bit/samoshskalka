# Instagram Follow Monitor

Sleduje změny ve followers/following tvého vlastního Instagram účtu a posílá oznámení.

## Co umí

- Detekuje **nové sledující** a **ztracené sledující**
- Detekuje koho jsi **začal(a) sledovat** a koho jsi **přestal(a) sledovat**
- Ukládá historii všech změn
- Volitelně posílá oznámení přes **Telegram**

## Instalace

```bash
cd instagram-monitor
pip install -r requirements.txt
cp .env.example .env
# Uprav .env — vyplň své přihlašovací údaje
```

## Použití

```bash
# Jednorázová kontrola
python monitor.py

# Běží v cyklu (výchozí interval 30 min)
python monitor.py --loop

# Zobrazí historii všech změn
python monitor.py --history
```

## Telegram notifikace (volitelné)

1. Vytvoř bota přes [@BotFather](https://t.me/BotFather)
2. Získej `TELEGRAM_BOT_TOKEN`
3. Napiš botovi zprávu a získej své `TELEGRAM_CHAT_ID` přes `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Vyplň obě hodnoty v `.env`

## Upozornění

- Nástroj používá neoficiální knihovnu `instagrapi` — Instagram může tvůj účet dočasně omezit při příliš častých dotazech
- Doporučený interval: 30+ minut
- Používej pouze pro svůj vlastní účet
