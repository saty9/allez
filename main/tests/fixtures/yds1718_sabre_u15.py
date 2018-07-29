from main import models
from django.utils import timezone


class TestCase:
    org = None
    s1 = None
    s2 = None
    s3 = None
    comp = None
    address = None
    club1 = None
    club2 = None
    club3 = None
    f1 = None
    f2 = None
    f3 = None
    f4 = None

    def __init__(self):
        self.org = models.Organisation(address=None, name='f4sf', email='a@b.com', contactNumber='07990624284')
        self.org.save()
        self.comp = models.Competition(organisation=self.org, date=timezone.now().date(), name='YDS Round 1')
        self.comp.save()
        self.s0 = models.Stage.objects.create(type=models.Stage.ADD, competition=self.comp, number=0)
        self.add_stage = self.s0.addstage_set.create()
        self.s1 = models.Stage(type=models.Stage.POOL, competition=self.comp, number=1)
        self.s1.save()
        self.ps1 = models.PoolStage.objects.create(stage=self.s1)
        self.s2 = models.Stage(type=models.Stage.POOL, competition=self.comp, number=2)
        self.s2.save()
        self.ps2 = models.PoolStage.objects.create(stage=self.s2, carry_previous_results=True)
        self.s3 = models.Stage(type=models.Stage.POOL, competition=self.comp, number=3)
        self.s3.save()
        self.ps3 = models.PoolStage.objects.create(stage=self.s3, carry_previous_results=True)
        self.address = models.Address(country='GBR')
        self.address.save()
        self.club1 = models.Club(name='Salle Ossian', address=self.address)
        self.club1.save()
        self.club2 = models.Club(name='EFC', address=self.address)
        self.club2.save()
        self.club3 = models.Club(name='WFFC', address=self.address)
        self.club3.save()
        self.f1 = models.Competitor(name='M, R', license_number=0, club=self.club1, organisation=self.org)
        self.f1.save()
        self.f2 = models.Competitor(name='J, M', license_number=1, club=self.club2, organisation=self.org)
        self.f2.save()
        self.f3 = models.Competitor(name='M, D', license_number=2, club=self.club1, organisation=self.org)
        self.f3.save()
        self.f4 = models.Competitor(name='H, K', license_number=3, club=self.club3, organisation=self.org)
        self.f4.save()
        for index, f in enumerate([self.f4, self.f3, self.f2, self.f1]):
            e = self.comp.entry_set.create(competitor=f, state=models.Entry.CHECKED_IN)
            self.add_stage.addcompetitor_set.create(entry=e, sequence=index)
        self.ps1.start(1)

        # Round 1
        p = models.Pool.objects.get(stage=self.ps1)
        pe1 = models.PoolEntry.objects.get(entry=self.f1.entry_set.first(), pool=p)
        pe2 = models.PoolEntry.objects.get(entry=self.f2.entry_set.first(), pool=p)
        pe3 = models.PoolEntry.objects.get(entry=self.f3.entry_set.first(), pool=p)
        pe4 = models.PoolEntry.objects.get(entry=self.f4.entry_set.first(), pool=p)

        models.PoolBout.create(pe1, pe2, 5, 1, True)
        models.PoolBout.create(pe1, pe3, 5, 1, True)
        models.PoolBout.create(pe1, pe4, 5, 0, True)
        models.PoolBout.create(pe2, pe3, 1, 5, False)
        models.PoolBout.create(pe2, pe4, 2, 5, False)
        models.PoolBout.create(pe3, pe4, 5, 1, True)

        # Round 2
        self.ps2.start(1)
        p = self.ps2.pool_set.first()
        pe1 = models.PoolEntry.objects.get(entry=self.f4.entry_set.first(), pool=p)
        pe2 = models.PoolEntry.objects.get(entry=self.f3.entry_set.first(), pool=p)
        pe3 = models.PoolEntry.objects.get(entry=self.f2.entry_set.first(), pool=p)
        pe4 = models.PoolEntry.objects.get(entry=self.f1.entry_set.first(), pool=p)

        models.PoolBout.create(pe1, pe2, 5, 3, True)
        models.PoolBout.create(pe1, pe3, 5, 2, True)
        models.PoolBout.create(pe1, pe4, 3, 5, False)
        models.PoolBout.create(pe2, pe3, 5, 1, True)
        models.PoolBout.create(pe2, pe4, 1, 5, False)
        models.PoolBout.create(pe3, pe4, 1, 5, False)

        # Round 3
        self.ps3.start(1)
        p = self.ps3.pool_set.first()
        pe1 = models.PoolEntry.objects.get(entry=self.f4.entry_set.first(), pool=p)
        pe2 = models.PoolEntry.objects.get(entry=self.f3.entry_set.first(), pool=p)
        pe3 = models.PoolEntry.objects.get(entry=self.f2.entry_set.first(), pool=p)
        pe4 = models.PoolEntry.objects.get(entry=self.f1.entry_set.first(), pool=p)

        models.PoolBout.create(pe1, pe2, 4, 5, False)
        models.PoolBout.create(pe1, pe3, 5, 2, True)
        models.PoolBout.create(pe1, pe4, 2, 5, False)
        models.PoolBout.create(pe2, pe3, 5, 4, True)
        models.PoolBout.create(pe2, pe4, 1, 5, False)
        models.PoolBout.create(pe3, pe4, 1, 5, False)

        self.s4 = models.Stage.objects.create(type=models.Stage.DE, competition=self.comp, number=4)
        self.de = models.DeStage.objects.create(stage=self.s4, fight_down_to=4)
        self.de.start()

        table = self.de.detable_set.first()

        table.detableentry_set.filter(entry=self.f1.entry_set.first()).update(victory=True, score=15)
        table.detableentry_set.filter(entry=self.f2.entry_set.first()).update(victory=False, score=5)
        table.detableentry_set.filter(entry=self.f3.entry_set.first()).update(victory=True, score=15)
        table.detableentry_set.filter(entry=self.f4.entry_set.first()).update(victory=False, score=7)

        table.make_children()

        de_table_w = table.children.get(winners=True)
        de_table_l = table.children.get(winners=False)

        de_table_w.detableentry_set.filter(entry=self.f1.entry_set.first()).update(victory=True, score=15)
        de_table_w.detableentry_set.filter(entry=self.f3.entry_set.first()).update(victory=False, score=0)

        de_table_l.detableentry_set.filter(entry=self.f2.entry_set.first()).update(victory=False, score=5)
        de_table_l.detableentry_set.filter(entry=self.f4.entry_set.first()).update(victory=True, score=15)
