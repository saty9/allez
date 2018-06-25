from main import models
from django.utils import timezone

class testCase:
    def setup(self):
        self.org = models.Organisation(address=None, name='f4sf', email='a@b.com', contactNumber='07990624284')
        self.org.save()
        self.structure = models.CompetitionStructure(name='YDS default')
        self.comp = models.Competition(organisation=self.org, date=timezone.now().date())
