from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
	return "Hello!"

@app.route('auth'):
	#Should be 301 Redirect to Dropbox app authentication		
	return "auth"


if __name__ == "__main__":
	app.run()
