from dataclasses import dataclass
from typing import Optional


@dataclass
class FtpConfig:
    """Contém todos os parâmetros de configuração para uma conexão FTP."""

    host: str
    user: str
    password: str
    port: Optional[int] = 21
    binary_mode: bool = True
    encoding: str = 'utf-8'


@dataclass
class SftpConfig:
    """Contém todos os parâmetros de configuração para uma conexão SFTP."""

    host: str
    user: str
    password: str
    port: Optional[int] = 22
    host_key: Optional[str] = None
    private_key: Optional[str] = None
    passphrase: Optional[str] = None
