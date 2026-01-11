#!/usr/bin/python3
"""
Render HTML components as static pages.

Author(s):
    Michael Yao @michael-s-yao and Aaron Hsieh @ayhsieh

Licensed under the MIT License. Copyright PennHealthX 2026.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

import yaml
from markdown_it import MarkdownIt

def is_valid_front_matter(text: str) -> int:
    """Checks if text has valid front matter and returns the end line"""
    lines = text.split("\n")
    indices = [i for i, line in enumerate(lines) if line == "---"][:2]
    error_message = "Error: Make sure your file starts with a block that looks " \
            "like:\n---\ntitle: My Title Here\n---"

    if len(indices) != 2:
        raise ValueError(error_message)

    start, end = indices
    if start != 0:
        raise ValueError(error_message)

    return end

def parse_config(text: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown file."""
    end = is_valid_front_matter(text)
    lines = text.split("\n")
    return yaml.safe_load("\n".join(lines[1:end]))

def markdown_to_html(text: str) -> str:
    """Convert markdown content (after frontmatter) to HTML."""
    end = is_valid_front_matter(text)
    lines = text.split("\n")
    content = "\n".join(lines[end + 1:])

    md = MarkdownIt("commonmark", {"breaks": True, "html": True})
    md = md.enable("table")
    return md.render(content)

def fill_template_variables(html: str, config: Dict[str, Any]) -> str:
    """Replace {{ variable }} placeholders with config values."""
    for arg in re.findall(r"\{\{ ([^}]+) \}\}", html):
        if arg == "stylesheets":
            stylesheets = [
                f"<link rel='stylesheet' type='text/css' href='{stylesheet}'>"
                for stylesheet in config.get(arg, [])
            ]
            html = html.replace(f"{{{{ {arg} }}}}", "\n  ".join(stylesheets))
        elif arg == "scripts":
            scripts = [
                f"<script src='{script}'></script>"
                for script in config.get(arg, [])
            ]
            html = html.replace(f"{{{{ {arg} }}}}", "\n  ".join(scripts))
        else:
            html = html.replace(f"{{{{ {arg} }}}}", str(config.get(arg, "")))

    return html

def generate_team_cards_html(team_yml_path: str) -> str:
    """Generate team cards HTML from team.yml file."""
    with open(team_yml_path, "r") as f:
        team_data = yaml.safe_load(f)

    # Icon mapping for contact types
    icon_map = {
        'email': 'envelope',
        'website': 'chrome',
        'twitter': 'twitter',
        'linkedin': 'linkedin'
    }

    cards = []
    for member in team_data:
        # Skip the year entry
        if 'year' in member:
            continue

        # Generate social buttons
        social_buttons = []
        for contact_item in member.get('contact', []):
            for contact_type, url in contact_item.items():
                icon = icon_map.get(contact_type, 'link')
                href = f"mailto:{url}" if contact_type == 'email' and not url.startswith('mailto:') else url
                label = contact_type.capitalize()
                social_buttons.append(
                    f'<a href="{href}" target="_blank" class="social-btn" aria-label="{label}">'
                    f'<i class="fa fa-{icon}"></i></a>'
                )

        social_html = '\n                '.join(social_buttons)

        # Generate team card HTML
        card = f"""<div class="team-card">
            <img src="/{member['headshot']}" alt="{member['name']}" class="team-image">
            <div class="image-overlay">
              <h2 class="name">{member['name']}</h2>
              <p class="role">{member['role']}</p>
            </div>
            <div class="hover-content">
              <h2 class="name">{member['name']}</h2>
              <p class="role">{member['role']}</p>
              <p class="bio-text">{member['bio']}</p>
              <div class="social-buttons">
                {social_html}
              </div>
            </div>
          </div>"""
        cards.append(card)

    return '\n'.join(cards)

# load components
with open("_components/footer.component.html", "r") as f:
    footer = f.read()
with open("_components/head.component.html", "r") as f:
    head = f.read()
with open("_components/header.component.html", "r") as f:
    header = f.read()

# delete docs folder if it exists, then create a fresh one
if os.path.exists("docs"):
    shutil.rmtree("docs")
os.makedirs("docs")

# copy public folder to docs so assets are accessible
if os.path.exists("public"):
    shutil.copytree("public", "docs/public")
    print("Copied public/ folder to docs/")

# process each template file in src
src_files = os.listdir("src")
for filename in src_files:
    if not (filename.endswith(".template.md") or filename.endswith(".template.html")):
        continue

    filepath = os.path.join("src", filename)
    with open(filepath, "r") as f:
        text = f.read()

    # check if front matter is valid
    end = is_valid_front_matter(text)

    # get config (e.g. stylesheets, scripts) from front matter
    config = parse_config(text)

    if filename.endswith(".template.md"):
        content_html = markdown_to_html(text)
    else:
        end = is_valid_front_matter(text)
        lines = text.split("\n")
        content_html = "\n".join(lines[end + 1:])

    html = f"""<!DOCTYPE html>
<html lang='en'>
  {head}
  <body>
    {header}
    <main>
{content_html}
    </main>
    {footer}
  </body>
</html>"""

    html = fill_template_variables(html, config)

    if filename.endswith(".template.md"):
        output_filename = filename.replace(".template.md", ".html")
    else:
        output_filename = filename.replace(".template.html", ".html")

    output_path = os.path.join("docs", output_filename)
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Generated {output_path}")

# generate team.html from team.yml
team_yml_path = "src/team.yml"
if os.path.exists(team_yml_path):

    # Read team data to get the year
    with open(team_yml_path, "r") as f:
        team_data = yaml.safe_load(f)

    year = None
    for item in team_data:
        if 'year' in item:
            year = item['year']
            break

    year_display = year or 2026

    # Create team config (since the yaml file doesn't have front matter)
    team_config = {
        "title": "PennHealthX - Our Team",
        "stylesheets": ["/public/css/team.css"]
    }

    # Generate team cards HTML
    team_cards_html = generate_team_cards_html(team_yml_path)

    # Wrap in container div with proper structure matching team.template.html
    content_html = f"""<div class='container'>
  <h1 id="team-year">{year_display} Executive Board</h1>
  <div class='team-grid' id="team-grid">
{team_cards_html}
  </div>
</div>"""

    # Construct full HTML page
    html = f"""<!DOCTYPE html>
<html lang='en'>
  {head}
  <body>
    {header}
    <main>
{content_html}
    </main>
    {footer}
  </body>
</html>"""

    # Fill in template variables
    html = fill_template_variables(html, team_config)

    # Write output file
    output_path = os.path.join("docs", "team.html")
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Generated {output_path}")