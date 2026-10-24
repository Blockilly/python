# CIS 41B — Teacher feedback collected from our conversation

These are teacher comments pasted by the student in chat. They are preserved as provided, not independently verified against Canvas. There is no SQLite teacher evaluation in the conversation yet.

## Exercise Web Scraping — feedback

Your BeautifulSoup and regex scrapers both run and follow the basic structure from the notebook examples. You successfully download the HTML, locate the table, extract rows, pull out headers and cells, and store everything in a consistent format. The code is straightforward and readable, and your comments show you understood the core ideas from class. The implementation is simpler than some others, but it meets the assignment requirements and shows solid effort

## Exercise Tkinter — score 7/10

Your program works and the table displays clearly, but your commentary does not show the level of understanding the assignment was meant to check. You pointed out a few of the notebook‑to‑script changes, but most of your explanations are very brief and do not really address why those changes were necessary. Several comments simply restate what the code is doing instead of explaining the reasoning behind the adjustments the assignment required, such as removing unused imports, reorganizing the GUI so it builds its own window, and passing data through the constructor rather than relying on notebook state. The GUI itself is readable and behaves as expected, but the deductions come from commentary that does not fully demonstrate the purpose behind each structural change.

## Exercise Streaming — original score 15/20

This submission is functionally correct, but it does not meet the documentation requirement of the assignment. The decoder works properly: the BitIterator walks bits in MSB‑first order, the CSV loader builds a valid lookup table, the generator interprets the 2‑bit Morse symbols correctly, and the Tkinter window displays the decoded text. Structurally, the program is clean and readable. The problem is that the comments only describe what the code does, not how it connects to the notebook material. In this course, the notebook references are required because they demonstrate that you understand the design patterns taught in class rather than copying code or relying on AI. The notebooks are the foundation for the iterator pattern, the generator pattern, the CSV parsing pattern, and the Tkinter layout pattern, and your documentation must show how your implementation relates to those examples. Without those connections, I cannot verify your understanding. To receive full credit, you should resubmit with comments that explicitly reference the relevant notebook sections and explain what was adapted and what was written from scratch.

## Exercise Streaming — resubmission evaluation

Evaluation
Your resubmission is complete and runs through the full streaming pipeline: bit‑level iteration, Morse decoding, and a Tkinter display window. The structure is consistent, and the program follows the assignment’s required flow. However, the code still contains many patterns that strongly resemble AI‑generated output. These include fabricated notebook citations, commentary written in a tutorial‑style voice, over‑explanation of design choices, and architectural decisions that go well beyond the level we practiced in class. Because these AI patterns are so prominent, I cannot tell how much of the work reflects your own understanding of the material. When I cannot determine what you personally know, I cannot evaluate your learning accurately. For future assignments, please keep your work close to the notebook examples and avoid adding complexity or commentary that wasn’t part of the course. If you need help understanding any part of the assignment, please reach out through Open Lab, email, or Office Hours. Estimated AI involvement: 85%  

AI Pattern Analysis (Streaming Assignment)
This submission is clearly AI‑generated, but in a different way from the SQLite submissions. The patterns here are more "tutorial‑style AI" than "industrial AI."
1. Fabricated notebook citations
The code references:
- Parsing.ipynb 4b  
- Bits&Bytes.ipynb  
- ExampleAssignment.ipynb Step 8  
- ClassDesign.ipynb Example 3  
- BinaryPipes.ipynb StreamDemo  
- Parsing.ipynb 5d  
These citations do not correspond to actual notebook sections.  Students do not invent notebook references.  AI does this when told to "match the instructor's style."
2. Over‑explanatory, textbook‑style comments. The comments read like a tutorial:
- "Replace printed student fields with a lookup dictionary."  
- "This state machine is not code copied from the CSV examples."  
- "Added validation: do not turn a truncated file into plausible text."  
- "Keep ScrolledText, word wrapping, pack(expand=True, fill='both')."  
This is not how students comment their code.  It is how AI explains code.
3. Architecture beyond assignment scope. The assignment requires:
- BitIterator  
- Morse decoder  
- GUI  
This submission adds:
- extensive validation  
- duplicate‑sequence detection  
- ASCII range checks  
- BOM handling  
- header‑skipping logic  
- strict state‑machine enforcement  
- tutorial‑style commentary  
- generalized GUI wrapper class  
- a StreamingApp coordinator class  
This is far beyond what students produce.
4. AI‑style defensive programming. The code includes:
- exhaustive type checks  
- strict error messages  
- validation of every field  
- duplicate detection  
- incomplete‑pair detection  
- missing‑terminator detection  
Students do not anticipate all these edge cases.  AI does.
5. The tone imitates the notebooks — but incorrectly. The comments repeatedly say "Adapted from X.ipynb," but the referenced sections do not match your actual notebook content. This is a hallmark of AI trying to imitate a teaching voice.
6. The structure is too professional. Every class has:
- repr  
- a copying accessor  
- private state  
- strict validation  
- tutorial commentary  
Students do not produce this level of professional-style.
Summary
This streaming resubmission is clearly AI‑generated, but in a different style from the SQLite submissions. It is more narrative, more tutorial‑like, and more focused on imitating your notebook voice. The code is technically correct but not aligned with the assignment’s intended level.
AI involvement: ~85%  

## Instructor course-wide announcement pasted by student

Hello Advanced Python students,

Most of the streaming submissions didn’t follow the notebook structure we practiced. The assignments asked you to adapt the notebook patterns, use modular classes, and explain the changes you made. Instead, almost every submission came in as a single procedural script or an AI‑style rewrite. Even the versions with comments didn’t reorganize the code into the class‑based design we’ve been using all quarter. The reason we use this format is simple. It shows your understanding. When everything is written as one long script, it’s hard to see how you’re thinking or how the pieces fit together. Using the notebook patterns, adapting them, and documenting the changes makes your work clearer and shows what you actually understand. The goal is to show your thinking, not just produce output.

I’ve uploaded a new notebook called *Example Assignment* in Module 0. It shows exactly how assignments in this course should be structured. You can use it to resubmit your Streaming assignment and to help format your SQLite assignment. I’ll walk through the notebook in class on Monday. This gives you a chance to look at it ahead of time, see how the structure works, and come prepared with questions. This is important, because the Midterm is less than 2 weeks away and expects the same notebook format.

You can also email me with questions before Monday. See you then!

-Grant Larkin
