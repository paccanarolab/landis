from django.db import models

# Create your models here.
class neighbourhood(models.Model):
    omim1 = models.CharField(max_length=10)
    omim2 = models.CharField(max_length=10)
    similarity = models.CharField(max_length=10)
    lca = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["omim1"], name="omim1_neigh_idx"),
            models.Index(fields=["omim2"], name="omim2_neigh_idx")
        ]


class similarityscores (models.Model):
    omim1 = models.CharField(max_length=10)
    omim2 = models.CharField(max_length=10)
    similarity = models.CharField(max_length=10)
    percentile = models.CharField(max_length=10)
    #lca = models.CharField(max_length=100)
    class Meta:
        indexes = [
            models.Index(fields=["omim1"], name="omim1_sim_idx"),
            models.Index(fields=["omim2"], name="omim2_sim_idx")
        ]

class mimtoprot(models.Model):
    omim = models.CharField(max_length=10)
    uniprot_id = models.CharField(max_length=10)

class ppi(models.Model):
    interactor_a = models.CharField(max_length=10)
    interactor_b = models.CharField(max_length=10)

class mesh(models.Model):
    omim = models.CharField(max_length=10)
    mesh_term = models.CharField(max_length=10)
    identifier = models.CharField(max_length=8)
    coordinates = models.CharField(max_length=300)
    #mesh_tree = modesl.CharField(max_length=100)


class omim_details(models.Model):
    omim = models.CharField(max_length=10)
    title = models.CharField(max_length=500)
    prefix = models.CharField(max_length=2)


class omim_names(models.Model):
    value = models.CharField(max_length=100)
    label = models.CharField(max_length=100)



# Create your models here.
