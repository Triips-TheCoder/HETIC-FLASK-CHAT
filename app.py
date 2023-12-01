from flask import Flask, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__=='__main__':
    app.run(debug = True)