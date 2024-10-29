from django.db import models

class NetworkCoverage(models.Model):
    operator = models.CharField(max_length=50)
    longitude = models.FloatField()
    latitude = models.FloatField()
    g2 = models.BooleanField(default=False)
    g3 = models.BooleanField(default=False)
    g4 = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Network Coverages"

    def __str__(self):
        return f"{self.operator} - {self.longitude}, {self.latitude}"
