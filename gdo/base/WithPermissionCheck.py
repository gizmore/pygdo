from gdo.base.Application import Application
from gdo.base.Util import module_enabled, href, Arrays, dump, urlencode


class WithPermissionCheck:

    def has_permission(self, user, display_error: bool = True) -> bool:
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
        return True

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
            self.err('err_type_guest', [link1, link2])
            return False
        else:
            return self.err_type_members_only()

    def err_type_members_only(self):
        if module_enabled('login'):
            from gdo.ui.GDT_Link import GDT_Link
            back_to = f"&_back_to={urlencode(Application.current_href())}"
            link = GDT_Link().text('link_login_before_continue').href(href('login', 'form', back_to)).render()
            self.err('err_type_member', [link])
            return False
        else:
            return self.err_type_not_allowed(['guest'])

    def err_type_not_allowed(self, types: list[str]):
        print_types = Arrays.human_join(types)
        self.err('err_type', [print_types])
        return False

    def err_permission(self, perm: str):
        self.err('err_permission', [perm])
        return False
