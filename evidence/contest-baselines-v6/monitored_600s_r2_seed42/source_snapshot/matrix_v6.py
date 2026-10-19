"""Monitor independent runs, stop complete process trees, and seal validated results.

No previous experiment solution is read. Only complete solution/metadata pairs
written by the current worker are eligible for post-search validation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time


PROJECT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
V4 = PROJECT / 'evidence/contest-baselines-v4'
V6 = PROJECT / 'evidence/contest-baselines-v6'
LABEL = re.compile(r'^(Q2|Q3)_(time|energy)_(greedy|aco|alns|cp_sat)$')


class WindowsJob:
    """Own the launcher and descendants, including a Windows venv's real Python.

    The launcher is created suspended, attached, then resumed. This prevents a
    fast launcher from creating an untracked child before job assignment.
    """
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.lock = threading.Lock()
        class Basic(ctypes.Structure):
            _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong),
                ('PerJobUserTimeLimit', ctypes.c_longlong), ('LimitFlags', wintypes.DWORD),
                ('MinimumWorkingSetSize', ctypes.c_size_t), ('MaximumWorkingSetSize', ctypes.c_size_t),
                ('ActiveProcessLimit', wintypes.DWORD), ('Affinity', ctypes.c_size_t),
                ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(n, ctypes.c_ulonglong) for n in
                ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
        class Extended(ctypes.Structure):
            _fields_ = [('BasicLimitInformation', Basic), ('IoInfo', IO),
                ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.SetInformationJobObject.restype = wintypes.BOOL
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        self.kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.TerminateJobObject.restype = wintypes.BOOL
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel.CloseHandle.restype = wintypes.BOOL
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        info = Extended()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def attach_and_resume(self, proc):
        ctypes = self.ctypes
        if not self.kernel.AssignProcessToJobObject(self.handle, int(proc._handle)):
            raise ctypes.WinError(ctypes.get_last_error())
        ntdll = ctypes.WinDLL('ntdll')
        ntdll.NtResumeProcess.argtypes = [ctypes.c_void_p]
        ntdll.NtResumeProcess.restype = ctypes.c_long
        result = ntdll.NtResumeProcess(int(proc._handle))
        if result < 0:
            raise OSError(f'NtResumeProcess returned NTSTATUS {result:#x}')

    def terminate(self):
        with self.lock:
            if not self.handle:
                return False
            if not self.kernel.TerminateJobObject(self.handle, 137):
                raise self.ctypes.WinError(self.ctypes.get_last_error())
            return True

    def close(self):
        with self.lock:
            if self.handle:
                self.kernel.CloseHandle(self.handle)
                self.handle = None


def utc():
    return datetime.now(timezone.utc).isoformat()


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.{os.getpid()}.{threading.get_ident()}.{time.perf_counter_ns()}.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                        allow_nan=False), encoding='utf-8')
        # Windows readers can briefly hold the destination without share-delete.
        # Retry only that transient error; retain the original failure otherwise.
        for attempt in range(100):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if attempt == 99:
                    raise
                time.sleep(.005)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except PermissionError:
            pass


def read(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return default


def worker_progress(state):
    """A transient Windows read lock must never erase observed search success."""
    value = read(state['directory'] / 'search_progress.json')
    if isinstance(value, dict) and value:
        state['last_good_progress'] = value
    progress = state.get('last_good_progress', {})
    state['has_incumbent_seen'] = (state.get('has_incumbent_seen', False)
                                   or bool(progress.get('has_incumbent')))
    return progress


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def targets(seconds):
    return sorted(set(t for t in (30., 60., 180., float(seconds)) if t <= seconds))


def freeze(base):
    snapshot = base / 'source_snapshot'
    snapshot.mkdir()
    sources = {}
    # The entire small local Python module directory covers transitive legacy
    # imports as well as the active worker, constructor, joint solver and runner.
    for path in sorted(SCRIPTS.glob('*.py')):
        shutil.copy2(path, snapshot / path.name)
        sources[path.relative_to(PROJECT).as_posix()] = digest(path)
    paths = [V4 / n for n in ('pool_q2.json', 'pool_q3.json', 'sites.json', 'atoms.json')]
    inputs = PROJECT / 'evidence/contest-baselines-v1/inputs'
    paths += [inputs / n for n in ('normalized_inputs.json', 'terrain_evidence_all.json')]
    # Raw physical inputs are hashes only; nothing outside this project is read.
    raw = PROJECT / 'references/modeling/data'
    paths += sorted((raw / 'terrain').glob('*.mat'))
    paths += [raw / 'tables' / n for n in ('通信链路参数.xlsx', '中继无人机数据.xlsx')]
    physical = {p.relative_to(PROJECT).as_posix(): digest(p) for p in paths}
    return sources, physical


def seal(state, seconds):
    """Run outside the monitor thread, so expensive Q3 QA cannot delay stops."""
    from benchmark_v2 import validate_solution, solution_metrics

    directory = state['directory']
    label = state['label']
    q, objective, method = LABEL.fullmatch(label).groups()
    progress = worker_progress(state)
    clock = read(directory / 'clock.json', {})
    finished = read(directory / 'worker_finished.json', {})
    worker_error = read(directory / 'worker_error.json')
    pairs, pair_errors = [], []
    solutions = list(directory.glob('checkpoint_*s_solution.json'))
    if (directory / 'best_solution.json').exists():
        solutions.append(directory / 'best_solution.json')
    for solution in solutions:
        meta_path = solution.with_name(solution.name.replace('_solution.json', '_meta.json'))
        meta = read(meta_path)
        if not meta:
            pair_errors.append(dict(path=solution.name, reason='missing_complete_metadata'))
            continue
        actual_hash = digest(solution)
        found = meta.get('best_found_s', meta.get('found_s'))
        if actual_hash != meta.get('solution_sha256'):
            pair_errors.append(dict(path=solution.name, reason='metadata_hash_mismatch'))
            continue
        if not isinstance(found, (int, float)) or not 0 <= found <= seconds + 1e-6:
            pair_errors.append(dict(path=solution.name, reason='found_outside_budget', found_s=found))
            continue
        value = read(solution)
        try:
            metrics = solution_metrics(value)
        except Exception as exc:
            pair_errors.append(dict(path=solution.name, reason='unreadable_solution', error=repr(exc)))
            continue
        pairs.append(dict(path=solution, found_s=found, sha256=actual_hash, metrics=metrics))
    def score(pair):
        m = pair['metrics']
        return (m['completion_s'], m['energy_kwh']) if objective == 'time' else (m['energy_kwh'], m['completion_s'])
    sealed = directory / 'sealed'
    sealed.mkdir(exist_ok=True)
    checkpoints, checked, validation_errors = [], {}, []
    cap = {'Q2': 6000., 'Q3': 5939.9}[q] if objective == 'energy' else None
    for t in targets(seconds):
        eligible = [p for p in pairs if p['found_s'] <= t + 1e-6]
        if not eligible:
            checkpoints.append(dict(checkpoint_s=t, status='NO_FEASIBLE_SOLUTION_FOUND',
                                    metrics=None, best_found_s=None, solution_sha256=None))
            continue
        candidate = min(eligible, key=score)
        path = sealed / f'checkpoint_{t:g}s_solution.json'
        shutil.copyfile(candidate['path'], path)
        output = sealed / f'checkpoint_{t:g}s_validation.json'
        try:
            sha = digest(path)
            if sha in checked:
                metrics, audit = checked[sha]
                atomic(output, audit)
            else:
                metrics, audit = validate_solution(q, path, output)
                if cap is not None and metrics['completion_s'] > cap + 1e-6:
                    raise AssertionError(f'Completion {metrics["completion_s"]} exceeds cap {cap}')
                checked[sha] = (metrics, audit)
            checkpoints.append(dict(checkpoint_s=t, status='VALIDATED_FEASIBLE',
                metrics=metrics, best_found_s=candidate['found_s'], solution_sha256=sha,
                solution_path=path.relative_to(PROJECT).as_posix(),
                source_path=candidate['path'].name))
        except Exception as exc:
            error = dict(checkpoint_s=t, error=repr(exc))
            validation_errors.append(error)
            checkpoints.append(dict(checkpoint_s=t, status='VALIDATION_FAILED', metrics=None,
                                    best_found_s=candidate['found_s'], solution_sha256=candidate['sha256']))
    trace = progress.get('trace', [])
    first_found = min((r['found_s'] for r in trace if 0 <= r.get('found_s', -1) <= seconds + 1e-6),
                      default=min((p['found_s'] for p in pairs), default=None))
    start = clock.get('started_perf')
    elapsed = state['exit_perf'] - start if start is not None else None
    program_error = worker_error is not None or (state['returncode'] != 0 and state['stop_reason'] is None)
    status = ('WORKER_ERROR' if program_error else 'VALIDATION_ERROR' if validation_errors else
              'STOPPED_BY_MONITOR' if state['stop_reason'] == 'monitor_abort' else 'COMPLETED')
    record = dict(question=q, objective=objective, method=method, seed=42, budget_s=seconds,
        status=status, supplied_initial_solution=False, supplied_warm_start=False,
        paper_solution_used=False, completion_cap_s=cap,
        search_wall_s=finished.get('search_wall_s', elapsed), process_end_elapsed_s=elapsed,
        process_startup_s=start - state['launched_perf'] if start is not None else None,
        first_found_s=first_found, hard_stop=state['stop_reason'] == 'deadline_hard_stop',
        termination_reason=state['stop_reason'] or 'worker_exit', returncode=state['returncode'],
        early_worker_exit=finished.get('early_exit'), program_failure=program_error,
        hard_stop_requested_elapsed_s=state.get('stop_requested_perf', 0) - start
            if start is not None and state.get('stop_requested_perf') else None,
        attempts=progress.get('attempts', 0), complete_constructions=progress.get('complete_constructions', 0),
        constructor_stats=progress.get('constructor_stats', {}), decoder_calls=progress.get('decoder_calls', 0),
        callbacks=progress.get('callbacks', 0), rejections=progress.get('rejections', {}),
        trace=trace, last_worker_phase=progress.get('phase'), checkpoints=checkpoints,
        worker_error=worker_error, validation_errors=validation_errors,
        incomplete_pair_notes=pair_errors, run_path=directory.relative_to(PROJECT).as_posix())
    atomic(directory / 'run.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='monitored_600s_seed42')
    parser.add_argument('--seconds', type=float, default=600.)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--configs', help='Comma-separated Q2_time_greedy,...; defaults to all 16.')
    parser.add_argument('--require-first', type=float, default=90.)
    args = parser.parse_args()
    if args.seconds <= 0 or args.workers < 1 or args.require_first <= 0:
        parser.error('seconds, workers and require-first must be positive')
    labels = (args.configs.split(',') if args.configs else
              [f'{q}_{o}_{m}' for q in ('Q2', 'Q3') for o in ('time', 'energy')
               for m in ('greedy', 'aco', 'alns', 'cp_sat')])
    labels = [x.strip() for x in labels]
    if len(set(labels)) != len(labels) or not all(LABEL.fullmatch(x) for x in labels):
        parser.error('configs must be distinct Q2/Q3_time/energy_greedy/aco/alns/cp_sat labels')
    base = (V6 / args.name).resolve()
    if not base.is_relative_to(V6.resolve()) or base == V6.resolve():
        parser.error('name must stay inside evidence/contest-baselines-v6')
    base.mkdir(parents=True, exist_ok=False)
    sources, physical = freeze(base)
    began = time.perf_counter()
    event_lock = threading.Lock()
    states, records, jobs, alerts, pending = {}, [], {}, [], list(labels)
    abort_reason = None

    def event(kind, **values):
        item = dict(at=utc(), matrix_wall_s=time.perf_counter() - began, event=kind, **values)
        with event_lock:
            with (base / 'monitor_events.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(item, ensure_ascii=False, allow_nan=False) + '\n')
        if kind not in ('HEARTBEAT',):
            print(kind, json.dumps(values, ensure_ascii=False), flush=True)

    protocol = dict(started_at=utc(), configs=labels, seed=42,
        seconds_per_configuration=args.seconds, max_processes=args.workers, cp_workers=1,
        require_first_solution_s=args.require_first, no_first_solution_alert_s=30.,
        monitor_poll_s=1., checkpoints=targets(args.seconds), supplied_initial_solution=False,
        supplied_warm_start=False, paper_solution_used=False,
        source_sha256=sources, physical_input_sha256=physical,
        timing='Input loading is excluded; clock.json starts the per-worker search budget. All first-solution construction, model building, decoding, and improvement are inside it. Parent final validation is outside it.',
        hard_stop='A dedicated deadline watchdog calls taskkill /PID launcher_pid /T /F on Windows. Complete same-run checkpoints with found_s within budget are independently validated afterward.',
        windows_job='The launcher starts suspended, is assigned to a KILL_ON_JOB_CLOSE job, then resumes. The watchdog terminates this whole job immediately at deadline and also attempts taskkill /T /F; taskkill permission failures cannot leave the Python descendant running.',
        no_solution_semantics='NO_FEASIBLE_SOLUTION_FOUND is not an infeasibility proof. Early normal exit and deadline enforcement are not program failures.',
        final_gate='All requested configurations must have independently validated final solutions; otherwise complete is false.',
        energy_caps=dict(Q2=6000., Q3=5939.9), time_caps=dict(Q2=None, Q3=None))
    atomic(base / 'protocol.json', protocol)

    def stop_tree(state, reason):
        with state['stop_lock']:
            if state['proc'].poll() is not None:
                return
            if state['stop_reason'] is None:
                state['stop_reason'] = reason
                state['stop_requested_perf'] = time.perf_counter()
            event('STOP_TREE_REQUEST', config=state['label'], pid=state['proc'].pid,
                  reason=state['stop_reason'], search_elapsed_s=(time.perf_counter() - state['clock']['started_perf'])
                  if state.get('clock') else None)
            if os.name == 'nt':
                job_terminated = False
                try:
                    job_terminated = state['job'].terminate()
                    event('JOB_TREE_TERMINATED', config=state['label'], success=job_terminated)
                except Exception as exc:
                    event('JOB_TREE_TERMINATE_FAILED', config=state['label'], error=repr(exc))
                try:
                    result = subprocess.run(['taskkill', '/PID', str(state['proc'].pid), '/T', '/F'],
                        capture_output=True, text=True, errors='replace', timeout=15,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                    state['tree_stop_returncode'] = result.returncode
                    if result.returncode and state['proc'].poll() is None and not job_terminated:
                        event('STOP_TREE_FAILED', config=state['label'], returncode=result.returncode,
                              detail=(result.stdout + result.stderr)[-2000:])
                except Exception as exc:
                    event('STOP_TREE_FAILED', config=state['label'], error=repr(exc))
            else:
                try:
                    os.killpg(state['proc'].pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def watchdog(state):
        delay = max(0., state['clock']['deadline_perf'] - time.perf_counter())
        if not state['cancel_watch'].wait(delay):
            stop_tree(state, 'deadline_hard_stop')

    def launch(label):
        q, objective, method = LABEL.fullmatch(label).groups()
        directory = base / label
        log = (base / f'{label}.txt').open('w', encoding='utf-8')
        command = [sys.executable, '-u', str(SCRIPTS / 'benchmark_v6.py'), '--question', q,
                   '--objective', objective, '--method', method, '--seconds', str(args.seconds),
                   '--name', str(Path(args.name) / label)]
        kwargs = dict(cwd=PROJECT, stdout=log, stderr=subprocess.STDOUT,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'OMP_NUM_THREADS': '1',
                 'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'})
        if os.name == 'nt':
            job = WindowsJob()
            kwargs['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0) | 0x00000004  # CREATE_SUSPENDED
        else:
            job = None
            kwargs['start_new_session'] = True
        try:
            proc = subprocess.Popen(command, **kwargs)
            if job is not None:
                try:
                    job.attach_and_resume(proc)
                except BaseException:
                    # A suspended, unresumed launcher cannot have descendants.
                    proc.kill()
                    proc.wait(timeout=5)
                    raise
        except BaseException:
            if job is not None:
                job.close()
            log.close()
            raise
        state = dict(label=label, directory=directory, proc=proc, log=log,
            launched_perf=time.perf_counter(), clock=None, stop_reason=None,
            cancel_watch=threading.Event(), stop_lock=threading.Lock(),
            exited=False, alert30=False, startup_alert30=False, job=job,
            last_good_progress={}, has_incumbent_seen=False)
        states[label] = state
        atomic(base / f'{label}_process.json', dict(pid=proc.pid, started_at=utc(), command=command))
        event('START', config=label, pid=proc.pid)

    def save_progress():
        active = []
        for state in states.values():
            if not state['exited']:
                progress = worker_progress(state)
                active.append(dict(config=state['label'], pid=state['proc'].pid,
                    stop_reason=state['stop_reason'], has_incumbent_seen=state['has_incumbent_seen'], **progress))
        atomic(base / 'progress.json', dict(completed=len(records), total=len(labels),
            active=active, pending=list(pending), validating=list(jobs), alerts=alerts,
            abort_reason=abort_reason, wall_s=time.perf_counter() - began))
        atomic(base / 'results.json', sorted(records, key=lambda r: (r['question'], r['objective'], r['method'])))

    validator = ThreadPoolExecutor(max_workers=2, thread_name_prefix='independent_validation')
    last_status = 0.
    try:
        while pending or any(not s['exited'] for s in states.values()) or jobs:
            while pending and abort_reason is None and sum(not s['exited'] for s in states.values()) < args.workers:
                launch(pending.pop(0))
            now = time.perf_counter()
            for label, state in list(states.items()):
                if state['exited']:
                    continue
                directory = state['directory']
                if state['clock'] is None:
                    clock = read(directory / 'clock.json')
                    if clock:
                        if abs(clock['budget_s'] - args.seconds) > 1e-6 or clock['deadline_perf'] < clock['started_perf']:
                            abort_reason = abort_reason or f'{label}: invalid worker clock'
                        state['clock'] = clock
                        threading.Thread(target=watchdog, args=(state,), daemon=True,
                                         name=f'deadline_{label}').start()
                        event('CLOCK', config=label, startup_s=clock['started_perf'] - state['launched_perf'])
                progress = worker_progress(state)
                clock = state['clock']
                elapsed = now - (clock['started_perf'] if clock else state['launched_perf'])
                error = read(directory / 'worker_error.json')
                if error:
                    abort_reason = abort_reason or f'{label}: worker_error {error}'
                if clock is None and elapsed >= 30 and not state['startup_alert30']:
                    state['startup_alert30'] = True
                    alerts.append(dict(config=label, reason='startup_no_clock_30s'))
                    event('ALERT', config=label, reason='startup_no_clock_30s')
                if clock is not None and not state['has_incumbent_seen'] and elapsed >= 30 and not state['alert30']:
                    state['alert30'] = True
                    alerts.append(dict(config=label, reason='no_first_solution_30s', phase=progress.get('phase')))
                    event('ALERT', config=label, reason='no_first_solution_30s', progress=progress)
                if not state['has_incumbent_seen'] and elapsed >= args.require_first and state['proc'].poll() is None:
                    abort_reason = abort_reason or f'{label}: no first solution after {args.require_first:g}s ({progress.get("phase", "startup")})'
                returncode = state['proc'].poll()
                if returncode is not None:
                    state['exited'] = True
                    state['cancel_watch'].set()
                    state['returncode'] = returncode
                    state['exit_perf'] = time.perf_counter()
                    if state['job'] is not None:
                        state['job'].close()
                    state['log'].close()
                    if returncode != 0 and state['stop_reason'] is None:
                        abort_reason = abort_reason or f'{label}: unexpected exit {returncode}'
                    jobs[label] = validator.submit(seal, state, args.seconds)
                    event('PROCESS_EXIT', config=label, returncode=returncode,
                          reason=state['stop_reason'] or 'worker_exit')
            for label, future in list(jobs.items()):
                if not future.done():
                    continue
                try:
                    record = future.result()
                    records.append(record)
                    final_status = record['checkpoints'][-1]['status']
                    event('SEALED', config=label, status=record['status'], final_status=final_status,
                          first_found_s=record['first_found_s'])
                    if record['status'] in ('WORKER_ERROR', 'VALIDATION_ERROR'):
                        abort_reason = abort_reason or f'{label}: {record["status"]}'
                except Exception as exc:
                    abort_reason = abort_reason or f'{label}: parent validation exception {exc!r}'
                    event('VALIDATION_EXCEPTION', config=label, error=repr(exc))
                del jobs[label]
            if abort_reason:
                if not any(a.get('reason') == 'round_aborted' for a in alerts):
                    alerts.append(dict(reason='round_aborted', detail=abort_reason))
                    event('ROUND_ABORT', reason=abort_reason, not_started=list(pending))
                pending.clear()
                for state in states.values():
                    if not state['exited'] and state['stop_reason'] is None:
                        threading.Thread(target=stop_tree, args=(state, 'monitor_abort'), daemon=True).start()
            save_progress()
            if time.perf_counter() - last_status >= 15:
                event('STATUS', completed=len(records), active=[k for k, s in states.items() if not s['exited']],
                    phases={k: worker_progress(s).get('phase')
                            for k, s in states.items() if not s['exited']},
                    live_feasible=[k for k, s in states.items() if not s['exited'] and s['has_incumbent_seen']],
                    feasible=[f'{r["question"]}_{r["objective"]}_{r["method"]}' for r in records
                              if r['checkpoints'][-1]['status'] == 'VALIDATED_FEASIBLE'])
                last_status = time.perf_counter()
            time.sleep(1.)
    except BaseException:
        for state in states.values():
            if not state['exited']:
                stop_tree(state, 'monitor_abort')
        raise
    finally:
        validator.shutdown(wait=True)
        for state in states.values():
            state['cancel_watch'].set()
            if state['job'] is not None:
                state['job'].close()
            if not state['log'].closed:
                state['log'].close()
    source_changes = [p for p, sha in sources.items() if not (PROJECT / p).exists() or digest(PROJECT / p) != sha]
    physical_changes = [p for p, sha in physical.items() if not (PROJECT / p).exists() or digest(PROJECT / p) != sha]
    final_feasible = sum(r['checkpoints'][-1]['status'] == 'VALIDATED_FEASIBLE' for r in records)
    complete = (len(records) == len(labels) and final_feasible == len(labels) and abort_reason is None
                and not source_changes and not physical_changes)
    completion = dict(complete=complete, completed_runs=len(records), requested_runs=len(labels),
        feasible_final_runs=final_feasible, abort_reason=abort_reason,
        experiment_wall_s=time.perf_counter() - began,
        sum_search_wall_s=sum(r['search_wall_s'] or 0 for r in records),
        source_changes=source_changes, physical_input_changes=physical_changes,
        not_started=[label for label in labels if label not in states], finished_at=utc())
    atomic(base / 'completion.json', completion)
    import csv
    with (base / 'results.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        columns = ['question', 'objective', 'method', 'checkpoint_s', 'status', 'completion_s',
                   'energy_kwh', 'transport_sorties', 'relay_sorties', 'first_found_s', 'search_wall_s', 'hard_stop']
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for record in sorted(records, key=lambda r: (r['question'], r['objective'], r['method'])):
            for cp in record['checkpoints']:
                metrics = cp['metrics'] or {}
                writer.writerow(dict(question=record['question'], objective=record['objective'], method=record['method'],
                    checkpoint_s=cp['checkpoint_s'], status=cp['status'],
                    **{k: metrics.get(k) for k in ('completion_s', 'energy_kwh', 'transport_sorties', 'relay_sorties')},
                    first_found_s=record['first_found_s'], search_wall_s=record['search_wall_s'], hard_stop=record['hard_stop']))
    event('COMPLETE' if complete else 'INCOMPLETE', **completion)
    return 0 if complete else 2


if __name__ == '__main__':
    sys.exit(main())
