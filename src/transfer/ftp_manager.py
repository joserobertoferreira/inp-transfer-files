import logging
from ftplib import FTP, error_perm
from pathlib import Path
from typing import Optional

from src.config.connection_ftp import FtpConfig

logger = logging.getLogger(__name__)


class FtpManager:
    """
    Gerencia a conexão e as operações com um servidor FTP específico.
    """

    def __init__(self, config: FtpConfig):
        """
        Inicializa o gerenciador.

        Args:
            config (FtpConfig): Configurações de conexão FTP.
        """
        self.hostname = config.host
        self.port = config.port or 21  # Usa a porta 21 se for None ou 0
        self.username = config.user
        self.password = config.password
        self.ftp: Optional[FTP] = None

        # Guardar o estado do modo de transferência
        self.binary_mode = config.binary_mode
        self.encoding = config.encoding if not self.binary_mode else 'latin-1'

        mode_str = 'BINÁRIO' if self.binary_mode else f'ASCII (encoding: {self.encoding})'
        logger.debug(f'FtpManager para {self.hostname} configurado para usar o modo {mode_str}.')

    def __enter__(self):
        try:
            logger.info(f'A conectar ao servidor FTP em {self.hostname}:{self.port}...')
            # Usamos FTP() para a conexão padrão, com um timeout
            self.ftp = FTP(encoding=self.encoding)
            self.ftp.connect(self.hostname, self.port, timeout=15)
            self.ftp.login(self.username, self.password)

            # Entrar em modo passivo é quase sempre necessário e mais seguro através de firewalls.
            self.ftp.set_pasv(True)

            logger.info(f"Conexão FTP com '{self.hostname}' estabelecida com sucesso.")
            return self
        except Exception as e:
            logger.error(f'Falha na conexão FTP com {self.hostname}: {e}', exc_info=True)
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as e:
                logger.warning(f"Erro ao fechar a conexão FTP com '{self.hostname}': {e}")
            finally:
                self.ftp = None
        logger.info(f"Conexão FTP com '{self.hostname}' fechada.")

    def list_files(self, remote_path: str) -> list[str]:
        if not self.ftp:
            logger.error('Cliente FTP não conectado.')
            return []
        try:
            logger.info(f"Listar ficheiros em '{remote_path}'...")
            return self.ftp.nlst(remote_path)
        except error_perm as e:
            if '550' in str(e):  # Código de erro comum para 'ficheiro não encontrado'
                logger.warning(f'Diretório remoto não encontrado ou vazio: {remote_path}')
                return []
            logger.error(f"Falha ao listar ficheiros em '{remote_path}': {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Falha inesperada ao listar ficheiros em '{remote_path}': {e}", exc_info=True)
            return []

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        if not self.ftp:
            logger.error('Cliente FTP não conectado.')
            return False

        local_file = Path(local_path)
        if not local_file.exists():
            logger.error(f'Ficheiro local não encontrado para upload: {local_path}')
            return False

        try:
            logger.info(f"Iniciar upload de '{local_path}' para '{remote_path}'...")

            open_mode = 'rb' if self.binary_mode else 'r'

            with open(local_file, open_mode) as f:
                if self.binary_mode:
                    self.ftp.storbinary(f'STOR {remote_path}', f)
                else:
                    self.ftp.storlines(f'STOR {remote_path}', f)
            logger.info('Upload concluído com sucesso.')
            return True
        except Exception as e:
            logger.error(f'Falha no upload do ficheiro: {e}', exc_info=True)
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        if not self.ftp:
            logger.error('Cliente FTP não conectado.')
            return False

        try:
            logger.info(f"Iniciar download de '{remote_path}' para '{local_path}'...")

            if self.binary_mode:
                with open(local_path, 'wb') as f:
                    self.ftp.retrbinary(f'RETR {remote_path}', f.write)
            else:
                with open(local_path, 'w', encoding=self.encoding) as f:
                    self.ftp.retrlines(f'RETR {remote_path}', f.write)
            logger.info('Download concluído com sucesso.')
            return True
        except Exception as e:
            logger.error(f'Falha no download do ficheiro: {e}', exc_info=True)
            return False

    def delete_file(self, remote_path: str) -> bool:
        if not self.ftp:
            logger.error('Cliente FTP não conectado.')
            return False

        try:
            logger.info(f'A remover ficheiro remoto: {remote_path}')
            self.ftp.delete(remote_path)
            logger.info(f"Ficheiro '{remote_path}' removido com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Falha ao remover ficheiro remoto '{remote_path}': {e}", exc_info=True)
            return False
