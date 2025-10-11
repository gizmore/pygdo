import base64
import hashlib
import hmac
from typing import Type

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Util import module_enabled, Arrays, dump, urlencode

from typing import TYPE_CHECKING

from gdo.base.util.href import href

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User


class WithPermissionCheck:

    CACHE: dict[Type['WithPermissionCheck'],dict['GDO_User',bool]] = {}

    def has_permission(self, user: 'GDO_User', display_error: bool = True) -> bool:
        if not (cached := self.CACHE.get(self.__class__)):
            self.CACHE[self.__class__] = cached = {}
        if cached.get(user):
            return True
        from gdo.core.GDO_Permission import GDO_Permission
        typestr = self.gdo_user_type()
        if typestr:
            types = typestr.split(',')
            type = user.get_user_type()
            if type not in types:
                return False if not display_error else self.err_type(types)
        perm = self.gdo_user_permission()
        if perm and not GDO_Permission().has_permission(user, perm):
            return False if not display_error else self.err_permission(perm)
        if not self.gdo_in_private() and not self._env_channel:
            return False if not display_error else self.err_not_in_private()
        if not self.gdo_in_channels() and self._env_channel is not None:
            return False if not display_error else self.err_not_in_channel()
        # if self.gdo_needs_authentication():
        #     if not user._authenticated:
        #         return False if not display_error else self.err_not_authenticated()
        if not self.gdo_has_permission(user):
            return False if not display_error else self.err_generic_permission()
        if not self.allows_connector():
            return False if not display_error else self.err_connector_not_supported()
        if self._env_channel and self._disabled_in_channel(self._env_channel):
            return False if not display_error else self.err_method_disabled()
        if self._disabled_in_server(self._env_server):
            return False if not display_error else self.err_method_disabled()
        cached[user] = True
        return True

    def _disabled_in_channel(self, channel: 'GDO_Channel') -> bool:
        return self._get_config_channel('disabled', channel).get_value()

    def _disabled_in_server(self, server: 'GDO_Server') -> bool:
        return self._get_config_server('disabled', server).get_value()

    def allows_connector(self) -> bool:
        connectors = self.gdo_connectors()
        if not connectors:
            return True
        connector = self._env_server.get_connector()
        return connector.get_name().lower() in connectors.split(',')

    def err_method_disabled(self):
        self.err('err_method_disabled')
        return False

    def err_connector_not_supported(self):
        self.err('err_method_connector_not_supported')
        return False

    def err_not_authenticated(self):
        self.err('err_not_authenticated')
        return False

    def err_not_in_private(self):
        self.err('err_not_in_private')
        return False

    def err_not_in_channel(self):
        self.err('err_not_in_channel')
        return False

    def err_type(self, types: list[str]) -> bool:
        if 'guest' in types:
            return self.err_type_guest_allowed()
        elif 'member' in types:
            return self.err_type_members_only()
        else:
            return self.err_type_not_allowed(types)

    def err_type_guest_allowed(self) -> bool:
        from gdo.register import module_register
        from gdo.ui.GDT_Link import GDT_Link
        if module_enabled('register') and module_register.instance().cfg_guest_signup():
            back_to = f"&_back_to={urlencode(Application.current_href())}"
            link1 = GDT_Link().text('link_login_before_continue').href(href('login', 'form', back_to)).render()
            link2 = GDT_Link().text('link_continue_as_guest').href(href('register', 'guest', back_to)).render()
            self.err('err_type_guest', (link1, link2))
            return False
        else:
            return self.err_type_members_only()

    def err_type_members_only(self):
        if module_enabled('login'):
            from gdo.ui.GDT_Link import GDT_Link
            back_to = f"&_back_to={urlencode(Application.current_href())}"
            link = GDT_Link().text('link_login_before_continue').href(href('login', 'form', back_to)).render()
            self.err('err_type_member', (link,))
            return False
        else:
            return self.err_type_not_allowed(['guest'])

    def err_type_not_allowed(self, types: list[str]):
        print_types = Arrays.human_join(types)
        self.err('err_type', (print_types,))
        return False

    def err_permission(self, perm: str):
        self.err('err_permission', (perm,))
        return False

    def err_generic_permission(self):
        self.err('err_permissions')
        return False

    ########
    # AUTH #
    ########
    def create_autologin_token(self, user_id: str = None, method_id: str = None, valid_for_hours: int = 120) -> str:
        from gdo.date.Time import Time
        user_id = user_id or self._env_user.get_id()
        method_id = method_id or self.get_method_id()
        valid_ts = str(int(Application.TIME + Time.ONE_HOUR * valid_for_hours))
        secret = Application.config('core.secret')
        data = f"{user_id}|{method_id}|{valid_ts}"
        sig = hmac.new(secret.encode(), data.encode(), hashlib.sha1).hexdigest()
        token = f"{data}|{sig}"
        return base64.urlsafe_b64encode(token.encode()).decode()

    def validate_auth_token(self, token: str) -> str:
        try:
            from gdo.core.GDO_Method import GDO_Method
            token = base64.urlsafe_b64decode(token).decode()
            parts = token.split('|')
            if len(parts) != 4: return ''
            user_id, token_method_id, valid_until_str, provided_sig = parts
            valid_until = int(valid_until_str)
            secret = Application.config('core.secret')
            my_id = GDO_Method.for_method(self).get_id()
            if token_method_id != my_id: return ''
            if valid_until < Application.TIME: return ''
            data = f"{user_id}|{my_id}|{valid_until}"
            expected_sig = hmac.new(secret.encode(), data.encode(), hashlib.sha1).hexdigest()
            if not hmac.compare_digest(expected_sig, provided_sig):
                return ''
            return user_id
        except Exception as ex:
            Logger.exception(ex, 'Cannot validate auth token.')
            return ''



