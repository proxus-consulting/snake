# ☁️ Azure Static Web Apps Deployment Guide

Denne guide viser hvordan du deployer Snake spillet til Azure Static Web Apps - gratis og professionelt!

## 📋 Forudsætninger

- En Azure konto (gratis tier er nok)
- GitHub repository: https://github.com/proxus-consulting/snake
- Adgang til at tilføje secrets i GitHub repository

## 🚀 Step-by-Step Setup

### 1. **Opret Azure Static Web App**

1. Log ind på [Azure Portal](https://portal.azure.com)

2. Klik på **"Create a resource"**

3. Søg efter **"Static Web App"** og klik **Create**

4. Udfyld formularen:
   - **Subscription**: Vælg din subscription
   - **Resource Group**: Opret ny eller vælg eksisterende (f.eks. "snake-game-rg")
   - **Name**: `snake-game` (eller andet unikt navn)
   - **Plan type**: **Free**
   - **Region**: Vælg den nærmeste (f.eks. "West Europe")
   - **Deployment details**:
     - **Source**: GitHub
     - Klik **"Sign in with GitHub"** og autoriser Azure
     - **Organization**: `proxus-consulting`
     - **Repository**: `snake`
     - **Branch**: `main`
   - **Build Details**:
     - **Build Presets**: Custom
     - **App location**: `build/web`
     - **Api location**: (lad stå tom)
     - **Output location**: (lad stå tom)

5. Klik **"Review + create"** og derefter **"Create"**

### 2. **Hent Deployment Token**

Azure opretter automatisk en GitHub Action, men vi skal bruge vores egen:

1. I Azure Portal, gå til din nye Static Web App
2. I venstre menu, klik på **"Manage deployment token"**
3. Klik **"Reset deployment token"**
4. **Kopier tokenet** (du får kun vist det én gang!)

### 3. **Tilføj Secret til GitHub**

1. Gå til https://github.com/proxus-consulting/snake/settings/secrets/actions

2. Klik **"New repository secret"**

3. Udfyld:
   - **Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - **Secret**: (indsæt det token du kopierede)

4. Klik **"Add secret"**

### 4. **Slet Azure's Auto-Generated Workflow**

Azure har lavet sin egen workflow fil som konflikter med vores:

```bash
cd d:\Dev\Snake
git pull origin main

# Find og slet Azure's workflow fil (typisk azure-static-web-apps-*.yml)
# Den ligger i .github/workflows/
```

Eller slet den direkte på GitHub:
1. Gå til https://github.com/proxus-consulting/snake/tree/main/.github/workflows
2. Find filen der starter med `azure-static-web-apps-`
3. Klik på den → Klik på 🗑️ (trash icon) → Commit

### 5. **Push og Deploy**

```bash
cd d:\Dev\Snake
git add .
git commit -m "Add Azure Static Web Apps deployment"
git push origin main
```

### 6. **Tjek Deployment**

1. Gå til https://github.com/proxus-consulting/snake/actions
2. Se "Azure Static Web Apps CI/CD" køre
3. Når den er grøn ✓, gå tilbage til Azure Portal
4. I din Static Web App, find **URL** øverst (f.eks. `https://nice-ocean-xxx.azurestaticapps.net`)
5. Åbn linket og spil! 🎮

## 🔄 Fremtidige Updates

Hver gang du pusher til `main`, deployer Azure automatisk:

```bash
git add .
git commit -m "Dine ændringer"
git push origin main
```

## 🌐 Custom Domain (Valgfrit)

Hvis du vil bruge et custom domain (f.eks. `snake.proxus.dk`):

1. I Azure Portal → Din Static Web App
2. Klik **"Custom domains"** i venstre menu
3. Klik **"Add"** → **"Custom domain on other DNS"**
4. Følg instruktionerne for at tilføje CNAME record

## 💰 Pricing

**Free Tier inkluderer:**
- 100 GB bandwidth/måned
- 0.5 GB storage
- 2 custom domains
- Automatisk HTTPS
- Global CDN

Mere end nok til dette projekt! 🎉

## ⚠️ Troubleshooting

### Workflow fejler med "unauthorized"
- Check at `AZURE_STATIC_WEB_APPS_API_TOKEN` secret er sat korrekt
- Token skal være fra **din** Static Web App

### Siden loader ikke
- Check at workflow er grøn i GitHub Actions
- Vent 1-2 minutter efter deployment
- Hard refresh: Ctrl+Shift+R

### Build fejler
- Check logs i GitHub Actions
- Verificer at Python 3.11 bruges

## 📊 Monitoring

I Azure Portal kan du:
- Se visitor statistik
- Monitere bandwidth
- Se deployment history
- Check logs

## 🎮 Færdig!

Dit spil er nu live på Azure med professionel hosting! ☁️🐍
