import time
import os
import magic
from cortexutils.analyzer import Analyzer
import requests

class PurpleLabAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.token = self.get_param('config.token', None, 'No PurpleLab token defined')

    def run(self):
        if self.data_type == 'file':
            file_path = self.get_param('file', None, 'File path is missing')
            self.report(self.upload_file(file_path))
        else:
            self.error('Invalid data type')

    def upload_file(self, file_path):
        purplelab_url = "https://YourPurpleLabURL:5000/api/upload"
        vm_upload_url = "https://YourPurpleLabURL:5000/api/upload_to_vm"

        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        magic_extension = magic.Magic(extension=True)
        file_extension = magic_extension.from_file(file_path)
        
        if file_extension and not file_extension.startswith('.'):
            file_extension = '.' + file_extension

        file_name = os.path.basename(file_path) + file_extension
        execute_upload_url = f"https://YourPurpleLabURL:5000/api/execute_upload?file_name={file_name}"

        try:
            with open(file_path, 'rb') as f:

                response = requests.post(
                    purplelab_url,
                    headers={'Authorization': f'Bearer {self.token}'},
                    files={'file': f},
                    verify=False  
                )
                response.raise_for_status()

                f.seek(0)
                api_response = requests.post(
                    vm_upload_url,
                    headers={'Authorization': f'Bearer {self.token}'},
                    files={'file': f},
                    verify=False
                )
                api_response.raise_for_status()

                time.sleep(3)

                execute_response = requests.post(
                    execute_upload_url,
                    headers={'Authorization': f'Bearer {self.token}'},
                    verify=False
                )
                execute_response.raise_for_status()

                return response.json()  
        except Exception as e:
            self.error(str(e))

if __name__ == '__main__':
    PurpleLabAnalyzer().run()
