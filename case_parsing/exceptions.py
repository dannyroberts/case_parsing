class CaseParsingException(Exception):
    pass


class CaseArithmeticError(CaseParsingException):
    pass


class CreateCaseError(CaseArithmeticError):
    pass


class CloseCaseError(CaseArithmeticError):
    pass


class CaseIdError(CaseArithmeticError):
    pass