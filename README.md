# PennHealthX Website

[![LICENSE](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![CONTACT](https://img.shields.io/badge/contact-pennhealthx%40gmail.com-blue)](mailto:pennhealthx@gmail.com)
[![CONTACT](https://img.shields.io/badge/contact-michael.yao%40pennmedicine.upenn.edu-blue)](mailto:michael.yao@pennmedicine.upenn.edu)

This repository contains the source code for the PennHealthX website. We have made significant efforts to make adding new website pages and editing existing ones as easy as possible.

## Installation and Setup

To modify Penn HealthX's website, you first need to download a local copy of this repository:

```
git clone https://github.com/PennHealthX/pennhealthx.github.io.git
cd pennhealthx.github.io
```

If you run into issues with the above Terminal commands, you might not have `git` installed. See [these Git installation instructions](https://github.com/git-guides/install-git) or [contact us](mailto:michael.yao@pennmedicine.upenn.edu) if this is the case.

We also assume that you have some version of [Python 3](https://www.python.org/downloads/) installed on your computer. If this is not the case, see [these instructions](https://realpython.com/installing-python/) for assistance.

This repository uses Python to render website pages. Install the relevant dependencies:

```
python3 -m pip install -r requirements.txt
```

## Usage

Unless you are an experienced web developer, **the only files you should ever need to modify are in the `src` and `public` folders**. The files in `public` correspond to assets such as PDFs, images, and other attachments or documents that you want to include on the website. The files in `src` contain the raw text for the pages of the website.

Each website page is specified by either a `template.md` or `template.html` file in the `src` directory. Most users will likely by using the `template.md` option.

### Creating a New Webpage

Suppose you want to create a new webpage at `pennhealthx.com/my-webpage`. To do this, create a new text file `src/my-webpage.template.md` with the following content:

```
---
title: [TITLE OF WEBPAGE]
---

[MY CONTENT]
```

where `[TITLE OF WEBPAGE]` is the title of your webpage (should be no more than a few words), and `[MY CONTENT]` is the text content of your website in Markdown format (if you're not sure what Markdown is, check out this [super quick tutorial](https://www.markdowntutorial.com)).

Check out [`src/projects.template.md`](src/projects.template.md) for an example.

### Advanced: Creating a New Webpage

If you have experience writing HTML webpages, you can also instead create a new text file `src/my-webpage.template.html` with the following content:

```
---
title: [TITLE OF WEBPAGE]
stylesheets:
  - [OPTIONAL RELATIVE PATHS TO STYLESHEETS]
---
[MY HTML CONTENT]
```

There are a couple of quirks of `template.html` files that are different from your usual HTML files.

First, note that the YAML-style metadata should still be included at the top of the file separated by 3 dashes and a newline character before and after. You can also include a list of paths to CSS stylesheets as well using the optional `stylesheets` keyword argument.

Second, you only need to include the HTML elements that you would include within the `<main>` HTML element. This means you don't need to (and should not!) define the `<head>`, `<header>`, or `<footer>` elements. This is to ensure that all webpages follow a consistent format.

Check out [`src/index.template.html`](src/index.template.html) for an example.

### Building a Webpage

Once you have a completed `template.md` or `template.html` webpage, you can build it by running

```
python3 render.py src/my-webpage.template.md  # or python3 render.py src/my-webpage.template.html
```

This will create a rendered `my-webpage.html` file in the working directory. To preview this webpage, you can open the file using your favorite web browser.

### Updating the [Team](https://www.pennhealthx.com/team) Page

The webpage listing all of the members of the Executive Board works differently from the other pages. All you need to do is update the `src/team.yml` page with the new members. Each member must have the fields (1) `name`; (2) `role`; (3) `headshot` (the relative path to the file with their *square*-shaped headshot); (4) `contact` (must have at least the `email` field); and (5) `bio`.

If you are updating the teams page for a new year, edit the first line to the correct year:

```yaml
- year: 2026
# rest of yaml file
```

### Testing Your Changes

To test your website changes locally before deploying, you'll need to run a local web server.

First, ensure you have [Node.js](https://nodejs.org/) installed on your computer. This will give you access to the `npx` command. You can verify Node.js is installed by running the following in your terminal:

```
node --version
```

If Node.js is not installed, download it from [nodejs.org](https://nodejs.org/).

Once Node.js is installed, you can start a local web server from the repository directory:

```
npx serve -p 8000
```

This will start a local server at `http://localhost:8080`. Open this URL in your web browser to preview your website changes locally.


### Deploying Your Changes

Once you are satisfied with your changes, you can create a new [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) to add your changes to the website:

```
git checkout -b my-new-branch-name  # Replace `my-new-branch-name` with a name for your branch.
git add .
git commit -m "Write a short summary of your changes here."
git push origin my-new-branch-name
```

You can then open the pull request on [GitHub](https://github.com/PennHealthX/pennhealthx.github.io) - tag one of the Co-Presidents or VPs of Marketing to review before the changes go live. 

## Contact

Questions and comments are welcome. Suggestions can be submitted through GitHub issues. Contact information is linked below.

[PennHealthX Team](mailto:pennhealthx@gmail.com)

[Michael Yao](mailto:michael.yao@pennmedicine.upenn.edu)

## License

This repository is MIT licensed (see [LICENSE](LICENSE)).

## Acknowledgments

The design of this website was inspired by [Cosmos](https://cosmos.network).
