import requests
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class CodaAPIClient:
    def __init__(self):
        self.api_token = settings.CODA_API_TOKEN
        self.base_url = settings.CODA_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Coda API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"API Response Error: {e.response.text if hasattr(e, 'response') and e.response else str(e)}")

    def list_documents(self, limit: int = 100) -> List[Dict]:
        documents = []
        page_token = None
        while True:
            params = {'limit': min(limit, 100)}
            if page_token:
                params['pageToken'] = page_token

            data = self._make_request('GET', 'docs', params=params)
            if not data:
                break

            documents.extend(data.get('items', []))
            page_token = data.get('nextPageToken')
            if not page_token:
                break

        return documents

    def get_document_info(self, doc_id: str) -> Optional[Dict]:
        return self._make_request('GET', f'docs/{doc_id}')

    def list_tables(self, doc_id: str) -> List[Dict]:
        tables = []
        page_token = None

        while True:
            params = {}
            if page_token:
                params['pageToken'] = page_token

            data = self._make_request('GET', f'docs/{doc_id}/tables', params=params)
            if not data:
                break

            tables.extend(data.get('items', []))
            page_token = data.get('nextPageToken')
            if not page_token:
                break

        return tables

    def get_table_rows(self, doc_id: str, table_id: str, limit: int = 100) -> List[Dict]:
        """Get rows from a table with proper column mapping"""
        rows = []
        page_token = None

        while True:
            params = {
                'limit': min(limit, 100),
                'useColumnNames': 'true'
            }
            if page_token:
                params['pageToken'] = page_token

            data = self._make_request('GET', f'docs/{doc_id}/tables/{table_id}/rows', params=params)
            
            if not data:
                break
            
            for item in data.get('items', []):
                row_data = {
                    'id': item.get('id'),
                    'cells': []
                }
                
                if 'values' in item:
                    values = item['values']
                    
                    for column_name, column_value in values.items():
                        if column_value:
                            row_data['cells'].append({
                                'column': column_name,
                                'value': column_value
                            })
                else:
                    for cell in item.get('cells', []):
                        cell_info = {
                            'column': cell.get('column'),
                            'value': cell.get('value')
                        }
                        
                        if 'value' in cell:
                            cell_info['value'] = cell['value']
                        elif 'text' in cell:
                            cell_info['value'] = cell['text']
                        
                        row_data['cells'].append(cell_info)
                
                rows.append(row_data)
            
            page_token = data.get('nextPageToken')
            if not page_token:
                break
        return rows

    def get_table_columns(self, doc_id: str, table_id: str) -> List[Dict]:
        """Get column information for a table"""
        data = self._make_request('GET', f'docs/{doc_id}/tables/{table_id}/columns')
        return data.get('items', []) if data else []