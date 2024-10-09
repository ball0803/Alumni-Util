MATCH (u:UserProfile)-[:HAS_POST]->(p:Post {visibility: "public"}) RETURN u, p;

MATCH (u:UserProfile)<-[:COMMENTED_BY]-(c:Comment)-[:COMMENTED_ON]->(p:Post {post_id: "359306"})
OPTIONAL MATCH (reply:Comment)-[:REPLIES_TO]->(c)
OPTIONAL MATCH (replier:UserProfile)<-[:COMMENTED_BY]-(reply)
OPTIONAL MATCH (p)<-[:LIKES]-(liker:UserProfile)
RETURN u AS commenter,
       c AS comment,
       p AS post,
       reply AS reply_comment,
       replier AS replier_profile,
       collect(liker) AS likers
ORDER BY c.created_timestamp, reply.created_timestamp;


MATCH (u:UserProfile {admit_year: 2535, education_level: 'ปริญญาตรี'}) RETURN u;

MATCH (u:UserProfile {user_id: "378035"})

MATCH (u)-[:SENT]->(sent:Message)
MATCH (sent)<-[:RECEIVED]-(receiver:UserProfile)
OPTIONAL MATCH (sent)<-[:REPLIES_TO]-(reply:Message)
WITH u, sent, receiver, reply


MATCH (u)-[:RECEIVED]->(received:Message)
MATCH (received)<-[:SENT]-(sender:UserProfile)
RETURN u AS user,
       collect(sent) AS sent_messages,
       collect(receiver) AS sent_to_users,
       collect(reply) AS replies,
       collect(received) AS received_messages,
       collect(sender) AS received_from_users;
