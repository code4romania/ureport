from django import forms
from dash.categories.models import Category

from ureport.userbadges.models import BadgeType


class BadgeTypeForm(forms.ModelForm):

    class Meta:
        model = BadgeType
        fields = (
            "org", "title", "image", "is_active", 
            "validation_category", "validation_total",
            "unfinished_template", "finished_description",
        )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)

        # If the badge type belongs to an Org, then restrict the category choices to the same Org
        if instance and getattr(self, "org", None) and ("validation_category" in self.fields):
            self.fields["validation_category"].queryset = Category.objects.filter(org=instance.org)        
