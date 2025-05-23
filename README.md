# Intelligent Pizza Ordering Platform - Backend

## Overview

This repository contains the backend server for the Intelligent Pizza Ordering Platform. It is built using Python with the Django framework and serves a REST API consumed by the React frontend. The backend handles all business logic, database interactions, user authentication, order processing, and the AI-powered pizza recommendation engine.

**Technology Stack:**
* Python
* Django
* Django REST Framework (Assumed for API)
* Content-Based Filtering (for AI recommendations)
* SQLite

## Features

* **REST API:** Exposes endpoints for frontend interaction.
* **Database Management:** Manages models and data for users, menu items (pizzas, ingredients, prices), orders, user preferences, and delivery information using Django ORM.
* **User Authentication:** Handles user registration, login, and session management.
* **Order Processing:** Manages the creation, updating, and tracking of pizza orders.
* **Menu Logic:** Calculates dynamic pricing, handles dietary information, and serves menu data.
* **Discount Logic:** Implements rules for automatic discounts and coupon codes.
* **AI Recommendation Engine:** Provides personalized pizza recommendations using a content-based filtering approach based on user history and preferences. Includes logic for the "Quick Ordering" feature.
* **Delivery Management:** Basic logic for tracking order status and assigning deliveries.
* **Restaurant Interface Logic:** Provides data endpoints for the staff view (e.g., pending orders, earnings reports).

## AI Component

The recommendation engine uses content-based filtering. It represents pizzas and user preferences in a common feature space (based on ingredients) and calculates similarity (e.g., cosine similarity) to generate suggestions for the quick ordering feature. User preferences are updated based on order history and reviews.

### How to Run the Application:

Backend (Django):
After cloning the repository, open the pizza-delivery-backend folder in your preferred code environment.
Ensure you have Python installed and all required libraries by running.
Start the server by running this command in the terminal:
python manage.py runserver
Leave the terminal window open as the backend must keep running.

Frontend (React):
After cloning the repository, open the pizza-delivery-frontend folder in a code environment.
Ensure you have Node.js installed. If not, download it here: Node.js.
In the terminal, run the command:
npm run dev
Follow the link provided in the terminal to access the app in your browser.

Explore the App:
Take some time to explore all the functionalities of the app. Once you’ve tried both the classic and quick ordering methods, and completed the tasks above, please close the app and answer the following questions.

GitHub Links:
Backend Repository: https://github.com/Mihai-Solescu/pizza-delivery-backend
Frontend Repository: https://github.com/Mihai-Solescu/pizza-delivery-frontend

Create an Account:
Go to the registration page and create an account.
Please use the format firstname_lastname as your username and firstname_lastname@gmail.com as your email to ensure your account details are unique.
You can fill out the other fields however you like.

Set Your Preferences:
After registering, fill out your pizza preferences to help tailor your experience.

Order Pizzas (Classic Method):
Explore the normal ordering menu and place your pizza order. Maybe rate some pizzas as well. Used in updating preferences.

Log In Again:
Log out, then access the login page and log back in using your account.
Try Quick Ordering:

Navigate to the quick ordering section and follow the tasks below.

There exists a ready-made account with admin privileges in the database with credentials:
username: mihai
password: 1234


### Non-AI version task instructions:
Login:
Log into your account using the credentials you created.
Access the Quick Order Page:

Navigate to the Quick Order section of the app.

Go through Quick Ordering (for non-AI version):
Make sure the top-left corner circle is green. If it's not, click it to switch to the non-AI version.
Press the pizza button.
Answer the questionnaire to generate your pizza order.

Confirm Your Order:
After selecting your pizza (in either version), confirm your order to complete the task.



### AI version task instructions:
Pre-requirements:
User has submitted the initial preferences questionnaire.

Login:
Log into your account using the credentials you created.

Access the Quick Order Page:
Navigate to the Quick Order section of the app.

Go through Quick Ordering (for the AI Version):
(Assuming user has already set preferences, else do so
Make sure the top-left corner circle is blue. If it's not, click it to switch to the AI version.
Pick your preferred pizza order from the options provided

Confirm Your Order:
After selecting your pizza (in either version), confirm your order to complete the task.
