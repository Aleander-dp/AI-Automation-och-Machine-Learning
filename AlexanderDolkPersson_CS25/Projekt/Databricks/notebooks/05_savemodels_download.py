# ============================================================
# STEG 5 – Spara modeller + skapa nedladdningsknappar
# ============================================================

import joblib
import os
import base64
from IPython.display import HTML, display

# Spara modellerna i /tmp
os.makedirs("/tmp/models", exist_ok=True)

joblib.dump(rf, "/tmp/models/random_forest_model.pkl")
joblib.dump(iso, "/tmp/models/isolation_forest_model.pkl")
joblib.dump(le_dict, "/tmp/models/label_encoders.pkl")

print("Modellerna är sparade.\n")

def create_download_link(file_path, file_name):
    """Skapar en nedladdningslänk/knapp för en fil"""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    
    # Gör en HTML-kod som innehåller en nedladdningsknapp för lättare nerladdning
    html = f'''
    <a download="{file_name}" 
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
       ⬇ Ladda ner {file_name}
    </a>
    '''
    return HTML(html)

# Visa knapparna (label_encoders är inte modell, kan användas av andra användare om de vill träna modellerna ytterligare)
display(create_download_link("/tmp/models/random_forest_model.pkl", "random_forest_model.pkl"))
display(create_download_link("/tmp/models/isolation_forest_model.pkl", "isolation_forest_model.pkl"))
display(create_download_link("/tmp/models/label_encoders.pkl", "label_encoders.pkl"))