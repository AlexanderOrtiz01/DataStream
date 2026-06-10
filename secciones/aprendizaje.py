# -*- coding: utf-8 -*-
"""Opcion 3: Aprendizaje Automatico (regresion y clasificacion interactivos)."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error,
    accuracy_score, precision_score, recall_score, f1_score,
)

from utils.datos import cargar_datos, columnas_numericas, columnas_categoricas

# Variables objetivo posibles (cuantitativas -> regresion; categoricas -> clasificacion)
_OBJETIVOS_REGRESION = ["salario_prom_k", "salario_max_k",
                        "valoracion", "antiguedad_empresa"]
_OBJETIVOS_CLASIFICACION = ["sector", "tipo_propiedad",
                            "tamano_empresa", "aplicacion_facil"]


def mostrar():
    st.title("Aprendizaje Automatico")
    df = cargar_datos()

    st.write(
        "Configura un modelo seleccionando la variable a predecir, las variables "
        "predictoras, el algoritmo y la division de datos. La aplicacion entrena el "
        "modelo y muestra sus resultados."
    )

    # ----------------------------- Configuracion -------------------------- #
    st.sidebar.markdown("### Configuracion del modelo")

    tipo = st.radio(
        "Tipo de problema",
        ["Regresion (predecir un valor numerico)", "Clasificacion (predecir una categoria)"],
        horizontal=False,
    )
    es_regresion = tipo.startswith("Regresion")

    col_a, col_b = st.columns(2)
    with col_a:
        if es_regresion:
            objetivo = st.selectbox("Variable a analizar (objetivo)", _OBJETIVOS_REGRESION)
            algoritmo = st.selectbox(
                "Algoritmo",
                ["Regresion Lineal", "Arbol de Decision", "Random Forest"])
        else:
            objetivo = st.selectbox("Variable a analizar (objetivo)", _OBJETIVOS_CLASIFICACION)
            algoritmo = st.selectbox(
                "Algoritmo",
                ["Regresion Logistica", "K-Vecinos (KNN)", "Random Forest"])

    # Variables independientes candidatas (numericas, sin el objetivo)
    candidatas = [c for c in columnas_numericas(df) if c != objetivo]
    with col_b:
        predeterminadas = candidatas[:2] if len(candidatas) >= 2 else candidatas
        predictoras = st.multiselect(
            "Variables independientes (predictoras)",
            candidatas, default=predeterminadas)

    # Division de datos: dos sliders separados que se mantienen sincronizados
    # (entrenamiento y prueba son complementarios y siempre suman 100%).
    st.markdown("**Division de los datos**")
    if "ml_test_pct" not in st.session_state:
        st.session_state["ml_test_pct"] = 25
        st.session_state["ml_train_pct"] = 75

    def _sync_desde_train():
        st.session_state["ml_test_pct"] = 100 - st.session_state["ml_train_pct"]

    def _sync_desde_test():
        st.session_state["ml_train_pct"] = 100 - st.session_state["ml_test_pct"]

    col_tr, col_te = st.columns(2)
    with col_tr:
        st.slider("Datos de ENTRENAMIENTO (%)", 50, 90, step=5,
                  key="ml_train_pct", on_change=_sync_desde_train,
                  help="Porcentaje de filas para entrenar el modelo. Al moverlo se "
                       "ajusta el de prueba (siempre suman 100%).")
    with col_te:
        st.slider("Datos de PRUEBA (%)", 10, 50, step=5,
                  key="ml_test_pct", on_change=_sync_desde_test,
                  help="Porcentaje de filas para evaluar el modelo. Al moverlo se "
                       "ajusta el de entrenamiento (siempre suman 100%).")

    test_size = st.session_state["ml_test_pct"]
    st.caption(f"Entrenamiento: **{100 - test_size}%**  ·  Prueba: **{test_size}%**")

    if len(predictoras) < 1:
        st.warning("Selecciona al menos una variable independiente.")
        return
    if objetivo in predictoras:
        st.warning("La variable objetivo no puede estar entre las predictoras.")
        return

    if not st.button("Entrenar modelo", type="primary"):
        st.info("Configura los parametros y presiona **Entrenar modelo**.")
        return

    # ------------------------------ Entrenamiento ------------------------- #
    # El dataset real tiene valores faltantes: se descartan las filas con NaN en
    # las columnas implicadas para que el modelo pueda entrenarse.
    datos = df[predictoras + [objetivo]].dropna()
    filas_descartadas = len(df) - len(datos)
    if len(datos) < 20:
        st.error("Quedan muy pocos datos sin valores faltantes para entrenar. "
                 "Elige otras variables.")
        return
    if filas_descartadas:
        st.caption(f"Se descartaron {filas_descartadas:,} filas con valores "
                   f"faltantes en las variables seleccionadas.")

    X = datos[predictoras].copy()
    y = datos[objetivo].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size / 100, random_state=42)

    escalador = StandardScaler()
    X_train_s = escalador.fit_transform(X_train)
    X_test_s = escalador.transform(X_test)

    if es_regresion:
        _entrenar_regresion(algoritmo, predictoras, objetivo,
                            X_train_s, X_test_s, y_train, y_test)
    else:
        _entrenar_clasificacion(algoritmo, predictoras, objetivo,
                               X_train_s, X_test_s, y_train, y_test)


# --------------------------------------------------------------------------- #
def _modelo_regresion(nombre):
    return {
        "Regresion Lineal": LinearRegression(),
        "Arbol de Decision": DecisionTreeRegressor(max_depth=6, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=120, random_state=42),
    }[nombre]


def _entrenar_regresion(algoritmo, predictoras, objetivo,
                        X_train, X_test, y_train, y_test):
    modelo = _modelo_regresion(algoritmo)
    modelo.fit(X_train, y_train)
    pred_train = modelo.predict(X_train)
    pred_test = modelo.predict(X_test)

    st.subheader("Resultados del modelo de regresion")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R² (prueba)", f"{r2_score(y_test, pred_test):.3f}")
    c2.metric("R² (entrenamiento)", f"{r2_score(y_train, pred_train):.3f}")
    c3.metric("MAE (prueba)", f"{mean_absolute_error(y_test, pred_test):.3f}")
    c4.metric("RMSE (prueba)", f"{np.sqrt(mean_squared_error(y_test, pred_test)):.3f}")

    # Parametros del modelo (coeficientes o importancias)
    st.markdown("**Parametros de entrenamiento:**")
    if hasattr(modelo, "coef_"):
        coefs = pd.DataFrame({"Variable": predictoras, "Coeficiente": modelo.coef_})
        coefs.loc[len(coefs)] = ["(intercepto)", modelo.intercept_]
        st.dataframe(coefs, width="stretch", hide_index=True)
    elif hasattr(modelo, "feature_importances_"):
        imp = pd.DataFrame({"Variable": predictoras,
                            "Importancia": modelo.feature_importances_}
                           ).sort_values("Importancia", ascending=False)
        st.dataframe(imp, width="stretch", hide_index=True)

    # Grafica: valores reales vs predichos, distinguiendo entrenamiento y prueba
    st.markdown("**Valores reales vs. predichos** (entrenamiento y prueba):")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_train, y=pred_train, mode="markers", name="Entrenamiento",
        marker=dict(color="#4C78A8", opacity=0.5)))
    fig.add_trace(go.Scatter(
        x=y_test, y=pred_test, mode="markers", name="Prueba (predicciones)",
        marker=dict(color="#7267ef", opacity=0.8)))
    lo = float(min(y_train.min(), y_test.min()))
    hi = float(max(y_train.max(), y_test.max()))
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                             name="Prediccion perfecta",
                             line=dict(color="green", dash="dash")))
    fig.update_layout(xaxis_title=f"{objetivo} (real)",
                      yaxis_title=f"{objetivo} (predicho)",
                      title="Ajuste del modelo")
    st.plotly_chart(fig, width="stretch")
    _explicacion_regresion()


# --------------------------------------------------------------------------- #
def _modelo_clasificacion(nombre):
    return {
        "Regresion Logistica": LogisticRegression(max_iter=1000),
        "K-Vecinos (KNN)": KNeighborsClassifier(n_neighbors=7),
        "Random Forest": RandomForestClassifier(n_estimators=120, random_state=42),
    }[nombre]


def _entrenar_clasificacion(algoritmo, predictoras, objetivo,
                            X_train, X_test, y_train, y_test):
    modelo = _modelo_clasificacion(algoritmo)
    modelo.fit(X_train, y_train)
    pred_train = modelo.predict(X_train)
    pred_test = modelo.predict(X_test)

    st.subheader("Resultados del modelo de clasificacion")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy (prueba)", f"{accuracy_score(y_test, pred_test):.3f}")
    c2.metric("Accuracy (entren.)", f"{accuracy_score(y_train, pred_train):.3f}")
    c3.metric("Precision", f"{precision_score(y_test, pred_test, average='weighted', zero_division=0):.3f}")
    c4.metric("F1-score", f"{f1_score(y_test, pred_test, average='weighted', zero_division=0):.3f}")

    # Matriz de confusion
    st.markdown("**Matriz de confusion (datos de prueba):**")
    clases = sorted(pd.unique(y_test))
    matriz = pd.crosstab(pd.Series(y_test.values, name="Real"),
                         pd.Series(pred_test, name="Predicho"))
    fig = px.imshow(matriz, text_auto=True, color_continuous_scale="Blues",
                    title="Matriz de confusion")
    st.plotly_chart(fig, width="stretch")

    # Importancia / parametros
    if hasattr(modelo, "feature_importances_"):
        st.markdown("**Importancia de las variables:**")
        imp = pd.DataFrame({"Variable": predictoras,
                            "Importancia": modelo.feature_importances_}
                           ).sort_values("Importancia", ascending=False)
        st.dataframe(imp, width="stretch", hide_index=True)

    # Grafica comparando aciertos en entrenamiento vs prueba
    st.markdown("**Aciertos por conjunto** (entrenamiento y prueba):")
    resumen = pd.DataFrame({
        "Conjunto": ["Entrenamiento", "Prueba"],
        "Accuracy": [accuracy_score(y_train, pred_train),
                     accuracy_score(y_test, pred_test)],
    })
    fig2 = px.bar(resumen, x="Conjunto", y="Accuracy", color="Conjunto",
                  range_y=[0, 1], text_auto=".3f",
                  title="Exactitud en entrenamiento vs prueba")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, width="stretch")
    _explicacion_clasificacion()


def _explicacion_regresion():
    with st.expander("Como interpretar estos resultados"):
        st.markdown(
            "- **R²**: proporcion de la varianza explicada (1 = perfecto, 0 = nulo).\n"
            "- **MAE / RMSE**: error promedio de las predicciones (menor es mejor).\n"
            "- En la grafica, cuanto mas cerca esten los puntos de la linea verde "
            "discontinua, mejor es la prediccion. Los puntos morados son los datos de "
            "**prueba** y los azules los de **entrenamiento**."
        )


def _explicacion_clasificacion():
    with st.expander("Como interpretar estos resultados"):
        st.markdown(
            "- **Accuracy**: porcentaje de predicciones correctas.\n"
            "- **Matriz de confusion**: la diagonal son los aciertos; fuera de ella, "
            "los errores.\n"
            "- Comparar la exactitud de **entrenamiento** y **prueba** ayuda a "
            "detectar sobreajuste (overfitting)."
        )
