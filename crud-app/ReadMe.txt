CRUD app with backend in FastAPI and React frontend
https://dev.to/gilly7/building-your-first-full-stack-crud-app-with-fastapi-and-reactjs-3i1n

1. Start the backend
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --reload

#-----     -----     -----     -----#

1. Create frontend directory & copy frontend code
npx -y create-react-app frontend
cp frontend-src/App.css frontend-src/App.js frontend/src/
cd frontend

2. Install Axios for API calls
npm install axios

3. Start the frontend
npm start
