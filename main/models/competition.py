from django.db import models
from . import Organisation, Club


class Competition(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.TextField()

    def add_entry(self, license_number, name, club_name, seed=None):
        """Add an entry to a competition by either finding or creating a competitor
        If an entry already exists will update its club and seed

        :param str license_number: license number of the competitor to add
        :param str name: name of the competitor to add
        :param str club_name: name of the club to enter this competitor under
        :param optional int seed: seed to add the entry with
        :return: the created entry
        :rtype: main.models.Entry
        """
        if seed is None:
            seed = 999
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
        entry = self.entry_set.get_or_create(competitor=competitor)[0]
        entry.club = club
        entry.seed = seed
        entry.save()
        return entry

    def __str__(self):
        return self.name
