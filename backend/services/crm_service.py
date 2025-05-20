from typing import Dict, Any
import requests
import os

class CRMService:
    def __init__(self):
        self.api_keys = {
            'salesforce': os.getenv('SALESFORCE_API_KEY'),
            'hubspot': os.getenv('HUBSPOT_API_KEY')
        }
        self.base_urls = {
            'salesforce': 'https://your-salesforce-instance.salesforce.com/services/data/v56.0',
            'hubspot': 'https://api.hubapi.com/crm/v3'
        }

    def update_crm(self, crm_type: str, object_type: str, action: str, data: Dict[str, Any]) -> bool:
        """Update CRM with provided data."""
        try:
            if crm_type not in self.api_keys or not self.api_keys[crm_type]:
                raise ValueError(f"Invalid CRM type or missing API key: {crm_type}")

            headers = {
                'Authorization': f'Bearer {self.api_keys[crm_type]}',
                'Content-Type': 'application/json'
            }

            if crm_type == 'salesforce':
                return self._update_salesforce(object_type, action, data, headers)
            elif crm_type == 'hubspot':
                return self._update_hubspot(object_type, action, data, headers)
            
            return False
        except Exception as e:
            print(f"Error updating CRM: {str(e)}")
            return False

    def _update_salesforce(self, object_type: str, action: str, data: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Update Salesforce CRM."""
        try:
            url = f"{self.base_urls['salesforce']}/sobjects/{object_type}"
            
            if action == 'create':
                response = requests.post(url, headers=headers, json=data)
            elif action == 'update':
                response = requests.patch(f"{url}/{data.get('Id')}", headers=headers, json=data)
            elif action == 'delete':
                response = requests.delete(f"{url}/{data.get('Id')}", headers=headers)
            else:
                raise ValueError(f"Invalid action: {action}")

            return response.status_code in [200, 201, 204]
        except Exception as e:
            print(f"Error updating Salesforce: {str(e)}")
            return False

    def _update_hubspot(self, object_type: str, action: str, data: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Update HubSpot CRM."""
        try:
            url = f"{self.base_urls['hubspot']}/objects/{object_type}"
            
            if action == 'create':
                response = requests.post(url, headers=headers, json=data)
            elif action == 'update':
                response = requests.patch(f"{url}/{data.get('id')}", headers=headers, json=data)
            elif action == 'delete':
                response = requests.delete(f"{url}/{data.get('id')}", headers=headers)
            else:
                raise ValueError(f"Invalid action: {action}")

            return response.status_code in [200, 201, 204]
        except Exception as e:
            print(f"Error updating HubSpot: {str(e)}")
            return False 