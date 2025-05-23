from . import __version__ as app_version

app_name = "ecopan_bot"
app_title = "ecopanBot"
app_publisher = "Techloop"
app_description = "ChatGPT in the Desk, powered by React, LangChain & OpenAI API"
app_email = "Techloop"
app_license = "AGPL-3.0"

# web_include_js = ["/assets/ecopan_bot/js/ecopanbot_public.bundle.js"]

# Configurazione delle route del sito web
website_route_rules = [
    {"from_route": "/chatbot", "to_route": "chatbot"},
]

# Permessi per le pagine web
website_redirects = [
    {"source": "/chat", "target": "/chatbot"},
]
