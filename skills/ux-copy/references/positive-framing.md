# Positive framing

Negation slows comprehension. The brain processes a negative as two operations: build the picture (*you can edit this*), then erase it (*not*). Positive framing skips the second step.

This document is the working catalogue: when to flip, how to flip, and the small set of cases where negation is the right move.

## Why this matters

- **Speed.** Positive sentences read faster. On a button or a tooltip, milliseconds matter.
- **Trust.** Negation foregrounds the problem. *Don't lose your work* primes loss before the user has done anything wrong.
- **Action.** Verbs in the positive form push the user forward. *Save your work* is a complete instruction.
- **Tone.** Positive framing reads as confident. Negation often reads as defensive or apologetic.

## The replacement patterns

Six patterns cover most cases.

### Pattern 1: Condition to opportunity

When the copy gates an action on a missing prerequisite.

| Negative form                       | Positive form                                  |
| ----------------------------------- | ---------------------------------------------- |
| Don't have an account?              | New here? Create an account.                   |
| You haven't connected a card yet.   | Add a card to start your trial.                |
| You haven't completed onboarding.   | Three steps left to finish setup.              |

### Pattern 2: State to next step

When the copy reports a system condition.

| Negative form                       | Positive form                                  |
| ----------------------------------- | ---------------------------------------------- |
| Can't connect right now.            | Connection lost. Retry in a few seconds.       |
| The file isn't ready yet.           | The file is processing. Done in about a minute.|
| We couldn't find that.              | Nothing matches that search. Try a broader term.|

### Pattern 3: Rule to fact

When the copy states a limitation or policy.

| Negative form                       | Positive form                                  |
| ----------------------------------- | ---------------------------------------------- |
| You can't edit after submitting.    | Submissions are final.                         |
| Don't use the same password twice.  | Use a unique password.                         |
| This is not reversible.             | This is permanent.                             |
| Not available on the free plan.     | Available on Team and above.                   |

### Pattern 4: Warning to instruction

When the copy is steering the user away from a mistake.

| Negative form                       | Positive form                                  |
| ----------------------------------- | ---------------------------------------------- |
| Don't lose your changes.            | Save your changes.                             |
| Don't share this code.              | Keep this code private.                        |
| Don't close this window.            | Stay on this page while we finish.             |

### Pattern 5: Validation as advice

When the copy is responding to an invalid form value. Validation reads as help, not punishment.

| Negative form                       | Positive form                                  |
| ----------------------------------- | ---------------------------------------------- |
| Password isn't strong enough.       | Add a number or a symbol to finish.            |
| That's not a valid email.           | Use the format name@domain.com.                |
| You can't use this username.        | That username is taken. Try one of these: [...]|

### Pattern 6: Scope as inclusion

When the copy is describing what is included, not what is missing.

| Negative form                              | Positive form                                  |
| ------------------------------------------ | ---------------------------------------------- |
| Not available in your region.              | Available in 14 countries. More on the way.    |
| We don't support Internet Explorer.        | Works in Chrome, Safari, Firefox, and Edge.    |
| You won't be charged until your trial ends.| Your card is charged on day 15. Cancel anytime.|

## When negation is the right move

Negation has a place. Keep it for the cases below.

### 1. Irreversible destructive actions

The negation *cannot be undone* is the standard for a reason. It carries the right weight. Keep it on dialogs that wipe data, cancel subscriptions, or delete accounts.

- *Delete this workspace? This cannot be undone.*
- *Cancel your subscription? You lose access at the end of the billing period.*

### 2. Legal and compliance copy

Terms, refunds, and obligations sometimes need the precision negation gives. Plain English still applies.

- *We do not sell your data to third parties.*
- *Refunds are not issued after 30 days.*

### 3. Safety and accessibility hints

When the negation prevents harm or misuse.

- *Do not turn off your device while updating.*
- *Do not enter your password on a shared computer.*

### 4. Empathetic acknowledgement

Sometimes a negation makes the copy more human, not less. Use sparingly, and only when the alternative reads as cold.

- *You haven't done anything wrong. The card issuer flagged the charge.*
- *No rush. Save your draft and come back later.*

## The flip technique

When a negation appears in copy, ask three questions in order.

1. **What is the positive fact?** If you can state the same idea as a fact about the world (*Submissions are final*), use that.
2. **What is the next step?** If the user is at a fork (*Don't have an account?*), state the opportunity (*New here? Create an account.*).
3. **What is the rule, plainly?** If neither of the above fits, state the rule with a positive verb (*Use a unique password*) instead of a prohibition (*Don't reuse passwords*).

If none of the three rewrites read better, the original negation probably belongs. Keep it.

## Common landmines

A few flips backfire. Watch for these.

- **Empty optimism.** *Available in 14 countries* is a better line than *not available in your region* only if 14 countries is the truth. Skip the flip if the positive form misleads.
- **Buried *no*.** *Submissions are final* says no without saying no. Make sure the user can still tell that they cannot edit. Pair with a hint when the consequence is non-obvious: *Submissions are final. Double-check before you send.*
- **Over-cheerful tone.** A flipped sentence should be neutral, not perky. *No invoices in May* is the right tone for a calm month. *No invoices yet, but soon!* reads as needy.

## A short before-and-after gallery

The examples below are taken from common UI moments. Each pair carries the same information; the positive form lands faster and reads cleaner.

| Surface                  | Before                                          | After                                              |
| ------------------------ | ----------------------------------------------- | -------------------------------------------------- |
| Login (no account)       | Don't have an account? Sign up.                 | New here? Create an account.                       |
| Connection error         | We can't connect right now.                     | Connection lost. Retry in a few seconds.           |
| Read-only state          | You can't edit this anymore.                    | This is locked. Duplicate to make changes.         |
| Plan gate                | This feature is not available on the free plan. | Available on Team and above.                       |
| Password validation      | Password isn't strong enough.                   | Add a number or a symbol to finish.                |
| Search empty state       | We couldn't find anything for "X".              | Nothing matches "X". Try a broader term.           |
| File too large           | This file isn't supported.                      | Files up to 10 MB. This one is 24 MB.              |
| Permission denied        | You don't have access.                          | This view is for owners and admins. Ask one to invite you.|
| Save reminder            | Don't forget to save.                           | Save your changes.                                 |
| Trial end                | Your trial isn't over yet.                      | 8 days left in your trial.                         |
