import uuid
import names
from crewai_tools import BaseTool
from cloud_shield_ai import logger
from cryptography.fernet import Fernet


class RandomNameGeneratorTool(BaseTool):
    name: str = "RandomNameGenerator"
    description: str = "Generates a random first name."

    def _run(self) -> str:
        random_name = names.get_first_name()
        logger.info(f"Generated random name: {random_name}")
        return random_name


class BucketNameGeneratorTool(BaseTool):
    name: str = "BucketNameGenerator"
    description: str = "Generates a unique valid S3 bucket name."

    def _run(self) -> str:
        try:
            random_name_generator = RandomNameGeneratorTool()
            random_name = random_name_generator._run()
            bucket_name = f"{random_name.lower()}-{uuid.uuid4()}"
            logger.info(f"Generated bucket name: {bucket_name}")
            return bucket_name
        except Exception as e:
            logger.error(f"Failed to generate bucket name: {e}")
            raise
        

class CompileReportTool(BaseTool):
    name: str = "CompileReport"
    description: str = "Compiles a report of chain of permissions."

    def _run(self, permissions: list[str]) -> str:
        report = "\n".join(permissions)
        logger.info(f"Compiled report: {report}")
        return report
    
    

class EncryptionUtility(BaseTool):
    name: str = "EncryptionUtility"
    description: str = "Utility to encrypt the data, generating a key automatically and encrypting the data passed as argument."

    @staticmethod
    def generate_key() -> bytes:
        return Fernet.generate_key()

    @staticmethod
    def encrypt_data(data: bytes, key: bytes) -> bytes:
        f = Fernet(key)
        return f.encrypt(data)

    def _run(self, data: str) -> str:
        try:
            key = self.generate_key()
            data_bytes = data.encode('utf-8')
            encrypted_data = self.encrypt_data(data_bytes, key)
            logger.info("Data encrypted successfully.")
            return f"Encryption successful. Decryption key: {key.decode()}"
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return "Encryption failed"
