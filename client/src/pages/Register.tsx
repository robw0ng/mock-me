// src/pages/Login.tsx
import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
// import styles from "./Login.module.css";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
        const response = await axios.post("http://localhost:8000/api/register", {
            email,
            password,
            confirm_password: confirmPassword
        });
        console.log(response.data);
        // navigate("/login");
    } catch (err: any) {
        setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleRegister} className="bg-white p-6 rounded shadow-md w-full max-w-sm">
        <h2 className="flex text-black justify-center text-xl font-semibold mb-4">Login</h2>
        {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="bg-gray-200 w-full p-2 mb-3 border-none border rounded text-black"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="bg-gray-200 w-full p-2 mb-4 border-none border rounded text-black"
          required
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="bg-gray-200 w-full p-2 mb-4 border-none border rounded text-black"
          required
        />
        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
        >
          Create Account
        </button>

        <button
          type="button"
          className="w-full bg-gray-400 text-white py-2 rounded mt-4 hover:bg-gray-600"
          onClick={() => navigate("/login")}
        >
          Go Back To Login
        </button>
      </form>
    </div>
  );
}
