"""Small, source-backed project guide. No external model calls or invented metrics."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCES={
 'app':('CycleScope workflow','cyclescope/README.md'),
 'archive':('Archive inventory and recording years','docs/MIOVISION_ARCHIVE_INVENTORY_README.md'),
 'speed':('Existing speed workflows','docs/SPEED_WORKFLOWS.md'),
 'weights':('HiPerGator weights and local setup','cyclescope/HIPERGATOR_NEXT_STEPS.md'),
 'references':('Reference-camera mapping','vision3/best/test_colonial/code/speed_site_screen.py'),
 'handoff':('What is needed from HiPerGator','cyclescope/HIPERGATOR_NEXT_STEPS.md'),
}
TOPICS=[
 (('landmark','ground x','ground y','calibrat','region','scale'), 'Ground X/Y are measured distances in metres from an origin you choose. Image clicks provide pixels, not metre distances. The first point may be (0,0); other points need real measurements. Regions label road areas and can be saved without metric calibration.', ['app','speed']),
 (('speed','mph','edit','save','n/a','not measured'), 'Speeds belong to individual objects. Select an object, enter its speed and click Save reviewed speed. Switching to another object shows that object’s own speed; returning to the first should retain its saved value. Not measured means there is no eligible calibrated trajectory or reviewed override. Overrides remain separate from computed motion and do not alter interaction metrics.', ['app','speed']),
 (('hipergator','weights','chunk','failed','processing','port'), 'Uploads use an explicit chunk index because their server filename is not the original archive name. Retry a failed unedited job after updating the app. RT-DETR weights and the X-CLIP cache are now available locally in this checkout. Long or batch inference can run faster on a HiPerGator GPU; source files and camera-specific calibration must be copied separately when absent.', ['weights','handoff']),
 (('reference','alias','location','street','bl ','nbl','sw '), 'The workbook has 14 speed-reference locations; nine have the saved same-video comparison. These are different evidence scopes. Original archive folder and device names are retained. Workbook-to-camera links use candidate aliases, not verified person-level matches. Silver Star has workbook references but no mapped recording, so its year and hours stay unknown.', ['archive','references']),
 (('interaction','ttc','pet','near miss','clearance'), 'Interactions are road-user pairs eligible for review, not automatic confirmed near misses. TTC predicts collision under current motion. PET describes the estimated time gap in a shared area. Clearance uses assumed footprints. Calibration and adequate observed trajectories are required; the existing road-axis routine needs at least two moving vehicle tracks. Confirm or reject a candidate after inspecting the footage.', ['app']),
 (('year','hours','count','data','factual','invent','source'), 'The saved archive audit reports 9,085 videos, 179 archive groups and 9,057.34 summed playback hours across 2019–2026. The 2019 study count table sums to 5,053 bicycles. Values are checked against saved source files; this is not independent validation of the original measurements. Missing values remain unavailable. A separate reference-only row does not add videos or playback hours.', ['archive','app']),
 (('time','clip','range','minute','batch'), 'Select local videos, choose First 10 minutes, Last 15 minutes or adjust the start/end sliders. These use elapsed playback time. The optional real camera clock only enables day/night rules after you confirm it. Two jobs process concurrently by default; additional jobs wait in the local queue.', ['app']),
]

def answer(question,job=None):
    text=question.strip().lower()
    for words,response,sources in TOPICS:
        if any(word in text for word in words):
            if job and any(w in text for w in ('speed','mph','n/a','not measured')):
                overrides=job.get('speed_overrides',{})
                response+=f" This video has {len(overrides)} saved reviewed speed override(s)."
            return dict(answer=response,sources=[dict(id=k,title=SOURCES[k][0],url=f'/api/help/sources/{k}')for k in sources],mode='project_guide')
    return dict(answer='I do not have a source-backed answer to that question. Ask about calibration, object speeds, interactions, archive coverage, clip selection or HiPerGator setup. I will not fill in missing study results.',sources=[],mode='project_guide')
