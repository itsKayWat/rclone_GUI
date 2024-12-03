import tkinter as tk
import subprocess
import os

def run_command(command):
    try:
        rclone_path = r"C:\Users\xlkay\Downloads\rclone-v1.68.2-windows-amd64\rclone-v1.68.2-windows-amd64\rclone.exe"
        subprocess.run([rclone_path] + command.split())
    except Exception as e:
        print(f"Error: {e}")

def view_git_log():
    try:
        os.startfile("git-log.txt")
    except Exception as e:
        print(f"Error: {e}")

# Create the main window
root = tk.Tk()
root.title("Rclone Tool User Interface")
root.geometry("400x400")
root.configure(bg="#004d00")  # Dark green background

# Create buttons for rclone commands
commands = [
    "lsjson",
    "lsl",
    "md5sum",
    "mkdir",
    "move",
    "sync",
    "rc",
    "serve",
    "version"
]

for cmd in commands:
    button = tk.Button(root, text=f"Run {cmd}", command=lambda c=cmd: run_command(c), bg="#66ff66", fg="black", font=("Arial", 10))
    button.pack(pady=5)

# Button to view git log
view_log_button = tk.Button(root, text="View Git Log", command=view_git_log, bg="#ffff66", fg="black", font=("Arial", 10))
view_log_button.pack(pady=10)

# Exit button
exit_button = tk.Button(root, text="Exit", command=root.quit, bg="#ff6666", fg="black", font=("Arial", 10))
exit_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()