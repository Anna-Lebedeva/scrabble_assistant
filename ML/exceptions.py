class ClfNotFoundException(FileNotFoundError):
    """
    Исключение, выбрасываемое если не найден дамп классификатора.
    """
    pass


class ScNotFoundException(FileNotFoundError):
    """
    Исключение, выбрасываемое если не найден дамп шкалировщика.
    """
    pass
