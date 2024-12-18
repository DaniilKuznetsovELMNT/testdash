import pandas as pd
import numpy as np
import streamlit as st
from fbprophet import Prophet
import plotly.express as px
import plotly.graph_objects as go

# Streamlit Page Configuration
st.set_page_config(
    page_title="ELEMENT · Обзор рынка недвижимости",
    page_icon="https://static.tildacdn.com/tild3763-6366-4764-b663-303235373839/logo_element_dark.svg",
    layout="wide"
)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


# Function for loading and caching data
@st.cache_data()
def load_realty_data():
    # Replace this with actual data file path
    df = pd.read_pickle("realty_sold_LO_SPB.gz")
    df = df.rename(columns={"ЖК рус": "ЖК_рус"})
    df['Цена_м2'] = df['Оценка цены'] / df['Площадь']
    return df


# Load data
df = load_realty_data()

# Sidebar Navigation
with st.sidebar:
    st.header("Навигация")
    selected_tab = st.radio(
        "Выберите модуль",
        ["Обзор", "Прогнозы", "Карта объектов"]
    )

# 1. Dynamic Charts Module
if selected_tab == "Обзор":
    st.title("Динамический анализ цен и площади")

    # Scatter Plot
    st.subheader("Цены на м² по площади")
    fig = px.scatter(
        df,
        x='Площадь',
        y='Цена_м2',
        color='ЖК_рус',
        title="Соотношение цены за м² и площади",
        labels={"Площадь": "Площадь (м²)", "Цена_м2": "Цена (руб/м²)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bar Chart
    st.subheader("Распределение объектов по ЖК")
    bar_fig = px.histogram(
        df,
        x='ЖК_рус',
        title="Количество объектов по ЖК",
        labels={"ЖК_рус": "Название ЖК", "count": "Количество объектов"},
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(bar_fig, use_container_width=True)

# 2. Predictive Analytics Module
elif selected_tab == "Прогнозы":
    st.title("Прогноз цен на будущее")

    # Prepare data for prediction
    st.write("Используем модель временных рядов для прогнозирования цен.")
    df_prophet = df[['Дата сделки', 'Цена_м2']].dropna()
    df_prophet.rename(columns={'Дата сделки': 'ds', 'Цена_м2': 'y'}, inplace=True)

    # Fit Prophet Model
    model = Prophet()
    model.fit(df_prophet)

    # Predict future prices
    future = model.make_future_dataframe(periods=365)
    forecast = model.predict(future)

    # Plot forecast
    fig_forecast = px.line(
        forecast,
        x='ds',
        y='yhat',
        title="Прогноз цен на ближайший год",
        labels={"ds": "Дата", "yhat": "Прогноз цены (руб/м²)"}
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

# 3. Geospatial Analysis Module
elif selected_tab == "Карта объектов":
    st.title("Геопространственный анализ объектов")

    # Assuming 'latitude' and 'longitude' columns exist in the dataset
    if 'latitude' in df.columns and 'longitude' in df.columns:
        st.subheader("Карта ЖК")
        map_fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            color='ЖК_рус',
            size='Площадь',
            mapbox_style="open-street-map",
            title="Объекты на карте",
            hover_name='ЖК_рус'
        )
        st.plotly_chart(map_fig, use_container_width=True)
    else:
        st.error("Нет данных для построения карты. Проверьте наличие колонок с координатами.")

# Footer
st.markdown("---")
st.markdown("© 2024 ELEMENT · Интерактивный дашборд")