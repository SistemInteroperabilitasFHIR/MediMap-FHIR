from flask import Flask, request, jsonify
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

app = Flask(__name__)

# Konfigurasi logging audit
logging.basicConfig(filename='fhir_audit.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurasi enkripsi
key = Fernet.generate_key()
cipher = Fernet(key)

# Konfigurasi FHIR
settings = {
    'app_id': 'indonesia_fhir_app',
    'api_base': 'https://fhirtest.uhn.ca/baseDstu3'  # Ganti dengan server BPJS atau lokal
}
smart = client.FHIRClient(settings=settings)

# Fungsi validasi terminologi dengan fallback
def validate_code(code, system, fallback_system=None):
    api_urls = {
        'http://loinc.org': f'https://api.loinc.org/v1/loinc/{code}',
        'http://snomed.info/sct': f'https://browser.ihtsdotools.org/snowstorm/snomed-ct/MAIN/2023-01-31/concepts/{code}',
        'http://hl7.org/fhir/sid/icd-10': f'https://icd.who.int/browse10/2019/en#/http%3a%2f%2fid.who.int%2ficd%2fentity%2f{code}',
        'local_icd': f'https://api.bpjs-kesehatan.go.id/icd/{code}'  # Fallback ICD Indonesia
    }
    url = api_urls.get(system, api_urls.get(fallback_system))
    if not url:
        return False
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except:
        return False

# Fungsi pemetaan
def map_legacy_to_fhir(data):
    results = {'patient': None, 'observations': [], 'conditions': []}
    
    # Map Patient
    patient = Patient()
    patient.id = data['patient'].get('id')
    name_parts = data['patient'].get('nama', '').split()
    patient.name = [{'family': name_parts[-1] if name_parts else '', 'given': name_parts[:-1]}]
    patient.birthDate = data['patient'].get('tanggal_lahir')
    patient.gender = 'male' if data['patient'].get('jenis_kelamin') == 'L' else 'female'
    results['patient'] = patient.as_json()
    
    # Map Observations
    for obs in data.get('observations', []):
        observation = Observation()
        observation.id = obs.get('id_obs')
        observation.subject = {'reference': f'Patient/{patient.id}'}
        observation.code = CodeableConcept()
        code = obs.get('kode_loinc')
        system = 'http://loinc.org'
        if validate_code(code, system, 'local_icd'):
            observation.code.coding = [Coding(system=system, code=code, display=obs.get('deskripsi')).as_json()]
        observation.valueQuantity = {'value': obs.get('nilai'), 'unit': obs.get('satuan')}
        results['observations'].append(observation.as_json())
    
    # Map Conditions
    for cond in data.get('conditions', []):
        condition = Condition()
        condition.id = cond.get('id_kondisi')
        condition.subject = {'reference': f'Patient/{patient.id}'}
        condition.code = CodeableConcept()
        code = cond.get('kode_icd')
        system = 'http://hl7.org/fhir/sid/icd-10'
        if validate_code(code, system, 'http://snomed.info/sct'):
            condition.code.coding = [Coding(system=system, code=code, display=cond.get('deskripsi')).as_json()]
        results['conditions'].append(condition.as_json())
    
    return results

# Endpoint untuk pemetaan
@app.route('/map', methods=['POST'])
def map_data():
    try:
        data = request.json
        encrypted_data = cipher.encrypt(json.dumps(data).encode())
        decrypted_data = json.loads(cipher.decrypt(encrypted_data).decode())
        mapped = map_legacy_to_fhir(decrypted_data)
        logging.info("Data mapped successfully")
        return jsonify(mapped)
    except Exception as e:
        logging.error(f"Mapping error: {str(e)}")
        return jsonify({'error': 'Mapping failed'}), 500

# Endpoint untuk upload
@app.route('/upload', methods=['POST'])
def upload_data():
    try:
        data = request.json
        # Simulasi upload
        logging.info("Data uploaded to FHIR")
        return jsonify({'status': 'Uploaded successfully'})
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)