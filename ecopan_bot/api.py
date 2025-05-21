import frappe
import redis
import json
from openai import OpenAI
from datetime import datetime

# System message to define the chatbot's behavior and personality
SYSTEM_MESSAGE = """You are ecopanBot, an AI assistant whose birth date is April 16, 2025. 
You are talkative and provide lots of specific details from your context.
If you do not know the answer to a question, truthfully say you do not know.
Any programming code should be output in a github flavored markdown code block mentioning the programming language."""

class RedisChatStore:
    """Handles storing and retrieving chat messages from Redis"""
    
    def __init__(self, session_id, redis_url=None):
        self.session_id = session_id
        self.redis_url = redis_url or frappe.conf.get("redis_cache") or "redis://localhost:6379/0"
        self.redis_client = redis.from_url(self.redis_url)
        self.messages_key = f"ecopan_chat:{session_id}"
    
    def get_messages(self):
        """Retrieve all messages for this session"""
        messages_json = self.redis_client.get(self.messages_key)
        if messages_json:
            return json.loads(messages_json)
        else:
            # Initialize with system message
            initial_messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
            self.save_messages(initial_messages)
            return initial_messages
    
    def save_messages(self, messages):
        """Save the full message history"""
        self.redis_client.set(self.messages_key, json.dumps(messages))
    
    def add_message(self, role, content):
        """Add a new message to the history"""
        messages = self.get_messages()
        messages.append({"role": role, "content": content})
        self.save_messages(messages)

@frappe.whitelist()
def get_chatbot_response(session_id: str, prompt_message: str) -> str:
    """Process a user message and get a response from the chatbot"""
    # Throw if no key in site_config
    openai_api_key = frappe.conf.get("openai_api_key")
    if not openai_api_key:
        frappe.throw("Please set `openai_api_key` in site config")
    
    # Get model from settings
    openai_model = get_model_from_settings()
    
    # Initialize the chat store for this session
    chat_store = RedisChatStore(session_id)
    
    # Add the user message to the history
    chat_store.add_message("user", prompt_message)
    
    # Get all messages for context
    messages = chat_store.get_messages()
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Call the API
    response = client.chat.completions.create(
        model=openai_model,
        messages=messages,
        temperature=0,
    )
    
    # Extract the assistant's message
    assistant_message = response.choices[0].message.content
    
    # Save the assistant's response
    chat_store.add_message("assistant", assistant_message)
    
    return assistant_message

def get_model_from_settings():
    """Get the configured OpenAI model from settings"""
    return (
        frappe.db.get_single_value("ecopanBot Settings", "openai_model") 
        or "gpt-4o-mini"  # Updated default model to a more modern one
    )