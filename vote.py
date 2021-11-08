from bs4 import BeautifulSoup
import requests
import sys
import webbrowser

# When called via cmd the user needs to specify the URL to the event to check, this should be automated if run serverside
if len(sys.argv) < 2:
    print("You need to invoke this script along with an URL to the event you want to check. Example below:")
    print("vote.py https://community.16aa.net/calendar/event/582-operation-hidden-trigger-xi/\n")


OrbatURL = "https://community.16aa.net/orbat/"
attendanceURL = sys.argv[1]
# When running serverside: replace the above attendanceURL with one of the below (not sure which one due to not being on a server yet)
#attendanceURL = self.request.url
# OR:
#attendanceURL = self.request.query_string

# Locates the orbat and parses the content
orbatPage = requests.get(OrbatURL)
orbat = BeautifulSoup(orbatPage.content, "html.parser")


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
    full_selection_voted_yes = attendance.find("div", id="ipsTabs_elAttendeesMob_elGoing_panel")
    full_selection_voted_maybe = attendance.find("div", id="ipsTabs_elAttendeesMob_elMaybe_panel")
    full_selection_voted_no = attendance.find("div", id="ipsTabs_elAttendeesMob_elNotGoing_panel")
    attending_voters = full_selection_voted_yes.find_all("a")
    maybe_voters = full_selection_voted_maybe.find_all("a")
    loa_voters = full_selection_voted_no.find_all("a")
    votes_dictionary = {"yes": [], "maybe": [], "no": []}
    for voter in attending_voters:
        votes_dictionary["yes"].append(voter.text[:-2].strip())
    for voter in maybe_voters:
        votes_dictionary["maybe"].append(voter.text[:-2].strip())
    for voter in loa_voters:
        votes_dictionary["no"].append(voter.text[:-2].strip())
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
# Coy HQ is not tagged with an ID (assumed to be "Coy HQ"), therefore commented out
#coyhq =  get_section_members("Coy HQ")
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
# FST is tagged twice, with all of Attachments being the first.
#fst = get_section_members("FST")
pathfinders = get_section_members("Pathfinders")

# Compile a list of the company and a variable to hold the page
the_unit = [oneplt, onetwo, oneone,  onethree, twoplt, twotwo, twothree, fsg, aasr, csmr, jhc,pathfinders]
page = ""

# Iterate through the list of the company, rendering the HTML-template for each of them  
for section in the_unit:
    current_section = get_attending_members(section)
    page += render_page(current_section)

# Open the target HTML-file, permissions to write to it, encoding utf-8 to ensure unicode support
f = open("attendance.html", "w",encoding="utf-8")
f.write(page)
f.close()
webbrowser.open_new_tab("attendance.html")