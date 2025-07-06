import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier

# 🟢 Streamlit Setup
st.set_page_config(page_title="KI Frühwarnsystem Demo", layout="wide")
st.title("Frühwarnsystem (Prototyp)")

# 🟢 1. Eingaben: User-Parameter
regen = st.slider("Regenmenge (mm)", 0, 100, 50)
bodenfeuchte = st.slider("Bodenfeuchte (%)", 0, 100, 60)
hoehe_schwelle = st.slider("Max. Höhenlage (m)", 0, 50, 20)

# 🟢 2. Dummy Historische Daten + ML-Block
np.random.seed(42)
num_points = 50
heights = np.random.uniform(0, 50, num_points)

# Dummy-Daten (normalerweise CSV oder echte Sensordaten)
data = pd.DataFrame({
    "regen": np.random.randint(0, 100, num_points),
    "bodenfeuchte": np.random.randint(20, 100, num_points),
    "hoehe": np.random.randint(0, 50, num_points),
    "label": np.random.choice([0, 1], size=num_points)
})

X = data[["regen", "bodenfeuchte", "hoehe"]]
y = data["label"]

# Trainiere Dummy-Modell
model = RandomForestClassifier()
model.fit(X, y)

# Vorhersage für aktuelle Eingaben
input_data = pd.DataFrame({
    "regen": [regen],
    "bodenfeuchte": [bodenfeuchte],
    "hoehe": [hoehe_schwelle]
})
prediction = model.predict_proba(input_data)[0][1] * 100

st.write(f"**ML-basiertes Risiko für aktuelle Eingaben: {prediction:.1f}%**")

# 🟢 3. Dynamische Zeitreihe (Forecast)
# Jetzt wird die Zeitreihe direkt an die ML-Vorhersage gekoppelt
time = pd.date_range(start="2025-07-01", periods=7, freq="D")
risk_series = np.clip(
    np.random.normal(loc=prediction, scale=5, size=7),
    0, 100
)

df = pd.DataFrame({"Datum": time, "Risiko (%)": risk_series}).set_index("Datum")
st.subheader("Risiko-Entwicklung über die Zeit")
st.line_chart(df)

# 🟢 4. Risiko-Logik für alle Rasterpunkte
risk_probability = np.random.uniform(50, 95, num_points)
risk = np.where(
    (heights < hoehe_schwelle) &
    (regen > 40) &
    (bodenfeuchte > 50),
    1, 0
)

risk_score = np.zeros(num_points)
for i in range(num_points):
    if risk[i] == 1:
        if risk_probability[i] < 70:
            risk_score[i] = 1  # mittel
        elif 70 <= risk_probability[i] < 85:
            risk_score[i] = 2  # hoch
        else:
            risk_score[i] = 3  # extrem

# 🟢 5. Interaktive Karte
m = folium.Map(location=[23.7, 90.4], zoom_start=7)

# Risiko-Zone (Kreis)
folium.Circle(
    location=[23.7, 90.4],
    radius=20000,
    color='purple',
    fill=True,
    fill_opacity=0.2,
    popup="Haupt-Risikozone"
).add_to(m)

# Rasterpunkte mit Popups & Farbcodes
for i in range(num_points):
    if risk[i] == 1:
        if risk_score[i] == 1:
            color = 'orange'
            radius = 5
        elif risk_score[i] == 2:
            color = 'red'
            radius = 7
        elif risk_score[i] == 3:
            color = 'darkred'
            radius = 10

        popup_text = (
            f"<b>Raster #{i}</b><br>"
            f"Höhe: {heights[i]:.1f} m<br>"
            f"Schwelle: {hoehe_schwelle} m<br>"
            f"Regen: {regen} mm<br>"
            f"Bodenfeuchte: {bodenfeuchte}%<br>"
            f"Wahrscheinlichkeit: {risk_probability[i]:.1f}%<br>"
            f"Risikostufe: {int(risk_score[i])}"
        )

        folium.CircleMarker(
            location=[23.7 + np.random.uniform(-0.05, 0.05),
                      90.4 + np.random.uniform(-0.05, 0.05)],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=popup_text
        ).add_to(m)

# Karte einbinden
st.subheader(" Risiko-Karte")
st_data = st_folium(m, width=800, height=600)
st.write(f"🔍 Anzahl kritischer Rasterpunkte: {int(risk.sum())}")

# 🟢 6. Frühwarn-Trigger
if prediction > 70:
    st.warning("Achtung! Frühwarnung aktiviert: SMS an Behörden wird simuliert.")
else:
    st.success("Kein kritisches Risiko erkannt.")
