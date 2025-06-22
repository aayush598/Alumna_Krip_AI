# Alumna_Krip_AI

# Dynamic AI College Counselor Chatbot
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
## Overview

This project implements a dynamic AI college counselor chatbot designed to interact with students, extract relevant information from conversations, and provide personalized college recommendations. The chatbot uses natural language processing to understand and organize information from natural conversation, making it easy for students to get guidance without filling out forms.

## Features

- **Natural Language Interaction**: Chat naturally about your academic background, goals, and preferences.
- **Dynamic Information Extraction**: The chatbot automatically extracts and organizes relevant information from conversations.
- **Personalized Recommendations**: Get tailored college recommendations based on your unique profile.
- **Comprehensive College Database**: The chatbot uses a detailed database of colleges to match student profiles with suitable options.
- **User-Friendly Interface**: Built with Gradio for an intuitive and interactive experience.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
## Installation

1. Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
2.Set Up Environment Variables:

- **Create a .env file in the root directory**.
- **Add your Groq API key to the .env file**:
   ```sh
   GROQ_API_KEY=your_api_key_here
3.Install Dependencies:

      > pip install -r requirements.txt
   
4.Run the Application:

    > python app.py
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
Usage

> Start the Chatbot:
> Launch the application using the command above.
> Open the provided URL in your web browser to access the chatbot interface.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Interact with the Chatbot:

Begin by greeting the chatbot and sharing information about your academic background, goals, and preferences.
The chatbot will dynamically extract relevant information and guide the conversation toward providing personalized college recommendations.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Download Your Profile:

Once sufficient information has been collected, you can download your profile by clicking the "Download Profile" button.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Code Structure
> DynamicStudentProfile Class: Defines the model for storing student information.
> DynamicCollegeCounselorChatbot Class: Core class for the chatbot, handling information extraction, sufficiency assessment, and recommendation generation.
> Gradio Interface: Sets up the user interface for interacting with the chatbot.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Dependencies

> Python 3.7+

> Gradio

> Groq

> Pydantic

> dotenv
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
License

This project is licensed under the MIT License.



