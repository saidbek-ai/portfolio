def save_user_details(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        user.first_name = response.get('given_name')
        user.last_name = response.get('family_name')
        user.set_unusable_password()
        user.save()
