import factory
from conftest import UserFactory
from resources.models import Resource


class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resource

    title = factory.Faker("sentence", nb_words=5)
    owner = factory.SubFactory(UserFactory)
