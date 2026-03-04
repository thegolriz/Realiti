# Backend Documentation

**This document is meant to capture my journey through building this backend.**  
It is *not* intended as a full production usage guide. A separate document
with API usage instructions will be included later in this folder. 
(As of now, it hasn't been written.)

---

##  January – The Beginning

After a hectic semester and some downtime (thanks to Hurricane Helene), 
I started this project as a way to stay sharp and catch up on 
backend development skills.

###  The Search

Initially, I tried reading documentation and decoding the starter code I had,
but it was overwhelming. I had almost no backend experience, the starter
code might as well have been in another language. So, I switched gears and 
started following tutorial videos to understand the basics.That got me through 
building a basic `__init__.py` and setting up a SQLite-backed web API.

---

##  February – Transition to a Flask API

Feeling a bit more confident, I transitioned into building a proper 
**Flask-based REST API**. My understanding was still limited,
so I leaned on ChatGPT to explain concepts and guide my implementation.

Through that, I learned about:
- JWT authentication
- Secure password hashing
- Structuring API routes
- Environment configuration

I also switched from SQLite to PostgreSQL, which went smoother than expected.

---

##  March – Routes, Refactors & Cleanup

I focused on completing the API routes, debugging leftover tutorial code that 
was clashing with the new setup, and finally started reading actual documentation.

By the end of March:
- Most routes were working
- I had begun cleaning up unused code
- The app structure was getting more modular and readable

---

##  Intel to M1 – Unexpected Migration Woes

I upgraded from an Intel Mac to an M1 Mac — and chaos followed.

- PostgreSQL DB wiped
- Compatibility issues (Flask asked for PostgreSQL 14, I had 17)
- Ghost config files from the Intel setup haunted my new machine
- I had to manually hunt down lingering paths, cached references, and mismatched binaries

---

##  June – Back at It

After exams, internship grinds, and some well-earned mental rest
, I’m back on the project. I’ve started by documenting the work so far 
and planning what’s next.

---

## July - Docker, Poetry, Pytest

I have fixed the current API's around mid June, the DB was rebuilt and I learned
how to move the DB for future instances, i.e. using a cloud service. This month
was all about adding modern dependeny management and containorizing my project.
I have made a DockerFile with some basic stuff, added poetry to keep up with
the dependencies and even add a CI action to check flake8 and black formatting
before being allowed to merge pull requests. The final thing I started working
on was a docker-compose file. I can now also put more in depth text on what i've
done since its current work being written down.

To summarize:
- Added DockerFile
- Added Poetry 
- Renamed long backend name folder to just backend
- Added CI actions to run flake8 and black
- Added docker-compose.yml file

### What's Next
- Fix isort for CI 
- Flesh out docker-compose file
- Make mock DB for test suite
- Research how to cache user information with Redis

## August - School start, Arch fun

I took a break while getting adjusted to school, and I built my first pc. This did take
a good chunk of time, however, I am getting back into the groove of working as well as
making a schedule which allows for fun and work. I believe I may have an idea of what 
to shift this project towards to see if I can get real world data. Of course, i'll need
to do research as to see if my idea is not already implemented, if it is maybe I can do 
some sort of alternative, like airbnb and vrbo. Similar models with different systems.

###  Author:  
**Anis Golriz**

