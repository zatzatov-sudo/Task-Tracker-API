# Reflection

Being a non-programmer, when I started this course, I thought the hardest part would be writing the code. 
It turned out that writing the code was actually the straightforward part with the help of AI tools.

The harder parts were making sure the code worked correctly by passing the appropriate tests, understanding why things broke when they did, and keeping track of every decision I made along the way, especially the fear of loosing a "working" code.

Before this project, I thought of tests as something you write at the end to check that things work. But building the pytest suite as I went and
running it after every single change, meant I caught problems immediately instead of hours later when I'd already moved on and forgotten what I touched.

There was a moment when I added the tags feature and the test suite came back with nine failures all pointing to the exact same missing field in
storage. That would have taken me a long time to debug manually. The tests just told me exactly where to look. That felt like a real shift in how I think about building any next project.

Documentation was something I used to think of writing it at the end and move on, taken by the excitement of a working code. This project showed me that it's actually useful while you're still building. Writing down what a feature was supposed to do, what constraints it had to respect, and what was deliberately left out of scope meant that when I came back to something after a break, I didn't have to
reconstruct all the context from scratch.

The structured pathway; plan, constrain, implement, inspect, verify, test, document, felt a bit slow at first. But looking back at the commit history, I can see exactly what was built, why, and in what order. That's something I wouldn't have had if I'd just written
code and hoped for the best.
