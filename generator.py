import os
import pathlib
import subprocess
from yaml import safe_load

def read_frontmatter(file: pathlib.Path):
    yaml_lines = []
    with open(str(file), 'r', encoding='utf-8') as f:
        first_line = True
        for line in f:
            if first_line:
                if line.strip() != "---":
                    # File with no frontmatter
                    # handle it
                    return {}
                else:
                    first_line = False
                    continue
            else:
                if line.strip() == "---":
                    break
                else:
                    yaml_lines.append(line)

        front_matter = "".join(yaml_lines)

        return safe_load(front_matter)

            

def generate_standalone_html(file: pathlib.Path, source_parent_dir: pathlib.Path, output_parent_dir: pathlib.Path):
    # just the filename
    filename = file.name

    # get the relative leaf directory in which the input file is at
    relative_path = str(file.relative_to(source_parent_dir))
    relative_leaf_dir = relative_path[:-len(filename)]

    # if we need to make a subdirectory in the output, public directory, make it
    if relative_leaf_dir != "":
        (output_parent_dir / relative_leaf_dir).mkdir(parents=True, exist_ok=True)

    output_file_path = output_parent_dir / file.relative_to(source_parent_dir).with_suffix(".html")

    # Attempt to parse file.
    print(f"Parsing {str(file)}...")
    subprocess.run([
        "pandoc",  # our parser
        "--standalone",  # create a full HTML file, not a document fragment
        "--mathjax",  # math parsing from LaTeX expressions using MathJAX. Use $ $ and $$ $$.
        "-f", "markdown",  # from markdown format
        "-t", "html5",  # to HTML5 format
        # HTML template file to use. Variables appear using $(varname)$ and similar syntax.
        # They are read from the YAML frontmatter automatically, and might have some default values
        # if they don't appear there, not sure. Refer to pandoc docs for this.
        "--template", "mytemplate.html",
        # Link to CSS style file. Multiple may be specified.
        # esto funciona. no preguntes :)
        "-c", ".." / pathlib.Path("resources/mystyle.css").relative_to(relative_leaf_dir, walk_up=True),
        str(file),  # input filename path
        "-o", str(output_file_path),
    ])


def main():
    if not os.path.exists("public"):
        os.mkdir("public")

    public_path = pathlib.Path("./public")

    # Recursively find all .md files inside the posts directory
    posts_path = pathlib.Path("./posts")
    for f in posts_path.rglob("*.md"):
        front_matter = read_frontmatter(f)
        generate_standalone_html(f, posts_path, public_path)

    print("Done!")

if __name__ == "__main__":
    main()

