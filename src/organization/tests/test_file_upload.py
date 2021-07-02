import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from organization.tests.factories.organization import OrganizationFactory


def get_image_content():
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
    )


class AvatarUploadTests(TestCase):
    def setUp(self):
        self.organization = OrganizationFactory.create()

    def test_image_upload(self):
        url = reverse("orga_avatar_image_upload", kwargs={"pk": self.organization.pk})
        image = SimpleUploadedFile(name="avatar.jpg", content=get_image_content(), content_type="image/jpeg")
        post_data = {"avatar_image": image}
        response = self.client.post(url, data=post_data)
        self.assertEquals(response.status_code, 200)
        self.organization.refresh_from_db()
        self.assertTrue(self.organization.avatar_image)
