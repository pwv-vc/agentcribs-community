# PWV Founder Sessions: AgentCribs™ Series
**Date:** February 25, 2026  
**Host:** Jennifer Tacheff (PWV)  
**Speaker:** Sam Odio  
**Video:** Password-protected Vimeo recording of the session  
**Note:** Auto-generated captions cover ~0:00–33:04. Remaining ~24 min of Q&A not captioned.

---

## Raw Transcript (VTT → cleaned)

**[0:00]**
Um, yeah. So this, this originated because I perceive, uh, or at least I have struggled with a signal to noise problem with like all the Twitter. Like, Hey, you've gotta use this tool now. And then like tomorrow, it's like, oh, actually, that, that tool is all news. You gotta use this new tool, um, or open source repo or, uh, language model, et cetera.

And, um, and, you know, it's almost a full-time job just to like, sift through all of that and figure out what it looks like to, to actually write real code that real users use without bugs or, um, security vulnerabilities. Um, and, um, and, and do that productively, um, at the bleeding edge. Right?

Um, and actually with that, I have to caveat, I just had a baby one month ago. This, this is my, this is my second day coming back from paternity. And so a lot of what I show you is gonna be probably old news, right?

Um, and, uh, and so my, my hope in and like creating a community is, is to learn as much as I share, um, if not, if not more. And so, uh, I'm only, I'm, I'm, I'm gonna kind of go through what I do and a little bit about my company, but my, you know, really my aspiration is to figure out like, hey, together, how can we solve this signal to noise problem?

If you don't think there's a signal to noise problem, and you feel like you have a source for all of the right, like workflows and tools to use this, probably we can just end this call right now. Uh, and I'd love to — No, no, they do the next demo. That's, that's fine. Yeah. That'll be the next time. Yeah.

More than the demo though, is like, teach me to fish. You know, like, I, I wanna know where you, what your resources, um, 'cause I, I feel like I'm just scraping everything together from like, people I, I know and trust.

Um, this is my aunt who's here taking care of the baby. So she has to say hi, uh, she's allowing me to do this. So, um, okay.

**[2:11]**
Actually, so one of the things I kind of wanted to do is just before I even share anything, start off with a little bit of a survey to get a lay of the land. And, um, I am curious, does everyone know how to use, like, reactions? Like the, the, the thumbs up reaction in, um, yeah. Okay.

I think, um, actually, sorry. I think we want to use the raise hand reaction. 'cause I actually want to get a count for these, uh, questions. So, you know, like, raise your hand, um, if, if the answer is yes.

So I'm curious, how many of you write code, um, write code in a completely automated fashion so you're never writing a line of code by hand? Raise your hand.

Okay, we have like, 1, 2, 3, 4, 5, 6 — about 12. Okay. Um, okay. So you can lower your hands. I'm curious how many of you are — I'm gonna just gonna name a number of tools. How many of you are using Superpowers or how many of you are actively using Superpowers?

Okay. One. Um, how many of you are using Steve Yogi's Beads? Open source repo? None. How about Ralph Wigga? None. How about OpenClaw? Four. How about — how about SuperSet Conductor? Human Layer? Three.

Okay. How about, um, Claude, uh, how, how, how about, um, and, and like MCP — you're using some sort of MCP server in your development process? And how about like Claude skills in the development process?

Nice. Uh, how many of you are using more than 10 Claude skills? Three. One of them is on my team.

Um, cool. All right. So, um, if you are using Superpowers or more than 10 Claude skills, I think what I'm gonna show you may look like old news. Um, and, uh, and I would love for you to present, uh, your workflow or show me how to work more effectively.

**[5:00]**
Um, so let me just share a little bit about, uh, my startup. So I am a two time YC founder. I'm found — I just founded another company. Uh, we raised about $3 million. Um, and we're very much in the, uh, product market fit exploration phase, right? I like — people call it wandering in the wilderness. I like to describe it as like searching for a key in a, in a, in a black room, right? And, you know, you see the light underneath the door, you know, there's light on the other side of the door, uh, but the door is locked and you don't know if, uh, if the key is in the room or under the pillow or like right next to your hand, right? And so we're definitely in that mode right now.

I'll just share a little bit, um, about us. You can kind of see one of our prototypes, uh, at chatrun.com. Uh, this is probably small, but, uh, and, and essentially it's built on this premise. We, we have a, we have a phone number. So this is built on the premise that apps are really a means to an end. What, what users really want is like a job to be done. We believe in the future, you're not gonna interact with apps, but you're gonna interact with, um, what feels like humans, right? And, uh, and that could be phone numbers, right? And so we, our product is exclusively a phone number. We're focused on saving high conflict marriages from divorce.

We believe people don't want couples therapy, you know, they want when it's 9:00 PM and their husband's yelling at them, or, or their spouse is being an ass. They want to like, solve that problem in the moment, right? And so we have an infinitely patient, infinitely available, uh, phone number.

Um, in my case, I, whenever I text my wife, Abby, I do it on a group thread with this phone number. And this phone number tells me how I can be a better human to, to my wife, and, um, does all sorts of cool stuff, which is kind of outta scope of this conversation.

**[7:00]**
As far as like the state of the company right now, we have about 200,000 lines of code. Just now is like trying to calculate how many human hours that would be. So if you're writing 50 lines of code a day, or I guess a, uh, maybe a hundred lines of code a day, um, you know, that's 20,000 days of, uh, of engineering days of work. About a hundred thousand of that is our core Python app. Actually, half of that is our validation suite right now. Um, and then we have 30, 31,000 for the front end, 62,000 for, for our infra — it's all, all of our infra is in code. That help — that, that's key for, um, uh, language model coding and, and development in my opinion. And then, um, our CLAUDE.md and associated directories is 32,000 lines of code right now.

Uh, our core stack is pretty standard. Maybe LangFuse is a little bit unusual. I think there are actually better, um, prompt management suites today that you can use. And we use PG Vector for our vector databases.

As far as our usage, like I mentioned, we're very much in product market fit. Uh, we have 25,000 messages sent, and we have 188 active users. Um, and for us, like HIPAA and security matters a lot. For example, we had 13 self-harm alerts, um, in the last 30 days. So these are messages flagged, uh, where, uh, the user is, is, um, ideating or threatening to, to physically hurt themselves. One actually triggered a mandatory reporting policy. We have a therapist on staff, and that therapist reported, you know, and worked with actually a local police department to do a welfare check. Um, and then we have five engineers.

**[8:47]**
Cool. Uh, so our, our like key principle is: software production is cheap, but software validation is hard.

And I'm gonna kind of go through, um, like that in a little bit more detail. And then I'm, I'm hoping to do a demo where I actually double click on some of this. So this is where we are today.

Uh, and then this is where we, we hope to be — actually, does somebody have a question? Just heard an unmute.

Maybe before I continue, I, let me just stop. And is there anything I'm saying surprising or any reactions to anything?

Cool. All makes sense. All right.

**[9:31]**
So I would estimate today we have a one to five token ratio. So one token spent on validation for every five tokens spent on code. We actually want to target in, um, flipping that where we spend five tokens on validation for every one token on code, um, by — by 25x increasing the amount of tokens we spend on validation.

Uh, today our philosophy is we want to test behavior, not implementation. So we lean heavily into smoke tests and end-to-end tests and all, um, kind of briefly demo that.

Uh, in the future, we want to test outcomes non-deterministically with simulated traffic at, at scale, kind of simulating, um, our, our entire user base.

Um, and, uh, today we connect feedback loops using, uh, Claude skills. This is the thing that David, we were talking about in the car. This is the thing I'm gonna demo — spend most of the time demoing. In the future, we want to encode business and user goals into a, a self-healing product development lifecycle. Today, we review code, um, manually as humans. In the future, we want to remove ourselves from the code review process.

Any questions about this? Okay.

**[10:52]**
Um, so what I want to really demo is, is essentially this 32,000 lines of code, um, and how that allows us to connect feedback loops and work more effectively.

So just share my whole screen.

Okay. You all can see this. Okay. Actually, um, before I continue — one thing. So I, I was very torn for this demo because, um, user privacy is very important to us. For, for me, really to demo this, I have to show you real user data. And I'm, and so I am, I am in an, in an authorized state, right? As an employee within the company. Um, I have a filter here to protect PII — I'm gonna show you my actual data with my wife Abby.

Um, there is a non-zero chance that I, on this call, leak PII in some capacity that this filter does not work. If that happens, I would just ask, um, that you all keep this conversation confidential and David will have to, you know, follow up regarding the recording and, and all of that. Um, and I want to take this risk to, to, to, to really like open kimono — show you, um, show you how we, how we work. Okay? All right.

**[12:31] Old World**
So, um, this is the old world.

Sam. Is there any way you could boost the font? Yeah, yeah. Here we go. There you go. Maybe it's good for me. I don't know about others. I'm, I'm on a laptop, so I, I just make it a little bigger. I'm good. You're good? Okay. Yep. Um, so this is the old world.

I actually kind of tested a few queries in the old world. So, um, I asked, please look at the user behavior from the last week. Any interesting behavior that would imply product feedback. And then I asked — let's see, what else did I ask? Um, I asked, why did this error happen? So I copy and pasted an error from our alerts channel. And then I asked, uh, can you describe the health of Sam and Abby as a couple?

Um, but I can really ask any question and you, you all are, are free to, to, uh, actually suggest questions. So I can ask, uh, what, what does our onboarding funnel look like?

Um, somebody, somebody put a question in chat. You can ask what, what, uh, could you improve on your relationship with Abby and see if it — Okay, uh, let's see.

Okay, so, um, so again, this is the old world and, you know, not to kind of bury the lead here, but you can imagine what the, what the answer's gonna be, which is effectively all of these questions are not particularly helpful, right?

So, you know, why did this error happen? I pasted that in, uh, the answer is one of your LLM calls hit its, cut off mid-generation because it hit the max completion tokens limit. That, that, I mean, that was actually clear from the error, right? OpenAI response truncated — hit max completion tokens limit, right?

Um, I asked, please look at the user behavior from the last week. And it kind of just suggests like things that I could do to look at the user behavior from the last week, right? So this is kind of the old world.

**[15:22] New World**
Now, let me switch over to the new world here.

Um, let's see, what did I ask here? Okay, so why did this error happen? Check — you know, and I paste the log in. So the answer I got in the new world is, um, on February 26th at 1317 UTC, this particular prompt — I can actually view the LangFuse trace for that prompt. So this is the URL to the — oops, there, let's see, I'm getting 404 for that. Let's see. 404.

Um, you know, but I'll link to the LangFuse prompt. What happened? Here's the job IDs. Um, and the, this particular prompt had 11,000 tokens. The completion token limit was 512, it hit the limit. Exactly, right?

And so there's actually a risk assessment and then a, a suggested change, right? Um, so it's figuring out — it's actually using a skill to figure out that the LangFuse URL is incorrect. So I can actually say, can you please implement your change and fix?

Okay? So then Sam and Abby. So again, in the old world, we really couldn't answer that question. In the new world, um, Sam and Abby — overall healthy and stable over the past two to three weeks. Uh, our affect ratio — so this is a, an actual relational term that predicts the stability of your marriage and longevity of your marriage. There are two other complaints. There's, uh, zero conflict in three of the four. Okay?

So now I can ask what Daniel suggested — what can Sam do to improve the relationship?

Um, I can ask, um — onboarding. So run the actual onboarding funnel analysis. Okay?

And then over here I asked, please look at the user feedback from the last week. Any interesting behavior that'll imply product feedback. And it is actually kind of fascinating.

**[17:55]**
So what it said, um, is 50 new users onboarded this last week, zero converted to couples. This is, to be honest, this is, this is like full kimono. This is our number one strategic problem as a company.

Um, no digital product in the history of humanity has solved this problem at scale, which is the double opt-in for, for couples, right? And, uh, you know, like the closest is maybe Paired — I think Paired has, um, few million downloads, right? But it just, the double opt-in kills, um, our onboarding funnel and it, and so it's identifying that organically.

Um, it's saying that your, your users are onboarding 1-on-1, but not converting to couples. Um, it gave me a couple options for how to fix this. Um, which is one is: embrace one-on-one as a standalone product. And then the other is: hard gate one-on-one coaching.

Um, option one is clearly the winner, given the data. The 0% conversion rate isn't a funnel problem to fix — it's the market telling you what the product actually is, right? So it's arriving at that conclusion.

I, my response was — um, let's see if I can pull that up while this is thinking.

I don't want to — ah, shit, I interrupted it. Please continue.

So, um, so I, I asked, please look at our user behavior, then I asked, uh, what changes would you make to the LangFuse templates? What's your number one product suggestion? I made that suggestion. I said — and now it, it wrote a spec. And so it's actually implementing it. And critically, um, it is, it is implementing this in our LangFuse templates themselves. So once this is done, I'll actually be able to pull up LangFuse and, and look at the new product experience and, and, um, and deploy that new product experience to production.

**[20:02]**
Um, so what it's — it's literally in, in the, this is like in the last hour pivoting our company, right? Based on user feedback.

Um, okay, so what else?

Uh, okay, so let me just show you one more old world / new world. So when we started Wren, this was in 2024, we ran a bunch of Facebook ads, and this was like a one month process. I had a full-time — I still have a full-time designer running these ads, uh, managing Facebook. So that was in the old world.

In the new world, we can automate — we can automatically, um, come up with a dozen variants of Wren, right? Um, schedule user interviews. We can then actually take one of these variants and we can say, um, so I just actually asked this — can you use the end-to-end ads campaign to create a skill? And I pasted in this variant.

So it's, uh, just created — this just came back, um, five new landing pages. It's asking me which one I like. Oh, I like this one — Table Talk. I like this one — when you create ads.

Um, so now it'll create — actually just ran this this morning. So while it's thinking, let me just switch over to, uh, it created five different, um, hero images for those ads. Um, this was the landing page — it created, actually created a couple different landing pages, um, and Facebook. It created, uh, 273 ads. Just different variants of images and, um, uh, copy. You know, this is, this is one of those ads that I created this morning: "One call, two coffees, zero screens. Personalized couple insights from a real conversation." Right?

And so now I can just turn all these ads on and Facebook will obviously manage, um, determining which, which ad is the winning ad, and, and then we can tie that back into the, into the product roadmap.

**[22:14]**
Cool. So that did all that in like, um, in prep for this call in the last few minutes. This will take a little while. This one is the slowest — Daniel, how long does this take?

> **Daniel:** From beginning to end, it's like 15 minutes, uh, from since the, uh, HTML pages design to you choosing and then selecting the ads ideas and it coming up with the ads is like 50 minutes.

Yeah. So, um, that hopefully gives you a sense for how we are using — we actually, we, we, we call it Arsenal. It's an internal, uh, repository. I think Superpowers is a close proxy for this, so you can just assume it's Superpowers, but how, how we're using Arsenal — uh, those 30,000 lines of code to connect feedback loops, whether it be written user feedback, um, behavioral feedback, like, or, or behavioral feedback like ad performance or, or product usage. Um, and connect it, um, to, to into a full cycle. Right now we get the feedback, we can deploy code, we can deploy edits to our prompts to LangFuse, but there's still a human in the loop. Same with — we can deploy ads. There's still a human in the loop to turn things on. Uh, but our long-term goal is to remove the human in the loop.

**[23:42]**
Is it okay for me to respond to this Michael question?

> **Jennifer:** Yeah. So yeah, he thinks this concept for running the, uh, validation pipeline is a product by itself. So he's curious about how that was built.

And, uh, I guess the, my mindset when I'm building stuff is, uh, Claude is doing everything. So I, I would just start a process of brainstorming. So, uh, there's Arsenal that is, or, uh, set up for letting Claude develop things the way we want. So I would just brainstorm the concept and making sure that there is a way to validate — for, for example, in this case, uh, if I have access to the Facebook ads API and Claude knows to do that, uh, I can ask, Hey, can you come up with ads — and I tell it how to verify, so it can go to Facebook and verify the ads are there. Um, so as long as you have like this concept of how, how to instruct the AI to validate the work that it is doing, uh, we're just applying this, this strategy on, uh, everything that we, we want to ship. This product was just another experiment.

**[25:06]**
You are on mute now, Sam.

Oh, I'll just demo one last thing here, and then maybe we can just move into like a Q&A. But, uh, yeah, so the, the pivot to, um, from a couple's product to a one-on-one product just landed, you know, and so currently our, our workflow — you can see these are the URLs for the, um, for each template. We, we use about 150 prompt templates in our product experience. And then I can kind of diff these — uh, this is all the work that Claude just did, and, um, and then if I'm happy with it, I, I promote those prompts to production, which I'm not gonna do. Um, 'cause I'm not ready to make that pivot.

Um, and then, you know, obviously again, you know, the really, the, the hard thing here is, um, validation, um, which is why, um, we — this is, this is sort of the 40,000 lines of code that I described. We, we have a validation suite that whenever we're, we're writing code, we'll run it through the suite. The suite will simulate, um, users interacting with the product and then obviously fail, um, if, uh, if the, if the product responds in unexpected ways.

So, cool. Okay. That's just a, that's what I'm doing.

**[26:35]**
Any, any questions? Anything, anything in my work? I'm also very curious, like, is there any anyone else willing to demo or anything?

> **Jennifer:** Let's, let's do — yeah, Sam, if you, so no more demo from you or your team, correct?

Yeah. Which is great. Okay. Yep. Let's, let's do at least 10 minutes. Well, maybe I'll watch the clock for 10 minutes — I'm sure people have questions for you. And then maybe spend the final 15, 20 minutes kind of as the community at large talking about where to go from here and broader comments. But I wanna make sure people get to talk to you first. So sound good?

Great. Let's do it. Okay. Prepare. Here they come.

**[27:14] Q&A**

> **Attendee:** Hey, Sam, that was, uh, really, really cool to see. Thanks for walking us through that and being so transparent. I think I had kind of two questions. One is just how would you define or describe the main differences from before and after? And apologies if I missed that, but you kind of shared like, here's the old way, here's the new way. What, like, what was the core piece of the change? And then, yeah, the second question is just like, uh, what do you have a crisp definition of what validation means for you? Because I think there's different ways that can be understood semantically. So I was just curious how, how you've been thinking about it.

Okay. So as far as before and after — I'd say before I was a vehicle to shuttle context from the, the, the rest of the world to the language model to the developer, right? And the developer was sort of locked in a box. Um, and I underestimated the amount of overhead that that created for me as a developer.

Um, so that's how I describe the difference between the before and after. And so in the after world, you know, I can essentially ask Claude any question about my product. Um, we, the — and this is really where the 40,000 lines of code comes from — is, is essentially giving Claude access to the world that is relevant to it for, for my purposes, right? So it has access to our AWS CloudWatch logs. It has access — it has read-only access to our RDS database, our vector databases. It has access to, um, the codebase, obviously LangFuse the prompts, um, uh, um, our Meta ads account. Um, so, uh, with the goal of connecting the product development lifecycle, connecting from user feedback — you know, the test, learn, um, iterate loop.

Does that answer your, your first question? Okay. Remind me what your second question was?

> **Attendee:** Just how you define validation.

Validation. Okay. Yeah. You know, I, um, I think ultimately we, many of us here probably want the same thing — product market fit. And, um, and so the question is what is the product experience that delivers that within the scope of our, our mission?

Um, and I, I'm long term, my hope with validation is — if it looks like a duck, talks like a duck, walks like a duck, you know, that's great. That passes the validation test. You know, if, if we're able to deploy a product that has user signals indicating product market fit and does not have some sort of major security vulnerability, you know, like that's what I'm looking for, right?

And so that's at the highest level. You can double click that in many different directions, right? You can, you can double click and look at, um, like price sensitivity and willingness to pay and like make that an outcome that you are testing for in your, um, in your feedback loop. Um, you can double click that and look at, okay, based on these thousand simulated behaviors, uh, how does the product respond and does it respond in an expected way? Uh, which is something we do.

We actually know of another company — and this is really fascinating to me. This company, uh, is in the enterprise space. They have, um, something like a hundred of the S&P 500 as clients. They've actually simulated 10 companies and have for each of those companies, 500 employees that are agentic. So that's, you know, 5,000 employees are, are using their prototype product continuously 24 hours a day, and they're looking for business outcomes. They're actually looking for business outcomes based on their product. Do these synthetic employees use the product differently? And they use that as a gate to determine whether or not they want to deploy the product to all of their human users.

So, um, yeah. Does that answer your question?

> **Attendee:** Yeah, no, that's, that's super helpful to see that, that dimension of validation. And I did have one other question, but I don't know if someone else wants to jump in.

> **Jennifer:** There's some questions in chat too, Sam. Yeah, yeah. We can circle back to me if you want to take some of those.

**[31:52]**
Yeah, maybe I'll just, uh, pull up Arsenal — and I'm happy we have this, um, closed because of just kind of latent PII risk, uh, if we were to open source this to the world, but I'm happy to actually share this, uh, repo with anybody. So, sorry, let me answer the question. How is the 40K CLAUDE.md organized?

Uh, and I'm gonna do that by pulling up, um, Arsenal, which is effectively a submodule, which we install. Um, we install this in our core product, right? And so we, what we do is we install the GitHub submodule, um — shout out to GitHub, by the way, uh, for helping us, uh, organize all this very, very, very, uh, apropos.

And, uh, and what this does is, um, this install script effectively copies, um, into your top level CLAUDE.md. I'm not gonna, I'm not gonna really go through the, the CLAUDE.md right now, but I'm, I'm happy to do that. I think the kind of maybe some of the more interesting stuff is your docs/claude directory.

---

*[Transcript ends at 33:04 — remaining ~24 minutes of Q&A/community discussion not auto-captioned]*
