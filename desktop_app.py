import os
import sys
import threading
import time
import json
import requests
import webbrowser
from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime
import subprocess
import shutil
import glob
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# ✅ Suppress all spawned CMD windows (Windows only)
if sys.platform == "win32":
    _si = subprocess.STARTUPINFO()
    _si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _si.wShowWindow = subprocess.SW_HIDE

    _original_popen = subprocess.Popen

    def _patched_popen(*args, **kwargs):
        if "startupinfo" not in kwargs:
            kwargs["startupinfo"] = _si
        return _original_popen(*args, **kwargs)

    subprocess.Popen = _patched_popen

# Add ffmpeg/bin to PATH manually
ffmpeg_path = os.path.abspath("ffmpeg/bin")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
    print("[DEBUG] Using ffmpeg at:", shutil.which("ffmpeg"))
else:
    print("[WARN] ffmpeg/bin folder not found!")

# Add MiKTeX portable to PATH
miktex_path = os.path.abspath("latex/miktex/texmfs/install/miktex/bin/x64")
if os.path.exists(miktex_path):
    os.environ["PATH"] = miktex_path + os.pathsep + os.environ.get("PATH", "")
    os.environ["MIKTEX_PORTABLE"] = "1"  # Ensure portable mode is respected
    os.environ["MIKTEXCONFIG"] = os.path.abspath("latex/miktex/texmfs/config/miktex")
    os.environ["LATEX_EXECUTABLE"] = os.path.join(miktex_path, "latex.exe")  # Override latex binary
    os.environ["MIKTEX_UI_MODE"] = "silent"
    os.environ["MIKTEX_AUTO_INSTALL"] = "0"
    print("[DEBUG] latex resolved to:", shutil.which("latex"))
    os.environ["MIKTEX_PORTABLE"] = "1"
    print("[DEBUG] Using MiKTeX at:", miktex_path)
else:
    print("[WARN] MiKTeX not found!")

# ===================== Flask App Setup ===================== #

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

shutil.rmtree(os.path.expanduser("~/.cache/manim"), ignore_errors=True)

VIDEO_FOLDER = os.path.join("static", "output")
INPUT_FILE = "user_input.txt"

@app.route("/status")
def status():
    return jsonify({"running": True})

os.makedirs(VIDEO_FOLDER, exist_ok=True)

QUALITY_MAP = {
    "ql": "l",
    "qm": "m",
    "qh": "h"
}

# ===================== Utility ===================== #
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clear_output_folder():
    if os.path.exists(VIDEO_FOLDER):
        for filename in os.listdir(VIDEO_FOLDER):
            file_path = os.path.join(VIDEO_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"[WARN] Failed to delete {file_path}: {e}")



TEMP_SCENE_DIR = os.path.join(os.getcwd(), "scenes")
os.makedirs(TEMP_SCENE_DIR, exist_ok=True)

from manim import config, tempconfig
from change_of_basis import ChangeOfBasis_Clean
from transformation import Transformation_Clean

def generate_video(script, quality, uid):
    clear_output_folder()

    quality_map = {
        "ql": "low_quality",
        "qm": "medium_quality",
        "qh": "high_quality"
    }

    scene_class = Transformation_Clean if "transformation" in script else ChangeOfBasis_Clean
    output_path = os.path.join(VIDEO_FOLDER, "videos")
    os.makedirs(output_path, exist_ok=True)

    config.media_dir = VIDEO_FOLDER
    config.verbosity = "WARNING"

    try:
        import contextlib
        with open("manim_error_log.txt", "w", encoding="utf-8") as log, \
             contextlib.redirect_stderr(log), \
             contextlib.redirect_stdout(log):

            print(f"[INFO] Rendering {scene_class.__name__} with quality: {quality_map.get(quality, 'medium_quality')}")
            with tempconfig({
                "quality": quality_map.get(quality, "medium_quality"),
                "disable_caching": True,
                "flush_cache": True,
            }):
                scene = scene_class()
                scene.render()

            print(f"[INFO] Finished rendering {scene_class.__name__}")
    except Exception as e:
        print(f"[ERROR] Exception during rendering: {e}")
        raise

    # Find newest mp4 file
    search_pattern = os.path.join(VIDEO_FOLDER, "videos", "**", "*.mp4")
    candidates = glob.glob(search_pattern, recursive=True)

    if not candidates:
        raise FileNotFoundError(f"[ERROR] No .mp4 file found under {search_pattern}")

    original_path = max(candidates, key=os.path.getctime)
    flat_path = os.path.join(VIDEO_FOLDER, f"{uid}.mp4")

    print(f"[INFO] Found video at: {original_path}")
    print(f"[INFO] Moving video to: {flat_path}")

    try:
        os.replace(original_path, flat_path)
    except Exception as e:
        print(f"[ERROR] Could not move video: {e}")
        raise

    return flat_path



# ===================== Flask Routes ===================== #

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transform")
def transform():
    return render_template("transform.html")

@app.route("/change")
def change():
    return render_template("change.html")

@app.route("/generate", methods=["POST"])
def generate_transform():
    try:
        matrix = [[float(request.form["m00"]), float(request.form["m01"])],
                  [float(request.form["m10"]), float(request.form["m11"])]]
        vector = [float(request.form["v0"]), float(request.form["v1"])]
        quality = request.form["quality"]
        uid = datetime.now().strftime("%Y%m%d%H%M%S%f")

        with open(INPUT_FILE, "w") as f:
            f.write(json.dumps(matrix) + "\n")
            f.write(json.dumps(vector) + "\n")

        generate_video("transformation.py", quality, uid)

        return jsonify({"uid": uid, "matrix": matrix, "vector": vector})
    except Exception as e:
        print("[ERROR]", str(e))
        return str(e), 500

@app.route("/generate_change", methods=["POST"])
def generate_change():
    try:
        matrix = [[float(request.form["m00"]), float(request.form["m01"])],
                  [float(request.form["m10"]), float(request.form["m11"])]]
        quality = request.form["quality"]
        uid = datetime.now().strftime("%Y%m%d%H%M%S%f")

        with open(INPUT_FILE, "w") as f:
            f.write(json.dumps(matrix) + "\n")

        generate_video("change_of_basis.py", quality, uid)

        return jsonify({"uid": uid, "matrix": matrix})
    except Exception as e:
        print("[ERROR]", str(e))
        return str(e), 500

@app.route("/video")
def get_video():
    uid = request.args.get("uid")

    # Always resolve using the current working directory (not PyInstaller temp path)
    base_dir = os.getcwd()
    path = os.path.join(base_dir, "static", "output", f"{uid}.mp4")

    print(f"[DEBUG] Looking for video at: {path}")

    if os.path.exists(path):
        return send_file(path, mimetype="video/mp4")
    else:
        print("[ERROR] Video not found at:", path)
        return "Video not found", 404
    

@app.route("/shutdown", methods=["POST"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func:
        func()
    return "Server shutting down..."

# ===================== Desktop GUI ===================== #

def run_server():
    print("[APP] Starting Flask server...")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

def shutdown_server():
    try:
        requests.post("http://127.0.0.1:5000/shutdown")
    except Exception as e:
        print("[ERROR] Couldn't shut down Flask:", e)

# def launch_gui():
#     root = tk.Tk()
#     root.title("Linear Algebra Visualizer")
#     root.geometry("300x100")
#     root.resizable(False, False)

#     icon_path = resource_path("app.ico")
#     try:
#         root.iconbitmap(icon_path)
#     except:
#         print("[WARN] Failed to set icon")

#     tk.Label(root, text="App is running...", font=("Arial", 12)).pack(pady=10)
#     tk.Button(root, text="Quit App", command=lambda: (shutdown_server(), root.destroy())).pack()
#     root.mainloop()

# ===================== Entrypoint ===================== #

import tkinter as tk

def launch_gui():
    root = tk.Tk()
    root.title("Linear Algebra Visualizer")
    root.geometry("300x100")
    root.resizable(False, False)

    icon_path = resource_path("app.ico")
    try:
        root.iconbitmap(icon_path)
    except:
        print("[WARN] Failed to set icon")

    # ✅ Open the web app in browser automatically
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except:
        print("[WARN] Failed to open browser")

    tk.Label(root, text="App is running...", font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Quit App", command=lambda: (shutdown_server(), root.destroy())).pack()
    root.mainloop()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()

    time.sleep(1)

    def preload_latex():
        try:
            dummy_uid = "preload"
            generate_video("change_of_basis.py", "ql", dummy_uid)
            os.remove(os.path.join(VIDEO_FOLDER, f"{dummy_uid}.mp4"))
        except Exception as e:
            print(f"[WARN] Preload failed: {e}")

    preload_thread = threading.Thread(target=preload_latex)
    preload_thread.start()
    preload_thread.join()  # ✅ Wait for preload to finish before GUI opens

    print("[INFO] Launching control panel...")
    launch_gui()

    print("[INFO] GUI closed. Shutting down app.")
