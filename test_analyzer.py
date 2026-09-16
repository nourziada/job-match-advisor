from tools.analyzer import analyze_job

# Paste a real job posting here to try the analyzer
sample_job = """
Who we are:Open-minded intellectuals who embrace emerging technologies on our mission to create innovative Software Engineering Solutions that will impact millions of users around the world.

What you will do:
Full lifecycle software development (design specification and system architecture, coding, testing, debugging and rollout)
Design of software solutions based on client requirements and business needs
Development of web software solutions according to specification
Unit testing and performance testing
Technical support activities
Providing estimation of development
Code review, bug assignments and bug fixing
Write technical specification and technical documentation
Active participation at technical meetings
Technical coach for the development team members
Focus on delivering high quality software components and products on-time, according to project timelines.


What we are looking for:
Minimum 3- 4 years of experience in full-lifecycle projects.
Design and development of web applications using: PHP and HTML/CSS and JavaScript (jQuery, VueJS or ExtJS) and AJAX.
Programming and use of databases: MySQL, Oracle, MS SQL Server or similar - knowledge of DDL/DQL queries, not just the use of visual tools
Minimum 1 year of experience in full-lifecycle projects in which he/she has performed activities of: Development of REST or SOAP web services APIs
Object oriented programming (especially PHP5)
Working experience with web development frameworks: Laravel/Lumen, CodeIgniter, VueJS
Web security techniques
Working experience with versioning systems (GIT/SVN/)
Experience working with Jira
ETL: Pentaho
Other RDBMS (Relational Database Management System)
Apache configuration and administration
Unix/Linux configuration and administration
Tools:
PhpStorm
Navicat or SQLyog or alternative
TortoiseSVN
Putty

#LI-DG1
What's in it for you:
Extended compensation and benefits package
Continuous learning opportunities to enhance your professional and soft skills
A great working environment with people who put their heart, mind, and soul into everything they do and understand the importance of team spirit

We really welcome open-minded and committed people:
Eager to take on new challenges and learn new things;
Who put their heart, mind, and soul into everything they do;
Who enjoy sharing knowledge and understand the importance of team spirit.

Note*SII Romania is proud to be an equal opportunity workplace. We are committed to promoting diversity, equality and inclusion within our workforce and working environment. For this purpose, we encourage all qualified candidates regardless of gender, age, sexual orientation, race ethnicity, beliefs, marital status, disability or other characteristics to send us their applications.
"""

result = analyze_job(sample_job)
print("Decision:", result["decision"])
print("Confidence:", result["confidence"])
print("Matched skills:", result["matched_skills"])
print("Missing skills:", result["missing_skills"])
print("\nBreakdown:")
for r in result["reasoning"]:
    print(f"  - {r['criterion']}: {r['verdict']}")