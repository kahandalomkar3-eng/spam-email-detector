# Project Documentation

## 2.1 Data Requirements of the System

The Spam Email Detector needs two main types of data:

1. Training data
   The system needs a dataset of email messages that are already labeled as `spam` or `ham` (safe email). In this project, that data is stored in the `spam.csv` file.

2. Runtime data
   When the system is running, it needs the email message entered by the user. It also stores the prediction result, confidence score, and date/time in the history database.

The main data requirements are:

- The training dataset must be in CSV format.
- The dataset must contain email text and a label column.
- The accepted labels are `spam` and `ham`.
- Empty records should not be used.
- Duplicate records should be removed for better model quality.
- The trained model files `spam_model.pkl` and `vectorizer.pkl` must be available before prediction starts.
- A SQLite database file is needed to store prediction history.

In simple words, the system needs clean email examples for learning, and it needs user-entered email text for checking messages in real use.

## 2.2 Identify End Users of the System

The main end users of this system are:

1. General email users
   People who want to check whether an email message is safe or suspicious.

2. Office staff or employees
   Users who receive many emails and want quick help in identifying spam messages.

3. Small business owners or team leads
   People who want to keep a record of checked emails and review old results.

4. System administrator or project owner
   The person who maintains the application, trains the model again when needed, and checks the saved history data.

In this project, the interface is simple enough for non-technical users, so the main focus is everyday users who want a quick spam check.

## 2.3 Input Data to the System

The system accepts the following input data:

1. Email message text
   The user pastes the content of an email into the text box on the detector page.

2. Sample input messages
   The frontend also provides sample spam and safe messages for testing the system quickly.

3. Training dataset
   During model training, the system reads labeled email data from `spam.csv`.

4. History requests
   When the user opens the history page, the system receives requests to load saved records or export them as a CSV file.

The most important live input is the email message entered by the user. Without that message, the system cannot perform prediction.

## 2.4 Output Information from the System

After processing the input, the system gives the following output:

1. Prediction result
   The system tells whether the email is `spam` or `safe` (`ham` in the backend logic).

2. Confidence score
   The system shows how confident the model is in its prediction as a percentage.

3. Status message
   The user sees messages such as analysis in progress, completed, cleared, or error messages if something goes wrong.

4. Saved history record
   Each checked email is stored with:
- Record ID
- Email message
- Predicted label
- Confidence score
- Date and time of analysis

5. History summary
   On the history page, the user can see:
- Total checked emails
- Total spam emails
- Total safe emails

6. CSV export
   The system can generate a downloadable CSV file containing the full prediction history.

In simple language, the output is not only the spam result, but also a stored record that the user can review later.

## 2.5 Functional / Nonfunctional / Processing Requirements of the System

### A. Functional Requirements

These are the tasks the system must perform:

1. The system must allow the user to enter an email message.
2. The system must analyze the message using the trained machine learning model.
3. The system must classify the message as spam or safe.
4. The system must display the confidence score of the prediction.
5. The system must save every prediction in the history database automatically.
6. The system must allow users to view saved prediction history.
7. The system must show total, spam, and safe message counts.
8. The system must allow users to export history as a CSV file.
9. The system must handle invalid input, such as an empty message.
10. The system must load the saved model and vectorizer before prediction starts.

### B. Nonfunctional Requirements

These describe how well the system should work:

1. Usability
   The system should be simple, clear, and easy to use for non-technical users.

2. Performance
   The system should give prediction results quickly after the user submits a message.

3. Reliability
   The system should return correct responses when the backend, model files, and database are available.

4. Accuracy
   The prediction accuracy should be good enough to help users identify suspicious emails. Accuracy depends on the quality of the training data.

5. Maintainability
   The system should be easy to update, retrain, and improve in the future.

6. Data persistence
   The prediction history should remain saved even after the application is restarted.

7. Compatibility
   The system should run through a web browser and connect properly with the Flask backend.

### C. Processing Requirements

These explain how the system processes data step by step:

1. The user enters or pastes an email message into the web page.
2. The frontend sends the message to the backend using a POST request.
3. The backend checks whether the message is empty.
4. The message is converted into numerical features using the saved TF-IDF vectorizer.
5. The trained Logistic Regression model predicts whether the message is spam or ham.
6. The backend calculates the confidence score from the prediction probability.
7. The prediction result is saved into the SQLite history database with the current timestamp.
8. The result is sent back to the frontend and displayed to the user.
9. If the user opens the history page, the backend loads all saved records.
10. If the user clicks export, the backend creates a CSV file from the saved history.

In short, the system takes email text, converts it into a format the model understands, predicts the result, stores it, and shows it to the user.

## 3.1 Identify the Entities and the Attributes

In this project, the main data entity stored in the database is the prediction history of checked emails.

### Main Entity: Email History

This entity stores every email checked by the system and its result.

Attributes of `email_history`:

1. `id`
   A unique number for each record.

2. `message`
   The email text entered by the user.

3. `label`
   The prediction result. It can be `spam` or `ham`.

4. `confidence`
   The confidence score of the prediction.

5. `created_at`
   The date and time when the prediction was saved.

### Supporting Data Used by the System

These are important for the project, but they are not stored as database tables in the current version:

1. Training dataset
   Stored in `spam.csv`

   Main attributes:
- `label`
- `text`

2. Model files
   Stored as:
- `spam_model.pkl`
- `vectorizer.pkl`

So, in simple words, the actual database mainly stores prediction history, while the training dataset and model files are used by the system in the background.

## 3.2 E-R Diagram

The current project has one main database entity, so the E-R diagram is simple.

```text
+----------------------------------+
|          EMAIL_HISTORY           |
+----------------------------------+
| PK  id                           |
|     message                      |
|     label                        |
|     confidence                   |
|     created_at                   |
+----------------------------------+
```

Explanation:

- Each row in `EMAIL_HISTORY` represents one checked email.
- `id` is the primary key.
- In the current database, there is no second user-defined table, so there is no foreign key relationship.

## 3.3 Identifying All Tables, Fields, Relationship Between Tables etc.

### A. Main Table in the Project Database

Table name: `email_history`

Fields in the table:

1. `id`
- Data type: `INTEGER`
- Key: `PRIMARY KEY`
- Extra: `AUTOINCREMENT`
- Purpose: Identifies each record uniquely

2. `message`
- Data type: `TEXT`
- Constraint: `NOT NULL`
- Purpose: Stores the email content entered by the user

3. `label`
- Data type: `TEXT`
- Constraint: `NOT NULL`
- Purpose: Stores the prediction result (`spam` or `ham`)

4. `confidence`
- Data type: `REAL`
- Constraint: `NOT NULL`
- Purpose: Stores the confidence score of the prediction

5. `created_at`
- Data type: `TEXT`
- Constraint: `NOT NULL`
- Purpose: Stores the timestamp of the prediction

### B. Other Table Present in SQLite

Table name: `sqlite_sequence`

This is an internal SQLite system table. It is automatically used to manage the `AUTOINCREMENT` value of the `id` field. It is not part of the user-designed project data.

### C. Relationship Between Tables

In the current implementation:

- There is only one user-created table: `email_history`
- Therefore, there is no table-to-table relationship in the database
- There are no foreign keys in the present design

In simple language, the project currently uses a single table database. Each prediction is stored as one complete record.

## 3.4 Normalize Database

Normalization means arranging the database in a proper structure so that data is clean, clear, and not repeated unnecessarily.

### A. First Normal Form (1NF)

The table is in 1NF because:

- Each column stores only one value
- There are no repeating groups
- Each record is unique because of the `id` field

### B. Second Normal Form (2NF)

The table is in 2NF because:

- It already satisfies 1NF
- The primary key is a single field (`id`)
- All other fields depend fully on that primary key

### C. Third Normal Form (3NF)

The table is in 3NF because:

- It already satisfies 2NF
- Non-key fields do not depend on other non-key fields
- `message`, `label`, `confidence`, and `created_at` are stored directly for each prediction record

So, the current table structure is simple and already normalized enough for a small project.

### D. Possible Improved Normalized Design for Future Use

If the project becomes larger, the database can be split into separate tables to reduce repetition even more.

Example:

1. `emails`
- `email_id`
- `message`

2. `predictions`
- `prediction_id`
- `email_id`
- `label`
- `confidence`
- `created_at`

Relationship:

- One email in the `emails` table can be linked to one or more records in the `predictions` table

This design is better when:

- The same email is checked multiple times
- The system needs more reports
- The project grows in size

In short, the current database is already acceptable for this project, but a separate `emails` and `predictions` table design would be a more strongly normalized structure for future expansion.
