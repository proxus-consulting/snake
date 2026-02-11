# 🐍 Snake Game

Et moderne Snake spil lavet i Python med Pygame, som kan spilles både lokalt og i browseren!

## 🎮 Spil Nu!

**Browser version:** Kommer snart (efter deployment)

## ✨ Features

- 🎨 **4 forskellige temaer** - Skov, Vildmark, Vulkan, Militærbase
- 🏆 **4 sværhedsgrader** - Fra Let til Vanvid
- 📊 **Highscore system** - Gem dine bedste scores lokalt
- 🎵 **Lyd effekter** - Retro-stil game sounds
- 🌲 **Procedural generated maps** - Træer, ruiner og detaljer
- 🐍 **Dynamisk sværhedsgrad** - Spillet bliver hurtigere jo længere du kommer

## 🖥️ Kør Lokalt

### Kræver:
- Python 3.11+
- Pygame

### Installation:

```bash
# Clone repository
git clone https://github.com/proxus-consulting/snake.git
cd snake

# Installer dependencies
pip install pygame

# Kør spillet
python snake.py
```

## ☁️ Deploy til Web

Dette spil kan deployes til browseren med Pygbag og køre som en web app!

### Azure Static Web Apps (Anbefalet)
Se detaljeret guide i [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)

**Fordele:**
- ✅ Gratis tier med 100GB bandwidth
- ✅ Professionel hosting med CDN
- ✅ Custom domain support
- ✅ Automatisk deployment fra GitHub

### GitHub Pages (Alternativ)
Se guide i [DEPLOYMENT.md](DEPLOYMENT.md)

**Note:** Kræver public repository og at organisationen har Pages aktiveret.

### Andre Muligheder
- **Netlify** - Nem setup, gratis tier
- **Vercel** - Hurtig deployment
- **Itch.io** - Populær game hosting platform

## 🎯 Kontroller

- **↑↓←→** - Piletaster til at styre slangen
- **ESC** - Menu / Pause
- **Enter** - Vælg i menu
- **Esc i menu** - Tilbage / Afslut

## 📁 Projekt Struktur

```
snake/
├── snake.py              # Hovedspil (Pygame)
├── main.py              # Entry point til web (Pygbag)
├── index.html           # Web interface
├── highscores.json      # Gemte highscores
├── savedata.json        # Spil indstillinger
├── .github/workflows/
│   └── azure-static-web-apps.yml  # Auto deployment
├── AZURE_DEPLOYMENT.md  # Azure deployment guide
└── DEPLOYMENT.md        # GitHub Pages guide
```

## 🛠️ Teknisk Info

- **Sprog:** Python 3.11
- **Framework:** Pygame
- **Web:** Pygbag (WebAssembly)
- **Deployment:** Azure Static Web Apps / GitHub Actions
- **Hosting:** Azure / GitHub Pages / Netlify

## 📝 Udvikling

### Modificeret til Web
Spillet er modificeret til at understøtte async/await for at kunne køre i browseren:
- Tilføjet `asyncio` support
- Async game loop med `await asyncio.sleep(0)`
- Kompatibel med både lokal Python og Pygbag

## 📄 Licens

Dette er et demo/lære projekt. Brug frit! 🎉

## 🤝 Bidrag

Pull requests er velkomne! Åbn gerne et issue først for større ændringer.

---

**Lavet med ❤️ og Python**
