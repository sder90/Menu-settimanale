import json
import os
import random
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Generatore Menù Settimanale", page_icon="🥗", layout="wide"
)

# Nome del file in cui salveremo i piatti permanentemente
DB_FILE = "piatti_db.json"

# Database di default iniziale
database_default = {
    "Legumi": [
        "Pasta e ceci",
        "Zuppa di lenticchie",
        "Insalata di fagioli e farro",
        "Burger di lenticchie con contorno",
    ],
    "Pesce": [
        "Salmone al forno con patate",
        "Merluzzo al vapore con bieta",
        "Spaghetti alle vongole",
        "Trancio di pesce spada alla griglia",
    ],
    "Carne Bianca": [
        "Petto di pollo ai ferri con insalata",
        "Tacchino al limone",
        "Coniglio al forno con rosmarino",
    ],
    "Uova": [
        "Frittata alle zucchine",
        "Uova strapazzate con pomodori",
        "Uova sode con verdure grigliate",
    ],
    "Formaggi": [
        "Caprese con mozzarella fior di latte",
        "Ricotta fresca con spinaci",
        "Insalata con feta e cetrioli",
    ],
    "Carne Rossa": ["Tagliata di manzo con rucola", "Polpette al sugo"],
}


# Funzioni per caricare e salvare il database su file JSON
def carica_database():
  if os.path.exists(DB_FILE):
    try:
      with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return database_default
  return database_default


def salva_database(db):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=4)


# Inizializzazione dello State con il database persistente
if "database_piatti" not in st.session_state:
  st.session_state.database_piatti = carica_database()

# Target di frequenza settimanale OMS (14 pasti totali)
frequenze_target = {
    "Legumi": 4,
    "Pesce": 3,
    "Carne Bianca": 2,
    "Uova": 2,
    "Formaggi": 2,
    "Carne Rossa": 1,
}

st.title("🥗 Generatore Menù Settimanale (Linee Guida OMS)")
st.write(
    "Gestisci i tuoi piatti preferiti: le modifiche verranno salvate in modo"
    " permanente!"
)

# --- SIDEBAR: GESTIONE PIATTI ---
st.sidebar.header("🍳 Gestione Database Piatti")

# Aggiungi nuovo piatto
with st.sidebar.form("form_aggiungi_piatto"):
  st.subheader("Aggiungi un piatto")
  nuovo_piatto = st.text_input("Nome del piatto")
  categoria_scelta = st.selectbox(
      "Categoria", list(st.session_state.database_piatti.keys())
  )
  submit_aggiungi = st.form_submit_button("Aggiungi al Database")

  if submit_aggiungi and nuovo_piatto.strip():
    piatto_pulito = nuovo_piatto.strip()
    if (
        piatto_pulito
        not in st.session_state.database_piatti[categoria_scelta]
    ):
      st.session_state.database_piatti[categoria_scelta].append(piatto_pulito)
      salva_database(st.session_state.database_piatti)  # Salvataggio su file
      st.sidebar.success(f"Piatto '{piatto_pulito}' aggiunto e salvato!")
    else:
      st.sidebar.warning("Questo piatto esiste già in questa categoria.")

# --- Rimuovi piatto esistente (Senza form per aggiornamento in tempo reale) ---
st.sidebar.subheader("Rimuovi un piatto")

# 1. Seleziona la categoria
cat_rimuovi = st.sidebar.selectbox(
    "Categoria da cui eliminare",
    list(st.session_state.database_piatti.keys()),
    key="cat_rim",
)

# 2. Preleva i piatti aggiornati di quella categoria
piatti_disponibili = st.session_state.database_piatti[cat_rimuovi]

if piatti_disponibili:
  # 3. Seleziona il piatto da eliminare
  piatto_da_rimuovere = st.sidebar.selectbox(
      "Seleziona piatto", piatti_disponibili, key="piatto_rim"
  )

  # 4. Pulsante diretto per eliminare (senza form)
  if st.sidebar.button("Elimina Piatto Selezionato", key="btn_elimina"):
    st.session_state.database_piatti[cat_rimuovi].remove(piatto_da_rimuovere)
    salva_database(st.session_state.database_piatti)  # Aggiornamento su file
    st.sidebar.success(f"Piatto '{piatto_da_rimuovere}' rimosso!")
    st.rerun()  # Ricarica immediatamente la pagina per aggiornare le liste
else:
  st.sidebar.text("Nessun piatto in questa categoria.")

# Mostra i piatti attuali divisi per categoria nella sidebar
with st.sidebar.expander("Visualizza piatti esistenti"):
  for cat, piatti in st.session_state.database_piatti.items():
    st.markdown(f"**{cat}** ({len(piatti)} piatti)")
    for p in piatti:
      st.text(f"- {p}")


# --- CORPO PRINCIPALE: GENERATORE MENU ---
st.divider()

if st.button(
    "🎲 Genera / Rigenera Menù Settimanale",
    type="primary",
    use_container_width=True,
):
  categorie_vuote = [
      cat for cat, piatti in st.session_state.database_piatti.items() if not piatti
  ]
  if categorie_vuote:
    st.error(
        "Attenzione! Le seguenti categorie non hanno piatti inseriti: "
        f"{', '.join(categorie_vuote)}. Aggiungi almeno un piatto per"
        " procedere."
    )
  else:
    pool_categorie = []
    for cat, freq in frequenze_target.items():
      pool_categorie.extend([cat] * freq)

    random.shuffle(pool_categorie)

    giorni = [
        "Lunedì",
        "Martedì",
        "Mercoledì",
        "Giovedì",
        "Venerdì",
        "Sabato",
        "Domenica",
    ]
    menu = {}

    pasto_idx = 0
    for giorno in giorni:
      cat_pranzo = pool_categorie[pasto_idx]
      cat_cena = pool_categorie[pasto_idx + 1]
      pasto_idx += 2

      piatto_pranzo = random.choice(st.session_state.database_piatti[cat_pranzo])
      piatto_cena = random.choice(st.session_state.database_piatti[cat_cena])

      menu[giorno] = {
          "Pranzo": {"piatto": piatto_pranzo, "categoria": cat_pranzo},
          "Cena": {"piatto": piatto_cena, "categoria": cat_cena},
      }

    st.session_state.menu_corrente = menu

# Visualizzazione del menù se esiste nella sessione
if "menu_corrente" in st.session_state:
  st.subheader("📅 Il tuo Menù della Settimana")

  giorni = list(st.session_state.menu_corrente.keys())
  col1, col2 = st.columns(2)

  for idx, giorno in enumerate(giorni):
    container = col1 if idx < 4 else col2
    with container:
      with st.container(border=True):
        st.markdown(f"### {giorno}")
        pasti = st.session_state.menu_corrente[giorno]
        st.markdown(
            f"☀️ **Pranzo:** {pasti['Pranzo']['piatto']}  \n`[{pasti['Pranzo']['categoria']}]`"
        )
        st.markdown(
            f"🌙 **Cena:** {pasti['Cena']['piatto']}  \n`[{pasti['Cena']['categoria']}]`"
        )
else:
  st.info(
      "Clicca sul pulsante qui sopra per generare il tuo primo menù settimanale"
      " basato sulle tue preferenze e sulle frequenze OMS!"
  )
