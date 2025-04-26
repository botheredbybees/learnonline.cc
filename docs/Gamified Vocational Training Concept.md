learnonline.cc will be a gamified vocational training web site using the training package, qualification, skill set, and unit of competency data available from the Australian Quality Training Framework (AQTF)



The AQTF XML data will be read by a python script using their SOAP API, with selected nodes being written to a PostgreSQL database.



I plan to use FastAPI for role based access to a vue.js front end. All servers will run in Docker containers and the source code will be stored on GitHub.



User types will be administrator, mentor, player, and guest. The mentor and student users will also have  level based permissions within their user type determined by the game elements of their training activities.



Administrators can run the XML acquisition script which interrogates the AQTF API looking for new or updated content. The script will also allow for filtering by training package, qualification, skill set, or unit code before interrogating the AQTF API.



Administrators can also set a 'hide' field in the relevant database records to prevent training packages, qualifications, skillets, or individual units from being displayed to users with lower privileges.



Mentors can create quests: collections of units of competency with optional pathways from unit to unit. These will be similar to AQTF skillsets and qualifications, which are official 'quests' in the context of the learnonline.cc environment.



Mentors can also create teams (equivalent to a class in college): collections of players; and see information about logins, duration spent on site, progress, results of quizzes, and contributions to the site made by each of their team members.



Players (students) can create quests (courses) if they progress to a high enough level in the game: lists of units, which can be edited and rearranged. They can also study individual units on the site.



The Web application will use python to gather and update the training information from the AQTF, and to help generate content for each unit's performance criteria, elements, and required skills using RAGS, LangChain, ChromaDB and a large language model along with the Gemini API along with FastAPI and a vue.js front end with Streamlit and H5P for the quiz elements.



The application will store content in the database once generated. Initially this generation of content will be on demand, a whenever a new unit is accessed. Subsequent calls will check to see if there is any updated information on the AQTF if there is it will update the database(s) before displaying the stored content.



Content will include summaries, Web links to sites and YouTube videos, multiple choice quizzes, fill in the blank questions, rearrange the steps questions, and longer free text answer questions, all generated from either a local LLM like llamafile or HuggingFace Transformers, or one of the free tiers or low-cost models available on HuggingFace Hub (or the Gemini API)



Players can gain points and levels by reading material, following links and completing quizzes. They can also gain points by suggesting new links, correcting or adding to content, and rating existing content elements.



Guests can access a limited set of units and associated content. This will be an introduction to the philosophy, pedagogy and Ui for the site and must be completed by anyone at least once before they can create an account.



Beyond the achievement system, progress visualisation, and points/levels already mentioned, learnonline.cc could also incorporate the following gamification elements:

Earning Points for Specific Actions: Students could gain points for various engagement activities within the platform, such as:
Reading learning materials.
Following provided web links and watching YouTube videos.
Successfully completing multiple-choice quizzes.
Answering fill-in-the-blank questions correctly.
Accurately rearranging steps in a process.
Providing thoughtful responses to longer free-text answer questions.
Community Contributions and Rewards: To foster a more collaborative learning environment, students could earn points for:
Suggesting new and relevant web links or YouTube videos that enhance the learning content.
Identifying and suggesting corrections to existing content.
Contributing additional relevant information to the learning materials.
Providing ratings or feedback on different content elements, helping to identify high-quality resources.
Leveling System: The defined user levels (Administrator, mentor, student, and guest) could be expanded into a more granular leveling system for students. Progression through these levels could be tied to the accumulation of points or the demonstration of specific competencies.
Gamified Learning Pathways: Mentors can create "skillets: collections of units of competency with optional pathways from unit to unit". These pathways could be presented in a gamified manner, perhaps with visual representations of progress along the path and rewards for completing milestones within a pathway.
Unlockable Content: As students progress and achieve certain levels or demonstrate specific competencies, they could unlock access to more advanced units, specialised content, or bonus materials.
Challenges and Leaderboards:  optional challenges related to specific units or skill sets, with points or badges awarded for successful completion. Leaderboards could create friendly competition amongst students (while being mindful of not discouraging those who may need more time or support).