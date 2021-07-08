from .AccessMixin import AccessMixin


class UserPassesTestMixin(AccessMixin):
    """
    Deny a request with a permission error if the test_func() method returns
    False.
    """

    def test_func(self):
        raise NotImplementedError(
            '{} is missing the implementation of the test_func() method.'.format(self.__class__.__name__)
        )

    def get_test_func(self):
        """
        Override this method to use a different test_func method.
        """
        return self.test_func

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)