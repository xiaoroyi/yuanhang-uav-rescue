"""Mutation tests of review examples; these do not fabricate solver evidence."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import check_contracts as c


class ContractsTest(unittest.TestCase):
    def setUp(self):
        self.snapshot = c.read_json(c.ROOT / 'fixtures/mock/snapshot.json')
        self.plan = c.read_json(c.ROOT / 'fixtures/mock/plan.json')
        self.options = c.read_json(c.ROOT / 'fixtures/mock/solver-options.json')
        self.job = c.read_json(c.ROOT / 'fixtures/mock/solve-job.json')
        self.outcome = c.read_json(c.ROOT / 'fixtures/mock/solver-outcome.json')
        self.event = c.read_json(c.ROOT / 'fixtures/mock/event.json')

    def test_all_development_examples(self):
        c.main()

    def test_soc_is_fraction(self):
        for value in [25, -0.1, 1.01]:
            with self.subTest(value=value):
                s = copy.deepcopy(self.snapshot['scenario'])
                s['batteries'][0]['soc'] = value
                with self.assertRaises(c.ContractError):
                    c.validate_scenario(s)

    def test_unversioned_extra_field_rejected(self):
        self.plan['relay_missions'] = []
        with self.assertRaises(c.ContractError):
            c.validate_schema('plan', self.plan)

    def test_coordinates_are_bounded_lon_lat(self):
        self.snapshot['scenario']['base']['coordinates'] = [22.9, 108.9]
        with self.assertRaises(c.ContractError):
            c.validate_scenario(self.snapshot['scenario'])

    def test_absolute_time_needs_offset_and_valid_date(self):
        for value in ['2026-10-17T09:00:00', '2026-02-30T09:00:00+08:00']:
            with self.subTest(value=value):
                s = copy.deepcopy(self.snapshot['scenario'])
                s['start_time'] = value
                with self.assertRaises(c.ContractError):
                    c.validate_scenario(s)

    def test_duplicate_and_missing_references(self):
        s = copy.deepcopy(self.snapshot['scenario'])
        s['drones'].append(copy.deepcopy(s['drones'][0]))
        with self.assertRaises(c.ContractError):
            c.validate_scenario(s)
        s = copy.deepcopy(self.snapshot['scenario'])
        s['cargo_items'][0]['demand_id'] = 'missing'
        with self.assertRaises(c.ContractError):
            c.validate_scenario(s)

    def test_snapshot_hash_and_version(self):
        self.snapshot['scenario']['name'] = 'Changed without rehash'
        with self.assertRaises(c.ContractError):
            c.validate_snapshot(self.snapshot)
        self.snapshot['content_hash'] = c.content_hash(self.snapshot['scenario'])
        self.snapshot['scenario_state_version'] += 1
        with self.assertRaises(c.ContractError):
            c.validate_snapshot(self.snapshot)

    def test_old_plan_cannot_bind_new_snapshot(self):
        self.plan['scenario_state_version'] += 1
        with self.assertRaises(c.ContractError):
            c.validate_plan(self.plan, self.snapshot)

    def test_mock_can_never_be_confirmable(self):
        self.plan['has_validated_plan'] = True
        with self.assertRaises(c.ContractError):
            c.validate_plan(self.plan, self.snapshot)

    def test_feasible_without_plan_is_invalid(self):
        self.outcome['solver_status'] = 'FEASIBLE'
        with self.assertRaises(c.ContractError):
            c.validate_outcome(self.outcome, self.snapshot)

    def test_success_cannot_reference_mock_plan(self):
        self.outcome.update(solver_status='FEASIBLE', plan=self.plan, candidate_count=1,
                            first_feasible_s=0, stop_reason='finished', validation={'status':'passed','checks':[]})
        with self.assertRaises(c.ContractError):
            c.validate_outcome(self.outcome, self.snapshot)

    def test_unknown_completed_job_has_no_plan(self):
        self.job.update(job_state='completed', solver_status='UNKNOWN', plan_id='PLAN-MOCK-001',
                        runtime_s=1, finished_at='2026-10-17T09:00:01+08:00')
        with self.assertRaises(c.ContractError):
            c.validate_job(self.job)

    def test_job_success_requires_resolvable_validated_plan(self):
        self.job.update(job_state='completed', solver_status='FEASIBLE', plan_id=self.job['reserved_plan_id'],
                        has_validated_plan=True, runtime_s=1, finished_at='2026-10-17T09:00:01+08:00')
        with self.assertRaises(c.ContractError):
            c.validate_job(self.job)

    def test_duplicate_cargo_detected(self):
        self.plan['sorties'].append(copy.deepcopy(self.plan['sorties'][0]))
        self.plan['sorties'][1]['sortie_id'] = 'SECOND'
        with self.assertRaises(c.ContractError):
            c.validate_plan(self.plan, self.snapshot)

    def test_release_and_visit_time_order(self):
        for key, value in [('battery_released_s',899), ('drone_released_s',899), ('takeoff_s',901)]:
            with self.subTest(key=key):
                p = copy.deepcopy(self.plan)
                p['sorties'][0][key] = value
                with self.assertRaises(c.ContractError):
                    c.validate_plan(p, self.snapshot)

    def two_sorties(self):
        s = self.snapshot['scenario']
        s['demands'][0]['required_quantity'] = 2
        item = copy.deepcopy(s['cargo_items'][0]); item['cargo_id'] = 'BOX02'; s['cargo_items'].append(item)
        self.snapshot['content_hash'] = c.content_hash(s)
        other = copy.deepcopy(self.plan['sorties'][0])
        other.update(sortie_id='SECOND', cargo_ids=['BOX02'])
        other['visits'][0]['cargo_ids'] = ['BOX02']
        self.plan['sorties'].append(other)
        self.plan['metrics']['sortie_count'] = 2

    def test_overlapping_entity_windows_detected(self):
        self.two_sorties()
        with self.assertRaisesRegex(c.ContractError, 'overlapping'):
            c.validate_plan(self.plan, self.snapshot)

    def test_half_open_release_allows_next_task(self):
        self.two_sorties()
        second = self.plan['sorties'][1]
        for key in ['prepare_start_s','takeoff_s','return_s','drone_released_s','battery_released_s']:
            second[key] += 1200
        second['visits'][0]['delivery_complete_s'] += 1200
        self.plan['metrics'].update(makespan_s=2100,last_delivery_s=1700)
        c.validate_plan(self.plan, self.snapshot)

    def test_unknown_energy_is_not_zero(self):
        self.plan['metrics']['energy_kwh'] = 0
        with self.assertRaises(c.ContractError):
            c.validate_plan(self.plan, self.snapshot)

    def test_mandatory_scope_cannot_be_omitted(self):
        self.snapshot['scenario']['policy']['requires_communication'] = True
        self.snapshot['content_hash'] = c.content_hash(self.snapshot['scenario'])
        with self.assertRaises(c.ContractError):
            c.validate_options(self.options, self.snapshot)

    def test_replan_links_are_paired(self):
        self.options['mode'] = 'replan'
        with self.assertRaises(c.ContractError):
            c.validate_options(self.options, self.snapshot)

    def test_event_cannot_rewind_execution(self):
        self.snapshot['scenario']['cargo_items'][0]['status'] = 'delivered'
        with self.assertRaises(c.ContractError):
            c.validate_event(self.event, self.snapshot['scenario'])

    def test_wrong_event_payload_rejected(self):
        self.event['payload'] = {'battery_id':'BAT01'}
        with self.assertRaises(c.ContractError):
            c.validate_event(self.event, self.snapshot['scenario'])

    def test_partial_service_requires_new_contract(self):
        self.snapshot['scenario']['demands'][0]['required_quantity'] = 2
        self.snapshot['content_hash'] = c.content_hash(self.snapshot['scenario'])
        with self.assertRaises(c.ContractError):
            c.validate_plan(self.plan, self.snapshot)

    def test_json_duplicates_and_nan_rejected(self):
        with self.assertRaises(c.ContractError):
            c.unique_pairs([('a',1),('a',2)])
        with self.assertRaises(ValueError):
            c.content_hash({'bad':float('nan')})


if __name__ == '__main__':
    unittest.main()
