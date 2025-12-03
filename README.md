# CSCI331 Final Site

## Overview
This website was designed to show a proof of concept that an LLM can function as a viable customer service and salesperson
for an online shop. This site features a home page, catalog, FAQ, and a chatbot page which saves progress based off cookies.
The chatbot is powered using Groq's LLM API on Meta's Llama 4 Scout model. 

## Features
- Home Page
- Catalog Page
- FAQ Page
- Chatbot Page with Cookie-Based Progress Saving
- Clears sessions after 15 minutes of inactivity using threading
- Uses HTMX for dynamic content loading on the chatbot page
- Deployed on Heroku

## Setup
The project is designed to be deployed to Heroku or locally. To run the project locally, follow these steps:
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
4. Set the environment variable for the Groq API key
5. Set the environment variable for the Flask secret key
6. Run the Flask application:
   ```
   python app.py
   ```
7. Open the application at the URL given in the output (localhost by default).

To deploy to Heroku using the GUI:
1. Create a new Heroku application.
2. Connect your GitHub repository to the Heroku app.
3. Install the python buildpack.
4. Set the environment variables for the Groq API key and Flask secret key in the Heroku settings.
5. Deploy the application from the GitHub repository.
6. Open the application in your web browser.

## Group Members
- Davis Stryer
- Julia Larsen
