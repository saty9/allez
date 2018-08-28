from django.db import models
from . import Organisation, Club


class Competition(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.TextField()

    def add_entry(self, license_number, name, club_name):
        """Add an entry to a competition by either finding or creating a competitor

        :param str license_number: license number of the competitor to add
        :param str name: name of the competitor to add
        :param str club_name: name of the club to enter this competitor under
        :return: the created entry
        :rtype: main.models.Entry
        """
        org_competitors = self.organisation.competitor_set
        query = org_competitors.filter(license_number=license_number)
        if query.exists():
            competitor = query.first()
        else:
            competitor = org_competitors.create(name=name, license_number=license_number)
        club = Club.objects.filter(name=club_name)
        if club.exists():
            club = club.first()
        else:
            simple_club_name = Club.simplify_name(club_name)
            club = Club.objects.filter(name__icontains=simple_club_name)
            if club.exists():
                club = club.first()
            else:
                club = Club.objects.create(name=club_name)
        return self.entry_set.get_or_create(competitor=competitor, club=club)[0]
