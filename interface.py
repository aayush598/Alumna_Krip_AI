import gradio as gr
from counselor import DynamicCollegeCounselorChatbot

def create_chatbot_interface():
    """Create enhanced Gradio interface for the AI college counselor"""
    counselor = DynamicCollegeCounselorChatbot(name="Lauren")

    with gr.Blocks(title="Lauren - Dynamic AI College Counselor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎓 Lauren - Your Dynamic AI College Counselor")
        gr.Markdown("""
        Welcome! I'm Lauren, your AI college counselor. I use advanced conversation analysis to understand your needs and provide personalized recommendations.
        Just chat naturally about your academic background, goals, and preferences - I'll automatically extract and organize the relevant information!
        """)

        chatbot = gr.Chatbot(height=600, show_copy_button=True, type="messages")

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Hi Lauren! I'm looking for college guidance. I scored 85% in 12th grade...",
                container=False,
                scale=7
            )
            submit = gr.Button("Send", variant="primary", scale=1)

        with gr.Row():
            clear = gr.Button("New Session", scale=1)
            download_btn = gr.Button("📄 Download Profile", variant="secondary", scale=1)

        download_file = gr.File(label="Your Profile", visible=False)
        status_display = gr.Markdown("🤖 **Status:** Ready to chat! I'll dynamically extract information as we talk.")

        initial_greeting = {
            "role": "assistant",
            "content": """
            👋 Hi there! I'm Lauren, your AI college counselor.
            I'm here to help you find the perfect colleges based on your unique profile and goals. What makes me special is that I can understand and organize information from natural conversation - you don't need to fill out forms!
            Just tell me about yourself, your academic background, what you're interested in studying, or any concerns you have about college selection. I'll automatically pick up on the important details and help guide you toward great options.
            What would you like to share about your educational journey? 😊
            """
        }

        def respond(message, chat_history):
            if not message.strip():
                return chat_history, gr.update(), gr.update(visible=False)

            response = counselor.chat(message, chat_history)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})

            status_text = "📊 **Status:** Collecting information..."
            if counselor.sufficient_info_collected:
                status_text = "✅ **Status:** Ready with recommendations! You can download your profile."

            return chat_history, gr.update(value=status_text), gr.update(visible=counselor.sufficient_info_collected)

        def download_profile():
            return gr.update(value=str(counselor.profile_filename), visible=True)

        def new_session():
            counselor.__init__()  # reset counselor
            return [], gr.update(visible=False), gr.update(value="🤖 **Status:** Ready to chat! I'll dynamically extract information as we talk.")

        # Event handlers
        submit.click(respond, [msg, chatbot], [chatbot, status_display, download_btn])
        clear.click(new_session, outputs=[chatbot, download_file, status_display])
        download_btn.click(download_profile, outputs=[download_file])

        # Set initial message
        chatbot.value = [initial_greeting]

    return app
