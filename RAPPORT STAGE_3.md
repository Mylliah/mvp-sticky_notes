Stage 3 - Technical Documentation 
1. User Stories and Mockups 
MoSCoW method for prioritizing tasks: 
Must Have (essential for the MVP): 
1. As a user, I want to create a new, empty note using the "New +" button to quickly enter a 
task. 
2. As a user, I want the note to appear as a thumbnail in the dashboard as soon as it's 
created, so I can edit it. 
3. As a user, I want my note to be automatically saved (auto-save) while I'm writing it, so I 
don't lose anything. 
4. As a user, I want to close the note I'm writing with a "✕" button, so I can return to my list 
of notes knowing that it's saved. 
5. As a user, I want to be able to assign a note to a contact by dragging and dropping it 
from its thumbnail, with clear visual feedback (translucent ghost, contact highlighted 
when hovered over), so I can clearly understand the action. 
6. As a user, I want a note created from a contact tab (e.g., Laura) to be automatically 
assigned to that person, to simplify targeted creation. 
7. As a user, I want to be able to assign the same note to multiple contacts by successively 
dragging and dropping them, in order to share a collaborative task. 
8. As a user, I want my tiles to display status bullets (Important, In Progress, Completed, To 
[X], From [X]), to quickly distinguish their status and origin. 
9. As a user, I want to be able to filter my notes via clickable dots (Important, In progress, 
Completed, Received, Issued, Date ↑/↓), in order to efficiently sort my dashboard. 
Should Have (important but not vital): 
11.  As a user, I want a search bar to be visible at the top of the page (except on the 
"Settings" tab) to easily find any note. 
12. As a user, I want to be able to view, via a details icon in the open note, additional 
information such as the creation, sending, and modification dates, the read status 
("read") by recipients, and any local deletions (e.g., "deleted by Laura"), in order to 
improve transparency, tracking, and history. 
13. As a user, I want to receive visual confirmation when my note is assigned ("Note 
assigned to Laura") as well as an "Undo" button, so I can quickly undo the assignment if 
necessary. 
14. As a user, I want to be able to undo an assignment action (Undo 3–5 seconds or by 
releasing outside a contact) to correct an error or avoid an assignment error without 
having to go through a complex menu. 
Could Have (pleasant but not a priority): 
15. As a user, I want to be able to assign a note via an "Assign to..." context menu, so I can 
use the keyboard or a screen reader. 
16. As a user, I want to be able to enable a "multiple selection" mode to assign or complete 
multiple notes in a single action, to save time. 
17. As a user, I want a "New" icon to briefly appear on the note automatically assigned from 
a contact tab, to confirm that it has been accepted. 
18. As a user, I want to be able to mark certain received notes as high priority so I can 
decide their priority myself and thus process them more quickly. 
Won’t Have (explicitly excluded from the MVP) 
19. As a user, I will not receive real-time notifications (push or email) when notes are 
assigned. 
20. As a user, I will not have a native mobile app to manage my notes. 
21. As a user, I will not be able to integrate my notes with external services (Google 
Calendar, Slack, Trello). 
MVP Mockups :  
Justification of the graphic and ergonomic choices of the mockups 
The two mockups created for the MVP meet complementary needs: to facilitate handling for a 
non-technical audience, while ensuring clear visual organization and a seamless user 
experience. 
1. Colored Dashboard Mockup 
This mockup adopts a colorful palette, using pastel tones and illustrated visual elements 
(stylized icons, handwritten notes). This graphic design choice has several key objectives: 
● Make the interface user-friendly and engaging for users unfamiliar with digital tools. 
● Visually differentiate important elements (note issued, assignment, "important" status) 
through color and contrast, facilitating quick reading and action. 
● Stimulate memorization and adoption through visual codes reminiscent of the "Post-it" 
system, intuitive and reassuring. 
● The recipient panel on the right "pops" with a colored hover effect, allowing for clear 
drag-and-drop interaction, with immediate visual feedback on the action. 
● Priority is given to the "central note," which opens wide for editing or viewing, thus 
focusing activity around essential information. 
This approach promotes the personalization of uses and simplicity of action, while highlighting 
multiple recipients through a clear, contrasting, and interactive display. 
2. Simple Dashboard Mockup 
Here, the style is deliberately simple and clean: 
● Predominantly black and white: a choice motivated by the desire to enhance readability 
and not distract the user with graphics. 
● Convene grid organization: each note is clearly structured, displaying essential 
information (creator, recipient, status) without unnecessary additions. 
● Top filter and sorting bar: accessible, intuitive, allows for quick and efficient navigation 
even in large volumes of tasks. 
● Icons and buttons: minimalist and simple, promoting ergonomics without visual overload. 
This design meets the need for "professional" management: the clean table facilitates 
monitoring, sorting, and prioritization, essential for intensive daily use. This type of interface is 
perfectly suited to a "power user" mode, complementing the more "general public" color view. 
Current Status and Outlook 
At this stage of the project, the final choice of user interface has not yet been made. The two 
mockup proposals offer complementary approaches: colorful and engaging for intuitive handling, 
and simple and refined for efficient professional management. These versions are the basis for 
reflection that will undergo user testing and iterations to validate the best user experience (UX). 
The goal is to gather concrete feedback, observe ease of use, readability, and target user 
satisfaction in order to adjust and refine the design. The project remains open to the adoption of 
a single or hybrid graphic direction depending on the results of the prototyping and validation 
phases. 
This experimentation phase is essential to ensure that the final interface is truly adopted by 
users, easy to understand, and effective in their daily use. 
2. System Architecture 
1. Project Architecture 
Architecture diagram 
Tree structure 
Content of each folder: 
● User vs Contact 
● User = application account (can log in, has a JWT, creates notes). 
● Contact = assignable recipient (can be a referenced internal user or an external 
contact without an account). 
● The Assignment relationship links Note ↔ Contact (and not Note ↔ User), to allow 
assignment to external users. 
● If a Contact corresponds to an internal User, we can store contact.user_id (nullable) 
to link it to the account. 
● Assignment 
● Join table with UNIQUE constraint (note_id, contact_id). 
● Used for access rules (note creator or assigned contact). 
● ActionLog 
● Logs important events: payload, created_at (create_note, assign_contact, 
update_note, etc.). 
● Useful for auditing, debugging, and product metrics. Excluding critical workflows, 
therefore not blocking in case of failure (best effort). 
● Corresponding Endpoints 
● /api/v1/contacts: minimal search/list/CRUD of contacts. 
● /api/v1/assignments: creates/delete Note↔Contact links. 
● /api/v1/notes: CRUD + filters (visibility = creator or assigned contact). 
● /api/v1/auth/*: login, me (JWT).. 
● Security & Visibility 
● Access to a note if: creator_user_id == me or EXISTS assignment(note_id, 
contact_id linked to me if I am internal). 
● For external contacts, no application access (no login). They are only recipients 
“referenced” by the author. 
2. Diagramme d’architecture en 3 couches 
a. Presentation Layer 
This is the layer visible to the user—the interface with which they interact. 
It consists of a React application (Single Page App), displaying the dashboard, note 
thumbnails, filters, the drag-and-drop area, and the contact list. 
It includes interface controllers (an abstract concept on the front-end side) that drive API calls: 
● UserController: manages the current user (profile, login, etc.). 
● NoteController: creates, edits, and autosaves notes. 
● AssignmentController: assigns notes to contacts. 
● ContactController: loads and displays available contacts. 
● ActionLogController: displays or sends actions to the log (optional in the MVP).  
When a user performs an action (e.g., creating a note, dragging a thumbnail, clicking "Close"), 
this layer: 
● prepares the JSON request, 
● calls the corresponding REST API, 
● updates the interface with the server response (optimistic UI + toasts). 
b. Business Logic Layer 
This is the heart of the application—the business logic. 
This layer is implemented in Python with Flask + SQLAlchemy. It receives REST requests 
from the frontend, processes them, applies business rules, and communicates with the 
database via the ORM. 
It contains dedicated services: 
● UserService: access validation, user creation, profile management. 
● NoteService: creation, editing, automatic backup, filtered retrieval. 
● AssignmentService: assignment or multi-assignment of notes to users. 
● ContactService: retrieval of the list of visible contacts. 
● ActionLogService: logging user actions in the activity_log (optional in the MVP but ready 
for extension). 
This layer enforces privacy rules: 
E.g., only the creator or an assigned recipient can access a note. 
It can also integrate external services in the future (such as OAuth authentication, cloud 
storage, etc.). 
c. Persistence Layer 
This is the data access layer—the relational database. 
It is managed via SQLAlchemy (ORM) and can use: 
● SQLite for local development, 
● PostgreSQL for production (e.g., Render, Fly.io, etc.). 
It contains the following data models: 
● UserModel: identifiers, user profile. 
● NoteModel: content, status, importance, timestamps. 
● AssignmentModel: N-N join table between notes and recipients. 
● ContactModel: (optional in MVP) custom contact list if implemented. 
● ActionLogModel: action logging (assignment, editing, deletion, etc.). 
Each model corresponds to a table. 
CRUD operations are triggered by the business layer services. 
How do the layers communicate? 
User → UI → API call → controller (React) 
→ Flask REST API → business service (validation, logic) 
→ model access → ORM query → database. 
← JSON result → UI display (toasts, updates, filters) 
Why this architecture? 
● Separation of responsibilities (view, logic, data) 
● Modularity (can change React or Flask without breaking everything) 
● Scalability (ability to add authentication, logging, complex filters) 
● Clarity: each layer has a specific role—which facilitates maintenance, testing, and code 
review. 
3. Components, Classes, and Database 
Design 
1) Class Diagram (object view) 
What it shows 
The object view of the application (code side): 
● Classes: User, Note, Assignment, Contact, ActionLog. 
● Attributes: application types (string, datetime, bool, int). 
● Indicative methods (e.g., Note.update_content(), Assignment.mark_as_read()), which 
reflect the MVP use cases. 
● Associations with multiplicities ("1", "*"): 
○ User creates Note (1→*) 
○ Note assigned to User via Assignment (↔) 
○ User owner of Contact (1→*) 
○ User performs ActionLog (1→*) 
○ ActionLog targets Note (→0..1) 
Why this choice? 
● Serves as a contract between the front-end and back-end: it clarifies the expected 
behavior of classes and the methods exposed by services. 
● Facilitates functional review (association verbs are similar to user stories).  
● Prepares for serialization (DTO/API): Attributes and operations guide payloads. 
Key Design Points 
● Assignment as a dedicated class: clearly separates note creation and assignment 
(status per recipient: assigned_date, is_read). 
● ActionLog externalizes auditing (who/when/what/target), extensible with payloads. 
● Technical identifiers (id): robust for unambiguous mapping to the database. 
2) Entity-Relationship (ER) Diagram (Relational Logical View) 
What it shows 
The relational structure as it will be stored: 
● USERS(PK id, username, email, password_hash, created_date) 
● NOTES(PK id, content, status, important, dates…, creator_id FK→USERS) 
● ASSIGNMENTS(PK id, note_id FK→NOTES, contact_id FK→CONTACTS, 
assigned_date, is_read) 
● CONTACTS(PK id, user_id FK→USERS, contact_user_id FK→USERS, nickname, 
contact_action, created_date) 
● ACTIONLOGS(PK id, user_id FK→USERS, target_id FK→NOTES NULL, action_type, 
timestamp, payload) 
Why this choice? 
● This is the exact map of the relational database: tables, PK/FK, direction of 
dependencies. 
● Used to generate SQL DDL (migrations) and prepare indexes/constraints. 
Recommended Constraints/Indexes 
● USERS: UNIQUE(username), UNIQUE(email). 
● ASSIGNMENTS: UNIQUE(note_id, contact_id) (no duplicate assignments). 
● CONTACTS: UNIQUE(user_id, contact_user_id), CHECK (user_id <> contact_user_id). 
● Repository: ON DELETE CASCADE for ASSIGNMENTS and CONTACTS; ON DELETE 
SET NULL for ACTIONLOGS.target_id (keeps track of whether a note is deleted). 
Benefits 
● Normalization (3FN): No multivalued attributes or misplaced transitive dependencies. 
● Scalability: Easy to add assignment fields (due_date, priority) or extend ActionLog. 
3) Merise Diagram – MCD (conceptual view) 
What it shows 
The DBMS-independent business model: entities, attributes, verbalized associations, and 
cardinalities (min, max). 
● Main associations: 
○ create: USER (1,1) → NOTE (0,n) (a note always has 1 creator) 
○ note_assignment: NOTE (0,n) ↔ ASSIGNMENT (1,1) 
○ user_assignment: USER (0,n) ↔ ASSIGNMENT (1,1) 
○ owns: USER (1,1) → CONTACT (0,n) (personal notebook) 
○ aims: CONTACT (0,n) → USER (1,1) (the contact refers another user) 
○ performs: USER (1,1) → ACTIONLOG (0,n) 
○ target: ACTIONLOG (0,n) → NOTE (0,1) (a log may not target a note) 
Why this choice? 
● Clarifies business semantics (verbs become rules) before any implementation.  
● Provides direct traceability: MCD (conceptual) → ER/MLD (logical) → DDL (physical). 
Justified key decisions 
● Separate "creation" and "assignment": allows self-assignment but maintains two 
distinct business concepts. 
● ASSIGNMENT associative entity: essential for carrying attributes per recipient 
(is_read, assigned_date) and imposing UNIQUE (note_id, contact_id). 
● ACTIONLOG for auditing and extensibility (payload). 
● Technical identifiers on all entities: robustness of FKs and indexes. 
How the three views complement each other: 
Need 
Explain domain behavior to 
developers and the PO 
Most useful 
diagram 
Classes 
Reason 
Methods + multiplicities close to user 
stories 
Define the base and its 
FK/constraints 
Freeze the business meaning (who 
does what, on what) 
Traceability: 
ER 
Logical diagram ready for DDL 
Merise MCD Verbalized associations + minimal 
cardinalities 
● User.create() ↔ association create ↔ FK NOTES.creator_id. 
● Assignment (class) ↔ entity ASSIGNMENTS (ER) ↔ associations 
note_assignment/user_assignment (MCD). 
● ActionLog.log_action() ↔ ACTIONLOGS (ER) ↔ performs/target (MCD). 
● Contact (class) ↔ CONTACTS (ER) ↔ owns/aims (MCD). 
Conclusion: 
➢ The MCD ensures business consistency. 
➢ The ER diagram translates this business into a solid, standardized, and maintainable 
relational schema. 
➢ The class diagram guides the implementation (services, methods, DTOs), while 
remaining aligned with the schema. This set provides a complete technical plan for the 
MVP: readable by stakeholders, implementable by devs, and stable for the future (tests, 
migrations, scaling). 
4) MPD — Physical Data Model (PostgreSQL) 
 
CREATE TABLE users ( 
    id SERIAL PRIMARY KEY, 
    username VARCHAR(255) UNIQUE NOT NULL, 
    email VARCHAR(255) UNIQUE NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
); 
 
CREATE TABLE notes ( 
    id SERIAL PRIMARY KEY, 
    content TEXT NOT NULL, 
    status VARCHAR(50) NOT NULL, 
    creator_id INT NOT NULL REFERENCES users(id) ON DELETE RESTRICT, 
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    delete_date TIMESTAMP NULL, 
    read_date TIMESTAMP NULL 
); 
 
CREATE TABLE assignments ( 
    id SERIAL PRIMARY KEY, 
    note_id INT NOT NULL REFERENCES notes(id) ON DELETE CASCADE, 
    user_id INT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE, 
    assigned_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    is_read BOOLEAN NOT NULL DEFAULT FALSE 
); 
 
CREATE TABLE contacts ( 
    id SERIAL PRIMARY KEY, 
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
    contact_user_id INT NULL REFERENCES users(id) ON DELETE SET NULL, 
    -- external identity (nullable): used when contact_user_id is NULL 
    name VARCHAR(255) NULL, 
    email VARCHAR(255) NULL, 
    nickname VARCHAR(255), 
    contact_action VARCHAR(50), 
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
); 
 
CREATE TABLE actionlogs ( 
    id SERIAL PRIMARY KEY, 
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
    action_type VARCHAR(100) NOT NULL, 
    target_id INT NULL REFERENCES notes(id) ON DELETE SET NULL, 
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    payload TEXT 
); 
Presentation of the PDM Diagram (SQL): 
The Physical Data Model (PDM), represented here by the diagram and the SQL script for table 
creation, is the technical and operational translation of the conceptual (CDM) and then logical 
(LDM) model designed upstream. It materializes the actual structure of the relational database 
that will be used by the application. 
● The PDM precisely defines for each table: 
● the actual names of the tables and columns, 
● the type of each data item (int, varchar, boolean, datetime, etc.), 
● the primary (PK) and foreign (FK) keys, uniqueness and integrity constraints, cascading 
actions, and sometimes additional indexes. 
How the PDM Works in the Project: 
Each business entity (user, note, contact, assignment, etc.) becomes a table, and each 
relationship or association (e.g., assigning a note to a user) is translated either by a foreign key 
or an association table. 
● 1,N relationships: modeled by a foreign key, on the "N" side. 
● N,N relationships: modeled by an intermediate table (e.g., assignments for user-note 
assignments). 
● Constraints: Each table imposes SQL constraints to ensure integrity (foreign keys, 
cascading deletion, etc.). 
Thanks to the PDM, all business operations (note creation, assignment, contact sharing, 
logging, etc.) are translated into efficient, consistent, and secure SQL operations. 
Why this choice? 
1. Standardization and Performance 
○ The relational schema derived from the PDM is standardized: it avoids 
redundancy, optimizes storage, and simplifies maintenance and data model 
upgrades. 
○ Interactions between tables are explicit and guaranteed by the SQL engine. 
2. Security and Integrity 
○ The use of foreign keys and constraints makes it possible to detect and prevent 
any inconsistencies or referential integrity errors in the data (for example, 
preventing a user from being deleted if they have related notes or logs). 
○ Adapted types prevent incorrect formatting (e.g., dates or Booleans are correctly 
managed). 
3. Interoperability and Portability 
○ The PDM (SQL) is based on a standard language understood by the main 
relational DBMSs (PostgreSQL, MySQL, MariaDB, etc.). 
○ It reliably automates database creation and migration.  
4. Traceability and Scalability 
○ Any changes to the model are clearly reflected in the MPD: addition of features, 
new tables, history management, etc. 
○ The database remains readable, documented, and adapted to the application's 
scalability. 
Conclusion 
The MPD diagram (and the associated SQL script) is the concrete foundation of the project 
database. It provides a solid, professional, scalable, and secure structure. Its rigorous design 
based on the MCD/MLD ensures that functional needs, business logic, and robustness 
requirements are fully covered in the chosen technical solution. 
4. Sequence Diagrams 
1) "My Tasks" table — retrieving & filtering visible notes 
Context 
The user opens their board. The front-end must list only the notes they have permission to view 
(created by them or assigned to them) and apply filters (e.g., visible=true, status, date). 
Actors & Roles 
● User: Triggers the consultation. 
● DashboardController (front-end): Orchestrates the call and prepares the display. 
● PortfolioFacade (back-end API): Business entry point (aggregates/validates). 
● NoteModel: Filtering logic (access rules, filterable fields). 
● NoteRepository: Data access (SQL/ORM queries). 
● Database: Persistent storage. 
Detailed Process 
1. User → DashboardController: GET /api/v1/notes?filter=visible 
● Triggers retrieval with current filters (here: visibility). 
2. DashboardController → PortfolioFacade: get_visible_notes(user_id, filters) 
● The front-end transmits the identity (session) + filters to the back-end. 
3. PortfolioFacade → NoteModel: filter_notes(user_id, filters) 
● The facade delegates the construction of authorized criteria to the domain. 
4. NoteModel → NoteRepository: fetch_notes(user_id, filters) 
● The model translates the rules (user scope + filters) into queries. 
5. NoteRepository → Database: SELECT * FROM notes WHERE user_id=? AND 
visible=TRUE AND ... 
● Execution with secure settings (?) + filter clauses. 
6. Database → NoteRepository: Resultset of visible notes 
● Raw return of matching rows. 
7. NoteRepository → NoteModel: Filtered notes 
● SQL mapping → objects/DTOs, possible enrichments. 
8. NoteModel → PortfolioFacade: List of notes 
● Return of the consolidated result set on the domain side. 
9. PortfolioFacade → DashboardController: Data ready 
● Final payload: notes + meta (counters, pagination, etc. if provided). 
10. DashboardController → User: 200 OK { notes: [...] } 
● Rendering of the list with filters enabled. 
Alternative Scenarios / Errors 
● 0 results: return 200 [] (no error; UI displays an empty state). 
● Invalid filters: 400 Bad Request (values  outside the scope). 
● Invalid session: 401 Unauthorized. 
Validations & Security 
● The scope is determined by user_id (creator or assignee) — limit it to visible=TRUE 
here, but the full logic can include OR assigned(user_id) if that's the MVP scope. 
● Prepare a whitelist of filterable fields (avoids logic injection). 
● Systematically parameterize queries. 
Data exchanged (examples) 
● Request: GET /api/v1/notes?filter=visible&status=todo&sort=updated_at 
● Response: [{ id, content, status, important, creator_id, assignees[], 
created_at, updated_at }] 
Points of attention 
● Pagination (if the list grows). 
● DB index on (user_id, visible, status, updated_at) for common filters. 
● UI consistency: filters reflect the URL (shareable permalink). 
2) Login — Obtain a secure session 
Context 
The user authenticates. The email is validated, the hashed password is compared, and a 
session token is issued if OK. 
Actors & Roles 
● User: Provides email + password. 
● AuthController (front): Sends the login request, handles feedback. 
● PortfolioFacade (back): Coordinates authentication. 
● UserModel: Authentication logic (validation, hash verification, token generation). 
● UserRepository: Reads the user by email. 
● Database: User persistence. 
Detailed Process 
1. User → AuthController: POST /login { email, password } 
2. AuthController → PortfolioFacade: authenticate_user(email, password) 
3. PortfolioFacade → UserModel: validate_credentials(email, password) - 
Checks email format, password rules (not empty, etc.). 
4. UserModel → UserRepository: find_user_by_email(email) 
5. UserRepository → Database: SELECT * FROM users WHERE email=? 
6. Database → UserRepository: User data 
7. UserRepository → UserModel: User found or none 
8. UserModel (internal): check_password_hash(password) 
Alternate Block 
9. UserModel (internal): generate_session_token() (JWT or session ID) 
10. UserModel → PortfolioFacade: Valid Token 
11. PortfolioFacade → AuthController: Auth successful, token 
12. AuthController → User: 200 OK {token, user_info} 
Incorrect Password 
13. UserModel → PortfolioFacade: Authentication Error 
14. PortfolioFacade → AuthController: Auth failed 
15. AuthController → User: 401 Unauthorized 
Validations & Security 
● Always server-side hashing (e.g., bcrypt/argon2); never cleartext passwords. 
● Constant response time (avoids time-based leaks). 
● Time-limited token + refresh if necessary. 
● After success: store the token in memory / httpOnly cookie (depending on the MVP 
security choice). 
Data exchanged (examples) 
● Success response: {token, user_info: {id, email, name}} 
● Failure: {error: "Invalid credentials"} 
Points of attention 
● Lockout / backoff after X failures. 
● Audit logs (connection, failures, IP). 
● Logout flow (server-side invalidation if sessions). 
3) Creating a note → assigning by drag-and-drop (multi-recipients) 
Context 
The user creates a note, then drags it to several contacts to assign it. Each assignment creates 
a note ↔ contact link. 
Actors & Roles 
● User: Enters and drags the note. 
● NoteController (front): Manages creation + assignment DnD. 
● PortfolioFacade (back): Coordinates validation + persistence. 
● NoteModel / NoteRepository: Validates and saves the note. 
● AssignmentModel / AssignmentRepository: Validates and saves assignments. 
● Database: Persistence. 
Detailed Process 
A) Creating the Note: 
1. User → NoteController: POST /notes {content} 
2. NoteController → PortfolioFacade: create_note(note_data, user_id) 
3. PortfolioFacade → NoteModel: validate_note_data() - 
check_content(): not empty, maximum length, prohibited characters, etc. - - 
generate_uuid(): unique ID on the domain side. 
set_timestamps(): created_at, updated_at. 
4. PortfolioFacade → NoteRepository: save_note(note_instance) 
5. NoteRepository → Database: INSERT INTO notes VALUES (...) 
6. Database → NoteRepository: Creation confirmation 
7. NoteRepository → PortfolioFacade: Note created 
8. PortfolioFacade → NoteController: note_id + status success 
9. NoteController → User: 201 Created { note_id, message } - 
UI: Displays the new note card (optimistic UI possible). 
B) Drag-and-drop assignment (multi-contact loop): 
For each selected contact_id: 
10. User → NoteController: Drag-drop note → contact_id 
11. NoteController → PortfolioFacade: assign_note(note_id, contact_id, user_id) 
12. PortfolioFacade → AssignmentModel: validate_assignment() - 
check_contact_exists() / check_note_exists() - - 
generate_uuid() (assignment ID), set_timestamps() 
Check permission: creator or already assigned. 
13. PortfolioFacade 
→ 
AssignmentRepository: 
save_assignment(assignment_instance) 
14. AssignmentRepository → Database: INSERT INTO assignments VALUES (...) 
15. Database → AssignmentRepository: Assignment confirmation 
16. AssignmentRepository → PortfolioFacade: Assignment created 
17. PortfolioFacade → NoteController: Confirmation 
18. NoteController → User: Toast “Assignment successful” 
Alternative Scenarios / Errors 
● Non-existent note: 404 Not Found. 
● Non-existent contact: 404 Not Found. 
● Duplicate assignment (same note, same contact): 409 Conflict (uniqueness 
constraint on the DB side). 
● Insufficient rights: 403 Forbidden. 
Validations & Security 
● Access rule: Only the creator and recipients can see the note. 
● Integrity: UNIQUE(note_id, contact_id) constraint on assignments. 
● Front-end idempotence: Ignore repeated successes, disable the button during the 
request. 
Data exchanged (examples) 
● POST /notes → 201 { id, content, status="todo", important=false, 
created_at } 
● POST /assignments → 201 { assignment_id, note_id, contact_id } 
Points of attention 
● Clear drag-over UX (valid/invalid target). 
● In case of massive multi-assignment: make requests in batches or parallelize with 
concurrency limits. 
● Rollback strategy if an assignment out of N fails (all or nothing vs. continuous). 
5. API Specifications  
1. External APIs 
Decision: No external APIs will be consumed at the MVP level. 
Possible future developments (outside the MVP scope): 
● User avatars (e.g., Gravatar/Libravatar) for visual contact rendering.

2. Internal API – General 
Principles Details 
URL Base /api/v1 
Input/Output Format JSON (Content-Type: application/json) 
Authentication JWT Bearer – header Authorization: Bearer 
<token> 
Versioning Included in the /v1 URL 
Success Codes 200 OK, 201 Created, 204 No Content 
Error Codes 400, 401, 403, 404, 409, 422, 500 
Error Format {"error":{"code":"invalid_input","message":"...","d
 etails":{}}} 
Pagination Parameters page, limit → 
{"items":[...],"page":1,"limit":20,"total":57} 
Filtering/Sorting Parameter whitelist (status, important, q, sort, 
order) 
 
Auth 
● POST /auth/login — Authenticate and issue a token. 
Input: email, password. Output: token, minimal user. Auth: no. 
● GET /auth/me — Current profile / Verify token. 
Input: —. Output: minimal user. Auth: yes. 
Contacts (recipients) 
● GET /contacts — List/search assignable contacts (paginated). 
Input: Search, page/limit. Output: Contacts list. Auth: yes. 
Notes 
● GET /notes — List visible notes (created by me or assigned to me), with filters. 
Input: Filters (status, important, text), sort, page/limit. Output: Notes list. Auth: yes. 
● POST /notes — Create a note. 
Input: Content (+ optional important). Output: Note created. Auth: yes. 
● GET /notes/{id} — Note details (access control). 
Input: id. Output: Detailed note. Auth: Yes. 
● PATCH /notes/{id} — Partial update (content, status, important). 
Input: Fields to edit. Output: Note updated. Auth: Yes. 
● DELETE /notes/{id} — Delete a note (creator). 
Input: id. Output: — (204). Auth: Yes. 
Assignments (Note ↔ Contact) 
● POST /assignments — Assign a note to a contact. 
Input: note_id, contact_id. Output: Assignment created. Auth: yes. 
● DELETE /assignments/{id} — Remove an assignment. 
Input: assignment id. Output: — (204). Auth: yes. 
● GET /notes/{id}/assignees — List the recipients of a note. 
Client Errors 
400 — Bad Request (malformed request) 
● When: missing body, unexpected field, unauthorized sorting/filters, out-of-scope value 
(e.g., sort=foobar). 
● Examples: GET /notes?order=sideways, POST /notes without a body. 
401 — Unauthorized (unauthenticated) 
● When: missing Authorization header or invalid/expired JWT token. 
● Examples: accessing /notes without a token; token expired during a PATCH 
/notes/{id}. 
403 — Forbidden (auth OK but insufficient privileges) 
● When: the user is authenticated but does not have the right to act/view. 
● Examples: deleting a note that did not create; attempting to assign a note to which do 
not have access. 
404 — Not Found (resource not found or hidden) 
● When: The ID doesn't exist, or the resource exists but is not visible to the user (do not 
"reveal" its existence). 
● Examples: GET /notes/{id} on someone else's note without an assignment; DELETE 
/assignments/{id} if it doesn't exist. 
409 — Conflict (state conflict) 
● When: The request violates a uniqueness constraint, or the current state prevents the 
action. 
● Example: POST /assignments with an existing (note_id, contact_id) pair; attempt to 
create two notes with the same business key if have one. 
415 — Unsupported Media Type 
● When: Unsupported content type (other than application/json). 
422 — Unprocessable Entity (validation failed) 
● When: The request is well-formed, but the business rules fail. 
● Examples: empty or too long content; invalid status; unknown contact_id during an 
assignment. 
429 — Too Many Requests (rate limit) 
● When: Anti-abuse protection (e.g., too many attempts on /auth/login). 
Server Errors 
500 — Internal Server Error 
● When: Unhandled exception, unexpected outage. 
● Action: Log on the server side and return a generic message on the client side. 
503 — Service Unavailable 
● When: Maintenance, dependency unavailable (e.g., database). 
● Recommend a retry after a timeout. 
Formatting Recommendations (Consistency) 
● Clear and actionable message: Short sentence explaining the cause (e.g., “Missing 
Authorization header,” “Unknown filter ‘foo’”). 
● Stable application code: A short key (e.g., , ,, invalid_input 
not_found 
forbidden 
duplicate_resource) that the front-end can plug in. 
● Optional details: List of invalid fields, unauthorized filter, expected value (useful for 
400/422). 
● No information leaks: For 403/404 errors on non-visible resources, remain neutral (“not 
found” rather than “exists but forbidden” if want to hide their existence). 
● Uniformity: Same error structure on all endpoints, same labels for the same causes. 
Endpoint Reminders (Reminders) 
● /auth/login: 400 (format), 401 (invalid credentials), 429 (rate limit). 
● /notes (GET): 400 (filters/sorting not whitelisted), 401. 
● /notes/{id} (GET): 401, 404 (not visible or nonexistent). 
● /notes (POST): 401, 422 (content validation). 
● /notes/{id} (PATCH): 401, 403 (no permission), 404, 422 (rules). 
● /notes/{id} (DELETE): 401, 403 (sole creator), 404. 
● /assignments (POST): 401, 403 (no access to note), 404 (note/contact), 409 
(duplicate), 422 (validation). 
● /assignments/{id} (DELETE): 401, 403, 404. 
● /contacts (GET): 401, 400 (invalid pagination). 
6. SCM and QA Plans  
Source Code Management (SCM) Plan and Quality Assurance (QA) Strategy 
1. Version Control (SCM) 
Chosen tool: Git, hosted on GitHub. 
Primary branches: 
● main: Stable branch containing the production release. 
● development: Aggregates validated features for the next release. 
● feature/<feature-name>: Dedicated branch for a new feature or bug fix, created from 
development. 
Workflow: 
● Each task is developed in a dedicated feature branch. 
● Features are merged into development via pull requests after peer code review. 
● Merges into main occur only after full validation in the staging environment. 
Best practices: 
● Make frequent, concise commits with clear, descriptive messages. 
● Use GitHub issues for ticket tracking and prioritization. 
● Enforce mandatory code reviews to ensure quality and consistency. 
2. Quality Assurance (QA) Strategy 
Types of tests: 
● Unit tests: Validate isolated functions in the backend (Flask) and frontend (React). 
● Integration tests: Verify module interactions, especially API calls and database access. 
● End-to-end (E2E) tests: Simulate complete user scenarios (e.g., creating, assigning, 
editing notes). 
● Manual tests: UX/usability checks and final validation before release. 
Chosen tools: 
● pytest for backend unit and integration tests (Python). 
● Jest for frontend unit tests (JavaScript/React). 
● Postman for exploratory and automated testing of REST endpoints. 
● Cypress can be added later for automated frontend E2E tests. 
Deployment process: 
● Continuous Integration runs unit and integration test suites on every push to 
development. 
● Automatic deployment to the staging environment after tests pass. 
● Manual validation on staging, then production deployment via merge to main. 
● Post-production monitoring to detect errors and anomalies. 
This policy ensures robust source control, secure and smooth collaboration, and sustained 
product quality throughout the lifecycle. 
7. Technical Justifications 
This section explains the MVP’s technology choices and how they satisfy the functional 
requirements (create/assign notes, filter, access control) and non-functional requirements 
(simplicity, time-to-MVP, security, maintainability). 
Frontend: React (SPA) 
➔ Why React SPA? 
● Simplicity & speed: mature ecosystem, fast bootstrapping (Vite), reusable 
components. 
● Smooth UX: rich interactions (drag-and-drop assignments), instant filtering 
without full page reloads. 
● Maintainability: clear separation of components/pages/services; testable with 
RTL/Jest. 
➔ Covered needs: visual note manipulation (sticky-note metaphor), immediate feedback 
(optimistic UI), UI scalability. 
Backend: Flask + SQLAlchemy 
➔ Why Flask? 
● Minimal yet extensible: ideal for an MVP with clean REST endpoints. 
● Clarity: routes, middlewares (auth, CORS), and modular structure 
(api/services/models). 
➔ Why SQLAlchemy? 
● Productivity: ORM mapping, migrations (Alembic), straightforward model-level 
validation. 
● Portability: develop on SQLite, run PostgreSQL in production with no code 
changes. 
➔ Covered needs: stable /api/v1/* endpoints, access rules (creator/assignee), business 
validations. 
Database: PostgreSQL (prod) / SQLite (dev) 
➔ Why PostgreSQL in production? 
● Robustness & integrity: strong constraints (UNIQUE, FK, CHECK), transactions, 
advanced indexing. 
● Vertical scalability: solid performance for filtered/ordered queries at MVP scale. 
Why SQLite in development? 
● Time-to-MVP: zero setup, very fast dev/test cycle. 
● Covered needs: data consistency (notes/assignments/contacts) and performant 
filters/sorts. 
Authentication: JWT (Bearer) 
➔ Why JWT? 
● Simple for SPA: send token via Authorization, stateless API. 
● Security: short-lived tokens, controlled claims, centralized verification 
(middleware). 
➔ Covered needs: quick access control (creator or recipient), clean front/back separation, 
extensible to roles later. 
No External APIs in the MVP 
➔ Why no external dependencies? 
● Risk reduction (latency, quota, third-party outages). 
● Faster time-to-MVP: focus on core value (create/assign/filter). 
● Security & compliance: fewer secrets/API keys to manage. 
➔ Future options: avatars, emails, SSO can be added without changing the core 
architecture. 
Data Model & Constraints (UNIQUE, FK, cascades) 
➔ Key constraints: 
● ASSIGNMENTS.UNIQUE(note_id, contact_id) → no duplicate assignment. 
● FKs (e.g., notes.creator_id → users.id, assignments.contact_id → 
contacts.id) → referential integrity. 
● Controlled cascades (e.g., ON DELETE CASCADE on assignments) → clean 
deletions without orphans. 
➔ Benefits: 
● Data safety enforced at the database level (prevents inconsistencies). 
● Performance via targeted indexes (status, dates, creator) for filtered lists. 
Alignment with Non-Functional Requirements 
● Simplicity: minimal stack (React/Flask/SQLAlchemy), clear 3-layer architecture. 
● Time-to-MVP: quick bootstrap (Vite, Flask), SQLite in dev, simple migrations. 
● Security: JWT, DB constraints, service-level access control, standardized error handling 
(401/403/404/409/422). 
● Maintainability: separation of api / services / models / persistence, unit/integration 
tests, code conventions. 
● Evolvability: PostgreSQL in prod, API versioning (/v1), support for external Contacts, 
generalized ActionLog, notifications later. 
Conclusion 
These choices maximize delivery speed and clarity while ensuring security and quality. They 
form a solid base for iteration: new features (batch assignments, notifications), reasonable 
scale-up, and a low complexity cost over time.