from django.db import models


class Constituency(models.Model):
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=200)
<<<<<<< HEAD
    boundary = models.MultiPolygonField()
=======
    boundary = models.TextField(blank=True)  # Temporarily store as JSON text instead of GIS field
>>>>>>> 93da3f46d34717aee5283fc5c58b966410a8be70
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Constituencies"


class MLA(models.Model):
    constituency = models.ForeignKey(
        Constituency, on_delete=models.CASCADE, related_name='mla'
    )
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=200)
    education = models.CharField(max_length=500, blank=True)
    term_start = models.IntegerField()
    term_end = models.IntegerField(null=True, blank=True)
    achievements_raw = models.TextField(blank=True)
    source_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.constituency.name})"


class MP(models.Model):
    constituency = models.ForeignKey(
        Constituency, on_delete=models.CASCADE, related_name='mp'
    )
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=200)
    lok_sabha_seat = models.CharField(max_length=200)
    term_start = models.IntegerField()
    term_end = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.lok_sabha_seat})"


class ElectionResult(models.Model):
    constituency = models.ForeignKey(
        Constituency, on_delete=models.CASCADE, related_name='results'
    )
    year = models.IntegerField()
    winner_name = models.CharField(max_length=200)
    winner_party = models.CharField(max_length=200)
    winner_votes = models.IntegerField()
    runner_up_name = models.CharField(max_length=200)
    runner_up_votes = models.IntegerField()
    total_votes = models.IntegerField()
    turnout_percent = models.FloatField()

    def __str__(self):
        return f"{self.constituency.name} {self.year}"
