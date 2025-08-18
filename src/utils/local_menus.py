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
