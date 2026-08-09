# ============================================================
# DASHBOARD-CELL – KPI, Modelljämförelse, Feature Importance,
# ROC-kurva, Confusion Matrix
# ============================================================

# Används främst för att visa information på dashboarden här i Databricks

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc, confusion_matrix

print(" Bygger Enterprise-dashboard...")

# ------------------------------------------------------------
# 1. KPI-tabell
# ------------------------------------------------------------
kpi = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1-score"],
    "Random Forest": [
        report["accuracy"],
        report["1"]["precision"],
        report["1"]["recall"],
        report["1"]["f1-score"]
    ],
    "Isolation Forest": [
        report_iso["accuracy"],
        report_iso["1"]["precision"],
        report_iso["1"]["recall"],
        report_iso["1"]["f1-score"]
    ]
})

print("✅ KPI-tabell:")
display(kpi)

# ------------------------------------------------------------
# 2. Modelljämförelse – linjegraf
# ------------------------------------------------------------
rf_scores = [
    report["accuracy"],
    report["1"]["precision"],
    report["1"]["recall"],
    report["1"]["f1-score"]
]

iso_scores = [
    report_iso["accuracy"],
    report_iso["1"]["precision"],
    report_iso["1"]["recall"],
    report_iso["1"]["f1-score"]
]

metrics = ["Accuracy", "Precision", "Recall", "F1-score"]

plt.figure(figsize=(10, 6))
plt.plot(metrics, rf_scores, marker="o", label="Random Forest")
plt.plot(metrics, iso_scores, marker="o", label="Isolation Forest")
plt.title("Modelljämförelse – Random Forest vs Isolation Forest")
plt.ylabel("Score")
plt.grid(True)
plt.legend()
plt.show()

# ------------------------------------------------------------
# 3. Feature Importance – topp 10
# ------------------------------------------------------------
fi = pd.DataFrame({
    "Feature": importance.index,
    "Importance": importance.values
}).sort_values("Importance", ascending=False).head(10)

plt.figure(figsize=(10, 6))
plt.barh(fi["Feature"], fi["Importance"])
plt.title("Top 10 Feature Importance – Random Forest")
plt.xlabel("Importance")
plt.gca().invert_yaxis()
plt.show()

# ------------------------------------------------------------
# 4. ROC-kurva – Random Forest
# ------------------------------------------------------------
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
plt.plot([0, 1], [0, 1], "k--")
plt.title("ROC Curve – Random Forest")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
plt.grid(True)
plt.show()

# ------------------------------------------------------------
# 5. Confusion Matrix – Random Forest
# ------------------------------------------------------------
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix – Random Forest")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

print("🎉 Dashboard-visualiseringar klara – lägg nu dessa som visualiseringar i din Databricks Dashboard.")
