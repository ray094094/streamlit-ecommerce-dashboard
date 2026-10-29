# --- 1 Импорт библиотек ---
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Заголовок приложения
st.title("Анализ данных интернет-магазина")

# --- 2 Загрузка данных ---
@st.cache_data
def load_data():
    orders = pd.read_csv("/content/project/orders.csv")
    items = pd.read_csv("/content/project/items.csv")
    users = pd.read_csv("/content/project/users.csv")
    return orders, items, users

orders, items, users = load_data()

# --- 3 Объединение таблиц ---
df = orders.merge(users, on="user_id", how="left")
df = df.merge(items, on="item_id", how="left")

# --- 4. Очистка данных ---
df["order_date"] = pd.to_datetime(df["order_date"])
df["registration_date"] = pd.to_datetime(df["registration_date"])

# РАСЧЕТ total_price СРАЗУ ДЛЯ ВСЕГО ДАТАСЕТА (решает KeyError)
df["total_price"] = df["quantity"] * df["price_per_unit"]

# --- 5.1 Сырые данные ---
selected_category = st.selectbox(
    "Выберите категорию товара:", 
    options=df["category"].dropna().unique()
)

filtered_df = df[df["category"] == selected_category]

st.write(f"Найдено записей: {len(filtered_df)}")
st.dataframe(filtered_df)

# --- 5.2 Ключевые показатели ---
st.subheader("Ключевые показатели")

total_orders = filtered_df["order_id"].nunique()
total_revenue = filtered_df[filtered_df["category"] == selected_category]["total_price"].sum()
unique_users = filtered_df["user_id"].nunique()
avg_check = total_revenue / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Всего заказов", total_orders)
col2.metric("Общая выручка", f"{total_revenue:,.2f} ₽")
col3.metric("Уник. пользователей", unique_users)
col4.metric("Средний чек", f"{avg_check:,.2f} ₽")

# --- 5.3 Визуализация ---
st.subheader("Визуализация данных")

# График 1: Топ-10 товаров по выручке
st.markdown("### Топ-10 товаров по выручке")
top_items = filtered_df.groupby("item_name")["total_price"].sum().nlargest(10).sort_values()

fig1, ax1 = plt.subplots(figsize=(8, 4))
top_items.plot(kind="barh", ax=ax1, color="skyblue")
ax1.set_xlabel("Выручка")
ax1.set_ylabel("Товар")
st.pyplot(fig1)

# График 2: Выручка по категориям товаров (по ВСЕМУ датафрейму)
st.markdown("### Доля категорий в выручке (по всему магазину)")
category_revenue_all = df.groupby("category")["total_price"].sum()

fig2, ax2 = plt.subplots(figsize=(6, 6))
category_revenue_all.plot(kind="pie", ax=ax2, autopct="%1.1f%%", startangle=90)
ax2.set_ylabel("")
st.pyplot(fig2)

# График 3: Зависимость количества заказов от дня недели
st.markdown("### Количество заказов по дням недели")
filtered_df_copy = filtered_df.copy()
filtered_df_copy["order_day"] = filtered_df_copy["order_date"].dt.day_name()
orders_by_day = filtered_df_copy.groupby("order_day")["order_id"].nunique()

fig3, ax3 = plt.subplots(figsize=(8, 4))
orders_by_day.plot(kind="bar", ax=ax3, color="orange")
ax3.set_xlabel("День недели")
ax3.set_ylabel("Количество заказов")
plt.xticks(rotation=45)
st.pyplot(fig3)

# --- 5.4 Аналитические выводы ---
st.subheader("💡 Аналитические выводы")
st.markdown("""
- **Лидеры продаж:** Основной объем выручки формируют высокочековые технологичные товары. Первое место уверенно занимает *Ноутбук ASUS VivoBook*, за ним следуют *Apple Watch* и *PlayStation*. Бюджетные позиции (например, фитнес-браслеты) вносят минимальный вклад в общий оборот.
- **Структура категорий товаров:** Безоговорочным лидером среди товарных категорий является **Электроника**, на которую приходится более половины всей выручки (54.6%). Вторую и третью позиции по доле занимают *Бытовая техника* (11.2%) и *Одежда* (9.0%), что определяет ключевые фокусные направления для ассортиментной политики.
- **Динамика покупательской активности:** Анализ заказов по дням недели выявил ярко выраженный пик спроса в **четверг** (достигающий пика в 6 заказов), а также повышенную активность в пятницу. Полученные данные позволяют оптимизировать логистику, рекламные кампании и график работы службы поддержки с учетом недельных паттернов.
""")
