import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Задаем путь к CSV-файлу
file_path = "/Users/gulalekmametjumayeva/Downloads/health_fitness_dataset.csv"
df = pd.read_csv(file_path)

# Удаляем лишние пробелы в заголовках
df.columns = df.columns.str.strip()
print("Заголовки столбцов:", df.columns.tolist())

# Преобразуем столбец 'Datetime' в формат datetime и сортируем данные
df['Datetime'] = pd.to_datetime(df['Datetime'])
df = df.sort_values('Datetime')

# Создаем агрегированные данные по неделям для диаграммы "Дистанция в км по неделям"
df_week = df.resample('W', on='Datetime').sum().reset_index()

# =============================================================================
# 1. АКТИВНОСТЬ
# =============================================================================
# 1.1. Линейный график: "Шаги по дням"
fig_steps = px.line(df, x="Datetime", y="Steps", title="Шаги по дням")

# 1.2. Столбчатая диаграмма: "Дистанция в км по неделям"
fig_distance = px.bar(df_week, x="Datetime", y="Distance_km", title="Дистанция в км по неделям")

# =============================================================================
# 2. ЗДОРОВЬЕ
# =============================================================================
# 2.1. Линейный график: "Пульс и давление во времени"
fig_health = go.Figure()
fig_health.add_trace(go.Scatter(x=df["Datetime"], y=df["Heart_Rate"], mode="lines", name="Пульс"))
fig_health.add_trace(go.Scatter(x=df["Datetime"], y=df["Blood_Pressure"], mode="lines", name="Давление"))
fig_health.update_layout(title="Пульс и давление во времени", xaxis_title="Дата", yaxis_title="Значение")

# 2.2. Гистограмма: "Распределение по пульсу"
fig_hist_pulse = px.histogram(df, x="Heart_Rate", nbins=20, title="Гистограмма по пульсу")

# =============================================================================
# 3. КАЛОРИИ
# =============================================================================
# 3.1. Линейный график: "Сожжённые калории по дням"
fig_calories = px.line(df, x="Datetime", y="Calories_Burned", title="Сожжённые калории по дням")

# 3.2. Диаграмма рассеяния: "Калории vs шаги"
fig_scatter = px.scatter(df, x="Steps", y="Calories_Burned", title="Калории vs шаги", trendline="ols")

# =============================================================================
# 4. СОН
# =============================================================================
# 4.1. Линейный график: "Продолжительность сна по дням"
fig_sleep_duration = px.line(df, x="Datetime", y="Sleep_Duration_hr", title="Продолжительность сна по дням")

# 4.2. Круговая диаграмма: "Качество сна"
sleep_quality_counts = df['Sleep_Quality'].value_counts().reset_index()
sleep_quality_counts.columns = ['Sleep_Quality', 'Количество']
fig_sleep_quality = px.pie(sleep_quality_counts, names='Sleep_Quality', values='Количество', title="Качество сна")

# 4.3. Корреляционная диаграмма: "Сон vs Пульс / Калории / Шаги"
corr_df = df[['Sleep_Duration_hr', 'Heart_Rate', 'Calories_Burned', 'Steps']].corr()
fig_corr = px.imshow(corr_df, text_auto=True, title="Корреляция: Сон vs Пульс / Калории / Шаги")

# =============================================================================
# 5. ГЕОГРАФИЯ
# =============================================================================
# 5.1. "Активность по городам" (суммарные шаги по локациям)
geo_steps = df.groupby("Location")["Steps"].sum().reset_index()
fig_geo = px.bar(geo_steps, x="Location", y="Steps", title="Активность по городам (суммарные шаги)")

# 5.2. Boxplot: "Качество сна по городам" (по часам сна)
fig_box = px.box(df, x="Location", y="Sleep_Duration_hr", title="Качество сна по городам (по часам сна)")

# =============================================================================
# 6. ИНТЕГРАЛЬНЫЕ МЕТРИКИ
# =============================================================================
# 6.1. Радар-график: "Индивидуальный профиль за день (средние значения)"
avg_metrics = {
    "Шаги": df["Steps"].mean(),
    "Сон (час)": df["Sleep_Duration_hr"].mean(),
    "Пульс": df["Heart_Rate"].mean(),
    "Калории": df["Calories_Burned"].mean(),
    "Дистанция": df["Distance_km"].mean()
}
categories = list(avg_metrics.keys())
values = list(avg_metrics.values())
values += values[:1]
categories += categories[:1]
fig_radar = go.Figure(data=go.Scatterpolar(
    r=values,
    theta=categories,
    fill='toself'
))
fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True)
    ),
    title="Индивидуальный профиль за день (средние значения)"
)

# 6.2. График "Wellness Score"
norm_columns = ["Steps", "Sleep_Duration_hr", "Heart_Rate", "Calories_Burned", "Distance_km"]
df_norm = df.copy()
for col in norm_columns:
    df_norm[col] = (df_norm[col] - df_norm[col].min()) / (df_norm[col].max() - df_norm[col].min())
df_norm["Wellness_Score"] = (df_norm["Steps"] * 0.2 +
                             df_norm["Sleep_Duration_hr"] * 0.2 +
                             df_norm["Heart_Rate"] * 0.2 +
                             df_norm["Calories_Burned"] * 0.2 +
                             df_norm["Distance_km"] * 0.2)
fig_wellness = px.line(df_norm, x="Datetime", y="Wellness_Score", title="Wellness Score")

# =============================================================================
# СБОРКА DASHBOARD
# =============================================================================
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Дашборд Health & Fitness", style={"textAlign": "center"}),
    dcc.Tabs([
        dcc.Tab(label="Активность", children=[
            html.Div([
                dcc.Graph(figure=fig_steps),
                dcc.Graph(figure=fig_distance)
            ])
        ]),
        dcc.Tab(label="Здоровье", children=[
            html.Div([
                dcc.Graph(figure=fig_health),
                dcc.Graph(figure=fig_hist_pulse)
            ])
        ]),
        dcc.Tab(label="Калории", children=[
            html.Div([
                dcc.Graph(figure=fig_calories),
                dcc.Graph(figure=fig_scatter)
            ])
        ]),
        dcc.Tab(label="Сон", children=[
            html.Div([
                dcc.Graph(figure=fig_sleep_duration),
                dcc.Graph(figure=fig_sleep_quality),
                dcc.Graph(figure=fig_corr)
            ])
        ]),
        dcc.Tab(label="География", children=[
            html.Div([
                dcc.Graph(figure=fig_geo),
                dcc.Graph(figure=fig_box)
            ])
        ]),
        dcc.Tab(label="Интегральные метрики", children=[
            html.Div([
                dcc.Graph(figure=fig_radar),
                dcc.Graph(figure=fig_wellness)
            ])
        ]),
    ])
])

if __name__ == '__main__':
    app.run(debug=True)
