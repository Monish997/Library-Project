CREATE TABLE publishers(
    publisher_name VARCHAR(64) PRIMARY KEY
);

CREATE TABLE authors(
    author_name VARCHAR(64) PRIMARY KEY
);

CREATE TABLE categories(
    category_name VARCHAR(32) PRIMARY KEY
);

CREATE TABLE books(
    isbn_13 CHAR(13) PRIMARY KEY,
    title VARCHAR(64) NOT NULL,
    category VARCHAR(32),
    author VARCHAR(64),
    publisher VARCHAR(64),
    date_published DATE NOT NULL,
    price INT NOT NULL,
    CONSTRAINT FOREIGN KEY (publisher) REFERENCES publishers (publisher_name),
    CONSTRAINT FOREIGN KEY (author) REFERENCES authors (author_name),
    CONSTRAINT FOREIGN KEY (category) REFERENCES categories (category_name)
);

CREATE TABLE copies(
    copy_id CHAR(36) PRIMARY KEY,
    isbn_13_fk CHAR(13),
    date_acquired DATE NOT NULL,
    CONSTRAINT FOREIGN KEY (isbn_13_fk) REFERENCES books (isbn_13)
);

CREATE TABLE membership_plans(
    title VARCHAR(32) PRIMARY KEY,
    borrow_limit INT NOT NULL,
    annual_fee INT NOT NULL,
    fine_per_day INT NOT NULL
);

CREATE TABLE members(
    member_id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(32) NOT NULL,
    last_name VARCHAR(32) NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    dob DATE NOT NULL,
    doj DATE NOT NULL,
    email VARCHAR(64) UNIQUE NOT NULL,
    membership_plan VARCHAR(32),
    expiry_date DATE,
    CONSTRAINT FOREIGN KEY (membership_plan) REFERENCES membership_plans (title) ON UPDATE CASCADE
);

CREATE TABLE staff_levels(
    title VARCHAR(32) PRIMARY KEY,
    manage_member BOOLEAN NOT NULL,
    manage_staff BOOLEAN NOT NULL,
    manage_books BOOLEAN NOT NULL,
    manage_issues BOOLEAN NOT NULL,
    salary INT
);

CREATE TABLE staff(
    staff_id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(32) NOT NULL,
    last_name VARCHAR(32) NOT NULL,
    gender enum('Male', 'Female'),
    dob DATE NOT NULL,
    doj DATE NOT NULL,
    email VARCHAR(64) NOT NULL,
    job_title VARCHAR(32),
    CONSTRAINT FOREIGN KEY (job_title) REFERENCES staff_levels (title) ON UPDATE CASCADE
);

CREATE TABLE issues(
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    copy_id_fk CHAR(36),
    issued_on DATE NOT NULL,
    issued_to CHAR(36),
    due_on DATE NOT NULL,
    fine INT DEFAULT 0,
    CONSTRAINT FOREIGN KEY (copy_id_fk) REFERENCES copies (copy_id),
    CONSTRAINT FOREIGN KEY (issued_to) REFERENCES members (member_id)
);

DELIMITER $$

CREATE EVENT update_fines
ON SCHEDULE EVERY 1 DAY STARTS TIMESTAMP(CURDATE())
DO BEGIN
    UPDATE issues
    SET fine = DATEDIFF(CURDATE(), due_on) * (
        SELECT fine_per_day FROM membership_plans 
        WHERE title = (
            SELECT membership_plan FROM members 
            WHERE member_id = issued_to
        )
    )
    WHERE due_on < CURDATE();
END$$

CREATE EVENT expire_members
ON SCHEDULE EVERY 1 DAY STARTS TIMESTAMP(CURDATE())
DO BEGIN
    UPDATE members
    SET membership_plan = 'Basic', expiry_date=NULL
    WHERE expiry_date < CURDATE();
END$$

DELIMITER ;

INSERT INTO publishers VALUES
('HarperCollins'),
('Penguin Random House'),
('Hachette Livre');
INSERT INTO authors VALUES
('Jonathan Swift'),
('John Grisham'),
('Agatha Christie');
INSERT INTO categories VALUES
('Mystery'),
('Educational'),
('Sci-Fi'),
('Manga'),
('Fantasy');
INSERT INTO books VALUES 
('1234567890123', 'Gulliver Travels', 'Fantasy', 'Jonathan Swift', 'HarperCollins', '2000-01-01', 500),
('0987654321098', 'Camino Island', 'Mystery', 'John Grisham', 'Penguin Random House', '1998-04-30', 600),
('1029384756123', 'Murder on the Orient Express', 'Mystery', 'Agatha Christie', 'Penguin Random House', '2002-04-01', 550);
INSERT INTO copies VALUES
('47b0d6cc-5155-4c4f-9cb3-6cdb4662e23f', '1234567890123', '2020-01-04'),
('c62db5db-335e-4bb0-98ab-2b5c0aa2e43b', '1234567890123', '2020-01-04'),
('6bf3e76d-8a86-4922-a4b7-c4de1325da32', '0987654321098', '2020-01-04'),
('db829287-79f4-4d1c-a8ff-3396f499f53e', '0987654321098', '2020-01-04'),
('fdd8f7a9-1f4d-40cc-accc-9b1ac9c32c70', '1029384756123', '2020-01-04'),
('00f36802-9ab2-47c5-ad9f-1c301030b324', '1029384756123', '2020-01-04');
INSERT INTO membership_plans VALUES
('Basic', 1, 0, 15),
('Silver', 3, 500, 10),
('Gold', 5, 1000, 5);
INSERT INTO members VALUES 
('edd74ed7-684b-4ab7-a04c-8b5744841673', 'Austin', 'Howard', 'Male', '2000-02-08', '2020-11-09', 'austin@gmail.com', 'Basic', NULL),
('de438362-dcc1-470e-9f23-e778a582e770', 'Abigail', 'Anderson', 'Female', '2003-05-30', '2020-06-01', 'abigail@yahoo.com', 'Silver', '2021-06-01'),
('3ada1a9c-aeb4-4bd8-9908-67c1ca33e9dc', 'Leah', 'Brown', 'Female', '1997-07-29', '2020-07-01', 'leah@gmail.com', 'Gold', '2021-07-01');
INSERT INTO staff_levels VALUES
('Admin', 1, 1, 1, 1, NULL),
('Librarian', 0, 0, 1, 1, 20000),
('Human Resource', 1, 1, 0, 0, 30000);
INSERT INTO staff VALUES
('bccb480b-3394-467b-98b4-60b0ea544831', 'Oliver', 'Glover', 'Male', '2003-08-27', '2020-01-04', 'oliver@outlook.com', 'Admin'),
('61743a67-c698-48c3-8067-b5eb3a182a5d', 'Rebecca', 'Fisher', 'Female', '2003-02-18', '2020-01-04', 'rebecca@outlook.com', 'Librarian'),
('16bbfe03-b3ee-456e-aa2d-7bb8e843662f', 'Kevin', 'Greene', 'Male', '2003-04-16', '2020-01-04', 'kevin@gmail.com', 'Human Resource');