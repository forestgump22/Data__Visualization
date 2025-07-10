# CC211 – Data Visualization - Trabajo Final 2025
# Profesor: Andrés Gibu La Torre
# Dashboard desarrollado con alto contraste visual para facilitar la lectura y validación de hipótesis

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from scipy.stats import pearsonr

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DEL DASHBOARD
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CC211 - Amazon Books Analytics",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados con alto contraste
st.markdown("""
<style>
body {
    color: #111 !important;
}
.main-header {
    background: linear-gradient(135deg, #FF9900 0%, #146EB4 50%, #232F3E 100%);
    padding: 2rem;
    border-radius: 15px;
    color: #fff;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: #FFFFFF;
    padding: 1.25rem;
    border-radius: 10px;
    border-left: 6px solid #FF9900;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    color: #232F3E;
}
.insight-box {
    background: #FFF8DC;
    padding: 1.25rem;
    border-radius: 10px;
    border: 2px solid #FFA500;
    color: #111;
}
.conclusion-box {
    background: #E8F5E9;
    padding: 2rem;
    border-radius: 10px;
    border: 2px solid #4CAF50;
    color: #111;
}
.academic-info {
    background: #f9f9f9;
    padding: 1.25rem;
    border-left: 5px solid #146EB4;
    border-radius: 10px;
    margin-bottom: 1rem;
    color: #111;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNCIONES DE DATOS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("bestsellers.csv")
        st.success("✅ Dataset cargado exitosamente")
    except FileNotFoundError:
        st.warning("⚠️ Archivo no encontrado. Generando dataset simulado.")
        np.random.seed(42)
        sample_books = ["Becoming", "The Help", "Gone Girl"]
        authors = ["Obama", "Flynn", "Stockett"]
        data = []
        for year in range(2009, 2020):
            for _ in range(50):
                data.append({
                    "Name": np.random.choice(sample_books),
                    "Author": np.random.choice(authors),
                    "User Rating": np.round(np.random.uniform(3.5, 5.0), 2),
                    "Reviews": np.random.randint(50, 80000),
                    "Price": np.random.randint(5, 60),
                    "Year": year,
                    "Genre": np.random.choice(["Fiction", "Non Fiction"])
                })
        df = pd.DataFrame(data)
    return df

def create_synthetic_variables(df):
    df['Engagement_Score'] = df['Reviews'] / df['Reviews'].max() * 100
    return df

def analyze_hypothesis_3(df):
    grouped = df.groupby('Name').agg(
        Years_Count=('Year', 'count'),
        Avg_Rating=('User Rating', 'mean')
    ).sort_values(by='Years_Count', ascending=False)
    return grouped

def analyze_hypothesis_5(df):
    df['Review_Category'] = pd.cut(
        df['Reviews'], bins=[0,1000,5000,15000,float('inf')],
        labels=['Bajo','Medio','Alto','Muy Alto']
    )
    return df.groupby('Review_Category')[['Reviews', 'User Rating', 'Price']].mean().round(2), df

def analyze_hypothesis_9(df):
    corr_values = {
        'rating_reviews': pearsonr(df['User Rating'], df['Reviews'])[0],
        'rating_price': pearsonr(df['User Rating'], df['Price'])[0],
        'reviews_price': pearsonr(df['Reviews'], df['Price'])[0]
    }
    corr_matrix = df[['User Rating','Reviews','Price','Engagement_Score']].corr()
    return corr_values, corr_matrix

# -----------------------------------------------------------------------------
# CARGA Y FILTROS
# -----------------------------------------------------------------------------
df = load_data()
df = create_synthetic_variables(df)

st.markdown("""
<div class="main-header">
    <h1>📊 TRABAJO FINAL - CC211 DATA VISUALIZATION</h1>
    <h2>Amazon Books Analytics Dashboard</h2>
    <p><strong>Análisis de compra de libros 2009-2019</strong></p>
    <p>Profesor: Andrés Gibu La Torre</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="academic-info">
    <h4>📋 INFORMACIÓN DEL PROYECTO</h4>
    <ul>
        <li><strong>Objetivo:</strong> Identificar patrones de compra en libros</li>
        <li><strong>Dataset:</strong> Top 50 Best Sellers Amazon (2009-2019)</li>
        <li><strong>Metodología:</strong> Desarrollo cíclico de DataViz con validación de hipótesis</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sidebar - Filtros
years = sorted(df['Year'].unique())
genres = df['Genre'].unique()
sel_years = st.sidebar.multiselect("Años de Análisis:", years, default=years)
sel_genres = st.sidebar.multiselect("Géneros: ", genres, default=genres)
filtered_df = df[df['Year'].isin(sel_years) & df['Genre'].isin(sel_genres)]

# -----------------------------------------------------------------------------
# MÉTRICAS GENERALES
# -----------------------------------------------------------------------------
st.markdown("## 📈 MÉTRICAS GENERALES")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Libros", f"{len(filtered_df)}")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Rating Promedio", f"{filtered_df['User Rating'].mean():.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Reviews Promedio", f"{filtered_df['Reviews'].mean():,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HIPÓTESIS 3 - Persistencia
# -----------------------------------------------------------------------------
st.markdown("## 🔄 HIPÓTESIS 3: Persistencia en Rankings")
persistencia = analyze_hypothesis_3(filtered_df).reset_index()
st.dataframe(persistencia)

fig_persist = px.bar(
    persistencia.head(10),
    x='Years_Count', y='Name',
    color='Avg_Rating', orientation='h',
    title="Top 10 Libros Más Persistentes",
    labels={'Years_Count': 'Años en Ranking', 'Name': 'Libro', 'Avg_Rating': 'Rating Promedio'},
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig_persist, use_container_width=True)

# -----------------------------------------------------------------------------
# HIPÓTESIS 5 - Reviews y Ventas
# -----------------------------------------------------------------------------
st.markdown("## 💬 HIPÓTESIS 5: Reviews como Indicador de Ventas")
review_summary, df_cat = analyze_hypothesis_5(filtered_df)
st.dataframe(review_summary)

fig_reviews = px.bar(
    review_summary.reset_index(),
    x='Review_Category', y='Reviews',
    color='User Rating',
    title="Promedio de Reviews y Rating por Categoría",
    labels={'Reviews': 'Reviews Prom.', 'User Rating': 'Rating Prom.'},
    color_continuous_scale='Blues'
)
st.plotly_chart(fig_reviews, use_container_width=True)

# -----------------------------------------------------------------------------
# HIPÓTESIS 9 - Correlaciones
# -----------------------------------------------------------------------------
st.markdown("## 📊 HIPÓTESIS 9: Correlaciones Entre Variables")
corr_values, corr_matrix = analyze_hypothesis_9(filtered_df)
st.dataframe(corr_matrix)

fig_corr = px.imshow(
    corr_matrix,
    text_auto=True,
    title="Matriz de Correlación",
    color_continuous_scale='RdBu',
    zmin=-1, zmax=1
)
st.plotly_chart(fig_corr, use_container_width=True)

# -----------------------------------------------------------------------------
# RESUMEN
# -----------------------------------------------------------------------------
st.markdown("""
<div class="conclusion-box">
    <h4>📋 RESUMEN EJECUTIVO</h4>
    <ul>
        <li><strong>Hipótesis 3:</strong> Confirmada parcialmente. Libros con buen rating tienden a permanecer más tiempo.</li>
        <li><strong>Hipótesis 5:</strong> Confirmada. Reviews correlaciona con engagement.</li>
        <li><strong>Hipótesis 9:</strong> Parcialmente confirmada. Rating no tiene correlación fuerte con reviews.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("Desarrollado por el estudiante | CC211 - UPC 2025")
