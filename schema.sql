CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20)
);

CREATE TABLE medications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    med_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    reminder_time TIME NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medication_id INT,
    sent_at DATETIME,
    method VARCHAR(10),
    status VARCHAR(20),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

INSERT INTO patients (name, email, phone) 
VALUES ('Test Patient', 'test@example.com', '+15550000000');

INSERT INTO medications (patient_id, med_name, dosage, reminder_time, frequency) 
VALUES (1, 'Vitamin D', '1000 IU', '09:00:00', 'daily');