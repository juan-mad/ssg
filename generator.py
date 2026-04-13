import os
import pathlib
import subprocess

def main():
    if not os.path.exists("public"):
        os.mkdir("public")

    public_path = pathlib.Path("./public")

# Recursively find all .md files inside the posts directory
    posts_path = pathlib.Path("./posts")
    for f in posts_path.rglob("*.md"):
        
        # just the filename
        filename = f.name

        # get the relative leaf directory in which the input file is at
        relative_path = str(f.relative_to(posts_path))
        relative_leaf_dir = relative_path[:-len(filename)]

        # if we need to make a subdirectory in the output, public directory, make it
        if relative_leaf_dir != "":
            (public_path / relative_leaf_dir).mkdir(parents=True, exist_ok=True)

        output_file_path = public_path / f.relative_to(posts_path).with_suffix(".html")

        # Attempt to parse file.
        print(f"Parsing {str(f)}...")
        subprocess.run([
            "pandoc",  # our parser
            "--standalone",  # create a full HTML file, not a document fragment
            "--mathjax",  # math parsing from LaTeX expressions using MathJAX. Use $ $ and $$ $$.
            "-f", "markdown",  # from markdown format
            "-t", "html5",  # to HTML5 format
            str(f),  # input filename path
            "-o", str(output_file_path),
        ])

    print("Done!")

if __name__ == "__main__":
    main()

