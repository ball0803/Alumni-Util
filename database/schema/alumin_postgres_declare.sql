CREATE TABLE "ContactType" (
  "id" SERIAL PRIMARY KEY,
  "text" VARCHAR(255)
);

CREATE TABLE "UserProfile" (
  "id" SERIAL PRIMARY KEY,
  "username" VARCHAR(255) NOT NULL,
  "password" VARCHAR(255) NOT NULL,
  "first_name" VARCHAR(255),
  "last_name" VARCHAR(255),
  "first_name_eng" VARCHAR(255),
  "last_name_eng" VARCHAR(255),
  "DOB" DATE,
  "gender" VARCHAR(50),
  "admit_year" INTEGER,
  "graduation_year" INTEGER,
  "education_level" VARCHAR(30),
  "student_type" VARCHAR(255),
  "profile_picture" TEXT,
  "field" VARCHAR(255),
  "department" VARCHAR(255),
  "faculty" VARCHAR(255),
  "gpax" DECIMAL(3, 2),
  "role" VARCHAR(50),
  "created_datetime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updated_datetime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "UserContact" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER,
  "contact_type" INTEGER,
  "text" VARCHAR(255),
  CONSTRAINT "FK_UserContact_contact_type"
    FOREIGN KEY ("contact_type") REFERENCES "ContactType"("id"),
  CONSTRAINT "FK_UserContact_profile_id"
    FOREIGN KEY ("user_id") REFERENCES "UserProfile"("id")
);

CREATE TABLE "PostType" (
  "id" SERIAL PRIMARY KEY,
  "text" VARCHAR(255)
);

CREATE TABLE "UserPost" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER,
  "post_type" INTEGER,
  "media_location" TEXT[],
  "title" VARCHAR(100),
  "text" TEXT,
  "visibility" VARCHAR(20),
  "created_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updated_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "FK_UsesPost_user_id"
    FOREIGN KEY ("user_id") REFERENCES "UserProfile"("id"),
  CONSTRAINT "FK_UsesPost_post_type"
    FOREIGN KEY ("post_type") REFERENCES "PostType"("id")
);

CREATE TABLE "PostLike" (
  "id" SERIAL PRIMARY KEY,
  "post_id" INTEGER,
  "user_id" INTEGER,
  "created_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "FK_PostLike_profile_id"
    FOREIGN KEY ("user_id") REFERENCES "UserProfile"("id"),
  CONSTRAINT "FK_PostLike_post_id"
    FOREIGN KEY ("post_id") REFERENCES "UserPost"("id")
);

CREATE TABLE "UserMessage" (
  "id" SERIAL PRIMARY KEY,
  "src_user_id" INTEGER,
  "dest_user_id" INTEGER,
  "text" TEXT,
  "media_location" TEXT[],
  "reply_id" INTEGER,
  "created_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updated_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "FK_UserMessage_src_profile_id"
    FOREIGN KEY ("src_user_id") REFERENCES "UserProfile"("id"),
  CONSTRAINT "FK_UserMessage_dest_profile_id"
    FOREIGN KEY ("dest_user_id") REFERENCES "UserProfile"("id")
);

CREATE TABLE "Donation" (
  "id" SERIAL PRIMARY KEY,
  "post_id" INTEGER,
  "goal_amount" DECIMAL(10, 2),
  "deadline" DATE,
  CONSTRAINT "FK_Donation_post_id"
    FOREIGN KEY ("post_id") REFERENCES "UserPost"("id")
);

CREATE TABLE "Transaction" (
  "id" SERIAL PRIMARY KEY,
  "donation_id" INTEGER,
  "user_id" INTEGER,
  "amount" DECIMAL(10, 2),
  "status" VARCHAR(50),
  "reference" VARCHAR(255),
  "qr_code_url" TEXT,
  "created_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "FK_Transaction_user_id"
    FOREIGN KEY ("user_id") REFERENCES "UserProfile"("id"),
  CONSTRAINT "FK_Transaction_donation_id"
    FOREIGN KEY ("donation_id") REFERENCES "Donation"("id")
);

CREATE TABLE "PostComment" (
  "id" SERIAL PRIMARY KEY,
  "post_id" INTEGER,
  "profile_id" INTEGER,
  "text" TEXT,
  "reply_id" INTEGER,
  "created_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updated_timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "FK_PostComment_post_id"
    FOREIGN KEY ("post_id") REFERENCES "UserPost"("id"),
  CONSTRAINT "FK_PostComment_profile_id"
    FOREIGN KEY ("profile_id") REFERENCES "UserProfile"("id")
);

CREATE TABLE "Company" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER,
  "company" VARCHAR(255),
  "address" TEXT,
  "job" VARCHAR(255),
  "type" VARCHAR(50),
  CONSTRAINT "FK_Company_user_id"
    FOREIGN KEY ("user_id") REFERENCES "UserProfile"("id")
);

CREATE TABLE "UserFriends" (
	"friend_id"SERIAL PRIMARY KEY,
	"user1_id" INT NOT NULL,
	"user2_id" INT NOT NULL,
	"created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"status" VARCHAR(10) DEFAULT 'active',
	UNIQUE (user1_id, user2_id),
	CONSTRAINT fk_user1 FOREIGN KEY (user1_id) REFERENCES "UserProfile"(id) ON DELETE CASCADE,
	CONSTRAINT fk_user2 FOREIGN KEY (user2_id) REFERENCES "UserProfile"(id) ON DELETE CASCADE
);

COPY "UserProfile"(
  id, username, password, first_name, last_name, first_name_eng,
  last_name_eng, gender, "DOB", faculty, department, field, student_type,
  education_level, admit_year, graduation_year, gpax, role, profile_picture)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\user_profile.csv'
DELIMITER ','
CSV HEADER;

COPY "PostType"(
  id,text)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\post_type.csv'
DELIMITER ','
CSV HEADER;

COPY "ContactType"(
  id,text)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\contact_type.csv'
DELIMITER ','
CSV HEADER;

COPY "UserContact"(
  user_id,contact_type,text)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\user_contact.csv'
DELIMITER ','
CSV HEADER;

COPY "Company" (user_id,company,address,job,type)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\company.csv'
DELIMITER ','
CSV HEADER;


COPY "UserPost" (id,user_id,text,post_type,visibility,created_timestamp,title,media_location,updated_timestamp)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\user_post.csv'
DELIMITER ','
CSV HEADER;

COPY "UserMessage" (id,src_user_id,dest_user_id,text,created_timestamp,updated_timestamp,reply_id)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\user_message.csv'
DELIMITER ','
CSV HEADER;

COPY "PostLike" (id,post_id,user_id,timestamp)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\post_like.csv'
DELIMITER ','
CSV HEADER;

COPY "PostComment" (id,post_id,user_id,text,created_timestamp,reply_id,updated_timestamp)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\post_comment.csv'
DELIMITER ','
CSV HEADER;

COPY "Donation" (id,post_id,goal_amount,deadline)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\post_donation.csv'
DELIMITER ','
CSV HEADER;

COPY "Transaction" (id,donation_id,user_id,timestamp,amount,status,reference,qr_code_url)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\transaction.csv'
DELIMITER ','
CSV HEADER;

COPY "UserFriend" (id,user1_id,user2_id)
FROM 'C:\Users\COMPUTER\Desktop\Project\Python\Alumni\postgres\user_friend.csv'
DELIMITER ','
CSV HEADER;
