import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from dp_utilities import check_password
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper

st.set_page_config(page_title="Death Wall", page_icon=":skull:")
st.title("Death Wall :skull_and_crossbones:")

email, user_name, authenticated = check_password()

def query_wikidata_by_id(wiki_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?personLabel ?birthDate ?deathDate ?image
    WHERE {{
      wd:{wiki_id} wdt:P569 ?birthDate.
      wd:{wiki_id} wdt:P570 ?deathDate.
      OPTIONAL {{ wd:{wiki_id} wdt:P18 ?image. }}
    }}
    LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

def format_date(date_str):
    """Format the date string from full datetime to YYYY-MM-DD."""
    if "T" in date_str:
        return date_str.split("T")[0]
    return date_str

def display_person_info_from_df(row):
    wiki_id = row['WIKI_ID']
    name = row['NAME']
    data = query_wikidata_by_id(wiki_id)
    
    if data:
        person = data[0]
        birth_date = format_date(person.get("birthDate", {}).get("value", "Unknown"))
        death_date = format_date(person.get("deathDate", {}).get("value", "Unknown"))
        image_url = person.get("image", {}).get("value", None)

        st.subheader(name)
        st.write(f"Born: {birth_date} - Died: {death_date}")
        if image_url:
            st.image(image_url)
    else:
        st.write(f"Could not find data for {name}.")

if authenticated:
    
    # Initialize connection and get all the dead people.
    conn = snowflake_connection_helper()
    df = load_snowflake_table(conn, "picks")
    df_dead = df.loc[df["DEATH_DATE"].notnull() & (df['YEAR'] == 2024)]
    
    # Load the dead people from 2024 in the dataframe
    col1, col2 = st.columns(2)
    
    # Loop through the dataframe and display the info
    for i, row in df_dead.iterrows():
        if i % 2 == 0:
            with col1:
                display_person_info_from_df(row)
        else:
            with col2:
                display_person_info_from_df(row)