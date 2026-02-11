# 🚀 Deployment Guide - Snake Game på GitHub Pages

Dette dokument forklarer hvordan du deployer Snake spillet til GitHub Pages, så det kan spilles direkte i browseren.

## 📋 Forudsætninger

- En GitHub konto
- Git installeret på din computer
- Python 3.11+ installeret (til lokal test)

## 🎯 Trin-for-trin Guide

### 1. **Aktiver GitHub Pages i Repository Settings**

1. Gå til dit GitHub repository på https://github.com/proxus-consulting/snake
2. Klik på **Settings** (øverst til højre)
3. I venstre menu, klik på **Pages** (under "Code and automation")
4. Under "Build and deployment":
   - **Source**: Vælg "GitHub Actions"
   - (Ikke "Deploy from a branch")

### 2. **Push Koden til GitHub**

Hvis du ikke allerede har pushed de nyeste filer:

```bash
cd d:\Dev\Snake
git add .
git commit -m "Add web deployment support with Pygbag"
git push origin main
```

### 3. **Workflow Kører Automatisk**

- Gå til **Actions** tab i dit GitHub repository
- Du skulle se et workflow ved navn "Build and Deploy to GitHub Pages" køre
- Vent på at det bliver grønt ✓ (tager typisk 2-3 minutter første gang)

### 4. **Find Din Game URL**

Når workflow'et er færdigt:
- Gå til **Settings** → **Pages** igen
- Øverst vil der stå: "Your site is live at `https://proxus-consulting.github.io/snake/`"
- Klik på linket for at spille!

## 🧪 Test Lokalt Først (Valgfrit)

Hvis du vil teste Pygbag lokalt før deployment:

```bash
# Installer Pygbag
pip install pygbag

# Byg og kør lokalt
cd d:\Dev\Snake
pygbag .

# Åbn browser på http://localhost:8000
```

## 🔄 Opdatering af Spillet

Hver gang du laver ændringer og pusher til GitHub, vil spillet automatisk blive gendeployet:

```bash
git add .
git commit -m "Beskrivelse af ændringer"
git push origin main
```

## ⚠️ Almindelige Problemer

### Workflow Fejler

- **Check Python version**: Workflow bruger Python 3.11
- **Check logs**: Klik på den fejlede workflow i Actions tab for at se fejl

### Pages Vises Ikke

- **Vent lidt**: Det kan tage et par minutter efter workflow er færdig
- **Check Pages er aktiveret**: Settings → Pages → Source skal være "GitHub Actions"
- **Hard refresh**: Ctrl+Shift+R (Windows) eller Cmd+Shift+R (Mac)

### Spillet Loader Ikke

- **Check browser console**: Højreklik → Inspicér → Console tab
- **Check HTTPS**: Sørg for at du bruger https:// og ikke http://

## 📁 Fil Oversigt

- **main.py** - Entry point for Pygbag (påkrævet)
- **snake.py** - Dit Snake spil (modificeret til async)
- **index.html** - Web interface template
- **.github/workflows/deploy.yml** - Automatisk deployment workflow
- **DEPLOYMENT.md** - Denne fil

## 🎮 Efter Deployment

Del dit spil med andre ved at sende dem linket:
`https://proxus-consulting.github.io/snake/`

Spillet kører 100% i browseren - ingen server nødvendig! 🎉

## 🛠️ Teknisk Info

- **Pygbag**: Konverterer Pygame til WebAssembly
- **GitHub Actions**: Automatisk build og deployment
- **GitHub Pages**: Gratis static hosting
