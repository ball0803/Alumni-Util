LOAD CSV WITH HEADERS FROM 'file:///alumni_user.csv' AS row
// Merge Faculty, Department, and Field Nodes (avoid duplication)
MERGE (f:Faculty {name: row.faculty})
MERGE (d:Department {name: row.department})
MERGE (fld:Field {name: row.field})
MERGE (st:StudentType {name: row.student_type})
// Link Faculty to Department, and Department to Field, Field to Student Type
MERGE (f)-[:HAS_DEPARTMENT]->(d)
MERGE (d)-[:HAS_FIELD]->(fld)
MERGE (fld)-[:HAS_STUDENT_TYPE]->(st)

// Merge UserProfile
MERGE (u:UserProfile {
    user_id: row.user_id,
    username: row.username,
    user_password: row.password
})
SET u.first_name = row.first_name,
    u.last_name = row.last_name,
    u.first_name_eng = row.first_name_eng,
    u.last_name_eng = row.last_name_eng,
    u.DOB = date(row.DOB)
    u.gender = row.gender,
    u.email = row.email,
    u.education_level = row.education_level,
    u.admit_year = toInteger(row.admit_year),
    u.graduate_year = toInteger(row.graduate_year),
    u.gpax = toFloat(row.gpax),
    u.profile_picture = row.profile_picture,
    u.phone = CASE WHEN row.phone <> "" THEN row.phone ELSE NULL END,
    u.linkedin = CASE WHEN row.linkedin <> "" THEN row.linkedin ELSE NULL END,
    u.facebook = CASE WHEN row.facebook <> "" THEN row.facebook ELSE NULL END,
    u.github = CASE WHEN row.github <> "" THEN row.github ELSE NULL END

// Connect User to Field and Student Type
MERGE (u)-[:BELONGS_TO_FIELD]->(fld)
MERGE (u)-[:BELONGS_TO_STUDENT_TYPE]->(st)

// Merge Address if company is provided
WITH u, row
WHERE row.company <> ""
MERGE (a:Company {company: row.company, address: row.workplace})
MERGE (u)-[r:HAS_WORK_WITH]->(a)
SET r.type = 'workplace',
    r.job = row.job;

WITH u, row
WHERE row.internship <> ""
MERGE (a:Company {company: row.company_internship, address: row.internship})
MERGE (u)-[r:HAS_WORK_WITH]->(a)
SET r.type = 'workplace',
    r.job = row.job_internship;


LOAD CSV WITH HEADERS FROM 'file:///user_post.csv' AS post_row
// Match the user based on user_id
MATCH (u:UserProfile {user_id: post_row.user_id})

// Create Post node and its properties
MERGE (p:Post {
    post_id: post_row.post_id
})
SET p.content = post_row.content,
    p.post_type = post_row.post_type,
    p.visibility = post_row.visibility,
    p.created_timestamp = apoc.date.parse(post_row.created_datetime, 's', 'yyyy-MM-dd HH:mm:ss'),
    p.updated_timestamp = CASE WHEN post_row.updated_datetime <> "" THEN apoc.date.parse(post_row.updated_datetime, 's', 'yyyy-MM-dd HH:mm:ss') ELSE NULL END,
    p.title = post_row.title,
    p.media_urls = CASE
                    WHEN post_row.media_url <> ""
                    THEN split(replace(replace(replace(post_row.media_url, "[", ""), "]", ""), "'", ""), ", ")
                    ELSE []
                   END

// Create the relationship between User and Post
MERGE (u)-[:HAS_POST]->(p);

// Load comments from post_comments.csv
LOAD CSV WITH HEADERS FROM 'file:///post_comments.csv' AS comment_row
MATCH (u:UserProfile {user_id: comment_row.user_id})
MATCH (p:Post {post_id: comment_row.post_id})

// Create Comment node and its properties
MERGE (c:Comment {
    comment_id: comment_row.comment_id
})
SET c.comment = comment_row.comment,
    c.created_timestamp = apoc.date.parse(comment_row.created_datetime, 's', 'yyyy-MM-dd HH:mm:ss'),
    c.updated_timestamp = CASE WHEN comment_row.updated_datetime <> "" THEN apoc.date.parse(comment_row.updated_datetime, 's', 'yyyy-MM-dd HH:mm:ss') ELSE NULL END

MERGE (c)-[:COMMENTED_ON]->(p)
MERGE (c)-[:COMMENTED_BY]->(u)

WITH comment_row, c
WHERE comment_row.reply_id IS NOT NULL
MATCH (r:Comment {comment_id: toInteger(comment_row.reply_id)})
CREATE (c)-[:REPLIES_TO]->(r);


// Load likes from post_likes.csv
LOAD CSV WITH HEADERS FROM 'file:///post_likes.csv' AS like_row
MATCH (u:UserProfile {user_id: like_row.user_id})
MATCH (p:Post {post_id: like_row.post_id})

// Create the relationship between User and Post with properties
MERGE (u)-[l:LIKES]->(p)
SET l.timestamp = apoc.date.parse(like_row.datetime, 's', 'yyyy-MM-dd HH:mm:ss');


// Load donations from post_donations.csv
LOAD CSV WITH HEADERS FROM 'file:///post_donations.csv' AS donation_row
// Match the corresponding Post based on post_id
MATCH (p:Post {post_id: donation_row.post_id})

// Create Donation node and its properties
MERGE (d:Donation {
    donation_id: donation_row.donation_id
})
SET d.goal_amount = toFloat(donation_row.goal_amount),
    d.current_amount = toFloat(donation_row.current_amount),
    d.deadline_timestamp = apoc.date.parse(donation_row.deadline, 's', 'yyyy-MM-dd HH:mm:ss')

MERGE (p)-[:HAS_DONATION]->(d);

// Load donation transactions from donation_transactions.csv
LOAD CSV WITH HEADERS FROM 'file:///donation_transactions.csv' AS transaction_row
// Match the corresponding Donation and User based on donation_id and user_id
MATCH (d:Donation {donation_id: transaction_row.donation_id})
MATCH (u:UserProfile {user_id: transaction_row.user_id})

// Create Transaction node and its properties
MERGE (t:Transaction {
    transaction_id: transaction_row.transaction_id
})
SET t.amount = toFloat(transaction_row.amount),
    t.status = transaction_row.status,
    t.reference = transaction_row.reference,
    t.qr_code_url = transaction_row.qr_code_url,
    t.timestamp = apoc.date.parse(transaction_row.datetime, 's', 'yyyy-MM-dd HH:mm:ss')

// Create the relationship between Donation and Transaction
MERGE (d)-[:HAS_TRANSACTION]->(t)
MERGE (u)-[:MADE_TRANSACTION]->(t);


// Load user interactions from user_interactions.csv
LOAD CSV WITH HEADERS FROM 'file:///user_interactions.csv' AS interaction_row

MATCH (sender:UserProfile {user_id: interaction_row.sender_id})
MATCH (receiver:UserProfile {user_id: interaction_row.receiver_id})

// Create Message node and its properties
MERGE (m:Message {
    message_id: interaction_row.message_id
})
SET m.content = interaction_row.content,
    m.created_timestamp = apoc.date.parse(interaction_row.created_datetime, 's', 'yyyy-MM-dd HH:mm:ss'),
    m.updated_timestamp = CASE WHEN interaction_row.updated_datetime <> "" THEN apoc.date.parse(interaction_row.updated_datetime, 's', 'yyyy-MM-dd HH:mm:ss') ELSE NULL END

// Create relationships between sender, receiver, and the message
MERGE (sender)-[:SENT]->(m)
MERGE (receiver)-[:RECEIVED]->(m)

WITH interaction_row, m
WHERE interaction_row.reply_id IS NOT NULL
MATCH (r:Comment {comment_id: toInteger(interaction_row.reply_id)})
CREATE (m)-[:REPLIES_TO]->(r);
