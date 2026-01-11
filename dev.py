#!/usr/bin/env python3
"""
Build and serve the website locally.

Author(s): Aaron Hsieh @ayhsieh

Licensed under the MIT License. Copyright PennHealthX 2026.
"""
import os
import subprocess
import sys
import http.server
import socketserver
from pathlib import Path

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves .html files for clean URLs."""

    def do_GET(self):
        """Handle GET requests with clean URL support."""
        # Try to serve .html file for clean URLs
        if not self.path.endswith('.html') and not '.' in Path(self.path).name:
            # Check if corresponding .html file exists
            html_path = self.path.rstrip('/') + '.html'
            if Path('.' + html_path).exists():
                self.path = html_path

        return super().do_GET()

def main():
    """Build the site and start a local development server."""
    print("Building site...")

    # Run render.py to generate the site
    result = subprocess.run([sys.executable, "render.py"])

    if result.returncode != 0:
        print("Error: Build failed!")
        sys.exit(1)

    print("\nStarting local server at http://localhost:8000")
    print("Press Ctrl+C to stop the server")

    # Change to docs directory
    os.chdir("docs")

    # Start HTTP server with clean URL support
    PORT = 8000
    Handler = CleanURLHandler

    # Allow reusing the address immediately after the server stops
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"To fix this, either:")
            print(f"  1. Stop the other server running on port {PORT}")
            print(f"  2. Kill the process: lsof -ti:{PORT} | xargs kill -9")
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()
