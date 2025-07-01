## Idea: python main.py and json files as database - all you need until your work is interacted by thousand users..

# How To develop and launch something in few minutes
  The development speed with LLMs drastically depends on 
  1) the choices of limitations explicitly specified, by far
  2) choice of models
  3) speed of LLM output and speed of your input (use voice transcriber based on Whisper)
  Prerequisites: make access to the source hosting platform(github account), launch platform(render.com account), development environment(_uv_, Cursor) and where to purchase domain(cheapdomains.com)

  Design - took 1 minute

  Start with the design prompt and best suitable model on some top level interface such using "_you're an expert python backend developer
  ...tasked with designing simple possible website satusfying the ... using only python aiohttp and managing all database-suitable content in JSON files
  with /admin side to manage all that content; organize entire design in steps with 1 concrete prompt for another developer agent_"
  Review the steps till the design presents the most simple function for your project task purpose 

  Development - took 4 minutes
  Use the design steps' prompt thread with top LLM(Claude) controlling it on localhost run after every prompt

  Domain - took 1 minute
  Purchase domain(cheapdomain.com) and point ns records to a platform you use to launch (such as render.com)

  Launch - took 1 minute
  As your localhost version is satisfactory to launch, push it to your repository production branch and connect that repository and branch to launch platform specifying how to get the dependencies (pip install .) and how to run it(python main.py) and run it. 
  Share it with your people.

  Additionally - few seconds
  put JS track code(mouseflow) in template and watch the use on yout website

  ... and only then .. actually start developing it closely varying on what you learned from your users
  

# Work Website

This is how this website was built. 

## Quick Start
Just manage and run it with uv, I recommend that tool. It will install environment and manage dependencies by itself
```bash
uv run python main.py
```

## Features
- **This is your entire site** 
  - No frameworks. No setup. No reverse proxy. No middleware. No assumptions.
  - python main.py is all you need for this site production purposes
- **Easy Modification**: The database is json files. Change to the one you like in seconds.
- **Admin Panel**: Access at `/admin` with default password `1234`
- **GitHub Markdown**: Posts and about render with GitHub-style markdown
- **Production Ready**: Deploy to production by purchasing domain, running on render.com free trial and pointing ns servers to render endpoint in less then 2 minutes


