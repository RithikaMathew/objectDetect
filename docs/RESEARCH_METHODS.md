> **Implementation update:** TTA is now an optional pipeline flag; Grounding DINO is implemented as a separate sampled-frame proposal audit. Both are submitted by code/submit_research.py. Local code tests pass; no new GPU experiment result exists yet. Read the root README.md for submission. Temporal feature aggregation remains unimplemented.

# Additional detection methods — primary-source review, 2026-10-19

Scope: improve detection before wider application; no own-night training or 40-track labelling campaign is active. Search of the project README/code found no implemented multi-scale/flip test-time augmentation or Grounding DINO. Temporal detection was already discussed, so it is not presented as a newly discovered idea. None of the ideas below has a measured gain on these clips yet.

## First experiment: multi-scale and horizontal-flip inference (TTA)

Run the same frozen detector on resized and left/right-flipped views, map boxes back into the original frame, then merge duplicates before tracking. This is different from the existing tile-only approach. It could recover detections sensitive to scale or pose, but adds computation and may add false boxes. The [official YOLOv5 TTA guide](https://docs.ultralytics.com/yolov5/tutorials/test-time-augmentation/) documents this approach and a speed/accuracy trade-off for YOLOv5. That benchmark is NOT evidence of a gain for this RT-DETR model. RT-DETR integration needs explicit transforms and inverse box mapping; do not assume augment=True implements it. Keep the original image view in the union and test with/without the same fusion rules.

## Second experiment: an independent pretrained proposal detector

[Grounding DINO's official repository](https://github.com/IDEA-Research/GroundingDINO) provides code and pretrained models for text-prompted detection. Use prompts such as person / bicycle / motorcycle to inspect hard frames that RT-DETR missed. A bicycle box alone is not proof of a cyclist; preserve the current class semantics and verify rider association. First compare proposal recall and extra false regions offline, before any union into the counting pipeline. Our recommendation to try it is an inference from its different training/model, not a demonstrated advantage on night/fisheye traffic. This differs from the existing optional COCO-person ensemble; no new model was installed or substituted.

## Larger option already discussed: temporal feature aggregation

[Flow-Guided Feature Aggregation (ICCV 2017)](https://arxiv.org/abs/1703.10025) aligns and combines neighbouring-frame features for detection under degraded appearance. ByteTrack links detections AFTER they occur; temporal feature aggregation can improve the detector input/features themselves. It is not the existing optical-flow box coasting. Research code exists, but the old architecture is not a drop-in RT-DETR flag; porting and validation are substantial work. Consider only after cheaper frozen-model experiments.

## Clarification: BNE-DETR and background proposals

[Public BNE-DETR code exists](https://github.com/luy02735-lang/BNE-DETR). The old deck's no-ready-made-code claim is corrected. Available pretrained weights, supported classes and environment compatibility still need verification; no claim that it is ready to replace this pipeline. Background subtraction plus crop re-detection was already proposed in the README; it is not new research here, and basic MotionDiag already generated too many candidates.

## Evaluation that makes a useful conclusion

Use the existing four truth-labelled clips first, so no relabelling is required. Compare counted-and-correct people, entirely missed people, wrong class, rejected short tracks, extra counted tracks and runtime against b4_combo_static5. More boxes alone is not success. Freeze any selected settings, then score a NEW higher-resolution clip from any year; only that new clip needs its own human truth. Do not tune on the two known errors and then call improvement on those same examples independent validation.

Higher-resolution screening uses encoded width x height > 720x480, not year. Inspect lens distortion, compression and the pixel height of people as well: a larger frame does not guarantee more useful person detail, and upscaled footage does not create evidence.
