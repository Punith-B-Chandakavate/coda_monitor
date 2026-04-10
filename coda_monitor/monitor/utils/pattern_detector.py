import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class PatternDetector:
    PATTERNS = {
        'EMAIL': {
            'regex': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'severity': 'MEDIUM',
            'description': 'Email address'
        },
        'CREDIT_CARD': {
            'regex': r'\b(?:\d[ -]*?){13,16}\b',
            'severity': 'CRITICAL',
            'description': 'Credit card number',
            'validation': lambda x: len(re.sub(r'[\s-]', '', x)) in [13, 14, 15, 16]
        },
        'SSN': {
            'regex': r'\b\d{3}-\d{2}-\d{4}\b',
            'severity': 'CRITICAL',
            'description': 'Social Security Number'
        },
        'PHONE': {
            'regex': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'severity': 'MEDIUM',
            'description': 'Phone number'
        },
        'IP_ADDRESS': {
            'regex': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'severity': 'MEDIUM',
            'description': 'IP address'
        },
        'API_KEY': {
            'regex': r'\b(?:[A-Za-z0-9]{32,})\b',
            'severity': 'HIGH',
            'description': 'Possible API key'
        },
        'PASSWORD': {
            'regex': r'(?i)(?:password|passwd|pwd)[\s]*[:=][\s]*[\S]+',
            'severity': 'HIGH',
            'description': 'Password in text'
        },
        'BANK_ACCOUNT': {
            'regex': r'\b\d{10,12}\b',
            'severity': 'HIGH',
            'description': 'Bank account number'
        },
        'DATE_OF_BIRTH': {
            'regex': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'severity': 'MEDIUM',
            'description': 'Date of birth'
        }
    }

    def __init__(self):
        self.compiled_patterns = {}
        for pattern_name, pattern_info in self.PATTERNS.items():
            self.compiled_patterns[pattern_name] = {
                'regex': re.compile(pattern_info['regex'], re.IGNORECASE),
                'severity': pattern_info['severity'],
                'description': pattern_info['description'],
                'validation': pattern_info.get('validation')
            }

    def detect_in_text(self, text: str) -> List[Tuple[str, str, str]]:
        """Detect sensitive patterns in text"""
        if not text or not isinstance(text, str):
            return []

        # Convert to string if it's not
        text = str(text)

        detections = []

        for pattern_name, pattern_info in self.compiled_patterns.items():
            matches = pattern_info['regex'].finditer(text)
            for match in matches:
                matched_value = match.group()

                # Apply validation if exists
                if pattern_info['validation']:
                    if not pattern_info['validation'](matched_value):
                        continue

                detections.append((
                    pattern_name,
                    matched_value,
                    pattern_info['severity']
                ))

        # Remove duplicates
        return list(set(detections))

    def scan_table_rows(self, rows: List[Dict]) -> List[Dict]:
        """Scan table rows for sensitive data"""
        issues = []

        for row in rows:
            row_id = row.get('id')
            cells = row.get('cells', [])

            for cell in cells:
                column = cell.get('column', 'Unknown')
                value = cell.get('value', '')

                # Skip empty values
                if not value:
                    continue

                # Convert to string for pattern matching
                value_str = str(value)

                # Log for debugging
                logger.debug(f"Scanning cell: {column} = {value_str[:100]}")

                # Detect patterns
                detections = self.detect_in_text(value_str)

                if detections:
                    logger.info(f"Found {len(detections)} issues in {column}: {value_str[:50]}")

                    for pattern_type, matched_value, severity in detections:
                        issues.append({
                            'row_id': row_id,
                            'column_name': column,
                            'detected_value': matched_value[:200],
                            'pattern_type': pattern_type,
                            'severity': severity,
                            'full_content': value_str[:500]
                        })

        return issues