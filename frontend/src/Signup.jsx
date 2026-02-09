import { useState } from "react";
import { signup } from "./api";
import { useNavigate } from "react-router-dom";

function Signup() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();


  const handleSignup = async () => {

    try {

      await signup(email, password);

      navigate("/");

    } catch (err) {

      console.log(err);
      setError("Signup failed ❌");
    }
  };


  return (
    <div className="auth-box">

      <h1>Signup</h1>

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

      <button onClick={handleSignup}>
        Signup
      </button>

      {error && <p className="error">{error}</p>}

    </div>
  );
}

export default Signup;
