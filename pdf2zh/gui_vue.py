"""
Author: Rongxin rongxin@u.nus.edu
Date: 2025-08-13 13:17:44
LastEditors: Rongxin rongxin@u.nus.edu
LastEditTime: 2025-08-13 13:17:56
FilePath: /PDFMathTranslate/pdf2zh/gui_vue.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


def _spawn(cmd: list[str], cwd: Path | None = None) -> subprocess.Popen:
    kwargs = {
        "cwd": str(cwd) if cwd else None,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "bufsize": 1,
    }
    if sys.platform == "win32":
        # start new process group on Windows
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    else:
        # start new session so we can SIGTERM the whole group
        kwargs["start_new_session"] = True
    return subprocess.Popen(cmd, **kwargs)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    gui_root = repo_root / "gui-vue"

    processes: list[subprocess.Popen] = []

    try:
        # 1) Start Flask backend if not already running
        flask_proc = _spawn(
            [sys.executable, "-m", "pdf2zh.pdf2zh", "--flask"], cwd=repo_root
        )
        processes.append(flask_proc)

        # 2) Celery/Redis not used in in-memory mode

        # 3) Start Vue dev server
        # Choose package manager: prefer pnpm, fallback to npm
        pkg = (
            "pnpm" if shutil.which("pnpm") else ("npm" if shutil.which("npm") else None)
        )
        if not pkg:
            print(
                "ERROR: Neither pnpm nor npm found in PATH. Please install Node.js (npm) or pnpm."
            )
            return 1

        if not (gui_root / "node_modules").exists():
            install_proc = _spawn([pkg, "install"], cwd=gui_root)
            install_code = install_proc.wait()
            if install_code != 0:
                print(f"ERROR: {pkg} install failed with exit code {install_code}")
                return install_code

        dev_cmd = (
            [pkg, "run", "dev", "--", "--host"]
            if pkg == "pnpm"
            else [pkg, "run", "dev", "--", "--host"]
        )
        vite_proc = _spawn(dev_cmd, cwd=gui_root)
        processes.append(vite_proc)

        # 4) Wait for Vite to come up on default port and open browser
        url = "http://localhost:5173"
        ready = False
        for _ in range(90):  # up to ~90s
            try:
                with urllib.request.urlopen(url, timeout=1) as resp:
                    if resp.status < 500:
                        ready = True
                        break
            except Exception:
                pass
            # Drain a bit of logs to keep buffers moving
            if vite_proc.stdout:
                for _ in range(5):
                    line = vite_proc.stdout.readline()
                    if not line:
                        break
                    if "Local" in line and "5173" in line:
                        ready = True
                        break
            if ready:
                break
            time.sleep(1)
        if ready:
            webbrowser.open(url)
        else:
            print(
                "WARNING: Vite dev server did not become ready on http://localhost:5173 within timeout."
            )
            print(
                "You can manually run: cd gui-vue &&",
                pkg,
                "install &&",
                pkg,
                "run dev -- --host",
            )

        # 5) Stream logs; exit when either child exits
        while True:
            if flask_proc.poll() is not None:
                print("Flask backend exited; shutting down GUI...")
                break
            if vite_proc.poll() is not None:
                print("Vite dev server exited; shutting down backend...")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        for p in processes:
            try:
                if p.poll() is None:
                    if sys.platform == "win32":
                        # send CTRL_BREAK to process group then terminate
                        try:
                            p.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
                            time.sleep(0.5)
                        except Exception:
                            pass
                        p.terminate()
                    else:
                        try:
                            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                        except ProcessLookupError:
                            p.terminate()
            except (ProcessLookupError, OSError):
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
