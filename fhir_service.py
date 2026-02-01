import json
import requests
import logging
from cryptography.fernet import Fernet
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.observation import Observation
from fhirclient.models.condition import Condition
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding

# Konfigurasi audit
logging.basicConfig(filename='fhir_audit.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurasi enkripsi
key = Fernet.generate_key() 
cipher = Fernet(key)

# Konfigurasi server FHIR
settings = {
    'app_id': 'indonesia_ehr_app',
    'api_base': 'https://fhirtest.uhn.ca/baseDstu3'
}
smart = client.FHIRClient(settings=settings)

def validate_code(code, system, fallback_system=None):
    api_urls = {
        'http://loinc.org': f'https://api.loinc.org/v1/loinc/{code}',
        'http://snomed.info/sct': f'https://browser.ihtsdotools.org/snowstorm/snomed-ct/MAIN/2023-01-31/concepts/{code}',
        'http://hl7.org/fhir/sid/icd-10': f'https://icd.who.int/browse10/2019/en#/http%3a%2f%2fid.who.int%2ficd%2fentity%2f{code}',
        'local_icd': f'https://api.bpjs-kesehatan.go.id/icd/{code}'
    }
    url = api_urls.get(system, api_urls.get(fallback_system))
    if not url: return False
    try:
        response = requests.get(url, timeout=5)
        return True if response.status_code == 200 else False
    except: return False

def map_to_patient(legacy_data):
    patient = Patient()
    patient.id = legacy_data.get('id')
    name_parts = legacy_data.get('nama', '').split()
    patient.name = [{'family': name_parts[-1] if name_parts else '', 'given': name_parts[:-1]}]
    patient.birthDate = legacy_data.get('tanggal_lahir')
    patient.gender = 'male' if legacy_data.get('jenis_kelamin') == 'L' else 'female'
    return patient

def process_and_upload(data):
    # Logika utama upload
    patient = map_to_patient(data['patient'])
    # Di sini kamu bisa tambahkan logika mapping observation/condition seperti di kode awalmu
    # patient.create(smart.server) # Aktifkan jika server tujuan sudah siap
    logging.info(f"Proses data pasien {patient.id} selesai.")
    return True

# Data contoh untuk testing
legacy_data_example = {
    'patient': {'id': '123', 'nama': 'Budi Santoso', 'tanggal_lahir': '1990-05-20', 'jenis_kelamin': 'L'},
    'observations': [{'id_obs': 'obs1', 'kode_loinc': '8480-6', 'deskripsi': 'Sistolik', 'nilai': 120, 'satuan': 'mmHg'}],
    'conditions': [{'id_kondisi': 'cond1', 'kode_icd': 'I10', 'deskripsi': 'Hipertensi'}]
}