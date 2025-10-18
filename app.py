import streamlit as st
from pymongo import MongoClient
import datetime
import time
import pandas as pd

# ============================================================
# 🔐 Conexión a MongoDB Atlas
# ============================================================
st.set_page_config(page_title="Pomodoro Dashboard", layout="centered")

# Cargar secretos desde Streamlit (secrets.toml)
mongo_uri = st.secrets["mongodb"]["uri"]
client = MongoClient(mongo_uri)
db = client["pomodoro_db"]
collection = db["sessions"]

# ============================================================
# ⏱ Funciones CRUD
# ============================================================

def create_session(task_name, duration, status="En curso"):
    session = {
        "task_name": task_name,
        "duration": duration,
        "status": status,
        "start_time": datetime.datetime.now(),
    }
    collection.insert_one(session)
    st.success(f"✅ Sesión '{task_name}' creada exitosamente.")

def read_sessions():
    data = list(collection.find({}, {"_id": 0}))
    return pd.DataFrame(data) if data else pd.DataFrame()

def update_session(task_name, new_status):
    result = collection.update_one({"task_name": task_name}, {"$set": {"status": new_status}})
    if result.modified_count > 0:
        st.success(f"🔁 Estado de '{task_name}' actualizado a '{new_status}'.")
    else:
        st.warning("⚠️ No se encontró la tarea.")

def delete_session(task_name):
    result = collection.delete_one({"task_name": task_name})
    if result.deleted_count > 0:
        st.success(f"🗑️ Tarea '{task_name}' eliminada.")
    else:
        st.warning("⚠️ No se encontró la tarea.")

# ============================================================
# 🎨 Interfaz Streamlit
# ============================================================

st.title("🍅 Pomodoro Dashboard – Control de Tiempo")
st.markdown("Un panel simple con conexión a MongoDB Atlas.")

menu = ["Registrar Sesión", "Ver Sesiones", "Actualizar Estado", "Eliminar Sesión", "Pomodoro Timer"]
choice = st.sidebar.selectbox("📋 Menú", menu)

# ============================================================
# 🧾 Crear
# ============================================================
if choice == "Registrar Sesión":
    task_name = st.text_input("🧠 Nombre de la tarea:")
    duration = st.number_input("⏳ Duración (minutos):", min_value=1, max_value=120, value=25)
    if st.button("Iniciar Sesión"):
        create_session(task_name, duration)

# ============================================================
# 📖 Leer
# ============================================================
elif choice == "Ver Sesiones":
    st.subheader("📊 Historial de Sesiones")
    df = read_sessions()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No hay sesiones registradas aún.")

# ============================================================
# ✏️ Actualizar
# ============================================================
elif choice == "Actualizar Estado":
    task_name = st.text_input("🔍 Nombre de la tarea:")
    new_status = st.selectbox("Nuevo estado:", ["En curso", "Completado", "Pausado"])
    if st.button("Actualizar"):
        update_session(task_name, new_status)

# ============================================================
# 🗑️ Eliminar
# ============================================================
elif choice == "Eliminar Sesión":
    task_name = st.text_input("❌ Nombre de la tarea a eliminar:")
    if st.button("Eliminar"):
        delete_session(task_name)

# ============================================================
# ⏰ Pomodoro Timer
# ============================================================
elif choice == "Pomodoro Timer":
    st.subheader("🍅 Técnica Pomodoro")
    task = st.text_input("Tarea actual:")
    work_time = st.number_input("Duración trabajo (min):", 1, 60, 25)
    break_time = st.number_input("Duración descanso (min):", 1, 15, 5)

    if st.button("Iniciar Pomodoro"):
        st.write(f"Iniciando tarea: **{task}**")
        with st.empty():
            for sec in range(work_time * 60, 0, -1):
                mins, secs = divmod(sec, 60)
                st.metric("Tiempo restante de trabajo", f"{mins:02d}:{secs:02d}")
                time.sleep(1)
        st.success("🎉 ¡Tiempo de descanso!")
        time.sleep(break_time * 60)
        st.info("✅ Ciclo Pomodoro finalizado.")
        create_session(task, work_time, status="Completado")
