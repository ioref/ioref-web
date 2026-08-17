from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user, defined at project start because it cannot be added later.

    Deliberately the same shape as ioref-inventory's `accounts.User`. The two
    applications have separate databases and separate user tables, with no
    shared session and no cross-application login, but the same person signs
    into both with the same eppn, so an account here and an account there should
    agree on what identifies them.

    `username` holds the eduPersonPrincipalName (`user@andrew.cmu.edu` at CMU)
    rather than a bare Andrew ID. eppn is unique across the federation where
    a bare username is unique only within one institution, and it maps directly
    onto Entra's UPN when that migration happens. Django's default username
    validator already permits `@`, so this needs no field override.

    `subject_id` holds an opaque, permanent identifier from the IdP when one is
    released (eduPersonUniqueId, or the SAML persistent NameID). eppn may be
    reassigned after a person leaves, so matching on it alone would eventually
    hand a new person an old account's history, which here includes authorship
    of every page they ever edited.

    Optional by design: not every deployment's IdP releases such an attribute,
    and the app degrades to matching on eppn alone.
    """

    subject_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text="Opaque permanent identifier from the identity provider.",
    )
    idp = models.CharField(
        max_length=50,
        blank=True,
        help_text="Which AUTH_MODE provisioned this account.",
    )

    def __str__(self):
        return self.get_full_name() or self.username
