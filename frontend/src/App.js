import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Base URL for our backend API
const API_BASE = "http://localhost:8000";

function App() {
  // State variables to manage our data
  const [items, setItems] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [editingId, setEditingId] = useState(null);

  // useEffect hook runs when the component mounts
  useEffect(() => {
    fetchItems();
  }, []);

  // Function to fetch all items from the backend
  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API_BASE}/items/`);
      setItems(response.data);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  // Function to create a new item
  const createItem = async () => {
    try {
      const response = await axios.post(`${API_BASE}/items/`, {
        name,
        description
      });
      setItems([...items, response.data]);
      setName('');
      setDescription('');
    } catch (error) {
      console.error("Error creating item:", error);
    }
  };

  // Function to update an existing item
  const updateItem = async () => {
    try {
      const response = await axios.put(`${API_BASE}/items/${editingId}`, {
        name,
        description
      });
      setItems(items.map(item => item.id === editingId ? response.data : item));
      setEditingId(null);
      setName('');
      setDescription('');
    } catch (error) {
      console.error("Error updating item:", error);
    }
  };

  // Function to delete an item
  const deleteItem = async (id) => {
    try {
      await axios.delete(`${API_BASE}/items/${id}`);
      setItems(items.filter(item => item.id !== id));
    } catch (error) {
      console.error("Error deleting item:", error);
    }
  };

  // Function to start editing an item
  const startEdit = (item) => {
    setEditingId(item.id);
    setName(item.name);
    setDescription(item.description);
  };

  // Function to cancel editing
  const cancelEdit = () => {
    setEditingId(null);
    setName('');
    setDescription('');
  };

  return (
    <div className="App">
      <h1>CRUD App with FastAPI and React</h1>

      <div className="item-form">
        <h2>{editingId ? 'Edit Item' : 'Add New Item'}</h2>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        {editingId ? (
          <>
            <button onClick={updateItem}>Update</button>
            <button onClick={cancelEdit}>Cancel</button>
          </>
        ) : (
          <button onClick={createItem}>Create</button>
        )}
      </div>

      <div className="items-list">
        <h2>Items</h2>
        {items.length === 0 ? (
          <p>No items found</p>
        ) : (
          <ul>
            {items.map(item => (
              <li key={item.id}>
                <h3>{item.name}</h3>
                <p>{item.description}</p>
                <button onClick={() => startEdit(item)}>Edit</button>
                <button onClick={() => deleteItem(item.id)}>Delete</button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;
