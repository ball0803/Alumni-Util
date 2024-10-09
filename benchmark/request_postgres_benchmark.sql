-- Query 1: Get public posts and join with user profile
BEGIN;

SELECT up.*, up2.first_name_eng, up2.last_name_eng, up2.admit_year
FROM "UserPost" up
JOIN "UserProfile" up2 ON up.user_id = up2.id
WHERE visibility = 'public';

COMMIT;

-- Query 2: Get a specific post along with author's profile
\set post_id 359306
BEGIN;

SELECT
    p.id as post_id,
    p.text as post_text,
    p.created_timestamp as post_created,
    p.updated_timestamp as post_updated,
    u.first_name as author_first_name,
    u.last_name as author_last_name
FROM
    "UserPost" p
LEFT JOIN
    "UserProfile" u ON p.user_id = u.id
WHERE
    p.id = :post_id;

COMMIT;

-- Query 3: Get comments for the specific post
BEGIN;

SELECT
    c.id as comment_id,
    c.text,
    c.created_timestamp as comment_created,
    u.first_name,
    u.last_name
FROM
    "PostComment" c
LEFT JOIN
    "UserProfile" u ON c.user_id = u.id
WHERE
    c.post_id = :post_id;

COMMIT;

-- Query 4: Get likes for the specific post
BEGIN;

SELECT
    u.first_name,
    u.last_name,
    l.timestamp
FROM
    "PostLike" l
LEFT JOIN
    "UserProfile" u ON l.user_id = u.id
WHERE
    l.post_id = :post_id;

COMMIT;

-- Query 5: Get profiles of users admitted in a specific year and education level
\set admit_year 2535
BEGIN;

SELECT *
FROM "UserProfile" up
WHERE admit_year = :admit_year AND education_level = 'ปริญญาตรี';

COMMIT;

-- Query 6: Get message details between a specific user and others
\set user_id 378035
BEGIN;

SELECT
    um.src_user_id,
    um.dest_user_id,
    COUNT(um.id) AS message_count,
    ARRAY_AGG(um.text) AS messages,
    MIN(um.created_timestamp) AS first_message_time,
    MAX(um.created_timestamp) AS last_message_time
FROM
    "UserMessage" um
WHERE
    (um.src_user_id = :user_id OR um.dest_user_id = :user_id)
GROUP BY
    um.src_user_id, um.dest_user_id
ORDER BY
    last_message_time;

COMMIT;
