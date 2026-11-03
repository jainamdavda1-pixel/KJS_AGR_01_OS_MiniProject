#!/usr/bin/env python3
"""Educational synthetic-data sugarcane irrigation advisory; not agronomic guidance."""
import argparse,csv,json,math,os,statistics,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'outputs'; LOG=ROOT/'logs'
FIELDS=['plot_id','soil_moisture_pct','temp_c','humidity_pct','rain_forecast_mm','crop_age_days','pump_lpm']

def validate(row):
    x={k:float(row[k]) for k in FIELDS if k!='plot_id'}
    if not row['plot_id'].strip(): raise ValueError('blank plot_id')
    bounds={'soil_moisture_pct':(0,100),'temp_c':(-10,60),'humidity_pct':(0,100),'rain_forecast_mm':(0,300),'crop_age_days':(1,600),'pump_lpm':(1,1000)}
    for k,(lo,hi) in bounds.items():
        if not math.isfinite(x[k]) or not lo<=x[k]<=hi: raise ValueError(f'{k} out of range: {x[k]}')
    return x

def load(path):
    with open(path,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        if not set(FIELDS).issubset(reader.fieldnames or []): raise ValueError('missing CSV columns')
        rows=list(reader)
    if not rows: raise ValueError('empty CSV')
    if len({r['plot_id'] for r in rows})!=len(rows): raise ValueError('duplicate plot_id')
    for r in rows:validate(r)
    return rows

def baseline(x):
    # Demonstration target, not a scientifically calibrated crop-water equation.
    deficiency=max(0,55-x['soil_moisture_pct'])
    heat=max(0,x['temp_c']-28)*0.40
    age=1.1 if 90<=x['crop_age_days']<=300 else 0.85
    return max(0,(deficiency*.58+heat+max(0,55-x['humidity_pct'])*.07)*age-x['rain_forecast_mm']*.72)

def features(x):
    return [1.,x['soil_moisture_pct']/100,x['temp_c']/50,x['humidity_pct']/100,x['rain_forecast_mm']/50,x['crop_age_days']/400]

def train():
    # Deterministic ridge linear regression on labelled synthetic examples.
    import random
    rng=random.Random(42)
    samples=[]
    for _ in range(650):
        x={'soil_moisture_pct':rng.uniform(15,75),'temp_c':rng.uniform(22,43),'humidity_pct':rng.uniform(25,90),'rain_forecast_mm':rng.uniform(0,30),'crop_age_days':rng.uniform(30,400),'pump_lpm':rng.uniform(100,400)}
        samples.append((features(x),baseline(x)))
    # Coordinate gradient descent on normalized features with stable small steps.
    weights=[0.0]*6
    for epoch in range(6000):
        grads=[0.0]*6
        for f,target in samples:
            error=sum(w*v for w,v in zip(weights,f))-target
            for j in range(6):grads[j]+=error*f[j]
        for j in range(6):weights[j]-=0.16*(grads[j]/len(samples)+(0.002*weights[j] if j else 0))
    mae=statistics.mean(abs(max(0,sum(w*v for w,v in zip(weights,f)))-target) for f,target in samples)
    OUT.mkdir(exist_ok=True)
    (OUT/'model.json').write_text(json.dumps({'weights':weights,'synthetic_training_mae_mm':round(mae,3),'note':'synthetic surrogate trained from rule-based labels; no field validation'},indent=2))
    return weights,mae

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['acquire','predict','report','all']);p.add_argument('--input',default=str(DATA/'sensor_readings.csv'));a=p.parse_args()
    OUT.mkdir(exist_ok=True);LOG.mkdir(exist_ok=True)
    t=time.perf_counter()
    if a.stage in ('acquire','all'):
        raw=load(a.input)
        with open(OUT/'validated.csv','w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(raw)
        print(f'[SENSOR] Read {len(raw)} plot records from {a.input}',flush=True)
        for row in raw:print(f"[SENSOR] Plot {row['plot_id']}: soil={row['soil_moisture_pct']}%, temperature={row['temp_c']} C, forecast rain={row['rain_forecast_mm']} mm",flush=True)
        print('[FILE] All values are within allowed ranges. Saved clean readings to outputs/validated.csv',flush=True)
    if a.stage in ('predict','all'):
        rows=load(OUT/'validated.csv')
        print('[MODEL] Training a small linear regression on 650 synthetic examples labelled by a rule-based baseline...',flush=True)
        weights,mae=train()
        print(f'[MODEL] Training complete. Synthetic in-sample MAE = {mae:.3f} mm (not real-world accuracy).',flush=True)
        results=[]
        for row in rows:
            x=validate(row)
            required=max(0,sum(w*v for w,v in zip(weights,features(x))))
            # 100 m^2 teaching plot and pump conversion; illustrative assumption.
            liters=required*100
            minutes=liters/x['pump_lpm']
            if x['rain_forecast_mm']>=15: advice='DEFER: significant rain forecast'
            elif required>=12:advice='IRRIGATE: high estimated requirement'
            elif required>=4:advice='MONITOR: moderate estimated requirement'
            else:advice='NO IRRIGATION: low estimated requirement'
            results.append({'plot_id':row['plot_id'],'predicted_deficit_mm':round(required,2),'estimated_liters':round(liters,1),'pump_minutes':round(minutes,1),'advisory':advice})
        with open(OUT/'predictions.csv','w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=results[0]);writer.writeheader();writer.writerows(results)
        print(f'[MODEL] Estimated irrigation needs for {len(results)} plots:',flush=True)
        for r in results:print(f"[ADVISORY] {r['plot_id']}: {r['predicted_deficit_mm']} mm estimated deficit, {r['pump_minutes']} pump minutes -> {r['advisory']}",flush=True)
        print('[FILE] Predictions saved to outputs/predictions.csv',flush=True)
    if a.stage in ('report','all'):
        with open(OUT/'predictions.csv',newline='') as f:items=list(csv.DictReader(f))
        with open(OUT/'advisory.txt','w') as f:
            f.write('SUGARCANE IRRIGATION ADVISORY — EDUCATIONAL SYNTHETIC DEMO\n')
            f.write('Not verified for real farm decisions; agronomist review required.\n\n')
            for r in items:f.write(f"{r['plot_id']}: {r['advisory']} | deficit {r['predicted_deficit_mm']} mm | pump {r['pump_minutes']} min\n")
        print('[FILE] Farmer-facing summary written to outputs/advisory.txt',flush=True)
        print(f'[ADVISORY] Report includes {len(items)} plot recommendations; expert review required.',flush=True)
    print(f'[TIME] {a.stage.capitalize()} task took {1000*(time.perf_counter()-t):.2f} ms',flush=True)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:
        print('ERROR:',e,file=__import__('sys').stderr);raise SystemExit(2)
