import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import datetime
import time
import pandas as pd

# ============================================================
# 🔐 Conexión a MongoDB Atlas (DIRECTO - SIN SECRETS)
# ============================================================
st.set_page_config(page_title="Pomodoro Dashboard", layout="centered")

# ⚠️ REEMPLAZA CON TUS CREDENCIALES REALES
MONGO_USERNAME = "elefante123"  # 👈 Cambia esto
MONGO_PASSWORD = "elefante123"  # 👈 Cambia esto
MONGO_CLUSTER = "cluster0.le4sexx.mongodb.net"
MONGO_DATABASE = "pomodoro_db"

# Construcción de la URI
MONGO_URI = f"mongodb+srv://elefante123:elefante123@cluster0.le4sexx.mongodb.net/"

# Función para conectar a MongoDB con manejo de errores
@st.cache_resource
def init_connection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test de conexión
        client.admin.command('ping')
        st.sidebar.success("✅ Conectado a MongoDB")
        return client
    except ConnectionFailure:
        st.error("❌ Error de conexión a MongoDB. Verifica tu conexión a internet.")
        return None
    except OperationFailure as e:
        st.error(f"❌ Error de autenticación: {str(e)}")
        st.info("Verifica:\n- Usuario y contraseña correctos\n- IP whitelist configurada (0.0.0.0/0)\n- Permisos del usuario")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return None

client = init_connection()

if client is None:
    st.stop()

db = client[MONGO_DATABASE]
collection = db["sessions"]

# ============================================================
# ⏱ Funciones CRUD
# ============================================================

def create_session(task_name, duration, status="En curso"):
    try:
        session = {
            "task_name": task_name,
            "duration": duration,
            "status": status,
            "start_time": datetime.datetime.now(),
        }
        collection.insert_one(session)
        st.success(f"✅ Sesión '{task_name}' creada exitosamente.")
    except Exception as e:
        st.error(f"❌ Error al crear sesión: {str(e)}")

def read_sessions():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al leer sesiones: {str(e)}")
        return pd.DataFrame()

def update_session(task_name, new_status):
    try:
        result = collection.update_one({"task_name": task_name}, {"$set": {"status": new_status}})
        if result.modified_count > 0:
            st.success(f"🔁 Estado de '{task_name}' actualizado a '{new_status}'.")
        else:
            st.warning("⚠️ No se encontró la tarea.")
    except Exception as e:
        st.error(f"❌ Error al actualizar: {str(e)}")

def delete_session(task_name):
    try:
        result = collection.delete_one({"task_name": task_name})
        if result.deleted_count > 0:
            st.success(f"🗑️ Tarea '{task_name}' eliminada.")
        else:
            st.warning("⚠️ No se encontró la tarea.")
    except Exception as e:
        st.error(f"❌ Error al eliminar: {str(e)}")

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
        if task_name.strip():
            create_session(task_name, duration)
        else:
            st.warning("⚠️ Por favor ingresa un nombre de tarea válido.")

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
        if task_name.strip():
            update_session(task_name, new_status)
        else:
            st.warning("⚠️ Por favor ingresa un nombre de tarea.")

# ============================================================
# 🗑️ Eliminar
# ============================================================
elif choice == "Eliminar Sesión":
    task_name = st.text_input("❌ Nombre de la tarea a eliminar:")
    if st.button("Eliminar"):
        if task_name.strip():
            delete_session(task_name)
        else:
            st.warning("⚠️ Por favor ingresa un nombre de tarea.")

# ============================================================
# ⏰ Pomodoro Timer
# ============================================================
elif choice == "Pomodoro Timer":
    st.subheader("🍅 Técnica Pomodoro")
    task = st.text_input("Tarea actual:")
    work_time = st.number_input("Duración trabajo (min):", 1, 60, 25)
    break_time = st.number_input("Duración descanso (min):", 1, 15, 5)

    if st.button("Iniciar Pomodoro"):
        if not task.strip():
            st.warning("⚠️ Por favor ingresa un nombre de tarea.")
        else:
            st.write(f"Iniciando tarea: **{task}**")
            placeholder = st.empty()
            
            # Fase de trabajo
            for sec in range(work_time * 60, 0, -1):
                mins, secs = divmod(sec, 60)
                placeholder.metric("Tiempo restante de trabajo", f"{mins:02d}:{secs:02d}")
                time.sleep(1)
            
            st.success("🎉 ¡Tiempo de descanso!")
            
            # Fase de descanso
            for sec in range(break_time * 60, 0, -1):
                mins, secs = divmod(sec, 60)
                placeholder.metric("Tiempo de descanso", f"{mins:02d}:{secs:02d}")
                time.sleep(1)
            
            st.info("✅ Ciclo Pomodoro finalizado.")
            create_session(task, work_time, status="Completado")

