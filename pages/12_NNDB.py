"""
Display some dead people stats
"""
import streamlit as st
import altair as alt
from utilities import check_password, get_user_name, load_snowflake_table

st.set_page_config(page_title="NNDB Stats", page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except KeyError:
    st.write("Please login again")


def run_query(conn, query):
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetch_pandas_all()
        return result


# Initialize connection.
conn = st.connection("snowflake")


df_nndb = load_snowflake_table(conn, "nndb")
df_nndb = df_nndb[df_nndb["AGE"] < 100]

df_nndb["IS_ALIVE"] = df_nndb["DIED"].isnull()
df_nndb["IS_DECEASED"] = df_nndb["DIED"].notnull()

df_nndb_dead = df_nndb[df_nndb["IS_DECEASED"]]

st.write(
    "Data from the Notable Names Database.  The following charts "
    "represent statistics on celebrities."
)

# c = (
#     alt.Chart(df_nndb).mark_bar().encode(
#         alt.X("AGE", bin=alt.Bin(maxbins=50)),
#         y='count()',
#     )
# )

# st.altair_chart(c, use_container_width=True)

c = (
    alt.Chart(df_nndb_dead)
    .mark_line()
    .encode(
        alt.X("AGE"),
        y="count()",
    )
)

st.altair_chart(c, use_container_width=True)

st.write(
    "Let's now look at summary statistics for people " 
    "in the database that are dead."
)

st.write(df_nndb["AGE"].describe())

df_nndb_occupation = df_nndb.dropna(subset=["OCCUPATION"])

# Count the number of alive and deceased individuals for each occupation
counts = (
    df_nndb_occupation.groupby("OCCUPATION")
    .agg({"IS_ALIVE": "sum", "IS_DECEASED": "sum"})
    .reset_index()
)

top_15_alive = counts.sort_values(by="IS_DECEASED", ascending=False).head(10)

# Melt the DataFrame to long format
long_format = top_15_alive.melt(
    id_vars="OCCUPATION",
    value_vars=["IS_ALIVE", "IS_DECEASED"],
    var_name="Status",
    value_name="Count",
)

# Create a side-by-side bar chart
chart = (
    alt.Chart(long_format)
    .mark_bar()
    .encode(
        x=alt.X("OCCUPATION", axis=alt.Axis(title="OCCUPATION")),
        y=alt.Y("Count", axis=alt.Axis(title="Count")),
        color="Status",
        column="Status",
    )
)

occupation_ratio = """
SELECT
    OCCUPATION,
    COUNT(CASE WHEN DIED IS NOT NULL THEN 1 END) AS DECEASED_COUNT,
    COUNT(CASE WHEN DIED IS NOT NULL THEN 1 END) /
    NULLIF(COUNT(CASE WHEN DIED IS NULL THEN 1 END), 0) as RATIO
FROM deadpool.prod.nndb
WHERE occupation is not null
GROUP BY 1
ORDER by 2 desc
limit 15
"""
df = run_query(conn, occupation_ratio)
df["RATIO"] = df["RATIO"].astype(float)

st.write(df.sort_values(by="RATIO", ascending=False))

st.bar_chart(data=df, x="OCCUPATION", y="RATIO", color="#F28749")
