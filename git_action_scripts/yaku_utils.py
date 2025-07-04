import requests
import os

class ApiResponse:
    def __init__(self,success,data=None,status_code=None,error_message=None):
        """
        :param success: True if the API call was successful,False otherwise
        :param data: Parsed JSON response (on success)
        """
        self.success=success
        self.data = data
        self.status_code = status_code
        self.error_message = error_message
    def __repr__(self):
        return f"<ApiResponse success={self.success} status={self.status_code} error={self.error_message}>"
    
    def response_data(self):
        return (self.data)

class YakuClient:
    def __init__(self,base_url,namespace_id,token=None):
        """
        :param base_url: YAKU's Base URL of the API.It's a internal k8s service
        :param namespace_id: Namespace ID to target
        :param token: YAKU's long run token.
        """
        self.base_url=base_url.rstrip("/")
        self.namespace_id=namespace_id
        self.headers={
            "Content-Type":"application/json"
        }
        if token:
            self.headers["Authorization"]=f"Bearer {token}"
    def _request(self,method,url,**kwargs):
        """
        This is Internal method to handle HTTP requests
        """
        try:
            response=requests.request(method,url,headers=self.headers,timeout=15,**kwargs)
            response.raise_for_status()
            return ApiResponse(
                success=True,
                data=response.json(),
                status_code=response.status_code
            )
        except requests.exceptions.HTTPError as http_err:
            error_text = response.text if response is not None else str(http_err)
            print(f"[HTTP ERROR] {method.upper()} {url} -> {response.status_code}: {error_text}")
            return ApiResponse(
                success=False,
                status_code=response.status_code if response else None,
                error_message=error_text
            )
    def get_configs(self):
        url = f"{self.base_url}/api/v1/namespaces/{self.namespace_id}/configs"
        return self._request("get", url)

    def create_config(self, name, description):
        url = f"{self.base_url}/api/v1/namespaces/{self.namespace_id}/configs"
        body = {
            "name": name,
            "description": description
        }
        return self._request("post", url, json=body)
    def upload_file(self, config_id, file_path):
        url = f"{self.base_url}/api/v1/namespaces/{self.namespace_id}/configs/{config_id}/files"
        if not os.path.isfile(file_path):
            return ApiResponse(
                success=False,
                error_message=f"File does not exist: {file_path}"
            )

        filename = os.path.basename(file_path)
        files = {
            "content": (filename,open(file_path, "rb"),"application/yaml")
        }
        data = {
                "filename":  filename # Sending filename as a separate form field
            }

        # Use a separate headers (requests handles multipart boundary automatically)
        try:
            response = requests.post(url, headers={"Authorization": self.headers.get("Authorization")}, files=files,data=data ,timeout=10)
            response.raise_for_status()
            return ApiResponse(
                success=True,
                data=response.json(),
                status_code=response.status_code
            )
        except requests.exceptions.JSONDecodeError:
            print("Warning: Server response was not valid JSON.")
        except requests.exceptions.RequestException as e:
            print(f"[UPLOAD ERROR] POST {url} -> {e}")
            return ApiResponse(
                success=False,
                error_message=str(e),
                status_code=response.status_code if 'response' in locals() and response else None
            )
        finally:
            files["content"][1].close()
    def run_config(self, config_id):
        url = f"{self.base_url}/api/v1/namespaces/{self.namespace_id}/runs"
        body= {
            "configId": config_id,
            "environment": {
                "ENV_KEY1": "env-value1",
                "ENV_KEY2": "env-value2"
            }
        }
        self._request("post", url, json=body)

if __name__ == "__main__":
    YAKU_API_TOKEN=os.environ.get('YAKU_API_TOKEN')
    yaku_client=YakuClient("http://127.0.0.1:3000/",1,YAKU_API_TOKEN)
    result=yaku_client.get_configs()
    #create a config
    result_1=yaku_client.create_config("appname_version_ADTOPS-1163","ADTOPS-1163 test case for appname")
    config_id=result_1.response_data()['id']
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    file_path=os.path.join(project_root,'automation/testcase/ADTOPS-1163/qg-config.yaml')
    yaku_client.upload_file(config_id,file_path)
    #
    file_path=os.path.join(project_root,'automation/testcase/ADTOPS-1163/jira_utils.py')
    yaku_client.upload_file(config_id,file_path)
    yaku_client.run_config(config_id)
    #add file in config