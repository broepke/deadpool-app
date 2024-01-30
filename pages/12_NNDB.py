"""
Display some dead people stats
"""
import streamlit as st
import altair as alt
from dp_utilities import check_password
from dp_utilities import load_snowflake_table
from dp_utilities import run_snowflake_query
from dp_utilities import snowflake_connection_helper

st.set_page_config(page_title="NNDB Stats", page_icon=":skull:")

st.title("NNDB :skull_and_crossbones:")

email, user_name, authenticated = check_password()
if authenticated:

    # Initialize connection.
    conn = snowflake_connection_helper()

    df_nndb = load_snowflake_table(conn, "nndb")
    df_nndb = df_nndb[df_nndb["AGE"] < 100]

    df_nndb["IS_ALIVE"] = df_nndb["DEATH_DATE"].isnull()
    df_nndb["IS_DECEASED"] = df_nndb["DEATH_DATE"].notnull()

    df_nndb_dead = df_nndb[df_nndb["IS_DECEASED"]]

    st.subheader("Number of People Who are Dead by Age")
    st.write(
        "Data from the Notable Names Database.  The following charts "
        "represent statistics on celebrities."
    )

    age_line_chart = (
        alt.Chart(df_nndb_dead)
        .mark_line()
        .encode(alt.X("AGE"), y="count()", color=alt.value("#F63366"))
    )

    st.altair_chart(age_line_chart, use_container_width=True)

    ###########################
    # DESCRIPTIVE STATISTICS
    ###########################
    st.subheader("Descriptive Statistics on Age")
    st.dataframe(df_nndb_dead["AGE"].describe(), use_container_width=True)

    ###########################
    # OCCUPATION DATA
    ###########################
    occupation_ratio = """
    SELECT
        OCCUPATION,
        COUNT(CASE WHEN DEATH_DATE IS NOT NULL THEN 1 END) AS DECEASED_COUNT,
        COUNT(CASE WHEN DEATH_DATE IS NOT NULL THEN 1 END) /
        NULLIF(COUNT(CASE WHEN DEATH_DATE IS NULL THEN 1 END), 0) AS RATIO
    FROM DEADPOOL.PROD.NNDB
    WHERE OCCUPATION IS NOT NULL
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 15
    """
    df_occupation = run_snowflake_query(conn, occupation_ratio)
    df_occupation["RATIO"] = df_occupation["RATIO"].astype(float)
    df_occupation = df_occupation.sort_values(by="RATIO", ascending=False)

    st.subheader("Occupations: Most Alive/Dead Ratio in the DB")
    occupation_chart = (
        alt.Chart(df_occupation)
        .mark_bar()
        .encode(
            x="RATIO:Q",
            y=alt.Y("OCCUPATION:N", sort=None),
            color=alt.value("#F63366"),
        )
    )

    st.altair_chart(occupation_chart, use_container_width=True)

    ###########################
    # RISK FACTORS
    ###########################
    risk_factors = """
    SELECT NAME, RISK_FACTORS, AGE
    FROM DEADPOOL.PROD.NNDB
    WHERE RISK_FACTORS IS NOT NULL
    AND DEATH_DATE IS NULL
    AND AGE IS NOT NULL
    AND AGE < 101
    GROUP BY 1, 2, 3
    ORDER BY 3 DESC
    LIMIT 200
    """
    df_risk = run_snowflake_query(conn, risk_factors)
    st.subheader("High Risk People by Age")
    st.dataframe(df_risk, use_container_width=True)

    ###########################
    # PREDICTION MODEL
    ###########################
    df_nndb_preds = load_snowflake_table(conn, "nndb_predictions")

    st.subheader("The Aribiter's Picks for 2024 are as follows.")

    df_nndb_preds.drop(columns=["ID", "IS_DECEASED"], inplace=True)
    df_nndb_preds = (
        df_nndb_preds.sort_values("PREDICTION", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    st.dataframe(df_nndb_preds, use_container_width=True)
