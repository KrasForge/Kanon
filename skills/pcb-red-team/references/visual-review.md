# Visual PCB review rubric

Record the input snapshot/manifest hash and the exact top, bottom and isometric artifact
names. Establish whether the bottom image is mirrored, the viewing direction, units and
board origin. Identify pin 1 and connector mating direction from manufacturer drawings;
a pleasing render is not evidence of orientation or electrical correctness.

For each image, actively seek reversed connectors, ambiguous pin-1/polarity markings,
connector bodies facing into the board, overlaps, inaccessible fasteners/test points,
component heights conflicting with the enclosure, silkscreen hidden by assembly, and
labels readable from the intended service direction. Compare the 3D model origin and
orientation with native pads and manufacturer dimensions; models can be wrong or absent.

Inspect conspicuous routing anomalies and functional placement: distant local capacitors,
large switching/feedback loops, clocks near sensitive inputs, references routed through
noisy regions, plane splits under critical signals and connectors without a credible
protection path. These observations nominate checks; a visible ground pour does not prove
a return path, and an invisible internal plane cannot be assessed from a top render.

Inspect actual Gerber renders separately from native PCB images. Confirm expected copper,
mask, silk, board outline and drill outputs; compare polarity and orientation across views.
Do not infer plated status, hole tolerances or layer mapping from color alone. Parser
warnings or missing models/layers are limitations, not clean reviews.

Write structured blocker/major/minor/observation findings with evidence, affected objects,
explanation and remediation. State what could not be seen. Verify suspected faults in
native connectivity/geometry, ERC/DRC, electrical calculations, BOM and mechanical models.
Never approve release solely because images look plausible or all available views were generated.
