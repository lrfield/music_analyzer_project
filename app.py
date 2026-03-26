import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

# Import all MongoDB interaction from db.py
import db as database

app = Flask(__name__)

# --- Business logic ---

def multiply(a, b):
    return a * b

def generate_scatterplot():
    x = np.random.rand(50)
    y = np.random.rand(50)

    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_title('Random Scatterplot')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    return image_base64

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/visualization')
def visualization():
    plot = generate_scatterplot()
    return render_template('visualization.html', plot=plot)

@app.route('/queries', methods=['GET', 'POST'])
def queries():
    # Populate dropdowns from the database
    countries = database.get_countries()

    results       = None
    query_type    = None
    query_country = None

    if request.method == 'POST':
        query_type    = request.form['query_type']   # 'artists' or 'genre'
        query_country = request.form['country']

        if query_type == 'artists':
            results = database.top_artists_in_country(query_country)
        elif query_type == 'genre':
            results = database.top_genres_in_country(query_country)

    return render_template(
        'queries.html',
        countries=countries,
        results=results,
        query_type=query_type,
        query_country=query_country
    )

if __name__ == '__main__':
    app.run(debug=False)