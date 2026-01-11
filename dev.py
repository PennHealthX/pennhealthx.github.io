#!/usr/bin/env python3
"""
Build and serve the website locally.

Author(s): Aaron Hsieh @ayhsieh

Licensed under the MIT License. Copyright PennHealthX 2026.
"""
import http.server
import os
import socketserver
import subprocess
import sys
from pathlib import Path

import watchdog
from watchdog.observers import Observer

from render import render

DIRECTORY = "dist"


class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves .html files for clean URLs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        """Handle GET requests with clean URL support."""
        # Try to serve .html file for clean URLs
        if not self.path.endswith(".html") and "." not in Path(self.path).name:
            # Check if corresponding .html file exists
            html_path = self.path.rstrip("/") + ".html"
            if Path(DIRECTORY + html_path).exists():
                self.path = html_path

        return super().do_GET()


class FileChangeHandler(watchdog.events.FileSystemEventHandler):
    """Handler for re-rendering site on file change"""

    def on_any_event(self, event):
        """when a file changes in any way, re-render the site"""
        try:
            render()
        except Exception as e:
            print(e)


def main():
    """Build the site and start a local development server."""
    print("Building site...")

    # Run render.py to generate the site
    result = subprocess.run([sys.executable, "render.py"])

    if result.returncode != 0:
        print("Error: Build failed!")
        sys.exit(1)

    cwd = os.getcwd()

    observer = Observer()
    observer.schedule(FileChangeHandler(), os.path.join(cwd, "src"), recursive=True)
    observer.start()

    # Start HTTP server with clean URL support
    PORT = 8000

    # Allow reusing the address immediately after the server stops
    socketserver.TCPServer.allow_reuse_address = True

    print("\nStarting local server at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    try:
        with socketserver.TCPServer(("", PORT), CleanURLHandler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print("To fix this, either:")
            print(f"  1. Stop the other server running on port {PORT}")
            print(f"  2. Kill the process: lsof -ti:{PORT} | xargs kill -9")
            observer.stop()
            sys.exit(1)
        else:
            observer.stop()
            raise
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)
        observer.stop()


if __name__ == "__main__":
    main()
