import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend, required for Flask
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)

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

    # Save plot to an in-memory buffer and encode as base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    return image_base64

# --- Routes ---

# "A Minimal Application"
@app.route('/')
def home():
    # "Rendering Templates"
    return render_template('index.html')

# "Routing"
@app.route('/report')
def report():
    # "Rendering Templates"
    return render_template('report.html')

# "Routing"
@app.route('/visualization')
def visualization():
    # "Rendering Templates"
    plot = generate_scatterplot()
    return render_template('visualization.html', plot=plot)

# "HTTP Methods"
@app.route('/queries', methods=['GET', 'POST'])
def queries():
    result = None
    error = None
    # "The Request Object"
    if request.method == 'POST':
        try:
            # "The Request Object"
            a = float(request.form['operand_a'])
            b = float(request.form['operand_b'])
            result = multiply(a, b)
        except ValueError:
            error = "Both fields must be numbers."
    # "Rendering Templates"
    return render_template('queries.html', result=result, error=error)

# "Debug Mode"
if __name__ == '__main__':
    app.run(debug=True)