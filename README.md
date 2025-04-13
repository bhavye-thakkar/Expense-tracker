<h1 align="center">📱 Expense Tracker Mobile App</h1>
  <div align="center">
    An intuitive and lightweight mobile application to track your daily expenses, set budgets, and gain insights into your spending habits. Perfect for personal finance management on the go.
  </div>
</div>

## 📋 Table of Contents

1. 🤖 [Introduction](#introduction)
2. 🔋 [Features](#features)
3. ⚙ [Tech Stack](#techstack)
4. ❔ [Prerequisites](#prerequisites)
5.  ✒ [Steps](#steps)
6. 🚀 [Usage](#usage)


## 🤖 Introduction

 An intuitive and lightweight mobile application to track your daily expenses, set budgets, and gain insights into your spending habits. Perfect for personal finance management on the go.

## 🔋 Features

- 💸 Add, edit, and delete expenses with categories
- 📊 View expenses through interactive charts and summaries
- 🗓 Track weekly, monthly, and yearly spending
- 🎯 Set spending limits and receive alerts
- 🔐 Secure login and data protection

## 🛠 Tech Stack

- Frontend: Flutter 
- Backend : Crud py
- Database: Sql alchemy

## ❔ Prerequisites

- Dart
- Flutter SDK
- Android Studio

## ✒ Steps

1. *Clone the Repository*

   bash
    https://github.com/bhavye-thakkar/Expense-tracker.git

### Backend Setup
bash
## Install dependencies
pip install -r backend/requirements.txt

## Start the server
uvicorn backend.app.main:app --reload

## Access API documentation
open http://127.0.0.1:8000/docs


### Frontend Setup
bash
## enter the working directory
cd frontend

## Ensure Flutter is installed
flutter doctor

## Get dependencies
flutter pub get

## Run the application
flutter run -d chrome


## 🚀 Usage

1. *Launch the App*  
   Open the app on your mobile device or emulator after running it successfully.

2. *Sign Up / Log In*  
   Create an account or log in using your email and password. (Third-party logins optional if implemented.)

3. *Add Your First Expense*  
   Tap the "+" button or "Add Expense" to input details like:
   - Title/Description
   - Amount
   - Category (e.g., Food, Transport, Utilities)
   - Date

4. *View Summary and Charts*  
   Navigate to the dashboard to view:
   - /Weekly/Monthly/Yearly expenses
   - Pie charts showing category-wise distribution

6. *Manage Expenses*  
   - View or delete entries
