**What I learned**

While implementing this multi-agent workflow, I learned the limitations of AI Agents. Even though I thought that my prompt engineering for the Planner and Reviewer were direct and descriptive, I still saw how the Planner would occasionally make mistakes or the Reviewer would miss something that I explicitly prompted it to check for.

Through lots of prompt engineering and rephrasing, I learned that even with our dedicated Reviewer agent to look over and fact check the generated plan, there is always the chance that something will be missed or uncorrected. I think that this validates the discussion we had in class about faith and accountability in our current AI Agents. While we may expect that the AI Agent can look over a short plan and check the feasibility with internet searches, our current models are not good enough to check and correct every mistake.

**Challenges**

Like I mentioned before, I encountered challenges with getting the Reviewer agent to correctly identify and correct all mistakes in the generated plan. Sometimes the Reviewer identified mistakes and correctly put them in the Delta List, but then would not apply those changes to the Validated Itinerary. To fix this, I added to the prompt that it should go through the delta list and correct each mistake that it identified. Overall this seemed to improve the performance, but every now and then I will still see that a change is present in Delta List but uncorrected in the Valid Itinerary.

Additionally I encountered some problems with the model wanting to adjust things for no reason. For example, if the Planner scheduled a Louvre visit at 10:30, but the Louvre opens at 9:30, the Planner would want to move it earlier to 9:30, giving the reason that it was to “maximize the time available” even though my prompt made no mention of this. To try and reduce the chance of this, I modified my prompt to tell the reviewer to not make unnecessary changes to the schedule if a conflict, budget, or hours issue was not encountered. This reduced the occurrences of these changes that I noticed, though did not completely remove the likelihood of them being present.

**Design Choices**
I did not make any changes to the overall Streamlit app. I did some prompt engineering as I specified above, as well as specifically telling each agent its role as either a trip planner or trip reviewer/feasibility checker.

**AI Usage**

I wrote out my prompts and used Copilot to refine them with adding more specific details and instructions for the agents to better understand

