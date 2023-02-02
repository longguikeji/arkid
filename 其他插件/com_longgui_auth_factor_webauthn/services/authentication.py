from typing import List, Union
import json
from dataclasses import dataclass

from django.conf import settings
from webauthn import (
    generate_authentication_options,
    options_to_json,
    verify_authentication_response,
)
from webauthn.helpers import json_loads_base64url_to_bytes, base64url_to_bytes
from webauthn.helpers.structs import (
    PublicKeyCredentialRequestOptions,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
    AuthenticationCredential,
)

from .redis import RedisService
from ..schema import WebAuthnCredential
from ..exceptions import InvalidAuthenticationResponse
from arkid.extension.models import TenantExtensionConfig


@dataclass
class VerifiedAuthentication:
    """
    A custom version of py_webauthn's VerifiedAuthentication since it doesn't output username from
    the response
    """

    credential_id: bytes
    new_sign_count: int
    username: str


class AuthenticationService:
    redis: RedisService

    def __init__(self):
        self.redis = RedisService(db=3)

    def generate_authentication_options(
        self,
        *,
        config: TenantExtensionConfig,
        cache_key: str,
        require_user_verification: bool,
        existing_credentials: List[WebAuthnCredential],
    ) -> PublicKeyCredentialRequestOptions:
        """
        Generate and store authentication options
        """

        user_verification = UserVerificationRequirement.DISCOURAGED
        if require_user_verification:
            user_verification = UserVerificationRequirement.REQUIRED

        authentication_options = generate_authentication_options(
            rp_id=config.config.get('RP_ID', 'localhost'),
            user_verification=user_verification,
            allow_credentials=[
                PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(cred.id), transports=cred.transports
                )
                for cred in existing_credentials
            ],
        )

        self._save_options(cache_key=cache_key, options=authentication_options)

        return authentication_options

    def verify_authentication_response(
        self,
        *,
        config: TenantExtensionConfig,
        cache_key: str,
        existing_credential: WebAuthnCredential,
        response: dict,
    ) -> VerifiedAuthentication:
        credential = AuthenticationCredential.parse_raw(json.dumps(response))
        options = self._get_options(cache_key=cache_key)

        if not options:
            raise InvalidAuthenticationResponse(f"no options for user {cache_key}")

        require_user_verification = False
        if options.user_verification:
            require_user_verification = (
                options.user_verification == UserVerificationRequirement.REQUIRED
            )

        self._delete_options(cache_key=cache_key)

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=options.challenge,
            expected_rp_id=config.config.get('RP_ID', 'localhost'),
            expected_origin=config.config.get(
                'RP_EXPECTED_ORIGIN', 'http://localhost:9528'
            ),
            require_user_verification=require_user_verification,
            credential_public_key=base64url_to_bytes(existing_credential.public_key),
            credential_current_sign_count=existing_credential.sign_count,
        )

        confirmed_username = cache_key
        if credential.response.user_handle:
            # Use the username provided by the authenticator if present
            confirmed_username = credential.response.user_handle.decode("utf-8")

        return VerifiedAuthentication(
            credential_id=verification.credential_id,
            new_sign_count=verification.new_sign_count,
            username=confirmed_username,
        )

    def _save_options(
        self, *, cache_key: str, options: PublicKeyCredentialRequestOptions
    ):
        """
        Store authentication options for the user so we can reference them later
        """
        expiration = options.timeout
        if type(expiration) is int:
            # Store them temporarily, for twice as long as we're telling WebAuthn how long it
            # should give the user to complete the WebAuthn ceremony
            expiration = int(expiration / 1000 * 2)
        else:
            # Default to two minutes since we default timeout to 60 seconds
            expiration = 120

        return self.redis.store(
            key=cache_key, value=options_to_json(options), expiration_seconds=expiration
        )

    def _get_options(
        self, *, cache_key: str
    ) -> Union[PublicKeyCredentialRequestOptions, None]:
        """
        Attempt to retrieve saved authentication options for the user
        """
        options: str = self.redis.retrieve(key=cache_key)
        if options is None:
            return options

        # We can't use PublicKeyCredentialRequestOptions.parse_raw() because
        # json_loads_base64url_to_bytes() doesn't know to convert these few values to bytes, so we
        # have to do it manually
        options_json: dict = json_loads_base64url_to_bytes(options)
        options_json["challenge"] = base64url_to_bytes(options_json["challenge"])
        options_json["allowCredentials"] = [
            {**cred, "id": base64url_to_bytes(cred["id"])}
            for cred in options_json["allowCredentials"]
        ]

        return PublicKeyCredentialRequestOptions.parse_obj(options_json)

    def _delete_options(self, *, cache_key: str) -> int:
        return self.redis.delete(key=cache_key)
