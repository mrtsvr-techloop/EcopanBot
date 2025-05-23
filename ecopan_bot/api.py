import frappe
import openai
import redis
import json
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest=True)
def serve_chatbot_js():
    """Serve un'implementazione JavaScript del chatbot pronta all'uso"""
    
    js_content = """
    (function() {
        window.ecopanbot = window.ecopanbot || {};
        window.ecopanbot.public = window.ecopanbot.public || {};
        
        // Implementazione di una classe PublicChatUI che funziona nel browser
        window.ecopanbot.public.PublicChatUI = class PublicChatUI {
            constructor(opts) {
                this.wrapper = opts.wrapper;
                this.messages = [];
                this.sessionId = this.generateSessionId();
                this.init();
            }
            
            generateSessionId() {
                return 'session_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            }
            
            init() {
                this.wrapper.innerHTML = `
                    <div class="chat-container" style="height: 100%; display: flex; flex-direction: column;">
                        <div class="chat-header" style="padding: 15px; background: #4CAF50; color: white; font-weight: bold; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                            <div>ecopanBot - Assistente Virtuale</div>
                        </div>
                        <div class="chat-messages" style="flex: 1; overflow-y: auto; padding: 15px; background: #f9f9f9;"></div>
                        <div class="chat-input" style="padding: 10px; border-top: 1px solid #ddd; display: flex; background: #fff;">
                            <input type="text" class="form-control" placeholder="Scrivi un messaggio..." style="flex: 1; margin-right: 10px;">
                            <button class="btn btn-primary">Invia</button>
                        </div>
                    </div>
                `;
                
                this.messagesContainer = this.wrapper.querySelector('.chat-messages');
                this.inputField = this.wrapper.querySelector('input');
                this.sendButton = this.wrapper.querySelector('button');
                
                this.sendButton.addEventListener('click', () => this.sendMessage());
                this.inputField.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.sendMessage();
                });
                
                // Messaggio di benvenuto
                this.addMessage("Ciao! Sono ecopanBot, il tuo assistente virtuale. Come posso aiutarti oggi?", false);
            }
            
            addMessage(text, isUser) {
                // Crea l'elemento del messaggio
                const messageEl = document.createElement('div');
                messageEl.className = isUser ? 'user-message' : 'bot-message';
                messageEl.style.padding = '10px 15px';
                messageEl.style.borderRadius = '10px';
                messageEl.style.marginBottom = '10px';
                messageEl.style.maxWidth = '80%';
                messageEl.style.wordBreak = 'break-word';
                
                if (isUser) {
                    messageEl.style.backgroundColor = '#dcf8c6';
                    messageEl.style.marginLeft = 'auto';
                    messageEl.style.color = '#000';
                } else {
                    messageEl.style.backgroundColor = 'white';
                    messageEl.style.marginRight = 'auto';
                    messageEl.style.color = '#000';
                    messageEl.style.boxShadow = '0 1px 2px rgba(0,0,0,0.1)';
                }
                
                // Supporto per formattazione con markdown minimale (grassetto, corsivo, link)
                let formattedText = text
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')  // **grassetto**
                    .replace(/\\*(.*?)\\*/g, '<em>$1</em>')              // *corsivo*
                    .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank">$1</a>');  // [link](url)
                
                messageEl.innerHTML = formattedText;
                this.messagesContainer.appendChild(messageEl);
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
                
                // Aggiungi il messaggio all'array dei messaggi
                this.messages.push({
                    text: text,
                    isUser: isUser,
                    timestamp: new Date().toISOString()
                });
            }
            
            sendMessage() {
                const message = this.inputField.value.trim();
                if (!message) return;
                
                // Aggiungi il messaggio dell'utente alla chat
                this.addMessage(message, true);
                this.inputField.value = '';
                
                // Mostra un indicatore di caricamento
                const loadingEl = document.createElement('div');
                loadingEl.className = 'bot-message loading';
                loadingEl.style.padding = '10px 15px';
                loadingEl.style.borderRadius = '10px';
                loadingEl.style.marginBottom = '10px';
                loadingEl.style.backgroundColor = 'white';
                loadingEl.style.marginRight = 'auto';
                loadingEl.style.color = '#888';
                loadingEl.innerHTML = '<em>ecopanBot sta scrivendo...</em>';
                this.messagesContainer.appendChild(loadingEl);
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
                
                // Chiamata API per ottenere la risposta
                frappe.call({
                    method: 'ecopan_bot.api.get_chatbot_response',
                    args: { 
                        session_id: this.sessionId,
                        prompt_message: message 
                    },
                    callback: (response) => {
                        // Rimuovi l'indicatore di caricamento
                        if (loadingEl.parentNode) {
                            loadingEl.parentNode.removeChild(loadingEl);
                        }
                        
                        if (response.message) {
                            // Aggiungi la risposta del bot alla chat
                            this.addMessage(response.message, false);
                        } else {
                            this.addMessage("Mi dispiace, si è verificato un errore. Riprova più tardi.", false);
                        }
                    },
                    error: () => {
                        // Rimuovi l'indicatore di caricamento
                        if (loadingEl.parentNode) {
                            loadingEl.parentNode.removeChild(loadingEl);
                        }
                        
                        this.addMessage("Mi dispiace, si è verificato un errore. Riprova più tardi.", false);
                    }
                });
            }
        };
    })();
    """
    
    response = Response(js_content)
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache per 1 ora
    return response


@frappe.whitelist(allow_guest=True)
def get_chatbot_response(session_id: str, prompt_message: str) -> str:
    # Recupera la chiave API di OpenAI dal file di configurazione del sito
    openai_api_key = frappe.conf.get("openai_api_key")
    if not openai_api_key:
        frappe.throw("Imposta 'openai_api_key' nel file di configurazione del sito.")

    # Recupera il modello dalle impostazioni personalizzate, con un valore predefinito
    openai_model = frappe.db.get_single_value("ecopanBot Settings", "openai_model") or "gpt-3.5-turbo"

    # Configura la chiave API di OpenAI
    openai.api_key = openai_api_key

    # Connessione a Redis per la gestione della cronologia della chat
    redis_url = frappe.conf.get("redis_cache") or "redis://localhost:6379/0"
    r = redis.from_url(redis_url)

    # Chiave per la sessione corrente
    redis_key = f"chat_history:{session_id}"

    # Recupera la cronologia dei messaggi dalla sessione corrente
    history_json = r.get(redis_key)
    if history_json:
        messages = json.loads(history_json)
    else:
        # Messaggio di sistema iniziale
        messages = [
            {
                "role": "system",
                "content": (
                    "La seguente è una conversazione amichevole tra un umano e un'IA. "
                    "L'IA è loquace e fornisce molti dettagli specifici dal suo contesto. "
                    "Il nome dell'IA è ecopanbot e la sua data di nascita è il 24 aprile 2023. "
                    "Se l'IA non conosce la risposta a una domanda, lo dice sinceramente."
                )
            }
        ]

    # Aggiunge il nuovo messaggio dell'utente
    messages.append({"role": "user", "content": prompt_message})

    try:
        # Richiesta all'API di OpenAI
        response = openai.chat.completions.create(
            model=openai_model,
            messages=messages,
            temperature=0.7,
        )

        # Estrae la risposta dell'assistente
        assistant_message = response.choices[0].message.content

        # Aggiunge la risposta dell'assistente alla cronologia
        messages.append({"role": "assistant", "content": assistant_message})

        # Salva la cronologia aggiornata in Redis
        r.set(redis_key, json.dumps(messages))

        return assistant_message

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Errore nell'API di OpenAI")
        frappe.throw("Si è verificato un errore durante la generazione della risposta.")

        