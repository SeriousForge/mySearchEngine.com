from flask import Flask, render_template, request
import Part_3
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
    file_name = doc_id_to_file.get(doc_id)
    if not file_name:
        return "Page not found", 404

    # Get document info
    title = Part_3.DOCUMENTS.get(doc_id, {}).get("title", file_name)
    zip_path = "rhf.zip"

    # Extract the HTML content from the ZIP
    from zipfile import ZipFile
    with ZipFile(zip_path, 'r') as zip_archive:
        with zip_archive.open(file_name) as f:
            html_content = f.read().decode("utf-8", errors="ignore")

    return render_template(
        "view_page.html",
        doc_id=doc_id,
        title=title,
        html_content=html_content
    )


if __name__ == "__main__":
    app.run(debug=True)
