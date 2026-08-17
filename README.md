<div align="center">

# 🐾 Git-Tamagotchi ✨ *Neko Edition* 🐾

### a lil pixel cat that lives on your desktop and eats your commits 🍙💻

*/ᐠ｡ꞈ｡ᐟ\*　**Lv.5 Neko** 👑 · 🔥 **3-day streak** · **100%** ❤️

```
    ┌──────────────────────────┐
    │          /ᐠ｡ꞈ｡ᐟ\         │  ⋆｡°✩ "+35 XP! commit detected!" ✩°｡⋆
    │       🎯 focus: 24:50    │  🍅 pomodoro sprint in progress
    │   [████████████░░░░░]    │  💗 happiness bar
    └──────────────────────────┘
```

**a floating, borderless desktop buddy that watches your GitHub, cheers your streaks, and naps when you disappear 😴**

</div>

---

## 🌸 what is this little guy

Git-Tamagotchi is a tiny pixel cat that lives right on top of your screen. Every time you push code, it perks up, munches some XP, and gets happier. Leave it alone too long and it gets sad — then sleepy. It's basically a Tamagotchi, but it's fed by `git push` instead of digital kibble. 🐟

---

## ✨ features

- 🛰️ **Global GitHub Watching** — quietly polls your authenticated GitHub activity (public + private repos) in the background
- 💥 **Commit = XP** — every push gives **+35 XP** and tops up happiness to 100%
- 🔥 **Daily Streak Engine** — counts your consecutive coding days automatically, no manual logging
- 🎁 **Procedural Wardrobe & Level-Ups**
  - Lv 1–4 → 🐈 plain lil neko
  - Lv 5–9 → 👑 royal crown (gold band, ruby center, drawn on the fly)
  - Lv 10+ → 🧙‍♂️ starry wizard hat *or* 🕶️ cool pixel shades, swappable via right-click
- 🍅 **Built-in Pomodoro Timer** — 25-min focus sprint + 5-min cat nap, with a chime + desktop notification when you finish (**+25 XP**)
- 🔊 **Audio & Meow Engine** — plays `meow.mp3`, or synthesizes its own tiny waveform meow + victory jingle if the file's missing
- 🎭 **Mood Reactions**
  - 👀 idle/alert → watches you type
  - 🥳 happy → cheers on pushes, pets, and treats
  - 😿 hungry → paws sadly at the screen after 1hr+ of silence
  - 💤 asleep → curls up in a `z Z` loop after 8hr+ away
- 🎀 **Aesthetic** — Catppuccin dark-slate palette with soft pastel pink/lavender accents, draggable anywhere across your monitors

---

## 🧁 level & wardrobe chart

| Level | Unlock | Badge | What it does |
|:---:|:---|:---:|:---|
| 1–4 | plain neko | — | baseline tracking + pomodoro |
| 5–9 | 👑 Royal Crown | 👑 | gold crown, ruby center |
| 10+ | 🧙‍♂️ Wizard Hat / 🕶️ Shades | 🧙‍♂️ 🕶️ | unlocks the wardrobe menu |

---

## 🚀 quick start

**1. install the essentials**
```bash
pip install pillow
```
> needs Python 3.8+ 🐍

**2. tell it who you are**

make a `.env` file in the project root:
```env
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=ghp_yourPersonalAccessTokenHere
```
> 🔑 generate the token at GitHub → Settings → Developer Settings → Personal Access Tokens (classic), with the **repo** scope checked

**3. wake up your neko**
```bash
python app.py
```

---

## 🕹️ controls

| do this | to trigger | you get |
|:---|:---|:---|
| 🖱️ double-click the cat | pet it | meow + 5 XP + 5% happiness |
| ✋ left-click + drag | move it | repositions the borderless window anywhere |
| 🖱️ right-click | open menu | actions, pomodoro controls, wardrobe |
| 🐟 right-click → Feed Tuna | feed it | meow + 15 XP + full health/happiness top-up |
| ⏳ right-click → Start Pomodoro | focus mode | 25:00 timer, +25 XP on completion |
| 🎩 right-click → Wardrobe | dress it up | swap crown / wizard hat / shades / bare-headed |
| 🧪 right-click → Level Up Test | just for fun | instant fake level-up, chime + desktop toast |

---

## 📁 project structure

```
git-tamagotchi/
├── .env                # your GitHub token (gitignored, keep it secret 🤫)
├── .gitignore
├── README.md
├── RetroCatsFree.png   # 2D sprite sheet
├── meow.mp3             # meow sound effect
├── state_manager.py     # XP scaling, streaks, save/load
├── git_watcher.py        # authenticated GitHub event poller
├── sound_fx.py           # MCI player + synth waveform + OS notifications
├── state.json            # auto-saved runtime state
└── app.py                 # Tkinter UI, accessory compositor, main loop
```

---

## 🎨 customization

change the progress bar color in `app.py` under `Cute.Horizontal.TProgressbar`:

```python
# 🎀 color options
# #f5c2e7 → pastel pink (default)
# #a6e3a1 → mint green
# #89dceb → sky cyan
# #fab387 → peachy orange
background="#f5c2e7"
```

---

## 💌 credits

- 🐱 sprite sheet: **Cat Pack – Pochi** by ToffeeCraft
- 🎵 audio: custom synthesis + community sound effects

---

<div align="center">

## 📄 license

MIT — fork it, remix it, let your neko evolve 🌱

**made with 🩷 for people who need a reason to commit more often**

</div>
