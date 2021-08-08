import requests
from functools import wraps
from flask import session, redirect, render_template
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
import random

# Get requests from API
response = requests.get("https://type.fit/api/quotes").json()

# Configure SQLite to use the database
db = sqlite3.connect('corspat.db', check_same_thread=False)

def quote_length():
    return len(response)

def quote(num):
    return {
        'quote': response[num]["text"],
        'author': response[num]["author"]
    }

# Function from cs50
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def stuck(message, code=400):
    """Render a page when the user hits an error wall"""
    return render_template("stuck.html", top=code, bottom=message), code

def get_metadata(url):
    ''' 
    Metadata parser: Returns dictionary with (url, title, description and image link)
    '''
    # Check if URI exists
    if not uri_exists(url):
        return False

    # Creating a BeautifulSoup object
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    # Hostname
    get_hostname = urlparse(url).hostname
    if get_hostname[:4] == "www.":
        get_hostname = get_hostname[4:]

        # Title (if extra space)
    get_title = soup.title.string.strip()

    # Description (if none)
    get_desc = soup.find("meta", property="og:description")
    if get_desc is None or get_desc.get('content') is None:
        get_desc = "No description found."
    else:
        get_desc = soup.find("meta", property="og:description").get('content')

    # Image (if none)
    get_img = soup.find("meta", property="og:image")
    if get_img is None or get_img.get('content') is None:
        get_img = '/static/assets/img/path/img-none.jpg'
    else:
        get_img = soup.find("meta", property="og:image").get('content')

    return {
        'hostname': get_hostname,
        'url': url,
        'title': get_title,
        'desc': get_desc,
        'img': get_img
    }

def get_courses(user):
    '''
    Getting as a dictionary the courses added by user
    '''
    # Display courses
    cur = db.cursor()
    cur.execute("SELECT * FROM path WHERE user_id = ?", (user,))
    get_courses = cur.fetchall()

    courses = []

    for row in get_courses:
        courses.append({
            'id': row[0],
            'uuid': row[1],
            'hostname': row[2],
            'url': row[3],
            'title': row[4],
            'desc': row[5],
            'img': row[6],
            'isfinished': row[7],
            'added': datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S').strftime("%b. %d, %Y")
        })
    
    return courses

# Solution by 'Maxfield' here: https://stackoverflow.com/questions/16778435/python-check-if-website-exists
def uri_exists(uri: str) -> bool:
    try:
        with requests.get(uri, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                return False
    except requests.exceptions.ConnectionError:
        return False

def get_progression():
        cur = db.cursor()

        prog_c = cur.execute("SELECT COUNT(finished) FROM path WHERE user_id = ? and finished = 1;", (session["user_id"],)).fetchone()
        total_c = cur.execute("SELECT COUNT(finished) FROM path WHERE user_id = ?;", (session["user_id"],)).fetchone()

        try:
            return round((prog_c[0] / total_c[0]) * 100)
        except ZeroDivisionError:
            return 0

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def good_work():
    
    # Sentences come from here: https://www.myenglishteacher.eu/blog/keep-up-the-good-work/
    sentences = ['Good job!', 'Couldn’t have done it better myself', 'You’re on the right track now!',
                 'Keep up the great work!', 'Good job! Keep it up!', 'Keep up the hard work!', 'You’re doing a great job',
                 'That’s coming along nicely', 'Now you’ve got the hang of it!', 'You made it look easy!',
                 'You’ve almost mastered that!', 'Keep it up', 'You’re learning fast!', 'Good effort!',
                 'You’ve got it made', 'You’re getting better every day', 'SUPER DUPER!', 'You’ve got that down pat!',
                 'Way to go!', 'Nice work!', 'Now that’s what I call a fine job!', 'Good going!', 'Well done!',
                 'You’ve got it made!', 'I knew you could do it.', 'Couldn’t have done it better myself.',
                 'That’s the right way to do it.', 'Sensational!']

    return sentences[random.randrange(0, len(sentences))]

def yt_playlist():
    playlist = ['TgZUHw7kGX0', 'Df3ysUkdB38', 'z3FA2kALScU', 'KxV5Oh0eb6Y', 'd9gwmyPMByM', 'IwkyVjAHnZE', 'LG4q6YME5BA', '4eEaVqG8VFM', 'R7iN71uJcG0', 'EaD1Mpgzw1c', 'FFQ3cNGHgOM', 'SOL6C7VGDh0', 'WBGxOFspJh4', 'OMnBn0oUOBk', '1LxFtLbreLE', 'iO6lvhUFLJY', 'G-kGlmWgHKo', 'GEdvIzew-yw', 'AL08YZCYShc', 'O95oRLl6ks4', 'Z5zHAPbIBKg', '1I9ADpXbD6c', 'ef3Bj16fAPA', '_uL6NP38hbk', 'Bsph5BE6w1A', 'A5nsUjQFvok', '6rPRRAqpdxc', 'IcAU0v-TmaU', 'IrFiryKOS30', '_UtDMmx-Ouc', 'iPNXUHwKFJo', '0u_FkSzXyIY', 'pEYzig8a73M', 'XMLQYEvcGuM', '74HJNe2mqcI', 'iuNJLtj10Lg', 'Khwv5zPsSxc', 'eI2MDLvcqJ0', 'gKUL1VRSzlY', 'Rq6CL0nYQnk', '_1UbBBm3Qaw', 'CSQjA3R9TXE', 'z4034lRVaYA', 'OdY0UdiqTS0', '-ter4hZOJl0', 'InU87p6ayVo', 'mOlYmtPBSqE', '8zy_3lRR8sc', '3Hd-YLx-vAk', 'BfdvbZFXbNA', 'rG1v-57vFy0', '3c9laKeYiH0', 'IiGlVwbbcIg', '-uPaSOD7Dvk', 'bXGhtjezJPY', 'RASgqPsVXUM', 'YwIXNmwy-MQ', 'yopKr0x0t_s', '-Qy2vist-XQ', 'CR_o8pZNFlY', 'QTxRG6xpejo', '4_vayOXzcMM', 'xpWOEF-y9Is', '_CQ2UT8SsK8', 'iRkNVIlA7rc', 'xz34CuXw6EA', 'JzG28QJFTeM', 'HgkEsouZQJA', 'F5PUc7KXTy0', 'DRt6rcoqMhY', 'PZa-CKI5tw8', 'ayDLsz4Y2Vk', '5y_l-ay_i7Y', '2pZ_2P6Dd-0', 'N5R-RX4fbbk', 'Yatr-OvHXB8', '0a_aoj9-9-w', 'Z964cOvcOLY', 'YyXyr0WLjxw', 'aYkTbi8MCv8', 'efT4Mr9Xwkg', 'PfykaYKS5tY', '0x1SJ9zhAOY', 'TNLB5qRPLJY', '9zhY90QkV-Q', '6B9hluUf70g', 'vphIZItHbgs', 's0RPV40GKxc', 'w0fiTCewI_c', 'SvRdC5v88G0', 'ykAb2bHpQ-c', 'sr8HqzJbngo', 'N6zqatiur3A', 'CDPlp-gxLFE', '6veMHgxcDJE', 'yGlrrA-wLJE', 'Ec6xcIAoMIo', '962eYqe--Yc', 'yd_9aNqzfEc', 'EqevU-NrFs0', '1cIhzERWjmI', 'I1RoKhS-rhI', 'n-VBctp-suw', 'JGAewzvS53E', 'gdmIuLE0kzE', '8t92ubfvr6k', 'ldPOe1qVl-w', 'Xn0dFNGb0MA', 'mH7yqXcifHc', 'CbgdCRERFEg', 'rwjdY-MAIBg', 'EiphOZ3E_x4', 'E71APyXDW5w', 'nQOkqDOY9uk', 'UaaoBac2TTE', 'hyO8PNTwyYo', 'jI-B1myBFw8', 'UPgJ0SKzPzc', 'xm1OvMkCNiY', 'JHn-QAPltsc', 'nq56uzM4hu8', 'gpP7gjMr7js', 'xwAmEEKus_A', 'a00jKco0WWI', 'iA-8sxne0BY', 'Cj2G5D9kz6c', 'gVjKTcEzGNA', 'O885-LqlSeM', 'OVByjeVgKKw', 'kgSvjIhWQ3Y', 'lrkOdrOD5xA', 'luf9TP_nQWw', '2ovBQhyEK4g', '4HqSUv-hd44', 'h82Ja1iyjPk', 'EmEdb70OxQ8', '0Yv6r8Kl4bM', 'Jt9MivGwaRk', 'G0wSOizLFoY', 'vQzb34h7mtY', 'o_GFl1lppdA', 'w4lbjwgUEwE', 'TsNsmfw2Ea0', 'LrEwLXeh53c', 'hUYd8ifsWAg', 'g6BtbIiJ_rc', 'EchAqgWVeNQ', 'YPG_6618sWw', 'Ng5qiDAkiI0', 'oAbyfbZsRxg', '3DVH0X3LXAs', '61drPjOfzNM', 'VMpVymdcB2w', 'jNWjaZ7EBFc', 'zBHLk1PaCyQ', 't9jLzYxZu6k', '1rh8K4SwWjE', 'HRd3mHXP_CE', 'Rjvz79VR2II', 'bPZoo8byW98', 'MZSZtsaMsaI', 'jSdj2pTH1Zg', 'HwLK9dBQn0g', 'y0GJjPm_jEs', 'KvOt4wgdQOs', 'QmBESfmwEUo', '3yXMXNNHh38', '-i3KLKZMfhI', 'wRdWcjVumIU', 'cbEYDsFHaYc', 'HSwMLhFIDJU', 'K4HyuWna8hI', 'IQGZEwvLxuY', 'jXKEJ_-ajuM', 'DhOVN1omhv4', 'euBqngNt64A', 'Vnq9QB146M8', 'gpI0O8WBmaM', '8n7H1qIsy1s', 'x16NxoY1wo8', '5T5nWBoilqE', 'tAsKbRz2NZE', '7UAcBYa46H0', '3RB4ALczIM4', 'wvdqAkwCThc', 'YcdF_TsubxQ', '_hjMQvIRt9g', 'eJsOU7GvT5o', 'ijs4N-diiXM', 'hFWGWl10vuQ', 'gEF_oM5FI9o', 'NleiwcoZtBI', 'kXvMDHhfYwg', '59P01D1uL5w', 'azDCAppGnX4', 'EH6Jgz8_drY', 'HtwIrKSEpFE', 'dnY-kt54css', '7YSm6iMS6r0', 'QzmobNzmB8M', 'ZEI7QUhFExY', 'tMyxdf9LD0U', '2TdMI_vAA8A', 'lYlv4NZE2I4']
    shuffle = random.randint(0, len(playlist))
    return playlist[shuffle]