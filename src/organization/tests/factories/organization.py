import factory
from faker import Faker

fake = Faker()


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "organization.Organization"

    title = factory.LazyFunction(lambda: fake.name())
    on_trial = False
