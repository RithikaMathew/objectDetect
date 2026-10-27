The numbers in this file are identical to the earlier version, so my reading of the table doesn’t change. The one difference is in the timestamp audit, and it corrects something I said.

Correction on timing

The earlier version stated that all 18 clips had regular timestamps at about 29.97 fps. I told you that ruled timing out for those clips.
This version only says the 18 clips were audited. It no longer states the result, and it warns that problems introduced earlier in extraction can’t be excluded.
So I can’t say timing is ruled out. I should have been more careful before.

What to do

Open timestamp_audit.json and check the actual frame-interval statistics per clip. You want regular intervals around 1/29.97 s, with no gaps, duplicates or jumps.
Check how the review clips were cut from the hourly videos: re-encoding, frame dropping, or a changed frame rate. If timing was altered there, it would scale every speed at that camera.
A timing error is a plausible partial explanation for site-wide gaps like University (ratio about 1.8). It could never explain all of it unless the error were nearly 2x, though, which a half-speed or double-speed mix-up could produce. Your README says no extra half-speed factor is applied, so confirm that for the University clips specifically.

Everything else from my last assessment stands. The University distance test is still the best next step, and the estimator choice still matters little compared with calibration. If you paste the audit summary or the University clip’s timestamps, I can help read them.

timestamp_audit.json
182 lines
JSON

The timestamp audit supports regular timing on all 18 review clips, so timing is unlikely to explain the University gap. It does not cover everything.

What the audit shows

Regular steps: every clip has a median packet step of 0.033367 s (1/29.97), with 0% irregular steps and no duplicate timestamps.
No drift: the index-vs-average-fps difference is about 3×10⁻⁷ s, so there is no drift across a clip.
Clip length: most clips have 26,973 packets, which is 900 s at 29.97 fps. That matches 15 minutes of real time, so the clips look neither sped up nor slowed down.
University: it has 26,927 packets, about 1.5 s short of the others. That looks like a trimmed end. Just confirm the annotated times fall inside it.

What this rules out and what it doesn’t

It rules out irregular frame timing and a half-speed or double-speed mix-up in the review clips. A clip with the wrong rate would show a different duration or step, and none does. A site-wide error of about 1.8× from clip timing is therefore very unlikely.
It does not cover the original hourly recordings. If a camera’s own timestamps were wrong before the clips were cut, this audit wouldn’t catch it. The matching clip lengths are indirect evidence against that, not proof.
Click timing is also fine for speed. Your clicks use media time, and only the differences between click times matter, so any start offset cancels. A one-frame click error is about 0.033 s, or roughly 1-2% on a 2-3 s track.

Where that leaves the gaps

Aloma, Lee and University now point to calibration scale or different cyclist samples, not timing or the estimator.
The University distance test is still the one check that can separate those: what distance does the calibration imply between the two points tied to the roughly 55.17 ft measurement? Confirm that point correspondence first, and I can help set up the comparison.