# 📚 Corspat — Build Your Own Path

> [!WARNING]
> **Unmaintained and archived.** This was my CS50 final project (2021). It is no longer developed or deployed, and the versions pinned in `app/requirements.txt` carry known CVEs. Please don't run or deploy it as-is. Kept public for reference only.

<details>
<summary>Notes for reviving it later</summary>

Checked against PyPI in July 2026:

- **Python 3.9 → 3.12+.** Current `requests`, `urllib3`, `click`, `gunicorn` and `soupsieve` all require ≥ 3.10. Update both `Dockerfile` (`python:3.9.12-bullseye`) and `app/runtime.txt` (`python-3.9.6`).
- **Flask 2.0.1 → 3.1.x**, forced by the Werkzeug ≥ 3.1.4 advisory. Brings Werkzeug 3.1.x, Jinja2 3.1.6, itsdangerous 2.2.0, blinker 1.9.0.
- **Flask-Mail 0.9.1 → 0.10.0** and **Flask-Session 0.4.0 → 0.8.0**; both older versions predate Flask 3.
- **Keep SQLAlchemy on 1.4.x** (1.4.54 is the last one). `app.py` uses the legacy `engine.execute("SELECT …", param)` call, which was *removed* in SQLAlchemy 2.0 — moving to 2.x means rewriting every query in `app.py` and `helpers.py` around `text()` and `Connection.execute()`.
- **Code change required regardless:** `app.py` calls `send_file(..., attachment_filename=...)`. That argument was removed in Flask 2.2, so the `/settings/dl` CSV export breaks the moment Flask is upgraded — it needs to become `download_name=...`.
- Also worth a look: no `SECRET_KEY` is configured, `helpers.py` makes a network call at import time (so a slow or failed API call blocks startup), and the `corspat.herokuapp.com` links in the password-reset and verification emails are dead.

</details>

#### Video Demo:
[Click here to watch the demo on YouTube.](https://youtu.be/PNtzgsMiYY4)

#### About the website:
This is my final project for the [CS50's Introduction to Computer Science](https://cs50.harvard.edu/x/2021/). Corspat is a dream came true since I’ve always used spreadsheets in order to keep track of the time I spend studying online, but I’ve never came across a platform that can help me manage both the courses and the time spent on every course. So instead of using multiple tools and platforms, I decided to put all of these features in one and a same place, that… I called **CORSPAT**.


#### How to use

1. First, make sure to watch the demo video about Corspat then create an account to have access to the website.

2. In order to start using Corspat, a path of online courses is necessary. In other words, if you know where you are, you need to know where you're going. Fortunately, there's already an amazing website called `classcentral.com/` with over of 40,000 Courses from Top Universities where you can check and gather links of courses you want to enroll in.

3. Then, once the above step done. You can start tracking your study sessions. The website will show you your courses in the order you added them. At the end of your session, you only need to stop the stopwatch, you'll notice, then below a new row in the history. Well. Congratulations for your first record on Corspat.
	> If you ever forget to stop the timetracker, the **TimeGuard** 🤖 system will do it on your behalf and will only keep 1-hour in the last unfinished history record.

4. In case you have a hard time studying, you can still try the 'Motivation' page. See if it can help you. It did for me, so hopefully it will do the same for you too.

5. Finally, If any question occurs to you, please visit the FAQ. If your question is not answered, I would be more than happy to help you and add it the FAQ.

---

#### Story behind the technology

Well, at first, I started by drawing a simple design of the website on paper, the features needed came along while doing this.

The next day, I started by drawing a more advanced design with the help of the vector graphics editor `Figma` where I got new ideas again, the first core feature I thought of was the `path` page.
Which looks really easy to create at first sight. But I changed my mind very rapidly as I saw that this simple concept was expanding very fast beyond what my brain could handle at the time.

Creating a page where you can keep notes was a second idea I got, which I dropped for a better one I was already familiar with, which is a time tracker. The 'notes' idea wasn't doable, there is already plenty of websites online that keep your notes secure and do the job very efficiently.

But well, months of playing cat and mouse with `Microsoft Excel` and `Google Sheets` really taught me something. It was killing me (more than the courses I was enrolled in) to do this manually every time. And I needed a solution so badly ASAP.

The third page which is 'Motivation' is the last idea I got. It's so simple but still… It helped me a lot to overcome the challenges I had every day.
I tried to make it easy for anyone who wanted a random motivational quote and video. Hopefully, this will help someone someday.

The last page left, obviously, is the `F.A.Q`., I tried to answer some questions that would help users navigate the website.
And yes, it will expand with time.

Once all my ideas were gathered and organized, a settings page was the most obvious choice to add to the website, giving full control of accounts to the users.

Thus far, it was all about gathering ideas, trying to stabilize the backend and connect it with the frontend, more challenges I didn't know about were waiting at the corner every time.

Then came the time to start coding more fun features.

The page `path` was not only the first idea I got but also the first page I implemented, the first challenge I encountered was to scrap the web for ANY page posted without error and even if it’s the case a wanted behavior should occur instead.

The `BeautifulSoul` was not only a beautiful soup but also a beautiful documentation, and it was really helpful and easy to read. I spent some time reading it to understand how to use the library.
And to my surprise, a few hours later I was able to get the page title, the description and with luck an image of the course.
It was my first win. After this, I was able to build the rest of the website.

The main goal I had this whole time was to exactly implement the idea I had in mind every time I had one.

For instance, I always wanted in my `Google Sheet` a kind of stopwatch in my time tracker. The opportunity arose to build it in Corspat. The idea was that I wanted it to be sort of a live thing but without consuming too much computing power on the server-side.

The easiest way I thought of was to store the first timestamp, calculate the difference between there and now, then pass it to `JavaScript` (Front-End) which was prepared to start at any time given.
I was right, it worked.

After surviving this, everything was doable almost easily. Motivation has an `API `for quotes and the videos a list of YouTube video IDs.

`FAQ` is just a Bootstrap accordion with some MP4 videos converted online to GIF files.

The notifications here and there are just a Flask’s flashing system (`flash()`) turned into Bootstrap Toasts.

And finally, deploying the website should have been the easiest part of all it. But even this had some complications. I choose `Heroku` for some reasons over other host providers.

To only mention a few, Heroku supports Python and their platform is really easy to use. And unlike others cloud platforms, It doesn't delete or disable your website if inactive too long. Lastly it's free.

But it had some bad side effects I discovered very fast after deploying Corspat. `Heroku` is based on an ephemeral filesystem, which means that twice a day (sometimes even more) your `SQLite` database will be reset to the last push you did to the remote branch. The workaround thing I found (where I learned a lot of things by the way) is to change your `SQLite` library in Python to `SQLAlchemy` then connect it to `Heroku PostgreSQL`.

The good thing about it is that now I can switch to other database management system easily, only by editing the connection.

And that's it, it fixed my problem.

The website is online and working.

---

#### Technologies used

* ###### Frontend
	* `Bootstrap`
	* `Javascript`
	* `HTML`
	* `CSS`

* ###### Backend
	* `PostgreSQL`
	* `Docker`
	* `Python`
		* `Flask`
		* `SQLAlchemy`
		* `Flask Mail`
		* `bcrypt`
		* `BeautifulSoup`
		* `...`

* ###### Hosting
	* `Heroku`
