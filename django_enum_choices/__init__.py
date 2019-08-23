from django.apps import apps

if apps.apps_ready:
    """

    `register_enum_choice_list_filter` depends on `django.conf.settings`
    The tests do not define a settings module so we need to execute
    `register_enum_choice_list_filter` only when the apps are loaded.

    """

    from .admin import register_enum_choice_list_filter

    register_enum_choice_list_filter()
