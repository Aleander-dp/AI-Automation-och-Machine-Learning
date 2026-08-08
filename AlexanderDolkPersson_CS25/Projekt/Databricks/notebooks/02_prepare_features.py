# ============================================================
# STEG 2 – Förbered features för modellerna
# ============================================================

# Lista över de numeriska features vi ska använda
# (använder VERSALER eftersom kolumnnamnen i Snowflake är stora)
numeric_features = [
    'DURATION',
    'ORIG_BYTES',
    'RESP_BYTES',
    'ORIG_PKTS',
    'RESP_PKTS',
    'ORIG_IP_BYTES',
    'RESP_IP_BYTES',
    'BYTES_RATIO',
    'PKTS_RATIO',
    'IS_LOCAL_ORIG',
    'IS_LOCAL_RESP'
]

# Lista över de kategoriska (text) features
categorical_features = [
    'PROTOCOL',
    'SERVICE',
    'CONN_STATE'
]

# Fyller saknade numeriska värden med 0 (modellerna klarar endast nummer, inte NaN)
df[numeric_features] = df[numeric_features].fillna(0)

# Fyller saknade kategoriska värden med texten 'unknown'
df[categorical_features] = df[categorical_features].fillna('unknown')

# Skapar en dictionary där vi sparar LabelEncoders
# (behövs om vi senare vill transformera ny data på samma sätt)
le_dict = {}

# Loopar igenom varje kategorisk kolumn och omvandlar text till siffror
for col in categorical_features:
    le = LabelEncoder()                              # skapar en ny encoder
    df[col] = le.fit_transform(df[col].astype(str))  # tränar och omvandlar kolumnen
    le_dict[col] = le                                # sparar encodern

# Skapar feature-matrisen X (alla features vi ska träna på)
X = df[numeric_features + categorical_features]

# Skapar target-vektorn y (det vi vill förutsäga: 0 = benign, 1 = malicious)
y = df['IS_MALICIOUS'].astype(int)

# Delar upp datan i tränings- och testmängd (75 % träning, 25 % test)
# stratify=y ser till att andelen malicious blir ungefär densamma i båda mängderna
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,      # 25 % av datan blir testmängd
    random_state=42,     # gör att uppdelningen blir densamma varje gång
    stratify=y           # behåller klassfördelningen
)

# Skriver ut storleken på tränings- och testmängden
print(f"Train: {X_train.shape} | Test: {X_test.shape}")

# Skriver ut andelen malicious i hela datasetet
print(f"Malicious ratio i hela datan: {y.mean():.4f}")

# Visar de första raderna i X så vi ser att allt ser bra ut
X.head()