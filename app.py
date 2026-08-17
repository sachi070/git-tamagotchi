import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import state_manager
import git_watcher
import sound_fx

SPRITE_SHEET = "RetroCatsFree.png"
DISPLAY_SIZE = 72

def create_pixel_crown():
    crown = Image.new("RGBA", (11, 7), (0, 0, 0, 0))
    draw = ImageDraw.Draw(crown)
    GOLD_LIGHT = (249, 226, 175, 255)
    GOLD_DARK = (250, 179, 135, 255)
    RUBY = (243, 139, 168, 255)
    OUTLINE = (17, 17, 27, 220)

    draw.point([(1, 1), (5, 0), (9, 1)], fill=GOLD_LIGHT)
    draw.line([(1, 2), (9, 2)], fill=GOLD_LIGHT)
    draw.line([(2, 3), (8, 3)], fill=GOLD_DARK)
    draw.point([(5, 2), (5, 3)], fill=RUBY)
    draw.line([(1, 4), (9, 4)], fill=GOLD_DARK)
    draw.line([(2, 5), (8, 5)], fill=OUTLINE)
    return crown

def create_pixel_wizard_hat():
    hat = Image.new("RGBA", (15, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(hat)
    PURPLE_DARK = (136, 57, 239, 255)
    PURPLE_LIGHT = (203, 166, 247, 255)
    GOLD_STAR = (249, 226, 175, 255)

    draw.point([(7, 0), (6, 1), (7, 1), (8, 1)], fill=PURPLE_LIGHT)
    draw.line([(5, 2), (9, 2)], fill=PURPLE_DARK)
    draw.line([(5, 3), (9, 3)], fill=PURPLE_DARK)
    draw.line([(4, 4), (10, 4)], fill=PURPLE_LIGHT)
    draw.line([(4, 5), (10, 5)], fill=PURPLE_DARK)
    draw.line([(3, 6), (11, 6)], fill=PURPLE_DARK)
    draw.line([(3, 7), (11, 7)], fill=PURPLE_LIGHT)
    draw.line([(2, 8), (12, 8)], fill=PURPLE_DARK)
    draw.line([(0, 9), (14, 9)], fill=PURPLE_LIGHT)
    draw.line([(1, 10), (13, 10)], fill=PURPLE_DARK)
    draw.point([(7, 5), (6, 6), (8, 6), (7, 7)], fill=GOLD_STAR)
    return hat

def create_pixel_sunglasses():
    shades = Image.new("RGBA", (17, 6), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shades)
    BLACK = (17, 17, 27, 255)
    WHITE_SHINE = (255, 255, 255, 255)
    
    draw.rectangle([(1, 1), (6, 4)], fill=BLACK)
    draw.rectangle([(9, 1), (14, 4)], fill=BLACK)
    draw.line([(6, 1), (9, 1)], fill=BLACK)
    draw.point([(0, 0), (15, 0)], fill=BLACK)
    draw.point([(2, 2), (10, 2)], fill=WHITE_SHINE)
    return shades

class DesktopTamagotchi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GitPet")
        
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.geometry("220x165+1150+680")
        self.root.config(bg="#11111b")

        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        self.root.bind("<Double-Button-1>", lambda e: self.pet_cat())

        # State Initialization
        self.state = state_manager.load_state()
        self.frame_idx = 0
        self.happy_countdown = 0
        
        # Load Accessories
        self.crown_sprite = create_pixel_crown()
        self.hat_sprite = create_pixel_wizard_hat()
        self.shades_sprite = create_pixel_sunglasses()
        self.active_hat = self.state.get("active_hat", "auto") # auto, crown, wizard, shades, none

        # Build Context Menu
        self.rebuild_menu()
        self.root.bind("<Button-3>", self.show_menu)

        # Outer Cute Frame
        self.card = tk.Frame(self.root, bg="#181825", highlightbackground="#cba6f7", highlightthickness=1.5)
        self.card.pack(fill="both", expand=True, padx=4, pady=4)
        self.card.bind("<Button-1>", self.start_drag)
        self.card.bind("<B1-Motion>", self.do_drag)

        # Progress Bar Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Cute.Horizontal.TProgressbar",
            troughcolor="#313244",
            background="#f5c2e7",
            darkcolor="#f5c2e7",
            lightcolor="#f5c2e7",
            bordercolor="#181825",
            thickness=5
        )

        # UI Components
        self.sprite_label = tk.Label(self.card, bg="#181825")
        self.sprite_label.pack(pady=(2, 0))
        self.sprite_label.bind("<Double-Button-1>", lambda e: self.pet_cat())
        self.sprite_label.bind("<Button-1>", self.start_drag)
        self.sprite_label.bind("<B1-Motion>", self.do_drag)

        self.stats_label = tk.Label(
            self.card, text="", font=("Segoe UI", 8, "bold"),
            fg="#cdd6f4", bg="#181825"
        )
        self.stats_label.pack(pady=(1, 0))

        self.pomo_label = tk.Label(
            self.card, text="✨ right-click to play", 
            font=("Segoe UI", 7, "bold"), fg="#fab387", bg="#181825"
        )
        self.pomo_label.pack(pady=(0, 2))

        self.xp_bar = ttk.Progressbar(
            self.card, style="Cute.Horizontal.TProgressbar",
            length=170, mode='determinate'
        )
        self.xp_bar.pack(pady=(0, 4))

        self.pomo_active = False
        self.pomo_seconds = 25 * 60
        self.pomo_is_break = False

        self.animations = {}
        self.load_sprites_from_sheet()

        self.animate_loop()
        self.pomodoro_tick_loop()
        self.poll_github_loop()

    def rebuild_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, bg="#1e1e2e", fg="#cdd6f4", activebackground="#f5c2e7", activeforeground="#11111b")
        self.menu.add_command(label="🐾 Pet Neko (Meow)", command=self.pet_cat)
        self.menu.add_command(label="🐟 Feed Tuna (+15 XP)", command=self.feed_manual)
        self.menu.add_separator()
        self.menu.add_command(label="⏳ Start Pomodoro", command=self.start_pomodoro)
        self.menu.add_command(label="🛑 Stop Pomodoro", command=self.stop_pomodoro)
        
        # Unlocked Wardrobe Submenu
        lvl = self.state.get("level", 1)
        if lvl >= 5:
            wardrobe = tk.Menu(self.menu, tearoff=0, bg="#1e1e2e", fg="#cdd6f4", activebackground="#f5c2e7", activeforeground="#11111b")
            wardrobe.add_command(label="👑 Royal Crown", command=lambda: self.set_accessory("crown"))
            if lvl >= 10:
                wardrobe.add_command(label="🧙‍♂️ Wizard Hat", command=lambda: self.set_accessory("wizard"))
                wardrobe.add_command(label="🕶️ Cool Shades", command=lambda: self.set_accessory("shades"))
            wardrobe.add_command(label="❌ No Hat", command=lambda: self.set_accessory("none"))
            self.menu.add_cascade(label="🎩 Wardrobe", menu=wardrobe)

        self.menu.add_separator()
        self.menu.add_command(label="🧪 Level Up Test", command=self.test_level_up)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Exit", command=self.root.destroy)

    def set_accessory(self, acc_type):
        self.active_hat = acc_type
        self.state["active_hat"] = acc_type
        state_manager.save_state(self.state)
        self.load_sprites_from_sheet()

    def crop_row(self, sheet, row_y_ratio, row_height_ratio, num_frames, acc="none"):
        w, h = sheet.size
        frame_w = w / 4
        y1 = int(h * row_y_ratio)
        y2 = int(h * (row_y_ratio + row_height_ratio))
        
        frames = []
        for i in range(num_frames):
            x1 = int(i * frame_w)
            x2 = int((i + 1) * frame_w)
            cropped = sheet.crop((x1, y1, x2, y2))
            bbox = cropped.getbbox()
            if bbox:
                cropped = cropped.crop(bbox)

            if acc != "none":
                # Canvas buffer for hat room
                pad_top = 8 if acc == "wizard" else 4
                frame_acc = Image.new("RGBA", (cropped.width, cropped.height + pad_top), (0, 0, 0, 0))
                frame_acc.paste(cropped, (0, pad_top), cropped)

                if acc == "crown":
                    cx = (cropped.width - self.crown_sprite.width) // 2
                    frame_acc.paste(self.crown_sprite, (cx, 0), self.crown_sprite)
                elif acc == "wizard":
                    wx = (cropped.width - self.hat_sprite.width) // 2
                    frame_acc.paste(self.hat_sprite, (wx, 0), self.hat_sprite)
                elif acc == "shades":
                    # Place sunglasses over the cat's face
                    sx = (cropped.width - self.shades_sprite.width) // 2
                    frame_acc.paste(self.shades_sprite, (sx, pad_top + 9), self.shades_sprite)

                cropped = frame_acc

            resized = cropped.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.NEAREST)
            frames.append(ImageTk.PhotoImage(resized))
        return frames

    def get_current_accessory(self):
        lvl = self.state.get("level", 1)
        if self.active_hat in ["crown", "wizard", "shades", "none"]:
            return self.active_hat
        # Auto mode based on level progression
        if lvl >= 10:
            return "wizard"
        elif lvl >= 5:
            return "crown"
        return "none"

    def load_sprites_from_sheet(self):
        if not os.path.exists(SPRITE_SHEET):
            return
        sheet = Image.open(SPRITE_SHEET).convert("RGBA")
        acc = self.get_current_accessory()

        self.animations["hungry"] = self.crop_row(sheet, 0.02, 0.12, 4, acc=acc)
        self.animations["happy"] = self.crop_row(sheet, 0.16, 0.13, 2, acc=acc)
        self.animations["idle"] = self.animations["happy"]
        self.animations["sleeping"] = self.crop_row(sheet, 0.31, 0.13, 4, acc="none")

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def pet_cat(self):
        sound_fx.play_meow()
        self.state["happiness"] = min(100, self.state["happiness"] + 5)
        self.state["xp"] += 5
        self.check_level_up()
        self.state["mood"] = "happy"
        self.happy_countdown = 15
        state_manager.save_state(self.state)

    def feed_manual(self):
        sound_fx.play_meow()
        self.state["happiness"] = min(100, self.state["happiness"] + 15)
        self.state["health"] = min(100, self.state["health"] + 15)
        self.state["xp"] += 15
        self.check_level_up()
        self.state["mood"] = "happy"
        self.happy_countdown = 25
        state_manager.save_state(self.state)

    def check_level_up(self):
        prev_lvl = self.state["level"]
        while self.state["xp"] >= self.state["max_xp"]:
            self.state["xp"] -= self.state["max_xp"]
            self.state["level"] += 1
            self.state["max_xp"] = int(self.state["max_xp"] * 1.4)
            sound_fx.play_level_up()
            sound_fx.notify_desktop("🎉 Level Up!", f"Neko reached Level {self.state['level']}!")

        if prev_lvl < 5 and self.state["level"] >= 5:
            sound_fx.notify_desktop("👑 Crown Unlocked!", "Neko became royalty at Level 5!")
            self.rebuild_menu()
            self.load_sprites_from_sheet()
        elif prev_lvl < 10 and self.state["level"] >= 10:
            sound_fx.notify_desktop("🧙‍♂️ Wizard Hat & Shades Unlocked!", "Neko unlocked Magic & Swag at Level 10!")
            self.rebuild_menu()
            self.load_sprites_from_sheet()

    def start_pomodoro(self):
        self.pomo_active = True
        self.pomo_is_break = False
        self.pomo_seconds = 25 * 60
        self.pomo_label.config(text="🎯 focus: 25:00", fg="#fab387")
        sound_fx.play_meow()

    def stop_pomodoro(self):
        self.pomo_active = False
        self.pomo_label.config(text="✨ timer stopped", fg="#6c7086")

    def pomodoro_tick_loop(self):
        if self.pomo_active:
            mins, secs = divmod(self.pomo_seconds, 60)
            tag = "☕ break" if self.pomo_is_break else "🎯 focus"
            color = "#a6e3a1" if self.pomo_is_break else "#fab387"
            self.pomo_label.config(text=f"{tag}: {mins:02d}:{secs:02d}", fg=color)

            if self.pomo_seconds > 0:
                self.pomo_seconds -= 1
            else:
                if not self.pomo_is_break:
                    self.pomo_is_break = True
                    self.pomo_seconds = 5 * 60
                    self.state["xp"] += 25
                    self.check_level_up()
                    sound_fx.play_level_up()
                    sound_fx.notify_desktop("🍅 Pomodoro Complete!", "Great focus sprint! Take a 5m cat break.")
                else:
                    self.pomo_is_break = False
                    self.pomo_seconds = 25 * 60
                    sound_fx.play_meow()
                    sound_fx.notify_desktop("🎯 Focus Time", "Break is over! Time to build.")

        self.root.after(1000, self.pomodoro_tick_loop)

    def animate_loop(self):
        mood = self.state.get("mood", "idle")
        frames = self.animations.get(mood) or self.animations.get("idle", [])

        if frames:
            self.frame_idx = (self.frame_idx + 1) % len(frames)
            self.sprite_label.config(image=frames[self.frame_idx])

        if self.happy_countdown > 0:
            self.happy_countdown -= 1
            if self.happy_countdown == 0:
                self.state["mood"] = "idle"

        acc = self.get_current_accessory()
        badge = "👑 " if acc == "crown" else ("🧙‍♂️ " if acc == "wizard" else ("🕶️ " if acc == "shades" else ""))
        streak = self.state.get("streak", 0)
        self.stats_label.config(
            text=f"{badge}Lv.{self.state['level']} Neko  •  🔥 {streak}d  •  {self.state['happiness']}% ❤️"
        )
        self.xp_bar["maximum"] = self.state["max_xp"]
        self.xp_bar["value"] = self.state["xp"]

        delay = 240 if mood == "sleeping" else 140
        self.root.after(delay, self.animate_loop)

    def poll_github_loop(self):
        self.state = state_manager.update_decay(self.state)
        commit_sha, repo_name = git_watcher.get_latest_github_push()

        if commit_sha and commit_sha != self.state.get("last_commit_hash"):
            if self.state.get("last_commit_hash") != "":
                self.state, did_level_up = state_manager.add_commit_reward(self.state, commit_sha)
                self.happy_countdown = 35
                if did_level_up:
                    sound_fx.play_level_up()
                    sound_fx.notify_desktop("🎉 Level Up!", f"Neko reached Level {self.state['level']}!")
                    self.rebuild_menu()
                    self.load_sprites_from_sheet()
                else:
                    sound_fx.play_meow()
                print(f"🎉 New push in {repo_name}!")
            else:
                self.state["last_commit_hash"] = commit_sha
                state_manager.save_state(self.state)

        self.root.after(8000, self.poll_github_loop)

    def test_level_up(self):
        self.state["xp"] = self.state["max_xp"]
        self.check_level_up()
        self.happy_countdown = 30
        state_manager.save_state(self.state)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    DesktopTamagotchi().run()