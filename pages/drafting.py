import streamlit as st

conn = st.connection("snowflake")

df = conn.query(
    """select
        concat(first_name || ' ' || left(last_name, 1) || '.') as PLAYER, EMAIL 
    from PLAYERS
    order by 1
    """,
    ttl=600,
)

players = df["PLAYER"].tolist()

submitter = st.radio("Please choose your name", players, index=None)


st.subheader("Draft Picks:")
with st.form("Draft Picks"):
    pick = st.text_input("Please choose your celebritic pick:", "")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Draft Pick:", pick)

        # Filter the DataFrame
        filtered_df = df[df['PLAYER'] == submitter]

        # Check if the filtered DataFrame is empty
        if not filtered_df.empty:
            email = filtered_df['EMAIL'].iloc[0]
        else:
            print(f"No email found for {submitter}")
        
        write_query = f"INSERT INTO picks (name, picked_by) VALUES ('{pick}', '{email}')"
        
        st.write(write_query)

        conn.cursor().execute(write_query)