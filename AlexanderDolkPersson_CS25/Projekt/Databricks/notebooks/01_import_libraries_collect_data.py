# ============================================================
# STEG 1 – Importera bibliotek och hämta data
# ============================================================

# Importerar MLflow (används senare för att logga modeller och resultat osv...)
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

# Importerar pandas, hanterar/skapar tabeller
import pandas as pd

# Importerar numpy för numeriska beräkningar :)
import numpy as np

# Importerar funktionen som delar upp datan i träning och test
from sklearn.model_selection import train_test_split

# Importerar Random Forest (supervised modell) Innebär att den kommer tränas med labels 
from sklearn.ensemble import RandomForestClassifier

# Importerar Isolation Forest (unsupervised modell) Innebär att den kommer tränas utan labels
from sklearn.ensemble import IsolationForest

# Importerar LabelEncoder för att omvandla text till siffror
from sklearn.preprocessing import LabelEncoder

# Importerar utvärderingsmått
from sklearn.metrics import classification_report, roc_auc_score

# Skriver ut MLflow-version (endast för att se om jag har en gammal version) // felsökning // 1 timme slösades här :)
print("MLflow version:", mlflow.__version__)


# ----- Hämta data från Snowflake -----

# Läser in din feature-tabell från Snowflake via Databricks 
# OBS namnet namnet är inte samma som i Snowflake, det var kul att upptäcka!
df = spark.table("snowflakev1_catalog.dbt_aleanderdp.FEATURE_MODEL").toPandas()

# Visar hur många rader och kolumner datan har
print("Shape:", df.shape)

# Visar alla kolumnnamn
print("\nKolumner:")
print(df.columns.tolist())

# Visar hur stor andel som är malicious (1) vs benign (0) True/False
print("\nKlassfördelning:")
print(df['IS_MALICIOUS'].value_counts(normalize=True).round(4))

# Visar de första 5 raderna, endast för kontroll av data och hur den ser ut
df.head()