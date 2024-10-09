import pandas as pd


def convert_to_pg_array(df, column):
    df[column] = df[column].apply(
        lambda x: (
            x.replace("[", "{").replace("]", "}").replace("'", '"')
            if pd.notna(x)
            else None
        )
    )
    return df


def convert_to_timestamp(df, datetime_columns=None):
    """
    Convert specified datetime columns or automatically detect datetime-like columns in a DataFrame
    and convert them to Unix timestamps. Renames the columns by replacing 'datetime' with 'timestamp'.
    Handles missing data gracefully.

    Parameters:
    df (pd.DataFrame): DataFrame with potential datetime columns.
    datetime_columns (list): List of column names to be converted. If None, the function will
                             automatically detect columns with 'date' or 'datetime' in their name.

    Returns:
    pd.DataFrame: DataFrame with specified columns converted to Unix timestamps and renamed.
    """

    # If no datetime columns specified, automatically find them based on the name
    if datetime_columns is None:
        datetime_columns = [col for col in df.columns if "datetime" in col.lower()]

    # Convert the columns to Unix timestamps and handle missing data
    for col in datetime_columns:
        if col in df.columns:
            # Convert to datetime, forcing errors to NaT (missing datetime)
            # df[col] = pd.to_datetime(df[col], errors="coerce")

            # # Convert datetime to Unix timestamp (handle missing values)
            # df[col] = df[col].apply(
            #     lambda x: int(x.timestamp()) if pd.notnull(x) else None
            # )
            # df[col] = df[col].astype("Int64")

            # Rename the column
            new_col_name = col.replace("datetime", "timestamp")
            df.rename(columns={col: new_col_name}, inplace=True)

    return df


contact_type_mapping = {
    "github": 1,
    "email": 2,
    "phone": 3,
    "linkedin": 4,
    "facebook": 5,
}

post_type_mapping = {
    "event": 1,
    "story": 2,
    "job": 3,
    "mentorship": 4,
    "showcase": 5,
    "donation_campaign": 6,
    "announcement": 7,
    "discussion": 8,
    "survey": 9,
}

# Create a dataframe for ContactType
contact_type_df = pd.DataFrame(
    list(contact_type_mapping.items()), columns=["text", "id"]
)

contact_type_df = contact_type_df[["id", "text"]]

post_type_df = pd.DataFrame(list(post_type_mapping.items()), columns=["text", "id"])
post_type_df = post_type_df[["id", "text"]]

# Load the CSV
user_df = pd.read_csv("./neo4j/alumni_user.csv")

workplace_df = user_df[["user_id", "company", "workplace", "job"]].copy()
workplace_df.columns = ["user_id", "company", "address", "job"]
workplace_df["type"] = "workplace"

internship_df = user_df[
    ["user_id", "company_internship", "internship", "job_internship"]
].copy()
internship_df.columns = ["user_id", "company", "address", "job"]
internship_df["type"] = "internship"

company_df = pd.concat([workplace_df, internship_df], ignore_index=True)

contact_df = user_df.melt(
    id_vars=["user_id"],
    value_vars=["github", "email", "phone", "linkedin", "facebook"],
    var_name="contact_type",
    value_name="text",
)

contact_df = contact_df[
    contact_df["text"].notna() & (contact_df["text"] != "")
].reset_index(drop=True)

contact_df["contact_type"] = contact_df["contact_type"].map(contact_type_mapping)

# Rename columns to match the PostgreSQL table
user_df.rename(
    columns={
        "user_id": "id",
        "graduate_year": "graduation_year",
    },
    inplace=True,
)


# Remove columns that don't exist in the table
user_df = user_df.drop(
    columns=[
        "user_interaction",
        "workplace",
        "company",
        "job",
        "company_internship",
        "internship",
        "job_internship",
        "github",
        "email",
        "phone",
        "linkedin",
        "facebook",
    ]
)

user_post_df = pd.read_csv("./neo4j/user_post.csv")
user_post_df.rename(
    columns={"post_id": "id", "media_url": "media_location", "content": "text"},
    inplace=True,
)
user_post_df["post_type"] = user_post_df["post_type"].map(post_type_mapping)
user_post_df = convert_to_timestamp(user_post_df)
user_post_df = convert_to_pg_array(user_post_df, "media_location")


user_message_df = pd.read_csv("./neo4j/user_interactions.csv")
user_message_df.rename(
    columns={
        "message_id": "id",
        "sender_id": "src_user_id",
        "receiver_id": "dest_user_id",
    },
    inplace=True,
)
user_message_df["reply_id"] = user_message_df["reply_id"].astype("Int64")
user_message_df = convert_to_timestamp(user_message_df)


post_donation_df = pd.read_csv("./neo4j/post_donations.csv")
post_donation_df.rename(columns={"donation_id": "id"}, inplace=True)
post_donation_df = post_donation_df.drop(columns=["current_amount"])
post_donation_df = post_donation_df[["id", "post_id", "goal_amount", "deadline"]]
post_donation_df = convert_to_timestamp(post_donation_df, datetime_columns=["deadline"])

transaction_df = pd.read_csv("./neo4j/donation_transactions.csv")
transaction_df.rename(columns={"transaction_id": "id"}, inplace=True)
transaction_df = convert_to_timestamp(transaction_df)

post_like_df = pd.read_csv("./neo4j/post_likes.csv")
post_like_df.rename(columns={"like_id": "id"}, inplace=True)
post_like_df = convert_to_timestamp(post_like_df)

post_comment_df = pd.read_csv("./neo4j/post_comments.csv")
post_comment_df.rename(columns={"comment_id": "id", "comment": "text"}, inplace=True)
post_comment_df["reply_id"] = post_comment_df["reply_id"].astype("Int64")
post_comment_df = convert_to_timestamp(post_comment_df)

# Save the cleaned CSV
user_df.to_csv("./postgres/user_profile.csv", index=False)
contact_df.to_csv("./postgres/user_contact.csv", index=False)
user_message_df.to_csv("./postgres/user_message.csv", index=False)
user_post_df.to_csv("./postgres/user_post.csv", index=False)
post_type_df.to_csv("./postgres/post_type.csv", index=False)
contact_type_df.to_csv("./postgres/contact_type.csv", index=False)
post_comment_df.to_csv("./postgres/post_comment.csv", index=False)
post_like_df.to_csv("./postgres/post_like.csv", index=False)
transaction_df.to_csv("./postgres/transaction.csv", index=False)
post_donation_df.to_csv("./postgres/post_donation.csv", index=False)
company_df.to_csv("./postgres/company.csv", index=False)
