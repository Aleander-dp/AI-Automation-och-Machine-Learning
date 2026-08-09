# ============================================================
# STEG 6 – Skapa Slack-rapport + komplett Python-fil
# ============================================================

# Pga att min dashboard/workspace/notebook inte har åtkomst till internet och inte kan använda sig av webhooks eller API-calls, har jag valt att skapa en lokal lösning. Denna lösning består av att denna cell skapar ett Python script som skickar rapporten till Slack med en Webhook och använder sig av en GROK API sammanställa all info om medellerna och deras prestanda i text format. Därefter görs ett till API-call som summerar all info från GROK tidigare sammanställning av modellerna. Båda dessa AI-summeringarna skickas vidare till Slack.

import json
import base64
from IPython.display import HTML, display

print("Skapar Slack-rapport och komplett Python-fil...")

# Bygg Slack-rapporten från modeller

top_features = importance.head(10)
feature_text = "\n".join(
    f"• {feature}: {value:.4f}"
    for feature, value in top_features.items()
)

# Allt innehåll till slack rapporten
slack_text = (
    "*CTU IoT Malware – Modellrapport*\n\n"
    "*Random Forest – Supervised*\n"
    f"• Accuracy: {report['accuracy']:.2%}\n"
    f"• Precision (malicious): {report['1']['precision']:.2%}\n"
    f"• Recall (malicious): {report['1']['recall']:.2%}\n"
    f"• F1-score (malicious): {report['1']['f1-score']:.2%}\n"
    f"• ROC-AUC: {auc:.4f}\n\n"
    "*Isolation Forest – Unsupervised*\n"
    f"• Accuracy: {report_iso['accuracy']:.2%}\n"
    f"• Precision (malicious): {report_iso['1']['precision']:.2%}\n"
    f"• Recall (malicious): {report_iso['1']['recall']:.2%}\n"
    f"• F1-score (malicious): {report_iso['1']['f1-score']:.2%}\n\n"
    "*Top 10 viktigaste features – Random Forest*\n"
    f"{feature_text}\n\n"
    "*MLflow*\n"
    "Random Forest och Isolation Forest har tränats "
    "och loggats till MLflow.\n\n"
    "Rapport genererad automatiskt."
)

report_obj = {"slack_text": slack_text}

# Spara Slack-rapporten som JSON

json_path = "/tmp/slack_report.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(report_obj, f, ensure_ascii=False, indent=2)

# Print för syns skull
print("✔ Slack-rapport sparad i /tmp/slack_report.json")


# 3. Skapa komplett Python-fil som körs lokalt

python_script = r'''
import json
import requests
import socket
from getpass import getpass

# ============================================================
# DNS-check (lokalt)
# ============================================================

def check_dns(host="hooks.slack.com"):
    try:
        socket.gethostbyname(host)
        return True
    except Exception as e:
        print(f" DNS-fel: {e}")
        return False

# ============================================================
# Läs ML-rapporten
# ============================================================

with open("slack_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

slack_text = data["slack_text"]

# ============================================================
# Hämta API-nycklar
# ============================================================

webhook_url = getpass("Klistra in din Slack Webhook URL: ")
grok_api_key = getpass("Klistra in din GROK API-nyckel: ")

print("\n Kör DNS-test...")
if not check_dns():
    print(" DNS fungerar inte. Avslutar.")
    exit(1)

print("✔ DNS OK\n")

# ============================================================
# Skicka rapporten till Grok API (första sammanfattningen)
# ============================================================

print("🤖 Skickar rapporten till Grok AI...")

grok_url = "https://api.x.ai/v1/chat/completions"

prompt = f"""
Sammanfatta följande ML-resultat och jämför Random Forest och Isolation Forest.
Beskriv styrkor, svagheter och vilken modell som är mest lämplig för IoT-malware-detektering.

Rapport:
{slack_text}
"""

payload = {
    "model": "grok-4.5",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {grok_api_key}"
}

grok_response = requests.post(grok_url, json=payload, headers=headers)

if grok_response.status_code != 200:
    print(" Grok API-fel:", grok_response.text)
    exit(1)

summary = grok_response.json()["choices"][0]["message"]["content"]

print("\n Grok sammanfattning:\n")
print(summary)

# ============================================================
# Grok sammanfattar sin egen sammanfattning (meta-summary)
# ============================================================

print("\n Skickar sammanfattningen till Grok igen för meta-summary...")

meta_prompt = f"""
Sammanfatta följande text extremt kortfattat.
Fokusera på:
- huvudpoängen
- modelljämförelsen
- slutsatsen
- rekommendationen

Text:
{summary}
"""

meta_payload = {
    "model": "grok-4.5",
    "messages": [
        {"role": "user", "content": meta_prompt}
    ]
}

meta_response = requests.post(grok_url, json=meta_payload, headers=headers)

if meta_response.status_code != 200:
    print(" Grok API-fel (meta-summary):", meta_response.text)
    exit(1)

meta_summary = meta_response.json()["choices"][0]["message"]["content"]

print("\n Grok meta-summary:\n")
print(meta_summary)


# Skicka originalrapporten till Slack


print("\n📤 Skickar originalrapporten till Slack...")

original_message = {
    "text": f"*CTU IoT Malware – Modellrapport*\n\n{slack_text}"
}

response = requests.post(webhook_url, json=original_message)

if response.status_code == 200:
    print("✔ Originalrapport skickad!")
else:
    print("❌ Slack-fel:", response.text)


# Skicka AI-sammanfattningen till Slack


print("\n📤 Skickar AI-sammanfattningen till Slack...")

summary_message = {
    "text": f"*AI-sammanfattning av ML-resultat*\n\n{summary}"
}

response = requests.post(webhook_url, json=summary_message)

if response.status_code == 200:
    print("✔ AI-sammanfattning skickad!")
else:
    print("❌ Slack-fel:", response.text)


# Skicka meta-summary till Slack (sammanfattning nummer två)


print("\n Skickar meta-summary till Slack...")

meta_message = {
    "text": f"*AI Meta-Summary (Grok på Grok)*\n\n{meta_summary}"
}

response = requests.post(webhook_url, json=meta_message)

if response.status_code == 200:
    print(" Meta-summary skickad!")
else:
    print(" Slack-fel:", response.text)

print("\n Klart! Alla tre rapporterna är skickade till Slack.")
'''

py_path = "/tmp/send_full_report.py"
with open(py_path, "w", encoding="utf-8") as f:
    f.write(python_script)

print("✔ Python-fil sparad i /tmp/send_full_report.py")



# 4. Skapa nedladdningsknappar


def create_download_button(path, filename):
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    html = f'''
    <a download="{filename}"
       href="data:application/octet-stream;base64,{b64}"
       style="
           display:inline-block;
           padding:10px 18px;
           margin:6px 0;
           background-color:#0d6efd;
           color:white;
           text-decoration:none;
           border-radius:6px;
           font-weight:bold;
           font-family:sans-serif;
       ">
       ⬇ Ladda ner {filename}
    </a>
    '''
    return HTML(html)

display(create_download_button(json_path, "slack_report.json"))
display(create_download_button(py_path, "send_full_report.py"))

print(" Klart! Ladda ner filerna och kör send_full_report.py lokalt.")
