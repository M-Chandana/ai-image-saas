# Project Name

## Description
This project is developed as part of my internship. It focuses on building an AI SaaS system with frontend and backend integration.## Description.This project was initially developed with backend functionality. During the early phase, the system was working properly and all core features were tested successfully.Later, the project was modified to improve structure and add new changes. After these modifications, the full frontend-backend integration did not work as expected due to technical and configuration issues.All previous working demos, testing results, and related outputs have been documented and posted in the Issues section of this repository for reference and verification.This repository reflects both the development progress and troubleshooting efforts made during the internship period.

## Tools & Technologies

- **React** – Used for building the frontend user interface.
- **FastAPI** – Used for developing RESTful backend APIs.
- **PostgreSQL** – Used for storing application data.
- **Swagger (OpenAPI)** – Used for API documentation, testing, and validation of backend endpoints.
- **MinIO** – Used as an object storage service for storing files, images, and related project resources.
- **Docker** – Used for containerizing the application and managing deployment environments.
- **Git & GitHub** – Used for version control, collaboration, and project management.

## API Documentation

Swagger UI was used to test and verify backend APIs. It provides interactive documentation for all available endpoints.


## Tech Stack
- Frontend: React
- Backend: FastAPI
- Database: PostgreSQL
- Tools: Docker, GitHub

## Features
- User Authentication
- API Integration
- Secure Data Handling
- Dashboard

## How to Run

### Backend
```bash
docker compose up --build
uvicorn main:app --reload
```  
### frontend
```bash
cd frontend
npm install
npm run dev
```  