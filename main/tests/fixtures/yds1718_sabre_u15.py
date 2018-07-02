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
        self.comp = models.Competition(organisation=self.org, date=timezone.now().date())
        self.comp.save()
        self.s1 = models.Stage(type=models.Stage.POOL, data={}, competition=self.comp, number=1)
        self.s1.save()
        self.s2 = models.Stage(type=models.Stage.POOL, data={}, competition=self.comp, number=2)
        self.s2.save()
        self.s3 = models.Stage(type=models.Stage.POOL, data={}, competition=self.comp, number=3)
        self.s3.save()
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
        for stage in [self.s1, self.s2, self.s3]:
            p = models.Pool(stage=stage, number=1)
            p.save()

        # Round 1
        p = models.Pool.objects.filter(stage=self.s1).first()
        pe1 = models.PoolEntry.objects.create(fencer=self.f1.entry_set.first(), pool=p, number=1)
        pe2 = models.PoolEntry.objects.create(fencer=self.f2.entry_set.first(), pool=p, number=2)
        pe3 = models.PoolEntry.objects.create(fencer=self.f3.entry_set.first(), pool=p, number=3)
        pe4 = models.PoolEntry.objects.create(fencer=self.f4.entry_set.first(), pool=p, number=4)

        models.PoolBout.create(pe1, pe2, 5, 1, True)
        models.PoolBout.create(pe1, pe3, 5, 1, True)
        models.PoolBout.create(pe1, pe4, 5, 0, True)
        models.PoolBout.create(pe2, pe3, 1, 5, False)
        models.PoolBout.create(pe2, pe4, 2, 5, False)
        models.PoolBout.create(pe3, pe4, 5, 1, True)






