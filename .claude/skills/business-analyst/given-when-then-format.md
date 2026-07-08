# Skill: GIVEN-WHEN-THEN Formatting

Load this skill whenever writing or reviewing acceptance criteria.

## Structure

- **GIVEN** — the initial context/state before the action (preconditions).
- **WHEN** — the single action or event being tested.
- **THEN** — the observable, verifiable outcome.

One scenario should test one behavior. Do not chain multiple unrelated
WHEN/THEN pairs into a single scenario.

## Good example

```
GIVEN a logged-in user with an empty shopping cart
WHEN they add a product that is in stock
THEN the cart shows 1 item and the total price updates accordingly
```

## Bad example (too vague, not testable)

```
GIVEN the user is on the site
WHEN they use the cart
THEN it works correctly
```

## Coverage checklist per user story

- Happy path (at least one scenario).
- At least one edge case (boundary values, empty states, max limits).
- At least one negative/error case (invalid input, unauthorized access,
  unavailable dependency).
- Idempotency/repetition case, if relevant (what happens if the same action
  is performed twice).
