# Static Site Generator

This is just a very simple Static Site Generator that I am writing with Python and Pandoc. Markdown to HTML transformation is handled
by calling Pandoc, while Python takes care of the rest of the logic.

## Usage
Call the main script:
```
python generator.py
```

The script expects one `posts/` folder at the same level as the script. One HTML page will be created per `.md` file found under `posts/`.
 - Each `.md` file must have a front matter with YAML format, and include at least one field: `post_id`. This ID will identify
the post/page, and be used to generate hyperlinks from one page to another.
 - When linking to another post, one should write `\[text of the hyperlink\](\%link:post_id%)`. The script will use regular expressions
to find `%link:post_id%` and substitute it with the appropriate URL.
