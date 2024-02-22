#!/usr/bin/python3

from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/index', methods=['GET', 'POST'])
def index():
  print("index")
  if request.method == 'POST':
    ssid=request.form.get('ssid')
    password=request.form.get('password')
    # TODO: add logic to update wifi configuration with these credentials
    return "Wifi settings updated. Attempting to connect..."
  #render simple form for ssid and password input
  return render_template_string('''
				<form action="" method="post">
					SSID: <input type="text" name="ssid"><br>
					Password: <input type="password" name="password"><br>
					<input type="submit" value="Submit"
				</form>
				''')
  if __name__ == '__main__':
    print("if name == main")
    app.run(host="0.0.0.0", port=8080)


