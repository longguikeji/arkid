
from app.models import App

class ServiceProvider():
    # Identification
    entity_id = ""
    pretty_name = models.CharField(verbose_name='Pretty Name', blank=True, max_length=255, help_text='For display purposes, can be empty')
    description = models.TextField(verbose_name='Description', blank=True)

    # Metadata
    metadata_expiration_dt = models.DateTimeField(verbose_name='Metadata valid until')
    remote_metadata_url = models.CharField(verbose_name='Remote metadata URL', max_length=512, blank=True, help_text='If set, metadata will be fetched upon saving into the local metadata xml field, and automatically be refreshed after the expiration timestamp.')
    local_metadata = models.TextField(verbose_name='Local Metadata XML', blank=True, help_text='XML containing the metadata')

    def __init__(self,tenant_uuid,sp_entity_id) -> None:
        apps = App.active_objects.filter(tenant_uuid=tenant_uuid).all()
        # TODO 此处可能会引发BUG： 当同一sp在当前租户被配置多次时  仅有第一次能正确起效
        for item in apps:
            if item.data["entity_id"] == sp_entity_id:
                self.entity_id = sp_entity_id
                self.metadata = item.data["metadata"]
                break

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_db_values = dict(zip(field_names, values))
        return instance

    def field_value_changed(self, field_name: str) -> bool:
        ''' Returns whether the current value of a field is changed vs what was loaded from the db. '''
        current_value = getattr(self, field_name)
        return current_value != getattr(self, '_loaded_db_values', {}).get(field_name, current_value)

    def _should_refresh(self) -> bool:
        ''' Returns whether or not a refresh operation is necessary.
        '''
        # - Data was not fetched ever before, so local_metadata is empty, or local_metadata has been changed from what it was in the db before
        if not self.local_metadata or self.field_value_changed('local_metadata'):
            return True
        # - The remote url has been updated
        if self.field_value_changed('remote_metadata_url'):
            return True
        # - The expiration timestamp is not set, or it is expired
        if not self.metadata_expiration_dt or now() > self.metadata_expiration_dt:
            return True

        return False

    def _refresh_from_remote(self) -> bool:
        try:
            self.local_metadata = validate_metadata(fetch_metadata(self.remote_metadata_url))
            self.metadata_expiration_dt = extract_validuntil_from_metadata(self.local_metadata)
            # Return True if it is now valid, False (+ log an error) otherwise
            if now() > self.metadata_expiration_dt:
                raise ValidationError(f'Remote metadata for SP {self.entity_id} was refreshed, but contains an expired validity datetime.')
            return True
        except Exception as e:
            raise ValidationError(f'Metadata for SP {self.entity_id} could not be pulled from remote url {self.remote_metadata_url}.') from e

    def _refresh_from_local(self) -> bool:
        try:
            # Try to extract a valid expiration datetime from the local metadata
            self.metadata_expiration_dt = extract_validuntil_from_metadata(self.local_metadata)
            # Return True if it is now valid, False (+ log an error) otherwise
            if now() > self.metadata_expiration_dt:
                raise ValidationError(f'Local metadata for SP {self.entity_id} contains an expired validity datetime or none at all, no remote metadata found to refresh.')
            return True
        except Exception as e:
            # Could not extract a valid expiry timestamp, return False (+ log an error)
            raise ValidationError(f'Metadata expiration dt for SP {self.entity_id} could not be extracted from local metadata.') from e

    def refresh_metadata(self, force_refresh: bool = False) -> bool:
        ''' If a remote metadata url is set, fetch new metadata if the locally cached one is expired. Returns True if new metadata was set.
            Sets metadata fields on instance, but does not save to db. If force_refresh = True, the metadata will be refreshed regardless of the currently cached version validity timestamp.
        '''
        if not self._should_refresh() and not force_refresh:
            return False

        if not self.remote_metadata_url and not self.local_metadata:
            logger.error(f'Local metadata for SP {self.entity_id} is not present, and no remote metadata found to refresh.')
            return False

        if self.remote_metadata_url:
            try:
                return self._refresh_from_remote()
            except ValidationError as e:
                logger.error('Unable to refresh remote metadata', extra={'exception': str(e)})
                return False

        if force_refresh or (not self.metadata_expiration_dt) or (now() > self.metadata_expiration_dt) or self.field_value_changed('local_metadata'):
            try:
                return self._refresh_from_local()
            except ValidationError as e:
                logger.error('Unable to refresh local metadata', extra={'exception': str(e)})
                return False

        raise Exception('Uncaught case of refresh_metadata')

    # Configuration
    active = models.BooleanField(verbose_name='Active', default=True)
    _processor = models.CharField(verbose_name='Processor', max_length=256, help_text='Import string for the (access) Processor to use.', default=get_default_processor)
    _attribute_mapping = models.TextField(verbose_name='Attribute mapping', default=get_default_attribute_mapping, help_text='dict with the mapping from django attributes to saml attributes in the identity.')

    _nameid_field = models.CharField(verbose_name='NameID Field', blank=True, max_length=64, help_text='Attribute on the user to use as identifier during the NameID construction. Can be a callable. If not set, this will default to settings.SAML_IDP_DJANGO_USERNAME_FIELD; if that is not set, it will use the `USERNAME_FIELD` attribute on the active user model.')

    _sign_response = models.BooleanField(verbose_name='Sign response', blank=True, null=True, help_text='If not set, default to the "sign_response" setting of the IDP. If that one is not set, default to False.')
    _sign_assertion = models.BooleanField(verbose_name='Sign assertion', blank=True, null=True, help_text='If not set, default to the "sign_assertion" setting of the IDP. If that one is not set, default to False.')

    _signing_algorithm = models.CharField(verbose_name='Signing algorithm', blank=True, null=True, max_length=256, choices=[(constant, pretty) for (pretty, constant) in xmldsig.SIG_ALLOWED_ALG], help_text='If not set, use settings.SAML_AUTHN_SIGN_ALG.')
    _digest_algorithm = models.CharField(verbose_name='Digest algorithm', blank=True, null=True, max_length=256, choices=[(constant, pretty) for (pretty, constant) in xmldsig.DIGEST_ALLOWED_ALG], help_text='If not set, default to settings.SAML_AUTHN_DIGEST_ALG.')

    _encrypt_saml_responses = models.BooleanField(verbose_name='Encrypt SAML Response', null=True, help_text='If not set, default to settings.SAML_ENCRYPT_AUTHN_RESPONSE. If that one is not set, default to False.')

    class Meta:
        verbose_name = "Service Provider"
        verbose_name_plural = "Service Providers"
        indexes = [
            models.Index(fields=['entity_id', ]),
        ]

    def __str__(self):
        if self.pretty_name:
            return f'{self.pretty_name} ({self.entity_id})'
        return f'{self.entity_id}'

    def save(self, *args, **kwargs):
        if not self.metadata_expiration_dt:
            self.metadata_expiration_dt = extract_validuntil_from_metadata(self.local_metadata)
        super().save(*args, **kwargs)
        IDP.load(force_refresh=True)

    @property
    def attribute_mapping(self) -> Dict[str, str]:
        if not self._attribute_mapping:
            return DEFAULT_ATTRIBUTE_MAPPING
        return json.loads(self._attribute_mapping)

    @property
    def nameid_field(self) -> str:
        if self._nameid_field:
            return self._nameid_field
        if hasattr(settings, 'SAML_IDP_DJANGO_USERNAME_FIELD'):
            return settings.SAML_IDP_DJANGO_USERNAME_FIELD
        return getattr(User, 'USERNAME_FIELD', 'username')

    # Do checks on validity of processor string both on setting and getting, as the
    # codebase can change regardless of the objects persisted in the database.

    @cached_property
    def processor(self) -> "BaseProcessor":  # type: ignore
        from .processors import validate_processor_path, instantiate_processor
        processor_cls = validate_processor_path(self._processor)
        return instantiate_processor(processor_cls, self.entity_id)

    def metadata_path(self) -> str:
        """ Write the metadata content to a local file, so it can be used as 'local'-type metadata for pysaml2.
            Return the location of that file.
        """
        # On access, update the metadata if necessary
        refreshed_metadata = self.refresh_metadata()
        if refreshed_metadata:
            self.save()

        path = '/tmp/djangosaml2idp'
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except Exception as e:
                logger.error(f'Could not create temporary folder to store metadata at {path}: {e}')
                raise
        filename = f'{path}/{self.id}.xml'

        # Rewrite the file if it did not exist yet, or if the SP config was updated after having written the file previously.
        if not os.path.exists(filename) or refreshed_metadata or (self.dt_updated and self.dt_updated.replace(tzinfo=pytz.utc) > datetime.datetime.fromtimestamp(os.path.getmtime(filename)).replace(tzinfo=pytz.utc)):
            try:
                with open(filename, 'w') as f:
                    f.write(self.local_metadata)
            except Exception as e:
                logger.error(f'Could not write metadata to file {filename}: {e}')
                raise
        return filename

    @property
    def sign_response(self) -> bool:
        if self._sign_response is None:
            return getattr(IDP.load().config, "sign_response", False)
        return self._sign_response

    @property
    def sign_assertion(self) -> bool:
        if self._sign_assertion is None:
            return getattr(IDP.load().config, "sign_assertion", False)
        return self._sign_assertion

    @property
    def encrypt_saml_responses(self) -> bool:
        if self._encrypt_saml_responses is None:
            return getattr(settings, 'SAML_ENCRYPT_AUTHN_RESPONSE', False)
        return self._encrypt_saml_responses

    @property
    def signing_algorithm(self) -> str:
        if self._signing_algorithm is None:
            return getattr(settings, "SAML_AUTHN_SIGN_ALG", xmldsig.SIG_RSA_SHA256)
        return self._signing_algorithm

    @property
    def digest_algorithm(self) -> str:
        if self._digest_algorithm is None:
            return getattr(settings, "SAML_AUTHN_DIGEST_ALG", xmldsig.DIGEST_SHA256)
        return self._digest_algorithm

    @property
    def resulting_config(self) -> str:
        """ Actual values of the config / properties with the settings and defaults taken into account.
        """
        try:
            d = {
                'entity_id': self.entity_id,
                'attribute_mapping': self.attribute_mapping,
                'nameid_field': self.nameid_field,
                'sign_response': self.sign_response,
                'sign_assertion': self.sign_assertion,
                'encrypt_saml_responses': self.encrypt_saml_responses,
                'signing_algorithm': self.signing_algorithm,
                'digest_algorithm': self.digest_algorithm,
            }
            config_as_str = json.dumps(d, indent=4)
        except Exception as e:
            config_as_str = f'Could not render config: {e}'
        # Some ugly replacements to have the json decently printed in the admin
        return mark_safe(config_as_str.replace("\n", "<br>").replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"))

