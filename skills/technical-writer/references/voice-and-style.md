# Voice and Style — how the prose actually sounds

This file governs every sentence this skill writes or reviews. The methodology
(`methodology.md`) decides *what* to say; this file decides *how it sounds*.
Read it before drafting, rewriting, or auditing any prose. It is distilled from
a real, high-performing tutorial corpus (CloudBytes) plus a catalog of the AI
tells that make readers close the tab.

The target voice: **an experienced engineer who has already solved this once,
walking a reader through it without wasting their time.** Explain just enough
context, show the exact command or code, then tell the reader what to verify
next.

---

## The voice

Write with:

- **Direct second person**: "you need", "you can", "open a terminal", "run the
  following command".
- **Inclusive walkthrough language**: "we will", "let's", "in our case",
  "now". You and the reader are at the same keyboard.
- **Plain explanation before code, not theory sections.** One or two sentences
  of "why", then the command. Theory that doesn't change what the reader types
  gets cut or linked.
- **Concrete environments.** Name the OS, versions, tools: "Windows 11 +
  WSL2", "Node 22", "the AWS Console's Instances panel". Vague environments
  produce vague trust.
- **A light personal touch when it's true**: "I personally use...", "in my
  case this took about 4 minutes", "I got this wrong the first time". One or
  two per article. This is the strongest human signal there is — but only if
  it's real; never fabricate experience.
- **Practical caution.** Warn about credentials, deletion, costs, retain
  behavior, permissions, security groups — at the exact step where the mistake
  would happen, not in a disclaimers section.

The reader is smart but new to *this thing*. They want to make it work first
and understand the important parts second. Every article should answer, in
order: What are we trying to do? What do I need first? What do I type or click
next? How do I know it worked? How do I clean up or continue?

---

## Openings

Start close to the problem. The first two sentences name the reader's
situation or the exact thing being built — nothing else.

Good:

- "If you're using Git in WSL2, you've probably noticed you have to enter your
  username and password on every push."
- "In this post, we'll create a new CDK app that uses Python and deploy it to
  a real AWS account."
- "Our deploys started hanging for exactly 300 seconds. Here's why."

Bad (delete on sight):

- Any survey of the modern landscape ("In today's fast-paced world of cloud
  computing...").
- Abstract benefits before the reader knows what they're building
  ("Streamlining your workflow has never been more important...").
- A history lesson, unless the history is the kernel.
- Restating the title in different words and then previewing the sections
  ("In this article, we will explore..."). The reader read the title. Start.

---

## AI tells — the elimination list

Readers can't always articulate why prose feels machine-written, but they feel
it in the first paragraph. These are the tells. Treat every item as a bug: in
drafting, don't produce them; in auditing, flag each instance with a fix.

### Vocabulary tells

Never use (in prose — code identifiers are exempt):

- **delve, dive into, deep dive** (as verbs), *explore* as a section verb
- **leverage** (verb), **utilize** (say "use"), **harness** as a marketing
  verb ("harness the power of" — the noun "harness" in agent/test contexts is
  a load-bearing term and stays)
- **seamless(ly), robust, comprehensive, powerful, cutting-edge, game-changer,
  revolutionary, supercharge, unlock, elevate, streamline, empower, foster**
- **crucial, pivotal, vital** (usually "important", often nothing)
- **landscape, ecosystem, realm, journey** (as abstractions)
- Filler frames: **"It's important to note that"**, **"It's worth noting"**,
  **"That being said"**, **"Simply put"**, **"Essentially"** (as filler),
  **"In conclusion" / "In summary" / "Overall"**
- Connector chains: **Moreover / Furthermore / Additionally** starting
  consecutive paragraphs. Real writers connect with content, not adverbs.
- **"Whether you're a beginner or an expert..."**, **"Look no further"**,
  **"Buckle up"**, **"Let's get started!"** (the sentence, not the spirit)

### Structural tells

- **The mirrored intro/outro.** Intro previews the sections; conclusion
  summarizes them. Cut both. Open at the problem; end at verification, next
  steps, or the last insight — then stop. If a closing section is needed,
  make it "What's next" with concrete links, not a recap.
- **Rule-of-three everywhere.** "fast, scalable, and reliable" — triplets are
  fine occasionally; three triplets on one screen is a signature.
- **"It's not just X — it's Y."** The contrast-reveal scaffold. Once per
  career, maybe.
- **Uniform sections.** Every H2 the same length with the same shape reads
  generated. Real explanations are lumpy: hard parts get long, easy parts get
  two sentences.
- **Bullet-itis.** Bullets for everything, each opening with a **bolded
  phrase** followed by a colon. Use prose for reasoning, bullets for genuinely
  parallel items (prerequisites, options, checklists). If a bullet list has
  full sentences with subordinate clauses, it wanted to be a paragraph.
- **Colon-headline disease.** "X: Why Y Matters More Than You Think" on every
  heading. Prefer task headings (below).
- **Exhaustive symmetry.** Covering every option/edge case with equal weight.
  A human with experience has opinions: "there are three ways to do this; use
  the second one unless you're on Windows."
- **Em-dash density.** More than one or two per paragraph reads generated —
  vary with commas, parentheses, or a period.
- **Hedge stacks** ("might potentially, in some cases, depending on...") and
  the opposite, blanket certainty about things that vary by environment. State
  what you verified; mark what you didn't ("this worked on Node 22; earlier
  versions untested").

### Rhythm tells

- Every sentence 15–25 words, every paragraph 3–4 sentences. Break it up.
  Short sentence sometimes. Then a longer one that carries an actual chain of
  reasoning from cause to consequence without stopping to admire itself.
- Zero fragments, zero contractions, zero asides = starched. Use
  contractions. An occasional aside (like this one) is human.
- Perfect parallel grammar across every list and heading. Loosen where
  natural.

### The positive test

After removing the tells, the prose should pass this: **could only someone who
actually did this have written it?** Concrete numbers ("took 40 minutes",
"~$0.12/day"), the error message you actually hit, the step that surprised
you, the default you changed and why. If any paragraph could appear unchanged
in a thousand other blogs, it's not done.

---

## Headings and structure

- Short, task-oriented headings: "Create an S3 bucket", "Configure Git
  authentication", "Testing the Lambda function", "Cleanup".
- Question headings when the article is explanatory: "What is AWS CLI?",
  "Why create multiple stacks?" (these also serve AEO — see `seo-geo-aeo.md`).
- Before a long tutorial, show the visible workflow so the reader can see the
  whole path:

  ```markdown
  To create an EC2 instance from the console, we'll:

  1. Choose a region
  2. Launch the instance
  3. Choose the AMI and instance type
  4. Configure the security group
  5. Connect and verify
  ```

- For console/UI walkthroughs, lettered sub-steps read naturally:
  "a) Click **Instances** in the left panel  b) Click **Launch Instances**".

---

## Code and commands

Code is the center of a tutorial; prose exists to move the reader between
blocks.

- Fenced blocks with language tags, always.
- **One step, one block.** A sentence of intent before the block; result or
  verification after. The winning cadence:

  ````markdown
  Create a new directory for the CDK app and move into it:

  ```bash
  mkdir cdk-app && cd cdk-app
  ```

  Then initialize the app:

  ```bash
  cdk init app --language python
  ```
  ````

- Filename comments for multi-file examples (`# filename: cdk_app/stack.py`).
- Placeholders in angle brackets for user-specific values: `<bucket-name>`,
  `<your-profile>`. Never a fake-but-plausible literal the reader might paste.
- Explain the parameters that matter *after* the block; skip the ones that
  don't.
- **Verification is a step, not an afterthought**: "You should see...", the
  actual expected output shape, "If you get an error about X, it means Y."
- Cleanup commands for anything that costs money or persists (cloud
  resources, daemons, cron entries).

## Notes, warnings, images

- A note or warning must prevent a real mistake ("`cdk destroy` will NOT
  delete the S3 bucket — the default removal policy is Retain"). If it
  wouldn't change what the reader does, it's not a note.
- Images show actual UI state, command output, architecture, or verification
  results. No decorative images. (Diagrams and hero specs:
  `visual-assets.md`.)

---

## Accuracy rules (non-negotiable)

- **Never invent** command output, screenshots, benchmark numbers, account
  IDs, version numbers, or prices. If you don't have the real value, leave a
  clearly-marked placeholder for the writer: `[VERIFY: paste actual output]`.
- **Verify drift-prone facts** from primary documentation when the article
  depends on: current package/runtime versions, cloud console labels and
  defaults, quotas, managed policies, pricing or free-tier claims, or CLI
  install commands from external sources. Say what was verified and when.
- Security-sensitive configuration gets double-checked, not pattern-matched
  from memory.

---

## Phrases that carry the voice

Use these naturally — not in every paragraph:

- "Run the following command..." / "The above command will..."
- "You should see..." / "If you get an error..."
- "Now, we can..." / "Let's see how..."
- "In our case..." / "E.g. in my case..."

## Editing someone else's draft

Preserve tone, structure, and pacing; improve correctness. Fix spelling,
missing articles, duplicate words, overlong sentences, outdated command names.
Do **not** "improve" by making prose polished, formal, or detached — and never
swap load-bearing technical terms for smoother synonyms
(`methodology.md` § Load-bearing words).

If the project has its own local style guide (for example, a repo-level
writing skill like CloudBytes' `cloudbytes-article-writer`), read it first —
its frontmatter schemas, link conventions, and category shapes override the
generic guidance here. This file still governs the sentence-level craft.

---

## Voice review checklist

Before handing back any prose:

- [ ] The opening names the exact thing being built, fixed, or explained.
- [ ] Zero entries from the AI-tells lists (vocabulary, structural, rhythm).
- [ ] At least one detail only the actual author could know (real number,
      real error, real surprise) — or a `[VERIFY]` placeholder asking for one.
- [ ] Every command fenced, tagged, verifiable; cleanup present where needed.
- [ ] Warnings are practical and placed at the step where the mistake happens.
- [ ] No marketing register anywhere: no hype adjectives, no benefit-selling.
- [ ] Load-bearing terms untouched.
- [ ] Read a paragraph aloud — does it sound like a person explaining, or a
      system generating? If in doubt, shorten it.
