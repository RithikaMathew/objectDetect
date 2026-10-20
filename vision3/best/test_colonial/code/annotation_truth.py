"""Ground-truth display helpers. Never transfer Colonial labels to other sites."""
import datetime as dt
from pathlib import Path
import re


def colonial_truth_bins(video, session_start, bin_minutes, truth_dir):
    from eval_truth import CLIPS, read_truth
    if bin_minutes != 15 or not re.fullmatch(r'Standard_SCU8OG_2019-07-10_0000\.\d{3}\.mp4', Path(video).name):
        return {}
    session = dt.datetime.strptime(session_start, '%Y-%m-%d %H:%M:%S')
    if session != dt.datetime(2019, 7, 10):
        return {}
    result = {}
    for cc in CLIPS.values():
        path = Path(truth_dir) / Path(cc['truth']).name
        if not path.is_file(): continue
        people, skipped = read_truth(path)
        if skipped or not people:
            raise ValueError(f'Incomplete annotation truth: {path}: {skipped}')
        when = dt.datetime.strptime(cc['start'], '%Y-%m-%d %H:%M:%S')
        b = int((when-session).total_seconds() // (bin_minutes*60))
        result[b] = dict(bic=sum(p['c']=='cyclist' for p in people),
                         ped=sum(p['c']=='pedestrian' for p in people), source='hand-labelled')
    return result


def truth_text(truth):
    if truth is None: return 'GT: not labelled'
    bic = truth.get('bic', truth.get('bic_bl', 0)+truth.get('bic_sw', 0))
    return f'GT: Cyclists {bic} | Pedestrians {truth["ped"]}'
