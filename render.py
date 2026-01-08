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
import subprocess
from pathlib import Path
from typing import Final, Optional, Tuple, Union

import yaml
from markdown_it import MarkdownIt


def render_html(
    input_fn: Union[Path, str],
    components_dir: Union[Path, str],
    head_fn: str = "head.component.html",
    header_fn: str = "header.component.html",
    footer_fn: str = "footer.component.html",
    indent_size: int = 2,
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
        html_lines.extend([(2 * prefix) + line.rstrip() for line in f.readlines()])

    # Body: User-Defined Content
    html_lines.append((2 * prefix) + "<main>")
    if not any(
        str(input_fn).lower().endswith(ext)
        for ext in [".template.md", ".template.html"]
    ):
        print("Error: Make sure your file is a .template.md or " ".template.html file!")
        exit()
    with open(str(input_fn)) as f:
        lines = [line.rstrip() for line in f.readlines()]
    try:
        assert lines.index("---") == 0
        lines = lines[1:]
        sep_idx = lines.index("---")
    except Exception:
        print(
            "Error: Make sure your file starts with a block that looks "
            "like:\n---\ntitle: My Title Here\n---"
        )
        exit()
    input_config, input_data = lines[:sep_idx], lines[(sep_idx + 1) :]
    config = yaml.safe_load("\n".join(input_config))
    if md is None:
        html_lines.extend([(3 * prefix) + line for line in input_data])
    else:
        html_lines.append(md.render("\n".join(input_data)))
    html_lines.append((2 * prefix) + "</main>")

    # Body: Footer
    with open(os.path.join(str(components_dir), footer_fn)) as f:
        html_lines.extend([(2 * prefix) + line.rstrip() for line in f.readlines()])

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
            os.path.join(src_dir, fn)
            for fn in os.listdir(src_dir)
            if any(fn.endswith(suffix) for suffix in valid_suffixes)
        ],
        help="The input file(s) to render.",
    )
    fns_to_render = parser.parse_args().input_fn

    output_fns = []
    for input_fn in fns_to_render:
        html_str = render_html(input_fn, components_dir)
        output_fn = input_fn[input_fn.index(str(src_dir) + "/") :]
        output_fn = output_fn[(1 + len(str(src_dir))) :]
        for suffix in valid_suffixes:
            if not output_fn.endswith(suffix):
                continue
            output_fn = output_fn[: -len(suffix)] + ".html"
            break
        with open(output_fn, "w") as f:
            f.write(html_str)
        output_fns.append(output_fn)

    for fn in output_fns:
        if os.name == "nt":
            os.startfile(fn)  # type: ignore
        elif os.name == "posix":
            try:
                subprocess.run(["open", fn], check=True)
            except FileNotFoundError:
                subprocess.run(["xdg-open", fn], check=True)
        else:
            print("Unsupported operating system")


if __name__ == "__main__":
    main()
