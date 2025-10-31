from flask import Flask, render_template, request
import Part_3
from zipfile import ZipFile
import os

app = Flask(__name__)

# Global variables to store your index data
word_frequency = None
doc_id_to_file = None

@app.before_request
def initialize_index():
    global word_frequency, doc_id_to_file
    if word_frequency is None:
        word_frequency, doc_id_to_file = Part_3.build_index("rhf.zip")
        print("Indexing complete! Ready to search.")


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            results = Part_3.search_loop_equiv(query, word_frequency, doc_id_to_file)


    return render_template("index.html", results=results, query=query)

@app.route("/view/<int:doc_id>")
def view_page(doc_id):
    """Display the HTML content of a specific document."""
    file_name = doc_id_to_file.get(doc_id)
    if not file_name:
        abort(404, "Document not found")

    try:
        with ZipFile(zip_path, "r") as zip_archive:
            with zip_archive.open(file_name) as file_in_zip:
                html_content = file_in_zip.read().decode("utf-8", errors="ignore")

        title = Part_3.TITLE_RE.search(html_content)
        title_text = title.group(1).strip() if title else file_name

        return render_template(
            "view_page.html",
            title=title_text,
            html_content=html_content
        )
    except Exception as e:
        print(f"Error opening {file_name}: {e}")
        abort(500, "Failed to load document")

if __name__ == "__main__":
    app.run(debug=True)
