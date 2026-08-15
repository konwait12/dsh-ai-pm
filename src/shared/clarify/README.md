# Clarification And Issues

Create a QuestionRecord only when information is unknown, conflicting, or decision-dependent. Discoverable facts should be researched first. Questions are batched by decision owner and include preliminary judgment, evidence, options, impact, blocking flag, deferral risk and reflow target.

No empty issue record is required. Blocking questions set `needs_user_input`; non-blocking questions remain visible with an owner and deadline. Answers are written back to the affected artifact and trigger Audit again.
