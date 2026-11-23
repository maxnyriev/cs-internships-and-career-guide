# Your First Resume

A resume is a one-page summary of what you've done. Recruiters skim, so it has to be clean and easy to scan. You don't need an internship to make a good one. Employers say so too: in NACE's [Job Outlook 2026](https://naceweb.org/talent-acquisition/candidate-selection/internship-experience-often-the-deciding-factor-between-equal-candidates) (183 employers), general work experience and leadership ranked above a 3.0+ GPA when choosing between equally qualified candidates.

## The rules

- **One page.** Always, until you have years of full-time work.
- **Plain layout.** One column, one font, black text. No photo, icons, skill bars, or tables.
- **Contact info typed in the body of the page.** Some resume-reading software (an ATS, applicant tracking system) may skip the Word or Google Docs header and footer zones. How often that happens is unclear, but typing your name and contact line as normal text costs nothing, so do it as a cheap precaution.
- **Standard section names:** Education, Projects, Experience, Leadership and Activities, Skills. Software and recruiters both look for these words.
- **No objective or summary** at this stage. This is my preference: it takes space and says little, and your projects say more. Some guides, including Tech Interview Handbook, suggest a short summary, so either is defensible.
- **Working links.** Write them out short (`github.com/your-name`), and click every one in the PDF before you send it. Point project links to the repo or live demo, not your profile.
- **Save as PDF.** Name it `FirstName_LastName_Resume.pdf`. Copy all the text out of the PDF and paste it into a plain text file. If it comes out jumbled, the software sees it jumbled too.
- **Professional email.** Your name, not a nickname.
- **Update dates every term:** expected graduation, "Present" on current roles, classes in progress, new GPA.
- **Answer knockout questions carefully.** Forms ask about location, graduation date, degree, and clearance. These are the filters that really are automatic, so answer them truthfully and the same way every time ([answer sheet](applying.md#tracker-and-answer-sheet)).

## Sections, in order

1. **Header:** name, city and state, phone, email, LinkedIn, GitHub.
2. **Education:** school, degree and major, expected graduation (month and year), GPA if 3.0 or higher, honors, 4 to 6 relevant classes.
3. **Projects:** your best 2 or 3. This is the main section when you have no internship.
4. **Experience:** any job counts: retail, food service, campus jobs, caregiving, a family business. It shows you show up and handle responsibility.
5. **Leadership and activities:** club roles, competitions, hackathons, tutoring, volunteering, events you organized.
6. **Skills:** only what you have really used, grouped:

```
Languages: Java, Python, C, SQL
Tools: Git, Linux, VS Code, Spring Boot, MySQL
```

Leave out soft skills ("teamwork") and anything you've only watched a video about.

## Bullet formula (XYZ)

Write each bullet as: **Accomplished X, measured by Y, by doing Z.** (A former Google HR executive popularized this pattern.) Start with a strong verb (Built, Cut, Organized, Trained, Fixed, Wrote, Led).

- **Project:** "Cut shift-board page load from about 4 s to under 1 s (measured in Chrome DevTools) by caching schedule data instead of querying the database on every page."
- **Club:** "Grew weekly workshop attendance from about 10 to 30 by moving sessions right after intro CS labs and posting in class Discord servers."
- **Retail:** "Handled 60+ transactions per shift at a hardware store register and cut checkout errors by double-checking returns against receipts." (Use only counts you know, like transactions per shift from the register report.)
- **Food service:** "Trained 5 new hires on the register and drive-thru headset during the holiday rush, cutting the time the manager spent on training."
- **Caregiving:** "Managed medications and 6+ appointments a week for a family member by setting up a shared calendar and checklist the family still uses."
- **Campus job:** "Cut weekly inventory counting at the campus bookstore from about 6 hours to 2 by building a Google Sheets tracker with barcode-scanner input."

Good numbers: real users, tests written, time or money saved, response time, records handled, people trained or led. Lines of code is not a good number.

**No number? Say what it does and how you tested it.** "Built a shift-swap web app with sign-in, email alerts, and 18 JUnit tests for the claim logic." That's honest and specific.

**Never invent a number.** Interviewers ask "how did you measure that?" If you guessed, you're stuck. Use "about" only for numbers you really estimated from something real.

Use 2 to 4 bullets per item.

## Sample resume

A fictional sophomore with no internship. This is what "good enough to get interviews" looks like at this stage: real, specific, not inflated.

```
JORDAN LEE
Anytown, TX | (555) 555-0142 | jordan.lee@email.com | linkedin.com/in/jordan-lee | github.com/jordan-lee

EDUCATION
State University, Anytown, TX                                              Expected May 2029
B.S. in Computer Science | GPA: 3.4/4.0 | Dean's List (Fall 2025)
Relevant courses: Data Structures (in progress), Discrete Math, Computer Organization, Intro to Java

PROJECTS
Shift Swap Board | Java, Spring Boot, SQLite                       github.com/jordan-lee/shift-swap
- Built a web app where coworkers post and claim open shifts; 9 coworkers used it for 6 weeks
  in place of a group text thread
- Fixed a bug that let two people claim the same shift by adding a database transaction, then
  wrote 18 JUnit tests for the claim logic
Bus Arrival Display | C++, ESP32, LCD                              github.com/jordan-lee/bus-display
- Built a desk display that shows the next two campus bus times from the city's public transit feed
- Cached results and refreshed every 30 s instead of every 5 s to stay under the feed's rate limit

EXPERIENCE
Sales Associate, Main Street Hardware, Anytown, TX                                 Jun 2024 - Present
- Work 20 hours a week during the school year while taking a full course load
- Trained 4 new hires on the register and returns process during the 2025 holiday season
- Close the store 2 nights a week: balance the register and count high-value inventory

LEADERSHIP AND ACTIVITIES
Events Coordinator, Computing Club                                               Aug 2025 - Present
- Organized 5 workshops (Git basics, Linux, resume night) with 25 to 40 attendees each; booked
  rooms and recruited 3 upperclassmen to teach

SKILLS
Languages: Java, Python, C++, SQL, HTML/CSS
Tools: Git, GitHub, Spring Boot, SQLite, JUnit, Linux command line, VS Code, Arduino IDE
```

## Education edge cases

- **Transfer students:** list the four-year school you attend now first. Add the community college below it only if it helps (an associate degree, honors, or relevant classes). Example:
  ```
  State University, Anytown, TX — B.S. Computer Science, Expected May 2028
  Anytown Community College — A.S. Computer Science, May 2026 | Phi Theta Kappa
  ```
- **Which GPA?** Applications usually mean your current school's overall GPA. If your major GPA is much stronger, you can list both, labeled: "Major GPA: 3.6 | Overall: 3.1." If you just transferred and have no GPA yet at the new school, leave it off or use your community college GPA, labeled with that school.
- **Honors:** Dean's List (with terms), President's List, Phi Theta Kappa (the community college honor society), scholarships. One line in Education is enough.
- **GPA cutoff:** this guide says list it at 3.0 or higher. That's a convention, and some guides say 3.5. If yours is lower, leave it off. Some applications will ask; answer honestly there.
- **Took time off or changed majors?** Just list the degree and expected date. You don't need to explain gaps on the page.

## Experience that isn't an internship

All of these go under Experience and count:

- **Research with a professor.** Ask one whose class you did well in; a few hours a week is a normal start. "Undergraduate Research Assistant" is a real title.
- **Structured programs with code review.** Courses and fellowships where someone reviews your pull requests give you real teamwork stories.
- **Campus jobs:** IT help desk, lab assistant, library tech, web assistant for a department.
- **TA, grader, or tutor** for a CS or math class.
- **Short company projects:** [Forage](https://www.theforage.com) offers free, self-paced job simulations (list them under Projects or Certificates, not as a job). [Parker Dewey](https://www.parkerdewey.com) posts short paid "micro-internships" for students and recent grads. [Extern](https://www.extern.com) advertises a free trial and then paid plans, so check the price first.

## Tailor it

Tailor carefully for your top 10 to 15 applications. Send a solid general version to the rest.

1. Paste the job posting into a doc.
2. Highlight every tool, language, and skill it names (for example: Java, REST APIs, SQL, Linux, unit testing).
3. For each one you have **really used**, make sure the posting's exact words appear on your resume ("REST API," not just "backend"). Put them in Skills and in a bullet that shows where you used it. Don't stuff in keywords you can't talk about.
4. Move your most relevant project to the top of Projects.
5. Skip anything you haven't used. Interviewers will ask about every word.

**Example.** The posting says "build REST APIs in Java and write unit tests." Your general bullet: "Built a web app for coworkers to swap shifts." Tailored: "Built a Java REST API for a shift-swap app (post, claim, cancel) with 18 JUnit tests." Same project, same truth, but now it matches the words the reader is scanning for. About 20 minutes per application. Save each version as a separate PDF and note which one you sent in your tracker.

## Keep a master points file

Never write a resume from scratch. Keep one long document, your **master points file**, and build every resume by copying from it. It grows out of your [wins file](README.md#start-a-wins-file): the wins file is the raw log, the master file is the polished bullets.

For each project, job, or club role, write 4 to 6 bullets in XYZ form, plus a short and a long version of the best two. Tag each bullet with the skills it shows (`Java`, `SQL`, `leadership`, `customer service`). Then:

- **Tailoring** takes 20 minutes: copy the bullets whose tags match the posting.
- **Space** is easy to manage: swap in the short versions to fit one page.
- **Interview prep** is built in: every bullet is a claim you must be able to explain.

```
## Hardware store (Sales Associate)  [retail, training, cash handling]
- Trained 4 new hires on the register and returns process during the 2025 holiday season
- Balanced the register nightly and counted high-value inventory twice a week
## Shift Swap Board  [Java, Spring Boot, SQLite, JUnit]
- Built a web app where coworkers post and claim open shifts; 9 used it for 6 weeks
- Fixed a double-claim bug with a database transaction; wrote 18 JUnit tests
```

Add to it the week you finish something, and update dates every term. Sort retail, caregiving, and food-service jobs into the same file: handling a rush, training people, and keeping accounts straight are real skills ([Experience bullets](#bullet-formula-xyz)).

## Resume audit

Run this before you send a resume anywhere. Every answer should be "yes."

1. Is it one page, one column, with contact info typed in the body (not the header/footer area)?
2. Does the text copy cleanly out of the PDF?
3. Does every bullet start with a strong verb?
4. Does every bullet say what you did **and** a result or how it was tested?
5. Is every number true, and could you explain how you got it?
6. Are projects above anything less relevant, with your best one first?
7. Is every skill something you could answer a question about?
8. Do all links open the right page (repo or demo, not a 404)?
9. Are dates, graduation date, and GPA current for this term?
10. Has someone else read it for typos in the last month?

**Teardown: three weak bullets, fixed**

| Before | Problem | After |
|---|---|---|
| "Worked on a website for a class." | No verb, no detail, no result. | "Built a course-review site in React and Node.js with a 3-person team; wrote the search API and its 12 tests." |
| "Responsible for helping customers." | Duty, not an accomplishment. | "Resolved about 30 customer questions per shift at the service desk, including returns and special orders." |
| "Used Python, Java, C++, SQL, AWS, Docker, and Kubernetes." | A list of tools in a bullet; some never really used. | Move real tools to Skills. Replace with: "Wrote a Python script that cleaned 3 years of club attendance data from 9 spreadsheets into one SQLite database." |

## Get it reviewed

- **Your career center.** Free, and they know what local employers want. Book a resume review.
- **An upperclassman who has interned.** Ask: "What would make you skip this resume?"
- **An AI tool, only as a second opinion.** It can catch weak verbs and typos. Check every line it changes: it may add numbers, skills, or claims that aren't true, and you're the one who'll be asked about them.

**Short on time, or starting late?** In one evening: copy the sample above, replace it with your real classes, one project (even a class project), and one job, then book a review. A plain true resume this week beats a perfect one next month.

## Cover letters

Most internship applications don't require one. If a posting asks, write four short paragraphs: why this company, your best project and what it shows, one more reason you fit, and a thank-you. Keep it to half a page.

## Tools

- **Google Docs or Word** with a plain one-column template is all you need.
- **Optional:** the "Jake's Resume" template on [Overleaf](https://www.overleaf.com), a free LaTeX template many CS students use. It's based on [sb2nov/resume](https://github.com/sb2nov/resume) (use the layout; don't copy its author's content).
- **Optional:** [RenderCV](https://github.com/rendercv/rendercv) builds a PDF from a text file, if you dislike LaTeX. Run the copy-and-paste test on whatever it produces.

## Resources

- [Tech Interview Handbook: resume guide](https://www.techinterviewhandbook.org/resume/)
- [Jake's Resume template (Overleaf)](https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs) (optional, LaTeX)
- Need project material first? See [projects](projects.md).

Next: [Projects](projects.md)
