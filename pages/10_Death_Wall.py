import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from dp_utilities import (
    check_password,
    load_snowflake_table,
    snowflake_connection_helper,
)
from functools import lru_cache

st.set_page_config(page_title="Death Wall", page_icon=":skull:")
st.title("Death Wall :skull_and_crossbones:")

email, user_name, authenticator, config, authenticated = check_password()


@lru_cache(maxsize=100)
def query_wikidata_by_id(wiki_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?personLabel ?birthDate ?deathDate ?image ?description
    WHERE {{
      wd:{wiki_id} wdt:P569 ?birthDate.
      wd:{wiki_id} wdt:P570 ?deathDate.
      OPTIONAL {{ wd:{wiki_id} wdt:P18 ?image. }}
      OPTIONAL {{ wd:{wiki_id} schema:description ?description. FILTER(LANG(?description) = "en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def format_date(date_str):
    """Format the date string from full datetime to YYYY-MM-DD."""
    return date_str.split("T")[0] if "T" in date_str else date_str


def display_person_info(row, data):
    if data:
        person = data[0]
        birth_date = format_date(person.get("birthDate", {}).get("value", "Unknown"))
        death_date = format_date(person.get("deathDate", {}).get("value", "Unknown"))
        image_url = person.get("image", {}).get("value")
        description = person.get("description", {}).get("value", "")

        st.subheader(row["NAME"])
        st.write(f"Born: {birth_date} - Died: {death_date}")
        st.write(description)
        if image_url:
            st.image(image_url, width=200)
    else:
        st.write(f"Could not find data for {row['NAME']}.")


def load_data():
    conn = snowflake_connection_helper()
    df = load_snowflake_table(conn, "picks")
    df_dead = df.loc[df["DEATH_DATE"].notnull() & (df["YEAR"] == 2024)].sort_values(
        by="DEATH_DATE", ascending=False
    )
    return df_dead


if authenticated:
    df_dead = load_data()

    # Add a search box
    search_term = st.text_input("Search for a person")
    if search_term:
        df_dead = df_dead[
            df_dead["NAME"].str.contains(search_term, case=False, na=False)
        ]

    # Add pagination
    items_per_page = 10
    page_number = st.number_input("Page", min_value=1, value=1)
    start_idx = (page_number - 1) * items_per_page
    end_idx = start_idx + items_per_page

    df_page = df_dead.iloc[start_idx:end_idx]

    col1, col2 = st.columns(2)

    for i, row in df_page.iterrows():
        data = query_wikidata_by_id(row["WIKI_ID"])
        if i % 2 == 0:
            with col1:
                display_person_info(row, data)
        else:
            with col2:
                display_person_info(row, data)

    st.write(
        f"Showing {start_idx + 1}-{min(end_idx, len(df_dead))} of {len(df_dead)} results"
    )
