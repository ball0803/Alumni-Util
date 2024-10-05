from faker import Faker
import random
from scipy.stats import invgauss
import json
from typing import Dict, List, Tuple
import numpy as np
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import bcrypt
from pythainlp.transliterate import romanize
import string
import pandas as pd
from tqdm import tqdm
from transformers import pipeline
import random

generator = pipeline("text-generation", model="gpt2")

fake = Faker("th_TH")

POST_TYPE = (
    "event",
    "story",
    "job",
    "mentorship",
    "showcase",
    "donation_campaign",
    "announcement",
    "discussion",
    "survey",
)
DOMAINS = ("com", "com.br", "net", "net.br", "org", "org.br", "gov", "gov.br")
# Define constants
TECH_JOBS = [
    "Software Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "AI Researcher",
    "Cloud Architect",
    "Cybersecurity Analyst",
    "Mobile App Developer",
    "Full-Stack Developer",
    "Backend Developer",
]

FIELDS = ["วิศวกรรมคอมพิวเตอร์", "วิศวกรรมไฟฟ้าและคอมพิวเตอร์", "วิทยาศาสตร์ข้อมูลสุขภาพ"]

USER_INTERACTION = {"Low": 1, "Medium": 5, "High": 10}

USER_INTERNSHIP = {"Low": 0.0, "Medium": 0.5, "High": 0.8}
USER_PROFILE = {"Low": 0.1, "Medium": 0.5, "High": 0.8}
USER_PHONE = {"Low": 0.0, "Medium": 0.3, "High": 0.5}
USER_GITHUB = {"Low": 0.1, "Medium": 0.3, "High": 0.6}
USER_LINKIN = {"Low": 0.0, "Medium": 0.5, "High": 0.8}
USER_FACEBOOK = {"Low": 0.1, "Medium": 0.5, "High": 0.8}
USER_TWITTER = {"Low": 0.0, "Medium": 0.2, "High": 0.4}


# Function to hash a password
def hash_password(plain_password):
    # Generate a salt
    salt = bcrypt.gensalt()

    # Hash the password with the generated salt
    hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)

    return hashed_password


def calculate_user_interaction(admit_year: int) -> int:
    # Define the mean and standard deviation for the normal distribution
    mean_year = 2538
    std_dev = 3

    # Calculate the screw curve value based on the admit year
    # We normalize the input to get a z-score
    z_score = (admit_year - mean_year) / std_dev

    # Using a bell curve to determine the weight for user interactions
    weight_high = max(0, (1 - abs(z_score)))  # Closer to 0 is higher weight
    weight_medium = max(0, (0.75 - abs(z_score)))  # Slightly less weight for medium
    weight_low = max(0, (0.5 - abs(z_score)))  # Lowest weight for low

    # Normalize weights to sum to 1
    total_weight = weight_high + weight_medium + weight_low
    # Check if total weight is zero or negative
    if total_weight <= 0:
        # Default to low interaction if all weights are zero
        return "Low"  # Low interaction base

    # Normalize weights to sum to 1
    weight_high /= total_weight
    weight_medium /= total_weight
    weight_low /= total_weight
    # Randomly choose interaction level based on calculated weights
    user_interaction = random.choices(
        ["High", "Medium", "Low"], weights=[weight_high, weight_medium, weight_low], k=1
    )[0]

    # Return the base interaction count based on chosen level
    return user_interaction


def randomize_dob(admit_year):
    """Randomly generate a Date of Birth based on admit year and statistical birth month distribution."""
    # Assume typical student age 18 at admission, with ±2 year variation
    base_birth_year = admit_year - 18
    birth_year = base_birth_year + random.randint(-2, 2)

    # Statistical distribution of birth months (adjust weights as needed)
    month_weights = [
        0.07,
        0.07,
        0.08,
        0.08,
        0.09,
        0.09,
        0.10,
        0.10,
        0.11,
        0.10,
        0.06,
        0.05,
    ]  # Adjusted for higher September birth rates, etc.
    birth_month = random.choices(range(1, 13), weights=month_weights, k=1)[0]

    # Get the number of days in the selected month (handle leap years automatically)
    if birth_month == 2:  # February
        if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
            days_in_month = 29
        else:
            days_in_month = 28
    else:
        days_in_month = 30 if birth_month in [4, 6, 9, 11] else 31

    # Randomly select a day within the month
    birth_day = random.randint(1, days_in_month)

    # Generate date of birth
    dob = date(birth_year, birth_month, birth_day)
    return dob


# Function to generate education level and student type
def generate_education_info(field: str) -> Tuple[str, str]:
    if field == "วิศวกรรมไฟฟ้าและคอมพิวเตอร์":
        education_level = "ปริญญาเอก"
        student_type = random.choices(
            ["ปริญญาเอก นานาชาติ", "ปริญญาเอก ป.ตรีต่อป.เอก"], weights=[80, 20], k=1
        )[0]
    elif field == "วิทยาศาสตร์ข้อมูลสุขภาพ":
        education_level = "ปริญญาตรี"
        student_type = "ปริญญาตรี 4 ปี"
    else:
        education_level = random.choices(["ปริญญาตรี", "ปริญญาโท"], weights=[70, 30], k=1)[
            0
        ]
        student_type = generate_student_type(education_level)

    return education_level, student_type


# Function to generate student type based on education level
def generate_student_type(education_level: str) -> str:
    if education_level == "ปริญญาตรี":
        return random.choice(
            [
                "ปริญญาตรี 4 ปี",
                "ปริญญาตรี 4 ปี (หลักสูตรนานาชาติ)",
                "ปริญญาตรี 4 ปี (โครงการจากพื้นที่การศึกษาราชบุรี)",
            ]
        )
    else:
        return "ปริญญาโท 2 ปี นานาชาติ"


# Function to generate a job
def generate_job() -> str:
    return random.choices(
        TECH_JOBS + [fake.job() for _ in range(5)],
        weights=[70] * len(TECH_JOBS) + [30] * 5,
        k=1,
    )[0]


def clean_generated_content(content, prompt):
    """
    This function removes the input prompt or any echoes of the prompt from the generated content.
    """
    # Remove the exact prompt from the generated content, if present
    if prompt in content:
        content = content.replace(prompt, "").strip()

    return content


def generate_comment(post_content, max_retries=3):
    # Base prompt for generating comments
    comment_prompt = f"Based on this post: '{post_content}', provide a brief and unique comment that captures the essence of the update without repeating the content."

    model = generator.model
    eos_token_id = model.config.eos_token_id

    retries = 0
    comment = ""

    while retries < max_retries:
        # Generate unique comment using NLP
        comment = generator(
            comment_prompt,
            max_new_tokens=30,
            num_return_sequences=1,
            pad_token_id=eos_token_id,
        )[0]["generated_text"]

        comment = (
            clean_generated_content(comment, comment_prompt).strip().replace("\n", " ")
        )

        if comment:
            break

        retries += 1

    if not comment:
        comment = "This is a comment"

    return comment


# Main function to create a unique post
def generate_post_content(post_type):
    titles = {
        "event": [
            "Join Us for a Wonderful Event",
            "Exciting Event Coming Up!",
            "Don't Miss Our Next Gathering",
        ],
        "story": [
            "An Inspiring Journey",
            "Overcoming Challenges",
            "A Story of Success",
        ],
        "job": [
            "New Job Opening: Join Our Team!",
            "Career Opportunity Awaits",
            "We're Hiring!",
        ],
        "mentorship": [
            "Become a Mentor Today",
            "Looking for Mentors",
            "Share Your Knowledge",
        ],
        "showcase": [
            "Showcase Your Achievements",
            "Highlighting Alumni Success",
            "Spotlight on Our Talented Alumni",
        ],
        "donation_campaign": [
            "Support Our Cause",
            "Join Our Donation Drive",
            "Make a Difference Today",
        ],
        "announcement": [
            "Important Announcement",
            "Exciting News to Share",
            "Update from the Alumni Team",
        ],
        "discussion": [
            "Let's Discuss: Share Your Thoughts",
            "Open Discussion: Join the Conversation",
            "What Do You Think?",
        ],
        "survey": [
            "We Want Your Feedback",
            "Participate in Our Survey",
            "Help Us Improve with Your Input",
        ],
    }

    # Base prompt for the content generation
    base_prompts = {
        "event": "We are excited to announce an event that will bring our alumni together. Details include: ",
        "story": "Here is a remarkable story of an alumnus: ",
        "job": "We have a job opening that may interest you. The position requires: ",
        "mentorship": "We are looking for mentors to guide our recent graduates in their careers. If you have experience in: ",
        "showcase": "This month, we are showcasing a talented alumnus who has achieved: ",
        "donation_campaign": "We are launching a donation campaign to support: ",
        "announcement": "Important updates for our alumni community: ",
        "discussion": "We would like to open a discussion on: ",
        "survey": "We invite you to participate in our survey regarding: ",
    }

    # Generate title and content
    title = random.choice(titles[post_type])

    # Generate unique content using NLP
    prompt = base_prompts[post_type]

    model = generator.model
    eos_token_id = model.config.eos_token_id

    content: str = generator(
        prompt,
        max_new_tokens=80,
        num_return_sequences=1,
        pad_token_id=eos_token_id,
    )[0]["generated_text"]

    return title, clean_generated_content(content, prompt).strip().replace("\n", " ")


def generate_message_content():
    """Generate a random message content."""
    synonym_pools = {
        "greetings": ["Hey", "Hello", "Hi", "Howdy", "Hey there", "Greetings"],
        "inquiries": [
            "how's everything going?",
            "how are you doing?",
            "how have you been?",
            "what's new with you?",
            "hope you're doing well!",
            "how's life treating you?",
        ],
        "follow_ups": [
            "Let's catch up soon.",
            "We should meet up sometime.",
            "It would be great to reconnect.",
            "Maybe we could grab a coffee?",
            "Would love to chat soon.",
        ],
        "plans": [
            "Are you attending the alumni meetup?",
            "Do you have time for a quick chat?",
            "Are you free to meet sometime?",
            "Will you be at the next event?",
        ],
        "closings": [
            "Talk soon!",
            "Catch you later!",
            "Looking forward to it!",
            "See you around!",
            "Take care!",
        ],
    }

    messages = (
        f"{random.choice(synonym_pools['greetings'])}, ",
        f"{random.choice(synonym_pools['inquiries'])} ",
        f"{random.choice(synonym_pools['follow_ups'])} ",
        f"{random.choice(synonym_pools['plans'])} ",
        f"{random.choice(synonym_pools['closings'])}",
    )
    return random.choice(messages)


def create_post(user):
    """Simulate the creation of a post for a user."""
    post_type = random.choices(
        POST_TYPE,
        weights=[20, 2, 10, 10, 3, 20, 30, 10, 5],
        k=1,
    )[0]
    title, content = generate_post_content(post_type=post_type)
    post_datetime = fake.date_time_this_year()

    post = {
        "post_id": str(fake.unique.random_int(min=111111, max=999999)),
        "user_id": user["user_id"],
        "content": content,
        "post_type": post_type,
        "visibility": random.choices(
            ["public", "private", "alumni_only"], weights=[70, 5, 25], k=1
        )[0],
        "created_datetime": post_datetime,
    }

    if random.random() < 0.8:
        post["title"] = title

    if random.random() < 0.5:
        post["media_url"] = [fake.image_url() for _ in range(random.randint(1, 5))]

    if random.random() < 0.1:
        post["updated_datetime"] = random_time_after_post(post_datetime)

    # print(f"Post created for {post['user']} at {post['datetime']}")
    return post


def random_time_after_post(post_creation_time):
    """Generate a time delay that is most likely to be soon after post creation, but could be longer."""
    # Generate a random delay using an exponential distribution
    minutes_delay = int(
        np.random.exponential(scale=30)
    )  # Adjust the scale (mean) for time distribution
    return post_creation_time + timedelta(minutes=minutes_delay)


def simulate_user_engagement(posts, users):
    """Simulate users liking and commenting on posts based on their interaction level, including datetime."""
    post_likes = []
    post_comments = []

    for post in tqdm(posts, desc="Simulate post user engagement"):
        post_creation_time = post[
            "created_datetime"
        ]  # Datetime of when the post was created

        for user in users:
            user_interaction = user["user_interaction"]

            # Set the probability for liking/commenting based on interaction level
            if user_interaction == "High":
                like_chance = 0.5
            elif user_interaction == "Medium":
                like_chance = 0.3
            else:
                like_chance = 0.1

            if user_interaction == "High":
                comment_chance = 0.2
            elif user_interaction == "Medium":
                comment_chance = 0.1
            else:
                comment_chance = 0.0

            # Random chance for user to like the post
            if random.random() < like_chance:
                like_datetime = random_time_after_post(post_creation_time)
                post_likes.append(
                    {
                        "like_id": str(fake.unique.random_int(min=111111, max=999999)),
                        "post_id": post["post_id"],
                        "user_id": user["user_id"],
                        "datetime": like_datetime,
                    }
                )

            # Random chance for user to comment on the post
            if random.random() < comment_chance:
                comment_datetime = random_time_after_post(post_creation_time)
                comment = {
                    "comment_id": str(fake.unique.random_int(min=111111, max=999999)),
                    "post_id": post["post_id"],
                    "user_id": user["user_id"],
                    "comment": generate_comment(post["content"]),
                }

                if random.random() < 0.30 and len(post_comments) > 0:
                    random_comment = random.choice(post_comments)
                    comment_datetime = random_time_after_post(
                        random_comment["created_datetime"]
                    )
                    comment["reply_id"] = random_comment["comment_id"]

                comment["created_datetime"] = comment_datetime

                if random.random() < 0.10:
                    comment["updated_datetime"] = random_time_after_post(
                        comment_datetime
                    )
                post_comments.append(comment)

    return post_likes, post_comments


def create_donation_info(posts, users):
    post_donations = []
    donation_transactions = []
    for post in tqdm(posts, desc="Simulate donation transaction"):
        if post["post_type"] == "donation_campaign":
            post_creation_time = post["created_datetime"]
            post_donation_info = {
                "post_id": post["post_id"],
                "donation_id": str(fake.unique.random_int(min=111111, max=999999)),
                "goal_amount": random.randint(1, 20) * 1000,
                "current_amount": 0,
                "deadline": post_creation_time
                + relativedelta(int(np.random.exponential(scale=12))),
            }

            for user in users:
                user_interaction = user["user_interaction"]

                if user_interaction == "High":
                    engagement_chance = 0.5
                elif user_interaction == "Medium":
                    engagement_chance = 0.3
                else:
                    engagement_chance = 0.1

                # Random chance for user to donate to the campaign
                if (
                    random.random() < engagement_chance
                    and post_donation_info["current_amount"]
                    < post_donation_info["goal_amount"]
                ):
                    donation_datetime = random_time_after_post(post_creation_time)
                    amount = int(
                        post_donation_info["goal_amount"] * random.uniform(0.01, 0.30)
                    )
                    status = random.choices(
                        ["confirm", "pending"], weights=[80, 20], k=1
                    )[0]

                    if status == "confirm":
                        post_donation_info["current_amount"] += amount

                    donation_transaction = {
                        "transaction_id": str(
                            fake.unique.random_int(min=111111, max=999999)
                        ),
                        "donation_id": post_donation_info["donation_id"],
                        "user_id": user["user_id"],
                        "datetime": donation_datetime,
                        "amount": amount,
                        "status": status,
                        "reference": str(
                            fake.unique.random_int(min=111111, max=999999)
                        ),
                        "qr_code_url": f"https://www.example.com/qrcode/{''.join(random.choices(string.ascii_letters + string.digits, k=6))}",
                    }

                    donation_transactions.append(donation_transaction)

            post_donations.append(post_donation_info)

    return post_donations, donation_transactions


def random_message_time(previous_time):
    """Generate a datetime after a previous message time, with more frequent messages for highly interactive users."""
    minutes_delay = int(np.random.exponential(scale=30))  # Mean time between messages
    return previous_time + timedelta(minutes=minutes_delay)


def send_messages_between_users(users):
    """Simulate users sending messages to each other based on interaction levels."""
    messages = []  # To store the messages

    for sender in tqdm(users, desc="Simulate user message"):
        interaction_level = calculate_user_interaction(sender["admit_year"])

        # Determine how many messages the sender will initiate based on interaction level
        if interaction_level == 10:  # High interaction
            message_count = random.randint(
                5, 10
            )  # High interaction users send more messages
        elif interaction_level == 5:  # Medium interaction
            message_count = random.randint(2, 5)
        else:  # Low interaction
            message_count = random.randint(
                0, 2
            )  # Low interaction users rarely send messages

        # Generate messages
        for _ in range(message_count):
            receiver = random.choice(users)

            # Avoid self-messaging
            while receiver == sender:
                receiver = random.choice(users)

            # Generate a random datetime for the message
            if len(messages) > 0:
                last_message_datetime = messages[-1]["created_datetime"]
            else:
                last_message_datetime = fake.date_time_this_year()

            message_datetime = random_message_time(last_message_datetime)

            # Create message entry
            message = {
                "message_id": str(fake.unique.random_int(min=111111, max=999999)),
                "sender_id": sender["user_id"],
                "receiver_id": receiver["user_id"],
                "text": generate_message_content(),
            }

            if random.random() < 0.10 and len(messages) > 0:
                last_message = messages[-1]
                message_datetime = random_time_after_post(
                    last_message["created_datetime"]
                )
                message["reply_id"] = last_message["message_id"]

            message["created_datetime"] = message_datetime

            if random.random() < 0.05:
                message["updated_datetime"] = random_time_after_post(message_datetime)

            messages.append(message)  # Append message to the list

    return messages


# Function to generate graduate year
def calculate_graduate_year(admit_year: int, education_level: str) -> int:
    if education_level == "ปริญญาตรี":
        return admit_year + random.choices([3, 4], weights=[70, 30], k=1)[0]
    elif education_level == "ปริญญาโท":
        return admit_year + 2
    else:  # For PhD
        mu = 3.0
        lambda_param = 2
        return admit_year + int(invgauss.rvs(mu / lambda_param, scale=mu))


def safe_romanize(name):
    try:
        return romanize(name)
    except IndexError as e:
        print(f"Error romanizing name '{name}': {e}")
        return name  # or return a default value


def generate_valid_thai_name(gender: str) -> Tuple[str, str]:
    while True:
        first_name = (
            fake.first_name_female() if gender == "F" else fake.first_name_male()
        )
        last_name = fake.last_name()

        # Check if both names are valid Thai names
        try:
            # Try to romanize the names to check their validity
            romanize(first_name)
            romanize(last_name)
            return first_name, last_name
        except Exception as e:
            # If there is an error during romanization, retry
            print(f"Error with names: {first_name} {last_name} - {e}. Retrying...")


def main():
    # Main loop to generate alumni data
    alumni_user: List[Dict] = []
    user_post: List[Dict] = []
    # print("hello")
    for _ in tqdm(range(1000), desc="Generating Alumni User and Post"):
        user_id = str(fake.unique.random_int(min=111111, max=999999))
        gender = random.choices(["F", "M"], weights=[70, 30], k=1)[0]

        first_name, last_name = generate_valid_thai_name(gender=gender)
        first_name_eng = safe_romanize(first_name)
        last_name_eng = safe_romanize(last_name)
        faculty = "คณะวิศวกรรมศาสตร์"
        department = "ภาควิชาวิศวกรรมคอมพิวเตอร์"

        field = random.choices(FIELDS, weights=[70, 20, 10], k=1)[0]
        education_level, student_type = generate_education_info(field)

        company = fake.company()
        company_eng = safe_romanize(company).split(" ")[0]
        company_intern = fake.company()
        workplace_intern = f"{fake.street_address()}, {company_intern}"
        job_intern = generate_job()
        workplace = f"{fake.street_address()}, {company}"
        job = generate_job()

        dns_org = random.choice(DOMAINS)
        email = f"{first_name_eng}.{last_name_eng}@{company_eng}.{dns_org}".lower()

        admit_year = random.randint(2530, 2560)
        dob = randomize_dob(admit_year)
        graduate_year = calculate_graduate_year(admit_year, education_level)

        # Generate GPAX using a Gaussian distribution, ensure it is between 0.0 and 4.0
        gpax = round(max(0.0, min(4.0, random.gauss(3, 1))), 2)

        username = f"{first_name_eng}.{last_name_eng}@gmail.com".lower()
        password = hash_password(fake.password())

        user_interaction = calculate_user_interaction(admit_year=admit_year)

        role = "alumni"

        user = {
            "user_id": user_id,
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "first_name_eng": first_name_eng,
            "last_name_eng": last_name_eng,
            "gender": gender,
            "DOB": dob,
            "faculty": faculty,
            "department": department,
            "field": field,
            "student_type": student_type,
            "education_level": education_level,
            "workplace": workplace,
            "company": company,
            "job": job,
            "admit_year": admit_year,
            "graduate_year": graduate_year,
            "gpax": gpax,
            "email": email,
            "role": role,
            "user_interaction": user_interaction,
        }

        if random.random() < USER_PROFILE[user["user_interaction"]]:
            user["profile_picture"] = fake.image_url()

        if random.random() < USER_INTERNSHIP[user["user_interaction"]]:
            user["company_internship"] = company_intern
            user["internship"] = workplace_intern
            user["job_internship"] = job_intern

        if random.random() < USER_GITHUB[user["user_interaction"]]:
            user["github"] = f"{first_name_eng}.{last_name_eng}@github.com".lower()

        if random.random() < USER_LINKIN[user["user_interaction"]]:
            user["linkedin"] = f"{first_name_eng}.{last_name_eng}@linkedin.com".lower()

        if random.random() < USER_FACEBOOK[user["user_interaction"]]:
            user["facebook"] = f"{first_name_eng}.{last_name_eng}@gmail.com".lower()

        if random.random() < USER_PHONE[user["user_interaction"]]:
            user["phone"] = fake.phone_number()

        if random.random() < USER_TWITTER[user["user_interaction"]]:
            user["facebook"] = f"{first_name_eng}@gmail.com".lower()

        alumni_user.append(user)

        # Set initial chance of post creation based on user interaction level
        if user_interaction == "High":
            post_creation_chance = 0.3
        elif user_interaction == "Medium":
            post_creation_chance = 0.1
        else:
            post_creation_chance = 0.0

        # Continue trying to create posts until the chance drops to 0
        while post_creation_chance > 0:
            if random.random() < post_creation_chance:
                # If post creation is successful, call the post creation function
                user_post.append(create_post(user))
                # Halve the post creation chance
                post_creation_chance /= 2
            else:
                # Stop trying to create posts if one is not created
                break

    post_likes, post_comments = simulate_user_engagement(user_post, alumni_user)
    user_messages = send_messages_between_users(alumni_user)
    post_donations, donation_trasactions = create_donation_info(user_post, alumni_user)

    user_profile_df = pd.DataFrame(alumni_user)
    user_posts_df = pd.DataFrame(user_post)
    post_likes_df = pd.DataFrame(post_likes)
    post_comments_df = pd.DataFrame(post_comments)
    post_donations_df = pd.DataFrame(post_donations)
    donation_trasactions = pd.DataFrame(donation_trasactions)
    user_messages_df = pd.DataFrame(user_messages)

    user_profile_df.to_csv("alumni_user.csv", index=False, encoding="utf-8-sig")
    user_posts_df.to_csv("user_post.csv", index=False, encoding="utf-8-sig")
    post_likes_df.to_csv("post_likes.csv", index=False, encoding="utf-8-sig")
    post_comments_df.to_csv("post_comments.csv", index=False, encoding="utf-8-sig")
    post_donations_df.to_csv("post_donations.csv", index=False, encoding="utf-8-sig")
    donation_trasactions.to_csv(
        "donation_transactions.csv", index=False, encoding="utf-8-sig"
    )
    user_messages_df.to_csv("user_interaction.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
