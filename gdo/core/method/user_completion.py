from gdo.base.Util import module_enabled
from gdo.core.MethodCompletion import MethodCompletion
from gdo.core.GDT_User import GDT_User


class user_completion(MethodCompletion):

    def gdo_completion_items(self) -> list[dict[str, str]]:
        users = GDT_User('user').query_gdos(self.get_query())
        results = []
        for user in users:
            result = {
                'id': user.get_id(),
                'var': user.get_name_sid(),
                'display_var': user.render_name(),
            }
            if module_enabled('avatar'):
                from gdo.avatar.GDT_Avatar import GDT_Avatar
                result['avatar'] = GDT_Avatar('avatar').for_user(user).href_render()
            results.append(result)
        return results
