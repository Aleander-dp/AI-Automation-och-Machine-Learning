# ============================================================
# STEG 4 – Träna Isolation Forest
# ============================================================

# Startar ett nytt MLflow-run för Isolation Forest
with mlflow.start_run(run_name="IsolationForest_CTU_IoT") as run:

    # Tar endast ut de rader som är benign (y_train == 0)
    # Isolation Forest tränas bäst på "normal" trafik
    X_benign = X_train[y_train == 0]

    # Skapar Isolation Forest-modellen
    iso = IsolationForest(
        n_estimators=500,        # antal träd
        contamination=0.04,      # ungefärlig andel anomalier vi förväntar oss
        random_state=42,         # Är svaret på universum fortfarande 42?
        n_jobs=-1                # använd alla CPU-kärnor
    )

    # Tränar modellen enbart på benign trafik (Fit = Träning)
    # Modellen lär sig hur "normal" trafik ser ut
    iso.fit(X_benign)

    # Gör prediktioner på testdatan
    # Isolation Forest returnerar -1 för anomaly och 1 för normal
    # Vi omvandlar till 1 = malicious, 0 = benign
    y_pred_iso = np.where(iso.predict(X_test) == -1, 1, 0)

    # Skapar utvärderingsrapport
    report_iso = classification_report(y_test, y_pred_iso, output_dict=True)

    # Skriver ut resultaten
    print("=== Isolation Forest ===")
    print(classification_report(y_test, y_pred_iso))

    # Loggar parametrar och metrics till MLflow
    mlflow.log_param("model_type", "IsolationForest")
    mlflow.log_param("contamination", 0.04)
    mlflow.log_param("n_estimators", 500)
    mlflow.log_metric("precision_malicious", report_iso['1']['precision'])
    mlflow.log_metric("recall_malicious", report_iso['1']['recall'])
    mlflow.log_metric("f1_malicious", report_iso['1']['f1-score'])
    mlflow.log_metric("accuracy", report_iso['accuracy'])

    # Loggar Isolation Forest-modellen till MLflow
    mlflow.sklearn.log_model(iso, "model")