import tkinter as tk
from tkinter import ttk
import state_manager
import git_watcher

# Animated ASCII Sprite Frames
SPRITE_FRAMES = {
    "idle": [
        "( • ‿ • )",
        "( - ‿ - )",
        "( • ‿ • )",
        "( ◕ ‿ ◕ )"
    ],
    "happy": [
        "＼(＾▽＾)／",
        "٩(ˊᗜˋ*)و",
        "＼(＾▽＾)／",
        "(★ω★)"
    ],
    "hungry": [
        "(╥﹏╥)",
        "( •́ ̯•̀ )",
        "( ´•︵•` )"
    ],
    "sleeping": [
        "( u _ u ) zZ",
        "( u _ u ) zZZ",
        "( - _ - ) .oO"
    ]
}

class DesktopTamagotchi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GitPet")
        
        # Borderless, floating window
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.geometry("260x105+1100+750")
        self.root.config(bg="#1e1e2e")

        # Draggable support
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        
        # Right-click context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Feed Snack (+10 HP)", command=self.feed_manual)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)
        self.root.bind("<Button-3>", self.show_menu)

        # UI Styling (Custom Progress Bar Colors)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#313244",    # Dark slate background
            background="#fab387",     # Peach/Orange accent fill (Change to #a6e3a1 for Green, #89b4fa for Blue, #f38ba8 for Pink)
            darkcolor="#fab387",
            lightcolor="#fab387",
            bordercolor="#1e1e2e",
            thickness=6
        )

        # UI Elements
        self.sprite_label = tk.Label(
            self.root, text="", font=("Courier", 16, "bold"),
            fg="#a6e3a1", bg="#1e1e2e"
        )
        self.sprite_label.pack(pady=(8, 2))

        self.stats_label = tk.Label(
            self.root, text="", font=("Segoe UI", 8),
            fg="#cdd6f4", bg="#1e1e2e"
        )
        self.stats_label.pack()

        self.xp_bar = ttk.Progressbar(
            self.root,
            style="Custom.Horizontal.TProgressbar",
            length=200,
            mode='determinate'
        )
        self.xp_bar.pack(pady=(6, 0))

        # State Initialization
        self.state = state_manager.load_state()
        self.frame_idx = 0
        self.happy_countdown = 0

        # Start Loops
        self.animate_loop()
        self.poll_github_loop()

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
        self.state["happiness"] = min(100, self.state["happiness"] + 10)
        self.state["health"] = min(100, self.state["health"] + 10)
        self.state["mood"] = "happy"
        self.happy_countdown = 6
        state_manager.save_state(self.state)

    def animate_loop(self):
        mood = self.state.get("mood", "idle")
        frames = SPRITE_FRAMES.get(mood, SPRITE_FRAMES["idle"])
        
        self.frame_idx = (self.frame_idx + 1) % len(frames)
        self.sprite_label.config(text=frames[self.frame_idx])

        if self.happy_countdown > 0:
            self.happy_countdown -= 1
            if self.happy_countdown == 0:
                self.state["mood"] = "idle"

        self.stats_label.config(
            text=f"Lv.{self.state['level']} {self.state['name']} | HP: {self.state['health']}% | Happy: {self.state['happiness']}%"
        )
        self.xp_bar["maximum"] = self.state["max_xp"]
        self.xp_bar["value"] = self.state["xp"]

        self.root.after(500, self.animate_loop)

    def poll_github_loop(self):
        """Checks GitHub public activity every 30 seconds to respect rate limits."""
        self.state = state_manager.update_decay(self.state)
        commit_sha, repo_name = git_watcher.get_latest_github_push()

        if commit_sha and commit_sha != self.state.get("last_commit_hash"):
            if self.state.get("last_commit_hash") != "":
                self.state = state_manager.add_commit_reward(self.state, commit_sha)
                self.happy_countdown = 12  # Stay happy for ~6 seconds
                print(f"🎉 New push detected in {repo_name}!")
            else:
                self.state["last_commit_hash"] = commit_sha
                state_manager.save_state(self.state)

        # Check every 30 seconds (GitHub public API allows 60 req/hr unauthenticated)
        self.root.after(8000, self.poll_github_loop)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    DesktopTamagotchi().run()