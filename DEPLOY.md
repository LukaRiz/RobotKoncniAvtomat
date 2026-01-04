# Deployment na Render

## Korak za korakom navodila

### 1. Priprava repozitorija
- Prepričaj se, da je tvoj projekt na GitHub/GitLab/Bitbucket
- Vse datoteke morajo biti commitane in pushane

### 2. Ustvarjanje Web Service na Render

1. Pojdi na [Render Dashboard](https://dashboard.render.com)
2. Klikni **"New +"** → **"Web Service"** (NE Static Site!)
3. Poveži svoj Git repozitorij
4. Izberi repozitorij z aplikacijo

### 3. Konfiguracija Web Service

**Osnovne nastavitve:**
- **Name**: `robot-koncni-avtomat` (ali karkoli želiš)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Environment Variables:**
- `SECRET_KEY`: Generiraj naključen ključ (lahko uporabiš: `python -c "import secrets; print(secrets.token_hex(32))"`)

### 4. Dodajanje PostgreSQL baze (priporočeno)

1. V Render Dashboard klikni **"New +"** → **"PostgreSQL"**
2. Izberi **"Free"** plan (za testiranje)
3. Ime: `robot-fsm-db`
4. Render bo samodejno nastavil `DATABASE_URL` environment variable

**Pomembno:** Če dodajaš bazo ročno, moraš v Web Service dodati:
- `DATABASE_URL`: Vzemi iz PostgreSQL service → "Connections" → "Internal Database URL"

### 5. Deployment

1. Klikni **"Create Web Service"**
2. Render bo začel build proces
3. Po končanem build-u bo aplikacija dostopna na URL-ju (npr. `https://robot-koncni-avtomat.onrender.com`)

### 6. Preverjanje

- Odpri URL aplikacije v brskalniku
- Preveri, ali se aplikacija naloži
- Preveri logs v Render Dashboard, če so kakšne napake

## Opombe

- **Free tier**: Render free tier aplikacije "zaspi" po 15 minutah neaktivnosti. Prva zahteva lahko traja 30-60 sekund.
- **Database**: SQLite ne deluje dobro na Render (datoteke se izgubijo ob redeploy). Zato uporabljamo PostgreSQL.
- **Static files**: CSS in JS datoteke v `/static` bodo delovale avtomatično.

## Troubleshooting

- Če build ne uspe: Preveri logs v Render Dashboard
- Če aplikacija ne deluje: Preveri, ali je `DATABASE_URL` pravilno nastavljen
- Če so napake z bazo: Preveri, ali je PostgreSQL service povezan z Web Service

