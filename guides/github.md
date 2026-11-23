# GitHub

GitHub is where programmers store and share code. Interviewers and hiring managers often click your link, and it shows your resume is true. In a CodePath survey of 200+ engineering leaders ([reported by Fortune](https://fortune.com/2025/12/18/tech-hiring-slow-but-not-fully-stalled-exclusive-codepath-data-new-secret-to-land-tech-role/)), 34% named public code portfolios like GitHub as a top signal outside the interview, and 38% named side projects or portfolios. (The survey didn't split recruiters from managers.) One finished repo with a good README is enough to start.

## Make your account

- [ ] Sign up at github.com with a personal email (your school email can stop working after you graduate).
- [ ] Pick a simple username, like your name. Avoid jokes and numbers.
- [ ] Add a clear photo and your name.
- [ ] Turn on two-factor login (see [Protect your account](#protect-your-account)).

## Git basics

**Git** tracks changes to your code. **GitHub** is a website that stores your Git projects. You need both.

**1. Install.** Install [Git](https://git-scm.com/downloads), or install [GitHub Desktop](https://desktop.github.com) if you prefer clicking to typing. Desktop includes Git.

**2. Tell Git who you are.** Once per computer, in a terminal:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Commits carry this email, and it's public on your repos. If you don't want your real email public, turn on "Keep my email addresses private" in GitHub Settings under Emails. GitHub then shows you a private `noreply` address to use as `user.email`.

**3. The five commands you'll use every day:**

```
git clone <repo-url>     # copy a repo to your computer
git add .                # choose the changes to save
git commit -m "Add login form"   # save a snapshot with a message
git push                 # upload your commits to GitHub
git pull                 # download changes you don't have yet
```

**4. Signing in.** GitHub stopped accepting your account password for Git on the command line in 2021. Use one of these:
- GitHub Desktop: sign in once in the app.
- VS Code: sign in to GitHub when it asks.
- The GitHub command-line tool: install `gh`, run `gh auth login`, and follow the prompts.

**5. Practice 5 times.** Make a practice repo. Clone it, change a file, add, commit, push, five times, until you stop looking up commands. When something goes wrong, [Git Flight Rules](https://github.com/k88hudson/git-flight-rules) tells you what to do next.

**Done looks like:** you can start a new project, push it, and see it on github.com without help.

## Profile and pins

- Optional: a profile README (a public repo named exactly like your username), 3 lines, no badges or widgets.

```
Hi, I'm Alex, a CS student. I build small tools for student groups.
Now: learning SQL and testing. Best project: shift-swap
LinkedIn: linkedin.com/in/yourname
```

- **Pin 2 to 4 repos** that run and have a README. GitHub allows up to 6. Don't pin empty homework folders. Layout ideas: [awesome-github-profile-readme](https://github.com/abhisheknaiidu/awesome-github-profile-readme). Plain beats flashy.

## What a good repo looks like

- [ ] A clear name (`shift-swap`, not `project1`).
- [ ] A README with: what it does (one sentence), a screenshot, how to run it, and what you used.
- [ ] **The README is true of the code.** If it says "supports login," login works. Interviewers will test your claims, and a broken repo is a worse signal than a small working one (my judgment).
- [ ] It runs with one or two commands from a fresh clone. If it's a website or app, put the live link in the repo's **About** box (the gear icon on the right of the repo page).
- [ ] No passwords or API keys in the code. Ever.
- [ ] A `.gitignore` file so you don't upload junk files. GitHub's [gitignore templates](https://github.com/github/gitignore) cover most languages, including Java.
- [ ] A `LICENSE` file if you want others to reuse it (MIT is a common simple choice). Optional for a portfolio piece.
- [ ] Commit messages that say what you did ("Add login form", not "stuff").
- [ ] Optional: a few tests, and a free automatic test run (GitHub Actions) so a green check shows the tests pass.

**README skeleton** (fill in; delete what doesn't apply):

````
# Shift Swap Board
One sentence: coworkers post and claim open shifts instead of using a group text.

![screenshot](docs/screenshot.png)

## Run it
1. Install Java 21 and Maven.
2. git clone https://github.com/your-username/shift-swap
3. cp .env.example .env   (fill in your values)
4. mvn spring-boot:run
Open http://localhost:8080

## What works / what doesn't yet
Works: post a shift, claim a shift, email alert.
Not yet: sign-in with a school or work account.

## Tests
mvn test   (18 tests)

## Built with
Java 21, Spring Boot, SQLite
````

Copy the commands from a real run, not from memory. [Best-README-Template](https://github.com/othneildrew/Best-README-Template) is popular, but long, so delete what you don't need.

A minimal Java `.gitignore`:

```
target/
*.class
.idea/
.vscode/
.DS_Store
.env
```

## 30-minute cleanup pass

Do this before you apply. Set a timer.

1. **Pins:** keep 2 to 4 best repos.
2. **README:** each pinned repo has what, screenshot, how to run, and a live link in About. Check it matches the code.
3. **Junk:** remove build folders (`target`, `node_modules`) and `.DS_Store` files, and add them to `.gitignore`.
4. **Names:** rename `project1` and `test2`. Delete or archive (Settings, then Archive) empty or abandoned repos.
5. **Secrets:** search your code for `password`, `key`, and `token`. Use a `.env` file for secrets, keep it out of Git with `.gitignore`, and commit an example file (`.env.example`) with blank values. **If a secret was ever pushed, deleting it isn't enough. Go to the service that issued it and rotate it (make a new key and cancel the old one).** GitHub's history keeps the old one. To scan your whole history, try [TruffleHog](https://github.com/trufflesecurity/trufflehog), a free tool. ([Gitleaks](https://github.com/gitleaks/gitleaks) is another, but I've read it's getting security patches only.) GitHub blocks some known key formats on push, but don't rely on that.
6. **Default branch** is `main`, and the repo About box has a short description and topics.

**Done looks like:** a stranger can clone any pinned repo, follow the README, and see it run.

## Class projects

Post class projects only if your professor allows it, and never exam answers or code you were told to keep private. Rename them so it's clear what you built (`library-system`, not `CS201-hw4`), write a README, and list your part honestly in group work ("I built the database and login").

## AI-assisted code

If an AI tool wrote part of your project, you still own every line. Read it, run it, and be able to explain it ([projects: using AI tools](projects.md#using-ai-tools)). Never paste secrets or private class material into a chat tool. If it matters for a take-home or class, say in the README what you wrote and what you adapted.

The green activity squares aren't required. A few real projects beat a streak of tiny commits.

## Protect your account

- [ ] Turn on two-factor authentication (2FA) in Settings. GitHub announced in 2022 that people who contribute code on the site would need it by the end of 2023. Use an authenticator app or a passkey (a login stored on your phone or computer).
- [ ] Download your **recovery codes** and save them somewhere safe (a password manager or a printed copy). Without them, losing your phone can lock you out of your own code.

## Resources

- [GitHub Skills](https://skills.github.com): free hands-on courses inside GitHub.
- [Pro Git](https://git-scm.com/book/en/v2): the free official Git book.
- [First Contributions](https://github.com/firstcontributions/first-contributions): practice a first pull request (active in November 2026). Then try [Awesome for Beginners](https://github.com/MunGell/awesome-for-beginners) for beginner-friendly issues, and check a project has recent activity first. A good first PR is small, like a broken link.
- [The Missing Semester](https://github.com/missing-semester/missing-semester): free lectures on the terminal, Git, and editor skills.
- [GitHub Student Developer Pack](https://education.github.com/pack): free tools for students. Eligibility and approval time vary, so check the Pack page for the current rules.

Next: [LinkedIn](linkedin.md)
