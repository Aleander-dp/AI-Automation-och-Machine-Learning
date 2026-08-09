# ============================================================
# STEG 3 – Random Forest, Supervised
# ============================================================

# Startar ett nytt MLflow-experiment/run med ett beskrivande namn
with mlflow.start_run(run_name="RandomForest_CTU_IoT_v2") as run:

    # Skapar en Random Forest-klassificerare med valda hyperparametrar
    # (justerade för att undvika 100% accuracy)
    rf = RandomForestClassifier(
        n_estimators=60,               # antal träd i "skogen"
        max_depth=10,                  # max djup på varje träd (vill inte överanpassa)
        min_samples_leaf=5,            # minsta antal observationer i ett löv
        max_features='sqrt',           # använder bara en del av features per träd
        class_weight=None,             # ingen extra viktning (viktigt för mer realistiska resultat)
        random_state=42,               # Svaret på universum är 42
        n_jobs=-1                      # använder alla tillgängliga CPU-kärnor
    )

    # Tränar modellen på träningsdatan (Fit = Träning)
    # Här lär sig modellen mönster som skiljer benign från malicious
    rf.fit(X_train, y_train)

    # Gör prediktioner (predict) på testdatan → ger 0 eller 1
    y_pred = rf.predict(X_test)

    # Hämtar sannolikheter för klassen 1 (malicious)
    y_proba = rf.predict_proba(X_test)[:, 1]

    # Prediktioner (sannolikheter) — tillakt för att kunna skapa ROC-kurva
    y_pred_proba = rf.predict_proba(X_test)[:, 1]

    # Skapar en detaljerad utvärderingsrapport (precision, recall, f1 per klass)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Beräknar ROC-AUC (bra mått när klasserna är obalanserade)
    auc = roc_auc_score(y_test, y_proba)

    # Skriver ut resultaten här på plats
    print("=== Random Forest (v2) ===")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {auc:.4f}")

    # Loggar hyperparametrar till MLflow
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 60)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("min_samples_leaf", 5)
    mlflow.log_param("class_weight", "None")

    # Loggar utvärderingsmått till MLflow
    mlflow.log_metric("roc_auc", auc)
    mlflow.log_metric("precision_malicious", report['1']['precision'])
    mlflow.log_metric("recall_malicious", report['1']['recall'])
    mlflow.log_metric("f1_malicious", report['1']['f1-score'])
    mlflow.log_metric("accuracy", report['accuracy'])

    # Skapar en signatur som beskriver modellens input/output
    signature = infer_signature(X_train, rf.predict(X_train))

    # Loggar själva modellen till MLflow (kan senare laddas ner eller deployas)
    mlflow.sklearn.log_model(rf, "model", signature=signature)

    # Beräknar feature importance (vilka features modellen tycker är viktigast)
    importance = pd.Series(rf.feature_importances_, index=X.columns)\
                    .sort_values(ascending=False)

    # Skriver ut de 10 viktigaste features
    print("\nTop 10 viktigaste features:")
    print(importance.head(10))