"""
Mostly borrowed from Amazon
https://aws.amazon.com/developers/getting-started/python/
"""

import base64
import logging
import sys
import json

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

# Number of secrets manager secrets to look for - future scaling taken into account,
# given that each secret can store 4096 characters,
# so we shouldn't use more than a secret or two per application
MAX_SECRETS = 20


class SecretsManager(object):
    def __init__(self, secret_name_base, region="us-east-1"):
        self.secret_name = secret_name_base
        self.session = boto3.session.Session()
        if region is not "":
            self.region = region
        else:
            self.region = self.session.region_name
        self.session = boto3.session.Session()
        self.client = self.session.client(
            service_name='secretsmanager',
            region_name=self.region
        )

    def get_all_path_secrets(self):
        """
        Retrieve all secrets from secrets manager, retrieving up to MAX_SECRETS different secrets
        :return: all_secrets_combined - a dict of all secrets across up to MAX_SECRETS secret_name_base paths
        """

        all_secrets_combined = {}
        for path_int in range(1, MAX_SECRETS):
            logger.info('Attempting to pull secret: {}'.format(self.secret_name + '-{}'.format(path_int)))
            # If we returned nothing on the last pull, that was the last of the range, stop incrementing
            if self.get_secret(self.secret_name + '-{}'.format(path_int)) is False:
                break
            # Otherwise add to the dictionary
            else:
                all_secrets_combined.update(json.loads(self.get_secret(self.secret_name + '-{}'.format(path_int))))

        return all_secrets_combined

    def get_secret(self, secret_path):
        """
        :param secret_path:
        :return:
        """
        get_secret_value_response = {}
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_path
            )
        except ClientError as e:
            except_result = self._exception_handling(e)
            if not except_result:
                return False

        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret

    def _exception_handling(self, e):
        """
        :param e: Exception object to handle - ClientError
        :return: bool - returns False if we reached resource not found exception, otherwise null
        """
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            logger.info(
                "Did not find secret for path, likely this is ok and the previous was the last secret of the batch")
            return False
        else:
            logger.error('An unexpected error occurred:')
            raise e


if __name__ == '__main__':
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    sm = SecretsManager("platform/check-sponsor-proxy/all", "us-east-2")
    print(sm.get_all_path_secrets())