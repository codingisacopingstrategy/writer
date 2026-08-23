from tastypie.authentication import Authentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.exceptions import Unauthorized


PUBLISH_PERM = 'write.publish_mtentry'
DELETE_ENTRY_PERM = 'write.delete_mtentry'


def can_publish(user):
    return bool(user and user.is_authenticated and user.has_perm(PUBLISH_PERM))


def can_delete_entry(user):
    return bool(user and user.is_authenticated and user.has_perm(DELETE_ENTRY_PERM))


class LoggedInAuthentication(Authentication):
    """Session cookie is enough. Tastypie views are csrf_exempt; the editor
    fetch() does not send X-CSRFToken, so stock SessionAuthentication would
    401 every save.
    """

    def is_authenticated(self, request, **kwargs):
        return bool(getattr(request, 'user', None) and request.user.is_authenticated)

    def get_identifier(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return user.get_username()
        return 'anonymous'


class LoggedInAuthorization(Authorization):
    """Any logged-in user may read and write. Anonymous is out."""

    def _require_user(self, bundle):
        user = getattr(bundle.request, 'user', None)
        if not user or not user.is_authenticated:
            raise Unauthorized("Login required.")

    def read_list(self, object_list, bundle):
        self._require_user(bundle)
        return object_list

    def read_detail(self, object_list, bundle):
        self._require_user(bundle)
        return True

    def create_list(self, object_list, bundle):
        self._require_user(bundle)
        return object_list

    def create_detail(self, object_list, bundle):
        self._require_user(bundle)
        return True

    def update_list(self, object_list, bundle):
        self._require_user(bundle)
        return object_list

    def update_detail(self, object_list, bundle):
        self._require_user(bundle)
        return True

    def delete_list(self, object_list, bundle):
        self._require_user(bundle)
        return object_list

    def delete_detail(self, object_list, bundle):
        self._require_user(bundle)
        return True


class EntryAuthorization(DjangoAuthorization):
    """add / change / delete on MtEntry, plus publish_mtentry for the flag."""


class AuthorAuthorization(LoggedInAuthorization):
    """The author list is for the editor dropdown. Creating or deleting
    users is blocked. Update is allowed because Tastypie re-saves the
    related User on every entry PATCH (hydrate_author sends ``{'pk': …}``).
    """

    def create_detail(self, object_list, bundle):
        raise Unauthorized("You cannot create users through the API.")

    def delete_list(self, object_list, bundle):
        self._require_user(bundle)
        return object_list.none()

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("You cannot delete users through the API.")
