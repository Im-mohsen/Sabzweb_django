from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from django.urls import reverse
from django_resized import ResizedImageField
# from datetime import date
from django.template.defaultfilters import slugify


# Managers


class PublishManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


# Create your models here.


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Publish'
        REJECTED = 'RJ', 'Rejected'

    CATEGORY_CHOICES = (
        ('تکنولوژی','تکنولوژی'),
        ('زبان برنامه نویسی','زبان برنامه نویسی'),
        ('هوش مصنوعی','هوش مصنوعی'),
        ('بلاکچین','بلاکچین'),
        ('سایر','سایر')
    )

    # Relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    # Data fields
    title = models.CharField(max_length=250, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    slug = models.SlugField(max_length=250)
    # Date
    publish = jmodels.jDateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")
    reading_time = models.PositiveIntegerField(verbose_name="زمان مطالعه")
    # Choice fields
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name="وضعیت")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="دسته بندی", default='سایر')
    # Default manager
    # objects = models.Manager()
    objects = jmodels.jManager()
    # Personal manager
    published = PublishManager()

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=['-publish'])
        ]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.id])

    def save(self, *args,  **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # way number 2 for delete image with posts

    # def delete(self, *args, **kwargs):
    #     for img in self.images.all():
    #         storage, path = img.img_file.storage, img.img_file.path
    #         storage.delete(path)
    #     super().delete(*args, **kwargs)


class Ticket(models.Model):
    message = models.TextField(verbose_name="پیام")
    name = models.CharField(max_length=250, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    subject = models.CharField(max_length=250, verbose_name="موضوع")

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت ها"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    name = models.CharField(max_length=250, verbose_name="نام")
    body = models.TextField(verbose_name="متن کامنت")
    email = models.EmailField(max_length=250, verbose_name="ایمیل")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")
    active = models.BooleanField(default=False, verbose_name="وضعیت")

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=['created'])
        ]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

    def __str__(self):
        return f"{self.name}: {self.post}"


# def date_directory_path(instance, filename):
#     today = date.today().strftime("%B %d, %Y")
#     return f"post_images/{today}/{filename}"


def user_directory_path(instance, filename):
    user = instance.post.author.username
    return f"post_images/{user}/{filename}"


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images", verbose_name="پست")
    # image_file = ResizedImageField(upload_to=date_directory_path, size=[600, 340], quality=80,
    #                                crop=['middle', 'center'], null=True, blank=True)
    image_file = ResizedImageField(upload_to=user_directory_path, size=[600, 340], quality=80,
                                   crop=['middle', 'center'], null=True, blank=True)
    title = models.CharField(max_length=250, verbose_name="عنوان", null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=['created'])
        ]
        verbose_name = "تصویر"
        verbose_name_plural = "تصویر ها"

    def __str__(self):
        return f"title: {self.title}" if self.title else f"image_name: {self.image_file}"

    # def delete(self, *args, **kwargs):
    #     storage, path = self.image_file.storage, self.image_file.path
    #     storage.delete(path)
    #     super().delete(*args, **kwargs)


class Account(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    date_of_birth = jmodels.jDateField(verbose_name="تاریخ تولد", blank=True, null=True)
    bio = models.TextField(verbose_name="بایو", blank=True, null=True)
    photo = ResizedImageField(upload_to="account_image/", size=[500, 500], quality=60, crop=['middle', 'center'],
                              null=True, blank=True, verbose_name="تصویر پروفایل")
    job = models.CharField(max_length=250, verbose_name="شغل", blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "اکانت"
        verbose_name_plural = "اکانت ها"
