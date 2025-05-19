from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
import requests
import json
from flask import request, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

api_key = "AIzaSyCkvFTUftOIQP0uYMDgxIuRZL2d6qruB3w"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"


# Load models and encoders

model = joblib.load(r'C:\Users\Asus Laptop\Downloads\SalesPredictionFlask\model\sales_prediction_model.pkl')
label_encoders = joblib.load(r'C:\Users\Asus Laptop\Downloads\SalesPredictionFlask\model\label_encoders.pkl')


# Dummy user database
users = {}

# Load state-district data from Excel
df = pd.read_excel('final_professional_sales_dataset_with_month_year.xlsx')  # or full path
df.dropna(subset=['State', 'District'], inplace=True)

# Create State → [Districts] mapping
state_district_map = df.groupby('State')['District'].unique().apply(list).to_dict()

 
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def home_redirect():
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users:
            flash('Email already registered!')
        else:
            users[email] = generate_password_hash(password)
            flash('Signup successful! Please login.')
            return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email in users and check_password_hash(users[email], password):
            session['username'] = email
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
            return render_template('login.html')
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")

    try:
        # Gemini Flash 1.5 API key
        api_key = "AIzaSyCkvFTUftOIQP0uYMDgxIuRZL2d6qruB3w"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_input}]
                }
            ]
        }

        # First request
        response = requests.post(url, headers=headers, json=data)

        # Retry once if 502 error
        if response.status_code == 502:
            import time
            time.sleep(2)  # wait for 2 seconds
            response = requests.post(url, headers=headers, json=data)

        print("Status Code:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            result = response.json()
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})

        elif response.status_code == 502:
            return jsonify({"reply": "⚠️ Gemini servers are busy right now. Please try again in a few seconds."}), 502

        else:
            return jsonify({"reply": f"❌ Error {response.status_code}: {response.text}"}), 500

    except Exception as e:
        return jsonify({"reply": f"❌ Something went wrong with Gemini API: {str(e)}"}), 500




    
@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    else:
        return redirect(url_for('login'))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            state = request.form.get('state')
            district = request.form.get('district')
            category = request.form.get('category')
            date_str = request.form.get('date')  # format: yyyy-mm-dd

            if not state or not district or not category or not date_str:
                return render_template('result.html', error="Please select all fields, including date.")

            # Extract month and year from the date
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_name = date_obj.strftime("%B")
            year = date_obj.year

            # Encode inputs
            state_enc = label_encoders['State'].transform([state])[0]
            district_enc = label_encoders['District'].transform([district])[0]
            category_enc = label_encoders['Category'].transform([category])[0]

            # Build feature array including Month and Year
            X_input = [[state_enc, district_enc, category_enc, date_obj.month, year]]

            # Predict quantity using your updated single model
            predicted_quantity = round(model.predict(X_input)[0])

            # Fixed/static values (customize if needed)
            unit_price = 577.1
            profit_margin = 0.31

            # Compute outputs
            predicted_unit_price = unit_price
            predicted_profit_margin = profit_margin
            predicted_profit = round(predicted_quantity * unit_price * profit_margin, 2)


            return render_template('result.html',
                                   state=state,
                                   district=district,
                                   category=category,
                                   month=month_name,
                                   year=year,
                                   predicted_quantity=predicted_quantity,
                                   predicted_unit_price=predicted_unit_price,
                                   predicted_profit_margin=predicted_profit_margin,
                                   predicted_profit=predicted_profit)

        except Exception as e:
            return render_template('result.html', error=f"Prediction failed: {e}")

    # For GET
    state_options = label_encoders['State'].classes_
    district_options = label_encoders['District'].classes_
    category_options = label_encoders['Category'].classes_

    return render_template('prediction.html',
                           states=state_options,
                           districts=district_options,
                           categories=category_options)





@app.route('/get_districts/<state>')
def get_districts(state):
    districts = state_district_map.get(state, [])
    return {'districts': districts}


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

