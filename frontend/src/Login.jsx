import { useState } from "react";
import { login } from "./api";
import { useNavigate } from "react-router-dom";

function Login() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async () => {
    try {

      await login(email, password);

      window.location.href = "/dashboard";

    } catch (err) {

      console.log(err);
      setError("Invalid credentials ❌");
    }
  };

  return (
    <div className="login-page">

      {/* LEFT SIDE - LOGIN */}
      <div className="auth-box">

        <h1>Login</h1>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleLogin}>
          Login
        </button>

        {error && <p className="error">{error}</p>}

        <p style={{ marginTop: "15px" }}>
          New user?{" "}
          <span
            style={{ color: "#42c6ff", cursor: "pointer" }}
            onClick={() => navigate("/signup")}
          >
            Signup
          </span>
        </p>

      </div>


      {/* RIGHT SIDE - TITLE */}
      <div className="login-right">

        <h1>AI Image SaaS 🚀</h1>

        <p>
          Upload images, detect objects,
          download CSV reports, and manage jobs
          with ease.
        </p>

        <p className="tagline">
          Smart • Secure • Scalable
        </p>

      </div>

    </div>
  );
}

export default Login;
