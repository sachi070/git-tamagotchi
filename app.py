import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import state_manager
import git_watcher

SPRITE_SHEET = "RetroCatsFree.png"
DISPLAY_SIZE = 84

class DesktopTamagotchi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GitPet")
        
        # Borderless, floating window
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.geometry("240x175+1100+700")
        self.root.config(bg="#1e1e2e")

        # Draggable bindings
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        
        # Right-click context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Feed Tuna Bowl (+15 HP)", command=self.feed_manual)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)
        self.root.bind("<Button-3>", self.show_menu)

        # Style Progress Bar
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#313244",
            background="#a6e3a1",
            darkcolor="#a6e3a1",
            lightcolor="#a6e3a1",
            bordercolor="#1e1e2e",
            thickness=6
        )

        # Sprite Display Label
        self.sprite_label = tk.Label(self.root, bg="#1e1e2e")
        self.sprite_label.pack(pady=(6, 2))

        # Stats text
        self.stats_label = tk.Label(
            self.root, text="", font=("Segoe UI", 9, "bold"),
            fg="#cdd6f4", bg="#1e1e2e"
        )
        self.stats_label.pack()

        # XP Progress bar
        self.xp_bar = ttk.Progressbar(
            self.root,
            style="Custom.Horizontal.TProgressbar",
            length=180,
            mode='determinate'
        )
        self.xp_bar.pack(pady=(4, 6))

        # Slice animations from RetroCatsFree.png
        self.animations = {}
        self.load_sprites_from_sheet()

        # State Initialization
        self.state = state_manager.load_state()
        self.state["name"] = "Neko"
        self.frame_idx = 0
        self.happy_countdown = 0

        # Start loops
        self.animate_loop()
        self.poll_github_loop()

    def crop_row(self, sheet, row_y_ratio, row_height_ratio, num_frames):
        """Extracts proportional frames from a specific row on the sheet."""
        w, h = sheet.size
        frame_w = w / 4
        y1 = int(h * row_y_ratio)
        y2 = int(h * (row_y_ratio + row_height_ratio))
        
        frames = []
        for i in range(num_frames):
            x1 = int(i * frame_w)
            x2 = int((i + 1) * frame_w)
            cropped = sheet.crop((x1, y1, x2, y2))
            
            # Crop tighter to sprite bounding box to remove extra padding
            bbox = cropped.getbbox()
            if bbox:
                cropped = cropped.crop(bbox)
            
            resized = cropped.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.NEAREST)
            frames.append(ImageTk.PhotoImage(resized))
        return frames

    def load_sprites_from_sheet(self):
        if not os.path.exists(SPRITE_SHEET):
            print(f"Error: {SPRITE_SHEET} not found in directory!")
            return

        sheet = Image.open(SPRITE_SHEET).convert("RGBA")
        
        # Row 1: Brown Cat (Hungry / Pawing) -> 4 frames
        self.animations["hungry"] = self.crop_row(sheet, 0.02, 0.12, 4)
        
        # Row 2: White Cat (Alert / Happy / Jumping) -> 2 frames
        self.animations["happy"] = self.crop_row(sheet, 0.16, 0.13, 2)
        self.animations["idle"] = self.animations["happy"]  # Uses alert cat as default idle
        
        # Row 3: Sleeping Cat (zZZ animation) -> 4 frames
        self.animations["sleeping"] = self.crop_row(sheet, 0.31, 0.13, 4)

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def feed_manual(self):
        self.state["happiness"] = min(100, self.state["happiness"] + 15)
        self.state["health"] = min(100, self.state["health"] + 15)
        self.state["mood"] = "happy"
        self.happy_countdown = 20
        state_manager.save_state(self.state)

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

        self.stats_label.config(
            text=f"Lv.{self.state['level']} {self.state['name']}  •  {self.state['happiness']}% ❤️"
        )
        self.xp_bar["maximum"] = self.state["max_xp"]
        self.xp_bar["value"] = self.state["xp"]

        # Adjust frame delay based on mood
        delay = 240 if mood == "sleeping" else 150
        self.root.after(delay, self.animate_loop)

    def poll_github_loop(self):
        self.state = state_manager.update_decay(self.state)
        commit_sha, repo_name = git_watcher.get_latest_github_push()

        if commit_sha and commit_sha != self.state.get("last_commit_hash"):
            if self.state.get("last_commit_hash") != "":
                self.state = state_manager.add_commit_reward(self.state, commit_sha)
                self.happy_countdown = 35
                print(f"🎉 New push detected in {repo_name}!")
            else:
                self.state["last_commit_hash"] = commit_sha
                state_manager.save_state(self.state)

        self.root.after(8000, self.poll_github_loop)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    DesktopTamagotchi().run()