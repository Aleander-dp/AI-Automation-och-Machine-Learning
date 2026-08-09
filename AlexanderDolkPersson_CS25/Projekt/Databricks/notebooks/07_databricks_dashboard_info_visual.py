# ============================================================
# DATBRICKS DASHBOARD-CELL (EN CELL)
# - Visar jämförelse mellan Random Forest (RF) och Isolation Forest (ISO)
# ============================================================

# ---------- Importer ----------
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
from sklearn.metrics import (
    roc_curve, auc, precision_recall_curve, average_precision_score,
    confusion_matrix, precision_score, recall_score, f1_score, accuracy_score
)
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings("ignore")

sns.set(style="whitegrid")

# ---------- Hjälpfunktioner (säkra kontroller) ----------
def is_nonempty_array_like(x):
    """
    Returnerar True om x är en array/serie/lista med minst ett element.
    Returnerar False om x är None eller tom.
    Använd för att undvika ValueError vid if x: på array/serie.
    """
    if x is None:
        return False
    if isinstance(x, (pd.Series, pd.DataFrame)):
        return not x.empty
    if isinstance(x, np.ndarray):
        return x.size > 0
    if isinstance(x, (list, tuple)):
        return len(x) > 0
    return True

def first_nonempty(*keys):
    """
    Leta i globals() efter första icke-tomma värdet bland angivna nycklar.
    Returnerar värdet eller None.
    """
    for k in keys:
        v = globals().get(k, None)
        if is_nonempty_array_like(v):
            return v
    return None

def safe_auc(y_true, scores):
    """Beräkna ROC AUC och returnera (auc, fpr, tpr) eller (None, None, None) vid fel."""
    try:
        fpr, tpr, _ = roc_curve(y_true, scores)
        return auc(fpr, tpr), fpr, tpr
    except Exception:
        return None, None, None

def safe_pr(y_true, scores):
    """Beräkna PR AUC och returnera (pr_auc, precision, recall) eller (None, None, None)."""
    try:
        precision, recall, _ = precision_recall_curve(y_true, scores)
        return average_precision_score(y_true, scores), precision, recall
    except Exception:
        return None, None, None

# ---------- Widgets (kör en gång) ----------
try:
    dbutils.widgets.removeAll()
except Exception:
    pass

# Modellval (behåll för flexibilitet), tröskel, TopN och permutation toggle
dbutils.widgets.dropdown("ModelSelect", "Both", ["Both","RandomForest","IsolationForest"], "Visa modell")
dbutils.widgets.text("Threshold", "0.5", "Tröskel (0-1) för binär klassning (används för RF och ISO score->binär om önskas)")
dbutils.widgets.dropdown("TopN", "10", [str(i) for i in [5,10,15,20]], "Top N features")
dbutils.widgets.dropdown("ShowPermutation", "no", ["yes","no"], "Visa permutation importance (kan vara tungt)")

# ---------- Läs widgetvärden ----------
model_choice = dbutils.widgets.get("ModelSelect")
threshold = float(dbutils.widgets.get("Threshold"))
top_n = int(dbutils.widgets.get("TopN"))
show_perm = dbutils.widgets.get("ShowPermutation") == "yes"

print(f"Inställningar: model={model_choice}, threshold={threshold}, TopN={top_n}, Perm={show_perm}")

# ---------- Hämta variabler säkert från globals ----------
# RF: försök hämta sannolikheter och prediktioner från vanliga namn
rf_scores = first_nonempty("y_proba", "y_pred_proba")   # sannolikheter för klass 1 (RF)
rf_preds = first_nonempty("y_pred",)                    # binära prediktioner (RF)
rf_importance = globals().get("importance", None)       # RF feature importance (pd.Series)

# ISO: hämta om finns (kan vara None)
iso_scores = first_nonempty("iso_scores_norm", "iso_scores")  # normaliserade ISO-scores (0-1) om tillgängliga
iso_preds = first_nonempty("y_pred_iso",)                     # ISO binära prediktioner (0/1) om tillgängliga

# Debug-utskrifter för typ/shape — användbart vid felsökning
print("DEBUG: rf_scores type/shape:", type(rf_scores), getattr(rf_scores, "shape", None))
print("DEBUG: rf_preds type/shape:", type(rf_preds), getattr(rf_preds, "shape", None))
print("DEBUG: iso_scores type/shape:", type(iso_scores), getattr(iso_scores, "shape", None))
print("DEBUG: iso_preds type/shape:", type(iso_preds), getattr(iso_preds, "shape", None))
print("DEBUG: rf_importance type:", type(rf_importance))

# Kontrollera att X_test och y_test finns — annars avbryt
if "X_test" not in globals() or "y_test" not in globals():
    raise RuntimeError("X_test och/eller y_test saknas i miljön. Kör träningscellerna först.")

# ---------- KPI: samla huvudmetrics för RF och ISO (om tillgängliga) ----------
kpi_rows = []

# RF-metrics (om vi har scores eller preds)
if is_nonempty_array_like(rf_scores) or is_nonempty_array_like(rf_preds):
    # beräkna klassiska metrics om preds finns
    acc = prec = rec = f1 = None
    if is_nonempty_array_like(rf_preds):
        preds_arr = np.asarray(rf_preds)
        acc = float(accuracy_score(y_test, preds_arr))
        prec = float(precision_score(y_test, preds_arr, zero_division=0))
        rec = float(recall_score(y_test, preds_arr, zero_division=0))
        f1 = float(f1_score(y_test, preds_arr, zero_division=0))
    # ROC/PR om scores finns
    roc_auc_val = pr_auc_val = None
    if is_nonempty_array_like(rf_scores):
        scores_arr = np.asarray(rf_scores)
        roc_auc_val, _, _ = safe_auc(y_test, scores_arr)
        pr_auc_val, _, _ = safe_pr(y_test, scores_arr)
    kpi_rows.append({
        "Model": "RandomForest",
        "Accuracy": acc,
        "Precision_malicious": prec,
        "Recall_malicious": rec,
        "F1_malicious": f1,
        "ROC_AUC": roc_auc_val,
        "PR_AUC": pr_auc_val
    })
else:
    print("RF: inga giltiga scores eller prediktioner hittades. Kontrollera att rf, y_proba och y_pred finns i miljön.")

# ISO-metrics (vi beräknar ROC/PR och klassiska metrics om preds finns)
if is_nonempty_array_like(iso_scores) or is_nonempty_array_like(iso_preds):
    acc_i = prec_i = rec_i = f1_i = None
    if is_nonempty_array_like(iso_preds):
        preds_iso_arr = np.asarray(iso_preds)
        acc_i = float(accuracy_score(y_test, preds_iso_arr))
        prec_i = float(precision_score(y_test, preds_iso_arr, zero_division=0))
        rec_i = float(recall_score(y_test, preds_iso_arr, zero_division=0))
        f1_i = float(f1_score(y_test, preds_iso_arr, zero_division=0))
    roc_auc_i = pr_auc_i = None
    if is_nonempty_array_like(iso_scores):
        scores_iso_arr = np.asarray(iso_scores)
        roc_auc_i, _, _ = safe_auc(y_test, scores_iso_arr)
        pr_auc_i, _, _ = safe_pr(y_test, scores_iso_arr)
    kpi_rows.append({
        "Model": "IsolationForest",
        "Accuracy": acc_i,
        "Precision_malicious": prec_i,
        "Recall_malicious": rec_i,
        "F1_malicious": f1_i,
        "ROC_AUC": roc_auc_i,
        "PR_AUC": pr_auc_i
    })
else:
    print("ISO: inga giltiga scores eller prediktioner hittades. ISO-visualiseringar kommer att visa tillgängliga plots utan confusion matrix för ISO.")

kpi_df = pd.DataFrame(kpi_rows)
print("✅ KPI-tabell:")
display(kpi_df)

# ---------- ROC & PR subplot (jämför modeller) ----------
fig = make_subplots(rows=1, cols=2, subplot_titles=("ROC Curve","Precision-Recall Curve"))

# RF kurvor
if is_nonempty_array_like(rf_scores):
    rf_scores_arr = np.asarray(rf_scores)
    auc_rf, fpr_rf, tpr_rf = safe_auc(y_test, rf_scores_arr)
    pr_auc_rf, prec_rf, rec_rf = safe_pr(y_test, rf_scores_arr)
    if fpr_rf is not None:
        fig.add_trace(go.Scatter(x=fpr_rf, y=tpr_rf, mode='lines', name=f"RF ROC AUC={auc_rf:.3f}"), row=1, col=1)
    if rec_rf is not None:
        fig.add_trace(go.Scatter(x=rec_rf, y=prec_rf, mode='lines', name=f"RF PR AUC={pr_auc_rf:.3f}"), row=1, col=2)

# ISO kurvor
if is_nonempty_array_like(iso_scores):
    iso_scores_arr = np.asarray(iso_scores)
    auc_iso, fpr_iso, tpr_iso = safe_auc(y_test, iso_scores_arr)
    pr_auc_iso, prec_iso, rec_iso = safe_pr(y_test, iso_scores_arr)
    if fpr_iso is not None:
        fig.add_trace(go.Scatter(x=fpr_iso, y=tpr_iso, mode='lines', name=f"ISO ROC AUC={auc_iso:.3f}"), row=1, col=1)
    if rec_iso is not None:
        fig.add_trace(go.Scatter(x=rec_iso, y=prec_iso, mode='lines', name=f"ISO PR AUC={pr_auc_iso:.3f}"), row=1, col=2)

# Referenslinje för ROC
fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', line=dict(dash='dash', color='gray'), showlegend=False), row=1, col=1)
fig.update_xaxes(title_text="False Positive Rate", row=1, col=1)
fig.update_yaxes(title_text="True Positive Rate", row=1, col=1)
fig.update_xaxes(title_text="Recall", row=1, col=2)
fig.update_yaxes(title_text="Precision", row=1, col=2)
fig.update_layout(height=480, width=1100, title_text="ROC & PR – RandomForest vs IsolationForest")
fig.show()

# ---------- Confusion matrix (ENDAST Random Forest) ----------
# Vi tar bort confusion matrix för Isolation Forest enligt önskemål.
preds_rf_thresh = None
if is_nonempty_array_like(rf_scores):
    preds_rf_thresh = (np.asarray(rf_scores) >= threshold).astype(int)
elif is_nonempty_array_like(rf_preds):
    preds_rf_thresh = np.asarray(rf_preds)

if preds_rf_thresh is not None:
    cm = confusion_matrix(y_test, preds_rf_thresh)
    cm_df = pd.DataFrame(cm, index=["Actual 0","Actual 1"], columns=["Pred 0","Pred 1"])
    fig_cm = px.imshow(cm_df, text_auto=True, color_continuous_scale="Blues", title=f"Confusion Matrix (Random Forest) @ threshold {threshold}")
    fig_cm.update_layout(width=600, height=400)
    fig_cm.show()
else:
    print("Ingen binär prediktion tillgänglig för Random Forest confusion matrix. Ange y_pred eller y_proba.")

# ---------- Score-distribution (overlay) för båda modeller ----------
# Visar hur scores fördelar sig per klass; hjälper att bedöma separation.
if is_nonempty_array_like(rf_scores):
    df_rf = pd.DataFrame({"score": np.asarray(rf_scores), "label": y_test.values})
    fig_rf_hist = px.histogram(df_rf, x="score", color="label", nbins=40, barmode="overlay",
                               opacity=0.6, title="RF score distribution (overlay)", labels={"label":"Actual label"})
    fig_rf_hist.update_layout(width=800, height=350)
    fig_rf_hist.show()

if is_nonempty_array_like(iso_scores):
    df_iso = pd.DataFrame({"score": np.asarray(iso_scores), "label": y_test.values})
    fig_iso_hist = px.histogram(df_iso, x="score", color="label", nbins=40, barmode="overlay",
                                opacity=0.6, title="ISO score distribution (overlay)", labels={"label":"Actual label"})
    fig_iso_hist.update_layout(width=800, height=350)
    fig_iso_hist.show()

# ---------- Feature importance (RF) och permutation importance ----------
# RF inbyggd importance (endast RF har denna)
if rf_importance is not None:
    try:
        fi = pd.DataFrame({"feature": rf_importance.index, "importance": rf_importance.values}).head(top_n)
        fig_fi = px.bar(fi[::-1], x="importance", y="feature", orientation="h", title=f"Top {top_n} Feature Importance (RF)")
        fig_fi.update_layout(width=700, height=350)
        fig_fi.show()
    except Exception as e:
        print("Kunde inte rita RF feature importance:", type(e).__name__, e)
else:
    print("RF feature importance saknas eller ej tillgänglig som 'importance' (pd.Series).")

# Permutation importance (valfritt, tungt)
if show_perm and 'rf' in globals() and is_nonempty_array_like(X_test):
    try:
        print("Beräknar permutation importance (kan ta tid)...")
        perm_res = permutation_importance(rf, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
        perm_df = pd.DataFrame({
            "feature": X_test.columns,
            "perm_mean": perm_res.importances_mean,
            "perm_std": perm_res.importances_std
        }).sort_values("perm_mean", ascending=False).head(top_n)
        display(perm_df)
        fig_perm = px.bar(perm_df[::-1], x="perm_mean", y="feature", orientation="h", title="Permutation importance (top)")
        fig_perm.update_layout(width=700, height=350)
        fig_perm.show()
    except Exception as e:
        print("Permutation importance misslyckades eller tog för lång tid:", type(e).__name__, e)
elif show_perm:
    print("Permutation importance kräver att RF är tränad och X_test finns i miljön.")

# ---------- Cumulative gains / lift (approx) för RF och ISO ----------
def cumulative_gains(y_true, scores):
    df = pd.DataFrame({"y": y_true, "score": scores})
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["cum_positive"] = df["y"].cumsum()
    total_pos = df["y"].sum() if df["y"].sum() > 0 else 1
    df["cum_pct_pos"] = df["cum_positive"] / total_pos
    df["pct_samples"] = (np.arange(len(df)) + 1) / len(df)
    return df

if is_nonempty_array_like(rf_scores):
    cg_rf = cumulative_gains(y_test, np.asarray(rf_scores))
    fig_cg = go.Figure()
    fig_cg.add_trace(go.Scatter(x=cg_rf["pct_samples"], y=cg_rf["cum_pct_pos"], name="RF"))
    fig_cg.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', line=dict(dash='dash', color='gray'), showlegend=False))
    fig_cg.update_layout(title="Cumulative gains (RF)", xaxis_title="Proportion of sample", yaxis_title="Proportion of positives captured", width=700, height=400)
    fig_cg.show()

if is_nonempty_array_like(iso_scores):
    cg_iso = cumulative_gains(y_test, np.asarray(iso_scores))
    fig_cg2 = go.Figure()
    fig_cg2.add_trace(go.Scatter(x=cg_iso["pct_samples"], y=cg_iso["cum_pct_pos"], name="ISO"))
    fig_cg2.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', line=dict(dash='dash', color='gray'), showlegend=False))
    fig_cg2.update_layout(title="Cumulative gains (ISO)", xaxis_title="Proportion of sample", yaxis_title="Proportion of positives captured", width=700, height=400)
    fig_cg2.show()

# ---------- Avslutande meddelande ----------
print("Dashboard skapad")

