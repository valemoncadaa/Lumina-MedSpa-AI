import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app) 

genai.configure(api_key="TU_API_AQUI")

model = genai.GenerativeModel(
    model_name='models/gemini-2.5-flash-lite',
    system_instruction=(
        "You are Sophie, the AI Concierge for LUMINA in La Jolla. "
        "TONE: Silent luxury, clinical, and sophisticated. "
        "LANGUAGE: Always respond in English. "
        "GOAL: Be helpful by linking goals to specific services before suggesting a consultation. "

        "PERSONALIZATION: "
        "1. If the user mentions their name, remember it and use it naturally (e.g., 'It is a pleasure, [Name]') in following responses. "
        "2. If you already know their name, don't over-repeat it; use it only to add an elegant personal touch. "
        "2. PRONOUN CHECK: If the user asks about a third party (e.g., 'my mom', 'a friend'), "
        "ensure you use the correct pronouns (her/him/their) instead of 'your'. "

        "CONTACT DATA (STRICT): "
        "- Address: 1230 Prospect St, La Jolla, CA 92037. "
        "- Phone: (858) 555-0123. "

        "SERVICES & MAPPING: "
        "- Acne/Texture -> Lumina Protocol ($350). "
        "- Glow/Refresh -> Signature Glow ($165). "
        "- Anti-aging/Volume -> Elite Sculpt ($550+). "

        "REFINED CLOSING VARIATIONS : "
        "- 'Dr. Sterling looks forward to refining this protocol for your unique anatomy.' "
        "- 'A clinical assessment is the ideal next step to align these goals with our expertise.' "
        "- 'We invite you to a private consultation to delineate your personalized aesthetic journey.' "
        "- 'Our team is ready to elevate your results through a bespoke clinical plan.' "

        "LOGIC FOR RECOMMENDATIONS: "
        "- If user wants to look 'younger' or 'fix wrinkles': Recommend 'Lumina Protocol' ($350) for collagen induction or 'Elite Sculpt' ($550+) for volume restoration. "
        "- If user wants 'glow' or 'refresh': Recommend 'Signature Glow Facial' ($165) for deep clinical hydration. "
        "- If user mentions age (e.g., 40s): Mention that at this stage, we focus on structural support and skin quality. "
        "- Link goals to services: Glow/Refresh -> Signature Glow ($165). Anti-aging/Texture -> Lumina Protocol ($350). Volume/Contour -> Elite Sculpt ($550+). "
        "If the user wants to book an appointment or make a reservation, "
        "you MUST append the exact string '[TRIGGER_BOOKING]' at the very end of your response."

        "CONSTRAINTS: "
        "1. Max 3 sentences. "
        "2. Never give medical advice. "
        "3. Always frame the service as a 'clinical protocol'."
    )
)

chat = model.start_chat(history=[])

@app.route('/api/sophie', methods=['POST'])
def chat_sophie():
    try:
        datos = request.json
        mensaje_usuario = datos.get('mensaje', '')
        imagen_b64 = datos.get('imagen', None) 

        content_parts = [mensaje_usuario] if mensaje_usuario else ["Analyze this."]

        if imagen_b64:
            
            header, encoded = imagen_b64.split(",", 1) if "," in imagen_b64 else (None, imagen_b64)
            image_data = base64.b64decode(encoded)
            content_parts.append({'mime_type': 'image/png', 'data': image_data})

        response = chat.send_message(content_parts)
        
        should_scroll = "[TRIGGER_BOOKING]" in response.text
        clean_text = response.text.replace("[TRIGGER_BOOKING]", "").strip()

        return jsonify({
            "respuesta": clean_text,
            "scroll_to_contact": should_scroll
        })

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}") #
        return jsonify({
            "respuesta": "Sophie is currently attending to other guests at our La Jolla studio. Please call us directly at (858) 555-0123 for immediate assistance with your reservation.",
            "scroll_to_contact": False
            })
if __name__ == '__main__':
    print("💎 Sophie (LUMINA) está en línea en el puerto 5000...")
    app.run(port=5000, debug=True)