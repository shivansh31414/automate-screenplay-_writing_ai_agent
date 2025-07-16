import re
import yaml
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

load_dotenv()

# Use Path for file locations
current_dir = Path.cwd()
agents_config_path = current_dir / "config" / "agents.yaml"
tasks_config_path = current_dir / "config" / "tasks.yaml"

# Load YAML configuration files
with open(agents_config_path, "r") as file:
    agents_config = yaml.safe_load(file)

with open(tasks_config_path, "r") as file:
    tasks_config = yaml.safe_load(file)

## Define Agents
spamfilter = Agent(
    config=agents_config["spamfilter"], allow_delegation=False, verbose=True
)

analyst = Agent(config=agents_config["analyst"], allow_delegation=False, verbose=True)

scriptwriter = Agent(
    config=agents_config["scriptwriter"], allow_delegation=False, verbose=True
)

formatter = Agent(
    config=agents_config["formatter"], allow_delegation=False, verbose=True
)


scorer = Agent(config=agents_config["scorer"], allow_delegation=False, verbose=True)

# this is one example of a public post in the newsgroup alt.atheism
# try it out yourself by replacing this with your own email thread or text or ...
discussion = """From: keith@cco.caltech.edu (Keith Allan Schneider)
Subject: Re: <Political Atheists?
Organization: California Institute of Technology, Pasadena
Lines: 50
NNTP-Posting-Host: punisher.caltech.edu

bobbe@vice.ICO.TEK.COM (Robert Beauchaine) writes:

>>I think that about 70% (or so) people approve of the
>>death penalty, even realizing all of its shortcomings.  Doesn't this make
>>it reasonable?  Or are *you* the sole judge of reasonability?
>Aside from revenge, what merits do you find in capital punishment?

Are we talking about me, or the majority of the people that support it?
Anyway, I think that "revenge" or "fairness" is why most people are in
favor of the punishment.  If a murderer is going to be punished, people
that think that he should "get what he deserves."  Most people wouldn't
think it would be fair for the murderer to live, while his victim died.

>Revenge?  Petty and pathetic.

Perhaps you think that it is petty and pathetic, but your views are in the
minority.

>We have a local televised hot topic talk show that very recently
>did a segment on capital punishment.  Each and every advocate of
>the use of this portion of our system of "jurisprudence" cited the
>main reason for supporting it:  "That bastard deserved it".  True
>human compassion, forgiveness, and sympathy.

Where are we required to have compassion, forgiveness, and sympathy?  If
someone wrongs me, I will take great lengths to make sure that his advantage
is removed, or a similar situation is forced upon him.  If someone kills
another, then we can apply the golden rule and kill this person in turn.
Is not our entire moral system based on such a concept?

Or, are you stating that human life is sacred, somehow, and that it should
never be violated?  This would sound like some sort of religious view.

>>I mean, how reasonable is imprisonment, really, when you think about it?
>>Sure, the person could be released if found innocent, but you still
>>can't undo the imiprisonment that was served.  Perhaps we shouldn't
>>imprision people if we could watch them closely instead.  The cost would
>>probably be similar, especially if we just implanted some sort of
>>electronic device.
>Would you rather be alive in prison or dead in the chair?  

Once a criminal has committed a murder, his desires are irrelevant.

And, you still have not answered my question.  If you are concerned about
the death penalty due to the possibility of the execution of an innocent,
then why isn't this same concern shared with imprisonment.  Shouldn't we,
by your logic, administer as minimum as punishment as possible, to avoid
violating the liberty or happiness of an innocent person?

keith
"""

task0 = Task(
    description=f"{tasks_config['task0']['description']}\n### NEWGROUP POST:\n{discussion}",
    expected_output=tasks_config["task0"]["expected_output"],
    agent=spamfilter,
)

spam_crew = Crew(
    agents=[spamfilter],
    tasks=[task0],
    verbose=1,
    process=Process.sequential
)

spam_result = spam_crew.kickoff()
if "STOP" in spam_result:
    print("🛑 This message will be filtered out due to spam/vulgar content.")
    exit()
# 🎭 Main creative tasks crew
task1 = Task(
    description=f"{tasks_config['task1']['description']}\n### DISCUSSION:\n{discussion}",
    expected_output=tasks_config["task1"]["expected_output"],
    agent=analyst,
)

task2 = Task(
    description=f"{tasks_config['task2']['description']}\n### DISCUSSION:\n{discussion}",
    expected_output=tasks_config["task2"]["expected_output"],
    agent=scriptwriter,
)

task3 = Task(
    description=tasks_config["task3"]["description"],
    expected_output=tasks_config["task3"]["expected_output"],
    agent=formatter,
)
creative_crew = Crew(
    agents=[analyst, scriptwriter, formatter],
    tasks=[task1, task2, task3],
    verbose=2,
    process=Process.sequential,
)

result = creative_crew.kickoff()
result = re.sub(r"\(.*?\)", "", result)

print("===================== 🌟 FORMATTED SCREENPLAY 🌟 ================================")
print(result)
print("=================================================================================")

# 🧪 Run scoring task separately
task4 = Task(
    description=f"{tasks_config['task4']['description']}\n### SCRIPT:\n{result}",
    expected_output=tasks_config["task4"]["expected_output"],
    agent=scorer,
)
score_crew = Crew(
    agents=[scorer],
    tasks=[task4],
    verbose=1,
    process=Process.sequential
)

score = score_crew.kickoff().split("\n")[0]
print(f"✨ Scoring the dialogue: {score}/10")