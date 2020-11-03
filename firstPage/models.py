from django.db import models

# Create your models here.

class rankings(models.Model):
	rank_date = models.CharField(max_length=100)
	rank = models.IntegerField()
	country_full = models.CharField(max_length=100)
	country_abrv = models.CharField(max_length=20)
	cur_year_avg_weighted = models.FloatField()
	two_year_ago_weighted = models.FloatField()
	three_year_ago_weighted = models.FloatField()
