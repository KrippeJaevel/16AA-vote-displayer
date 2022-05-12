# 16AA-vote-displayer
Python script intended to render the votes for an event, and to display who has yet to vote.

WHAT IT DOES:
It compares the ORBAT (as it is) with the chosen event and renders a list of who has voted what, and who has yet to vote.
You can run this several times. It generates a local html-file locally, and displays that in a new tab on your web browser.

HOW TO USE:
Run vote.py in a command line interface (such as cmd). It will display a number of upcoming events to choose from or prompt you for a URL to a specific event you want to check attendance for.
It runs it's magic and stores the results in an offline html-file which is opened once rendered.


LIMITATIONS:
If you enjoy fancy designed webpages prepare for dissapointment.
Way too much stuff is hard coded in this file, so it is bound to break down eventually.
I'll try to stay ontop of maintaining it until a better solution is made by someone who cares.
Until then, good luck!

CHANGELOG:
1.3:
"Improved" the user experience to allow for less copy paste of URLs which makes crayoneaters confused. Tasty crayons...
1.2.1:
Corrected logic to find names instead of links with name as tooltip and stuff.
Included version number in prompt.
1.2:
FST renamed to JFIST on the website, adapted script to stop fucking up and breaking down.
Included MI under the name 3/2.
1.1:
Includes Coy HQ, Signals and FST who were previously not included due to website structure.
