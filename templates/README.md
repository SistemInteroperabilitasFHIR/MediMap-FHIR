# 🏥 FHIR Indonesia Web Bridge

Aplikasi web sederhana untuk memetakan data kesehatan legacy (SIMRS) ke standar internasional **HL7 FHIR**.

## 🚀 Fitur Utama
- **Auto-Mapping**: Mengubah format JSON lokal ke resource Patient, Observation, dan Condition FHIR.
- **Validasi Terminologi**: Cek otomatis kode ICD-10 dan LOINC via API.
- **Security First**: Enkripsi data sensitif pasien menggunakan `cryptography.fernet`.
- **Web Interface**: Input data mudah melalui dashboard Flask.

## 🛠️ Teknologi yang Digunakan
- **Bahasa**: Python 3.x
- **Framework Web**: Flask
- **Standard**: HL7 FHIR (Dstu3)
- **Security**: Fernet Symmetric Encryption

## 📦 Cara Instalasi

1. **Clone Repositori**
   ```bash
   git clone [https://github.com/username-kamu/fhir-web.git](https://github.com/username-kamu/fhir-web.git)
   cd fhir-web