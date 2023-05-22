from django.db import models

class Transaction(models.Model):
	user_email = models.EmailField(max_length=255)
	reference = models.CharField(max_length=255, unique=True, primary_key=True)
	date = models.DateField()
	amount = models.IntegerField()
	type = models.CharField(max_length=255, choices=(('inflow', 'inflow'), ('outflow', 'outflow')))
	category = models.CharField(max_length=255)

	def __str__(self):
		return self.reference
