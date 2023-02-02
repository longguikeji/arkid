import json
from typing import Union, List, Optional

from django.conf import settings
from webauthn import (
    generate_registration_options,
    options_to_json,
    verify_registration_response,
)
from webauthn.helpers import json_loads_base64url_to_bytes, base64url_to_bytes
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    RegistrationCredential,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    COSEAlgorithmIdentifier,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
)

from .redis import RedisService
from ..exceptions import InvalidRegistrationSession
from ..schema import WebAuthnCredential
from arkid.extension.models import TenantExtensionConfig


class RegistrationService:
    redis: RedisService

    def __init__(self):
        self.redis = RedisService(db=2)

    def generate_registration_options(
        self,
        *,
        config: TenantExtensionConfig,
        username: str,
        attestation: str,
        attachment: str,
        require_user_verification: bool,
        algorithms: List[str],
        existing_credentials: List[WebAuthnCredential],
    ):
        _attestation = AttestationConveyancePreference.NONE

        if attestation == "direct":
            _attestation = AttestationConveyancePreference.DIRECT

        authenticator_selection = AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.DISCOURAGED,
            resident_key=ResidentKeyRequirement.PREFERRED,
        )
        if attachment != "all":
            authenticator_attachment = AuthenticatorAttachment.CROSS_PLATFORM
            if attachment == "platform":
                authenticator_attachment = AuthenticatorAttachment.PLATFORM

            authenticator_selection.authenticator_attachment = authenticator_attachment

        if require_user_verification:
            authenticator_selection.user_verification = (
                UserVerificationRequirement.REQUIRED
            )

        supported_pub_key_algs: Optional[List[COSEAlgorithmIdentifier]] = None
        if len(algorithms) > 0:
            supported_pub_key_algs = []

            if "es256" in algorithms:
                supported_pub_key_algs.append(COSEAlgorithmIdentifier.ECDSA_SHA_256)

            if "rs256" in algorithms:
                supported_pub_key_algs.append(
                    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256
                )

        registration_options = generate_registration_options(
            rp_id=config.config.get('RP_ID', 'localhost'),
            rp_name=config.config.get('RP_NAME', 'ArkID'),
            user_id=username,
            user_name=username,
            attestation=_attestation,
            authenticator_selection=authenticator_selection,
            supported_pub_key_algs=supported_pub_key_algs,
            exclude_credentials=[
                PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(cred.id), transports=cred.transports
                )
                for cred in existing_credentials
            ],
        )

        # py_webauthn will default to all supported algorithms on an empty `algorithms` list
        # so clear it manually so we can test out that scenario
        if len(algorithms) == 0:
            registration_options.pub_key_cred_params = []

        self._save_options(username=username, options=registration_options)

        return registration_options

    def verify_registration_response(
        self, *, config: TenantExtensionConfig, username: str, response: dict
    ):
        credential = RegistrationCredential.parse_raw(json.dumps(response))
        options = self._get_options(username=username)

        if not options:
            raise InvalidRegistrationSession(f"no options for user {username}")

        require_user_verification = False
        if options.authenticator_selection:
            require_user_verification = (
                options.authenticator_selection.user_verification
                == UserVerificationRequirement.REQUIRED
            )

        self._delete_options(username=username)

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=options.challenge,
            expected_rp_id=config.config.get('RP_ID', 'localhost'),
            expected_origin=config.config.get(
                'RP_EXPECTED_ORIGIN', 'http://localhost:9528'
            ),
            require_user_verification=require_user_verification,
        )

        return verification

    def _save_options(self, username: str, options: PublicKeyCredentialCreationOptions):
        """
        Store registration options for the user so we can reference them later
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
            key=username, value=options_to_json(options), expiration_seconds=expiration
        )

    def _get_options(
        self, username: str
    ) -> Union[PublicKeyCredentialCreationOptions, None]:
        """
        Attempt to retrieve saved registration options for the user
        """
        options: str = self.redis.retrieve(key=username)
        if options is None:
            return options

        # We can't use PublicKeyCredentialCreationOptions.parse_raw() because
        # json_loads_base64url_to_bytes() doesn't know to convert these few values to bytes, so we
        # have to do it manually
        options_json: dict = json_loads_base64url_to_bytes(options)
        options_json["user"]["id"] = base64url_to_bytes(options_json["user"]["id"])
        options_json["challenge"] = base64url_to_bytes(options_json["challenge"])
        options_json["excludeCredentials"] = [
            {**cred, "id": base64url_to_bytes(cred["id"])}
            for cred in options_json["excludeCredentials"]
        ]

        return PublicKeyCredentialCreationOptions.parse_obj(options_json)

    def _delete_options(self, username: str) -> int:
        return self.redis.delete(key=username)
