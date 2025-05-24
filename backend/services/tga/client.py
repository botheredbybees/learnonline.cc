"""
Client implementation for Training.gov.au SOAP API.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time

from .exceptions import TGAClientError, TGAAuthenticationError, TGAConnectionError

logger = logging.getLogger(__name__)

class TrainingGovClient:
    """
    Client for interacting with Training.gov.au SOAP API.
    
    This client provides methods to search and retrieve training components
    from Training.gov.au using their SOAP API.
    
    Args:
        username (str): TGA API username for authentication
        password (str): TGA API password for authentication
        wsdl_url (str, optional): WSDL URL for the TGA service. Defaults to sandbox URL.
        xml_base_url (str, optional): Base URL for XML file downloads. Defaults to TGA URL.
    
    Attributes:
        client: SOAP client instance
        session: HTTP session for API calls
        xml_base_url (str): Base URL for XML file downloads
    """
    
    DEFAULT_WSDL = "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl"
    DEFAULT_XML_BASE = "https://training.gov.au/TrainingComponentFiles/"

    def __init__(
        self, 
        username: str, 
        password: str,
        wsdl_url: Optional[str] = None,
        xml_base_url: Optional[str] = None
    ):
        """Initialize the TGA client with authentication credentials."""
        self.xml_base_url = xml_base_url or self.DEFAULT_XML_BASE
        
        # Set up authentication session
        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        
        # Create transport with auth session
        transport = Transport(session=self.session)
        
        try:
            # Initialize SOAP client
            self.client = Client(
                wsdl=wsdl_url or self.DEFAULT_WSDL,
                transport=transport
            )
        except Exception as e:
            logger.error(f"Failed to initialize TGA client: {e}")
            raise TGAConnectionError(f"Failed to connect to TGA API: {e}")

    def search_components(
        self,
        filter_text: str = "",
        component_types: Optional[Dict[str, bool]] = None,
        page: int = 1,
        page_size: int = 100,
        include_deleted: bool = False,
        include_superseded: bool = True,
        search_code: bool = True
    ) -> Dict[str, Any]:
        """
        Search for training components using TGA API.
        
        Args:
            filter_text (str): Text to filter components by (e.g., training package code)
            component_types (dict, optional): Dict of component types to include in search
            page (int): Page number for paginated results
            page_size (int): Number of results per page
            include_deleted (bool): Whether to include deleted components
            include_superseded (bool): Whether to include superseded components
            search_code (bool): Whether to search by code (True) or title (False)
            
        Returns:
            dict: Search results containing training components
            
        Raises:
            TGAClientError: If the search request fails
        """
        # Default component types if none provided
        if component_types is None:
            component_types = {
                'IncludeAccreditedCourse': False,
                'IncludeAccreditedCourseModule': False,
                'IncludeQualification': True,
                'IncludeSkillSet': True,
                'IncludeTrainingPackage': True,
                'IncludeUnit': True,
                'IncludeUnitContextualisation': False
            }
        
        # Construct search request
        search_request = {
            'Filter': filter_text,
            'IncludeDeleted': include_deleted,
            'IncludeSuperseded': include_superseded,
            'SearchCode': search_code,
            'PageNumber': page,
            'PageSize': page_size,
            'TrainingComponentTypes': component_types
        }
        
        try:
            # Execute search request
            result = self.client.service.Search(request=search_request)
            
            if not hasattr(result, 'Results'):
                logger.warning("No results found in search response")
                return {'components': []}
                
            # Process results
            components = result.Results.TrainingComponentSummary
            if components and not isinstance(components, list):
                components = [components]
                
            return {'components': components or []}
            
        except Exception as e:
            logger.error(f"Failed to search components: {e}")
            raise TGAClientError(f"Component search failed: {e}")

    def get_component_details(
        self,
        code: str,
        show_files: bool = True,
        show_releases: bool = True
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific training component.
        
        Args:
            code (str): Component code to look up
            show_files (bool): Whether to include file information
            show_releases (bool): Whether to include release information
            
        Returns:
            dict: Component details including files and releases if requested
            
        Raises:
            TGAClientError: If the details request fails
        """
        # Construct information request
        information_request = {
            'ShowClassifications': False,
            'ShowCompletionMapping': False,
            'ShowComponents': False,
            'ShowContacts': False,
            'ShowCurrencyPeriods': False,
            'ShowDataManagers': False,
            'ShowFiles': show_files,
            'ShowMappingInformation': False,
            'ShowRecognitionManagers': False,
            'ShowReleases': show_releases,
            'ShowUnitGrid': False,
            'ShowUsageRecommendation': False
        }
        
        # Construct details request
        details_request = {
            'Code': code,
            'InformationRequest': information_request
        }
        
        try:
            # Get component details
            result = self.client.service.GetDetails(request=details_request)
            
            if not hasattr(result, 'GetDetailsResult'):
                logger.warning(f"No details found for component {code}")
                return {}
                
            return result.GetDetailsResult
            
        except Exception as e:
            logger.error(f"Failed to get details for component {code}: {e}")
            raise TGAClientError(f"Failed to get component details: {e}")

    def get_component_xml(
        self, 
        code: str,
        include_assessment: bool = True
    ) -> Dict[str, Optional[str]]:
        """
        Get XML file(s) for a training component.
        
        Args:
            code (str): Component code to get XML for
            include_assessment (bool): Whether to include assessment requirements XML
            
        Returns:
            dict: XML content with keys 'xml' and optionally 'assessment_xml'
            
        Raises:
            TGAClientError: If XML retrieval fails
        """
        try:
            # Get component details with files
            details = self.get_component_details(code, show_files=True, show_releases=True)
            
            if not details or not hasattr(details, 'Releases') or not details.Releases:
                raise TGAClientError(f"No releases found for component {code}")
                
            # Get release files
            release = details.Releases.Release
            if isinstance(release, list):
                release = release[0]  # Use latest release
                
            if not hasattr(release, 'Files') or not release.Files:
                raise TGAClientError(f"No files found for component {code}")
                
            # Find XML files
            xml_file = None
            assessment_file = None
            
            if hasattr(release.Files, 'ReleaseFile'):
                files = release.Files.ReleaseFile
                if not isinstance(files, list):
                    files = [files]
                    
                for file in files:
                    if not hasattr(file, 'Filename'):
                        continue
                        
                    filename = file.Filename
                    if not filename.endswith('.xml'):
                        continue
                        
                    if 'AssessmentRequirements' in filename:
                        assessment_file = filename
                    else:
                        xml_file = filename
                        
            if not xml_file:
                raise TGAClientError(f"No XML file found for component {code}")
                
            # Download XML content
            result = {'xml': self._download_xml(code, xml_file)}
            
            if include_assessment and assessment_file:
                result['assessment_xml'] = self._download_xml(code, assessment_file)
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to get XML for component {code}: {e}")
            raise TGAClientError(f"Failed to get component XML: {e}")

    def get_changes(
        self,
        from_date: str,
        component_types: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Get changes to training components since a given date.
        
        Args:
            from_date (str): ISO format date to check changes from
            component_types (dict, optional): Dict of component types to check
            
        Returns:
            dict: Changes to components since the given date
            
        Raises:
            TGAClientError: If the changes request fails
        """
        if component_types is None:
            component_types = {
                'IncludeAccreditedCourse': False,
                'IncludeAccreditedCourseModule': False,
                'IncludeQualification': True,
                'IncludeSkillSet': True,
                'IncludeTrainingPackage': True,
                'IncludeUnit': True,
                'IncludeUnitContextualisation': False
            }
            
        try:
            # Get changes from TGA
            result = self.client.service.GetChanges(
                modifiedSince=from_date,
                trainingComponentTypes=component_types
            )
            
            if not hasattr(result, 'Changes'):
                return {'changes': []}
                
            changes = result.Changes.Change
            if changes and not isinstance(changes, list):
                changes = [changes]
                
            return {'changes': changes or []}
            
        except Exception as e:
            logger.error(f"Failed to get changes since {from_date}: {e}")
            raise TGAClientError(f"Failed to get component changes: {e}")

    def _download_xml(self, code: str, filename: str) -> Optional[str]:
        """
        Download an XML file from TGA.
        
        Args:
            code (str): Component code the XML belongs to
            filename (str): Name of the XML file to download
            
        Returns:
            str: XML content if successful, None otherwise
            
        Raises:
            TGAClientError: If download fails
        """
        if not filename:
            return None
            
        try:
            # Construct download URL
            url = f"{self.xml_base_url}{filename}"
            
            # Download file
            response = self.session.get(url)
            if response.status_code != 200:
                raise TGAClientError(
                    f"Failed to download {url}: {response.status_code}"
                )
                
            return response.text
            
        except Exception as e:
            logger.error(f"Error downloading XML for {code}: {e}")
            raise TGAClientError(f"Failed to download XML: {e}")

    def extract_elements(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Extract elements and performance criteria from unit XML.
        
        Args:
            xml_content (str): XML content to parse
            
        Returns:
            list: List of elements with their performance criteria
            
        Raises:
            TGAClientError: If parsing fails
        """
        try:
            # Parse XML with BeautifulSoup
            soup = BeautifulSoup(xml_content, 'xml')
            
            elements = []
            element_sections = soup.find_all('div', class_='element')
            
            for element_div in element_sections:
                # Extract element number and title
                element_title = element_div.find('h4')
                if not element_title:
                    continue
                    
                element_text = element_title.text.strip()
                element_match = re.match(r'ELEMENT\s+(\d+)\s+(.*)', element_text)
                if not element_match:
                    continue
                    
                element_num, element_title = element_match.groups()
                
                # Find performance criteria
                pcs = []
                pc_items = element_div.find_all('tr')
                for pc_item in pc_items:
                    pc_cells = pc_item.find_all('td')
                    if len(pc_cells) < 2:
                        continue
                        
                    pc_num = pc_cells[0].text.strip()
                    pc_text = pc_cells[1].text.strip()
                    
                    if pc_num and pc_text:
                        pcs.append({
                            'number': pc_num,
                            'text': pc_text
                        })
                
                elements.append({
                    'number': int(element_num),
                    'title': element_title,
                    'performance_criteria': pcs
                })
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to parse elements from XML: {e}")
            raise TGAClientError(f"Failed to parse elements: {e}")
