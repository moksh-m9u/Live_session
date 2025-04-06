import gradio as gr
import os
from Backend.Chatbot import ChatBot
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TTS
import asyncio

# Initialize chat history and mic status
chat_history = []
mic_enabled = True

def toggle_mic():
    global mic_enabled
    mic_enabled = not mic_enabled
    return f"Mic {'Enabled' if mic_enabled else 'Muted'}"

def process_input(audio_input):
    global chat_history, mic_enabled
    
    if not mic_enabled:
        return "Mic is muted. Please unmute to speak.", None, format_chat_history(chat_history), None
    
    if not audio_input:
        return "Please speak your symptoms.", None, format_chat_history(chat_history), None
    
    # Save the audio input to Data folder
    audio_path = os.path.join("Data", "patient_voice_test.mp3")
    with open(audio_path, "wb") as f:
        with open(audio_input, "rb") as audio_file:
            f.write(audio_file.read())
    
    # Convert speech to text
    query = SpeechRecognition(audio_path)
    if "Sorry" in query or "Error" in query:
        return query, None, format_chat_history(chat_history), None
    
    # Get DocBot's response
    response = ChatBot(query)
    
    # Generate voice output
    asyncio.run(TTS(response))
    audio_output = "Data/speech.mp3"
    
    # Update chat history
    chat_history.append(("You", query))
    chat_history.append(("DocBot", response))
    
    # Format chat history for display
    chat_display = format_chat_history(chat_history)
    
    # Return latest response, audio, and updated chat history
    return response, audio_output, chat_display, None

def format_chat_history(history):
    """Format chat history into a neat string."""
    return "\n".join([f"{role}: {msg}" for role, msg in history])

with gr.Blocks(title="DocBot - AI Doctor") as demo:
    gr.Markdown("# DocBot - Your AI Doctor")
    
    # Conversation History (Top)
    chat_display = gr.Textbox(label="Conversation History", lines=10, interactive=False)
    
    # DocBot's Response (Middle)
    with gr.Row():
        text_output = gr.Textbox(label="DocBot's Response", interactive=False)
        audio_output = gr.Audio(label="Listen to DocBot", interactive=False)
    
    # Mic Controls (Bottom)
    with gr.Row():
        mic_toggle = gr.Button("Mic Enabled", variant="primary")
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Speak your symptoms")
    
    # Link toggle and audio input
    mic_toggle.click(toggle_mic, inputs=None, outputs=mic_toggle)
    audio_input.change(
        fn=process_input,
        inputs=[audio_input],
        outputs=[text_output, audio_output, chat_display, audio_input]
    )

# Launch with queue for smoother interaction
demo.queue().launch(share=True)