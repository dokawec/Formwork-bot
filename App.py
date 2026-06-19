from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import anthropic, os

app = Flask(__name__)

SYSTEM = """אתה מהנדס קבלנות מומחה בתחום מערכות התבניות.
DOKA: Framax Xlife plus, DokaXlight, Dokaflex, DokaXdek, SKE plus, Super Climber SCP, Concremote.
PERI: TRIO, MAXIMO, MULTIFLEX, SKYDECK, ACS, RCS, VARIOKIT.
ידע: EN 12812, בטון טרי 2500 kg/m³, עומסים 0.75-1.75 kN/m².
ענה בעברית מקצועית, קצר וממוקד לוואטסאפ."""

convos = {}
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body", "").strip()
    num = request.form.get("From", "")
    if num not in convos:
        convos[num] = []
    convos[num].append({"role": "user", "content": msg})
    if len(convos[num]) > 10:
        convos[num] = convos[num][-10:]
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=600, system=SYSTEM, messages=convos[num])
        reply = r.content[0].text
        convos[num].append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = "שגיאה: " + str(e)
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

@app.route("/")
def index():
    return "בוט פעיל ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
