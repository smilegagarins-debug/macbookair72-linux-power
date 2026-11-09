#!/usr/bin/env python3
# usage: pmeas.py LABEL [SECONDS]  - SMC power rails + battery + turbostat
import sys, time, subprocess, statistics, struct
sys.path.insert(0, '/usr/local/sbin'); import importlib.util
spec = importlib.util.spec_from_file_location('smc', '/usr/local/sbin/smc.py'); smc = importlib.util.module_from_spec(spec); sys.argv_save = sys.argv; sys.argv=['x']; spec.loader.exec_module(smc); sys.argv = sys.argv_save
L = sys.argv[1] if len(sys.argv)>1 else 'x'; N = int(sys.argv[2]) if len(sys.argv)>2 else 40
keys = ['PSTR','PDTR','PCPT','PCPG','PBLC','PAPC','PSDC','PM0C','PPBR','PO0R']
def sp78(b): return struct.unpack('>h', b)[0]/256
ts = subprocess.Popen(['turbostat','--quiet','--Summary','--show','Busy%,Pkg%pc2,Pkg%pc3,Pkg%pc6,Pkg%pc7,PkgWatt','--interval',str(N),'--num_iterations','1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
B='/sys/class/power_supply/BAT0/'
data = {k: [] for k in keys+['BAT']}
t0 = time.time()
while time.time()-t0 < N:
    for k in keys:
        try: data[k].append(sp78(smc.read(k, 2)))
        except Exception: pass
    c = int(open(B+'current_now').read()); v = int(open(B+'voltage_now').read())
    data['BAT'].append(c*v/1e12)
    time.sleep(0.5)
out = ts.communicate()[0].strip().splitlines()
st = open(B+'status').read().strip()
r = f"{L} [{st}] " + " ".join(f"{k}={statistics.mean(v):.2f}" for k,v in data.items() if v)
r += f" PSTRsd={statistics.pstdev(data['PSTR']):.2f}"
if len(out)>=2: r += " | " + " ".join(f"{h}={x}" for h,x in zip(out[-2].split(), out[-1].split()))
print(r); open('/var/log/pmeas.log','a').write(time.strftime('%F %T ')+r+'\n')
