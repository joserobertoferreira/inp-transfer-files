from enum import IntEnum


class YesNo(IntEnum):
    """Chapter 1: YES or NO"""

    NO = 1
    YES = 2


class ImportExport(IntEnum):
    """Chapter 2762: IMPORT or EXPORT"""

    IMPORT = 1
    EXPORT = 2


class FtpProtocol(IntEnum):
    """Chapter 6241: FTP or SFTP"""

    FTP = 1
    SFTP = 2


class PositionType(IntEnum):
    """Chapter 47: Sequence Number Fields
    Define os tipos de segmentos que compõem o valor do contador.
    """

    CONSTANT = 1
    YEAR = 2
    MONTH = 3
    WEEK = 4
    DAY = 5
    COMPANY = 6
    SITE = 7
    SEQUENCE = 8
    COMPLEMENT = 9
    FISCAL_YEAR = 10
    PERIOD = 11
    FORMULA = 12
