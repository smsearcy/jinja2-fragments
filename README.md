# Jinja2 fragments

Jinja2 Fragments allows rendering individual blocks from 
[Jinja2 templates](https://palletsprojects.com/p/jinja/). This library was created
to enable the pattern of 
[Template Fragments](https://htmx.org/essays/template-fragments/) with Jinja2. It's a
great pattern if you are using [HTMX](https://htmx.org/) or some other library that
leverages fetching partial HTML.

With jinja2, if you have a template block that you want to render by itself and
as part of another page, you are forced to put that block on a separate file and then
use the [include tag](https://jinja.palletsprojects.com/en/3.1.x/templates/#include)
(or [Jinja Partials](https://github.com/mikeckennedy/jinja_partials)) on the wrapping
template.

With Jinja2 Fragments, following the 
[Locality of Behavior](https://htmx.org/essays/locality-of-behaviour/) design principle
you have a single file for both cases. See below for examples.

## Install

It's just `pip install jinja2-fragments` and you're all set. It's a pure Python package
that only needs `jinja2` (for obvious reasons!).

## Usage

This is an example of how to use the library with vanilla Jinja2. Given the template `page.html.jinja2`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>This is the title</title>
</head>
<body>
    <h1>This is a header</h1>
    {% block content %}
    <p>This is the magic number: {{ magic_number }}.</p>
    {% endblock %}
</body>
</html>
```

If you want to render only the `content` block, do:

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block

environment = Environment(
    loader=FileSystemLoader("my_templates"), 
    autoescape=select_autoescape(("html", "jinja2"))
)
rendered_html = render_block(
    environment, "page.html.jinja2", "content", magic_number=42
)
```

And this will only render:
```html
<p>This is the magic number: 42.</p>
```

## Usage with Flask

If you want to use Jinja2 Fragments with Flask, assuming the same template as the
example above, do:

```python
from flask import Flask, render_template
from jinja2_fragments.flask import render_block

app = Flask(__name__)

@app.get("/full_page")
def full_page():
    return render_template("page.html.jinja2", magic_number=42)


@app.get("/only_content")
def only_content():
    return render_block("page.html.jinja2", "content", magic_number=42)
```