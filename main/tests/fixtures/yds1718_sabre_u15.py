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
        self.structure = models.CompetitionStructure(name='YDS default', stage1=self.s1)
        self.structure.save()
        self.comp = models.Competition(organisation=self.org, date=timezone.now().date(), structure=self.structure)
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
                sm = models.StageMember(competitor=e, stage=stage, data={})
                sm.save()
        sm = self.f1.entry_set.first().stagemember_set.first()
        sm.data = {models.StageMember.INDEX_POOL_NUMBER: 1,
                   models.StageMember.INDEX_POOL_POSITION: 1,
                   models.StageMember.INDEX_POINTS: [0, 5, 5, 5],
                   models.StageMember.INDEX_VICTORIES: [False, True, True, True]}
        sm.save()
        sm = self.f2.entry_set.first().stagemember_set.first()
        sm.data = {models.StageMember.INDEX_POOL_NUMBER: 1,
                   models.StageMember.INDEX_POOL_POSITION: 2,
                   models.StageMember.INDEX_POINTS: [1, 0, 1, 2],
                   models.StageMember.INDEX_VICTORIES: [False, False, False, False]}
        sm.save()
        sm = self.f3.entry_set.first().stagemember_set.first()
        sm.data = {models.StageMember.INDEX_POOL_NUMBER: 1,
                   models.StageMember.INDEX_POOL_POSITION: 3,
                   models.StageMember.INDEX_POINTS: [1, 5, 0, 5],
                   models.StageMember.INDEX_VICTORIES: [False, True, False, True]}
        sm.save()
        sm = self.f4.entry_set.first().stagemember_set.first()
        sm.data = {models.StageMember.INDEX_POOL_NUMBER: 1,
                   models.StageMember.INDEX_POOL_POSITION: 4,
                   models.StageMember.INDEX_POINTS: [0, 5, 1, 0],
                   models.StageMember.INDEX_VICTORIES: [False, True, False, False]}
        sm.save()



