#!/usr/bin/env python3
"""Explain resource safety for acquisition, prediction, and report tasks."""
TASKS=['Sensor acquisition','Water-needs prediction','Advisory report']
RESOURCES=['Sensor interface','Database lock','Pump controller']

def check(available, maximum, allocated, verbose=False):
    n=len(maximum);m=len(available)
    need=[[maximum[i][j]-allocated[i][j] for j in range(m)] for i in range(n)]
    if any(v<0 for row in need for v in row):raise ValueError('allocation exceeds maximum')
    work=available[:];finished=[False]*n;sequence=[]
    if verbose:
        print(f'  Available free resources: {dict(zip(RESOURCES,work))}')
        for i in range(n):
            print(f'  {TASKS[i]} currently holds {allocated[i]}; still needs {need[i]} to finish.')
    while True:
        selected=next((i for i in range(n) if not finished[i] and all(need[i][j]<=work[j] for j in range(m))),None)
        if selected is None:break
        if verbose:
            print(f'  [ALLOW] {TASKS[selected]} can receive its remaining resources and finish.')
        work=[work[j]+allocated[selected][j] for j in range(m)]
        finished[selected]=True;sequence.append(TASKS[selected])
        if verbose:print(f'  [RELEASE] It returns held resources. Now available: {work}')
    return all(finished),sequence,need

def main():
    scenarios={
      'Normal system load':([1,1,1],[[1,1,0],[0,1,1],[0,1,0]],[[1,0,0],[0,1,0],[0,0,0]]),
      'All available resources exhausted':([0,0,0],[[1,1,0],[0,1,1],[0,1,0]],[[1,0,0],[0,1,0],[0,0,0]])
    }
    print('[RESOURCE MANAGER] Three tasks share the sensor interface, database lock and pump controller.')
    print('[RESOURCE MANAGER] Checking if all tasks could finish without getting stuck.\n')
    for name,(avail,mx,alloc) in scenarios.items():
        print(f'--- Scenario: {name} ---')
        safe,seq,_=check(avail,mx,alloc,verbose=True)
        if safe:
            print('  [SAFE] All tasks can complete. One possible completion order:')
            print('  ' + ' -> '.join(seq))
        else:
            blocked=[t for t in TASKS if t not in seq]
            print('  [BLOCK] No currently runnable task can obtain the resources it still needs.')
            print('  Tasks unable to finish: ' + ', '.join(blocked))
            print('  [ACTION] Do not approve this allocation as safe; wait or release resources.')
            print('  [NOTE] This demonstrates an unsafe state, not proof of an actual deadlock.')
        print()
    assert check(*scenarios['Normal system load'])[0]
    assert not check(*scenarios['All available resources exhausted'])[0]
    print('[CHECK PASSED] Safe and unsafe resource scenarios were identified correctly.')
if __name__=='__main__':main()
