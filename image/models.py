from django.db import models

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Image(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/')
    description = models.TextField()


class TrainingResult(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    training_accuracy = models.FloatField()
    training_loss = models.FloatField()
    training_time = models.DateTimeField(auto_now_add=True)