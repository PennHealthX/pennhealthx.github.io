#!/usr/bin/python3
"""
Render HTML components as static pages.

Author(s):
    Michael Yao @michael-s-yao

Licensed under the MIT License. Copyright PennHealthX 2025.
"""
import argparse
import os
import re
import yaml
from datetime import date
from markdown_it import MarkdownIt
from pathlib import Path
from typing import Final, Optional, Tuple, Union


def render_html(
    input_fn: Union[Path, str],
    components_dir: Union[Path, str],
    head_fn: str = "head.component.html",
    header_fn: str = "header.component.html",
    footer_fn: str = "footer.component.html",
    indent_size: int = 2
) -> str:
    """
    Renders an HTML file from an input template file.
    Input:
        input_fn: the input HTML or Markdown template to render.
        components_dir: the local directory with the auxiliary HTML components.
        head_fn: the file name of the head component in `components_dir`.
        header_fn: the filename of the header component in `components_dir`.
        footer_fn: the filename of the footer component in `components_dir`.
        indent_size: indent size. Default 2 spaces.
    Returns:
        The rendered HTML string.
    """
    html_lines = ["<!DOCTYPE html>\n<html lang='en'>"]
    prefix = " " * indent_size
    md: Optional[MarkdownIt] = None
    if str(input_fn).lower().endswith(".md"):
        md = MarkdownIt("commonmark", {"breaks": True, "html": True})
        md = md.enable("table")

    # Head
    with open(os.path.join(str(components_dir), head_fn)) as f:
        html_lines.extend([prefix + line.rstrip() for line in f.readlines()])

    # Body
    html_lines.append(prefix + "<body>")

    # Body: Header
    with open(os.path.join(str(components_dir), header_fn)) as f:
        html_lines.extend([
            (2 * prefix) + line.rstrip() for line in f.readlines()
        ])

    # Body: User-Defined Content
    html_lines.append((2 * prefix) + "<main>")
    if str(input_fn).lower().endswith("team.yml"):
        with open(str(input_fn)) as f:
            team_config = yaml.safe_load(f)
        config = {
            "title": "PennHealthX - Our Team",
            "stylesheets": ["public/css/team.css"]
        }

        lines = [
            "<div class='container'>",
            prefix + f"<h1>{date.today().year} Executive Board</h1>",
            prefix + "<div class='team-grid'>"
        ]
        for person in team_config:
            headshot, name = person["headshot"], person["name"]
            role, bio = person["role"], person['bio']
            socials = {k: v for kv in person["contact"] for k, v in kv.items()}

            lines.append((2 * prefix) + "<div class='team-card'>")
            lines.append(
                (3 * prefix) + f"<img src='{headshot}' alt='{name}' "
                "class='team-image'>"
            )
            lines.append((3 * prefix) + "<div class='image-overlay'>")
            lines.append((4 * prefix) + f"<h2 class='name'>{name}</h2>")
            lines.append((4 * prefix) + f"<p class='role'>{role}</p>")
            lines.append((3 * prefix) + "</div>")
            lines.append((3 * prefix) + "<div class='hover-content'>")
            lines.append((4 * prefix) + f"<h2 class='name'>{name}</h2>")
            lines.append((4 * prefix) + f"<p class='role'>{role}</p>")
            lines.append((4 * prefix) + f"<p class='bio-text'>{bio}</p>")
            lines.append((4 * prefix) + "<div class='social-buttons'>")
            for soc_type, soc_val in socials.items():
                icon = {
                    "email": "envelope",
                    "website": "chrome",
                    "twitter": "twitter",
                    "linkedin": "linkedin"
                }[soc_type]
                if soc_type == "email" and not soc_val.startswith("mailto:"):
                    soc_val = "mailto:" + soc_val
                lines.append(
                    (5 * prefix) + f"<a href='{soc_val}' target='_blank' "
                    f"class='social-btn' aria-label='{soc_type.title()}'>"
                    f"<i class='fa fa-{icon}'></i></a>"
                )
            lines.append((4 * prefix) + "</div>")
            lines.append((3 * prefix) + "</div>")
            lines.append((2 * prefix) + "</div>")
        lines.extend([prefix + "</div>", "</div>"])
        html_lines.extend([(3 * prefix) + line for line in lines])
    else:
        with open(str(input_fn)) as f:
            lines = [line.rstrip() for line in f.readlines()]
        assert lines.index("---") == 0
        lines = lines[1:]
        sep_idx = lines.index("---")
        input_config, input_data = lines[:sep_idx], lines[(sep_idx + 1):]
        config = yaml.safe_load("\n".join(input_config))
        if md is None:
            html_lines.extend([(3 * prefix) + line for line in input_data])
        else:
            html_lines.append(md.render("\n".join(input_data)))
    html_lines.append((2 * prefix) + "</main>")

    # Body: Footer
    with open(os.path.join(str(components_dir), footer_fn)) as f:
        html_lines.extend([
            (2 * prefix) + line.rstrip() for line in f.readlines()
        ])

    html_lines.append(prefix + "</body>\n</html>")

    html_str = "\n".join(html_lines)
    for arg in re.findall(r"\{\{ ([^}]+) \}\}", html_str):
        if arg == "stylesheets":
            stylesheets = [
                f"<link rel='stylesheet' type='text/css' href='{stylesheet}'>"
                for stylesheet in config.get(arg, [])
            ]
            html_str = html_str.replace(
                f"{{{{ {arg} }}}}", ("\n" + (3 * prefix)).join(stylesheets)
            )
            continue
        html_str = html_str.replace(f"{{{{ {arg} }}}}", str(config[arg]))

    return html_str


def main() -> None:
    src_dir: Final[Union[Path, str]] = "src"
    components_dir: Final[Union[Path, str]] = "_components"
    valid_suffixes: Final[Tuple[str, ...]] = (".template.html", ".template.md")

    parser = argparse.ArgumentParser(
        description="Render HTML components as static pages."
    )
    parser.add_argument(
        "input_fn",
        nargs="+",
        type=str,
        choices=[
            os.path.join(src_dir, fn) for fn in os.listdir(src_dir)
            if fn == "team.yml" or any(
                fn.endswith(suffix) for suffix in valid_suffixes
            )
        ],
        help="The input file(s) to render."
    )
    fns_to_render = parser.parse_args().input_fn

    for input_fn in fns_to_render:
        html_str = render_html(input_fn, components_dir)
        output_fn = input_fn[input_fn.index(str(src_dir) + "/"):]
        output_fn = output_fn[(1 + len(str(src_dir))):]
        for suffix in valid_suffixes + (".yml",):
            if not output_fn.endswith(suffix):
                continue
            output_fn = output_fn[:-len(suffix)] + ".html"
            break
        with open(output_fn, "w") as f:
            f.write(html_str)


if __name__ == "__main__":
    main()
