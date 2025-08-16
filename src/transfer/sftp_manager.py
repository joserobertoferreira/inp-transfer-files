import logging
from pathlib import Path
from typing import Optional

import paramiko
from paramiko.ssh_exception import AuthenticationException, BadHostKeyException, SSHException

# Desativando o logging excessivo do paramiko
logging.getLogger('paramiko').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


class SftpManager:
    """
    Gerencia a conexão e as operações com um servidor SFTP específico.
    As credenciais são passadas durante a inicialização.
    """

    def __init__(self, host: str, port: int, user: str, password: str):
        """
        Inicializa o gerenciador com as configurações de um fornecedor específico.
        """
        self.hostname = host
        self.port = port
        self.username = user
        self.password = password

        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None

    def __enter__(self):
        try:
            logger.info(f'A conectar ao servidor SFTP em {self.hostname}:{self.port}...')
            self.ssh_client = paramiko.SSHClient()

            known_hosts_file = Path.cwd() / 'known_hosts'
            if not known_hosts_file.exists():
                logger.warning(
                    f'Ficheiro "known_hosts" não encontrado em {known_hosts_file}. '
                    'A conectar sem verificação de chave de host (menos seguro).'
                )
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                self.ssh_client.load_host_keys(str(known_hosts_file))
                self.ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())

            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=15,
            )
            self.sftp_client = self.ssh_client.open_sftp()
            logger.info(f"Conexão SFTP com '{self.hostname}' estabelecida com sucesso.")
            return self
        except BadHostKeyException as e:
            logger.error(f'ERRO DE CHAVE DE HOST para {self.hostname}: A chave do servidor é inválida! Detalhes: {e}')
            self.__exit__(None, None, None)
            raise
        except AuthenticationException:
            logger.error(f"Falha na autenticação SFTP para '{self.username}@{self.hostname}'.")
            self.__exit__(None, None, None)
            raise
        except (SSHException, TimeoutError, OSError) as e:
            logger.error(f'Falha na conexão SFTP com {self.hostname}: {e}')
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        logger.info(f"Conexão SFTP com '{self.hostname}' fechada.")

    def upload_file(self, local_path: str, remote_path: str):
        """
        Faz o upload de um ficheiro local para o servidor SFTP.

        :param local_path: Caminho do ficheiro na máquina local.
        :param remote_path: Caminho completo (incluindo nome do ficheiro) no servidor remoto.
        :return: True se o upload for bem-sucedido, False caso contrário.
        """
        if not self.sftp_client:
            logging.error('Cliente SFTP não está conectado. O upload foi abortado.')
            return False

        try:
            logging.info(f"Iniciar upload de '{local_path}' para '{remote_path}'...")
            self.sftp_client.put(local_path, remote_path)
            logging.info('Upload concluído com sucesso.')
            return True
        except Exception as e:
            logging.error(f'Falha no upload do ficheiro: {e}')
            return False

    def download_file(self, remote_path: str, local_path: str):
        """
        Faz o download de um ficheiro do servidor SFTP para a máquina local.

        :param remote_path: Caminho completo do ficheiro no servidor remoto.
        :param local_path: Caminho onde o ficheiro será salvo localmente.
        :return: True se o download for bem-sucedido, False caso contrário.
        """
        if not self.sftp_client:
            logging.error('Cliente SFTP não está conectado. O download foi abortado.')
            return False

        try:
            logging.info(f"Iniciar download de '{remote_path}' para '{local_path}'...")
            self.sftp_client.get(remote_path, local_path)
            logging.info('Download concluído com sucesso.')
            return True
        except Exception as e:
            logging.error(f'Falha no download do ficheiro: {e}')
            return False

    def list_files(self, remote_path: str) -> list[str]:
        """
        Lista os nomes dos ficheiros em um diretório remoto.
        Retorna uma lista vazia se o diretório não existir ou em caso de erro.
        """
        if not self.sftp_client:
            logging.error('Cliente SFTP não conectado.')
            return []

        try:
            logging.info(f"Listar ficheiros em '{remote_path}'...")
            return self.sftp_client.listdir(remote_path)
        except FileNotFoundError:
            logging.warning(f'Diretório remoto não encontrado: {remote_path}')
            return []
        except Exception as e:
            logging.error(f"Falha ao listar ficheiros em '{remote_path}': {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        """
        Remove um ficheiro no servidor SFTP.
        Retorna True se bem-sucedido, False caso contrário.
        """
        if not self.sftp_client:
            logging.error('Cliente SFTP não conectado.')
            return False

        try:
            logging.info(f'Deletando ficheiro remoto: {remote_path}')
            self.sftp_client.remove(remote_path)
            logging.info(f"Ficheiro '{remote_path}' removido com sucesso.")
            return True
        except Exception as e:
            logging.error(f"Falha ao remover ficheiro remoto '{remote_path}': {e}")
            return False
