from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist


class FollowRequestService:
    def __init__(self, page, f_pk=None, is_confirmed=True):
        self.page = page
        self.f_pk = f_pk
        self.is_confirmed = is_confirmed

    def validate(self):
        if self.is_confirmed == None:
            self.is_confirmed = True
        elif self.is_confirmed.lower() == "true":
            self.is_confirmed = True
        elif self.is_confirmed.lower() == "false":
            self.is_confirmed = False
        else:
            raise exceptions.ValidationError(
                detail={"is_confirmed": ["should equal False or True"]}
            )

    def is_private_page(self):
        "check if follow request even needed"
        if not self.page.is_private:
            msg = "Your page is not private. Follow requests are not needed."
            raise exceptions.APIException(msg)

    def get_user_from_follow_request(self):
        "returns User() object from follow request with f_pk id"
        try:
            user = self.page.follow_requests.get(id=self.f_pk)
            return user
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Follow Request with such id not found")

    def update_follow_requests(self):
        if self.f_pk:
            user = self.get_user_from_follow_request()
            self.page.follow_requests.remove(user)
            if self.is_confirmed:
                self.page.followers.add(self.f_pk)
        else:
            users = self.page.follow_requests.all()
            for user in users:
                self.page.follow_requests.remove(user)
                if self.is_confirmed:
                    self.page.followers.add(user)

        self.page.save()

    def validate_and_add_follow_request(self, request):
        user = request.user
        if self.page.is_private and user in self.page.follow_requests.all():
            raise exceptions.APIException("You already asked to follow this page.")
        elif user in self.page.followers.all():
            raise exceptions.APIException("You already follow this page.")
        elif user == self.page.owner:
            raise exceptions.APIException("Owner cannot follow their own page")
        elif self.page.is_private:
            self.page.follow_requests.add(user)
        else:
            self.page.followers.add(user)
