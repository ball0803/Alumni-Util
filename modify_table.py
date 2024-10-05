import pandas as pd

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
user_df = pd.read_csv("./alumni_user.csv")

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
    ]
)

user_post_df = pd.read_csv("./user_post.csv")
user_post_df.rename(
    columns={"post_id": "id", "media_url": "media_location"}, inplace=True
)
user_post_df["post_type"] = user_post_df["post_type"].map(post_type_mapping)

user_message_df = pd.read_csv("./user_interactions.csv")
user_message_df.rename(
    columns={
        "message_id": "id",
        "sender_id": "src_user_id",
        "receiver_id": "dest_user_id",
    }
)

post_donation_df = pd.read_csv("./post_donations.csv")
post_donation_df.rename(columns={"donation": "id"})
post_donation_df = post_donation_df.drop(columns=["current_amount"])

transaction_df = pd.read_csv("./donation_transactions.csv")
transaction_df.rename(columns={"transaction_id": "id"})

post_like_df = pd.read_csv("./post_likes.csv")
post_like_df.rename(columns={"like_id": "id"})

post_comment_df = pd.read_csv("./post_comments.csv")
post_comment_df.rename(columns={"comment_id": "id", "comment": "text"})
# Save the cleaned CSV
# user_df.to_csv("./postgres/user_profile.csv", index=False)
