from gdo.base.Util import module_enabled, href, Arrays


class WithPermissionCheck:

    def has_permission(self, user) -> bool:
        types = self.gdo_user_type().split(',')
        type = user.get_user_type()
        if type not in types:
            return self.err_type(types)
        return True

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
            link = GDT_Link().text('link_continue_as_guest').href(href('register', 'guest', "&_back_to=/foo")).render()
            self.err('err_type_guest', [link])
            return False
        else:
            return self.err_type_members_only()

    def err_type_members_only(self):
        if module_enabled('login'):
            from gdo.ui.GDT_Link import GDT_Link
            link = GDT_Link().text('link_login_before_continue').href(href('login', 'form', "&_back_to=/foo")).render()
            self.err('err_type_member', [link])
            return False
        else:
            return self.err_type_not_allowed(['admin'])

    def err_type_not_allowed(self, types: list[str]):
        print_types = Arrays.human_join(types)
        self.err('err_type', [print_types])
        return False

