from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
@app.route('/<name>')
def index(name=None):
    return render_template('index.html', name=name)

@app.route('/results', methods=['POST'])
def results():
    error = None
    if request.method == 'POST':
        return render_template('results.html')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('index.html', name=error)