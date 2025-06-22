from interface import create_chatbot_interface

if __name__ == "__main__":
    app = create_chatbot_interface()
    app.launch(server_name="0.0.0.0", server_port=8000)
