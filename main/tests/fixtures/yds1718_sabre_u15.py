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
        self.s1 = models.Stage(type=models.Stage.POOL, data={}, competition=self.comp, number=1)
        self.s1.save()
        self.ps1 = models.PoolStage.objects.create(stage=self.s1)
        self.s2 = models.Stage(type=models.Stage.POOL, data={}, competition=self.comp, number=2)
        self.s2.save()
        self.ps2 = models.PoolStage.objects.create(stage=self.s2, carry_previous_results=True)
        self.s3 = models.Stage(type=models.Stage.POOL, data={}, competition=self.comp, number=3)
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
        self.f1 = models.Competitor(name='M, R', license_number=0, club=self.club1)
        self.f1.save()
        self.f2 = models.Competitor(name='J, M', license_number=1, club=self.club2)
        self.f2.save()
        self.f3 = models.Competitor(name='M, D', license_number=2, club=self.club1)
        self.f3.save()
        self.f4 = models.Competitor(name='H, K', license_number=3, club=self.club3)
        self.f4.save()
        for f in [self.f1, self.f2, self.f3, self.f4]:
            e = models.Entry(competition=self.comp, competitor=f)
            e.save()
        for pool_stage in [self.ps1, self.ps2, self.ps3]:
            p = models.Pool.objects.create(stage=pool_stage, number=1)

        # Round 1
        p = models.Pool.objects.get(stage=self.ps1)
        pe1 = models.PoolEntry.objects.create(entry=self.f1.entry_set.first(), pool=p, number=1)
        pe2 = models.PoolEntry.objects.create(entry=self.f2.entry_set.first(), pool=p, number=2)
        pe3 = models.PoolEntry.objects.create(entry=self.f3.entry_set.first(), pool=p, number=3)
        pe4 = models.PoolEntry.objects.create(entry=self.f4.entry_set.first(), pool=p, number=4)

        models.PoolBout.create(pe1, pe2, 5, 1, True)
        models.PoolBout.create(pe1, pe3, 5, 1, True)
        models.PoolBout.create(pe1, pe4, 5, 0, True)
        models.PoolBout.create(pe2, pe3, 1, 5, False)
        models.PoolBout.create(pe2, pe4, 2, 5, False)
        models.PoolBout.create(pe3, pe4, 5, 1, True)

        # Round 2
        p = models.Pool.objects.get(stage=self.ps2)
        pe1 = models.PoolEntry.objects.create(entry=self.f4.entry_set.first(), pool=p, number=1)
        pe2 = models.PoolEntry.objects.create(entry=self.f3.entry_set.first(), pool=p, number=2)
        pe3 = models.PoolEntry.objects.create(entry=self.f2.entry_set.first(), pool=p, number=3)
        pe4 = models.PoolEntry.objects.create(entry=self.f1.entry_set.first(), pool=p, number=4)

        models.PoolBout.create(pe1, pe2, 5, 3, True)
        models.PoolBout.create(pe1, pe3, 5, 2, True)
        models.PoolBout.create(pe1, pe4, 3, 5, False)
        models.PoolBout.create(pe2, pe3, 5, 1, True)
        models.PoolBout.create(pe2, pe4, 1, 5, False)
        models.PoolBout.create(pe3, pe4, 1, 5, False)

        # Round 3
        p = models.Pool.objects.get(stage=self.ps3)
        pe1 = models.PoolEntry.objects.create(entry=self.f4.entry_set.first(), pool=p, number=1)
        pe2 = models.PoolEntry.objects.create(entry=self.f3.entry_set.first(), pool=p, number=2)
        pe3 = models.PoolEntry.objects.create(entry=self.f2.entry_set.first(), pool=p, number=3)
        pe4 = models.PoolEntry.objects.create(entry=self.f1.entry_set.first(), pool=p, number=4)

        models.PoolBout.create(pe1, pe2, 4, 5, False)
        models.PoolBout.create(pe1, pe3, 5, 2, True)
        models.PoolBout.create(pe1, pe4, 2, 5, False)
        models.PoolBout.create(pe2, pe3, 5, 4, True)
        models.PoolBout.create(pe2, pe4, 1, 5, False)
        models.PoolBout.create(pe3, pe4, 1, 5, False)

        self.s4 = models.Stage.objects.create(type=models.Stage.DE, competition=self.comp, data={}, number=4)
        self.de = models.DeStage.objects.create(stage=self.s4, fight_down_to=4)
        self.de.create_seeds()
        de_table = models.DeTable.objects.create(de=self.de, parent=None)

        models.DeTableEntry.objects.create(table=de_table, entry=self.f1.entry_set.first(), victory=True, score=15,
                                           table_pos=0)
        models.DeTableEntry.objects.create(table=de_table, entry=self.f2.entry_set.first(), victory=False, score=5,
                                           table_pos=1)
        models.DeTableEntry.objects.create(table=de_table, entry=self.f4.entry_set.first(), victory=False, score=5,
                                           table_pos=2)
        models.DeTableEntry.objects.create(table=de_table, entry=self.f3.entry_set.first(), victory=True, score=15,
                                           table_pos=3)

        de_table_w = models.DeTable.objects.create(de=self.de, parent=de_table, winners=True)
        de_table_l = models.DeTable.objects.create(de=self.de, parent=de_table, winners=False)

        models.DeTableEntry.objects.create(table=de_table_w, entry=self.f1.entry_set.first(), victory=True, score=15,
                                           table_pos=0)
        models.DeTableEntry.objects.create(table=de_table_w, entry=self.f3.entry_set.first(), victory=False, score=0,
                                           table_pos=1)

        models.DeTableEntry.objects.create(table=de_table_l, entry=self.f2.entry_set.first(), victory=False, score=5,
                                           table_pos=0)
        models.DeTableEntry.objects.create(table=de_table_l, entry=self.f4.entry_set.first(), victory=True, score=15,
                                           table_pos=1)
