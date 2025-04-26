from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432')
}

# **Sandbox endpoint for Training Component Service WSDL**
wsdl_url = "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl"

# **Sandbox credentials**
username = "WebService.Read"
password = "Asdf098"

def store_training_package(cursor, tp):
    """Store a training package in the database."""
    cursor.execute("""
        INSERT INTO training_packages (code, title, description, status)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (code) DO UPDATE
        SET title = EXCLUDED.title,
            description = EXCLUDED.description,
            status = EXCLUDED.status
        RETURNING id
    """, (tp.Code, tp.Title, getattr(tp, 'Description', None), getattr(tp, 'Status', None)))
    return cursor.fetchone()[0]

def store_unit(cursor, unit, training_package_id):
    """Store a unit in the database."""
    cursor.execute("""
        INSERT INTO units (training_package_id, code, title, description, status)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (code) DO UPDATE
        SET title = EXCLUDED.title,
            description = EXCLUDED.description,
            status = EXCLUDED.status
    """, (training_package_id, unit.Code, unit.Title, 
          getattr(unit, 'Description', None), getattr(unit, 'Status', None)))

try:
    # Create a session with basic authentication
    session = Session()
    session.auth = HTTPBasicAuth(username, password)
    transport = Transport(session=session)

    # Create a SOAP client
    client = Client(wsdl=wsdl_url, transport=transport)

    # Create the search request object
    search_request = {
        'Filter': '',
        'IncludeDeleted': False,
        'IncludeSuperseded': False,
        'SearchCode': False,
        'PageNumber': 1,
        'PageSize': 100,
        'TrainingComponentTypes': {
            'IncludeAccreditedCourse': False,
            'IncludeAccreditedCourseModule': False,
            'IncludeQualification': False,
            'IncludeSkillSet': False,
            'IncludeTrainingPackage': True,
            'IncludeUnit': False,
            'IncludeUnitContextualisation': False
        }
    }

    # Connect to the database
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # Call the Search operation
            search_result = client.service.Search(request=search_request)

            if hasattr(search_result, 'Results') and search_result.Results:
                training_packages = search_result.Results.TrainingComponentSummary
                if training_packages:
                    print("Processing Training Packages:")
                    for tp in training_packages:
                        print(f"Storing Training Package: {tp.Code} - {tp.Title}")
                        training_package_id = store_training_package(cur, tp)
                        
                        # If you need to store units, you would need to make another API call
                        # to get the units for this training package
                        
                    conn.commit()
                    print("Successfully stored training packages in the database.")
                else:
                    print("No training packages found.")
            else:
                print("No results returned from the search.")

except Exception as e:
    print(f"An error occurred: {e}")
