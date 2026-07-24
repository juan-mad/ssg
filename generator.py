import os
import pathlib
import subprocess
import re
from yaml import safe_load

def read_frontmatter(file: pathlib.Path):
    """
    Reads the YAML-formatted frontmatter of Markdown files. 
    Args:
        file: path of the markdown file from which to read YAML frontmatter
    """
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

            if line.strip() == "---":
                break
            else:
                yaml_lines.append(line)

        front_matter = safe_load("".join(yaml_lines))

        if front_matter is None:
            front_matter = {}
        if not isinstance(front_matter, dict):
            raise ValueError(f"Could not parse frontmatter of {file} as dict")

        return front_matter

def get_relative_path(from_path: pathlib.Path, to_path: pathlib.Path) -> pathlib.Path:
    return to_path.relative_to(from_path.parent, walk_up=True)
    

def generate_internal_hyperlinks(file: pathlib.Path, public_files: dict):
    """
    Parses internal hyperlinks to other pages.
    Args:
        file (pathlib.Path): path to file to generate hyperlinks in
        post_files (dict): post_id -> filepath relationships, so we know where to direct each link
    """
    link_pattern = re.compile(r"%link:([^%]+)%")
    text = file.read_text(encoding="utf-8")

    warnings = []
    def replace(matchobj):
        post_id = matchobj.group(1)
        if post_id not in public_files:
            warnings.append(
                f"unknown post_id `{post_id}` to link to in `{file}`"
            )
            # returns the entire match, so we do nothing
            return matchobj.group(0)

        # Return first capture group, which should be the post ID.
        relative_path = get_relative_path(file, public_files[post_id])
        return str(relative_path)

    replaced_text, replacement_count = link_pattern.subn(
        lambda m: replace(m), text
    )

    if replacement_count > 0:
        file.write_text(replaced_text, encoding="utf-8")
    
    return warnings
           

def generate_standalone_html(file: pathlib.Path, source_parent_dir: pathlib.Path, output_parent_dir: pathlib.Path) -> pathlib.Path:
    """
    Create standalone HTML file from a Markdown file. Replicates the same folder structure present in source_parent_dir
    inside output_parent_dir.
    
    Args:
        file: path to the source markdown file
        source_parent_dir: path to the parent directory where the posts are
        output_parent_dir: path to the parent directory where the HTML files will be saved

    Returns:
        path of the output HTML file
    """
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
        "--from", "markdown",  # from markdown format
        "--to", "html5",  # to HTML5 format
        # HTML template file to use. Variables appear using $(varname)$ and similar syntax.
        # They are read from the YAML frontmatter automatically, and might have some default values
        # if they don't appear there, not sure. Refer to pandoc docs for this.
        "--template", "mytemplate.html",
        # Link to CSS style file. Multiple may be specified.
        "--css", ".." / pathlib.Path("resources/mystyle.css").relative_to(relative_leaf_dir, walk_up=True),
        str(file),  # input filename path
        "--output", str(output_file_path),
    ])

    return output_file_path


def main():
    if not os.path.exists("public"):
        os.mkdir("public")

    public_path = pathlib.Path("./public")

    posts_path = pathlib.Path("./posts")

    # Recursively find all .md files inside the posts directory
    # dict with post_id -> Path for each post
    # raises an error if no post_id exists in a post, or if the value is not unique
    post_files = {}
    for f in posts_path.rglob("*.md"):
        front_matter = read_frontmatter(f)
        if "post_id" not in front_matter:
            raise ValueError(f"post_id field not found in frontmatter of {f}")
        post_id = front_matter["post_id"]
        if post_id in post_files:
            raise ValueError(f"Encountered repeated post_id value `{post_id}` in {f} and {post_files[post_id]}.")
        post_files[front_matter["post_id"]] = f

    # Generate HTML files and get post_id -> Path dict with the HTML paths
    public_files = {}
    for post_id, f in post_files.items():
        public_files[post_id] = generate_standalone_html(f, posts_path, public_path)

    # Parse internal hyperlinks
    for post_id, f in public_files.items():
        warnings = generate_internal_hyperlinks(f, public_files)
        if warnings:
            print(warnings)

        
    print("Done!")

if __name__ == "__main__":
    main()

