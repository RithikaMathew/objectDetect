"""Compare exploratory distance/PET screens and audited false-flag fractions.

Threshold rules are engineering sensitivity screens, never trained predictors.
Adjudication refers to a physical pair within one clip/detector namespace and is
shared across its smoothing variants. Variants are never pooled as unique events.
"""
import csv
import math
from collections import defaultdict
from pathlib import Path


def number(value):
    if value in ('',None):return None
    value=float(value)
    return value if math.isfinite(value) else None


def write(path,rows,fields):
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def screening_reports(directory,rows):
    directory=Path(directory)
    metrics=('min_footprint_distance_m','min_sampled_clearance_m','min_collision_ttc_s','sampled_occupancy_pet_s')
    keys=lambda r:(r['task'],r['cyclist_id'],r['vehicle_id'])
    baseline={(keys(r),r['scenario']):r for r in rows if r['scenario'] in ('baseline','strict_False')}
    comparison=[]
    for row in rows:
        if row.get('motion') not in ('kalman','rts'):continue
        support='strict_False' if row['scenario'].endswith('_transfer') else 'baseline'
        ref=baseline.get((keys(row),support))
        for metric in metrics:
            value=number(row.get(metric));base=number(ref.get(metric)) if ref else None
            comparison.append(dict(task=row['task'],cyclist_id=row['cyclist_id'],vehicle_id=row['vehicle_id'],
                scenario=row['scenario'],baseline_scenario=support,metric=metric,value=value,
                baseline_value=base,difference=None if base is None or value is None else value-base,
                comparison_status='matched_available_metrics' if base is not None and value is not None else 'missing_baseline_or_metric'))
    write(directory/'smoothing_comparison.csv',comparison,
          ['task','cyclist_id','vehicle_id','scenario','baseline_scenario','metric','value','baseline_value','difference','comparison_status'])
    annotations=defaultdict(set)
    file=directory/'review_labels.csv'
    if file.exists():
        with file.open(newline='') as f:
            for r in csv.DictReader(f):
                label=(r.get('near_miss_review') or '').strip().lower()
                if label in ('yes','no') and (r.get('reviewer') or '').strip():
                    annotations[(r.get('task'),r.get('cyclist_id'),r.get('vehicle_id'))].add(label)
    groups=defaultdict(list)
    for r in rows:groups[(r['detector'],r['scenario'])].append(r)
    summaries=[];audit=[]
    for (detector,scenario),rr in groups.items():
        for rule in ('distance','pet','distance_AND_pet','distance_OR_pet','lateral_clearance'):
            flags=[]
            for r in rr:
                distance=number(r.get('min_footprint_distance_m'));pet=number(r.get('sampled_occupancy_pet_s'))
                clearance=number(r.get('min_sampled_clearance_m'))
                if rule=='distance':valid=distance is not None;flag=valid and distance<1.
                elif rule=='pet':valid=pet is not None;flag=valid and pet<1.
                elif rule=='distance_AND_pet':valid=distance is not None and pet is not None;flag=valid and distance<1. and pet<1.
                elif rule=='distance_OR_pet':valid=distance is not None or pet is not None;flag=(distance is not None and distance<1.) or (pet is not None and pet<1.)
                else:valid=clearance is not None;flag=valid and clearance<1.
                votes=annotations.get(keys(r),set())
                review=next(iter(votes)) if len(votes)==1 else 'conflicting' if votes else 'unreviewed'
                flags.append((valid,flag,review))
            eligible=sum(v for v,_,_ in flags);flagged=sum(f for _,f,_ in flags)
            judged=sum(f and label in ('yes','no') for _,f,label in flags)
            false=sum(f and label=='no' for _,f,label in flags)
            true=sum(f and label=='yes' for _,f,label in flags)
            summaries.append(dict(detector=detector,scenario=scenario,screen=rule,distance_threshold_m=1.,pet_threshold_s=1.,
                candidate_pairs=len(rr),eligible_pairs=eligible,flagged_pairs=flagged,
                interpretation='exploratory_screen_not_verified_near_miss_classifier'))
            audit.append(dict(detector=detector,scenario=scenario,screen=rule,flagged_pairs=flagged,
                adjudicated_flags=judged,reviewed_false_flags=false,reviewed_true_flags=true,
                unadjudicated_flags=flagged-judged,adjudication_coverage=judged/flagged if flagged else None,
                false_fraction_among_adjudicated_flags=false/judged if judged else None,
                status='reviewed_subset_only_not_population_FPR' if judged else 'awaiting_adjudication'))
    write(directory/'screening_comparison.csv',summaries,
          ['detector','scenario','screen','distance_threshold_m','pet_threshold_s','candidate_pairs','eligible_pairs','flagged_pairs','interpretation'])
    write(directory/'false_alarm_review.csv',audit,
          ['detector','scenario','screen','flagged_pairs','adjudicated_flags','reviewed_false_flags','reviewed_true_flags','unadjudicated_flags','adjudication_coverage','false_fraction_among_adjudicated_flags','status'])
