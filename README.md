# DataLab Backend (Flask)

Modular Flask backend matching the DataLab frontend feature set.

## Stack
- Flask + Flask-SocketIO (eventlet) — REST + WebSockets
- MongoDB (via PyMongo) — persistence
- scikit-learn + pandas — real AutoML training
- Mocked LLM — templated report generation & chat
- JWT auth (PyJWT) — login / signup

## Architecture

```
backend/
├── app.py                    # App + SocketIO factory, entrypoint
├── config.py                 # Env config
├── extensions.py             # Mongo, SocketIO, bcrypt singletons
├── requirements.txt
├── .env.example
├── api/                      # HTTP blueprints (one per domain)
│   ├── auth.py
│   ├── datasets.py
│   ├── reports.py
│   ├── automl.py
│   └── visualizations.py
├── services/                 # Business logic (framework-free)
│   ├── auth_service.py
│   ├── dataset_service.py
│   ├── report_service.py    # Mocked LLM
│   ├── automl_service.py    # scikit-learn training + WS streaming
│   └── viz_service.py
├── models/                   # Mongo document helpers
│   ├── user.py
│   ├── dataset.py
│   ├── report.py
│   └── job.py
├── sockets/                  # SocketIO namespaces
│   └── training.py
├── utils/
│   ├── jwt_utils.py
│   ├── decorators.py         # @auth_required
│   ├── parsers.py            # CSV/XLSX -> rows + column meta
│   └── errors.py
└── uploads/                  # Raw uploaded files (gitignored)
```

## Run

```bash
cd backend
cp .env.example .env          # set MONGO_URI, JWT_SECRET
pip install -r requirements.txt
python app.py
```

Server: `http://localhost:5000`  •  Sockets: same origin, namespace `/training`

## REST endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST   | /api/auth/signup                  | email + password → JWT |
| POST   | /api/auth/login                   | email + password → JWT |
| GET    | /api/auth/me                      | current user |
| GET    | /api/datasets                     | list user datasets |
| POST   | /api/datasets/upload              | multipart upload (csv/xlsx) |
| GET    | /api/datasets/<id>                | dataset + preview rows |
| DELETE | /api/datasets/<id>                | delete |
| POST   | /api/datasets/<id>/visualizations | suggest charts |
| POST   | /api/reports                      | generate report for dataset |
| GET    | /api/reports/<id>                 | get report |
| POST   | /api/reports/<id>/chat            | send chat message |
| POST   | /api/automl/jobs                  | start training job |
| GET    | /api/automl/jobs                  | list jobs |
| GET    | /api/automl/jobs/<id>             | job + results |

## WebSockets — namespace `/training`
- client emits `subscribe` `{ jobId }` after connect
- server emits `job:update` `{ jobId, status, progress, logs[] }`
- server emits `job:done`   `{ jobId, results }`
