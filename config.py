import os

def get_env_variable(name, required=True):
    value = os.environ.get(name)
    if required and not value:
        raise EnvironmentError(f"Required environment variable '{name}' is not set.")
    return value

# Example usage:
# GOOGLE_API_KEY = get_env_variable('GOOGLE_API_KEY')
# GOOGLE_MAIL = get_env_variable('GOOGLE_MAIL')
# GOOGLE_MAIL_KEY = get_env_variable('GOOGLE_MAIL_KEY')
# RECEIVER_MAIL = get_env_variable('RECEIVER_MAIL') 