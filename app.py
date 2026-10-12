import random
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Generatore Menù Settimanale", page_icon="🥗", layout="wide"
)

# 1. Inizializzazione dello State (database dei piatti di default)
if "database_piatti" not in st.session_state:
  st.session_state.database_piatti = {
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
    "Gestisci i tuoi piatti preferiti e genera un menù bilanciato per tutta la"
    " settimana con un solo clic!"
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
    if nuovo_piatto not in st.session_state.database_piatti[categoria_scelta]:
      st.session_state.database_piatti[categoria_scelta].append(
          nuovo_piatto.strip()
      )
      st.sidebar.success(f"Piatto '{nuovo_piatto}' aggiunto con successo!")
    else:
      st.sidebar.warning("Questo piatto esiste già in questa categoria.")

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
  # Controllo preliminare: verifica che ogni categoria abbia almeno un piatto
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
    # Crea il pool di categorie per i 14 pasti
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

  # Dividiamo i giorni in due colonne per una visualizzazione pulita
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
  
