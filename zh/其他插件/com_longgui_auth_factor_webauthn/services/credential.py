from typing import List, Optional
import json

from webauthn.registration.verify_registration_response import VerifiedRegistration
from webauthn.helpers import bytes_to_base64url

from .redis import RedisService
from .authentication import VerifiedAuthentication
from ..schema import WebAuthnCredential
from ..exceptions import InvalidCredentialID
from ..helpers import transports_to_ui_string
from ..models import UserWebauthnCredential
from arkid.common.logger import logger
from arkid.core.models import User


class CredentialService:
    """
    WebAuthn credential management
    """

    redis: RedisService

    def __init__(self) -> None:
        self.redis = RedisService(db=2)

    def store_credential(
        self,
        *,
        user: User,
        username: str,
        verification: VerifiedRegistration,
        is_discoverable_credential: bool,
        transports: Optional[List[str]] = None,
    ) -> WebAuthnCredential:
        """
        Temporarily store a new credential in Redis so we can leverage its record expiration to
        remove credentials after a certain number of hours

        The Redis key will be the base64url-encoded credential ID
        """
        new_credential = WebAuthnCredential(
            username=username,
            id=bytes_to_base64url(verification.credential_id),
            public_key=bytes_to_base64url(verification.credential_public_key),
            sign_count=verification.sign_count,
            transports=transports,
            is_discoverable_credential=is_discoverable_credential,
            device_type=verification.credential_device_type,
            backed_up=verification.credential_backed_up,
        )

        self._temporarily_store_in_db(user, new_credential)

        transports_str = transports_to_ui_string(transports or [])
        cred_type = (
            "discoverable credential" if is_discoverable_credential else "credential"
        )

        logger.info(
            f'User "{username}" registered a {cred_type} with transports {transports_str}'
        )

        return new_credential

    def retrieve_credential_by_id(
        self,
        *,
        credential_id: str,
        username: Optional[str] = None,
    ) -> WebAuthnCredential:
        """
        Retrieve a credential from Redis

        Raises `homepage.exceptions.InvalidCredentialID` if the given credential ID is invalid
        """
        # raw_credential: str | None = self.redis.retrieve(key=credential_id)
        db_credential = UserWebauthnCredential.active_objects.filter(
            credential_id=credential_id
        ).first()

        if not db_credential:
            raise InvalidCredentialID("Unrecognized credential ID")

        credential = WebAuthnCredential.parse_obj(db_credential.credential)

        if username and db_credential.user.username != username:
            raise InvalidCredentialID("Credential does not belong to user")

        return credential

    def retrieve_credentials_by_username(
        self, *, username: str
    ) -> List[WebAuthnCredential]:
        """
        Get all credentials for a given user
        """
        # all = self.redis.retrieve_all()
        # credentials = [
        #     WebAuthnCredential.parse_raw(cred) for cred in self.redis.retrieve_all()
        # ]
        user = User.active_objects.filter(username=username).first()
        if not user:
            return []
        credentials = user.webauthn_credential_set.all()
        return [WebAuthnCredential.parse_obj(cred.credential) for cred in credentials]

    def update_credential_sign_count(
        self, *, verification: VerifiedAuthentication
    ) -> None:
        """
        Update a credential's number of times it's been used

        Raises `homepage.exceptions.InvalidCredentialID` if the given credential ID is invalid
        """
        credential_id = bytes_to_base64url(verification.credential_id)
        # raw_credential: str | None = self.redis.retrieve(key=credential_id)
        db_credential = UserWebauthnCredential.active_objects.filter(
            credential_id=credential_id
        ).first()

        if not db_credential:
            raise InvalidCredentialID()

        credential = WebAuthnCredential.parse_obj(db_credential.credential)

        credential.sign_count = verification.new_sign_count

        db_credential.credential = credential.dict()
        db_credential.save()
        # self._temporarily_store_in_db(db_credential.user, credential)

    def _temporarily_store_in_db(
        self, user: User, credential: WebAuthnCredential
    ) -> None:
        """
        We only ever want to save credentials for a finite period of time
        """
        # self.redis.store(
        #     key=credential.id,
        #     value=json.dumps(credential.dict()),
        #     expiration_seconds=60 * 60 * 24,  # 24 hours
        # )
        cred_obj = UserWebauthnCredential()
        cred_obj.user = user
        cred_obj.credential_id = credential.id
        cred_obj.credential = credential.dict()
        cred_obj.save()
