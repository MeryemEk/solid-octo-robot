from logzero import logger

import pandas as pd
import streamlit as st

import data_munging
import plot_migration

padding = 0
st.set_page_config(page_title="TAFRA SMIG DATA", layout="wide", page_icon="📍")

st.markdown(
    """
    <style>
    .small-font {
        font-size:12px;
        font-style: italic;
        color: #b1a7a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

from data_munging import ALL_STATES_TITLE

TABLE_PAGE_LEN = 10

state_coordinates = data_munging.get_coordinates()
state_migration = pd.read_csv("data/state_migration.csv")
state_summary = pd.read_csv("data/state_migration_summary.csv")

st.title("State Movement")
state_choices = list(state_coordinates["name"])
state_choices.insert(0, ALL_STATES_TITLE)


with st.sidebar.form(key="my_form"):
    selectbox_state = st.selectbox("Choose a state", state_choices)
    selectbox_direction = st.selectbox("Choose a direction", ["Incoming", "Outgoing"])
    numberinput_threshold = st.number_input(
        """Set top N Migration per state""",
        value=3,
        min_value=1,
        max_value=25,
        step=1,
        format="%i",
    )
    st.markdown(
        '<p class="small-font">Results Limited to top 5 per State in overall US</p>',
        unsafe_allow_html=True,
    )
    pressed = st.form_submit_button("Build Migration Map")

expander = st.sidebar.expander("Qu'est ce que l'indice SMIG DATA")
expander.write(
    """
L'indice SMIG DATA a été développé par TAFRA pour évaluer la conformité des communes marocaines au Droit d'Accès à l'Information.
"""
)

# mig1 = plot_migration.build_migration_chart(G)
# mig_plot = st.plotly_chart(mig1)

network_place, _, descriptor = st.columns([6, 1, 3])

network_loc = network_place.empty()

# Create starting graph

descriptor.subheader(data_munging.display_state(selectbox_state))
descriptor.write(data_munging.display_state_summary(selectbox_state, state_summary))


edges = data_munging.compute_edges(
    state_migration,
    threshold=numberinput_threshold,
    state=ALL_STATES_TITLE,
    direction=selectbox_direction,
)


nodes = data_munging.compute_nodes(
    state_coordinates, edges, direction=selectbox_direction
)
G = data_munging.build_network(nodes, edges)
logger.info("Graph Created, doing app stuff")

migration_plot = plot_migration.build_migration_chart(G, selectbox_direction)
network_loc.plotly_chart(migration_plot)

st.write(
    """
    Hope you like the map!
    """
)

st.header("Migration Table")
table_loc = st.empty()
clean_edges = data_munging.table_edges(edges, selectbox_direction)
table_loc.table(clean_edges.head(20))

if pressed:
    edges = data_munging.compute_edges(
        state_migration,
        threshold=numberinput_threshold,
        state=selectbox_state,
        direction=selectbox_direction,
    )

    nodes = data_munging.compute_nodes(
        state_coordinates, edges, direction=selectbox_direction
    )
    # st.table(nodes[["name", "latitude", "Migration"]].head(10))
    G = data_munging.build_network(nodes, edges)
    # st.table(G.edges)
    migration_plot = plot_migration.build_migration_chart(G, selectbox_direction)
    network_loc.plotly_chart(migration_plot)

    clean_edges = data_munging.table_edges(edges, selectbox_direction)
    table_loc.table(clean_edges.head(20))
