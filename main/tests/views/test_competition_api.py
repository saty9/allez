import csv
from io import StringIO
from ..factories.competition_factory import BaseCompetitionFactory, PreAddedCompetitionOfSize, CompetitionOfSize
from ..factories.org_member_factory import ManagerFactory
from ..factories.organisation_factory import OrganisationFactory
from ..factories.club_factory import ClubFactory
from ..factories.competitor_factory import CompetitorFactory
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Competition, Club, Stage, Entry


class TestCompetitionAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = BaseCompetitionFactory()  # type: Competition
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        self.target = reverse('main/competition_endpoint', kwargs={'comp_id': self.competition.id})

    def test_authorization_block(self):
        out = self.c.post(self.target, {'type': 'anything'})
        unauthorised_message = {'success': False, 'reason': 'NotLoggedIn'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

        org = OrganisationFactory()
        wrong_org_manager = ManagerFactory(organisation=org).user
        self.c.force_login(wrong_org_manager)
        out = self.c.post(self.target, {'type': 'set_cull_level'})
        unauthorised_message = {'success': False, 'reason': 'InsufficientPermissions'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

    def test_entry_csv_file_upload_base(self):
        self.c.force_login(self.manager)
        entries = []
        entry_vals = []
        for x in range(8):
            competitor = CompetitorFactory.build()
            club = ClubFactory.build()
            entries.append((competitor, club))
            entry_vals.append((competitor.name, club.name, competitor.license_number, x))
        f = StringIO()
        csv.writer(f).writerows(entry_vals)
        f.seek(0)
        out = self.c.post(self.target, {'type': 'entry_csv',
                                        'file': f})
        self.assertJSONEqual(out.content, {'success': True,
                                           'added_count': len(entries)})
        self.assertEqual(len(entries), self.competition.entry_set.count())
        self.assertEqual(list(self.competition.stage_set.values('type', 'state')), [{'type': Stage.ADD,
                                                                                     'state': Stage.NOT_STARTED}])
        created_entries = self.competition.entry_set.order_by('seed').values_list('competitor__name',
                                                                                  'club__name',
                                                                                  'competitor__license_number',
                                                                                  'seed')
        self.assertEqual(entry_vals, list(created_entries))

    def test_entry_csv_file_upload_add_stage_already_exists(self):
        comp = PreAddedCompetitionOfSize(entries__num_of_entries=8, organisation=self.competition.organisation)
        self.c.force_login(self.manager)
        entry_vals = list(comp.entry_set.order_by('competitor').values_list('competitor__name',
                                                                            'club__name',
                                                                            'competitor__license_number',
                                                                            'seed'))
        vals_to_add = []
        adding = 8
        for x in range(adding):
            competitor = CompetitorFactory.build()
            club = ClubFactory.build()
            vals_to_add.append((competitor.name, club.name, competitor.license_number, x+8))
        entry_vals = vals_to_add + entry_vals
        f = StringIO()
        csv.writer(f).writerows(vals_to_add)
        f.seek(0)
        target = reverse('main/competition_endpoint', kwargs={'comp_id': comp.id})
        out = self.c.post(target, {'type': 'entry_csv',
                                   'file': f})
        self.assertJSONEqual(out.content, {'success': True,
                                           'added_count': adding})
        self.assertEqual(len(entry_vals), comp.entry_set.count())
        self.assertEqual(comp.stage_set.filter(type=Stage.ADD).count(), 2)
        created_entries = comp.entry_set.order_by('seed', 'competitor').values_list('competitor__name',
                                                                                    'club__name',
                                                                                    'competitor__license_number',
                                                                                    'seed')
        self.assertEqual(entry_vals, list(created_entries))

    def test_entry_csv_file_upload_repeated_club(self):
        self.c.force_login(self.manager)
        entries = []
        entry_vals = []
        for x in range(8):
            competitor = CompetitorFactory.build()
            club = ClubFactory.build()
            entries.append((competitor, club))
            entry_vals.append((competitor.name, club.name, competitor.license_number, x))
        entry_vals[0] = (entry_vals[0][0], entry_vals[1][1], entry_vals[0][2], entry_vals[0][3])
        f = StringIO()
        csv.writer(f).writerows(entry_vals)
        f.seek(0)
        out = self.c.post(self.target, {'type': 'entry_csv',
                                        'file': f})
        self.assertJSONEqual(out.content, {'success': True,
                                           'added_count': len(entries)})
        self.assertEqual(len(entries), self.competition.entry_set.count())
        self.assertEqual(len(entries) - 1, Club.objects.count())
        created_entries = self.competition.entry_set.order_by('seed').values_list('competitor__name',
                                                                                  'club__name',
                                                                                  'competitor__license_number',
                                                                                  'seed')
        self.assertEqual(entry_vals, list(created_entries))

    def test_entry_csv_file_upload_no_entries(self):
        self.c.force_login(self.manager)
        f = StringIO()
        f.seek(0)
        out = self.c.post(self.target, {'type': 'entry_csv',
                                        'file': f})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'row_column_error',
                                           'verbose_reason': 'Unexpected number of rows/columns in uploaded file'})
        self.assertEqual(0, self.competition.entry_set.count())

    def test_entry_csv_file_upload_column_errors(self):
        self.c.force_login(self.manager)
        f = StringIO()
        csv.writer(f).writerows([['name', 'club', 'license', 999, 'might show up'], ['a', 'b', 'c', 'd']])
        f.seek(0)
        out = self.c.post(self.target, {'type': 'entry_csv',
                                        'file': f})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'row_column_error',
                                           'verbose_reason': 'Unexpected number of rows/columns in uploaded file'})
        f = StringIO()
        csv.writer(f).writerows([['name', 'club'], ['a', 'b']])
        f.seek(0)
        out = self.c.post(self.target, {'type': 'entry_csv',
                                        'file': f})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'row_column_error',
                                           'verbose_reason': 'Unexpected number of rows/columns in uploaded file'})
        self.assertEqual(0, self.competition.entry_set.count())

    def test_entry_csv_file_upload_bad_seed(self):
        self.c.force_login(self.manager)
        entries = []
        entry_vals = []
        for x in range(8):
            competitor = CompetitorFactory.build()
            club = ClubFactory.build()
            entries.append((competitor, club))
            entry_vals.append((competitor.name, club.name, competitor.license_number, x))
        entry_vals[3] = (entry_vals[3][0], entry_vals[3][1], entry_vals[3][2], "hi")
        f = StringIO()
        csv.writer(f).writerows(entry_vals)
        f.seek(0)
        out = self.c.post(self.target, {'type': 'entry_csv',
                                        'file': f})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'seed_parse_error',
                                           'verbose_reason': 'one of the seeds could not be interpreted as a number'})
        self.assertEqual(0, self.competition.entry_set.count())

    def test_add_stage_base(self):
        self.c.force_login(self.manager)
        number = -1
        for stage_type in [Stage.ADD, Stage.POOL, Stage.CULL, Stage.DE]:
            out = self.c.post(self.target, {'type': 'add_stage',
                                            'number': number,
                                            'stage_type': stage_type})
            self.assertJSONEqual(out.content, {'success': True})
            number += 1
            assert self.competition.stage_set.filter(number=number, type=stage_type).exists()
            self.assertEqual(self.competition.stage_set.count(), number + 1)

    def test_add_stage_bad_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'add_stage',
                                        'number': 0,
                                        'stage_type': 'anything'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'bad_type',
                                           'verbose_reason': 'Failed to add stage: unrecognised stage type'})
        self.assertEqual(self.competition.stage_set.count(), 0)

    def test_add_stage_insert_between(self):
        self.c.force_login(self.manager)
        self.competition.stage_set.create(number=0, type=Stage.ADD)
        self.competition.stage_set.create(number=1, type=Stage.DE)
        out = self.c.post(self.target, {'type': 'add_stage',
                                        'number': 0,
                                        'stage_type': Stage.CULL})
        self.assertJSONEqual(out.content, {'success': True})
        assert self.competition.stage_set.filter(number=1, type=Stage.CULL).exists()
        assert self.competition.stage_set.filter(number=2, type=Stage.DE).exists()
        self.assertEqual(self.competition.stage_set.count(), 3)

    def test_add_stage_unappendable(self):
        self.c.force_login(self.manager)
        self.competition.stage_set.create(number=0, type=Stage.ADD, state=Stage.FINISHED)
        self.competition.stage_set.create(number=1, type=Stage.DE)
        out = self.c.post(self.target, {'type': 'add_stage',
                                        'number': 0,
                                        'stage_type': Stage.CULL})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'stage_unappendable_to',
                                           'verbose_reason': 'Stage cannot be appended to'})
        self.assertFalse(self.competition.stage_set.filter(number=1, type=Stage.CULL).exists())
        self.assertEqual(self.competition.stage_set.count(), 2)

    def test_delete_stage(self):
        self.c.force_login(self.manager)
        victim = self.competition.stage_set.create(number=0, type=Stage.ADD)
        shuffle_down = self.competition.stage_set.create(number=1, type=Stage.DE)
        out = self.c.post(self.target, {'type': 'delete_stage',
                                        'id': victim.id})
        self.assertJSONEqual(out.content, {'success': True})
        self.assertFalse(self.competition.stage_set.filter(id=victim.id).exists())
        self.assertEqual(self.competition.stage_set.count(), 1)
        shuffle_down.refresh_from_db()
        self.assertEqual(shuffle_down.number, 0)

    def test_delete_stage_undeletable(self):
        self.c.force_login(self.manager)
        victim = self.competition.stage_set.create(number=0, type=Stage.ADD, state=Stage.LOCKED)
        out = self.c.post(self.target, {'type': 'delete_stage',
                                        'id': victim.id})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'stage_undeletable',
                                           'verbose_reason': 'Cannot delete this stage'})
        assert self.competition.stage_set.filter(id=victim.id).exists()
        self.assertEqual(self.competition.stage_set.count(), 1)

    def test_check_in_all(self):
        self.c.force_login(self.manager)
        comp = CompetitionOfSize(entries__num_of_entries=8, organisation=self.competition.organisation)
        comp.entry_set.update(state=Entry.NOT_CHECKED_IN)
        target = reverse('main/competition_endpoint', kwargs={'comp_id': comp.id})
        out = self.c.post(target, {'type': 'check_in_all'})
        self.assertJSONEqual(out.content, {'success': True})
        assert all(map(lambda e: e.state == Entry.CHECKED_IN, comp.entry_set.all()))

    def test_check_in_all_doesnt_change_other_states(self):
        self.c.force_login(self.manager)
        comp = CompetitionOfSize(entries__num_of_entries=8, organisation=self.competition.organisation)
        comp.entry_set.update(state=Entry.NOT_CHECKED_IN)
        entry = comp.entry_set.first()
        entry.state = Entry.EXCLUDED
        entry.save()
        target = reverse('main/competition_endpoint', kwargs={'comp_id': comp.id})
        out = self.c.post(target, {'type': 'check_in_all'})
        self.assertJSONEqual(out.content, {'success': True})
        entry.refresh_from_db()
        self.assertEqual(entry.state, Entry.EXCLUDED)

    def test_check_in(self):
        self.c.force_login(self.manager)
        comp = CompetitionOfSize(entries__num_of_entries=8, organisation=self.competition.organisation)
        comp.entry_set.update(state=Entry.NOT_CHECKED_IN)
        entry = comp.entry_set.first()
        target = reverse('main/competition_endpoint', kwargs={'comp_id': comp.id})
        out = self.c.post(target, {'type': 'check_in',
                                   'id': entry.id})
        self.assertJSONEqual(out.content, {'success': True})
        entry.refresh_from_db()
        self.assertEqual(entry.state, Entry.CHECKED_IN)

    def test_check_in_doesnt_change_other_states(self):
        self.c.force_login(self.manager)
        comp = CompetitionOfSize(entries__num_of_entries=8, organisation=self.competition.organisation)
        entry = comp.entry_set.first()
        for state in [Entry.EXCLUDED, Entry.CHECKED_IN, Entry.DID_NOT_FINISH]:
            entry.state = state
            entry.save()
            target = reverse('main/competition_endpoint', kwargs={'comp_id': comp.id})
            out = self.c.post(target, {'type': 'check_in',
                                       'id': entry.id})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'already_checked_in',
                                               'verbose_reason': 'That entry has already checked in'})
            entry.refresh_from_db()
            self.assertEqual(entry.state, state)

    def test_check_in_entry_not_in_competition(self):
        self.c.force_login(self.manager)
        comp = CompetitionOfSize(entries__num_of_entries=8, organisation=self.competition.organisation)
        entry = CompetitionOfSize(entries__num_of_entries=8).entry_set.first()
        target = reverse('main/competition_endpoint', kwargs={'comp_id': comp.id})
        out = self.c.post(target, {'type': 'check_in',
                                   'id': entry.id})
        self.assertEqual(out.status_code, 404)

    def test_add_entry(self):
        self.c.force_login(self.manager)
        c = CompetitorFactory(organisation=self.competition.organisation)
        club = ClubFactory()
        out = self.c.post(self.target, {'type': 'add_entry',
                                        'name': c.name,
                                        'license_number': c.license_number,
                                        'club_name': club.name,
                                        'seed': 1})
        self.assertJSONEqual(out.content, {'success': True})
        assert self.competition.entry_set.filter(competitor=c, club=club, state=Entry.NOT_CHECKED_IN, seed=1).exists()

    def test_add_entry_no_seed(self):
        self.c.force_login(self.manager)
        c = CompetitorFactory(organisation=self.competition.organisation)
        club = ClubFactory()
        out = self.c.post(self.target, {'type': 'add_entry',
                                        'name': c.name,
                                        'license_number': c.license_number,
                                        'club_name': club.name})
        self.assertJSONEqual(out.content, {'success': True})
        assert self.competition.entry_set.filter(competitor=c, club=club, state=Entry.NOT_CHECKED_IN, seed=999).exists()

    def test_add_entry_bad_seed(self):
        self.c.force_login(self.manager)
        c = CompetitorFactory(organisation=self.competition.organisation)
        club = ClubFactory()
        out = self.c.post(self.target, {'type': 'add_entry',
                                        'name': c.name,
                                        'license_number': c.license_number,
                                        'club_name': club.name,
                                        'seed': 'hi'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'seed_parse_error',
                                           'verbose_reason': 'one of the seeds could not be interpreted as a number'})
        self.assertFalse(self.competition.entry_set.exists())

    def test_add_entry_auto_checkin(self):
        self.c.force_login(self.manager)
        c = CompetitorFactory(organisation=self.competition.organisation)
        club = ClubFactory()
        out = self.c.post(self.target, {'type': 'add_entry',
                                        'name': c.name,
                                        'license_number': c.license_number,
                                        'club_name': club.name,
                                        'check_in': '1'})
        self.assertJSONEqual(out.content, {'success': True})
        assert self.competition.entry_set.filter(competitor=c, club=club, state=Entry.CHECKED_IN).exists()

    def test_post_bad_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'anything_else'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'unrecognised request',
                                           'verbose_reason': 'Unrecognised request'})
