class UserNotFoundException(Exception):
    pass

class UserAlreadyExistsException(Exception):
    pass

class MissingHeadersException(Exception):
    pass

class MissingTokenException(Exception):
    pass

class TokenVerificationException(Exception):
    pass