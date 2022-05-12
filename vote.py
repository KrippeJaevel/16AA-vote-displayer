import webbrowser
import sys
import datetime
from bs4 import BeautifulSoup
import requests
OrbatURL = "https://community.16aa.net/orbat/"

# Locates the orbat and parses the content
orbatPage = requests.get(OrbatURL)
orbat = BeautifulSoup(orbatPage.content, "html.parser")
calendarURL = "https://community.16aa.net/calendar/"
calendarRAW = requests.get(calendarURL)
operationsCalendarURL = "https://community.16aa.net/calendar/2-operations-calendar/"
operationsCalendarRAW = requests.get(operationsCalendarURL)
calendar = BeautifulSoup(calendarRAW.content, "html.parser")
operationsCalendar = BeautifulSoup(operationsCalendarRAW.content, "html.parser")
nextOpCalendarURL = operationsCalendar.find("a", {"rel":"next nofollow"})
nextOperationsCalendarRAW = requests.get(nextOpCalendarURL["href"])
nextOperationsCalendar = BeautifulSoup(nextOperationsCalendarRAW.content, "html.parser")

# Sets the date range to start from today and add an arbitrary number of days to it
def date_range():
    today = datetime.date.today()
    week = [today.strftime('%Y-%m-%d')]
    added = 0
    while added < 25:
        added += 1
        day = today + datetime.timedelta(days=added)
        week.append(day.strftime('%Y-%m-%d'))
    return week

# Utility function that checks if the date range is beyond a single month
def checkMonthChange(firstMonth, lastMonth):
    if firstMonth != lastMonth:
        return True
    else:
        return False

# Receives a date range, finds all events in the operations calendar during that time period, and compiles them to present to the user
def get_events():
    dateRange = date_range()
    based_of_today = operationsCalendar.find_all("a", {'data-ipshover-target':True})
    events = []
    for a in based_of_today:
        for i in dateRange:
            if a["data-ipshover-target"].find(i)>0:
                events.append([i, a])
    if checkMonthChange(dateRange[0][5:7], dateRange[-1][5:7]):
        based_of_next_month = nextOperationsCalendar.find_all("a", {'data-ipshover-target':True})
        for a in based_of_next_month:
            for i in dateRange:
                if a["data-ipshover-target"].find(i)>0:
                    events.append([i, a])
    return events

# Utility function to make error messages a bit more flavourful
def printErrorBox(message):
    print("*****************************")
    print(message)
    print("*****************************")

# Prompts the user for input about which event they want to view
def get_attendance_URL():
    print("16AA Vote Displayer v1.3.\n")
    events = get_events()
    chosenEvent = ""
    for event in events:
        print(str(events.index(event)+1)+ ": " + event[0] + " - " + event[1]["title"])
    chosenEvent = input("Which of the events listed would you want to view? Enter the number OR paste the full URL to any other event not listed.\n")
    if "https://community.16aa.net/calendar/event/" in chosenEvent:
        return chosenEvent
    elif len(chosenEvent) != 1: 
        printErrorBox("Please enter a single digit value or the full URL")
        return get_attendance_URL()
    try:
        chosenEvent = int(chosenEvent)
        if chosenEvent > len(events) or chosenEvent<1:
            printErrorBox("There is only " + str(len(events)) + " events to chose from in the list. Try again. I believe in you.")
            return get_attendance_URL()
        else:
            return events[chosenEvent-1][1]["href"]
    except (TypeError, ValueError):
        printErrorBox("Select an event using the number on the list or pasting the full URL.")
        return get_attendance_URL()
    

attendanceURL = get_attendance_URL()

# Parameter section is the id of the div displaying the members on the ORBAT ("x/y section" or similar)
# Returns list with members in string form
def get_section_members(section):
    full_section_selection = orbat.find(id=section)
    section_roster = full_section_selection.find_all("a")
    members = [section]
    for individual in section_roster:
        members.append(individual.text.strip())
    return members

# Sorts all votes on chosen event into a dictionary 
def get_voters():
    attendancePage = requests.get(attendanceURL)
    attendance = BeautifulSoup(attendancePage.content, "html.parser")
    try:
        full_selection_voted_yes = attendance.find("div", id="ipsTabs_elAttendeesMob_elGoing_panel")
        full_selection_voted_maybe = attendance.find("div", id="ipsTabs_elAttendeesMob_elMaybe_panel")
        full_selection_voted_no = attendance.find("div", id="ipsTabs_elAttendeesMob_elNotGoing_panel")
        attending_voters_dirty = full_selection_voted_yes.find_all("span")
        maybe_voters_dirty = full_selection_voted_maybe.find_all("span")
        loa_voters_dirty = full_selection_voted_no.find_all("span")
        attending_voters = []
        maybe_voters = []
        loa_voters = []
        for attendee in attending_voters_dirty:
            attending_voters.append(attendee.get_text())
        for maybe in maybe_voters_dirty:
            maybe_voters.append(maybe.get_text())
        for loa in loa_voters_dirty:
            loa_voters.append(loa.get_text())
    except AttributeError as error:
        print("Make sure your URL was correct. I couldn't find anything at all there...")
        input("This will turn off now. Press any key and restart. Do it right next time. Bye!\n")
        sys.exit()
    votes_dictionary = {"yes": [], "maybe": [], "no": []}
    for voter in attending_voters:
        votes_dictionary["yes"].append(voter)
    for voter in maybe_voters:
        votes_dictionary["maybe"].append(voter)
    for voter in loa_voters:
        votes_dictionary["no"].append(voter)
    return votes_dictionary

# Save the votes from the event to a variable to check against with function get_attending_members()
votes = get_voters()

# Compares the list made from the ORBAT page with the dictionary containing the votes on the selected event
def get_attending_members(section_list):
    section_dictionary = {"section": section_list[0], "attending": [], "maybe": [], "no": [], "not_voted": []}
    for member in section_list[1:]:
        if member in votes["yes"]:
            section_dictionary["attending"].append(member)
        elif member in votes["maybe"]:
            section_dictionary["maybe"].append(member)
        elif member in votes["no"]:
            section_dictionary["no"].append(member)
        else:
            section_dictionary["not_voted"].append(member)
    return section_dictionary

# Renders a template to be called for each section on the ORBAT
def render_page(section_dictionary):
    page = """<h3>{}</h3>""".format(section_dictionary["section"])
    attending_list = """<div>GOING:</div><ul>"""
    for vote in section_dictionary["attending"]:
        attending_list += """<li>{}</li>""".format(vote)
    attending_list += """</ul>"""
    maybe_list = """<div>MAYBE:</div><ul>"""
    for vote in section_dictionary["maybe"]:
        maybe_list += """<li>{}</li>""".format(vote)
    maybe_list += """</ul>"""
    no_list = """<div>NO:</div><ul>"""
    for vote in section_dictionary["no"]:
        no_list += """<li>{}</li>""".format(vote)
    no_list += """</ul>"""
    not_voted_list ="""<div>NOT VOTED:</div><ul>"""
    for vote in section_dictionary["not_voted"]:
        not_voted_list += """<li>{}</li>""".format(vote)
    not_voted_list += """</ul>"""
    page += attending_list
    page += maybe_list
    page += no_list
    page += not_voted_list
    return page

# Get all the members from each section tagged with a unique ID on the ORBAT
coyhq =  get_section_members("Coy HQ")
oneplt = get_section_members("1 Platoon HQ")
oneone = get_section_members("1/1 Section")
onetwo = get_section_members("1/2 Section")
onethree = get_section_members("1/3 Section")
twoplt = get_section_members("2 Platoon HQ")
twotwo = get_section_members("2/2 Section")
twothree = get_section_members("2/3 Section")
fsg = get_section_members("FSG")
aasr = get_section_members("13AASR")
csmr = get_section_members("16CSMR")
jhc = get_section_members("JHC")
fst = get_section_members("JFIST")
sig = get_section_members("216 Sigs")
pathfinders = get_section_members("Pathfinders")
mi = get_section_members("3/2 Section")

# Compile a list of the company and a variable to hold the page
the_unit = [coyhq, oneplt, oneone, onetwo, onethree, twoplt, twotwo, twothree, fsg, aasr, csmr, jhc, fst, sig, pathfinders, mi]
page = ""

# Iterate through the list of the company, rendering the HTML-template for each of them  
for section in the_unit:
    current_section = get_attending_members(section)
    page += render_page(current_section)

# Open the target HTML-file, permissions to write to it, encoding utf-8 to ensure unicode support
filename = "{}.html".format(attendanceURL[42:-1])
f = open(filename, "w",encoding="utf-8")
f.write(page)
f.close()
webbrowser.open_new_tab(filename)