from flask import Flask, render_template, request
import Part_2
import os

app = Flask(__name__)

# Global variables to store your index data
word_frequency = None
doc_id_to_file = None

@app.before_request
def initialize_index():
    global word_frequency, doc_id_to_file
    if word_frequency is None:
        word_frequency, doc_id_to_file = Part_2.build_index("Jan.zip")
        print("Indexing complete! Ready to search.")


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            results = Part_2.search_loop_equiv(query, word_frequency, doc_id_to_file)


    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
